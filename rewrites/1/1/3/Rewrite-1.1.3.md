# Defining a board in R for the client-owned board
Status: settled on 2026-10-28. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): the R code that defines and launches an app, and how the board it builds becomes the client's opening board.
It builds on the [board objects proposal](Rewrite-1.1.1) and the [serialization proposal](Rewrite-1.1.4), and shapes removing the setters and modifiers of board objects ([blockr.core#418](https://github.com/BristolMyersSquibb/blockr.core/issues/418)), porting core's built-in blocks ([blockr.core#423](https://github.com/BristolMyersSquibb/blockr.core/issues/423)), what packages declare in R ([blockr.core#424](https://github.com/BristolMyersSquibb/blockr.core/issues/424)), the board's name and id ([blockr.core#427](https://github.com/BristolMyersSquibb/blockr.core/issues/427)), writing a board's JSON in R by schema ([blockr.core#428](https://github.com/BristolMyersSquibb/blockr.core/issues/428)), reading a JSON board in R ([blockr.core#429](https://github.com/BristolMyersSquibb/blockr.core/issues/429)), saving JSON boards in the client ([blockr.core#436](https://github.com/BristolMyersSquibb/blockr.core/issues/436)), serving a board with `serve()` ([blockr.core#442](https://github.com/BristolMyersSquibb/blockr.core/issues/442)), taking the app's plugins in `serve()` ([blockr.core#558](https://github.com/BristolMyersSquibb/blockr.core/issues/558)), the migration notes for app scripts ([blockr.core#445](https://github.com/BristolMyersSquibb/blockr.core/issues/445)), filling the block registry from the packages that the app names ([blockr.core#498](https://github.com/BristolMyersSquibb/blockr.core/issues/498)) and keeping links and stacks to core's properties ([blockr.core#511](https://github.com/BristolMyersSquibb/blockr.core/issues/511)), each an item in the Work list of [Client-owned board state](Rewrite-1.1#work).
How a block class is written is the block classes proposal ([Block classes in R](Rewrite-1.1.5)), what a plugin is and how a script gives an app its plugins are [Plugins](Rewrite-1.1.12)'s, and how a frontend draws the board is [Drawing the board](Rewrite-1.1.8)'s.

## What must hold

1. An app script keeps the shape it has today: `serve()` around a board constructor that takes blocks, links, stacks, board options and the state of plugins, while `serve()` takes the app's plugins, as it takes today's ([Plugins](Rewrite-1.1.12#a-plugin)).
2. The board the script builds reaches the client as a JSON board, as the client saves one, and R keeps nothing of it that an edit changes.
3. A block class defined in the app script works in every board the app opens, deployed or not.
4. R's `blockr_ser()` writes each value of a board as the client writes it in a JSON board, wherever a schema gives the value's shape.
5. Serving a single block while developing it, and serving a JSON board, work as today, but that where both locks are on, R refuses a JSON board that it cannot read as today's packages write one ([Locked boards and the properties of blocks](Rewrite-1.1.11#serving-a-json-board-locked)).
6. Data that a script hands to `serve()` stays in R, so no board, file or request carries it.
7. An app sets its blockr options as today, through R options and environment variables, which `blockr_option()` reads, and the board holds none of them, so its JSON describes the board in full.
8. An object an app script builds holds its class and what its counterpart in the client's board holds, its id, name and state, and a block its `locked` too, and nothing else.

## Today

The `serve()` generic has methods for a block, a board and the path of a saved file ([R/utils-serve.R#L28-L120](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L28-L120), [#L297-L305](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L297-L305)).
For a board, `serve.board(x, id, plugins, options, loader, ...)` combines `blockr_app_ui()` and `blockr_app_server()` ([#L204-L218](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L204-L218)), and blockr.dock implements those for `dock_board`, adding its navbar ([blockr.dock R/utils-serve.R#L2-L86](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serve.R#L2-L86)).
It keeps the board the script built for the process, and its `loader` may replace that board at each request, at the page's GET and again at the websocket's connect ([#L227-L273](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L227-L273)): the default `local_loader()` carries a board across the `session$reload()` that a restore triggers ([R/board-loader.R#L111-L168](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-loader.R#L111-L168)), and blockr.session's `rack_loader()` loads the board a URL names ([R/server.R#L1207-L1289](https://github.com/BristolMyersSquibb/blockr.session/blob/5f9b8e6aff54a58f84d2658963194c60e8a4262a/R/server.R#L1207-L1289)).
For a block, `serve.block(x, data = list(...))` hands each input's data straight to the block's server as a reactive value, with no board around it ([#L36-L91](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L36-L91)).
A board gets data that an R script holds through `new_static_block()`, which keeps the data in its state and reads it back from its constructor's environment ([R/data-static.R#L12-L36](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/data-static.R#L12-L36)).
A dock app reads ([inst/examples/edit-board/app.R#L9-L20](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/inst/examples/edit-board/app.R#L9-L20)):

```r
serve(
  new_dock_board(
    blocks = c(a = new_dataset_block("iris"), b = new_head_block()),
    links = links(ab = new_link(from = "a", to = "b", input = "data")),
    stacks = stacks(grp = new_dock_stack(blocks = "a", name = "Group A")),
    extensions = new_edit_board_extension()
  ),
  "my_board"
)
```

## Proposal

### The script

That script stays as it is, but for the packages it names in `serve()` ([The `serve()` generic](#the-serve-generic)), while the objects its constructors return hold only what their counterparts in the client's board hold: each its class, its id, name and state, and a block its `locked` too ([Board objects](Rewrite-1.1.1#the-board)).
A block holds its state, its name and its `locked` and refers to its block class ([Block classes in R](Rewrite-1.1.5)), a link its ends and input, a stack its blocks, name and colour ([Board objects](Rewrite-1.1.1#stacks)), and the board its blocks, links, stacks, board option values, name and plugins, each plugin its class, name and state, of which R reads the state from the board's list and the name from the list that `serve()` takes ([Plugins](Rewrite-1.1.12#a-plugin)).
The Shiny servers and UI functions they hold today go, and core's plugins of today become commands and plugins of the new kind, as [Plugins](Rewrite-1.1.12#today) maps them.

The constructors keep the arguments that carry such state, and `class`, through which a constructor that extends a link or a stack, such as `new_dock_stack()`, names its class in R ([R/stack-class.R#L47-L78](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/stack-class.R#L47-L78)), while `new_board()` loses its `class` and the components that its `...` adds ([R/board-class.R#L38-L62](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-class.R#L38-L62)), which its `plugins` replaces, so that every R board is of class `board` ([Plugins](Rewrite-1.1.12#what-goes)).
Their `ctor` and `pkg` arguments go, since a JSON board names no R constructor ([Serialization](Rewrite-1.1.4#files)), and nothing in R opens one: the client opens every board, finding each block's class in the block registry by its registry id ([Block classes in R](Rewrite-1.1.5)) and each plugin's class by the class's id, and draws it with the app's frontend ([Drawing the board](Rewrite-1.1.8#opening-a-board)).
R writes each plugin with its class's id instead, as `blockr.dock-dock_plugin` for the dock, in the opening board's state and among the app's plugins alike, by which the client finds the class of every plugin, the frontend included, and its package ([Plugins](Rewrite-1.1.12#a-plugin)).
A script passes neither argument, and what a plugin adds to a link or a stack lives in the plugin's state, keyed by the object's id ([Board objects](Rewrite-1.1.1#extending-cores-objects)).
The dock's `new_dock_board()` keeps its extensions, views, grids and active view ([R/dock-board.R#L55](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L55)), all of which a board needs to open, save and restore ([Client-drawn dock and extensions](Rewrite-1.2)), and returns a board that holds the state of the dock plugin and of a plugin for each extension, which plugins the script passes to `serve()` ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)), while a board option's constructor takes its value alone, since the package that ships the board option defines the rest in the client, its label, category, schema, default, UI and what a new value does ([Board options and blockr options](Rewrite-1.1.13#board-option-values-in-r)), and only two tests set a label or a category today.
Of these, `new_board()` gains a `name`, as blocks and stacks have one, and the board's name replaces core's `board_name` board option, while `new_board()` also takes the board's `id`, which `serve()` takes today (below), and the state of its plugins in `plugins` ([Plugins](Rewrite-1.1.12#a-plugin)).
No block holds data in its state (below).

In R, these objects become a definition language that R translates to JSON: constructors that build and check them, `blockr_ser()` that writes them and the accessors it uses.
R opens no board given as JSON, which the client opens, so it builds them only for the board a script defines, and, where both locks are on, for the JSON board that `serve()` is given ([Locked boards and the properties of blocks](Rewrite-1.1.11#serving-a-json-board-locked), [Board objects](Rewrite-1.1.1#the-board)).
Nothing changes a board in R, since every change is a delta in the client ([Board updates](Rewrite-1.1.2)), so core's setters and modifiers go (notes).
Every caller of them in the workspace is server code that moves to the client, except one script: CEDX derives its board from another with `rm_blocks()` and `board_links<-` ([R/cedx_board.R#L1072-L1092](https://github.com/BristolMyersSquibb/blockr.cdex/blob/7792b7e0fd9eda417995dd7e460f086f671df73c/R/cedx_board.R#L1072-L1092)), and builds it from that board's parts instead.
The containers that hold blocks, links and stacks need only be built and checked once, by the board's constructor, so of today's vctrs vectors and records they keep what a script builds with, such as `c()` on blocks, and lose the methods that keep them valid under modification, such as `names<-` ([R/blocks-class.R#L80-L94](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/blocks-class.R#L80-L94)), `[<-` and `[[<-` ([#L156-L202](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/blocks-class.R#L156-L202)).

### The opening board

An app gives its board in one of two ways.
Built with constructors, as the script above builds it, the board is converted to a JSON board once, when `serve()` is called as the script's top level runs, with every id, since the constructors draw each id the script left out ([Board objects](Rewrite-1.1.1#ids)): R registers the block classes its blocks refer to, from the blocks themselves, and writes it with `blockr_ser()`.
Given as JSON, as a path given to `serve()` is, it is a JSON board already ([Serialization](Rewrite-1.1.4#files)), of which R reads only its format, but its blocks and links too where both locks are on ([Locked boards and the properties of blocks](Rewrite-1.1.11#serving-a-json-board-locked)), and which it passes on as it is, for the client to open as it opens every JSON board, migrating what it holds in an older shape and dropping what the app cannot rebuild ([Board updates](Rewrite-1.1.2#opening-a-board)), while R loads no package for it, since the app names the packages whose block classes it offers ([The `serve()` generic](#the-serve-generic)).
R sends either in `board` with every reply to a session's `hello`, beside the block registry's entries ([Wire protocol](Rewrite-1.1.9#handshake)).
So the opening board holds nothing a JSON board cannot, such as a closure in a block's state, and a board the format cannot hold fails when the script runs, not when a session starts, while the store refuses an opening board with a value that its schema refuses, naming every such value, for the deployment to fix ([Board updates](Rewrite-1.1.2#opening-a-board)).
From then on the client owns the board, and R holds the session's results and, for the process, the opening board's JSON, which no edit changes, and, where both locks are on, what it built from the opening board to hold every block to it ([Locked boards and the properties of blocks](Rewrite-1.1.11#what-r-refuses)).

Registering the classes first keeps an app's own block classes working.
A class defined in the app script reaches the JSON only by its registry id ([Board objects](Rewrite-1.1.1#block-classes-outside-a-package)), so if the script's board were only JSON, the app would drop its own blocks.
Registered from the blocks, as [Board objects](Rewrite-1.1.1#the-board) has it for a board from a constructor call, each class is in the block registry before any session evaluates a block of it.
These registrations are the app script's own, so they stay when another board is opened, as a fresh app would have them ([Board updates](Rewrite-1.1.2#what-must-hold)), and a board saved from the app reopens in it, deployed or not.

The `loader` argument goes, since neither of today's loaders keeps its job: `store.open()` replaces the board in place, so no reload needs `local_loader()` to carry a board across it ([Board updates](Rewrite-1.1.2#opening-a-board)), and session management opens the board a URL names from the browser, which makes every storage call ([Session management as a client extension](Rewrite-1.6)).
So R writes the opening board once per process and sends it to every session.
A session under the load lock shows its script's board, since the load lock fixes the app to its opening board ([Locked boards and the properties of blocks](Rewrite-1.1.11#the-load-lock)), and no app today picks in R the board that a session shows under today's lock.
What remains of the loader is an ordering on the client: where `rack_loader()` resolves the board a URL names before the page is drawn, session management fetches it from its package's startup module a few round trips after the `hello`, and core opens it in place of the script's board, before anything is drawn or evaluated ([Drawing the board](Rewrite-1.1.8#starting-the-page)).

### Writing the opening board

R's `blockr_ser()` writes the opening board as a JSON board, and the client every board that is saved, in the one format of [Serialization](Rewrite-1.1.4#files), and both write each value of a board the same way, by the same schemas, those of a JSON board, of each block class's state, of each board option and of each plugin class's state ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)).
R records the versions of the shapes the board holds as the client does, each block's from its class, each plugin class's from its method of `plugin_version()` and each board option's from its method of `board_option_version()`, and the packages it records are those of its plugins' classes and its blocks' classes.
Fixtures that both test suites round-trip hold the two together, as they do the messages of [Wire protocol](Rewrite-1.1.9): each is a board as constructor calls that gives every id and the JSON board R writes for it, which the client opens and saves unchanged.

The opening board is where every app meets R's lack of scalars, since R writes the state of the script's blocks: `new_merge_block(by = "Time")` holds `by` and `all_x` as vectors of length one, and the client needs the first as `["Time"]` and the second as `false`, which R writes by the schema that the merge block's UI ships for its state ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)).

### The `serve()` generic

The `serve()` generic and its three methods stay.
For a board, `serve.board()` starts a Shiny app whose page loads core's client and the app's frontend, such as the dock for an app whose plugins hold the dock plugin, and whose server carries the protocol and evaluates.
The client loads the app's frontend, whether the script built the board or `serve()` was given a file ([Plugins](Rewrite-1.1.12#the-frontend)), and the `blockr_app_ui()` and `blockr_app_server()` methods go, since a package now offers its frontend in R as a module, which the page loads ([Drawing the board](Rewrite-1.1.8#what-a-package-declares-in-r)).
The board's id moves from `serve()`, where it is the board's namespace today, to the board: `new_board()` takes an `id`, which a script may leave out, as it may leave out those of blocks, links and stacks, where `serve()` draws its `id` today ([R/utils-serve.R#L120-L132](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L120-L132)), and `new_board()` draws one where it is left out ([Board objects](Rewrite-1.1.1#ids)), so a script that passes an id to `serve()`, as the dock app above passes `"my_board"`, passes it to the board's constructor instead.
A board given as JSON keeps the id it holds, whether `serve()` is given its path or the client opens it with `store.open()` ([Board objects](Rewrite-1.1.1#the-board)).
For a block, `serve.block(x, data = list(...))` serves the block and its data with no board around them, as today (below), but without today's `id`, since R serves the block as a board of one block, whose constructor draws the block's id, and with no plugin, since no frontend places one for a block served alone.
For a path, `serve()` keeps the file in place of the JSON it would write, and passes it on as it is, beside the app's plugins, for the client to migrate as it opens it ([Serialization](Rewrite-1.1.4#migrations)), while where both locks are on R reads its blocks and links too, and refuses a file that it cannot read as today's packages write one ([Locked boards and the properties of blocks](Rewrite-1.1.11#serving-a-json-board-locked)).
Every method takes in `packages` the packages whose block classes and modules the app offers, core always among them, which R reads as the app starts ([Block classes in R](Rewrite-1.1.5#registration)), since what an app offers is the app's and never a board's, as in `serve(new_board(), packages = "blockr.dplyr")`.
The methods for a board and for a path take the app's plugins in `plugins`, as a list that holds one frontend and at most one storage plugin, which run on every board that the app opens, the opening board among them, while the board and the file give only their state, so that a file never sets which plugins run ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)), and [Plugins](Rewrite-1.1.12#today) maps each of today's nine plugins to its new home.
By default, `plugins` holds core's basic frontend, its storage plugin and its Edit board plugin, `list(new_basic_frontend_plugin(), new_file_storage_plugin(), new_edit_board_plugin())`, so that an app whose script gives no plugins draws the board, saves it as a download and opens an upload, and lets the user add blocks and edit links and stacks, whether the script built the board or `serve()` was given a file ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has), [The Edit board plugin](Rewrite-1.1.15#what-serve-gives-by-default)).
Nothing else of today's `serve()` carries over, since each piece serves the R board or its UI, and what the new stack still needs of them it builds anew: the `options` argument that `custom_options()` fills, since a board holds only the board option values that something sets, while core resolves the defaults of those that something on the page requires ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)); `blockr_test_exports()`, through which shinytest2 reads the block servers' results and the dock's sync counters, whose place what core exports for end-to-end tests takes ([Drawing the board](Rewrite-1.1.8#testing)); what `serve()` passes through `...` to a frontend's UI, such as the dock's `navbar`, whose items become plugins' contributions on the client ([Client-drawn dock and extensions](Rewrite-1.2)); and the URL's query, which the client reads itself.
The methods for a board and for a path refuse every argument but the board or the path, `plugins` and `packages`, with an error that says where each of today's others went, such as `id` to `new_board()`, and evaluate none of them, so a script that still passes `loader = local_loader()` gets that error rather than one about a function that is gone ([blockr.core#545](https://github.com/BristolMyersSquibb/blockr.core/pull/545)).

### Data passed to `serve()`

A single-block app is for a block's developer, who serves the block with fixed data, as `serve(new_head_block(), data = list(data = iris))` does, and it has no board, as today: the page shows the block in a card of its own, and nothing in the app can change the data ([R/utils-serve.R#L36-L91](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L36-L91)).
The card shows the block's name, its UI, its output and a footer, one centred line of the block's status: a ready block's summary, or why a waiting block waits, and a pill for each severity of the conditions of R's reply ([blockr.core#545](https://github.com/BristolMyersSquibb/blockr.core/pull/545)).
The pill of the errors reads `error`, and those of the warnings and the messages count them, since a message of R's can be of any length, which the line has no room for.
Each pill opens and closes the banners of its conditions below the output, each condition in full, in the colour of its severity and in the order R raised them, and the pill of the errors is open from the start, so that a failed block shows its error at once.
While R evaluates the block, the footer and the output dim and keep what they show, and the output dims too while the block is not ready.
Core's client mounts both through the same `mountBlock()` and `mountOutput()` a frontend uses ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)), and keeps the block's state in its store and evaluates it with its scheduler, as it does a block on a board, so the page needs no runtime of its own, while nothing draws, saves or opens the block as a board, and the `hello` reply carries it as a board of one block, which only the store sees.
R keeps the data for the process and binds each entry to the block's input of that name whenever it evaluates the block, as today's `serve.block()` hands the data to the block's server, so the evaluation requests name no upstream block for an input R binds, and the data reaches neither a file nor the client, except as the block's output.
R takes the data from `data`, or from `...` where `data` is empty, and ignores `...` otherwise, with a warning that names what it ignores.
Each entry needs a name: R binds it to the block's input of that name, and for a variadic block, an entry that names none of its inputs goes into the block's `...` under that name, as in `serve(new_rbind_block(), a = iris, b = mtcars)`.
R refuses an unnamed entry, which today's `serve.block()` gathers into `...args`, since the reply to `hello` names each input that R binds in `bound`.

A board takes no data from `serve()`, since its data comes from its data blocks, and core's static block is the plainest of them: a block whose state is one expression that reads no data input, given as a string, which R evaluates for the block's result and shows as its code, such as `new_static_block("datasets::iris")`, `new_static_block("head(datasets::iris)")` or `new_static_block("safetyData::adam_adsl")`, which name the package of the data, since a block expression sees base R alone unless the blockr option `attach_default_packages` is set, as `eval_env()` has it today.
Its state holds code and never data, so the board, its files and its requests carry the expression while the data stays in R, and the code exported for the board reproduces the data.
Today's `new_static_block()` holds a data frame in its state and reads it back from its constructor's environment ([R/data-static.R#L12-L36](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/data-static.R#L12-L36)), and the tests and examples that call it with a data frame, such as blockr.ui's and blockr.dm's example apps ([inst/examples/table-preview/app.R#L29](https://github.com/BristolMyersSquibb/blockr.ui/blob/9bd8312a3408bbcbabff2b57d1d3fd5681843c94/inst/examples/table-preview/app.R#L29), [blockr.dm inst/examples/filter-demo/app.R#L38](https://github.com/BristolMyersSquibb/blockr.dm/blob/938428bce5a488f2479034eef088f86a5053e09d/inst/examples/filter-demo/app.R#L38)), give it an expression instead, as blockr.ui's can with `"safetyData::adam_adsl"`.

### Board options

A script gives a board option only to set a value other than its default, as `new_board(options = new_n_rows_option(25))` does, and R writes each such value under its id ([Board options and blockr options](Rewrite-1.1.13#board-option-values-in-r)).

### Blockr options

An app sets its blockr options as today, the board holds none of them, and a constructor argument that configures rather than holds state becomes a blockr option where it is a value ([Board options and blockr options](Rewrite-1.1.13#blockr-options)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

Each shared fixture is a board as constructor calls that gives every id, so that nothing is drawn at random, and the JSON board `blockr_ser()` writes for it.
R's suite writes the JSON board from the calls, and the client's suite opens it and saves it unchanged.
Between them, the fixtures cover a block class defined outside a package, the dock plugin's state, a board option, and length-one vectors of both kinds.

Today's `serve.block()` matches the names in `data` to the block's inputs and, for a variadic block, gathers the entries that match none into `...args` ([R/utils-serve.R#L49-L70](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L49-L70)).
Building it showed that the store holds the single block without trouble, and that the scheduler takes `bound` into its recipes, so the block needs no runtime of its own ([blockr.core#545](https://github.com/BristolMyersSquibb/blockr.core/pull/545)).
The static block class's one state arg holds the expression as a string, which it parses with `str2lang()`, and a string that does not parse is an error: its constructor parses it, so a script with such a static block fails when it runs, and a board opened from a file reports the parser's message when R builds the block's expression ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)), as it reports an expression that parses but fails, such as one naming a package that is not installed.
A script that still passes a data frame gets an error that asks for an expression.

The setters that go are `board_blocks<-`, `board_links<-`, `board_stacks<-`, `board_options<-`, `block_name<-`, `stack_blocks<-` and `stack_name<-`, and the modifiers `modify_board_links()`, `modify_board_stacks()`, `rm_blocks()`, `update_link()`, `update_stack()`, `add_block_to_stack()`, `remove_block_from_stack()`, `clear_board()` and `set_board_option_value()`, all exported by core at `da3fcb4`.
Their callers outside core are blockr.dock's actions, sidebars, board options and edit extension, blockr.assistant's staging and board option tools, blockr.session's loader and CEDX's script.
Opening a board needs none of them: the client drops a block it cannot rebuild with that block's links and stack places, as `drop_block_refs()` prunes the parts R read today ([R/utils-serdes.R#L433-L457](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L433-L457)).

</details>
