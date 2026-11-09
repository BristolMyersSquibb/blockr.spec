# Wire protocol between the client and R
Status: settled on 2026-10-29. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): the messages the client and R exchange, and what R does with each.
It builds on the [board objects](Rewrite-1.1.1), [board updates](Rewrite-1.1.2) and [block classes](Rewrite-1.1.5) proposals, and shapes writing the wire protocol ([blockr.core#420](https://github.com/BristolMyersSquibb/blockr.core/issues/420)), building the per-session evaluator ([blockr.core#430](https://github.com/BristolMyersSquibb/blockr.core/issues/430)) and the Shiny transport ([blockr.core#431](https://github.com/BristolMyersSquibb/blockr.core/issues/431)), locking a board when the app starts ([blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434)), the client scheduler ([blockr.core#435](https://github.com/BristolMyersSquibb/blockr.core/issues/435)), starting core again as a board opens ([blockr.core#497](https://github.com/BristolMyersSquibb/blockr.core/issues/497)), filling the block registry from the packages that the app names ([blockr.core#498](https://github.com/BristolMyersSquibb/blockr.core/issues/498)), the versions of plugin classes in the reply to `hello` ([blockr.core#504](https://github.com/BristolMyersSquibb/blockr.core/issues/504)), a plugin's requests ([blockr.core#505](https://github.com/BristolMyersSquibb/blockr.core/issues/505)), the reply to `blockr_options` ([blockr.core#510](https://github.com/BristolMyersSquibb/blockr.core/issues/510)), bounding the summary of an evaluation's reply ([blockr.core#512](https://github.com/BristolMyersSquibb/blockr.core/issues/512)) and stopping the page on a later `hello` that it cannot take ([blockr.core#515](https://github.com/BristolMyersSquibb/blockr.core/issues/515)), each an item in the Work list of [Client-owned board state](Rewrite-1.1#work).
How R evaluates a block with its class and describes its output is [Block classes in R](Rewrite-1.1.5)'s, how R decodes state values is the [serialization proposal](Rewrite-1.1.4)'s, how a module sends requests through its host is [UI modules in JS](Rewrite-1.1.7)'s, and what the client does with replies, its revisions, demand and statuses, is the evaluation proposal ([Evaluation in the client](Rewrite-1.1.10)).

## What must hold

1. Everything the client and R say to each other is one of a few message kinds, written down in a versioned document with fixtures that the R and the JS test suites both round-trip.
2. A client that starts a new session with the board it holds loses only recomputation, since what a request needs to rebuild a result travels with it or can be asked for, except a file that an action keeps for the session alone, such as an upload in the session's temporary directory.
3. R decodes what the client sends into plain values, so the protocol itself turns no value into code.
4. Shiny only carries the messages, so replacing it replaces one module.
5. Whether R runs a request in the session's process or in a worker process is R's own choice, which changes no message.

## Proposal

### Messages

A message is an array of requests from the client, or of replies and progress notes from R, so several travel together.
Every request but a `cancel` or a `forget`, which get no reply, has an id the client chooses, and its reply echoes it, so replies may arrive in any order.
The client sends nothing but its `hello` until R has answered it, as an MCP client sends no request but pings before the server has answered its `initialize` ([MCP lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)), and R ignores every message that comes before a session's `hello`, and takes a later `hello` as a fresh start of the session, which forgets every block, while the client ignores a reply to a request it is not waiting on, and R never sees a `hello` that Shiny replays after a reconnect (notes).

```ts
type Kind = "hello" | "blockr_options" | "evaluate" | "request" | "output" | "cancel" | "forget";

interface Request { id?: string; kind: Kind }                     // id on every kind but cancel and forget
interface Reply { id: string; status: "ok" | "error" | "cancelled" | "invalid" | "missing" }
interface Progress { id: string; progress: { value?: number; message?: string } }
```

A reply's status belongs to its request alone: an `error` carries the conditions raised, bounded as an evaluation's are (below), and a request or an output that fails never marks its block `failed`, which only an evaluation's reply does ([Evaluation in the client](Rewrite-1.1.10#statuses)).

### Handshake

A connection starts with a `hello`, after MCP's `initialize`: the client names the protocol version and capabilities it speaks, and R answers with its own and with everything the client needs before it draws a board: the versions of R's packages, the block registry's entries, each with the renderer of its class's outputs where R knows it ([Block classes in R](Rewrite-1.1.5#registration)), the startup modules of the packages that the app names, in the order of their R dependencies ([UI modules in JS](Rewrite-1.1.7#startup-modules)), the modules packages offer each other, those of plugin classes among them, the versions that those packages give their plugin classes, by the class's id, in `plugin_versions`, where a class without a method of `plugin_version()` is at version 1 ([Plugins](Rewrite-1.1.12#a-plugin)), the versions that those packages give board options, in `option_versions`, where a board option that it lacks is at version 1 ([Serialization](Rewrite-1.1.4#board-options)), the renderers that the app names for board options, since the renderer of an output comes in the output and in its block class's entry ([Drawing the board](Rewrite-1.1.8#renderers)), the locks that the app sets (below), and the opening board, in `board`, as a JSON board ([Defining a board in R](Rewrite-1.1.3#the-opening-board)): the one the app script built, with every id, since R draws each id the script left out ([Board objects](Rewrite-1.1.1#ids)), or the one given to `serve()`, which R passes on as it is, having read nothing of it but its format unless both locks are on ([Serving a JSON board locked](Rewrite-1.1.11#serving-a-json-board-locked)), with, for a block that `serve()` serves alone, the inputs R binds itself to the data it was given, in `bound`, which the client counts as linked and names in a request by the input alone ([Defining a board in R](Rewrite-1.1.3#data-passed-to-serve)).
R takes all of it from the packages that the app names, as the app starts, so that every reply to `hello` of the process holds the same, whatever a block's code loads ([Block classes in R](Rewrite-1.1.5#registration)).
Both sides use only the capabilities both named, such as `cancel`, `interrupt` and `progress` (below), so a capability can arrive without a major version, and on a major mismatch the client stops and says what to do, such as reload the page.

```json
{ "id": "1", "kind": "hello", "protocol": "1.0", "capabilities": ["cancel", "interrupt", "progress"] }
{ "id": "1", "status": "ok", "protocol": "1.0", "capabilities": ["cancel", "progress"], "packages": { "blockr.core": "0.2.0" },
  "block_registry": {}, "startup_modules": [], "modules": {}, "plugin_versions": {}, "option_versions": {}, "renderers": {},
  "lock": { "board": false, "load": false }, "board": {} }
```

A client that holds a board already, as when the server ended its session while the page lived on (below), keeps it and its undo history, since the app names the packages its block classes come from, as it did for the session before.
R sends the opening board all the same, which that client does not open, while a package that R names at another version than before makes core ask for the page to be reloaded ([UI modules in JS](Rewrite-1.1.7#startup-modules)).

### Opening a board

The client opens every board itself, as a JSON board, with what R's reply to `hello` holds: the block registry's entries, by which it draws the blocks, the versions of the plugin classes, the opening board, which sets the plugins of every board that the client opens ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)), and the versions of the packages that the app names ([Board updates](Rewrite-1.1.2#opening-a-board)).
R holds no board, and loads no package for one, since installing the packages whose block classes an app offers is the deployment's job, and the packages that the app names fill the block registry as the app starts, so that every block class a recipe names is registered before the first `hello` ([Block classes in R](Rewrite-1.1.5#registration)).
So no message opens a board: `store.open()` sends R nothing for a JSON board's text, nor for the board that a startup module names in place of the one R sent ([Drawing the board](Rewrite-1.1.8#starting-the-page)), while a block whose class the block registry lacks and a plugin whose class none of the app's packages registers are dropped and named, and so is each package that the JSON board lists and the app does not offer ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)), and a board that the client opens in place of another starts the session afresh with a `hello`, as core starts again ([Drawing the board](Rewrite-1.1.8#opening-a-board)), so that R drops every result and queued request of the board before (below).

### Blockr options

The client reads a blockr option by asking R for it, since it can read neither an R option nor an environment variable of the server ([Board options and blockr options](Rewrite-1.1.13#blockr-options)).
A `blockr_options` request names them in `names`, and R replies with the value of each it has one for, as `blockr_option()` reads it, in `values`, by name, leaving out the others, for which the client takes the fallback its code gives.
A value set through an environment variable arrives as a string, which the client converts to its fallback's type, and R writes `Inf` as `null`, since JSON has no infinite numbers, which the client reads as `Infinity` where its fallback is a number.
The client asks for a blockr option once per page, the first time its code reads it, and keeps the value, since a blockr option is fixed for the app, while core asks for those its scheduler reads as soon as R has answered its `hello` ([Evaluation in the client](Rewrite-1.1.10#scheduling)).
R answers for any blockr option, since a client can read whatever the R process can ([State in JS](Rewrite-1#proposal)).

```json
{ "id": "2", "kind": "blockr_options", "names": ["evaluation_queue", "background_evaluation_delay", "gate_visibility"] }
{ "id": "2", "status": "ok", "values": { "evaluation_queue": 3 } }
```

### Evaluating a block

An evaluation request names the block, its revision and its `locked`, which R reads only on a locked board ([Locked boards](#locked-boards)), and carries the recipe: the block's registry id and state, and its inputs as upstream blocks and revisions, each named by the input it feeds, in the order of the class's inputs, and a variadic block's in link order, where a positional link's input is empty ([Board objects](Rewrite-1.1.1#links)).
R puts their ids in the block expression it builds from what the class's `expr` returns, and evaluates it with each upstream result bound to its id ([Block classes in R](Rewrite-1.1.5#evaluation)).
A one-time evaluation's parameters, such as the write block's `save`, travel in the request's `params`, which R passes to `block_eval()` ([Evaluation in the client](Rewrite-1.1.10#demand), [Block classes in R](Rewrite-1.1.5#evaluation)).

```json
{ "id": "17", "kind": "evaluate", "block": "c", "revision": 4, "locked": null,
  "recipe": { "registry_id": "blockr.core-merge_block", "state": { "by": ["Species"], "all_x": false, "all_y": false },
              "inputs": [ { "input": "x", "block": "a", "revision": 2 }, { "input": "y", "block": "b", "revision": 3 } ] } }
```

R keeps the result under the block's id, with its revision, its block expression and the block's registry id, which an output request and a plugin's request that reads the block need (below), and the reply carries what the client shows about it: the result's summary ([Block classes in R](Rewrite-1.1.5#evaluation)), the conditions raised, and the standard output and error, all bounded.
It carries no code, since exporting a block's code is blockr.code's, through a request of its own that reads the expressions R keeps ([Code export as a client extension](Rewrite-1.5)).

```json
{ "id": "17", "status": "ok", "block": "c", "revision": 4, "summary": "<data.frame> [150 × 7]",
  "conditions": [ { "severity": "warning", "class": ["simpleWarning", "warning", "condition"], "phase": "block_eval", "message": "..." } ],
  "omitted": { "warning": 0, "message": 0 }, "stdout": "", "stderr": "" }
```

A reply keeps the first few conditions of each severity and counts the rest in `omitted`, carries no tracebacks, and replaces the conditions of the block's earlier reply, as the Language Server Protocol replaces diagnostics ([LSP](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_publishDiagnostics)).
The phase names what raised a condition: the class's `expr`, which builds the expression, its `inputs`, whose body checks the data, `block_eval()`, which runs the block expression, or `result_summary()`, which describes the result, and in the reply to an output request or a request, `output` or `request`, for the coercion or the request's function.
The status is `invalid` when the block class's `expr` or its `block_eval()` method signals `blockr_invalid()`, with its message, or `expr` uses an arg the state leaves unset, naming it, before the block expression runs ([Block classes in R](Rewrite-1.1.5#evaluation)).
A request on a revision that is still computing waits for it.

R replies `missing` to any request that names a block's revision it does not hold, such as a result it has forgotten or replaced, naming the blocks and revisions it lacks in `missing`, as `[ { "block": "b", "revision": 4 } ]`.
The client hands the reply back to the code that sent the request.
That code asks again once the blocks are evaluated at their current revisions.
A request that reads a `failed`, `invalid` or `waiting` block is never sent ([Evaluation in the client](Rewrite-1.1.10#demand)).
A new session holds no results, so after its `hello` the client gives every block a new revision.
Every block then reads `stale` until the new session has evaluated it ([Evaluation in the client](Rewrite-1.1.10#scheduling)).
It answers none of the requests the session before it held either, so the client sends again every output and every request of a block class, an output class or a renderer still waiting for its reply, and rejects an evaluation with parameters, an action, and a board option's or a plugin's request still waiting, which may have run and may write ([Evaluation in the client](Rewrite-1.1.10#scheduling)).

### Requests

A request asks R for an answer its caller needs, rather than for a block's result, by running a function that an object gives in R.
Every request belongs to one, as a block's belong to its class, and names in `type` which kind of object that is, as [blockr.core#484](https://github.com/BristolMyersSquibb/blockr.core/pull/484) built it.
R reads a request into an object of class `{type}_request` and answers it through the generic `request_call()`, whose method for that class finds the function that answers the request and binds its args.
Core has five types:

- The type `block_class` is a block class's request, which R finds by registry id, with `block` naming the block that asks.
- The type `output_class` is an output class's request, which R finds by the output it belongs to, which `output` names by its block and revision, among the requests that the method of `output_requests()` for its class vector gives ([Block classes in R](Rewrite-1.1.5#outputs)).
- The type `renderer` is a renderer's own request, which R finds by the renderer's id, which `renderer` names beside the output whose result it reads, among the requests of the renderer that draws that output alone, which has to be the one named ([Drawing the board](Rewrite-1.1.8#renderers)).
- The type `option` is a board option's request, which R finds among those that the method of `board_option_requests()` for the class of the board option that `option` names, `{id}_option`, gives ([Drawing the board](Rewrite-1.1.8#what-a-package-declares-in-r)).
- The type `plugin` is a plugin's request, which R finds among those that the method of `plugin_requests()` for the plugin class whose id `plugin` names gives ([Plugins](Rewrite-1.1.12#a-plugins-requests)).

A package adds no type of its own, since a plugin's request covers what the dock's extensions would have added one for, and R replies `error` to a type that is not core's ([Plugins](Rewrite-1.1.12#a-plugins-requests)).
A request names the block results it reads in `reads`, passes in `args` what its function takes, which for a block class's request is the state args its function names, filled in by the host from the block's state where the module passes none, and the parameters the UI gives it, and carries in `options` the values of the board options it reads, by id, as an output request does, since R holds none, which for a block class's request are those its `new_block_request()` names ([Block classes in R](Rewrite-1.1.5#requests)).
An output class's request, or a renderer's, carries the board options and parameters its output was asked with, as the output request did, and R runs it with the result that output was made from.

```json
{ "id": "18", "kind": "request", "type": "block_class", "registry_id": "blockr.core-head_block", "name": "n_max", "block": "b", "args": {},
  "reads": [ { "input": "data", "block": "a", "revision": 2 } ] }
{ "id": "18", "status": "ok", "value": [150] }

{ "id": "19", "kind": "request", "type": "option", "option": "data_dir", "name": "list_dir", "args": { "path": "~" } }
{ "id": "20", "kind": "request", "type": "plugin", "plugin": "blockr.code-code_plugin", "name": "script", "args": {},
  "reads": [ { "block": "a", "revision": 2 }, { "block": "b", "revision": 3 } ] }

{ "id": "22", "kind": "request", "type": "output_class", "output": { "block": "c", "revision": 7 }, "name": "download", "args": { "format": "pptx" },
  "options": {}, "params": {}, "body": { "type": "image/png" } }
{ "id": "22", "status": "ok", "body": { "type": "application/vnd.openxmlformats-officedocument.presentationml.presentation", "name": "chart.pptx" } }

{ "id": "35", "kind": "request", "type": "renderer", "output": { "block": "a", "revision": 3 }, "renderer": "blockr.ui-table_preview", "name": "labels",
  "args": {}, "options": { "n_rows": 50 }, "params": {} }
{ "id": "35", "status": "ok", "value": { "USUBJID": ["Unique Subject Identifier"], "AGE": ["Age"] } }
```

What R runs for the client comes in these flavors, which differ in who defines and calls them, whether the client keeps what they answer, and whether they may write:

| Flavor | Defined by | Called by | Kept by the client | May write |
|---|---|---|---|---|
| Evaluation | The block's class, through its `expr` and `block_eval()` ([Block classes in R](Rewrite-1.1.5#evaluation)) | The scheduler, for demand and one-time evaluations ([Evaluation in the client](Rewrite-1.1.10#demand)) | Its reply sets the block's status, and R keeps the result | No |
| Evaluation with parameters | A `block_eval()` method of the block's class, such as the write block's | A one-time evaluation with parameters, such as a save button's | No, it runs once per call | Yes |
| Output | The coercion of the output class that the block's class names | Core, for whatever draws the output ([UI modules in JS](Rewrite-1.1.7#the-contract)) | The last output, by revision, board options, `info` and parameters | No |
| Output class's request | The output class, through the method of `output_requests()` that the package that defines it gives | A renderer of the class, through its output host | Its answer, by block, revision, name, args, board options and parameters, unless the class wraps it in `volatile()` | No |
| Renderer's request | The renderer, as its package gives it to `new_renderer()` | That renderer, through its output host | Its answer, as for an output class's request, and by the renderer | No |
| Block class's request | The class's `requests` | The block's UI, through its host | Its answer, by registry id, name, args, board options and the revisions read | No |
| Volatile request | A request that the class makes with `new_block_request(volatile = TRUE)` | The block's UI, through its host | No | No |
| Action | A request that the class makes with `new_block_request(action = TRUE)`, such as an upload | The block's UI, through its host | No, it runs once per call | Yes |
| Board option's request | The package that ships the board option, through its method of `board_option_requests()` | The board option's UI or renderer, through its `OptionHost` | No | Yes |
| Plugin's request | The plugin's package, through its method of `plugin_requests()` | The plugin, through `CoreApi` | No | Yes |

On a locked board, R holds an evaluation, with parameters or without, to the block's data inputs and a locked block to its state, and draws every output and runs every request as on any board ([What R refuses](Rewrite-1.1.11#what-r-refuses)).
R calls a plugin's request with its `args` by name and, in `reads`, the results it reads, by block id, each with the block expression R built for it, and a request that reads blocks, a block class's or a plugin's, has them evaluated first, even off screen, as a one-time evaluation does ([Evaluation in the client](Rewrite-1.1.10#demand)).
No request times out, since no reply is lost on a live connection and giving up on a request frees nothing in R, which runs it when its turn comes: a block class's request is bounded by its author ([Client-owned board state](Rewrite-1.1#proposal)), and any request may send progress, as blockr.md's export to PowerPoint would, which shows that a long one is still running.

### Outputs

An output request asks for the output that the coercion its block class names in `output` makes from the block's result at a revision, which R knows by the registry id it keeps with the result ([Block classes in R](Rewrite-1.1.5#outputs)), with the values of the board options that its renderer requires, or, in a block's first output request where its registry entry names no renderer, of every board option that a loaded package defines, the board's value or else its default ([Board options and blockr options](Rewrite-1.1.13#the-renderer-before-the-first-output)), what the client measured for the output's element, and the output's parameters, which its renderer keeps ([UI modules in JS](Rewrite-1.1.7#the-contract)):

```json
{ "id": "21", "kind": "output", "block": "b", "revision": 4, "options": { "n_rows": 50 },
  "info": { "width": 640, "height": 400, "pixel_ratio": 2, "bg": "#ffffff", "fg": "#212529", "accent": "#0d6efd", "font": "Inter" },
  "params": {} }
{ "id": "21", "status": "ok", "output": { "renderer": { "id": "blockr.core-table_output", "module": "blockr.core/js/basic-table.js?v=b7e2a915" }, "columns": [], "rows": [], "total": 150 } }
```

An output is a description in JSON whose `renderer` is the renderer that draws it, with its id and where R serves its module, which the client loads the first time an output names it, unless it loaded it already as the renderer that the block registry entry names, and mounts to draw it ([Drawing the board](Rewrite-1.1.8#renderers)).
Any reply may come with one binary body, such as a plot's PNG beside its output, or a file a request answers with, as a download does, and a request may carry one, as an upload action does, or a chart's bitmap for its download ([UI modules in JS](Rewrite-1.1.7#the-contract)).
The reply or request announces it in `body`, with its MIME type and, for a download, a file name, as `"body": { "type": "image/png" }`, and the bytes travel beside it as the Shiny transport carries them (below), so that no message depends on how.

### One request at a time

R runs the requests that ask it for work one at a time, in the order they arrive, so that a request on a revision still computing waits for it, as the scheduler's topological order relies on ([Evaluation in the client](Rewrite-1.1.10#scheduling)), and a request that reads results waits behind a running evaluation, while a `cancel` or a `forget` acts as soon as R reads it (below).
R keeps the queue itself, and runs each request as a function that returns a promise of its reply, so that where a request runs is R's choice: in the session's process for now, where it holds the process until it ends, and in a worker process later, such as a mirai daemon, which no message notices.
A request's promise resolves to its reply whatever the block or the request's function did, an `error` included, and rejects only when R itself fails, in which case R replies `error` all the same, since nothing times out and the client waits for a reply to every request with an id.
Between two requests, R returns to its event loop and handles the messages that came in meanwhile, so that a `cancel` or a `forget` drops a queued request before it starts, and a request that starts before its `cancel` arrives costs only time, since the client drops every reply for a revision it has superseded ([Evaluation in the client](Rewrite-1.1.10#scheduling)).

### Cancelling

A `cancel` names a request by its id, as `{ "kind": "cancel", "request": "17" }`, and R drops it if it has not started and replies `cancelled` to it, if both sides named the capability `cancel`.
R names a second capability, `interrupt`, which the client names too, only where a worker runs its requests that can stop a running one, as mirai's `stop_mirai()` interrupts a running task, and then stops a started request too, replying `cancelled`.
The session's process names no `interrupt`, which keeps room for a worker later and is nothing to build now.
In the session's process, a request that has started runs to its end, since R reads no message while it runs, and a promise cannot be cancelled, so that stopping a running request is up to whatever runs it.
Its reply is then the one it would have had, which the client keeps where the block's revision is still current and drops where it has been superseded.
The client cancels an evaluation whose revision it has since superseded, and others as the scheduler decides, such as one that nothing needs any more or, where both sides named `interrupt`, one below the default evaluation priority that keeps another waiting ([Evaluation in the client](Rewrite-1.1.10#scheduling)), but never a one-time evaluation with parameters, which may write and so runs once per call ([Evaluation in the client](Rewrite-1.1.10#demand)).

### Forgetting blocks

When blocks leave the board, the client sends a `forget` naming them, and R drops their results and every queued request that evaluates or reads one of them, replying `cancelled` to each.
A board that the client opens in place of another has R forget every block of the one it replaces through the `hello` with which core starts again, rather than through a `forget`, since R takes a later `hello` as a fresh start of the session (above), while the block classes that packages and the app script registered stay ([Drawing the board](Rewrite-1.1.8#opening-a-board), [Board objects](Rewrite-1.1.1#block-classes-outside-a-package)).
That clears as well what an evaluation sent before it may have left in R, and the bodies that the transport holds for the session (below).

```json
{ "kind": "forget", "blocks": ["b", "c"] }
```

### Decoding

R decodes client input into plain values only, strings, numbers, logicals, lists and typed atomic vectors, never closures, calls, symbols or environments, so nothing becomes code by being decoded and `bquote()` keeps a value a value.
This protects nothing: a block may parse a string into code, so a board runs arbitrary R code, and the deployment sandboxes the R process ([Principles](Principles#a-board-runs-arbitrary-r-code-and-the-deployment-sandboxes-the-r-process)).
R decodes with yyjsonr, as [Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r) has it.

### Locked boards

The locks, and what R refuses for them, are [Locked boards and the properties of blocks](Rewrite-1.1.11)'s: the load lock, the blockr option `lock_load`, the board lock, the blockr option `locked`, and each block's `locked` ([Three locks](Rewrite-1.1.11#three-locks)).
Two properties of the messages carry them:

- The reply to `hello` holds the locks in `lock`, as `{ "board": true, "load": true }`, with `false` for a lock that the app does not set ([The locks in the reply to `hello`](Rewrite-1.1.11#the-locks-in-the-reply-to-hello)).
- An evaluation carries the block's `locked`, which R reads only on a locked board ([Block locks](Rewrite-1.1.11#block-locks)).

R refuses only what it can tell breaks the board lock or a block's lock, with an `error` that names the lock ([What R refuses](Rewrite-1.1.11#what-r-refuses)).
Where both locks are on, R holds every block to the opening board, from what it builds once as the app starts.
With illustrative names:

```r
lock <- if (isTRUE(blockr_option("locked", FALSE)) && isTRUE(blockr_option("lock_load", FALSE))) {   # as serve() starts the app
  lock_board(opening_board, open = blocks_left_open(opening_board))   # those whose locked is FALSE
}

lock_board <- function(board, open = character()) {        # once, when the app starts
  lapply(set_names(names(board$blocks)), function(id) {
    blk    <- board$blocks[[id]]
    cls    <- block_registry[[blk$registry_id]]
    inputs <- upstream_ids(board$links, id)                  # input -> upstream id, list(data = "a")
    list(cls = cls, inputs = inputs,
         expression = if (!id %in% open)                     # or the blockr_invalid() that building it signals,
           tryCatch(build_block_expression(cls, blk$state, inputs), blockr_invalid = identity))   # while another error stops the app
  })
}

block_expression_for <- function(req, lock = NULL) {         # for every evaluation
  if (is.null(lock)) {                                       # without both locks: the request's recipe
    rec <- req$recipe
    return(build_block_expression(block_registry[[rec$registry_id]], rec$state, input_ids(rec$inputs)))
  }
  fixed <- lock[[req$block]]
  if (is.null(fixed)) refuse("The locked board has no block ", req$block)
  refuse_unless_opening(req, fixed)                          # inputs of other blocks, or a locked block's other state
  fixed$expression %||% build_block_expression(fixed$cls, req$recipe$state, fixed$inputs)   # a block left open: its state from the request
}
```

### Versions

The protocol has a version of its own, apart from the JS API major that modules declare ([UI modules in JS](Rewrite-1.1.7#the-contract)), the format, the versions of shapes and the package versions that a JSON board records ([Serialization](Rewrite-1.1.4#files)) and a block's revision, which names its result ([Evaluation in the client](Rewrite-1.1.10#revisions)).
Its major changes only for what an existing peer would misread, and both sides ignore properties they do not know, as [shinyreact's protocol](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/protocol/README.md) does.

### The Shiny transport

The client sends each message as text, with `Shiny.setInputValue("blockr", JSON.stringify(message), { priority: "event" })`, for R to decode as [Serialization](Rewrite-1.1.4) has it, since Shiny's own decoding leaves every array a list and flattens a message that is itself an array.
R answers with `session$sendCustomMessage("blockr", message)`, which writes to the websocket at once, so that a request running in the session's process can send progress before it ends.
The transport's observer hands each message to R's queue and returns no promise, so Shiny never holds the session's inputs while a request runs, as it does for an observer that returns one.
How a body travels is the transport's choice too, which [blockr.core#455](https://github.com/BristolMyersSquibb/blockr.core/pull/455) settled by measuring (notes).
A later `hello` drops the bodies that the transport holds for the session too, those that requests posted and those that wait for the client to fetch them, since it starts the session afresh (above).
Leaving Shiny later replaces this module and nothing else.

The transport calls `session$allowReconnect(TRUE)`, so that a page whose session the server ended while the page lived on, after a network drop longer than the server waits or a server restart, starts a new session with a `hello`, and keeps its board (above).
An R process that exits ends the page instead: Shiny Server's proxy closes the page's connection with a code that forbids a new session, and its client covers the page until the user reloads it, so the board then survives as session management last saved it ([Session management as a client extension](Rewrite-1.6)).
Keeping a page alive through a crash, by hiding that cover or starting a new session when the user asks, goes against what the proxy signals and is left for later, which the protocol allows already, since a client that holds a board keeps it through a new session's `hello`.

## Open questions

None.

<details><summary>Notes for implementers</summary>

An interrupt stops compiled code only at its next check, as the review of [Evaluation in the client](Rewrite-1.1.10) measured.
With `mirai::stop_mirai()`, on one daemon with `cleanup = FALSE`, the daemon was free again at once after `Sys.sleep(30)`, but only 1.5 s after the interrupt during `lm()` on 2e7 rows, and with `callr::r_session$interrupt()`, `lm()` stopped 4.4 s and `sort(runif(2e8))` 44 s after it, while every worker kept the results it held.
A promise cannot be cancelled: promises 1.5.0 exports nothing to cancel, and shiny 1.14.0's `ExtendedTask` has only `invoke()`, `status()` and `result()`.

How a request runs was measured on shiny 1.14.0 and mirai 2.7.3, with an app whose requests took 2 s, driven over its websocket.
An `ExtendedTask` calls its function synchronously inside `invoke()`, so in the session's process it is a direct call behind a queue from which nothing can remove an invocation.
With 33 messages queued during a request, Shiny handled all of them before the next request started, which its documentation does not promise.
A request that called `session$sendCustomMessage()` reached the client every 0.5 s while it ran.
In a mirai daemon with dispatcher, `stop_mirai()` interrupted a running task within 15 ms, and the daemon took the next task at once, its state intact.

A request's function reports progress through core, with `report_progress(value, message)`, which sends it as progress notes, rather than through Shiny's `withProgress()`, whose messages Shiny's own client draws as a notification.
The export of blockr.md reports none today: it runs pandoc in a `downloadHandler()` ([R/md-server.R#L212-L270](https://github.com/BristolMyersSquibb/blockr.md/blob/32e088884d825813fb7ff0afc7d023df9e70a3b6/R/md-server.R#L212-L270)).
R's `setTimeLimit()` stopped an R loop at 1.01 s but let `Sys.sleep(3)` run its full 3 s, which is one reason no request times out.

A worker holds the results, since downstream blocks bind them, so every request that reads them runs there too, the browser's included, which reach it through the session's process, since the proxy reaches only the app's own process, so that only replies cross and no data does.
It needs no block registry, lock or protocol of its own, since the session's process can build every call that reads results, the block expression and the calls of `block_eval()`, of the summary, of the output and of a block class's request, for the worker to evaluate in its environment of results, loading the packages those calls name as they run.
What it needs copied in and kept in step is the code and settings those calls use beyond packages: the functions that the app script defines, the R options the app script set, the data passed to `serve()`, and the visitor's session token.
A mirai daemon resets its global environment after each task unless started with `cleanup = FALSE`, inherits environment variables but not R options, and receives with each task the environment its function was defined in, 3.9 MB for a function defined inside a Shiny server function against 592 bytes for one defined at top level, so each request's function is one of core's, which serializes as a reference to its namespace.
A task in a daemon cannot reach the session, so its progress needs a channel of its own.
A worker per session is a second R process, 137 MB resident with blockr.core loaded and no data, against 64 MB for bare R, and a pool of workers per session would move results between them, which cost the blockx prototype at cynkra 17 to 18 s against 4 to 9 s of evaluation over its largest board's 54 computations ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)).

Shiny Server and Connect wrap Shiny's websocket in shiny-server-client, which lets Shiny start a new session only when the server closes the connection with a 47xx code ([lib/main.js#L133-L153](https://github.com/rstudio/shiny-server-client/blob/92cbc96583f958f4e379120323fb3a48c2e61fd5/lib/main.js#L133-L153)), as Shiny Server does for a session it no longer knows after a network drop and for its own restart.
For an R process that exits, it closes the connection with `APP_EXIT`, 4503, which its table of codes describes as "Process exit with error (don't automatically restart)" ([lib/proxy/sockjs.js#L191-L235](https://github.com/rstudio/shiny-server/blob/4445750261a0d3ce4f303a14934d132be805f450/lib/proxy/sockjs.js#L191-L235), [lib/proxy/errorcode.js#L32-L55](https://github.com/rstudio/shiny-server/blob/4445750261a0d3ce4f303a14934d132be805f450/lib/proxy/errorcode.js#L32-L55)), and the wrapper covers the page with an overlay that takes every click, where Shiny's own lets clicks through.
Connect's proxy is closed source, and Shiny documents a new session after a reconnect for Connect 1.5.10 or later ([Reconnecting to Shiny apps](https://shiny.posit.co/r/articles/improve/reconnecting)), while locally only `session$allowReconnect("force")` reconnects.
When it reconnects, shiny.js 1.14.0 sends the new session the last value of every input, the transport's last message among them, and then the messages queued while the page was offline, all of which R ignores until the session's `hello`, the replayed last message included, since the transport ignores the value that an input starts a session with ([blockr.core#455](https://github.com/BristolMyersSquibb/blockr.core/pull/455)), before the client's own `hello` starts the session afresh.

How a body travels was settled by measuring as the transport was built ([blockr.core#455](https://github.com/BristolMyersSquibb/blockr.core/pull/455)).
A body from R of up to the blockr option `max_message_body` bytes, by default 1 MiB, or 4 MiB in binary frames, goes in its reply's message, as base64 in the JSON, a third larger, and a larger one from a session-scoped URL that `session$registerDataObj()` serves, which the browser fetches itself, so that a download streams to disk and no large body holds up the messages behind it on the websocket ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)).
A body goes in a binary frame from `session$sendBinaryMessage()` only where the blockr option `message_body_encoding` is `"binary"`, which is off by default, since Shiny Server's proxy writes each message of R's into the page's channel as text.
A body from the client is posted to another such URL, which R gives the client in the message that starts each session, `{ "body_url": ..., "max_request_size": ... }`, so that the deployment's `shiny.maxRequestSize` still limits it, while the client never goes through Shiny's `uploadInit`, which was never faster.
Core's output classes carry one page of rows as JSON, so core needs no Arrow writer, and an output class that needs one brings its own.

</details>
