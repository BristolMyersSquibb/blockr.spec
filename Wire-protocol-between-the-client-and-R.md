Status: draft. Design for [Client-owned board state](Client-owned-board-state).

One of the API proposals for the client-owned board ([Client-owned board state](Client-owned-board-state)): the messages the client and R exchange. It builds on the [document model](Document-model-for-the-client-owned-board) and shapes the protocol document ([blockr.core#393](https://github.com/BristolMyersSquibb/blockr.core/issues/393)), the evaluator and its Shiny bridge ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)) and outputs ([blockr.core#401](https://github.com/BristolMyersSquibb/blockr.core/issues/401)). What the client does with replies, its versions, demand and statuses, is the evaluation proposal ([Evaluation in the client](Evaluation-in-the-client)).

## What must hold

1. Everything the client and R say to each other is one of a few message kinds, written down in a versioned document with fixtures that the R and the JS test suites both round-trip.
2. Losing the R process costs only recomputation, since what a request needs to rebuild a result travels with it or can be asked for.
3. R decodes what the client sends as data only, never as code.
4. Shiny only carries the messages, so replacing it replaces one module.

## Proposal

### Messages

A message is an array of requests from the client, or of replies and progress notes from R, so several travel together. Every request has an id the client chooses, and its reply echoes it, so replies may arrive in any order.

```ts
type Kind = "hello" | "evaluate" | "request" | "output" | "cancel" | "forget";

interface Request { id: string; kind: Kind; long?: boolean }          // long lifts the timeout
interface Reply { id: string; status: "ok" | "error" | "cancelled" | "invalid" | "missing" }
interface Progress { id: string; progress: { value?: number; message?: string } }
```

### Handshake

A connection starts with a `hello`, after MCP's `initialize`: the client names the protocol version and capabilities it speaks, and R answers with its own, the registry ([blockr.core#396](https://github.com/BristolMyersSquibb/blockr.core/issues/396)) and the opening board, the one the app's startup script built ([Document model](Document-model-for-the-client-owned-board)). Both sides use only the capabilities both named, such as cancelling, binary bodies and progress, so a capability can arrive without a major version, and on a major mismatch the client stops and says what to do, such as reload the page. A client that holds a board already, as after R restarts, sends it with its `hello`, in the form of a saved file ([Serialization](Serialization-of-the-client-owned-board)), and R opens it as `store.open()` does ([Board updates](Board-updates-for-the-client-owned-board)), so that the packages its constructors name are loaded and the block types it defines registered before any recipe names them, and replies with the board as it rebuilt it in place of the startup script's.

```json
{ "id": "1", "kind": "hello", "protocol": "1.0", "capabilities": ["cancel", "binary", "progress"] }
{ "id": "1", "status": "ok", "protocol": "1.0", "capabilities": ["cancel", "progress"], "registry": {}, "board": {} }
```

### Evaluating a block

An evaluation request names the block and its version, carries the recipe, its registry id and state, and names its inputs as upstream blocks and versions, in slot order, so R binds them like the pairlist a type's `interpolate` receives. A positional input of a variadic block has an empty slot.

```json
{ "id": "17", "kind": "evaluate", "block": "c", "version": 4,
  "recipe": { "registry_id": "blockr.core-merge_block", "state": { "by": "Species" } },
  "inputs": [ { "slot": "x", "block": "a", "version": 2 }, { "slot": "y", "block": "b", "version": 3 } ] }
```

R keeps the result, and the reply carries what the client shows about it: the expression R built, the conditions raised, and the standard output and error, all bounded.

```json
{ "id": "17", "status": "ok", "block": "c", "version": 4, "expr": "merge(x, y, by = \"Species\", all.x = FALSE, all.y = FALSE)",
  "conditions": [ { "severity": "warning", "class": ["simpleWarning", "warning", "condition"], "phase": "eval", "message": "..." } ],
  "dropped": { "warning": 0, "message": 0 }, "stdout": "", "stderr": "" }
```

A reply keeps the first few conditions of each severity and counts the rest, carries no tracebacks, and replaces the conditions of the block's earlier reply, as the Language Server Protocol replaces diagnostics. The phase says where a condition came from: validating the state, building the expression, validating the data, or evaluating. The status is `invalid` when the block type's `validate` returns `FALSE`, with the message it attaches, which R checks before running anything ([Block types in R](Block-types-in-R-for-the-client-owned-board)). A request on a version that is still computing waits for it.

After a restart R holds no results, so it replies `missing` with the inputs it lacks, and the client sends their evaluation requests first and then asks again; that costs one round trip, and only after a restart.

### Requests

A block type's requests, the data-dependent attributes of its input elements among them, and a package's own requests share one kind, resolved through the registry by registry id or package and name. A request names the block results it reads in `reads`, and passes the state args its function names in `args`.

```json
{ "id": "18", "kind": "request", "registry_id": "blockr.core-head_block", "name": "n.max", "args": {},
  "reads": [ { "slot": "data", "block": "a", "version": 2 } ] }
{ "id": "18", "status": "ok", "value": 150 }

{ "id": "19", "kind": "request", "pkg": "blockr.code", "name": "code", "args": {},
  "reads": [ { "block": "a", "version": 2 }, { "block": "b", "version": 3 } ] }
```

The client caches a block type's answers by registry id, name, args and the versions read, and never caches a package's, since one may write. A package request that names blocks has them evaluated first, even off screen, as a one-off evaluation does ([Evaluation in the client](Evaluation-in-the-client)). A request that may run long, such as blockr.md's export to PowerPoint, says so with `long`, and R can send progress for it.

### Outputs

An output request asks for what the block type's `output(x, result, options, info, meta)` returns for the block's result at a version ([blockr.core#401](https://github.com/BristolMyersSquibb/blockr.core/issues/401)), with the board's option values, what the client measured for the output's element, and what the output's own client side keeps ([blockr.core#401](https://github.com/BristolMyersSquibb/blockr.core/issues/401)):

```json
{ "id": "20", "kind": "output", "block": "b", "version": 4, "options": { "n_rows": 50 },
  "info": { "width": 640, "height": 400, "pixel_ratio": 2, "bg": "#ffffff", "fg": "#212529", "accent": "#0d6efd", "font": "Inter" },
  "meta": {} }
{ "id": "20", "status": "ok", "output": { "type": "table", "columns": [], "rows": [], "total": 150 } }
```

A reply is JSON or a binary body with a MIME type and, for a download, a file name, and a request may carry a binary body too, such as an uploaded file.

### Cancelling

A `cancel` names a running request, and R stops it and replies `cancelled` to that request, if both sides named the capability. The client cancels an evaluation whose version it has since superseded.

### Forgetting blocks

When blocks leave the board, the client sends a `forget` naming them, and R drops their results ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)). Opening another board forgets every block, since R opens it afresh ([Board updates](Board-updates-for-the-client-owned-board)).

```json
{ "id": "21", "kind": "forget", "blocks": ["b", "c"] }
```

### Decoding

R decodes client input into plain values only, strings, numbers, logicals, lists and typed atomic vectors, never closures, calls, symbols or environments, so nothing becomes code by being decoded and `bquote()` keeps a value a value. That is the protocol's only safety, since a block may still parse a string into code, and opening a board may evaluate the definition of a block type registered outside a package where the `load_definitions` option allows it ([Document model](Document-model-for-the-client-owned-board)), so keeping the R process within bounds is the deployment's job. How R types survive JSON is a question for the [serialization proposal](Serialization-of-the-client-owned-board).

### Versions

The protocol version is one of three, apart from the JS API version modules declare and the package versions a saved board records ([Serialization](Serialization-of-the-client-owned-board)). Its major changes only for what an existing peer would misread, and both sides ignore fields they do not know, as shinyreact's protocol does.

### The Shiny bridge

The client sends a message with `Shiny.setInputValue("blockr", message, { priority: "event" })` and R answers with `session$sendCustomMessage("blockr", message)`. An evaluation runs as an `ExtendedTask`, which leaves the session's `busyCount` alone, so other messages are handled while it runs ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)). Leaving Shiny later replaces this module and nothing else.

## Open questions

- Which JSON decoding R applies, jsonlite's as today or typedjson's, taken up by the [serialization proposal](Serialization-of-the-client-owned-board) and left open in [blockr.core#393](https://github.com/BristolMyersSquibb/blockr.core/issues/393).
- Whether a binary body travels on Shiny through a session-scoped URL from `session$registerDataObj()` or as base64 on the websocket, to measure, and which Arrow writer serializes tables ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)).
- Whether R asking for missing inputs after a restart, as proposed, beats every request carrying the recipes of its whole upstream chain ([blockr.core#393](https://github.com/BristolMyersSquibb/blockr.core/issues/393)).
