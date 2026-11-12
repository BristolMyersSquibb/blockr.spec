# Backlog
Revised on 2026-11-11.

This page lists additions to blockr that are small or medium, go beyond what [State in JS](Rewrite-1) needs for parity, and are not ready for a spec.
Each item says what the addition would let us remove, what it would cost, and what would settle whether to build it, and an item leaves the list once it becomes a spec or an issue, or once it is dropped, with the reason.
The large projects after State in JS are on the [roadmap](Roadmap#after-state-in-js).

## Control links

A control link would be a second kind of edge on the board, beside links, saying that a selection on one block's output sets another block's state, such as a click on "SEX = F" in a chart setting a cohort filter's condition.
Today blockr.viz carries such a claim outside the DAG, from block code over a channel of its own, to a target that a block's setting names or that it finds by class ([R/ctrl-send.R#L1-L27](https://github.com/BristolMyersSquibb/blockr.viz/blob/332ce573ffafa86f5a41dc400b0f85e6800128f7/R/ctrl-send.R#L1-L27)).
In State in JS a renderer reports a selection through `emit()` and a plugin turns it into a command, keeping which block's selections go where in its state ([UI modules in JS](Rewrite-1.1.7#the-contract), [Plugins](Rewrite-1.1.12#running-a-plugin)).

What it would remove: a plugin's own record of where each block's selections go, and drill-down's need for a plugin at all, since core would route a selection to the state it sets.
Every such dependency would show on the board and in the DAG, as a link does.
A control link could point upstream, as a drill into a cohort filter does, since it carries an edit rather than data, so it closes no cycle, and it would add nothing to evaluation, so lazy evaluation never drags the sending block's upstream into its target, which is why blockr.viz kept such claims off links.

What it would cost: a new object in the board ([Board objects](Rewrite-1.1.1)), with commands to add, change and remove it and checks in the store ([Board updates](Rewrite-1.1.2)), a place in the JSON board ([Serialization](Rewrite-1.1.4)), a second kind of edge for the DAG to draw and edit and for frontends to offer ([Client-drawn dock](Rewrite-1.2), [Client-drawn DAG extension](Rewrite-1.3)), and a rule for how a target turns a selection into its state, which for blockr.dm's drill filter needs the dm to say which table a column belongs to.

What would settle it: whether, once drill-down runs as a plugin in State in JS, other packages route selections between blocks too, or blockr.viz's drill stays the only one.

## Block classes registered on demand

An app's block registry fills once, as `serve()` builds the app, from the block classes that it takes in `blocks`, every class of the available packages by default, and the reply to `hello` sends each of them in full: its metadata, its schema, its default state, its arg specs and its requests ([Block classes in R](Rewrite-1.1.5#registration), [Wire protocol](Rewrite-1.1.9#handshake)).
The first draw needs that only for the classes of the blocks on the opening board, while every other class needs only its id and the metadata that the picker shows, until a user adds a block of it, a board that holds one opens, or the assistant reads its arg specs.
So the reply could send each offered class's id and picker metadata, and the rest of its entry the first time something needs it.
The same would let an app take in a package installed while it runs.
R loads a package that it has not loaded yet as it loads any other, so discovery could run again and add the package's classes, modules and version to the app for the sessions that start afterwards, where [blockr.core#562](https://github.com/BristolMyersSquibb/blockr.core/pull/562) builds each app's block registry once, as `serve()` runs, so that a class registered later reaches no app built before.
Upgrading a package that the app has loaded still takes a restart, since R cannot swap a namespace in place, and a reconnecting page reloads where R names a package at another version than before ([Wire protocol](Rewrite-1.1.9#handshake)).
Raised in the review of [blockr.core#454](https://github.com/BristolMyersSquibb/blockr.core/pull/454), when loading a package registered all of its classes, which `blocks` and the object `._BLOCKR_MODULES_` that each package exports have since replaced ([Block classes in R](Rewrite-1.1.5#registration)).

What it would remove: the full entries of the block classes that no block on the opening board uses, from every reply to `hello`, and the restart that a package installed while the app runs needs.

What it would cost: a request for the rest of a class's entry, which the client makes before it draws, adds or migrates a block of the class or gives the assistant the class's arg specs, an `open` that names a board's registry ids ([Wire protocol](Rewrite-1.1.9#opening-a-board)), and, for a package installed while the app runs, a second discovery, an app's block registry that grows after `serve()` built it, and a reply to `hello` whose packages grow with it.
The board options of a class that an app takes in while it runs need nothing more, since core adds a component's board options as it first needs the component ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)).

What would settle it: the size of the block registry in the reply to `hello` with every available package offered, measured beside the time to the first draw, and whether apps want to take in packages installed while they run.

## Entries of a block's menu in core

Core would hold the entries of a block's menu, such as removing the block or appending one to it, and every frontend and the DAG would draw them in their menus of a block, so that a plugin adds an entry once for all of them.
Today core, the dock and the DAG each keep a list of their own.
Core's `edit_block` plugin offers a field for the block's name and buttons to remove the block and to add one before or after it ([R/plugin-block.R#L252-L294](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-block.R#L252-L294)).
The dock gives that plugin its own UI, its card, whose "…" menu has items that the dock fixes ([R/plugin-block.R#L191-L247](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L191-L247)).
The DAG's context menu offers on a block's node to create a link, remove the block, append one and edit its inputs, through its own method of `context_menu_items()`, a generic that any extension may extend and no other does ([R/ext.R#L118-L419](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L118-L419)).
In State in JS core's basic frontend, the dock and the DAG still draw a menu of a block each ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend), [Client-drawn DAG extension](Rewrite-1.3)), and the dock's cards offer plugins no entry ([Places the dock offers plugins](Rewrite-1.2.4#places-besides-the-panel)).

What it would remove: the three lists of a block's entries that core, the dock and the DAG keep today, which share entries such as removing a block.

What it would cost: a list in core of the commands that a block's menu offers, built on the command registry, whose `label` is for menus already ([Board updates](Rewrite-1.1.2#commands)), a way to offer what is no command, such as renaming a block in place or copying its id, and a menu in every frontend and in the DAG that draws the list and gathers the args of the commands it runs, as the dock's "+" menu gathers those of appending a block.

What would settle it: a package that needs an entry in a block's menu, under every frontend.
