# Backlog
Revised on 2026-11-02.

This page lists additions to blockr that are small or medium, go beyond what [State in JS](Rewrite-1) needs for parity, and are not ready for a spec.
Each item says what the addition would let us remove, what it would cost, and what would settle whether to build it, and an item leaves the list once it becomes a spec or an issue, or once it is dropped, with the reason.
The large projects after State in JS are on the [roadmap](Roadmap#after-state-in-js).

## Control links

A control link would be a second kind of edge on the board, beside links, saying that a selection on one block's output sets another block's state, such as a click on "SEX = F" in a chart setting a cohort filter's condition.
Today blockr.viz carries such a claim outside the DAG, from block code over a channel of its own, to a target that a block's setting names or that it finds by class ([R/ctrl-send.R#L1-L27](https://github.com/BristolMyersSquibb/blockr.viz/blob/332ce573ffafa86f5a41dc400b0f85e6800128f7/R/ctrl-send.R#L1-L27)).
In State in JS a renderer reports a selection through `emit()` and a plugin turns it into a command, keeping which block's selections go where in its state ([UI modules in JS](Rewrite-1.1.7#the-contract), [Client-drawn dock](Rewrite-1.2#open-questions)).

What it would remove: a plugin's own record of where each block's selections go, and drill-down's need for a plugin at all, since core would route a selection to the state it sets.
Every such dependency would show on the board and in the DAG, as a link does.
A control link could point upstream, as a drill into a cohort filter does, since it carries an edit rather than data, so it closes no cycle, and it would add nothing to evaluation, so lazy evaluation never drags the sending block's upstream into its target, which is why blockr.viz kept such claims off links.

What it would cost: a new object in the board ([Board objects](Rewrite-1.1.1)), with commands to add, change and remove it and checks in the store ([Board updates](Rewrite-1.1.2)), a place in the JSON board ([Serialization](Rewrite-1.1.4)), a second kind of edge for the DAG to draw and edit and for frontends to offer ([Client-drawn dock](Rewrite-1.2), [Client-drawn DAG extension](Rewrite-1.3)), and a rule for how a target turns a selection into its state, which for blockr.dm's drill filter needs the dm to say which table a column belongs to.

What would settle it: whether, once drill-down runs as a plugin in State in JS, other packages route selections between blocks too, or blockr.viz's drill stays the only one.

## Block classes registered on demand

A package registers every block class it ships as R loads it, in its `.onLoad()`, from the `blocks.yml` that `register_package_blocks()` reads, so `library()` makes all of a package's classes available to an app, and a board opened from a file that names the package brings all of them too, where it uses a few.
The block registry could fill per class instead, from what an app offers and what a board names: an app script registers the classes it offers, all of a package's through one call where it wants them, and R resolves a class that a board names by its registry id when the board opens, loading its package as it looks the class up and registering that class alone, from the same `blocks.yml`, which stays the data while only what reads it moves out of `.onLoad()`.
On top of that, a symbol that every block package exports would let a frontend list the installed block packages and offer to load any of them, and to register any of their block classes, while the app runs.
Raised in the review of [blockr.core#454](https://github.com/BristolMyersSquibb/blockr.core/pull/454).

What it would remove: the block classes that an app does not offer but gets because their package loaded, and the registration code in every block package's `.onLoad()`.

What it would cost: registration in R by class from a board's registry ids ([Block classes in R](Rewrite-1.1.5#registration)), an `open` that names a board's registry ids beside its packages ([Wire protocol](Rewrite-1.1.9#opening-a-board)), and the same move for what else a package declares as it loads, its modules, its startup module and its renderers, which a board needs whole whatever block classes it uses ([Drawing the board](Rewrite-1.1.8#what-a-package-declares-in-r)).
The board options of a class registered while the app runs need nothing more, since core adds a component's board options as it first needs the component ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)).

What would settle it: whether apps want to offer only some of a package's block classes, or to let a user load block packages while the app runs.
