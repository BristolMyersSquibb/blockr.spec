# State in JS
Status: draft.

State in JS moves board state from R to the browser: the client becomes the only writer of the board, and R evaluates what it is sent. Core is rewritten around a client-side store, the dock is drawn in the browser, the extensions are rebuilt on the dock's client API, and the block packages are ported to block types.

## Problem

Board state lives in R. The `board_server()` function of blockr.core holds the blocks and their args, links, stacks and options, and runs board management, block construction, demand and visibility gating and every block's UI logic as Shiny reactives in the session's R process, on its one thread. Evaluation, the only part that needs R, waits behind all of it.

Each node the reactive core re-runs costs about 1.4 ms (Shiny 1.14 on the dev workspace; 1.7.5 and 1.11.1 measure the same), against about 0.15 µs for a JS signals library on the same machine, so an edit that re-runs a few hundred nodes is a visible pause before any evaluation starts.

Much of core's recent work goes into working around this: deferred and prioritized construction ([blockr.core#243](https://github.com/BristolMyersSquibb/blockr.core/issues/243), [blockr.core#275](https://github.com/BristolMyersSquibb/blockr.core/issues/275)), the render gate ([blockr.core#257](https://github.com/BristolMyersSquibb/blockr.core/issues/257)), and the visibility channels [blockr#489](https://github.com/orgs/BristolMyersSquibb/discussions/489) moves out of core. Where the client holds state too, the two copies need guarding: blockr.dplyr's `js-block.R` keeps an echo guard, message priorities, a client-side queue and a ready handshake ([blockr.core#317](https://github.com/BristolMyersSquibb/blockr.core/issues/317)) only to keep a block's state in step between JS and R. The dock, which draws the board from R with DOM operations, shows the same split: 37 of 100 defects in the shell's history are that protocol failing ([blockr#493](https://github.com/orgs/BristolMyersSquibb/discussions/493)).

## What must hold

1. The client is the only writer of board state, opened boards and AI edits included.
2. R holds results and no board state. It evaluates what it is sent, so losing the R process costs recomputation, never the board.
3. A board edit costs no R time beyond evaluating what is demanded and fetching data for what is on screen.
4. Boards written by today's `blockr_ser()` open, for block types that have been ported.
5. A full app is still defined by R code calling board and block constructors, and a block is still an S3 object.

## Proposal

- Each piece of state has one writer. The board is a document held by a TypeScript store in core's JS API, and what R holds is either computed from one version of it, as a result is, or handed over once, as the opening board is, so nothing has to be kept in step with it. The table in [Document model](Rewrite-1.1.1#what-lives-where) gives each object, where it lives and for how long.
- Every edit, by the user, the assistant or an extension, is a versioned delta through one command registry in core, and the same deltas give undo ([Client-owned board state](Rewrite-1.1), [Board updates](Rewrite-1.1.2)).
- Whatever does not need R moves to the browser. R is an evaluator, one process per session. A request carries the recipe, and a result is named by block id and version, never by process, so a lost process costs only recomputation, and putting several sessions on one process, or one session on several, stays a server-side change.
- The client schedules: it bumps versions, tracks what is stale and what is demanded, and requests results in topological order, which replaces construction ordering, the render gate and the visibility channels in R ([Evaluation in the client](Rewrite-1.1.10)).
- Core keeps no plugin or extension type of its own. The dock is a React app on core's JS API, and extensions are ES modules that register with it, the one extension mechanism, with their logic on core's JS API and their UI in the dock's contribution points ([Client-drawn dock and extensions](Rewrite-1.2)).
- Block UIs keep a contract free of any framework: composed in R from the input elements core ships, or an ES module mounted with an injected host, which React reaches through its build ([Input elements](Rewrite-1.1.6), [UI modules in JS](Rewrite-1.1.7)).
- Core has a JS API and an R API, with a versioned wire protocol between them that both sides test against shared fixtures ([Wire protocol](Rewrite-1.1.9)).
- The code a block shows and exports is the code that ran, since R builds every expression with the block type's `interpolate`. Limiting what the R process may do, and who may read what, is the deployment's job: core knows nothing about users, and results are never shared between sessions.
- Shiny stays as host and transport for now, since on Connect a Shiny app with *Max connections per process* at 1 gives each session its own process. One small bridge module carries the protocol, and leaving Shiny later replaces only that module ([Client-owned board state](Rewrite-1.1)).
- Collaboration is not built, but stays open: a delta names its origin ([Board updates](Rewrite-1.1.2)), and the dock's fields hold only what everyone who opens a board shares ([Client-drawn dock and extensions](Rewrite-1.2)). Early cutoff is not built either and can come later, opt-in per block type.

## Migration

The switch is one step, since a board mirrored in R would be two owners again. The new client and the slimmer core are built beside the current stack, on a long-lived `js-state` branch of blockr.core, created from main with the first PR, that feature branches merge into, while main keeps the current stack until the switch. Block packages port one at a time, and deployments stay on the current stack until parity.

Documents written by today's `blockr_ser()` are the point of compatibility: they open in the new stack for block types that have been ported ([Serialization](Rewrite-1.1.4), [blockr.core#402](https://github.com/BristolMyersSquibb/blockr.core/issues/402)), with the dock's views and layouts and the DAG's positions. App scripts keep calling board and block constructors ([Defining a board in R](Rewrite-1.1.3)), and blocks stay S3 objects.

## Open questions

- Whether every repo the rewrite changes gets a `js-state` branch, as blockr.core does, how those branches pin each other in `Remotes:`, and how their versions move ahead of main's.
- Whether `js-state` gets main's rulesets, the merge queue and required reviews. Its first PR has to extend CI to it in any case, since the workflows run only on PRs to main.
- The parity list the switch waits for, and the order in which deployments move.
- What is released while the rewrite runs, besides fixes from main, and how the switch is released.
- What happens to the repos marked as not decided below, and the plans for the block packages.

## Parts

| Repo | Change | Page | Builds on |
|---|---|---|---|
| blockr.core | Rewritten | [Client-owned board state](Rewrite-1.1) | |
| blockr.dock | Rewritten | [Client-drawn dock and extensions](Rewrite-1.2) | blockr.core |
| blockr.dag | Rebuilt as a dock extension | [Client-drawn DAG extension](Rewrite-1.3) | blockr.dock |
| blockr.assistant | Rebuilt as a dock extension | [Assistant as a client extension](Rewrite-1.4) | blockr.dock |
| blockr.code | Rebuilt as a dock extension | [Code export as a client extension](Rewrite-1.5) | blockr.dock |
| blockr.session | Rebuilt as a dock extension | [Session management as a client extension](Rewrite-1.6) | blockr.dock |
| blockr.dplyr | Ported | Not written | blockr.core |
| blockr.ggplot | Ported | Not written | blockr.core |
| blockr.io | Ported | Not written | blockr.core |
| blockr.dm | Ported | Not written | blockr.core |
| blockr.cdex | Ported | Not written | blockr.core |
| blockr.sandbox | Ported | Not written | blockr.core |
| blockr.ui | Not decided | | |
| blockr.ai | Not decided | | |
| blockr.md | Not decided | | |
| blockr | Not decided | | |
| blockr.uat | Not decided | | |
| reactives | Not decided | | |
| typedjson | Not decided | | |
| dockViewR | No longer used | None | |
| g6R | No longer used | None | |

## Conventions

- Label: `js-state`, named after the integration branch, on every issue and on the thread.
- Integration branch: `js-state`, in blockr.core. Other repos are an open question.
- Versions and pins: open questions.
- Thread: [blockr#502](https://github.com/orgs/BristolMyersSquibb/discussions/502), where comments on any page go.
- Issue footer: "Branch from `js-state` and open the PR against it, creating the branch from main if this is the first PR to need it: that branch collects the client-owned board until the switch, and main keeps the current stack."

<details><summary>Notes for implementers</summary>

Measurements behind the problem, on the 4-core dev workspace while idle (1 µs per empty R closure call there): one source, 1,000 dependents, one update. Shiny 1.14 spends 1,450 µs per `reactive()` node and 1,490 µs per `observe()`; Preact signals (`@preact/signals-core` 1.14.4) 0.17 and 0.12 µs. Per run, `Context$new()` alone takes 215 µs and `isolate(rv())` 947 µs, and `rLog$createContext()` runs reactlog bookkeeping, about a fifth of `Context$new()`, with reactlog off. A `reactive()` has no equality cutoff: downstream of one that recomputed to an identical value, an observer re-ran on both of two updates, where the Preact effect ran on neither.

Block packages surveyed on 2026-10-23 (blockr.dplyr, blockr.dm, blockr.ggplot, blockr.io, blockr.cdex and blockr.sandbox) ask the framework for expressions built from the data, such as dm's inferred keys and its value filter's branch on the input's class, which `interpolate(x, state, inputs)` keeps possible; controls whose choices and limits follow the data, now the element set's job; UI code shared between packages, such as dm reusing blockr.dplyr's filter UI, through the host; writes, downloads and uploads, through expressions, outputs and requests; and S3 methods on blocks, through constructors. Every package that ships JS loses the plumbing that keeps two copies of state in step: echo guards, replay queues, and ready and mount handshakes.

The workspace packages that import blockr.core, directly or through each other, on 2026-10-26: blockr.ai, blockr.assistant, blockr.cdex, blockr.code, blockr.dag, blockr, blockr.dm, blockr.dock, blockr.dplyr, blockr.ggplot, blockr.io, blockr.md, blockr.sandbox, blockr.session, blockr.uat and blockr.ui; blockr.core imports reactives and typedjson, blockr.dock dockViewR, and blockr.dag g6R.

</details>
