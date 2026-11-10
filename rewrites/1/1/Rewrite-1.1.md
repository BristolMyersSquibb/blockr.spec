# Client-owned board state
Status: implementing in [blockr#503](https://github.com/orgs/BristolMyersSquibb/discussions/503). Part of [State in JS](Rewrite-1).

This part covers blockr.core: the client's store, command registry and scheduler, the wire protocol and R's per-session evaluator, block classes and the modules that draw their UIs, plugins, opening, saving and serving a board, and core's basic frontend with the API every plugin draws on.
Every other part builds on it, and its design pages set out each API.

## Problem

Of blockr.core's 18,353 lines of R, 7,405 hold the board and run it in the session's R process, on its one thread (Today, below): the board and block servers, which run board management, block construction, demand and visibility gating and every block's UI logic as Shiny reactives, the plugins, the lock and the generics that draw UI.
Evaluation, the only part that needs R, waits behind all of it, and [State in JS](Rewrite-1#problem) sets out what that has led to.

## What must hold

Conditions 1 to 6 of [State in JS](Rewrite-1#what-must-hold) rest on this part, and so does this one:

1. A block's R side is plain functions: its expression from its state and data inputs, and what its UI needs from the same.
2. Where the load lock and the board lock are both on, R evaluates only the opening board's blocks, with their opening links, and every locked block with its opening state, whatever a client sends.

## Today

| Today, at `da3fcb4` | Lines | Where it goes |
|---|---|---|
| Board and block servers, plugins, stack gating, notifications and the generics that draw UI | 7,358 | Replaced by the store and commands ([Board updates](Rewrite-1.1.2)), the scheduler ([Evaluation in the client](Rewrite-1.1.10)) and frontends ([Drawing the board](Rewrite-1.1.8)), while [Plugins](Rewrite-1.1.12#today) gives each of today's plugins its new home |
| The JS of today's UI, `changeBoardTitle.js`, `minimalPreviewWidth.js` and `moveBlockUi.js` | 55 of JS | Replaced by core's client ([Drawing the board](Rewrite-1.1.8)) |
| Locked boards, through `blockr.locked` and `is_board_locked()` | 47 | Carried over as the board lock, beside a lock on each block and a load lock, which fixes the app to its opening board, where today's dock restores any board, while R refuses what breaks the board lock or a block's lock in what it runs ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)) |
| Board options and their Shiny UIs | 1,274 | Constructors carried over, each taking its value alone, with the values in the board and the rest of each board option, its default and UI included, defined in the client ([Board options and blockr options](Rewrite-1.1.13)), but for `board_name`, which the board's name replaces, `thematic`, since plots follow the theme in their `info` ([Block classes in R](Rewrite-1.1.5#outputs)), `page_size`, since `n_rows` gives the rows of a table output's page, `filter_rows`, since table outputs page in R and have no search, and `llm_model`, which moves to the assistant ([Assistant as a client extension](Rewrite-1.4)) |
| The `serve()` generic and board loaders | 525 | The generic carried over, serving core's client and the board's frontend, while the loaders go, since the store opens a board in place ([Defining a board in R](Rewrite-1.1.3)), and `blockr_test_exports()` gives way to what core exports for end-to-end tests ([Drawing the board](Rewrite-1.1.8#testing)) |
| Board, block, link and stack classes | 2,298 | Constructors and accessors carried over, for app scripts, and setters and modifiers dropped, while the live state moves to the client ([Board objects](Rewrite-1.1.1), [Defining a board in R](Rewrite-1.1.3#the-script)) |
| The block class and its specializations, the block registry, roclet and metadata, arg specs and evaluation | 3,114 | Replaced by `new_block_class()`, with the block registry, the roclet and the arg specs carried over ([Block classes in R](Rewrite-1.1.5)) |
| Built-in blocks, with the tabular display and `str_value()` | 1,264 | Ported to block classes, and the tabular display replaced by renderers of table outputs ([Block classes in R](Rewrite-1.1.5), [Drawing the board](Rewrite-1.1.8#renderers)) |
| Serialization, code export and expressions | 813 | Carried over: the serializer for an app script's board, while reading and migrating today's files goes to a conversion outside core ([Serialization](Rewrite-1.1.4)), and `export_code()`, on which blockr.code builds its request ([Code export as a client extension](Rewrite-1.5)) |
| Utilities | 1,484 | Carried over in R and not ported ([State in JS](Rewrite-1#principles)) |
| Test helpers on a mock Shiny session | 176 | Replaced by helpers that need no Shiny ([Block classes in R](Rewrite-1.1.5#testing)) |

## Proposal

- The board is plain data held by a TypeScript store in core's JS API, in which each block names its class by registry id and each plugin its class by the class's id, while no object carries an R class ([Board objects](Rewrite-1.1.1)).
  Plugins are core's second way to extend a board, beside block classes, in place of board classes, core's plugins of today and the dock's extensions: what a package adds to a board, its frontend and its storage among them, is a plugin that the board holds, whose state core carries without reading it and which core's command and the plugin's own commands change ([Plugins](Rewrite-1.1.12)).
  Every edit, by the user or a plugin, the assistant among them, is a delta, in the `add`, `mod` and `rm` shape of today's `update()` for core's objects, in which the assistant stages its edits already, and as patches inside a plugin's state, and the same deltas give undo ([Board updates](Rewrite-1.1.2)).
- All edits run through one command registry, which menus, shortcuts, plugins and the assistant's tools call alike ([Board updates](Rewrite-1.1.2#commands)).
  It replaces the dock's action registry and what core's plugins of today do to the board, while what they draw and keep goes to the frontend or to a plugin of the new kind, as code export goes to blockr.code's plugin ([Plugins](Rewrite-1.1.12#today)).
- An app is still an R script that calls `serve()` on a board built with constructors, and that board becomes the client's opening board ([Defining a board in R](Rewrite-1.1.3)).
  The client opens every board, at startup or from a file, itself, as a JSON board, migrating what it holds in an older shape in JS, by the versions of its shapes that it records, and dropping what the app cannot rebuild, with the block registry's entries of the reply to `hello`, while R loads no package for a board, since the app names the packages it offers, whose block classes R reads as the app starts ([Block classes in R](Rewrite-1.1.5#registration), [Board updates](Rewrite-1.1.2#opening-a-board), [Wire protocol](Rewrite-1.1.9#opening-a-board)).
  Saving and restoring needed core today, since a restore is a `session$reload()` that the app's `board_loader()` handles ([R/utils-serve.R#L277-L288](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L277-L288)); here opening a board starts core again in place, with no reload, which is all session management needs ([Drawing the board](Rewrite-1.1.8#opening-a-board)).
  The client saves a board as a JSON board, the board itself with the versions of the shapes it holds and of the packages its content comes from, in the one format in which R writes the opening board too ([Serialization](Rewrite-1.1.4)), and core's own storage plugin saves one only as a download, while where else it is saved, such as to Connect or a draft, is the storage plugin of session management, built on the store and on the plugin's requests ([Plugins](Rewrite-1.1.12#storage), [Session management as a client extension](Rewrite-1.6)).
- R is an evaluator, one process per session, holding results and no board state.
  An evaluation request carries the recipe, a block's registry id and state with its inputs as upstream block ids and revisions, and R builds the block expression from its class's `expr` and runs it with `block_eval()`, keeping the latest result by block id and revision, never by process, so a client that starts a new session with its board loses only recomputation ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)).
  A block class is a value defined once, from which its constructor is made, and R calls a constructor only where a board is built ([Block classes in R](Rewrite-1.1.5)).
  A result is any R object, which the coercion its block class names turns into an output, so nothing in the protocol assumes a table, drawn by the renderer that the class's method of `output_renderer()` gives, which the package defining the class writes, and which an app replaces with another package's renderer, such as a UI kit's, through a blockr option and without touching a block class, while S3 dispatch gives a subclass its class's renderer ([Drawing the board](Rewrite-1.1.8#renderers)).
  A reply carries the block's status, summary and conditions, and the client decides which to show, so `show_conditions` stays a board option of core's, which a frontend reads to choose the severities it shows, while R reports every severity.
- The client schedules.
  It bumps a block's revision on every change to its recipe, its state or the links into it, or to anything upstream of it, the way spreadsheets and notebooks track their cells, keeps the last results on screen, and evaluates what is demanded, and everything upstream of it, by the evaluation priority each demand gives and in topological order within one, which replaces construction ordering, the render gate and the visibility channels in R ([Evaluation in the client](Rewrite-1.1.10)).
  Board options never reach `expr`: one that shapes outputs redraws them without re-evaluating, and a block that reads relative to a directory takes the directory as an input.
  What is demanded is what the frontend shows, every block under core's basic frontend, together with what other plugins and packages demand, such as blockr.io for a write block in auto mode ([Evaluation in the client](Rewrite-1.1.10#demand)).
- A block's UI is an ES module that core mounts with an injected host, under a contract free of any framework ([UI modules in JS](Rewrite-1.1.7)).
  Core ships the one copy of React on the page, with the React SDK, and draws its own UIs with it, in TSX: those of its built-in blocks, its renderers, its board options and its basic frontend ([UI modules in JS](Rewrite-1.1.7#react)).
  A block package writes its UI as it likes: in React, as TSX the way an app writes a `ui.tsx` in shinyreact's pattern ([README.md#L18-L22](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/README.md#L18-L22)), with `react` mapped to core's copy, or in plain TypeScript or JS.
  Core loads JS only, so every package's JS ships inside its R package, built by the package where it is written in TSX, and nothing goes to npm for now.
  Core treats the UI as a black box ([Principles](Principles#authors-own-their-blocks-and-core-treats-a-blocks-ui-as-a-black-box)), so input elements composed in R leave core, while the React SDK holds the inputs that core's own UIs draw with, and richer ready-made components for form-like UIs may come later from blockr.ui.
  The JSON a module exchanges with R is private to its block class, and the arg specs describe args for LLMs and tools, while a block's UI decides their shapes and ships their schema ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)).
- Core ships a basic frontend, which draws every board that holds no frontend, so a board serves without blockr.dock, while a frontend such as the dock is a plugin, which draws the board that holds it ([Plugins](Rewrite-1.1.12#the-frontend)).
  A frontend draws everything around a block and works on the board through `CoreApi`, while core mounts the block's UI and output, and the UI of every other plugin where the frontend places it, so a block class and a plugin work under every frontend and nothing in R draws UI ([Drawing the board](Rewrite-1.1.8)).
- Core has a JS API and an R API, with a versioned wire protocol between them that both sides test against shared fixtures, as shinyreact does ([Wire protocol](Rewrite-1.1.9)).
  R builds every block's expression from its class's `expr`, so the code that blockr.code exports is the code that ran.
  A block may parse a string into code, so a board runs arbitrary R code, and the deployment sandboxes the R process ([Principles](Principles#a-board-runs-arbitrary-r-code-and-the-deployment-sandboxes-the-r-process)), while R decodes what the client sends into plain values, which only keeps a value a value ([Wire protocol](Rewrite-1.1.9#decoding)).
  Access is the deployment's too: core knows nothing about users, since access is the data source's, through the process's file permissions or an API client's own token, and results are never shared between sessions, since what a read returns can depend on who runs it.
- An app sets three locks, each on its own: the load lock fixes the app to its opening board, the board lock fixes the board's blocks, links and stacks and the names of its plugins, and a block's lock fixes the block's state under the board lock, while board options stay open, since none reaches what R evaluates ([Locked boards and the properties of blocks](Rewrite-1.1.11)).
  The store refuses what they fix, and R refuses an evaluation that rebinds a block's data inputs or gives a locked block another state, so that, with the load lock on too, no client can loosen the locks, since R takes every block's class and input bindings, and a locked block's whole block expression, from what it builds when the app starts ([Locked boards and the properties of blocks](Rewrite-1.1.11#what-r-refuses)).
  A plugin, a frontend among them, may lock more of what it alone governs, as the dock does the arrangement of its panels.
- Other requests belong to an object too, as a block's belong to its class: to an output class, for what its renderers offer beyond the output, such as a download of what they show, to a renderer, for what it alone offers, such as the labels of a table's columns, to a board option, as blockr.io's data directory lists the server's directories, or to a plugin ([Plugins](Rewrite-1.1.12#a-plugins-requests)), for work that belongs to no single block and needs R or the server, such as code generation in blockr.code, or exchanging a visitor's Connect session token, which only the content's process receives, for the key that session management's storage calls then use from the browser ([Session management as a client extension](Rewrite-1.6)).
  A block class's request reads the block's inputs at given revisions, with the state args and parameters it names and the board options that its `new_block_request()` names, so the client caches its answers by them unless the class makes the request volatile or an action, which may write.
  An output class's request, or a renderer's, reads the result its output was made from, with the board options and parameters that output was asked with, and is cached as the output is, while a board option's or a plugin's request may write and is never cached ([Wire protocol](Rewrite-1.1.9#requests)).
  There is no generic request for a column's values: a value list is a block class's own request, bounded by its author.
  Effects need no mechanism of their own: a write is a block expression, which a write block's `block_eval()` method runs in auto mode, and in manual mode only when its save button asks, through a one-time evaluation with a parameter ([Block classes in R](Rewrite-1.1.5#evaluation)), an upload is a request its class marks as an action, which runs once per call and may write, and a download is a request whose answer is a file with its name ([UI modules in JS](Rewrite-1.1.7#the-contract)).
- Shiny stays as host and transport for now, since on Connect a Shiny app with *Max connections per process* at 1 gives each session its own process.
  A small module, the Shiny transport, carries the protocol ([Wire protocol](Rewrite-1.1.9#the-shiny-transport)), rather than shinyreact, whose API is React hooks and components and has no request and response, and leaving Shiny later replaces that module.

## Open questions

None.

## Work

The spec [blockr#503](https://github.com/orgs/BristolMyersSquibb/discussions/503) holds the Work list from here, each item with its issue.

## Design pages

- [Board objects: blocks, links, stacks, board options and plugins](Rewrite-1.1.1): the objects the client holds for a board, how a block names its class, and where a package keeps what it adds to core's objects
- [Board updates: deltas, commands and undo](Rewrite-1.1.2): the store, deltas, the state of plugins, commands, opening a board, undo, and following the board
- [Defining a board in R for the client-owned board](Rewrite-1.1.3): the app script, the opening board and how R writes it, `serve()` and data passed to it
- [Serialization of the client-owned board](Rewrite-1.1.4): JSON boards, state values between the client and R, and migrations
- [Block classes in R for the client-owned board](Rewrite-1.1.5): `new_block_class()`, expressions and interpolation, requests, core's classes and hooks, registration, evaluation, output classes, generics and testing
- [UI modules in JS: the host, React and packaging](Rewrite-1.1.7): the host a module receives, startup modules, React, packaging and testing
- [Drawing the board: `CoreApi`, the page, core's basic frontend and renderers](Rewrite-1.1.8): what core gives plugins through `CoreApi`, starting the page, opening a board, core's basic frontend, renderers, what a package declares in R, what goes from R, and testing
- [Wire protocol between the client and R](Rewrite-1.1.9): messages, the handshake, opening a board, blockr options, evaluation, requests, outputs, running one request at a time, cancelling, forgetting, decoding, locked boards, versions and the Shiny transport
- [Evaluation in the client: revisions, demand and statuses](Rewrite-1.1.10): revisions, demand, invalidation, statuses and scheduling
- [Locked boards and the properties of blocks](Rewrite-1.1.11): the load lock, the board lock and block locks, board options and plugins on a locked board, what R refuses, serving a JSON board locked, the locks in the reply to `hello`, what a plugin keeps about a block, and a block's properties in R
- [Plugins for the client-owned board](Rewrite-1.1.12): what a plugin is in R and in JS, plugin classes, the frontend and storage plugins, which plugins a board has, and a plugin's state, in place of board classes and the dock's extensions
- [Board options and blockr options](Rewrite-1.1.13): the two kinds side by side, defining a board option, which board options a board holds, the renderer before the first output, how R and the client read a board option's value, locked boards, blockr options, and where the two kinds meet
- [Notifications, logging and tracing: what the user is told and what is recorded where](Rewrite-1.1.14): one member of `CoreApi` for every message, warning and error that the user should see, whoever raised it, the API through which packages log in R and in the client with the logger that a deployment swaps, and the spans that join the client's work and R's into one trace

<details><summary>Notes for implementers</summary>

The rows of Today by file, at `da3fcb4` with roxygen included: the servers are `block-server.R`, `block-ui.R`, `board-plugins.R`, `board-server.R`, `board-ui.R`, the nine `plugin-*.R` files, `stack-gate.R`, `stack-ui.R` and `utils-shiny.R`; locking is `board-lock.R`; board options are `board-option.R` and `board-options.R`; serving is `utils-serve.R` and `board-loader.R`; the classes are `blocks-class.R`, `board-class.R`, `link-class.R`, `links-class.R`, `stack-class.R` and `stacks-class.R`; block classes are `arg-spec.R`, `block-class.R`, `block-eval.R`, `block-meta.R`, `block-registry.R`, `block-roclet.R` and the six specializations, `data-block.R` to `transform-block.R`; the built-in blocks are the twelve files with a constructor, `tabular-display.R` and `str-value.R`; serialization is `utils-serdes.R`, `utils-code.R` and `utils-expr.R`; the utilities are the other `utils-*.R` files and `zzz-onload.R`; and the test helpers are `utils-tests.R`.
Of the packages blockr.core imports at `da3fcb4`, reactives goes with the board servers, bslib with the UI that R draws, while bsicons stays, since the block registry draws its icons with it ([blockr.core#447](https://github.com/BristolMyersSquibb/blockr.core/pull/447)), and typedjson leaves with reading today's files, which a conversion outside core does in a mode that refuses code, while yyjsonr comes in to decode what the client sends ([Serialization](Rewrite-1.1.4)).

Inside core's client, signals come from `@preact/signals-core`, the store checks values against the JSON Schemas that plugin classes and board options register with [@cfworker/json-schema](https://www.npmjs.com/package/@cfworker/json-schema), which interprets drafts 4 to 2020-12 and generates no code, so that a content security policy that forbids eval does not break it, where Ajv would compile each schema with `new Function` and take 131 of the store's 167 KiB, and core generates the board's JSON Schema from its TypeScript types with ts-json-schema-generator, beside the types it ships ([UI modules in JS](Rewrite-1.1.7#packaging)).
Core's UIs draw with React 19, of which core's runtime bundles the one copy on the page ([UI modules in JS](Rewrite-1.1.7#react)).

The Work list's first issues, [blockr.core#393](https://github.com/BristolMyersSquibb/blockr.core/issues/393) to [blockr.core#404](https://github.com/BristolMyersSquibb/blockr.core/issues/404), were opened before the design pages settled and closed as not planned.
Their bodies and comments hold prior art and detail that the issues opened again take over, such as the stores of Excalidraw and Figma on [blockr.core#394](https://github.com/BristolMyersSquibb/blockr.core/issues/394), the schedulers of Excel, Observable and Incremental on [blockr.core#395](https://github.com/BristolMyersSquibb/blockr.core/issues/395), and the execution model on [blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400).

Related specs: [blockr#489](https://github.com/orgs/BristolMyersSquibb/discussions/489) and [blockr#488](https://github.com/orgs/BristolMyersSquibb/discussions/488) rework visibility, demand and status within the R board.
Here visibility and demand become client scheduling, and the statuses of [blockr#488](https://github.com/orgs/BristolMyersSquibb/discussions/488) become what R reports per evaluation, with staleness tracked by the client.

</details>
