# The `blockr` meta-package: what it attaches and its integration tests
Status: review. Design for [Wrap-up](Rewrite-1.8).

One of the design pages of [Wrap-up](Rewrite-1.8): what the meta-package blockr attaches in the new stack, what becomes of its own function and vignettes, and the integration tests that it gains, which run the packages that it attaches together.
It shapes the Work items of its section of that part's Work list.
How fast the packages run together is [The speed benchmark](Rewrite-1.8.4)'s, and each package's own tests are its part's.

## What must hold

1. Calling `library(blockr)` attaches blockr.core, blockr.dock, blockr.graph and blockr.assistant, and no other package.
   Until the switch, it attaches them at their `js-state` versions.
2. Another package joins only once it has been ported and is judged relevant enough to include, and the integration tests then cover it too.
3. The meta-package keeps no function that the new stack replaces, and its migration notes say what takes the place of each ([The conversion and the migration notes](Rewrite-1.8.3#the-migration-notes)).
4. The integration tests run the packages that blockr attaches together, in R and in a browser, and check what no package's own tests can.
5. The integration tests run every night against the `js-state` of every package that they cover, and on each pull request of blockr.
   No other package's merge waits on them.
6. A night's run that fails opens an issue in blockr, or adds to the one already open, with the tests that failed and each package's commits since the last run that passed.
7. The vignettes of blockr describe the new stack, with the packages that it attaches, before the switch.

## Today

The meta-package blockr, at 0.1.1 on main, imports and attaches twelve packages: blockr.core, blockr.dock, blockr.dag, blockr.dplyr, blockr.ggplot, blockr.io, blockr.ui, blockr.viz, blockr.dm, blockr.script, blockr.session and blockr.assistant ([DESCRIPTION#L38-L53](https://github.com/BristolMyersSquibb/blockr/blob/f086d3ff96dfeb8c1da5b7a0605d221d254696e5/DESCRIPTION#L38-L53)).
As it attaches them, it lists them with their versions, as the tidyverse does ([R/attach.R](https://github.com/BristolMyersSquibb/blockr/blob/f086d3ff96dfeb8c1da5b7a0605d221d254696e5/R/attach.R)).
Its only export, `run_app()`, serves a dock board with the DAG's extension and the plugins of `blockr_app_plugins` ([R/run.R#L22-L33](https://github.com/BristolMyersSquibb/blockr/blob/f086d3ff96dfeb8c1da5b7a0605d221d254696e5/R/run.R#L22-L33)).
Its namespace also holds patterns that are meant to export the constructors of blocks, boards, links, stacks and extensions ([NAMESPACE](https://github.com/BristolMyersSquibb/blockr/blob/f086d3ff96dfeb8c1da5b7a0605d221d254696e5/NAMESPACE)).
They export nothing, since R matches such a pattern only against the package's own objects, and blockr defines none of these.

Its tests check the list of packages and what `run_app()` passes on.
One end-to-end test, "merge app", runs the package's example app through shinytest2 and compares each block's result with a snapshot ([tests/testthat/test-run.R#L38-L64](https://github.com/BristolMyersSquibb/blockr/blob/f086d3ff96dfeb8c1da5b7a0605d221d254696e5/tests/testthat/test-run.R#L38-L64)).
That app holds blocks of blockr.core, blockr.dplyr, blockr.io and blockr.ggplot in the dock, with the DAG ([inst/examples/board/app.R](https://github.com/BristolMyersSquibb/blockr/blob/f086d3ff96dfeb8c1da5b7a0605d221d254696e5/inst/examples/board/app.R)).
Its vignettes welcome a new user, build a workflow from the blocks of blockr.dplyr, blockr.ggplot and blockr.io, and say how to install blockr.

## Proposal

### What it attaches

In the new stack, blockr imports and attaches blockr.core, blockr.dock, blockr.graph and blockr.assistant.
Once these four are installed, `serve()` gives an app of all four by default: core, with the dock as its frontend, and the DAG and the assistant as plugins ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)).
The other packages of today's list leave it.
They are blockr.dag, in whose place blockr.graph draws the DAG, and blockr.dplyr, blockr.ggplot, blockr.io, blockr.ui, blockr.viz, blockr.dm, blockr.script and blockr.session.
A package joins once it has been ported and is judged relevant enough to include.
Until then, a script that uses it attaches it itself, as `library(blockr.dplyr)` does.
On `js-state`, blockr requires the `js-state` versions of the four, pins them in `Remotes:` and carries a 0.2 version ([State in JS](Rewrite-1#conventions)).

### Its function and its vignettes

The meta-package keeps no function of its own beyond attaching its packages and listing them.
Its `run_app()` goes, with no alias, as [State in JS](Rewrite-1#migration) has it for each function that the new stack replaces.
The function `serve()` runs every plugin of the available packages by default ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)).
So `serve(new_dock_board(...))` gives what `run_app()` gives today: the dock with the DAG, and the assistant.
The patterns in its namespace go too, since they export nothing.

Its vignettes are rewritten for the new stack.
The workflow that they build uses core's block classes in the dock, with the DAG and the assistant, until a package of block classes joins.
Its migration notes, a vignette, list each change of an app script that calls blockr ([The conversion and the migration notes](Rewrite-1.8.3#the-migration-notes)):

- A script calls `serve()` with the dock's board in place of `run_app()`.
- A script attaches each package that blockr no longer attaches and that it uses, once that package has been ported.

### The integration tests

The integration tests live in blockr's `tests/testthat`.
Each test serves a board of the packages that blockr attaches with `serve()`, in another R process, and shinytest2 drives its page in Chrome, as the merge app test does today.
The tests read the board, each block's status and the notifications through what core exports for end-to-end tests ([Drawing the board](Rewrite-1.1.8#testing)).

Each package tests itself with stand-ins for the others, such as core's `CoreApi` for tests ([Plugins](Rewrite-1.1.12#testing)).
The integration tests check what those tests cannot, since they need the real packages together:

1. **The app starts.**
   An app of the four packages, served with no plugins named, draws with the dock and runs the DAG and the assistant.
   Every package's modules load through the page's import map.
   The page shows no notification and logs no error in the browser's console.
2. **An edit through one plugin reaches the others.**
   A block that the DAG adds gets a panel in the dock's active view ([The dock's state](Rewrite-1.2.1#the-update)).
   A block that the dock's block picker adds gets a place in the DAG ([The DAG's state](Rewrite-1.3.1#the-classs-update-and-afterstep)).
   The user's undo takes back each of these steps in both.
3. **The assistant edits through every package.**
   A mock of a model's API scripts the model's replies, as the assistant's own end-to-end tests do.
   The assistant's edit tool runs one batch of commands of core, the dock and the DAG ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).
   The user's undo takes the whole batch back.
4. **A saved board opens again.**
   A board that the user saves through core's storage plugin opens again into the same board, with the dock's views, the DAG's positions and the assistant's conversations.

A package that joins the meta-package adds the flows that cross it, such as the blocks of a package of block classes in the dock's cards, in the DAG and in the assistant's edits.

### When the integration tests run

Each package's merge queue runs the revdep checks of blockr.ci's revdep workflow ([State in JS](Rewrite-1#conventions)).
They check each downstream package, with its own tests, against the queued commit.
So they catch a change that breaks a downstream package's own tests, before the change merges.

The integration tests catch what shows only when the packages run together.
They run apart from every merge queue: every night, and on each pull request of blockr.
So no package's merge waits on tests of the whole stack in a browser, which fail now and then without a real cause.
The cost is that a break shows the next morning, after the merge that caused it, and possibly among the merges of several packages that day.

So a run that fails opens an issue in blockr, or adds to the one already open.
The issue names the tests that failed and each package's commits since the last run that passed.
Without it, GitHub would tell only one person of the failure: whoever last edited the workflow's schedule.

## Open questions

None.

<details><summary>Notes for implementers</summary>

GitHub runs a scheduled workflow only from the default branch, so until the switch the workflow on blockr's main checks out `js-state` before it runs the tests.
A night's run installs each package from its `js-state` head, which the pins in blockr's `Remotes:` name, and pak records the commit of each in the installed package's `RemoteSha`.
The issue's list of commits runs from the `RemoteSha` of each package in the last run that passed, which the run keeps, to that of the run that failed.

The assistant's end-to-end tests on `js-state` mock OpenAI's Responses API through webfakes, in another R process, and give the mock the replies of each turn in order ([tests/testthat/helper-mock-api.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/adf63d1f7544ece6bc3ca878df3864875e592cbe/tests/testthat/helper-mock-api.R)).
The integration tests need the same mock, which blockr.assistant exports for the tests of other packages, rather than blockr keeping a copy.

Today's merge app test raises chromote's timeouts for loaded runners and keeps Chrome's scratch directories out of the directory that R CMD check inspects ([tests/testthat/setup-chrome-ci.R](https://github.com/BristolMyersSquibb/blockr/blob/f086d3ff96dfeb8c1da5b7a0605d221d254696e5/tests/testthat/setup-chrome-ci.R)), which the integration tests keep.

</details>
