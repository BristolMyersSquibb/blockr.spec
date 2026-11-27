# Backlog
Revised on 2026-11-26.

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

## Block UIs composed in R

A block class's UI is a module in JS, which its author writes in TSX or in plain JS ([UI modules in JS](Rewrite-1.1.7#packaging)).
Most block UIs today are Shiny inputs that their authors compose in R instead, as core's head block draws `numericInput()` ([R/transform-head.R#L45](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/transform-head.R#L45)).
Composing a UI in R from blockr.ui's components would keep that way of writing a block for an author who writes no JS.
An earlier draft of the R side, with its elements, its layout and its attributes that depend on the data, is [Input elements for block UIs written in R](Rewrite-1.7.1), which this item replaces.

The kit holds nothing that knows a block ([UI kit and design system for the client](Rewrite-1.7#what-must-hold)), so the work splits in two:

1. The R constructors of blockr.ui build a UI as data, as `number_field("n", "Number of rows", min = 1)` within `stack()` or `row()`.
   The first argument is the key of the value that the input binds, which blockr.ui does not know to be a state arg.
2. An attribute given as an R function, as `max = \(data) nrow(data)`, becomes a dynamic attribute with a key, `n.max`.
   The description keeps the function for whoever uses it, and blockr.ui never reads its arguments.
3. The JS of blockr.ui draws a description with its components.
   Whoever mounts it hands it two functions: one that gives the `Bound` for a key ([The components of blockr.ui](Rewrite-1.7.3#the-interface-bound)), and one that gives a dynamic attribute's current value.
4. A package above core ties a description to a block class.
   Its UI module mounts blockr.ui's drawing and binds each key with core's `useValue()`.
   Each dynamic attribute becomes a request of the block class, which the module asks again whenever an input or a state arg that the function names changes, as core's `follow()` asks a request again whenever what it reads changes ([srcts/binding/binding.ts#L44-L46](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/srcts/binding/binding.ts#L44-L46)).

The tie needs nothing new from core: the module contract, `useValue()`, `follow()` and requests are there.
Its module gets the description of a block's class through a request of the class, whose answer core keeps for every block of the class ([UI modules in JS](Rewrite-1.1.7#the-contract)).
One module serves every class that the package ties, as blockr.ggplot draws its four block classes with one module from a declarative schema of fields ([inst/js/gg-blocks.js#L85-L102](https://github.com/BristolMyersSquibb/blockr.ggplot/blob/289cb60f03d10caf13d143d06562f7eb663763d9/inst/js/gg-blocks.js#L85-L102)).

What it would remove: the JS that a block package writes for a UI of common inputs, and the need for its author to write any.

What it would cost: an R constructor and its drawing in blockr.ui for each component that a form uses, with containers for the layout, and the package that ties descriptions to block classes, with its R function, which makes a block class's UI and requests from a description, and its module.

What would settle it: a spike that builds the tie and ports two of core's built-in blocks whose UIs read the data, head and merge ([R/transform-merge.R#L67](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/transform-merge.R#L67)), with the project built if both work with no change to core.
The spike also settles two questions that the draft left open:

- Which containers the first set has besides rows and gear trays, such as tabs or sections that collapse.
- Whether an attribute that reads only state, such as whether to show a field, is worked out in the client without asking R, since R runs one request at a time, and a UI with several dynamic attributes waits on each ([UI modules in JS](Rewrite-1.1.7#the-contract)).

## User options

A user option would be a third kind of option, beside board options and blockr options, for what each user picks for themselves, such as the mode that `dark_mode` switches.
An app's script could set its value as the app starts, as a script sets a board option today, while the board would never save it and the browser would keep the user's pick.
In State in JS, a board option whose definition has `scope: "user"` does this job instead, and `dark_mode` is the only such board option ([Board options and blockr options](Rewrite-1.1.13#board-options-that-stay-with-the-user)).
A script gives it no value, and an app sets its default through the blockr option `dark_mode`.

What it would remove: the `scope` of a board option, and with it a board option whose value no board holds, which the name "board option" does not fit.

What it would cost: a kind of option of its own in core, with its definitions and their registration, a constructor in R whose value R hands to the page rather than writing it into the board, and a place in each frontend that draws options, beside the board options.

What would settle it: a second option that should stay with the user, or an app that has to set the mode in its script rather than through a blockr option.

## Another kit in place of blockr.ui's components

Every UI of blockr's packages draws with blockr.ui's components, which style React Aria's components with Tailwind's classes.
An app restyles them through the theme variables alone: colours, fonts, sizes of text, radii, shadows and spacing ([The theme variables](Rewrite-1.7.2#which-theme-variables-blockrui-declares)).
So an app can give every UI Bootstrap's colours and proportions, but not the shapes of Bootstrap's components.
An app that brings its own blocks may draw everything that core draws with another kit, while the UIs of other packages, such as the dock and the blocks of blockr.dplyr, keep blockr.ui's components ([UI kit and design system for the client](Rewrite-1.7#what-blockrui-holds)).
A package could instead offer the same components, under the same names, with the same props and `Bound`, styled with CSS of its own, as React Aria's starter kit in plain CSS styles React Aria's components ([starters/docs](https://github.com/adobe/react-spectrum/tree/react-aria-components%401.22.1/starters/docs)).
The page's import map would then resolve `@blockr/ui` to that package's files, so that every UI draws with them, which the design keeps open ([Building on blockr.ui](Rewrite-1.7.4#the-bundle)).
Raised in the review of [Building on blockr.ui](Rewrite-1.7.4) on 2026-11-24.

What it would remove: the limit that the theme variables set on how far an app restyles the UIs of other packages.

What it would cost: a way for an app to name the kit, such as a blockr option, which R reads as it writes the page's import map from the entries of each package ([Building on blockr.ui](Rewrite-1.7.4#the-bundle)); the kit itself, which implements every component of blockr.ui with its props and sets every theme variable, since the classes of other packages read them ([Building on blockr.ui](Rewrite-1.7.4#the-list-of-theme-variables)); a stylesheet that styles the kit's components alone, as every package's does, and so not Bootstrap's own, which styles every element of the page ([Building on blockr.ui](Rewrite-1.7.4#what-must-hold)); and test helpers of its own wherever it draws a part somewhere other than where React Aria draws it, since the tests of other packages act on the components through the helpers of `@blockr/ui/stubs` ([The components of blockr.ui](Rewrite-1.7.3#testing)).

What would settle it: whether an app asks for a look that the theme variables cannot give, such as the shapes of Bootstrap's components.

## Each icon once on the page

Each package's build bundles the icons that it imports from `@blockr/ui/icons`, so an icon that two packages import sits in the files of both, at about 300 bytes each ([The components of blockr.ui](Rewrite-1.7.3#the-icons)).
R could serve each icon to a page once instead:

1. Each package's build would list the icons that its files import, beside its `inst/js/preload.json`.
   The preset would read the names off each import of `@blockr/ui/icons`, since esbuild reports which files a file imports but not which names it takes from them.
2. As the app starts, R would write one module with the union of the lists of the packages whose modules the page may load, from the icons of Lucide that blockr.ui would ship as data in R.
3. The page's import map would resolve `@blockr/ui/icons` to that module, under a URL with a hash of its content, so that the browser caches it.

It would remove the copies, and put every icon on the page at one version of Lucide, where each package otherwise draws the version that it built against.
It would cost the preset's reading of the imports, R's writing and serving of the module, and an entry of the import map that differs from app to app.
A list that fell behind its code would also fail to load the module that imports a missing icon, as a whole.
What would settle it is the weight of the copies on a page: on `js-state`, core and the dock both draw five icons, whose copies come to under 1 KB gzipped, while [Building on blockr.ui](Rewrite-1.7.4#the-bundle) lets a page load 16 KB of React Aria that it may not use.
The preset keeps it open, since every package imports its icons through `@blockr/ui/icons`, so that it would change no package's code.

## An empty New, and New in core's storage plugin

Session management's "New workflow" opens the board that R sent, blocks included ([Session management as a storage plugin](Rewrite-1.6#proposal)), as today's New does in an app that passes no loader to `serve()`.
Today's `rack_loader()` gives New an empty board instead: the script's board without its blocks, links and stacks, with its board options and the state of its extensions.
A second row, "New empty workflow", could give that board, and core's storage plugin could offer New and New empty beside Save and Open, so that a core app starts over without a reload.
It would remove the reload that starting over takes in a core app, and the empty board that a script would otherwise serve so that New starts empty.
It would cost an option of the core change that lets a plugin open the board that R sent: the store would drop its blocks, links and stacks as it drops a block that it cannot rebuild, through core's expansion and each plugin class's `update` ([Board updates](Rewrite-1.1.2#opening-a-board)).
For core's storage plugin it would cost two buttons too, with edits to [Plugins](Rewrite-1.1.12#storage), [The dock's navbar](Rewrite-1.2.5#the-storage-plugins-controls) and the [Glossary](Glossary).
Under the load lock, New could stay, since it opens the opening board, while New empty could not.
Users of the new stack asking for an empty start, where the app's board holds blocks, would settle it.
