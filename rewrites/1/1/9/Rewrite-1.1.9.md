# Wire protocol between the client and R
Status: draft. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): the messages the client and R exchange. It builds on the [board objects proposal](Rewrite-1.1.1) and shapes the protocol document ([blockr.core#393](https://github.com/BristolMyersSquibb/blockr.core/issues/393)), the evaluator and its Shiny bridge ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)) and outputs ([blockr.core#401](https://github.com/BristolMyersSquibb/blockr.core/issues/401)). What the client does with replies, its versions, demand and statuses, is the evaluation proposal ([Evaluation in the client](Rewrite-1.1.10)).

## What must hold

1. Everything the client and R say to each other is one of a few message kinds, written down in a versioned document with fixtures that the R and the JS test suites both round-trip.
2. Losing the R process costs only recomputation, since what a request needs to rebuild a result travels with it or can be asked for.
3. R decodes what the client sends as data only, never as code.
4. Shiny only carries the messages, so replacing it replaces one module.

## Proposal

### Messages

A message is an array of requests from the client, or of replies and progress notes from R, so several travel together. Every request has an id the client chooses, and its reply echoes it, so replies may arrive in any order.

```ts
type Kind = "hello" | "evaluate" | "request" | "output" | "upload" | "cancel" | "forget";

interface Request { id: string; kind: Kind; long?: boolean }          // long lifts the timeout
interface Reply { id: string; status: "ok" | "error" | "cancelled" | "invalid" | "missing" }
interface Progress { id: string; progress: { value?: number; message?: string } }
```

### Handshake

A connection starts with a `hello`, after MCP's `initialize`: the client names the protocol version and capabilities it speaks, and R answers with its own, the block registry's entries ([blockr.core#396](https://github.com/BristolMyersSquibb/blockr.core/issues/396)) with the startup modules of the packages it has loaded ([UI modules in JS](Rewrite-1.1.7#startup-modules)), the opening board, the one the app script built ([Board objects](Rewrite-1.1.1)), and the values of the blockr options the client reads ([Defining a board in R](Rewrite-1.1.3#blockr-options)). Both sides use only the capabilities both named, such as cancelling, binary bodies and progress, so a capability can arrive without a major version, and on a major mismatch the client stops and says what to do, such as reload the page. A client that holds a board already, as after R restarts, sends it with its `hello`, in the form of a saved file ([Serialization](Rewrite-1.1.4)), and R opens it as `store.open()` does ([Board updates](Rewrite-1.1.2)), so that the packages it names are loaded and the block types it defines registered before any recipe names them, and replies with the board as it opened it in place of the app script's.

```json
{ "id": "1", "kind": "hello", "protocol": "1.0", "capabilities": ["cancel", "binary", "progress"] }
{ "id": "1", "status": "ok", "protocol": "1.0", "capabilities": ["cancel", "progress"], "block_registry": {}, "board": {}, "blockr_options": {} }
```

### Evaluating a block

An evaluation request names the block and its version, carries the recipe, its registry id and state, and names its inputs as upstream blocks and versions, in slot order, whose results R binds to the inputs' names to evaluate the expression the block type's `expr` gives ([Block types in R](Rewrite-1.1.5#evaluation)). A positional input of a variadic block has an empty slot.

```json
{ "id": "17", "kind": "evaluate", "block": "c", "version": 4,
  "recipe": { "registry_id": "blockr.core-merge_block", "state": { "by": "Species" } },
  "inputs": [ { "slot": "x", "block": "a", "version": 2 }, { "slot": "y", "block": "b", "version": 3 } ] }
```

R keeps the result, and the reply carries what the client shows about it: the expression R built, the result's summary ([Block types in R](Rewrite-1.1.5#evaluation)), the conditions raised, and the standard output and error, all bounded.

```json
{ "id": "17", "status": "ok", "block": "c", "version": 4, "expr": "merge(x, y, by = \"Species\", all.x = FALSE, all.y = FALSE)",
  "summary": "<data.frame> [150 × 7]",
  "conditions": [ { "severity": "warning", "class": ["simpleWarning", "warning", "condition"], "phase": "eval", "message": "..." } ],
  "dropped": { "warning": 0, "message": 0 }, "stdout": "", "stderr": "" }
```

A reply keeps the first few conditions of each severity and counts the rest, carries no tracebacks, and replaces the conditions of the block's earlier reply, as the Language Server Protocol replaces diagnostics. The phase says where a condition came from: building the expression, validating the data, or evaluating. The status is `invalid` when the block type's `expr` signals `invalid()`, with its message, or uses an arg the state leaves unset, naming it, before anything runs ([Block types in R](Rewrite-1.1.5)). A request on a version that is still computing waits for it.

After a restart R holds no results, so it replies `missing` with the inputs it lacks, and the client sends their evaluation requests first and then asks again; that costs one round trip, and only after a restart.

### Requests

A block type's requests and a package's own requests share one kind, resolved through the block registry by registry id, or by package and name. A request names the block results it reads in `reads`, and passes in `args` the state args its function names and the parameters the UI gives it ([Block types in R](Rewrite-1.1.5#requests)).

```json
{ "id": "18", "kind": "request", "registry_id": "blockr.core-head_block", "name": "n_max", "args": {},
  "reads": [ { "slot": "data", "block": "a", "version": 2 } ] }
{ "id": "18", "status": "ok", "value": 150 }

{ "id": "19", "kind": "request", "pkg": "blockr.code", "name": "code", "args": {},
  "reads": [ { "block": "a", "version": 2 }, { "block": "b", "version": 3 } ] }
```

The client caches a block type's answers by registry id, name, args and the versions read, except a volatile request's, and never caches a package's, since one may write. A package request that names blocks has them evaluated first, even off screen, as a one-off evaluation does ([Evaluation in the client](Rewrite-1.1.10)). A request that may run long, such as blockr.md's export to PowerPoint, says so with `long`, and R can send progress for it.

### Outputs

An output request asks for what the block type's `output(x, result, options, info, meta)` returns for the block's result at a version ([blockr.core#401](https://github.com/BristolMyersSquibb/blockr.core/issues/401)), with the board's option values, what the client measured for the output's element, and what the output's own client side keeps ([blockr.core#401](https://github.com/BristolMyersSquibb/blockr.core/issues/401)):

```json
{ "id": "20", "kind": "output", "block": "b", "version": 4, "options": { "n_rows": 50 },
  "info": { "width": 640, "height": 400, "pixel_ratio": 2, "bg": "#ffffff", "fg": "#212529", "accent": "#0d6efd", "font": "Inter" },
  "meta": {} }
{ "id": "20", "status": "ok", "output": { "family": ["blockr.core-table"], "columns": [], "rows": [], "total": 150 } }
```

A reply is JSON or a binary body with a MIME type and, for a download, a file name. An output is a description in JSON whose `family` lists its output families, most specific first, which the renderer R picked for the first of them that has one draws ([Block types in R](Rewrite-1.1.5#outputs)), and it may come with one binary body, such as a plot's PNG. An `upload` carries a file the user picked, which R stores in the session's temporary directory, replying with its path, as Shiny's `fileInput()` does ([UI modules in JS](Rewrite-1.1.7#the-contract)).

### Cancelling

A `cancel` names a running request, and R stops it and replies `cancelled` to that request, if both sides named the capability. The client cancels an evaluation whose version it has since superseded.

### Forgetting blocks

When blocks leave the board, the client sends a `forget` naming them, and R drops their results ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)). Opening another board forgets every block, since R opens it afresh ([Board updates](Rewrite-1.1.2)).

```json
{ "id": "21", "kind": "forget", "blocks": ["b", "c"] }
```

### Decoding

R decodes client input into plain values only, strings, numbers, logicals, lists and typed atomic vectors, never closures, calls, symbols or environments, so nothing becomes code by being decoded and `bquote()` keeps a value a value. That is the protocol's only safety, since a block may still parse a string into code, and opening a board may evaluate the definition of a block type registered outside a package where the `load_definitions` option allows it ([Board objects](Rewrite-1.1.1)), so keeping the R process within bounds is the deployment's job. R decodes with yyjsonr, as [Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r) has it.

### Locked boards

An app locks a board when it starts, as `blockr.locked` does today, and the lock stays as the app set it: R builds it with the opening board and holds it in every recipe, so nothing a client sends can loosen it. A lock fixes the board's blocks, links, stacks and options, and every state arg of every block at its opening value, except the args the app leaves open, such as a filter's value on a board whose readers may only filter. R sends the lock with its reply to `hello`, and the client keeps to it, since its store refuses every `store.open()` and every delta the lock does not leave open ([Board updates](Rewrite-1.1.2#the-store)) and a front-end draws no control for one. A front-end may lock more of what it alone governs, as the dock locks the arrangement of its panels today, which never reaches R ([Client-drawn dock and extensions](Rewrite-1.2)).

That stops only a client that plays by the rules, so R holds the lock in what it runs. It keeps the opening board's recipes, and in a locked session:

- It evaluates a recipe only if it has the registry id and inputs of the block's opening recipe and the opening value of every arg the lock fixes.
- It answers a block type's request with the opening value of every arg the lock fixes, whatever `args` holds.
- It opens no board, whether `store.open()` sends one or a `hello` after a restart does, and builds the opening board from the app again instead.
- It runs a package's request only if the package declares that request safe on a locked board, since a request may evaluate what the client sends, as an assistant's trial of proposed args would.

Anything else is refused with an `error` that names the lock, while outputs are drawn as before, since an output request carries only values. A locked board thus runs only its opening board's blocks, with every arg the app did not leave open at its opening value, whatever a client sends, as condition 2 of [Client-owned board state](Rewrite-1.1#what-must-hold) asks. Today's lock leaves nothing open: core's update gate drops every update that changes state ([R/board-server.R#L377-L386](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L377-L386)), and the dock freezes the inputs of every block on a locked board ([blockr.dock R/board-server.R#L404-L433](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/board-server.R#L404-L433)).

### Versions

The protocol version is one of four, apart from the JS API version modules declare and the format version and package versions a saved board records ([Serialization](Rewrite-1.1.4#files)). Its major changes only for what an existing peer would misread, and both sides ignore fields they do not know, as shinyreact's protocol does.

### The Shiny bridge

The client sends each message as text, with `Shiny.setInputValue("blockr", JSON.stringify(message), { priority: "event" })`, for R to decode as [Serialization](Rewrite-1.1.4) has it, since Shiny's own decoding leaves every array a list and flattens a message that is itself an array. R answers with `session$sendCustomMessage("blockr", message)`. An evaluation runs as an `ExtendedTask`, which leaves the session's `busyCount` alone, so other messages are handled while it runs ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)). Leaving Shiny later replaces this module and nothing else.

## Open questions

- How an app names the args its lock leaves open when it starts, such as through an argument of `serve()`, of a block's constructor, or the blockr option that sets the lock itself, `blockr.locked`, as an app sets its other blockr options ([Defining a board in R](Rewrite-1.1.3#blockr-options)).
- Whether a locked board may still be restored, as [blockr.dock#123](https://github.com/BristolMyersSquibb/blockr.dock/issues/123) asked of today's lock, since a restored file comes from the client and so falls outside what R holds the lock to. It blocks locking a board when the app starts.
- Whether an arg that a block parses into code, as most of blockr.dplyr's builders do, may be left open at all, since it runs whatever a reader types into it, or only args that its block type declares safe.
- Whether a binary body travels on Shiny through a session-scoped URL from `session$registerDataObj()` or as base64 on the websocket, to measure, and which Arrow writer serializes tables ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)).
- Whether R asking for missing inputs after a restart, as proposed, beats every request carrying the recipes of its whole upstream chain ([blockr.core#393](https://github.com/BristolMyersSquibb/blockr.core/issues/393)).
