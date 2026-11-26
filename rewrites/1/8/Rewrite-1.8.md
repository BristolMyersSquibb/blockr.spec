# Wrap-up
Status: review. Part of [State in JS](Rewrite-1).

This part covers the work that checks the new stack and lets people move to it: the speed benchmark and the assistant's benchmark, the conversion of today's files and the migration notes, the documentation of the new stack, and the meta-package blockr with its integration tests.
Five design pages hold the detail, and each becomes a spec of its own once it settles ([A spec per design page](#a-spec-per-design-page)).
This part builds on the parts it measures, converts, documents and attaches, and comes last among them.

## Problem

Nothing measures the new stack yet, though the case for it is speed and its assistant is rebuilt.
On today's dock, a board of two blocks takes about 5.8 s and 13 busy periods to settle after it mounts ([blockr.dock#397](https://github.com/BristolMyersSquibb/blockr.dock/issues/397)).
On one R process, a classic Shiny app answered none of one user's updates within 120 s once four other sessions streamed, where the same updates sent as data took a few milliseconds ([blockr#493](https://github.com/BristolMyersSquibb/blockr/discussions/493#discussioncomment-18775537)).
The bar is a new stack that is faster than today's, rather than no slower, which takes measurements on boards of the size users run, such as the clinical data explorer's board.
Nor does anything show where the new stack spends its time, or tell a pull request that it made the new stack slower.
No file that today's stack saved opens in the new one, and 89 R scripts and 8 documents in 15 of the workspace's repos call `serve()`, whose packages change at the switch.
The packages also document their R APIs through roxygen2 and pkgdown, but their TypeScript APIs and client internals have no shared documentation form.
A reader can find neither one site that joins the R and TypeScript references nor guides that follow the client's work across its modules.
Each package tests itself with stand-ins for the others, and the revdep checks in a merge queue run each downstream package's own tests.
So no test runs the dock, the DAG and the assistant on one page.
The meta-package blockr attaches twelve packages today, and the switch does not wait for all of them to be ported.

## What must hold

1. Benchmarks compare the new stack with today's on named boards and report the speed of the client and R and how well the assistant does what users ask, as [The speed benchmark](Rewrite-1.8.4) and [The assistant's benchmark](Rewrite-1.8.1) set out.
2. Today's files and app scripts cross as [The conversion and the migration notes](Rewrite-1.8.3) requires, with no package but blockr.convert holding code that reads today's files.
3. Every package with client code documents its R and TypeScript APIs and its client internals on its pkgdown site, as [Documentation of the new stack](Rewrite-1.8.2) requires.
4. The migration notes and package documentation are complete before the switch, as [State in JS](Rewrite-1#migration) requires of migration notes.
5. The meta-package blockr attaches only packages of the new stack, and integration tests run them together every night, as [The `blockr` meta-package](Rewrite-1.8.5) requires.

## Proposal

### A spec per design page

Each design page of this part settles on its own, and then becomes a spec of its own, without waiting for the other design pages.
Other parts become one spec once all their design pages have settled.
This part's design pages share no decision, so none has to wait for another.
Each design page shapes only the Work items of its own section below, so a design page that settles later changes no issue that an earlier spec opened.
A spec made from a design page takes the design page's name as its title, links the design page and this part, and holds the design page's section of the Work list, moved.
The part is implementing once its first spec is posted, and its status line names each spec as it is posted.
A design page closes once its spec is resolved, and the part closes once every design page has closed.

### Benchmarks

The benchmarks live in blockr.bench, a repo of its own, which installs the packages that a run measures at the refs that it names, so that no package of the stack depends on the benchmarks.
The spec of whichever benchmark settles first creates blockr.bench, with what both benchmarks need: installing the packages at the refs that a run names, serving a board with `serve()` and driving its page in a headless browser.
The speed benchmark compares today's stack and the new stack on the same machine and boards, shows where the new stack spends its time, and posts on each pull request a comparison of its head with its base, as [The speed benchmark](Rewrite-1.8.4) has it.
The assistant's benchmark follows [The assistant's benchmark](Rewrite-1.8.1).

### The conversion and the migration notes

The package blockr.convert turns each file of today's stack into a JSON board once.
Each package writes migration notes for the app scripts that call it, and conversion tests check those notes against the scripts of the packages' examples.
[The conversion and the migration notes](Rewrite-1.8.3) holds the design.

### Documentation of the new stack

Each package with client code keeps one pkgdown site, with roxygen2's R reference, TypeDoc's TypeScript reference and hand-written guides to its client internals under one theme and navigation.
Blockr.core proves the TypeScript-to-pkgdown build before the reusable workflows gain it and the other packages adopt it.
[Documentation of the new stack](Rewrite-1.8.2) holds the design.

### The meta-package blockr

The meta-package blockr attaches blockr.core, blockr.dock, blockr.graph and blockr.assistant at first, and another package once it has been ported and is judged relevant enough to include.
It gains integration tests, which run those packages together every night, apart from every merge queue.
[The `blockr` meta-package](Rewrite-1.8.5) holds the design.

## Open questions

None.

## Work

Each section below moves into the spec of its design page once that page settles, and is then one line that links the spec.

### The repo blockr.bench

This item moves into the spec of whichever benchmark settles first.

- Create blockr.bench, which installs the packages that a run measures at the refs that the run names, serves a board with `serve()` and drives its page in a headless browser, as both benchmarks need, in blockr.bench

### [The assistant's benchmark](Rewrite-1.8.1)

- Build the assistant's benchmark in blockr.bench, with its harness and the clinical data explorer's five questions, as [The assistant's benchmark](Rewrite-1.8.1) has it, in blockr.bench
- Compare the edit tool with a tool per command and with tools for each block class, and keep the version that passes, as [The assistant's tools](Rewrite-1.4.2#the-edit-tool) and [The assistant's benchmark](Rewrite-1.8.1#the-decisions-it-compares) have it, in blockr.assistant
- Start a run of the assistant's benchmark from each pull request that changes what the model sees or may do, after `js-state` has merged into main, and show its comparison on that pull request, as [The assistant's benchmark](Rewrite-1.8.1#where-it-lives) has it, in blockr.assistant
- Start a run of the assistant's benchmark from each pull request that changes the `layout` skill, after `js-state` has merged into main, and show its comparison on that pull request, as [The assistant's benchmark](Rewrite-1.8.1#where-it-lives) has it, in blockr.dock
- Take the baseline of today's assistant on those questions by hand, as [The assistant's benchmark](Rewrite-1.8.1#todays-assistant-as-the-baseline) has it, in blockr.sandbox

### [Documentation of the new stack](Rewrite-1.8.2)

- Prove a pkgdown build that renders TypeDoc's reference for `@blockr/core` beside roxygen2's R reference under one theme and navigation, chooses how TypeDoc's Markdown becomes pkgdown input, and checks its internal links, in blockr.core ([One site per package](Rewrite-1.8.2#one-site-per-package))
- Extend the reusable CI workflow's `pkgdown-dev` job and the reusable pkgdown workflow to run a package's documentation build before their pkgdown builds, check the internal links of each built site, and leave a package without TypeScript entry points unchanged, in blockr.ci
- Generate reference pages for core's mounted block, board option, plugin and output modules and for `@blockr/core/react`, `@blockr/core/components`, `@blockr/core/binding`, `@blockr/core/controls`, `@blockr/core/stubs` and `@blockr/core/build` from their source entry points, with their exported `/** ... */` comments and the schema annotations preserved, in blockr.core
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

### [The conversion and the migration notes](Rewrite-1.8.3)

- Create blockr.convert, with `blockr_deser()` and the methods of blockr.core's main, and `convert_file()`, which reads a file of today's stack with typedjson in the mode that refuses code and writes its JSON board with `blockr_ser()`, with a README on converting a file, in blockr.convert
- Convert a dock board, with the methods of blockr.dock's main for the dock board, its stacks and the Edit board extension, which write the dock plugin's state at version 1 ([Saved boards and app scripts across the switch](Rewrite-1.2.2#the-dock-board)), in blockr.convert
- Refuse a file without a `format`, in the client and in `serve()`, with an error that names blockr.convert's `convert_file()`, in blockr.core
- Carry over the methods of `blockr_deser()` of blockr.dplyr's main, and write those that make the plugins of the DAG, the assistant and blockr.md from today's extensions, in blockr.convert
- Write the test files of every package that wrote today's files and of the clinical data explorer's board, from main at the switch, and the check that each example's script, changed by an AI from the migration notes alone, opens into the same board as the conversion of its file, in blockr.convert

### [The speed benchmark](Rewrite-1.8.4)

- Build the speed benchmark for the new stack, with its measurements on the generated boards, the times and counts that each run records and its report, as [The speed benchmark](Rewrite-1.8.4) has it, in blockr.bench
- Take the same measurements on today's stack, and report for each measurement and board whether the new stack meets the bar, as [The speed benchmark](Rewrite-1.8.4#comparing-with-todays-stack) has it, in blockr.bench
- Add the profiling run, which collects core's spans, the page's CPU profile and R's profile, and sums them by span and by function, as [The speed benchmark](Rewrite-1.8.4#where-the-time-goes) has it, in blockr.bench
- Offer a reusable workflow that compares a pull request's head with its base and posts the comparison as one comment on the pull request, as [The speed benchmark](Rewrite-1.8.4#what-a-pull-request-gets) has it, in blockr.bench
- Start the speed comparison from each pull request to `js-state`, in blockr.core
- Start the speed comparison from each pull request to `js-state`, in blockr.ui
- Start the speed comparison from each pull request to `js-state`, in blockr.dock
- Start the speed comparison from each pull request to `js-state`, in blockr.graph
- Start the speed comparison from each pull request to `js-state`, in blockr.assistant
- Add the clinical data explorer's board to the speed benchmark once its packages have been ported, in blockr.bench

### [The `blockr` meta-package](Rewrite-1.8.5)

- Create `js-state` in blockr, which attaches blockr.core, blockr.dock, blockr.graph and blockr.assistant at their `js-state` versions, pinned in `Remotes:`, at version 0.2.0, without `run_app()` and the patterns in its namespace, as [The `blockr` meta-package](Rewrite-1.8.5#what-it-attaches) has it, in blockr
- Export the mock of a model's API that the assistant's end-to-end tests use, for the tests of other packages, in blockr.assistant
- Write the integration tests of the four packages, as [The `blockr` meta-package](Rewrite-1.8.5#the-integration-tests) has them, in blockr
- Run the integration tests every night against the `js-state` of every package, and open or update an issue in blockr when a run fails, as [The `blockr` meta-package](Rewrite-1.8.5#when-the-integration-tests-run) has it, in blockr
- Rewrite the vignettes of blockr for the new stack, and write its migration notes, as [The `blockr` meta-package](Rewrite-1.8.5#its-function-and-its-vignettes) has them, in blockr

## Design pages

- [The assistant's benchmark: questions, answer keys and runs](Rewrite-1.8.1): how the decisions that shape what the assistant's model sees and does are judged, from its system prompt to its tools, what they return and how failures reach it, through questions with answer keys that a harness runs, with today's assistant as the baseline
- [Documentation of the new stack](Rewrite-1.8.2): one pkgdown site per package for the R and TypeScript references, with long-form guides to the client internals and a build that every package shares
- [The conversion and the migration notes](Rewrite-1.8.3): blockr.convert's package and methods, who converts, which objects do not cross, migration notes and the tests that check them against today's examples
- [The speed benchmark: boards, measurements and runs](Rewrite-1.8.4): how fast the new stack runs against today's stack on the same boards, where it spends its time, and the comparison that each pull request gets
- [The `blockr` meta-package: what it attaches and its integration tests](Rewrite-1.8.5): the packages that `library(blockr)` attaches in the new stack, and the integration tests that run them together every night
