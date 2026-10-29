# Wire protocol between the client and R
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): the messages the client and R exchange, and what R does with each. It builds on the [board objects](Rewrite-1.1.1), [board updates](Rewrite-1.1.2) and [block classes](Rewrite-1.1.5) proposals, and shapes writing the wire protocol, building the per-session evaluator and the Shiny bridge, and locking a board when the app starts, each an item in the Work list of [Client-owned board state](Rewrite-1.1#work). How R evaluates a block with its class and describes its output is [Block classes in R](Rewrite-1.1.5)'s, how R decodes state values is the [serialization proposal](Rewrite-1.1.4)'s, how a module sends requests through its host is [UI modules in JS](Rewrite-1.1.7)'s, and what the client does with replies, its versions, demand and statuses, is the evaluation proposal ([Evaluation in the client](Rewrite-1.1.10)).

## What must hold

1. Everything the client and R say to each other is one of a few message kinds, written down in a versioned document with fixtures that the R and the JS test suites both round-trip.
2. A client that starts a new session with the board it holds loses only recomputation, since what a request needs to rebuild a result travels with it or can be asked for, except a file that an action keeps for the session alone, such as an upload in the session's temporary directory.
3. R decodes what the client sends as data only, never as code.
4. Shiny only carries the messages, so replacing it replaces one module.
5. Whether R runs a request in the session's process or in a worker process is R's own choice, which changes no message.

## Proposal

### Messages

A message is an array of requests from the client, or of replies and progress notes from R, so several travel together. Every request but a `cancel` or a `forget`, which get no reply, has an id the client chooses, and its reply echoes it, so replies may arrive in any order. The client sends nothing but its `hello` until R has answered it, as an MCP client sends no request but pings before the server has answered its `initialize` ([MCP lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)), and R ignores every message that comes before a session's `hello`.

```ts
type Kind = "hello" | "open" | "evaluate" | "request" | "output" | "cancel" | "forget";

interface Request { id?: string; kind: Kind }                     // id on every kind but cancel and forget
interface Reply { id: string; status: "ok" | "error" | "cancelled" | "invalid" | "missing" }
interface Progress { id: string; progress: { value?: number; message?: string } }
```

A reply's status belongs to its request alone: an `error` carries the conditions raised, bounded as an evaluation's are (below), and a request or an output that fails never marks its block `failed`, which only an evaluation's reply does ([Evaluation in the client](Rewrite-1.1.10#statuses)).

### Handshake

A connection starts with a `hello`, after MCP's `initialize`: the client names the protocol version and capabilities it speaks, and R answers with its own and with everything the client needs before it draws a board: the versions of R's packages, the block registry's entries ([Block classes in R](Rewrite-1.1.5#registration)), the startup modules of the packages R has loaded, in the order of their R dependencies ([UI modules in JS](Rewrite-1.1.7#startup-modules)), the modules packages offer each other, the renderers R picked ([Front-ends and extension points](Rewrite-1.1.8#renderers)), the values of the blockr options the client reads ([Defining a board in R](Rewrite-1.1.3#blockr-options)), the lock where the app locks the board (below), and the opening board, the one the app script built ([Defining a board in R](Rewrite-1.1.3#the-opening-board)). Both sides use only the capabilities both named, such as cancelling, binary bodies and progress, so a capability can arrive without a major version, and on a major mismatch the client stops and says what to do, such as reload the page.

```json
{ "id": "1", "kind": "hello", "protocol": "1.0", "capabilities": ["cancel", "binary", "progress"] }
{ "id": "1", "status": "ok", "protocol": "1.0", "capabilities": ["cancel", "progress"], "packages": { "blockr.core": "0.2.0" },
  "block_registry": {}, "startup_modules": [], "modules": {}, "renderers": {}, "blockr_options": {}, "lock": null, "board": {} }
```

A client that holds a board already, as when the server ended its session while the page lived on (below), sends it with its `hello`, in the form of a saved file ([Serialization](Rewrite-1.1.4#files)), and R opens it as it opens one an `open` carries (below), so that the packages it names are loaded and the block classes it defines registered before any recipe names them, and replies with the board as it opened it in place of the app script's, and with what it dropped, except on a locked board, which loads no other board (below). The client keeps its own board and its undo history, since R opens the same board in the same app, and opens the board R returned only where R dropped something, saying what, while a package that R loaded at another version makes core ask for the page to be reloaded ([UI modules in JS](Rewrite-1.1.7#startup-modules)).

### Opening a board

The `store.open()` call sends an `open`, which carries a saved board as the file's text ([Board updates](Rewrite-1.1.2#opening-a-board)), as does a startup module that names the board to open in place of the one R sent ([Front-ends and extension points](Rewrite-1.1.8#starting-the-page)). R parses it and opens it as it opens every board it did not build itself ([Defining a board in R](Rewrite-1.1.3#the-opening-board)), forgets every block (below), and replies as to a `hello`, without the protocol and capabilities, with the board as it opened it and what it dropped, each object named with the package to install ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)).

```json
{ "id": "2", "kind": "open", "file": "{\"format\": 1, \"packages\": {}, \"definitions\": {}, \"board\": {}}" }
{ "id": "2", "status": "ok", "packages": {}, "block_registry": {}, "startup_modules": [], "modules": {}, "renderers": {},
  "blockr_options": {}, "lock": null, "board": {}, "dropped": [] }
```

### Evaluating a block

An evaluation request names the block and its version and carries the recipe: the block's registry id and state, and its inputs as upstream blocks and versions, in slot order, whose ids R puts in the expression the block class's `expr` gives, evaluating it with each upstream result bound to its id ([Block classes in R](Rewrite-1.1.5#evaluation)). A positional input of a variadic block has an empty slot.

```json
{ "id": "17", "kind": "evaluate", "block": "c", "version": 4,
  "recipe": { "registry_id": "blockr.core-merge_block", "state": { "by": ["Species"], "all_x": false, "all_y": false },
              "inputs": [ { "slot": "x", "block": "a", "version": 2 }, { "slot": "y", "block": "b", "version": 3 } ] } }
```

R keeps the result, and the reply carries what the client shows about it: the expression R built, the result's summary ([Block classes in R](Rewrite-1.1.5#evaluation)), the conditions raised, and the standard output and error, all bounded.

```json
{ "id": "17", "status": "ok", "block": "c", "version": 4, "expr": "merge(a, b, by = \"Species\", all.x = FALSE, all.y = FALSE)",
  "summary": "<data.frame> [150 × 7]",
  "conditions": [ { "severity": "warning", "class": ["simpleWarning", "warning", "condition"], "phase": "evaluate", "message": "..." } ],
  "omitted": { "warning": 0, "message": 0 }, "stdout": "", "stderr": "" }
```

A reply keeps the first few conditions of each severity and counts the rest in `omitted`, carries no tracebacks, and replaces the conditions of the block's earlier reply, as the Language Server Protocol replaces diagnostics ([LSP](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_publishDiagnostics)). The phase names the class's function that raised a condition: `expr`, which builds the expression, `inputs`, whose body checks the data, or `evaluate`. The status is `invalid` when the block class's `expr` signals `invalid()`, with its message, or uses an arg the state leaves unset, naming it, before anything runs ([Block classes in R](Rewrite-1.1.5#expressions)). A request on a version that is still computing waits for it.

R replies `missing` to any request that names a block version it does not hold, such as a result it has forgotten or replaced, naming the blocks and versions it lacks, and the client has a block evaluated again where that version is still its current one, then asks again. A new session holds no results, so after its `hello` the client evaluates every demanded block again, with everything upstream, in one message ([Evaluation in the client](Rewrite-1.1.10#scheduling)).

### Requests

A block class's requests and a package's own requests share one kind, resolved by registry id through the block registry, or by package and name. A request names the block results it reads in `reads`, passes in `args` what its function takes, which for a block class's request is the state args its function names, filled in by the host from the block's state where the module passes none, and the parameters the UI gives it, and carries in `options` the values of the board options its function names, as an output request does, since R holds none ([Block classes in R](Rewrite-1.1.5#requests)).

```json
{ "id": "18", "kind": "request", "registry_id": "blockr.core-head_block", "name": "n_max", "args": {},
  "reads": [ { "slot": "data", "block": "a", "version": 2 } ] }
{ "id": "18", "status": "ok", "value": 150 }

{ "id": "19", "kind": "request", "package": "blockr.code", "name": "code", "args": {},
  "reads": [ { "block": "a", "version": 2 }, { "block": "b", "version": 3 } ] }
```

The client caches a block class's answers by registry id, name, args, options and the versions read, except a volatile request's or an action's, and never caches a package's, since an action and a package's request may write. A package registers its requests in R as it loads, as it declares its renderers ([Front-ends and extension points](Rewrite-1.1.8#renderers)), and R calls one with its `args` and the results it reads, each with the expression R built for it. A request that reads blocks, a block class's or a package's, has them evaluated first, even off screen, as a one-off evaluation does ([Evaluation in the client](Rewrite-1.1.10#demand)). No request times out, since no reply is lost on a live connection and giving up on a request frees nothing in R, which runs it when its turn comes: a block class's request is bounded by its author ([Client-owned board state](Rewrite-1.1#proposal)), and any request may send progress, as blockr.md's export to PowerPoint would, which shows that a long one is still running.

### Outputs

An output request asks for the output that the generic its block class names in `output` makes from the block's result at a version ([Block classes in R](Rewrite-1.1.5#outputs)), with the board's option values, what the client measured for the output's element, and the output's `meta`, which its renderer keeps ([UI modules in JS](Rewrite-1.1.7#the-contract)):

```json
{ "id": "20", "kind": "output", "block": "b", "version": 4, "options": { "n_rows": 50 },
  "info": { "width": 640, "height": 400, "pixel_ratio": 2, "bg": "#ffffff", "fg": "#212529", "accent": "#0d6efd", "font": "Inter" },
  "meta": {} }
{ "id": "20", "status": "ok", "output": { "family": "blockr.core-table", "columns": [], "rows": [], "total": 150 } }
```

An output is a description in JSON whose `family` names its output family, which the renderer R picked for that family draws ([Front-ends and extension points](Rewrite-1.1.8#renderers)). Any reply may come with one binary body, with its MIME type and, for a download, a file name, such as a plot's PNG beside its output, or a file a block class's request answers with, and a request may carry a file as a binary body, as an upload action does ([UI modules in JS](Rewrite-1.1.7#the-contract)). A body is bytes with a MIME type, carried beside a message's JSON, and how the bytes travel is the Shiny bridge's (below), so that no message depends on it.

### One request at a time

R runs a session's requests one at a time, in the order they arrive, so that a request on a version still computing waits for it, as the scheduler's topological order relies on ([Evaluation in the client](Rewrite-1.1.10#scheduling)), and a request that reads results waits behind a running evaluation. R keeps the queue itself, and runs each request as a function that returns a promise of its reply, so that where a request runs is R's choice: in the session's process for now, where it holds the process until it ends, and in a worker process later, such as a mirai daemon, which no message notices. A request's promise resolves to its reply whatever the block or the request's function did, an `error` included, and rejects only when R itself fails. Between two requests, R returns to its event loop and handles the messages that came in meanwhile, so that a `cancel` or a `forget` drops a queued request before it starts, and a request that starts before its `cancel` arrives costs only time, since the client drops every reply for a version it has superseded ([Evaluation in the client](Rewrite-1.1.10#scheduling)).

### Cancelling

A `cancel` names a request, and R drops it if it has not started, replying `cancelled` to it, if both sides named the capability. In the session's process, a request that has started runs to its end, since R reads no message while it runs, and the client drops its reply, while a worker could stop it, as mirai's `stop_mirai()` interrupts a running task. The client cancels an evaluation whose version it has since superseded.

### Forgetting blocks

When blocks leave the board, the client sends a `forget` naming them, and R drops their results. Opening another board forgets every block, since R opens it afresh ([Board updates](Rewrite-1.1.2#opening-a-board)).

```json
{ "kind": "forget", "blocks": ["b", "c"] }
```

### Decoding

R decodes client input into plain values only, strings, numbers, logicals, lists and typed atomic vectors, never closures, calls, symbols or environments, so nothing becomes code by being decoded and `bquote()` keeps a value a value. That is the protocol's only safety, since a block may still parse a string into code, and opening a board may evaluate the definition of a block class registered outside a package where the `load_definitions` option allows it ([Board objects](Rewrite-1.1.1#block-classes-outside-a-package)), so keeping the R process within bounds is the deployment's job. R decodes with yyjsonr, as [Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r) has it.

### Locked boards

An app locks a board when it starts, through the blockr option `blockr.locked` as today, and the lock stays as the app set it, so that nothing a client sends can loosen it. A locked board loads no other board and keeps everything core keeps in it, its name and its blocks, links, stacks and options, as the app built them, and every block keeps its opening state but those whose inputs show, as core's attribute `visible` says on the board the app script built, which R reads once, when the app starts ([Board objects](Rewrite-1.1.1#blocks)). So a board whose readers may only change a filter shows the inputs of that filter alone, and on a locked board a block whose script set no visibility shows only its output, so that `blockr.locked = TRUE` alone locks every block, as the dock does today, and an app opens a block by showing its inputs. On a locked board the store refuses every change to `visible`, and R never reads it after startup, so nothing a client says about what it shows reaches the lock, while on a board that is not locked, what a block shows locks nothing. What other packages keep, their fields and the attributes of blocks, is for their own locks, as the dock locks the arrangement of its panels today, which never reaches R ([Client-drawn dock and extensions](Rewrite-1.2)). R sends the lock with its reply to `hello`, and the client keeps to it: its store refuses every `store.open()` and every delta the lock does not leave open ([Board updates](Rewrite-1.1.2#the-store)), a front-end draws no control for one, and whether a locked board shows saving and restoring at all is the front-end's and session management's to decide ([Session management as a client extension](Rewrite-1.6)).

That stops only a client that plays by the rules, so R holds the lock in what it runs, comparing nothing a client sends. When the app starts, it builds from the opening board every block's class and the ids its inputs bind to, and for a locked block the block expression it evaluates, such as `f <- dplyr::filter(a, Species == "setosa")`, so that a locked block's state and the bindings of its inputs are fixed together, and its `expr` never runs again. In a locked session:

- It evaluates a locked block with the block expression it built at startup, and a block left open with a block expression it builds from the request's state and the class and bindings it built at startup, reading from the request only the block's id, refusing one the opening board lacks, the versions of the inputs, which say only which of its own results to bind, and the state of a block left open.
- It answers a block class's request with a locked block's opening state and the board's opening option values, whatever the request holds, binding the inputs as it built them at startup, and takes only the parameters from the request.
- It runs a block class's action only if its class declares that it may run on a locked board, as it answers a request.
- It opens no board, refusing every `open` and ignoring a board that a `hello` carries, so that a client starting a new session keeps its own board, and with it a reader's choices in the blocks left open.
- It runs a package's request only if the package declares that the request may run on a locked board, since a request may evaluate what the client sends, as an assistant's trial of proposed args would, while one such as the code export only reads.

Anything else is refused with an `error` that names the lock, while outputs are drawn as before, since an output request carries only values. A locked board thus runs only its opening board's blocks, every locked one with its opening state, whatever a client sends, as condition 2 of [Client-owned board state](Rewrite-1.1#what-must-hold) asks. With illustrative names:

```r
lock <- if (isTRUE(blockr_option("locked", FALSE))) {          # as serve() starts the app
  lock_board(opening_board, open = blocks_showing_inputs(opening_board))   # by visible, on the script's board
}

lock_board <- function(board, open = character()) {        # once, when the app starts
  lapply(set_names(names(board$blocks)), function(id) {
    blk    <- board$blocks[[id]]
    cls    <- block_registry[[blk$registry_id]]
    inputs <- upstream_ids(board$links, id)                  # slot -> upstream id, list(data = "a")
    list(cls = cls, inputs = inputs,
         expression = if (!id %in% open) build_block_expression(cls, blk$state, inputs))
  })
}

block_expression_for <- function(req, lock = NULL) {         # for every evaluation
  if (is.null(lock)) {                                       # an unlocked board: the request's recipe
    rec <- req$recipe
    return(build_block_expression(block_registry[[rec$registry_id]], rec$state, slot_ids(rec$inputs)))
  }
  fixed <- lock[[req$block]]
  if (is.null(fixed)) refuse("The locked board has no block ", req$block)
  fixed$expression %||% build_block_expression(fixed$cls, req$recipe$state, fixed$inputs)   # a block left open: its state from the request
}
```

A block left open may parse what a reader types into code, as most of blockr.dplyr's builders do, and then runs whatever a reader types. Core decides nothing about what is safe to run: an app that serves a locked board to readers it does not trust hardens the R process, such as by running it in a sandbox like bubblewrap, since limiting what the R process may do is the deployment's job ([Client-owned board state](Rewrite-1.1#proposal)).

The lock leaves whole blocks open rather than single args, which a later minor version of the protocol can add, since only the lock's shape in the reply to `hello` would change. Today a locked core board drops every update that changes the board, while a block's own inputs stay editable unless a front-end reports them hidden through core's `frozen` channel ([R/board-server.R#L377-L386](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L377-L386), [R/block-server.R#L143-L153](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L143-L153)), and the dock freezes every block on a locked board, and on any board a block whose card hides its inputs, from what the client reports its cards show ([blockr.dock R/board-server.R#L386-L433](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/board-server.R#L386-L433)). The dock keeps saving and restoring in locked mode, which restores any board, since "locking is about preventing layout / structural mutations, not blocking a wholesale state import/export" ([blockr.dock#125](https://github.com/BristolMyersSquibb/blockr.dock/pull/125)), where a locked board here loads none.

### Versions

The protocol has a version of its own, apart from the JS API major that modules declare ([UI modules in JS](Rewrite-1.1.7#the-contract)), the format and package versions a saved board records ([Serialization](Rewrite-1.1.4#files)) and a block's version, which names its result ([Evaluation in the client](Rewrite-1.1.10#versions)). Its major changes only for what an existing peer would misread, and both sides ignore fields they do not know, as [shinyreact's protocol](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/protocol/README.md) does.

### The Shiny bridge

The client sends each message as text, with `Shiny.setInputValue("blockr", JSON.stringify(message), { priority: "event" })`, for R to decode as [Serialization](Rewrite-1.1.4) has it, since Shiny's own decoding leaves every array a list and flattens a message that is itself an array. R answers with `session$sendCustomMessage("blockr", message)`, which writes to the websocket at once, so that a request running in the session's process can send progress before it ends. The bridge's observer hands each message to R's queue and returns no promise, so Shiny never holds the session's inputs while a request runs, as it does for an observer that returns one. How a body travels is the bridge's choice too, which measuring settles when the bridge is built (notes). Leaving Shiny later replaces this module and nothing else.

The bridge calls `session$allowReconnect(TRUE)`, so that a page whose session the server ended while the page lived on, after a network drop longer than the server waits or a server restart, starts a new session and sends its board with its `hello` (above). An R process that exits ends the page instead: Shiny Server's proxy closes the page's connection with a code that forbids a new session, and its client covers the page until the user reloads it, so the board then survives as session management last saved it ([Session management as a client extension](Rewrite-1.6)). Keeping a page alive through a crash, by hiding that cover or starting a new session when the user asks, goes against what the proxy signals and is left for later, which the protocol allows already, since a `hello` may carry a board.

## Open questions

None.

<details><summary>Notes for implementers</summary>

How a request runs was measured on shiny 1.14.0 and mirai 2.7.3, with an app whose requests took 2 s, driven over its websocket. An `ExtendedTask` calls its function synchronously inside `invoke()`, so in the session's process it is a direct call behind a queue from which nothing can remove an invocation. With 33 messages queued during a request, Shiny handled all of them before the next request started, which its documentation does not promise. A request that called `session$sendCustomMessage()` reached the client every 0.5 s while it ran. In a mirai daemon with dispatcher, `stop_mirai()` interrupted a running task within 15 ms, and the daemon took the next task at once, its state intact.

A request's function reports progress through core, which sends it as progress notes, rather than through Shiny's `withProgress()`, whose messages Shiny's own client draws as a notification. The export of blockr.md reports none today: it runs pandoc in a `downloadHandler()` ([R/md-server.R#L212-L270](https://github.com/BristolMyersSquibb/blockr.md/blob/32e088884d825813fb7ff0afc7d023df9e70a3b6/R/md-server.R#L212-L270)). R's `setTimeLimit()` stopped an R loop at 1.01 s but let `Sys.sleep(3)` run its full 3 s, which is one reason no request times out.

A worker holds the results, since downstream blocks bind them, so every request that reads them runs there too, and it needs the rest of the session's state copied in and kept in step: the block classes an opened board registers, from its packages and definitions, the options the app script set, the app script's objects that its block classes use, the data passed to `serve()`, and the visitor's session token. A mirai daemon resets its global environment after each task unless started with `cleanup = FALSE`, inherits environment variables but not options, and receives with each task the environment its function was defined in, 3.9 MB for a function defined inside a Shiny server function against 592 bytes for one defined at top level, so each request's function is one of core's, which serializes as a reference to its namespace. A task in a daemon cannot reach the session, so its progress needs a channel of its own. A worker per session is a second R process, 137 MB resident with blockr.core loaded and no data, against 64 MB for bare R, and a pool of workers per session would move results between them, which cost the blockx prototype at cynkra 17 to 18 s against 4 to 9 s of evaluation over its largest board's 54 computations ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)).

Shiny Server and Connect wrap Shiny's websocket in shiny-server-client, which lets Shiny start a new session only when the server closes the connection with a 47xx code ([lib/main.js#L133-L153](https://github.com/rstudio/shiny-server-client/blob/92cbc96583f958f4e379120323fb3a48c2e61fd5/lib/main.js#L133-L153)), as Shiny Server does for a session it no longer knows after a network drop and for its own restart. For an R process that exits, it closes the connection with `APP_EXIT`, 4503, which its table of codes describes as "Process exit with error (don't automatically restart)" ([lib/proxy/sockjs.js#L191-L235](https://github.com/rstudio/shiny-server/blob/4445750261a0d3ce4f303a14934d132be805f450/lib/proxy/sockjs.js#L191-L235), [lib/proxy/errorcode.js#L32-L55](https://github.com/rstudio/shiny-server/blob/4445750261a0d3ce4f303a14934d132be805f450/lib/proxy/errorcode.js#L32-L55)), and the wrapper covers the page with an overlay that takes every click, where Shiny's own lets clicks through. Connect's proxy is closed source, and Shiny documents a new session after a reconnect for Connect 1.5.10 or later ([Reconnecting to Shiny apps](https://shiny.posit.co/r/articles/improve/reconnecting)), while locally only `session$allowReconnect("force")` reconnects. When it reconnects, shiny.js 1.14.0 sends the new session the last value of every input, the bridge's last message among them, and then the messages queued while the page was offline, all of which R ignores until the session's `hello`.

How a body travels is settled by measuring while the bridge is built. From R it can go as a binary frame from `session$sendBinaryMessage()`, which shiny.js 1.14.0 hands to the custom message handler for its type as an `ArrayBuffer`, as base64 in the JSON, a third larger, or from a session-scoped URL that `session$registerDataObj()` serves, which the browser fetches itself, so that a download streams to disk and no large body holds up the messages behind it on the websocket ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)). A file reaches R through the URL that Shiny's `uploadInit` gives, as `fileInput()` sends one, which refuses a file over `shiny.maxRequestSize`, 5 MB by default, or posted to a `registerDataObj()` URL, whose filter Shiny calls whatever the request's method. Core's output families carry one page of rows as JSON, so core needs no Arrow writer, and a family that needs one brings its own.

</details>
