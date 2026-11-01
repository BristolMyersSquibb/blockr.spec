# State in JS
Status: review.

State in JS moves board state from R to the browser: the client becomes the only writer of the board, and R evaluates what it is sent. Core is rewritten around a client-side store, the dock is drawn in the browser, the extensions are rebuilt on the dock's client API, and the block packages are ported to block classes.

## Problem

Board state lives in R. The `board_server()` function of blockr.core holds the blocks and their args, links, stacks and board options, and runs board management, block construction, demand and visibility gating and every block's UI logic as Shiny reactives in the session's R process, on its one thread. Evaluation, the only part that needs R, waits behind all of it.

Much of core's recent work goes into working around this: deferred and prioritized construction ([blockr.core#243](https://github.com/BristolMyersSquibb/blockr.core/issues/243), [blockr.core#275](https://github.com/BristolMyersSquibb/blockr.core/issues/275)), the render gate ([blockr.core#257](https://github.com/BristolMyersSquibb/blockr.core/issues/257)), and the visibility channels [blockr#489](https://github.com/orgs/BristolMyersSquibb/discussions/489) moves out of core. Where the client holds state too, the two copies need guarding: blockr.dplyr's `js-block.R` keeps an echo guard, message priorities, a client-side queue and a ready handshake ([blockr.core#317](https://github.com/BristolMyersSquibb/blockr.core/issues/317)) only to keep a block's state in step between JS and R. The dock, which draws the board from R with DOM operations, shows the same split: 37 of 100 defects in the shell's history are that protocol failing ([blockr#493](https://github.com/orgs/BristolMyersSquibb/discussions/493)).

## What must hold

1. The client is the only writer of board state, opened boards and AI edits included.
2. R holds results and no board state. It evaluates what it is sent, so a client that starts a new R session with its board loses only recomputation.
3. A board edit costs no R time beyond evaluating what is demanded and fetching data for what is on screen, except what an app has R evaluate in the background while it has nothing else to run ([Evaluation in the client](Rewrite-1.1.10#demand)).
4. Boards written by today's `blockr_ser()` open, with the dock's views and layouts and the DAG's positions, for block classes that have been ported ([Serialization](Rewrite-1.1.4)).
5. A full app is still defined by R code calling board and block constructors ([Defining a board in R](Rewrite-1.1.3)), and a block is still an S3 object.
6. The [design system](https://bristolmyerssquibb.github.io/blockr.ui/articles/design-system.html) documented in blockr.ui stays valid, so the dock and the extensions follow it, while core's client builds on Tailwind CSS ([Front-ends and extension points](Rewrite-1.1.8#cores-basic-front-end)).

## Principles

This is the second rewrite of blockr, and it must not undo what the first one fixed. The first blockr (2023 to 2024) built each block from fields, typed values from which the framework generated the block's UI and server. Logic between fields, such as one field's choices following another's selection, was hard to write, and a UI the field set lacked took a new field type. Inputs derived from an upstream result could not be written, and a custom output meant overriding the generated server. The rewrite into blockr.core and the packages around it handed each block to its author, who writes its UI and logic as a Shiny module that the framework wraps, and replaced linear stacks, which passed results between them through a result field, with links between blocks.

Keep what has served us well:

- Authors own their blocks. An author writes a block's UI and its logic, and core wraps them, supplying what every block shares through specific extension points, such as code generation, evaluation and display.
- Core treats a block's UI as a black box. It assumes nothing that a notion of fields per block would afford, such as knowing a block's inputs, generating them or computing their attributes.
- Two extension points, as blockr.dock's extensions have shown: a block, for logic that belongs to one block, and a board extension, for whatever shows or changes the board as a whole, such as the DAG, tools for bulk changes, AI that works on the whole board, and reports like blockr.md's.
- Well-defined APIs. Keeping blockr in separate packages forced us to think through what each one offers the others.
- A package plugs into another only through a hook the other offers, as `tabular_display()` is today, never by patching what it owns, in JS as in R.
- One shared toolkit per language, used instead of ad-hoc helpers.
- Gates that let nothing through: no lints, no failing tests and a clean check, in TypeScript as in R.

Improve what has not, which the Problem above sets out: state kept in two places, UI logic in R's reactive graph with the workarounds its cost needs, and a dock drawn from R. The same goes for having two ways to extend a board, core's plugins beside the dock's extensions.

Keep edge cases out of core. An edge case goes through an escape hatch core already has, such as a demand, a request, or a method of a generic, as a write block's manual save goes through a `block_eval()` method and a one-time evaluation with a parameter ([Block classes in R](Rewrite-1.1.5#evaluation)), and core grows a new capability only where none fits, and then a general one.

Translate rather than transliterate. The client follows established JS patterns, as the module contract follows anywidget's, and R's idioms stay in R, unless a page gives a strong reason to carry one over, as the last item below does:

- S3 classes stay in R and in the files R reads. Where R dispatches on a class, the client looks the object up by id, as it looks up block classes in the block registry and commands in the command registry, and what the methods did becomes data on one type, so a board option is an instance of one `Option` type rather than a type of its own ([Board objects](Rewrite-1.1.1#board-options)).
- Names follow each language, snake_case in R and camelCase in TypeScript, while the JSON between them keeps the snake_case it has today.
- Core's type-stable helpers, such as `chr_ply()` and `lst_xtr()`, are not ported, since the type checker and the standard library do their work.
- R's lack of scalars stays in R, which converts at the boundary, so the client sees plain JSON values.
- Shiny's reactives become signals for derived values inside core, with effects only at the edges, while core's JS API follows changes through a getter and a subscription, which any framework can use ([UI modules in JS](Rewrite-1.1.7#the-contract)).
- R's conditions become exceptions within JS, and cross the boundary as data that keeps their class.
- Dependencies are passed in, as the host and `CoreApi` are, rather than read from R options or the session where needed.
- What R gave for free is kept on purpose: copy-on-modify becomes a store that never changes a board in place, which read-only types enforce.

## Proposal

- Each piece of state has one writer. The board is plain data held by a TypeScript store in core's JS API, and what R holds is either computed from the board at one moment, as a result is, or handed over once, as the opening board is, so nothing has to be kept in step with it. The table in [Board objects](Rewrite-1.1.1#what-lives-where) gives each object, where it lives and for how long.
- Every edit, by the user, the assistant or an extension, is a versioned delta through one command registry in core, and the same deltas give undo ([Client-owned board state](Rewrite-1.1), [Board updates](Rewrite-1.1.2)).
- Whatever does not need R moves to the browser. R is an evaluator, one process per session. A request carries the recipe, and a result is named by block id and revision, never by process, so a client that starts a new session with its board loses only recomputation, and putting several sessions on one process, or one session on several, stays a server-side change.
- The client schedules: it bumps revisions, tracks what is stale and what is demanded, and requests results by the evaluation priority each demand gives and in topological order within one, which replaces construction ordering, the render gate and the visibility channels in R ([Evaluation in the client](Rewrite-1.1.10)).
- Core keeps no plugin or extension type of its own. The dock is a React app on core's JS API, and board extensions are ES modules that register with it, the only way to extend a board besides block classes, with their logic on core's JS API and their UI in the dock's contribution points ([Client-drawn dock and extensions](Rewrite-1.2)).
- Block UIs keep a contract free of any framework: an ES module mounted with an injected host, which React reaches through its build, from one copy that a package puts on the page, so core ships none ([UI modules in JS](Rewrite-1.1.7)). Whether blockr.ui later offers authors a way to compose a UI without writing JS, such as in R from its components, built on that contract, is still to be decided.
- Core has a JS API and an R API, with a versioned wire protocol between them that both sides test against shared fixtures ([Wire protocol](Rewrite-1.1.9)).
- The code that a board's script exports is the code that ran, since R builds every block's expression from its block class's `expr`, while exporting it is an extension's, blockr.code's, rather than core's. Limiting what the R process may do, and who may read what, is the deployment's job: core knows nothing about users, and results are never shared between sessions.
- Shiny stays as host and transport for now, since on Connect a Shiny app with *Max connections per process* at 1 gives each session its own process. One small bridge module carries the protocol, and leaving Shiny later replaces only that module ([Client-owned board state](Rewrite-1.1)).
- The assistant is a collaborator, editing the board beside the user, which is why collaboration shapes the design now: a delta names its origin, so the user and the assistant each undo their own steps ([Board updates](Rewrite-1.1.2)). Collaboration between people is not built, but stays open on the same terms, with the dock's front-end state holding what opening, saving and restoring a board need, and a later relay free to keep each person's switching between views on their own screen ([Client-drawn dock and extensions](Rewrite-1.2)). Early cutoff is not built either and can come later, opt-in per block class.

## Migration

The switch is one step, since a board mirrored in R would be two owners again. The new client and the slimmer core are built beside the current stack, on a `js-state` branch in every repo the rewrite changes, while main keeps the current stack until the switch. Block packages port one at a time.

## Open questions

None.

## Conventions

- Label: `js-state`, named after the integration branch, on every spec and issue and on the thread.
- Integration branch: `js-state`, in every repo the rewrite changes and in every package between two of them, which needs one for its pins. The first PR in a repo to need it creates it from main, adds it to the branch filters of the repo's workflows, and gives it the rulesets main has. Its revdep check lists no downstream at first, and adds each one, checked at its own `js-state`, once that branch exists.
- Versions: on `js-state` every package carries a 0.2 version, which the switch releases: 0.2.0, or the next patch above main's where main has already reached 0.2.0. So blockr.core goes from 0.1.4 to 0.2.0, and blockr.dock, whose main says 0.2.0, to 0.2.1. A package requires its upstreams at their `js-state` versions, so that a build against main fails at install.
- Pins: a package's `js-state` pins each upstream's in `Remotes:`, as `BristolMyersSquibb/blockr.core@js-state`, and so does every package between them, since pak cannot resolve one package at two refs. The pins come out at the switch.
- Thread: [blockr#502](https://github.com/orgs/BristolMyersSquibb/discussions/502), where comments on any page go.
- Issue footer: "Branch from `js-state` and open the PR against it, creating the branch from main if this is the first PR to need it: that branch collects the client-owned board until the switch, and main keeps the current stack."
- Terms: the [Glossary](Glossary), whose names every page, spec and issue of the rewrite uses in the senses it gives.
- Backlog: the [Backlog](Backlog) lists the small and medium additions beyond parity that are not ready for a spec, each with what it would remove and what it would cost.
- Code: the R code on the pages sketches what an API looks like and how it behaves, and is not to be carried over verbatim. It does not follow the patterns and utilities the blockr packages have settled on, internal ones such as blockr.core's `chr_ply()` family, `coal()` and `blockr_abort()`, which a sketch writes as `vapply()`, `is.null(x) ||` and `stop()`, and third-party ones such as rlang, vctrs and cli, so an implementation adapts it to the package it lands in. Adapting it is no departure from the pages.
- TypeScript: client code is strict TypeScript, or JS checked through `// @ts-check`, gated in each package's CI by `tsc`, typescript-eslint and Vitest on happy-dom, and a package that builds bundles its modules with esbuild into `inst/`, which it commits, while CI checks that a rebuild changes nothing there ([UI modules in JS](Rewrite-1.1.7#packaging)).
