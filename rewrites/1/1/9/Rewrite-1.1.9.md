# Wire protocol between the client and R
Status: settled on 2026-10-29. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): the messages the client and R exchange, and what R does with each. It builds on the [board objects](Rewrite-1.1.1), [board updates](Rewrite-1.1.2) and [block classes](Rewrite-1.1.5) proposals, and shapes writing the wire protocol, building the per-session evaluator and the Shiny bridge, and locking a board when the app starts, each an item in the Work list of [Client-owned board state](Rewrite-1.1#work). How R evaluates a block with its class and describes its output is [Block classes in R](Rewrite-1.1.5)'s, how R decodes state values is the [serialization proposal](Rewrite-1.1.4)'s, how a module sends requests through its host is [UI modules in JS](Rewrite-1.1.7)'s, and what the client does with replies, its revisions, demand and statuses, is the evaluation proposal ([Evaluation in the client](Rewrite-1.1.10)).

## What must hold

1. Everything the client and R say to each other is one of a few message kinds, written down in a versioned document with fixtures that the R and the JS test suites both round-trip.
2. A client that starts a new session with the board it holds loses only recomputation, since what a request needs to rebuild a result travels with it or can be asked for, except a file that an action keeps for the session alone, such as an upload in the session's temporary directory.
3. R decodes what the client sends as data only, never as code.
4. Shiny only carries the messages, so replacing it replaces one module.
5. Whether R runs a request in the session's process or in a worker process is R's own choice, which changes no message.

## Proposal

### Messages

A message is an array of requests from the client, or of replies and progress notes from R, so several travel together. Every request but a `cancel` or a `forget`, which get no reply, has an id the client chooses, and its reply echoes it, so replies may arrive in any order. The client sends nothing but its `hello` until R has answered it, as an MCP client sends no request but pings before the server has answered its `initialize` ([MCP lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)), and R ignores every message that comes before a session's `hello`, and takes a later `hello` as a fresh start of the session, which forgets every block, while the client ignores a reply to a request it is not waiting on, such as one to a `hello` that Shiny replays after a reconnect (notes).

```ts
type Kind = "hello" | "open" | "evaluate" | "request" | "output" | "cancel" | "forget";

interface Request { id?: string; kind: Kind }                     // id on every kind but cancel and forget
interface Reply { id: string; status: "ok" | "error" | "cancelled" | "invalid" | "missing" }
interface Progress { id: string; progress: { value?: number; message?: string } }
```

A reply's status belongs to its request alone: an `error` carries the conditions raised, bounded as an evaluation's are (below), and a request or an output that fails never marks its block `failed`, which only an evaluation's reply does ([Evaluation in the client](Rewrite-1.1.10#statuses)).

### Handshake

A connection starts with a `hello`, after MCP's `initialize`: the client names the protocol version and capabilities it speaks, and R answers with its own and with everything the client needs before it draws a board: the versions of R's packages, the block registry's entries ([Block classes in R](Rewrite-1.1.5#registration)), the startup modules of the packages R has loaded, in the order of their R dependencies ([UI modules in JS](Rewrite-1.1.7#startup-modules)), the modules packages offer each other, the renderers R picked ([Front-ends and extension points](Rewrite-1.1.8#renderers)), the values of the blockr options the client reads ([Defining a board in R](Rewrite-1.1.3#blockr-options)), the lock where the app locks the board (below), and the opening board, which the app script built or a file given to `serve()` holds ([Defining a board in R](Rewrite-1.1.3#the-opening-board)), with, for a block that `serve()` serves alone, the inputs R binds itself to the data it was given, in `bound`, which the client counts as linked and names in a request by the input alone ([Defining a board in R](Rewrite-1.1.3#data-passed-to-serve)). Both sides use only the capabilities both named, such as `cancel`, `interrupt` and `progress` (below), so a capability can arrive without a major version, and on a major mismatch the client stops and says what to do, such as reload the page.

```json
{ "id": "1", "kind": "hello", "protocol": "1.0", "capabilities": ["cancel", "interrupt", "progress"] }
{ "id": "1", "status": "ok", "protocol": "1.0", "capabilities": ["cancel", "progress"], "packages": { "blockr.core": "0.2.0" },
  "block_registry": {}, "startup_modules": [], "modules": {}, "renderers": {}, "blockr_options": {}, "lock": null, "board": {} }
```

A client that holds a board already, as when the server ended its session while the page lived on (below), sends it with its `hello`, as a saved file's text in `file`, as an `open` carries it ([Serialization](Rewrite-1.1.4#files)), and R opens it as it opens one an `open` carries (below), so that the packages it names are loaded and the block classes it defines registered before any recipe names them, and replies with the board as it opened it in place of the app script's, and with what it dropped, except on a locked board, which loads no other board (below). The client keeps its own board and its undo history, since R opens the same board in the same app, and opens the board R returned only where R dropped something, saying what, while a package that R loaded at another version makes core ask for the page to be reloaded ([UI modules in JS](Rewrite-1.1.7#startup-modules)).

### Opening a board

The `store.open()` call sends an `open`, which carries a saved board as the file's text ([Board updates](Rewrite-1.1.2#opening-a-board)), as does a startup module that names the board to open in place of the one R sent ([Front-ends and extension points](Rewrite-1.1.8#starting-the-page)). R parses it and opens it as it opens every board it did not build itself ([Defining a board in R](Rewrite-1.1.3#the-opening-board)), forgets every block (below), and replies as to a `hello`, without the protocol and capabilities. The board it replies with holds the front-end's state as the file holds it, and `saved` gives the version of each package that the file records, which R reads for a file from today's stack off the constructor nearest each package's state, so that each package's migration in JS knows what it reads ([Board updates](Rewrite-1.1.2#the-front-ends-state-and-attributes)). What R dropped comes in `dropped`, each object or key named with the package to install ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)).

```json
{ "id": "2", "kind": "open", "file": "{\"format\": 1, \"packages\": {}, \"board\": {}}" }
{ "id": "2", "status": "ok", "packages": {}, "block_registry": {}, "startup_modules": [], "modules": {}, "renderers": {},
  "blockr_options": {}, "lock": null, "board": {}, "saved": { "blockr.dock": "0.2.0" },
  "dropped": [ { "object": "block", "id": "d", "package": "blockr.dm" } ] }
```

### Evaluating a block

An evaluation request names the block and its revision and carries the recipe: the block's registry id and state, and its inputs as upstream blocks and revisions, each named by the input it feeds, in the order of the class's inputs, and a variadic block's in link order, where a positional link's input is empty ([Board objects](Rewrite-1.1.1#links)). R puts their ids in the block expression it builds from what the class's `expr` returns, and evaluates it with each upstream result bound to its id ([Block classes in R](Rewrite-1.1.5#evaluation)). A one-time evaluation's parameters, such as the write block's `save`, travel in the request's `params`, which R passes to `block_eval()` ([Evaluation in the client](Rewrite-1.1.10#demand), [Block classes in R](Rewrite-1.1.5#evaluation)).

```json
{ "id": "17", "kind": "evaluate", "block": "c", "revision": 4,
  "recipe": { "registry_id": "blockr.core-merge_block", "state": { "by": ["Species"], "all_x": false, "all_y": false },
              "inputs": [ { "input": "x", "block": "a", "revision": 2 }, { "input": "y", "block": "b", "revision": 3 } ] } }
```

R keeps the result under the block's id, with its revision, its block expression and the block's registry id, which an output request needs (below), and the reply carries what the client shows about it: the block expression R built, without the assignment to the block's id that an exported script adds, the result's summary ([Block classes in R](Rewrite-1.1.5#evaluation)), the conditions raised, and the standard output and error, all bounded.

```json
{ "id": "17", "status": "ok", "block": "c", "revision": 4, "expr": "merge(a, b, by = \"Species\", all.x = FALSE, all.y = FALSE)",
  "summary": "<data.frame> [150 × 7]",
  "conditions": [ { "severity": "warning", "class": ["simpleWarning", "warning", "condition"], "phase": "block_eval", "message": "..." } ],
  "omitted": { "warning": 0, "message": 0 }, "stdout": "", "stderr": "" }
```

A reply keeps the first few conditions of each severity and counts the rest in `omitted`, carries no tracebacks, and replaces the conditions of the block's earlier reply, as the Language Server Protocol replaces diagnostics ([LSP](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_publishDiagnostics)). The phase names what raised a condition: the class's `expr`, which builds the expression, its `inputs`, whose body checks the data, `block_eval()`, which runs the block expression, or `block_summary()`, which describes the result, and in the reply to an output request or a request, `output` or `request`, for the coercion or the request's function. The status is `invalid` when the block class's `expr` or its `block_eval()` method signals `invalid()`, with its message, or `expr` uses an arg the state leaves unset, naming it, before the block expression runs ([Block classes in R](Rewrite-1.1.5#evaluation)). A request on a revision that is still computing waits for it.

R replies `missing` to any request that names a block's revision it does not hold, such as a result it has forgotten or replaced, naming the blocks and revisions it lacks in `missing`, as `[ { "block": "b", "revision": 4 } ]`, and the client has a block evaluated again where that revision is still its current one and reads `ready`, then asks again, while a request that reads a block that is `failed`, `invalid` or `waiting` is never sent ([Evaluation in the client](Rewrite-1.1.10#demand)). A new session holds no results, so after its `hello` the client queues every demanded block again, with everything upstream ([Evaluation in the client](Rewrite-1.1.10#scheduling)). It answers none of the requests the session before it held either, so the client sends again every output and every request of a block class or an output class still waiting for its reply, and rejects an evaluation with parameters, an action, and an option's or an extension's request still waiting, which may have run and may write ([Evaluation in the client](Rewrite-1.1.10#scheduling)).

### Requests

A request asks R for an answer its caller needs, rather than for a block's result, by running a function that an object registers in R. Every request belongs to one, as a block's belong to its class, and R resolves it by the object's id: a block class's request by registry id, with `block` naming the block that asks, which R reads only on a locked board (below), a board option's by the option's id, under which the package that ships the option registers it in R, an output class's by the output it belongs to, which `output` names by its block and revision, against whose class vector R resolves it, most specific class first, as it picks a renderer ([Block classes in R](Rewrite-1.1.5#outputs)), and an extension's by the extension's id, `{pkg}-{name}`, under which its package registers it in R ([Front-ends and extension points](Rewrite-1.1.8#what-a-package-declares-in-r)), while how an extension registers with the dock is [Client-drawn dock and extensions](Rewrite-1.2)'s. A request names the block results it reads in `reads`, passes in `args` what its function takes, which for a block class's request is the state args its function names, filled in by the host from the block's state where the module passes none, and the parameters the UI gives it, and carries in `options` the values of the board options its function names, as an output request does, since R holds none ([Block classes in R](Rewrite-1.1.5#requests)). An output class's request carries the options and parameters its output was asked with, as the output request did, and R runs it with the result that output was made from.

```json
{ "id": "18", "kind": "request", "registry_id": "blockr.core-head_block", "name": "n_max", "block": "b", "args": {},
  "reads": [ { "input": "data", "block": "a", "revision": 2 } ] }
{ "id": "18", "status": "ok", "value": [150] }

{ "id": "19", "kind": "request", "option": "data_dir", "name": "list_dir", "args": { "path": "~" } }
{ "id": "20", "kind": "request", "extension": "blockr.code-code", "name": "script", "args": {},
  "reads": [ { "block": "a", "revision": 2 }, { "block": "b", "revision": 3 } ] }

{ "id": "22", "kind": "request", "output": { "block": "c", "revision": 7 }, "name": "download", "args": { "format": "pptx" },
  "options": {}, "params": {}, "body": { "type": "image/png" } }
{ "id": "22", "status": "ok", "body": { "type": "application/vnd.openxmlformats-officedocument.presentationml.presentation", "name": "chart.pptx" } }
```

What R runs for the client comes in these flavors, which differ in who defines and calls them, whether the client keeps what they answer, whether they may write, and what a locked board allows (below):

| Flavor | Defined by | Called by | Kept by the client | May write | On a locked board |
|---|---|---|---|---|---|
| Evaluation | The block's class, through its `expr` and `block_eval()` ([Block classes in R](Rewrite-1.1.5#evaluation)) | The scheduler, for demand and one-time evaluations ([Evaluation in the client](Rewrite-1.1.10#demand)) | Its reply sets the block's status, and R keeps the result | No | From the block expression R built at startup, for a locked block |
| Evaluation with parameters | A `block_eval()` method of the block's class, such as the write block's | A one-time evaluation with parameters, such as a save button's | No, it runs once per call | Yes | With its parameters only for a block left open |
| Output | The coercion of the output class that the block's class names | Core, for whatever draws the output ([UI modules in JS](Rewrite-1.1.7#the-contract)) | The last output, by revision, options, `info` and parameters | No | With the opening option values |
| Output class's request | The output class, as the package that defines it registers it | A renderer of the class, through its output host | Its answer, by block, revision, name, args, options and parameters, unless the class wraps it in `volatile()` | No | With the opening option values |
| Block class's request | The class's `requests` | The block's UI, through its host | Its answer, by registry id, name, args, options and the revisions read | No | With a locked block's opening state and the opening option values |
| Volatile request | A request the class wraps in `volatile()` | The block's UI, through its host | No | No | As a block class's request |
| Action | A request the class wraps in `action()`, such as an upload | The block's UI, through its host | No, it runs once per call | Yes | Only for a block left open |
| Option's request | The board option, as the package that ships it registers it | The option's UI or renderer, through its option host | No | Yes | Only where the option declares that it may run there |
| Extension's request | The extension, as its package registers it | The extension, through `CoreApi` | No | Yes | Only where the extension declares that it may run there |

An option or an extension declares for each of its requests, as its package registers it in R, whether it may run on a locked board, through `allow_locked`, so that each is decided on its own: one only reads, as the code export's does, while another may evaluate what the client sends, as an assistant's trial of proposed args would. R calls an extension's request with its `args` and the results it reads, each with the block expression R built for it, and a request that reads blocks, a block class's or an extension's, has them evaluated first, even off screen, as a one-time evaluation does ([Evaluation in the client](Rewrite-1.1.10#demand)). No request times out, since no reply is lost on a live connection and giving up on a request frees nothing in R, which runs it when its turn comes: a block class's request is bounded by its author ([Client-owned board state](Rewrite-1.1#proposal)), and any request may send progress, as blockr.md's export to PowerPoint would, which shows that a long one is still running.

### Outputs

An output request asks for the output that the coercion its block class names in `output` makes from the block's result at a revision, which R knows by the registry id it keeps with the result ([Block classes in R](Rewrite-1.1.5#outputs)), with the board's option values, what the client measured for the output's element, and the output's parameters, which its renderer keeps ([UI modules in JS](Rewrite-1.1.7#the-contract)):

```json
{ "id": "21", "kind": "output", "block": "b", "revision": 4, "options": { "n_rows": 50 },
  "info": { "width": 640, "height": 400, "pixel_ratio": 2, "bg": "#ffffff", "fg": "#212529", "accent": "#0d6efd", "font": "Inter" },
  "params": {} }
{ "id": "21", "status": "ok", "output": { "renderer": "blockr.core-basic_table", "columns": [], "rows": [], "total": 150 } }
```

An output is a description in JSON whose `renderer` names the renderer R picked for its output class, which the client mounts to draw it ([Front-ends and extension points](Rewrite-1.1.8#renderers)). Any reply may come with one binary body, such as a plot's PNG beside its output, or a file a request answers with, as a download does, and a request may carry one, as an upload action does, or a chart's bitmap for its download ([UI modules in JS](Rewrite-1.1.7#the-contract)). The reply or request announces it in `body`, with its MIME type and, for a download, a file name, as `"body": { "type": "image/png" }`, and the bytes travel beside it as the Shiny bridge carries them (below), so that no message depends on how.

### One request at a time

R runs the requests that ask it for work one at a time, in the order they arrive, so that a request on a revision still computing waits for it, as the scheduler's topological order relies on ([Evaluation in the client](Rewrite-1.1.10#scheduling)), and a request that reads results waits behind a running evaluation, while a `cancel` or a `forget` acts as soon as R reads it (below). R keeps the queue itself, and runs each request as a function that returns a promise of its reply, so that where a request runs is R's choice: in the session's process for now, where it holds the process until it ends, and in a worker process later, such as a mirai daemon, which no message notices. A request's promise resolves to its reply whatever the block or the request's function did, an `error` included, and rejects only when R itself fails, in which case R replies `error` all the same, since nothing times out and the client waits for a reply to every request with an id. Between two requests, R returns to its event loop and handles the messages that came in meanwhile, so that a `cancel` or a `forget` drops a queued request before it starts, and a request that starts before its `cancel` arrives costs only time, since the client drops every reply for a revision it has superseded ([Evaluation in the client](Rewrite-1.1.10#scheduling)).

### Cancelling

A `cancel` names a request by its id, as `{ "kind": "cancel", "request": "17" }`, and R drops it if it has not started and replies `cancelled` to it, if both sides named the capability `cancel`. R names a second capability, `interrupt`, which the client names too, only where a worker runs its requests that can stop a running one, as mirai's `stop_mirai()` interrupts a running task, and then stops a started request too, replying `cancelled`. The session's process names no `interrupt`, which keeps room for a worker later and is nothing to build now. In the session's process, a request that has started runs to its end, since R reads no message while it runs, and a promise cannot be cancelled, so that stopping a running request is up to whatever runs it. Its reply is then the one it would have had, which the client keeps where the block's revision is still current and drops where it has been superseded. The client cancels an evaluation whose revision it has since superseded, and others as the scheduler decides, such as one that nothing needs any more or, where both sides named `interrupt`, one below the default evaluation priority that keeps another waiting ([Evaluation in the client](Rewrite-1.1.10#scheduling)), but never a one-time evaluation with parameters, which may write and so runs once per call ([Evaluation in the client](Rewrite-1.1.10#demand)).

### Forgetting blocks

When blocks leave the board, the client sends a `forget` naming them, and R drops their results and every queued request that evaluates or reads one of them, replying `cancelled` to each. Opening another board forgets every block, since R opens it afresh, while the block classes that packages and the app script registered stay ([Board updates](Rewrite-1.1.2#opening-a-board), [Board objects](Rewrite-1.1.1#block-classes-outside-a-package)).

```json
{ "kind": "forget", "blocks": ["b", "c"] }
```

### Decoding

R decodes client input into plain values only, strings, numbers, logicals, lists and typed atomic vectors, never closures, calls, symbols or environments, so nothing becomes code by being decoded and `bquote()` keeps a value a value. That is the protocol's only safety, since a block may still parse a string into code, so keeping the R process within bounds is the deployment's job. R decodes with yyjsonr, as [Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r) has it.

### Locked boards

An app locks a board when it starts, through the blockr option `locked`, which an app sets as `blockr.locked` and a deployment as `BLOCKR_LOCKED`, as today, and the lock stays as the app set it, so that nothing a client sends can loosen it. A locked board loads no other board and keeps everything core keeps in it, its name and its blocks, links, stacks and options, as the app built them, and every block keeps its opening state but those whose inputs show, as core's attribute `visible` says on the board the app script built, which R reads once, when the app starts ([Board objects](Rewrite-1.1.1#blocks)). So a board whose readers may only change a filter shows the inputs of that filter alone, and on a locked board a block whose script set no visibility shows only its output, since R, as it locks the board, writes `visible` so into each such block of the opening board it sends, so that `locked` set to `TRUE` alone locks every block, as the dock does today, and an app opens a block by showing its inputs. On a locked board the store refuses every change to `visible`, and R never reads it after startup, so nothing a client says about what it shows reaches the lock, while on a board that is not locked, what a block shows locks nothing. What the front-end and its extensions keep, their state and the attributes they define, is for their own locks, as the dock locks the arrangement of its panels today, which never reaches R ([Client-drawn dock and extensions](Rewrite-1.2)). R sends the lock with its reply to `hello`, as the blocks it leaves open, `{ "open": ["f"] }`, or `null` where the app locks nothing, and the client keeps to it: its store refuses every `store.open()` and every delta the lock does not leave open ([Board updates](Rewrite-1.1.2#the-store)), a front-end draws no control for one, and whether a locked board offers saving is the front-end's and session management's to decide, while it offers no restoring, since it loads no other board ([Session management as a client extension](Rewrite-1.6)).

That stops only a client that plays by the rules, so R holds the lock in what it runs, comparing nothing a client sends. When the app starts, it builds from the opening board every block's class and the ids its inputs bind to, and for a locked block the block expression it evaluates, such as `dplyr::filter(a, Species == "setosa")`, so that a locked block's state and the bindings of its inputs are fixed together, and its `expr` never runs again. A locked block whose opening state cannot run, such as a merge whose `by` is unset, keeps the `invalid()` that building it signalled, and R replies `invalid` with it to every evaluation of the block. In a locked session:

- It evaluates a locked block with the block expression it built at startup, and a block left open with a block expression it builds from the request's state and the class and bindings it built at startup, reading from the request only the block's id, refusing one the opening board lacks, the revisions of the inputs, which say only which of its own results to bind, and the state and parameters of a block left open, so that a locked write block in manual mode, whose save button no front-end shows, never writes.
- It answers a block class's request for a locked block, as its `block` names it, with the block's opening state, whatever `args` holds, binding the inputs as it built them at startup, and takes only the parameters from the request.
- It takes the board's option values from the opening board for every request that carries them, a block class's, an output's or an output class's, whatever the request holds.
- It runs a block class's action only for a block left open.
- It opens no board, refusing every `open` and ignoring a board that a `hello` carries, so that a client starting a new session keeps its own board, and with it a reader's choices in the blocks left open.
- It runs an option's or an extension's request only where the option or extension declared that the request may run on a locked board (above).

Anything else is refused with an `error` that names the lock, while outputs are drawn as before, and the requests of their output classes answered, with the opening option values. A locked board thus runs only its opening board's blocks, every locked one with its opening state, whatever a client sends, as condition 2 of [Client-owned board state](Rewrite-1.1#what-must-hold) asks. With illustrative names:

```r
lock <- if (isTRUE(blockr_option("locked", FALSE))) {          # as serve() starts the app
  lock_board(opening_board, open = blocks_showing_inputs(opening_board))   # by visible, on the script's board
}

lock_board <- function(board, open = character()) {        # once, when the app starts
  lapply(set_names(names(board$blocks)), function(id) {
    blk    <- board$blocks[[id]]
    cls    <- block_registry[[blk$registry_id]]
    inputs <- upstream_ids(board$links, id)                  # input -> upstream id, list(data = "a")
    list(cls = cls, inputs = inputs,
         expression = if (!id %in% open)                     # or the invalid() that building it signals
           tryCatch(build_block_expression(cls, blk$state, inputs), invalid = identity))
  })
}

block_expression_for <- function(req, lock = NULL) {         # for every evaluation
  if (is.null(lock)) {                                       # an unlocked board: the request's recipe
    rec <- req$recipe
    return(build_block_expression(block_registry[[rec$registry_id]], rec$state, input_ids(rec$inputs)))
  }
  fixed <- lock[[req$block]]
  if (is.null(fixed)) refuse("The locked board has no block ", req$block)
  fixed$expression %||% build_block_expression(fixed$cls, req$recipe$state, fixed$inputs)   # a block left open: its state from the request
}
```

A block left open may parse what a reader types into code, as most of blockr.dplyr's builders do, and then runs whatever a reader types. Core decides nothing about what is safe to run: an app that serves a locked board to readers it does not trust hardens the R process, such as by running it in a sandbox like bubblewrap, since limiting what the R process may do is the deployment's job ([Client-owned board state](Rewrite-1.1#proposal)).

The lock leaves whole blocks open rather than single args, which a later minor version of the protocol can add, since only the lock's shape in the reply to `hello` would change. Today a locked core board drops every update that changes the board, while a block's own inputs stay editable unless a front-end reports them hidden through core's `frozen` channel ([R/board-server.R#L377-L386](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L377-L386), [R/block-server.R#L143-L153](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L143-L153)), and the dock freezes every block on a locked board, and on any board a block whose card hides its inputs, from what the client reports its cards show ([blockr.dock R/board-server.R#L386-L433](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/board-server.R#L386-L433)). The dock keeps saving and restoring in locked mode, which restores any board, since "locking is about preventing layout / structural mutations, not blocking a wholesale state import/export" ([blockr.dock#125](https://github.com/BristolMyersSquibb/blockr.dock/pull/125)), where a locked board here loads none.

### Versions

The protocol has a version of its own, apart from the JS API major that modules declare ([UI modules in JS](Rewrite-1.1.7#the-contract)), the format and package versions a saved board records ([Serialization](Rewrite-1.1.4#files)) and a block's revision, which names its result ([Evaluation in the client](Rewrite-1.1.10#revisions)). Its major changes only for what an existing peer would misread, and both sides ignore fields they do not know, as [shinyreact's protocol](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/protocol/README.md) does.

### The Shiny bridge

The client sends each message as text, with `Shiny.setInputValue("blockr", JSON.stringify(message), { priority: "event" })`, for R to decode as [Serialization](Rewrite-1.1.4) has it, since Shiny's own decoding leaves every array a list and flattens a message that is itself an array. R answers with `session$sendCustomMessage("blockr", message)`, which writes to the websocket at once, so that a request running in the session's process can send progress before it ends. The bridge's observer hands each message to R's queue and returns no promise, so Shiny never holds the session's inputs while a request runs, as it does for an observer that returns one. How a body travels is the bridge's choice too, which measuring settles when the bridge is built (notes). Leaving Shiny later replaces this module and nothing else.

The bridge calls `session$allowReconnect(TRUE)`, so that a page whose session the server ended while the page lived on, after a network drop longer than the server waits or a server restart, starts a new session and sends its board with its `hello` (above). An R process that exits ends the page instead: Shiny Server's proxy closes the page's connection with a code that forbids a new session, and its client covers the page until the user reloads it, so the board then survives as session management last saved it ([Session management as a client extension](Rewrite-1.6)). Keeping a page alive through a crash, by hiding that cover or starting a new session when the user asks, goes against what the proxy signals and is left for later, which the protocol allows already, since a `hello` may carry a board.

## Open questions

None.

<details><summary>Notes for implementers</summary>

An interrupt stops compiled code only at its next check, as the review of [Evaluation in the client](Rewrite-1.1.10) measured. With `mirai::stop_mirai()`, on one daemon with `cleanup = FALSE`, the daemon was free again at once after `Sys.sleep(30)`, but only 1.5 s after the interrupt during `lm()` on 2e7 rows, and with `callr::r_session$interrupt()`, `lm()` stopped 4.4 s and `sort(runif(2e8))` 44 s after it, while every worker kept the results it held. A promise cannot be cancelled: promises 1.5.0 exports nothing to cancel, and shiny 1.14.0's `ExtendedTask` has only `invoke()`, `status()` and `result()`.

How a request runs was measured on shiny 1.14.0 and mirai 2.7.3, with an app whose requests took 2 s, driven over its websocket. An `ExtendedTask` calls its function synchronously inside `invoke()`, so in the session's process it is a direct call behind a queue from which nothing can remove an invocation. With 33 messages queued during a request, Shiny handled all of them before the next request started, which its documentation does not promise. A request that called `session$sendCustomMessage()` reached the client every 0.5 s while it ran. In a mirai daemon with dispatcher, `stop_mirai()` interrupted a running task within 15 ms, and the daemon took the next task at once, its state intact.

A request's function reports progress through core, which sends it as progress notes, rather than through Shiny's `withProgress()`, whose messages Shiny's own client draws as a notification. The export of blockr.md reports none today: it runs pandoc in a `downloadHandler()` ([R/md-server.R#L212-L270](https://github.com/BristolMyersSquibb/blockr.md/blob/32e088884d825813fb7ff0afc7d023df9e70a3b6/R/md-server.R#L212-L270)). R's `setTimeLimit()` stopped an R loop at 1.01 s but let `Sys.sleep(3)` run its full 3 s, which is one reason no request times out.

A worker holds the results, since downstream blocks bind them, so every request that reads them runs there too, the browser's included, which reach it through the session's process, since the proxy reaches only the app's own process, so that only replies cross and no data does. It needs no block registry, lock or protocol of its own, since the session's process can build every call that reads results, the block expression and the calls of `block_eval()`, of the summary, of the output and of a block class's request, for the worker to evaluate in its environment of results, loading the packages those calls name as they run. What it needs copied in and kept in step is the code and settings those calls use beyond packages: the functions that the app script defines, the options the app script set, the data passed to `serve()`, and the visitor's session token. A mirai daemon resets its global environment after each task unless started with `cleanup = FALSE`, inherits environment variables but not options, and receives with each task the environment its function was defined in, 3.9 MB for a function defined inside a Shiny server function against 592 bytes for one defined at top level, so each request's function is one of core's, which serializes as a reference to its namespace. A task in a daemon cannot reach the session, so its progress needs a channel of its own. A worker per session is a second R process, 137 MB resident with blockr.core loaded and no data, against 64 MB for bare R, and a pool of workers per session would move results between them, which cost the blockx prototype at cynkra 17 to 18 s against 4 to 9 s of evaluation over its largest board's 54 computations ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)).

Shiny Server and Connect wrap Shiny's websocket in shiny-server-client, which lets Shiny start a new session only when the server closes the connection with a 47xx code ([lib/main.js#L133-L153](https://github.com/rstudio/shiny-server-client/blob/92cbc96583f958f4e379120323fb3a48c2e61fd5/lib/main.js#L133-L153)), as Shiny Server does for a session it no longer knows after a network drop and for its own restart. For an R process that exits, it closes the connection with `APP_EXIT`, 4503, which its table of codes describes as "Process exit with error (don't automatically restart)" ([lib/proxy/sockjs.js#L191-L235](https://github.com/rstudio/shiny-server/blob/4445750261a0d3ce4f303a14934d132be805f450/lib/proxy/sockjs.js#L191-L235), [lib/proxy/errorcode.js#L32-L55](https://github.com/rstudio/shiny-server/blob/4445750261a0d3ce4f303a14934d132be805f450/lib/proxy/errorcode.js#L32-L55)), and the wrapper covers the page with an overlay that takes every click, where Shiny's own lets clicks through. Connect's proxy is closed source, and Shiny documents a new session after a reconnect for Connect 1.5.10 or later ([Reconnecting to Shiny apps](https://shiny.posit.co/r/articles/improve/reconnecting)), while locally only `session$allowReconnect("force")` reconnects. When it reconnects, shiny.js 1.14.0 sends the new session the last value of every input, the bridge's last message among them, and then the messages queued while the page was offline, all of which R ignores until the session's `hello`, unless the last was a `hello` itself, which R answers as any `hello` and the client ignores, before the client's own `hello` starts the session afresh.

How a body travels is settled by measuring while the bridge is built. From R it can go as a binary frame from `session$sendBinaryMessage()`, which shiny.js 1.14.0 hands to the custom message handler for its type as an `ArrayBuffer`, as base64 in the JSON, a third larger, or from a session-scoped URL that `session$registerDataObj()` serves, which the browser fetches itself, so that a download streams to disk and no large body holds up the messages behind it on the websocket ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)). A file reaches R through the URL that Shiny's `uploadInit` gives, as `fileInput()` sends one, which refuses a file over `shiny.maxRequestSize`, 5 MB by default, or posted to a `registerDataObj()` URL, whose filter Shiny calls whatever the request's method. Core's output classes carry one page of rows as JSON, so core needs no Arrow writer, and an output class that needs one brings its own.

</details>
