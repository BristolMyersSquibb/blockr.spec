# Wrap-up
Status: review. Part of [State in JS](Rewrite-1).

This part covers the work that checks the new stack and lets people move to it: benchmarks, conversion of today's files, migration notes, and the documentation of the new stack.
The assistant's benchmark, the conversion and migration notes, and documentation have design pages of their own.
This part builds on the parts it measures, converts and documents, and comes last among them.

## Problem

Nothing measures the new stack yet, though the case for it is speed and its assistant is rebuilt.
On today's dock, a board of two blocks takes about 5.8 s and 13 busy periods to settle after it mounts ([blockr.dock#397](https://github.com/BristolMyersSquibb/blockr.dock/issues/397)).
On one R process, a classic Shiny app answered none of one user's updates within 120 s once four other sessions streamed, where the same updates sent as data took a few milliseconds ([blockr#493](https://github.com/BristolMyersSquibb/blockr/discussions/493#discussioncomment-18775537)).
The bar is a new stack that is faster than today's, rather than no slower, which takes measurements on boards of the size users run, such as the clinical data explorer's board.
No file that today's stack saved opens in the new one, and 89 R scripts and 8 documents in 15 of the workspace's repos call `serve()`, whose packages change at the switch.
The packages also document their R APIs through roxygen2 and pkgdown, but their TypeScript APIs and client internals have no shared documentation form.
A reader can find neither one site that joins the R and TypeScript references nor guides that follow the client's work across its modules.

## What must hold

1. Benchmarks compare the new stack with today's on named boards and report the speed of the client and R and how well the assistant does what users ask, as [The assistant's benchmark](Rewrite-1.8.1) sets out for the assistant.
2. Today's files and app scripts cross as [The conversion and the migration notes](Rewrite-1.8.3) requires, with no package but blockr.convert holding code that reads today's files.
3. Every package with client code documents its R and TypeScript APIs and its client internals on its pkgdown site, as [Documentation of the new stack](Rewrite-1.8.2) requires.
4. The migration notes and package documentation are complete before the switch, as [State in JS](Rewrite-1#migration) requires of migration notes.

## Proposal

### Benchmarks

The benchmarks live in blockr.bench, a repo of its own, which installs the packages that a run measures at the refs that it names, so that no package of the stack depends on the benchmarks.
The speed benchmarks compare today's stack and the new stack on the same machine and data, on boards whose packages have ported.
The first speed-benchmark issue takes today's measurements and chooses the first measurements, boards and machine from those of first paint, a view switch, an edit's round trip and several sessions sharing one R process.
Its report records those choices and the measured bar that later runs check.
The assistant's benchmark follows [The assistant's benchmark](Rewrite-1.8.1).

### The conversion and the migration notes

The package blockr.convert turns each file of today's stack into a JSON board once.
Each package writes migration notes for the app scripts that call it, and conversion tests check those notes against the scripts of the packages' examples.
[The conversion and the migration notes](Rewrite-1.8.3) holds the design.

### Documentation of the new stack

Each package with client code keeps one pkgdown site, with roxygen2's R reference, TypeDoc's TypeScript reference and hand-written guides to its client internals under one theme and navigation.
Blockr.core proves the TypeScript-to-pkgdown build before the reusable workflow gains it and the other packages adopt it.
[Documentation of the new stack](Rewrite-1.8.2) holds the design.

## Open questions

None.

## Work

- Create blockr.convert, with `blockr_deser()` and the methods of blockr.core's main, and `convert_file()`, which reads a file of today's stack with typedjson in the mode that refuses code and writes its JSON board with `blockr_ser()`, with a README on converting a file, in blockr.convert
- Convert a dock board, with the methods of blockr.dock's main for the dock board, its stacks and the Edit board extension, which write the dock plugin's state at version 1 ([Saved boards and app scripts across the switch](Rewrite-1.2.2#the-dock-board)), in blockr.convert
- Refuse a file without a `format`, in the client and in `serve()`, with an error that names blockr.convert's `convert_file()`, in blockr.core
- Carry over the methods of `blockr_deser()` of blockr.dplyr's main, and write those that make the plugins of the DAG, the assistant and blockr.md from today's extensions, in blockr.convert
- Write the test files of every package that wrote today's files and of the clinical data explorer's board, from main at the switch, and the check that each example's script, changed by an AI from the migration notes alone, opens into the same board as the conversion of its file, in blockr.convert
- Prove a pkgdown build that renders TypeDoc's reference for `@blockr/core` beside roxygen2's R reference under one theme and navigation, chooses how TypeDoc's Markdown becomes pkgdown input, and checks its internal links, in blockr.core ([One site per package](Rewrite-1.8.2#one-site-per-package))
- Extend the reusable pkgdown workflow to run a package's documentation build before `pkgdown::build_site_github_pages()`, check the internal links of the built site, and leave a package without TypeScript entry points unchanged, in blockr.ci
- Generate reference pages for `@blockr/core/react`, `@blockr/core/components`, `@blockr/core/binding`, `@blockr/core/controls`, `@blockr/core/stubs` and `@blockr/core/build` from their source entry points, with their exported `/** ... */` comments and the schema annotations preserved, in blockr.core
- Write the overview of core's client and the starting-the-page guide, with the source map, the boundary between source and generated files, and the sequence from `startPage()` through `hello`, registration, board opening, frontend rendering and scheduler startup, in blockr.core
- Write the guides to `CoreApi`, the hosts and mounting modules, covering block, board option, plugin and output mounts and their lifetimes, in blockr.core
- Write the guides to the store, deltas, steps, the command registry and board actions, following `BlockHost.submit()` and a board action through one step, in blockr.core
- Write the guides to the scheduler, wire protocol and Shiny transport, following demand through evaluation and output rendering, in blockr.core
- Write the guides to core's frontend and plugins, its block and option modules, and storage with logging and tracing, in blockr.core
- Write the guides to core's React SDK, binding and controls, and its build and tests, in blockr.core
- Add the TypeScript reference and a guide to the client internals of blockr.ui on its pkgdown site, in blockr.ui
- Add the TypeScript reference and a guide to the client internals of blockr.dock on its pkgdown site, in blockr.dock
- Add the TypeScript reference and a guide to the client internals of blockr.graph on its pkgdown site, in blockr.graph
- Add the TypeScript reference and a guide to the client internals of blockr.assistant on its pkgdown site, in blockr.assistant
- Add the TypeScript reference and a guide to the client internals of blockr.code on its pkgdown site, in blockr.code
- Add the TypeScript reference and a guide to the client internals of blockr.session on its pkgdown site, in blockr.session
- Add the TypeScript reference and a guide to the client internals of blockr.dplyr on its pkgdown site once its block classes have moved to the new stack, in blockr.dplyr
- Add the TypeScript reference and a guide to the client internals of blockr.ggplot on its pkgdown site once its block classes have moved to the new stack, in blockr.ggplot
- Add the TypeScript reference and a guide to the client internals of blockr.io on its pkgdown site once its block classes have moved to the new stack, in blockr.io
- Add the TypeScript reference and a guide to the client internals of blockr.dm on its pkgdown site once its block classes have moved to the new stack, in blockr.dm
- Add the TypeScript reference and a guide to the client internals of blockr.ai on its pkgdown site once its block classes have moved to the new stack, in blockr.ai
- Create blockr.bench, and build the assistant's benchmark in it, with its harness and the clinical data explorer's five questions, as [The assistant's benchmark](Rewrite-1.8.1) has it, in blockr.bench
- Compare the edit tool with a tool per command and with tools for each block class, and keep the version that passes, as [The assistant's tools](Rewrite-1.4.2#the-edit-tool) and [The assistant's benchmark](Rewrite-1.8.1#the-decisions-it-compares) have it, in blockr.assistant
- Start a run of the assistant's benchmark from each pull request that changes what the model sees or may do, after `js-state` has merged into main, and show its comparison on that pull request, as [The assistant's benchmark](Rewrite-1.8.1#where-it-lives) has it, in blockr.assistant
- Start a run of the assistant's benchmark from each pull request that changes the `layout` skill, after `js-state` has merged into main, and show its comparison on that pull request, as [The assistant's benchmark](Rewrite-1.8.1#where-it-lives) has it, in blockr.dock
- Take the baseline of today's assistant on those questions by hand, as [The assistant's benchmark](Rewrite-1.8.1#todays-assistant-as-the-baseline) has it, in blockr.sandbox
- Define and build the speed benchmark in blockr.bench, taking the baseline of today's stack, choosing and recording its first measurements, boards and machine, and reporting them against the new stack

## Design pages

- [The assistant's benchmark: questions, answer keys and runs](Rewrite-1.8.1): how the decisions that shape what the assistant's model sees and does are judged, from its system prompt to its tools, what they return and how failures reach it, through questions with answer keys that a harness runs, with today's assistant as the baseline
- [Documentation of the new stack](Rewrite-1.8.2): one pkgdown site per package for the R and TypeScript references, with long-form guides to the client internals and a build that every package shares
- [The conversion and the migration notes](Rewrite-1.8.3): blockr.convert's package and methods, who converts, which objects do not cross, migration notes and the tests that check them against today's examples
