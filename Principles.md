# Principles
Revised on 2026-11-04.

These principles hold for every blockr package, whichever rewrite, spec or issue changes it.
A rewrite's root page holds the principles of that rewrite alone and links here for these, as it links the [glossary](Glossary) for its terms.

## Core gives a basic implementation and ways to extend it

Core implements what every board needs in a basic form, and offers ways to extend it.
It does not build one solution for every case, least of all where such a solution would be expensive or cannot work in general.
A case that needs more uses a way to extend core, such as a renderer of its own, a method of a coercion, a request or a block class of its own.
So core's default stays simple and sensible, and core keeps no special case for what a package can do itself.

Core's table output is an example ([blockr.core#422](https://github.com/BristolMyersSquibb/blockr.core/issues/422)).
It holds the names and classes of a table's columns, one page of its rows and its total row count, which may be unknown.
A cell that is not a single value shows its summary, so that the table stays flat, and every other value goes to the JSON writer as it is.
Core shows no column labels, no groups and no row names.
A renderer that shows them asks R for them through requests of its own ([blockr.core#425](https://github.com/BristolMyersSquibb/blockr.core/issues/425#issuecomment-6579784904)), and a deployment picks that renderer for table outputs.
A package whose results need another kind of table output adds a method of `as_table_output()` for their class.

## A board runs arbitrary R code, and the deployment sandboxes the R process

By design, blockr runs arbitrary R code.
A block may parse a string into code, as core's subset block parses its condition, so whoever uses a board can make the R process do anything the process may do, such as read a file, an environment variable or a blockr option.
The R process therefore runs in a sandbox, which is the deployment's job: bubblewrap under an account that may read only what the app needs, or, for full isolation, a microVM.
Core knows nothing about users, and neither core nor a package builds a protection against what code can do, since such a check costs work and complexity and keeps out no one who can write an expression.

Blockr options are an example ([blockr.core#453](https://github.com/BristolMyersSquibb/blockr.core/pull/453)).
The client reads any blockr option by name through a `blockr_options` request, and R answers for each without a list of those a client may read, since code in a block could read them all the same ([Blockr options](Rewrite-1.1.9#blockr-options)).
Decoding is no protection either: R decodes what a client sends into plain values, which keeps a value a value in a block expression, but a block that parses a string runs whatever it holds ([Decoding](Rewrite-1.1.9#decoding)).

## Authors own their blocks, and core treats a block's UI as a black box

An author writes a block's UI and its logic, and core wraps them, supplying what every block shares, such as code generation, evaluation and display.
Core assumes nothing that a notion of fields per block would afford, such as knowing a block's inputs, generating them or computing their attributes.

The first blockr (2023 to 2024) shows why.
It built each block from fields, typed values from which the framework generated the block's UI and server.
Logic between fields, such as one field's choices following another's selection, was hard to write, and a UI the field set lacked took a new field type.
Inputs derived from an upstream result could not be written, and a custom output meant overriding the generated server.
Its successor, blockr.core, hands each block to its author instead, who writes its UI and logic as a module that core wraps.

## The code a board exports is the code that ran

R evaluates each block's expression, and the script a board exports holds the same expression, so the script reproduces the board's results outside blockr.
It leaves out only what changes how a result shows, such as the ggplot theme a plot takes on to match dark mode, never what the result is.

Today's core misses this for a block whose `expr_type` is `"bquoted"`: it evaluates the block with its inputs' names and exports it with the upstream blocks' ids in their place ([R/block-server.R#L754-L768](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L754-L768), [R/utils-code.R#L58-L69](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-code.R#L58-L69)), so where a function takes labels from its arguments, as `cbind()` takes column names, the board and the script disagree.
[Block classes in R](Rewrite-1.1.5#evaluation) closes the gap by having R evaluate the expression the script holds.
A plot's theme is what the script leaves out: `as_plot_output()` applies it through thematic as it draws, so switching to dark mode redraws the plot and changes neither the block expression nor the script ([blockr.core#422](https://github.com/BristolMyersSquibb/blockr.core/issues/422)).

## Each piece of state has one writer, and whatever follows from it is derived

A piece of state is written in one place, and whatever can be computed from it is computed rather than stored beside it.
Two copies of one state need guards to keep them in step, and each failure that slips past the guards adds another.

The dock's layout is an example ([blockr.dock#257](https://github.com/BristolMyersSquibb/blockr.dock/issues/257)).
The server kept reactive values that each shadowed one facet of the layout, every one added to reject the dock's own echo after a failure slipped past the others, until the issue made `board_layouts` the only source and removed the guards against the echo.
The DAG made the same move for what it saves ([blockr.dag#119](https://github.com/BristolMyersSquibb/blockr.dag/issues/119)): it kept the whole g6 graph, icons, labels and colors included, which could contradict the board, and now saves only positions and derives the rest from the board.
[State in JS](Rewrite-1#proposal) applies the principle to the whole board, which the client alone writes.

## R only evaluates

R evaluates what the client sends, keeps the results and answers requests, while the client holds the board and draws every UI.
R holds no board state and draws nothing, so a client that starts a new R session with its board loses only recomputation.
Shiny's model runs the other way, keeping an app's state in the session's R process and rendering its UI from there, which is how blockr began.

Today's blockr shows the cost ([State in JS](Rewrite-1#problem)).
Board state and every block's UI logic run as reactives in the session's R process, on its one thread, so evaluation, the only part that needs R, waits behind them.
Core grew deferred and prioritized construction ([blockr.core#243](https://github.com/BristolMyersSquibb/blockr.core/issues/243), [blockr.core#275](https://github.com/BristolMyersSquibb/blockr.core/issues/275)) and a render gate ([blockr.core#257](https://github.com/BristolMyersSquibb/blockr.core/issues/257)) to work around that, and 37 of 100 defects in the dock's history are its drawing from R failing ([blockr#493](https://github.com/orgs/BristolMyersSquibb/discussions/493)).

## Every edit goes through one central coordinator, in one shared shape, whoever makes it

The user, the assistant and every extension change the board the same way, and a package that needs a new kind of edit adds it to the coordinator rather than building a path around it.
So every edit is checked the same way, and whatever follows the board, such as undo, saving or a session's drafts, sees every edit.

Today's `board_update` reactive is the coordinator ([R/board-server.R#L1386-L1395](https://github.com/BristolMyersSquibb/blockr.core/blob/14e4a2a109c5ecbf9040c89b66c2f1e714756fda/R/board-server.R#L1386-L1395)).
Every state change flows through it as `add`, `mod` and `rm`, core validates and augments each payload before applying it, and a board class adds slots of its own, as the dock adds `extensions`.
State in JS keeps that shape for every delta, whoever makes it ([Board updates](Rewrite-1.1.2)).

## An object is known by an id that never changes, and its name is only a label

Whatever others refer to has an id that never changes, with a name beside it that a user may edit, so nothing keys on the name.
A rename then changes one value, and whatever compares two states of the board can tell a renamed object from a new one.

Blocks have always worked this way, with `block_name()` as an editable label over the block's id, while views did not ([blockr.dock#166](https://github.com/BristolMyersSquibb/blockr.dock/issues/166)).
A view's name was its key.
So a rename re-keyed the saved layouts, the view state, the registry of live docks and the nav tabs in step, and a reconciler could not tell a rename from a removal and an addition.
Names needed rules of uniqueness and charset only because they were keys.
Giving views ids took a breaking change to the dock's model and its serialization.

## Opening a board leaves the page as starting it with that board would

Opening a board in place of another leaves every package, core included, as it would be had the page started with that board.
Whatever derives from a board lives for one opening: core makes it per opening and drops it when the next board opens, and a package that keeps something of a board does the same.
Only what is fixed for the page outlives an opening: the code that is loaded, what the packages that the app names offer, the blockr options and the lock.
State that outlives an opening by accident shows only once a second board opens, as a bug that no test of a single board finds.

Today's restore gets this from a reload: it stages the board and calls `session$reload()`, so that the page starts again with that board ([R/utils-serve.R#L277-L288](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L277-L288)).
State in JS starts core again in place instead, with no reload ([Drawing the board](Rewrite-1.1.8#opening-a-board)), so that core makes everything it keeps of a board per opening, and only what the page keeps across openings needs care.
The board options that a UI module requires are an example: core imports the module once per page, so had it added them only as the module first loaded, a board opened later would lack them ([blockr.core#468](https://github.com/BristolMyersSquibb/blockr.core/pull/468)).
