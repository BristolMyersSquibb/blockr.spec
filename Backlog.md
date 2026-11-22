# Backlog
Revised on 2026-11-22.

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

What it would cost: a new object in the board ([Board objects](Rewrite-1.1.1)), with commands to add, change and remove it and checks in the store ([Board updates](Rewrite-1.1.2)), a place in the JSON board ([Serialization](Rewrite-1.1.4)), a second kind of edge for the DAG to draw and edit and for frontends to offer ([Client-drawn dock](Rewrite-1.2), [Client-drawn DAG](Rewrite-1.3)), and a rule for how a target turns a selection into its state, which for blockr.dm's drill filter needs the dm to say which table a column belongs to.

What would settle it: whether, once drill-down runs as a plugin in State in JS, other packages route selections between blocks too, or blockr.viz's drill stays the only one.

## Block classes registered on demand

An app's block registry fills once, as `serve()` builds the app, from the block classes that it takes in `blocks`, every class of the available packages by default, and the reply to `hello` sends each of them in full: its metadata, its schema, its default state, its arg specs and its requests ([Block classes in R](Rewrite-1.1.5#registration), [Wire protocol](Rewrite-1.1.9#handshake)).
The first draw needs that only for the classes of the blocks on the opening board, while every other class needs only its id and the metadata that the picker shows, until a user adds a block of it, a board that holds one opens, or the assistant reads its arg specs.
So the reply could send each offered class's id and picker metadata, and the rest of its entry the first time something needs it.
The same would let an app take in a package installed while it runs.
R loads a package that it has not loaded yet as it loads any other, so discovery could run again and add the package's classes, modules, board options and version to the app for the sessions that start afterwards, where [blockr.core#562](https://github.com/BristolMyersSquibb/blockr.core/pull/562) builds each app's block registry once, as `serve()` runs, and [blockr.core#678](https://github.com/BristolMyersSquibb/blockr.core/pull/678) reads the app's modules and board options there too, so that what a package installed later lists reaches no app built before.
Upgrading a package that the app has loaded still takes a restart, since R cannot swap a namespace in place, and a reconnecting page reloads where R names a package at another version than before ([Wire protocol](Rewrite-1.1.9#handshake)).
Raised in the review of [blockr.core#454](https://github.com/BristolMyersSquibb/blockr.core/pull/454), when loading a package registered all of its classes, which `blocks` and the object `._BLOCKR_MODULES_` that each package exports have since replaced ([Block classes in R](Rewrite-1.1.5#registration)).

What it would remove: the full entries of the block classes that no block on the opening board uses, from every reply to `hello`, and the restart that a package installed while the app runs needs.

What it would cost: a request for the rest of a class's entry, which the client makes before it draws, adds or migrates a block of the class or gives the assistant the class's arg specs, an `open` that names a board's registry ids ([Wire protocol](Rewrite-1.1.9#opening-a-board)), and, for a package installed while the app runs, a second discovery, an app's block registry that grows after `serve()` built it, and a reply to `hello` whose packages grow with it.
The board options of a class that an app takes in while it runs need nothing more, since core adds a component's board options as it first needs the component ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)).

What would settle it: the size of the block registry in the reply to `hello` with every available package offered, measured beside the time to the first draw, and whether apps want to take in packages installed while they run.

## Inputs of board actions that each host lays out

A board action's quick action is a set of rows, which core runs and draws, and its advanced action is a module, which draws a form of its own ([Board actions](Rewrite-1.1.16#a-board-action)).
A package that opens a menu chooses where such a form shows, as the Edit board plugin shows Edit link's form in the link's row, but not how the form lays out its fields ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).
A board action could instead describe its inputs as data: each input's kind, label, choices and check, with choices that depend on another input, as the inputs that a new link may feed depend on the block that it goes into.
Each host would then lay the inputs out itself:

- Core's menu would show them one at a time at the trigger.
- Core's dialog and the dock's sidebar would show them all at once, as a form.
- The Edit board plugin would show them as editable cells of its tables, one column for each input, in every row at once.

Blender draws the properties of an operator in this way, in a popup, a dialog or the Adjust Last Operation panel ([Operator](https://docs.blender.org/api/current/bpy.types.Operator.html)).
Figma draws a plugin's parameters in Quick Actions ([plugin parameters](https://developers.figma.com/docs/plugins/plugin-parameters/)).
Django's admin draws a model's fields as a form, and as editable cells of its list through `list_editable` ([ModelAdmin.list_editable](https://docs.djangoproject.com/en/stable/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_editable)).
Each of them keeps a custom UI for what its inputs cannot describe, as Blender's `draw()` and Figma's `showUI` do, and the block picker and the drag of Edit inputs would need one too.
Raised in the review of [Board actions](Rewrite-1.1.16) on 2026-11-20.

What it would remove: the forms that each board action writes, which core would draw from the inputs instead, and the second description of one edit that a board action with both a quick action and an advanced action gives today.

What it would cost: a description of inputs, with their kinds, choices that depend on other inputs or wait for R, such as a block's columns, and checks, which would replace both quick actions and advanced modules, with a custom UI beside them; a layout of each kind in every host that draws inputs; and moving the board actions and forms that core has built by then onto it.
A role names part of that description already: the commands of a board action and the args of theirs that the target fixes, so that the JSON Schemas of the other args give the kinds and checks of the role's inputs, while their labels and their choices, those that depend on other inputs and those that wait for R, would be new ([Board actions](Rewrite-1.1.16#roles)).

What would settle it: whether users edit many blocks, links or stacks at once in the Edit board plugin's tables, where cells would save opening a form for each row, and how many of the board actions of packages beyond core fit inputs that core can draw.
