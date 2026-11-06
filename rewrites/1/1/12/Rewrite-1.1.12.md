# Plugins for the client-owned board
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): what a plugin is in R and in JS, the plugin classes core defines in R, the frontend and storage plugins, which plugins a board has, how a plugin runs, and a plugin's state.
Plugins are core's second way to extend a board, beside block classes, and take the place of three mechanisms: core's plugins of today, the dock's extensions, and the board classes of [Board objects](Rewrite-1.1.1#the-board) and [Board updates](Rewrite-1.1.2#board-classes-and-attributes).
It changes what [Front-ends and extension points](Rewrite-1.1.8) says about registering a frontend and about extensions, and shapes `CoreApi` and starting the page ([blockr.core#440](https://github.com/BristolMyersSquibb/blockr.core/issues/440)), core's basic frontend ([blockr.core#441](https://github.com/BristolMyersSquibb/blockr.core/issues/441)), serving a board ([blockr.core#442](https://github.com/BristolMyersSquibb/blockr.core/issues/442)) and saving boards in the client ([blockr.core#436](https://github.com/BristolMyersSquibb/blockr.core/issues/436)), while no issue asks for plugins yet.
What core gives a frontend, starting the page and renderers stay with [Front-ends and extension points](Rewrite-1.1.8), and what the dock plugin keeps in its state and where it places other plugins stay with [Client-drawn dock and extensions](Rewrite-1.2).

## What must hold

1. Core has two ways to extend a board, block classes and plugins, and no other, so a board has no class of its own.
2. A plugin works under every frontend: it works on the board through `CoreApi`, keeps its state in the board, and offers its UI as a module that core mounts where the frontend puts it.
3. The frontend is a plugin, and every frontend places every plugin that has a UI, including one from a package it does not know.
4. A board holds all its plugins, its frontend and its storage plugin among them, and opening a board runs exactly those whose packages the app loads and drops the others, naming what to install, as it drops a block ([Board objects](Rewrite-1.1.1#what-must-hold)).
   So the page is what serving that board in a fresh app would give, whatever was open before, as condition 6 of [Board updates](Rewrite-1.1.2#what-must-hold) asks, and a JSON board describes the whole app.
5. A board that holds no frontend, or no storage plugin, takes those of the board it replaces, so opening it never switches what draws the page or where the page saves.
6. A plugin's state belongs to that plugin alone, keyed by its id: it is saved, undone and migrated with the board, and its shape is its class's own, so that the states of two frontends share nothing.
7. Boards saved by today's blockr.dock open with their views, their layouts and the state of their extensions, as condition 4 of [State in JS](Rewrite-1#what-must-hold) asks.
8. A board holds as many plugins of one class as it needs, such as two documents of blockr.md, but at most one frontend and one storage plugin.

## Today

Three mechanisms extend a board, two on main and one on `js-state`:

- **Core's plugins** are Shiny module pairs that `new_plugin(server, ui, validator, class)` makes, each of exactly one of the nine classes that `known_plugins()` lists, with its class as its id ([R/board-plugins.R#L38-L75](https://github.com/BristolMyersSquibb/blockr.core/blob/460afef170ed67ec926a75ed66021bc98ce61647/R/board-plugins.R#L38-L75)).
  The app sets them: `serve()` takes `plugins` as a function, which gives every board the app serves its plugins, restored boards included, and no file holds them ([R/utils-serve.R#L120-L160](https://github.com/BristolMyersSquibb/blockr.core/blob/460afef170ed67ec926a75ed66021bc98ce61647/R/utils-serve.R#L120-L160)).
  So an app swaps blockr.session's storage in for core's with `serve(plugins = custom_plugins(manage_project()))` ([README.Rmd#L38-L47](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/README.Rmd#L38-L47)).
- **The dock's extensions** are Shiny module pairs that `new_dock_extension()` makes, which `new_dock_board(extensions = ...)` puts on the board.
  The board sets them: saving writes each with its constructor, the constructor's package and its state, and restoring calls each constructor that the file names, loading its package where it is installed ([blockr.dock R/utils-serdes.R#L78-L185](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/utils-serdes.R#L78-L185), [R/utils-serdes.R#L518-L539](https://github.com/BristolMyersSquibb/blockr.core/blob/460afef170ed67ec926a75ed66021bc98ce61647/R/utils-serdes.R#L518-L539)).
- **Board classes**, on `js-state`, are defined in JS with the properties they add, each with a schema and a default, and with an `update` and a `migrate` for them, while R names each class's front-end and version through `board_front_end()` and `board_version()` ([blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474), [srcts/store/registrations.ts](https://github.com/BristolMyersSquibb/blockr.core/blob/3536c4dad52b09bb6f9adb220d4981b1350276b9/srcts/store/registrations.ts)).
  The dock board adds its views and layouts as properties, and keeps the state of its extensions in its `extensions`.

| Today | Where it goes |
|---|---|
| `preserve_board`, with core's Import and Export | Core's storage plugin, which saves a board as a download and opens an upload ([Storage](#storage)) |
| `manage_project()` of blockr.session | Its storage plugin ([Session management as a client extension](Rewrite-1.6)) |
| `generate_code`, core's and blockr.code's `generate_flat_code()` ([blockr.code R/plugin.R#L31-L35](https://github.com/BristolMyersSquibb/blockr.code/blob/72b20d6911496e4edc9ee64db758e70ebf3f50ca/R/plugin.R#L31-L35)) | The plugin of blockr.code ([Code export as a client extension](Rewrite-1.5)) |
| `manage_blocks`, `manage_links`, `manage_stacks`, `edit_block`, `edit_stack`, `notify_user` and `ctrl_block` | Where the notes of [Client-drawn dock and extensions](Rewrite-1.2) put them: core's commands, with the menus, cards, stack editors and notifications of the frontend and the DAG |
| The `ctrl_block` of blockr.ai, `ai_ctrl_block()`, a chat on every block ([blockr.ai R/ai-ctrl-block.R#L51-L56](https://github.com/BristolMyersSquibb/blockr.ai/blob/7441767266cd982858bef0c633bcad5597698a0a/R/ai-ctrl-block.R#L51-L56)) | Dropped, since the assistant, a plugin, replaces it ([Assistant as a client extension](Rewrite-1.4)) |
| The dock's extensions: the DAG, blockr.md's document, the assistant, the Edit board extension, blockr.viz's control bridge, and the outline, slides, report and minidag of blockr.outline | A plugin each, whose state is the extension's state |
| Board classes, the dock board among them | A frontend each, the dock plugin among them, whose state holds what the class's properties held ([The frontend](#the-frontend)) |

## Proposal

### A plugin

In R, a plugin is an S3 object of class `c("{name}_plugin", ..., "plugin")`.
A package's constructor `new_{name}_plugin()` returns one, made with core's `new_plugin()`.
Its args are the state it gives the board an app script builds, such as the DAG's `positions`, as a block's args are its state, and `plugin_name` gives its name, as `block_name` gives a block's.
Its class's id is `{pkg}-{name}_plugin`, as `blockr.dag-dag_plugin`.
That id joins the class to its package, the one its constructor lives in, as a registry id carries its package ([Board objects](Rewrite-1.1.1#registry-ids)).
The version of its state's shape is what its class's method of `plugin_version()` returns, 1 where it has none, in place of `board_version()`.
The board constructor takes the board's plugins in `plugins`, as `new_dock_board(extensions = ...)` takes extensions today, and a plugin's id is its name in that list ([Which plugins a board has](#which-plugins-a-board-has)):

```r
new_board(
  blocks = blks,
  plugins = list(
    new_dock_plugin(),
    new_dag_plugin(positions = pos),
    notes = new_md_plugin(content = "# Notes", plugin_name = "Notes"),
    report = new_md_plugin(content = "# Report", plugin_name = "Report")
  )
)
```

R writes each plugin into the opening board under its id, with its class's id, its name and its state, and records each class's version ([Serialization](Rewrite-1.1.4#files)).
In the reply to `hello`, R sends the versions that loaded packages give their plugin classes, by the class's id, in `plugin_versions`, where a class without a method of `plugin_version()` is at version 1, as `option_versions` has it for board options ([Wire protocol](Rewrite-1.1.9#handshake)).
The client takes a plugin's package from its class's id, and where its UI module is served from the modules that packages offer each other, so R keeps no list of plugin classes.

In JS, the package's startup module registers each of its plugin classes once, under the class's id, where it registered a board class before ([UI modules in JS](Rewrite-1.1.7#startup-modules)).
Every plugin class is defined by an object of one type, `PluginClass`, which the client looks up by the class's id, as it looks up block classes in the block registry, while R's class vectors stay in R ([State in JS](Rewrite-1#principles)).
What R knows by a plugin's class, the client knows by the members of the class's definition, as the methods of a board option became members of one `Option` ([Board objects](Rewrite-1.1.1#board-options)).
Core, the store or every frontend reads each member, while the board holds each plugin as plain data that names its class, as it holds a block, with illustrative names:

```ts
interface PluginClass {
  id: PluginClassId;                                // "blockr.dag-dag_plugin", as R names it
  options?: OptionId[];                             // the board options it requires
  state?: { schema: JsonSchema; default: Json };    // what each of its plugins keeps in the board, which the store reads, as it reads the next two
  update?(delta: Delta, board: Board, plugin: PluginId): Patch[];   // patches to that plugin's state that follow from a change
  migrate?(state: Json, version: number): Json;     // a plugin's state of an older version, in today's shape
  ui?: ModuleId;                                    // the module that every frontend places, once for each plugin of the class
  frontend?: ModuleId;                              // a frontend's: the module that draws the page, which core reads
  storage?: Storage;                                // a storage plugin's: what every frontend's save and open controls call
  start?({ core, plugin, signal }: { core: CoreApi; plugin: PluginId; signal: AbortSignal }): void | (() => void);   // runs while the open board holds the plugin
}

interface Plugin {                                  // held under its id in board.plugins
  class: PluginClassId;                             // "blockr.md-md_plugin"
  name: string;                                     // "Notes", which titles its panel
  state: Json;                                      // { content: "# Notes" }
}

core.plugins.register({                            // blockr.dag's, from its startup module
  id: "blockr.dag-dag_plugin",
  state: { schema: dagState, default: { positions: {} } },
  update: (delta, board, plugin) => dropPositions(delta.blocks?.rm ?? [], board, plugin),   // a removed block's position goes with it
  ui: "blockr.dag-dag",
});
```

A plugin class sets any mix of these members, or none of `ui`, `frontend` and `storage`, as blockr.viz's control bridge does.
Vite and Rollup take plugins in the same way, as one object whose optional hooks the bundler reads ([Vite](https://vite.dev/guide/api-plugin)), and so does ProseMirror, whose plugin spec holds an optional `state`, `props` and `appendTransaction` ([ProseMirror](https://prosemirror.net/docs/ref/#state.PluginSpec)).
Every other contract of core's client has this shape too, the module contract that follows anywidget's among them ([UI modules in JS](Rewrite-1.1.7#the-contract)).

A package registers the commands and board options of its plugin classes as it registers any others, through `core.commands.register()` and `core.options.register()`, and gives their requests in R ([A plugin's requests](#a-plugins-requests)).
A plugin works on the board through `CoreApi` alone, so the DAG adds a link by running core's command and draws its status badges from `scheduler.status()`, as [Front-ends and extension points](Rewrite-1.1.8#extensions) has it for extensions.

### Plugin classes

In R, core defines two plugin classes beside `plugin`, `frontend_plugin` and `storage_plugin`, since every page relies on what each does (below).
A package's class extends one of them or `plugin` itself, as blockr.session's is `c("session_plugin", "storage_plugin", "plugin")`.
R dispatches on these classes for a plugin's version and its requests.
The board constructor refuses a second frontend or a second storage plugin by them.

In JS, no plugin class extends another, and nothing walks a chain of classes.
A plugin whose class has `frontend` is a frontend, and one whose class has `storage` is a storage plugin.
So the dock has its save and open controls call the storage plugin of the open board, whichever package that plugin comes from.

A frontend places every plugin whose class has a `ui`, once for each plugin, so that two documents of blockr.md get a panel each.
It gives `mountPlugin()` an element of its choosing, such as a panel in the dock or a drawer in core's basic frontend, and core mounts the module there, as `mountBlock()` mounts a block's UI ([Front-ends and extension points](Rewrite-1.1.8#what-core-gives-a-front-end)).
So every plugin with a UI works under every frontend.
A frontend may know a plugin class by its id too, as the dock might know `blockr.dag-dag_plugin` to give the DAG a place of its own, but it needs nothing beyond core's members to place a plugin.
A plugin without a UI module, such as blockr.viz's control bridge, runs from its class's `start` alone, with no place on the screen ([Running a plugin](#running-a-plugin)).

A frontend may offer plugins more places than the one where it mounts their `ui`, such as items in the dock's navbar, through members of its own.
It declares each such member on core's type, which TypeScript's module augmentation lets a package do ([TypeScript](https://www.typescriptlang.org/docs/handbook/declaration-merging.html#module-augmentation)), and reads it from the class of each plugin that runs, while core reads nothing of it:

```ts
declare module "@blockr/core" {                    // in blockr.dock's types
  interface PluginClass {
    dockNavbar?(plugin: PluginId): { id: string; module: ModuleId; side: "left" | "right" }[];   // only the dock reads it
  }
}

const items = Object.keys(core.plugins.running())   // the dock, as it draws its navbar
  .flatMap(id => core.plugins.classOf(id).dockNavbar?.(id) ?? []);

core.plugins.register({                            // blockr.session's, with its avatar in the dock's navbar
  id: "blockr.session-session_plugin",
  ui: "blockr.session-browser",
  storage: { save: saveToConnect, open: pickOnConnect },
  dockNavbar: () => [{ id: "avatar", module: "blockr.session-avatar", side: "right" }],
});
```

Under another frontend, nothing reads `dockNavbar`, and blockr.session works all the same.
The package needs the dock's types only to build, so blockr.dock need not be loaded where it runs.
A package prefixes the members it adds, as `dockNavbar`, so that two packages never pick the same name, and TypeScript reports two declarations of one member with different types where a build sees both.
Such a member follows the open board by itself, since the frontend reads it from the plugins that run, so nothing is registered as a plugin starts or dropped as it stops ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).
Which places the dock offers is [The dock's contribution points](Rewrite-1.2.4)'s to settle.

A plugin's UI module meets the contract of a frontend's module: it exports the JS API major it was built against and a default whose `render({ el, core, plugin, signal })` core calls, here with the element the frontend gave and the id of the plugin it draws, and which returns the cleanup ([Front-ends and extension points](Rewrite-1.1.8#registering-a-front-end)).
So one module draws each plugin of its class, as two documents of blockr.md, each from its own state.
It is free of any framework, as a block's UI is, and may be written in React on the one copy that core ships ([UI modules in JS](Rewrite-1.1.7#react)).
Where [Client-drawn dock and extensions](Rewrite-1.2) has extensions render React components inside the dock's own tree, a plugin's UI renders in a root of its own, which shares no React context with the frontend's and takes its look from blockr.ui's design system ([UI kit and design system for the client](Rewrite-1.7)).

### The frontend

A frontend is a plugin whose class has `frontend`, the module that draws the page, and whose class in R extends `frontend_plugin`.
The module meets the contract of a UI module above, and core calls it with the page's element.
A page has one frontend: the one that the open board holds, or core's basic frontend where it holds none.
Core's basic frontend keeps no state, so no board holds it.
A board that holds no frontend takes the one of the board it replaces as it opens, with the default state of its class ([Which plugins a board has](#which-plugins-a-board-has)), so the dock opens a board made under core's basic frontend with its default layout.
A board holds at most one frontend: the board constructor refuses a second, and the store refuses to open a JSON board that holds two.
Core starts the page as [Front-ends and extension points](Rewrite-1.1.8#starting-the-page) has it, with the board's frontend in place of its class's front-end:

1. Core initializes the startup module of every package that R loaded.
2. Core opens the board, or the one a startup module names in its place.
3. Core imports the module of the board's frontend and calls its `render()`.
4. The scheduler sends nothing to R until `render()` has returned, so what the frontend first shows is evaluated first.
5. Core calls `start` for each plugin of the board whose class has one ([Running a plugin](#running-a-plugin)).

Opening a board that holds another frontend than the page's switches the page in place, as [Front-ends and extension points](Rewrite-1.1.8#switching-front-ends) has it.
A frontend's state holds what it keeps of the board, as the dock's views, their layouts and which view is active, which were the dock board's properties ([The dock board: views and layouts](Rewrite-1.2.1)).
A board that holds the dock, opened in an app that does not load blockr.dock, opens without the dock, whose package the client names, and takes the frontend of the board it replaces ([Which plugins a board has](#which-plugins-a-board-has)).

### Storage

A storage plugin saves boards and opens them through the functions in its class's `storage`, which every frontend's save and open controls call.
With illustrative names:

```ts
interface Storage {
  save(board: string): Promise<void>;        // the JSON board's text, as the store writes it
  open(): Promise<string | null>;            // the text of the board the user picks, or null where they pick none
}
```

Core's own storage plugin saves a board as a download and opens an upload, as today's `preserve_board` does, and has no `ui`, since the frontend draws the controls.
It keeps no state, so no board holds it: it saves and opens for every board that holds no storage plugin.
The storage plugin of blockr.session saves to Connect and opens from it ([Session management as a client extension](Rewrite-1.6)).

A board holds its storage plugin as it holds any other, so that a JSON board describes the whole app, its frontend and its storage among its plugins:

```r
new_board(blocks = blks, plugins = list(new_dock_plugin(), new_session_plugin()))
```

A board holds at most one storage plugin: the board constructor refuses a second, and the store refuses to open a JSON board that holds two.
A board that holds no storage plugin takes the one of the board it replaces as it opens ([Which plugins a board has](#which-plugins-a-board-has)).
Without that, this would go wrong:

1. A user saves a board as a download, in an app without Connect, so the file holds no storage plugin.
2. The user opens the file in a Connect app, through session management.
3. Opening a board runs exactly the plugins that it holds, so the page falls back to core's storage plugin, and session management stops.
4. The user's next save downloads a file instead of saving to Connect.

With the rule, the board takes session management as it opens, and the page keeps saving to Connect.
A board that holds a storage plugin keeps it, whichever storage plugin opened it, since the board describes its app and the page only fills in what the board leaves out.
So a deployment chooses where its pages save through the board its script builds and the packages it loads.

The interface holds only what every frontend's save and open controls call, and it can grow once a frontend needs more of every storage plugin.
A storage plugin offers the rest through its own UI, which every frontend places, as session management offers its board list, its versions and its sharing, and its `open()` may show a picker of its own before it resolves.
A storage plugin keeps no state in the board, since the record a board was opened from is the URL's and the plugin's own, as [Session management as a client extension](Rewrite-1.6) has it.
This settles the open question of [Session management as a client extension](Rewrite-1.6#open-questions) on whether storage becomes an interface of core.

### Which plugins a board has

A board holds its plugins in `plugins`, a property of core's board, each under its id, naming its class by the class's id, with its name and its state ([A plugin's state](#a-plugins-state)).
A plugin's id is its name in the list that the board constructor takes, as a block's id is its name among the blocks.
Where the list gives no name, the id is the class's name without `_plugin`, as `dag`, as today's dock names an extension after its class.
So two plugins of one class need names of their own, as two extensions of one class do today.
A board holds as many plugins of a class as it needs, as two documents of blockr.md, but at most one frontend ([The frontend](#the-frontend)) and one storage plugin ([Storage](#storage)).

Opening a board runs exactly the plugins that it holds and whose packages the app loads, its frontend among them, and stops every plugin that only the board before it held.
So the page is what serving that board in a fresh app would give ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).
The plugins of the board that an app script builds are no different: opening another board stops those that it does not hold.

Opening a board drops every plugin whose class no loaded package registers, as it drops a block whose class the block registry lacks, and names it with the package to install, which its class's id gives ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)).
So no plugin runs on a board that changed while its package was away, and a board saved afterwards is written without it, as condition 4 of [Board objects](Rewrite-1.1.1#what-must-hold) has it for blocks.

Then a board that holds no frontend, or no storage plugin, takes over the one of the board it replaces: a plugin of the same class, under the same id and name, with its class's default state, so that the page keeps drawing and saving as it did:

- A board made in a core app holds no frontend, and opened in a dock app it takes the dock, which lays it out from its default.
- A board saved as a download holds no storage plugin, and opened in a Connect app through session management it takes session management ([Storage](#storage)).
- A board that a startup module names in place of the opening board takes over those of the opening board, so a record that session management opens from a URL as the page starts takes the frontend and the storage plugin of the board that the app script built.
- A dock board opened in an app without blockr.dock loses the dock, which the client names, and takes the frontend of the board it replaces.

Adding a plugin to the open board, or removing one, is an edit through core's commands like any other, so undo takes it back and saving keeps it.
The commands `blockr.core-add_plugin` and `blockr.core-remove_plugin` do it with a patch at the plugin's own path, as `/plugins/dag`.
Adding a plugin gives it its class's id, its id, its name and the default of its class's state, and removing one takes its state with it.
So a board saved before an app offered the assistant takes the assistant up with one command.
Adding a frontend to a board that holds one replaces that frontend, in the same step, and switches the page to the new one in place.

### Running a plugin

Besides the store, which calls a plugin class's `migrate` as a board opens and its `update` with every change, core runs a plugin's code in two places: a frontend mounts its class's `ui` where it places the plugin, and core calls its class's `start`.
Core calls `start` for each plugin of the board once the board has opened and the frontend's `render()` has returned, so that what the frontend first shows is evaluated first.
As the next board opens, or a command removes the plugin, core aborts the plugin's signal and runs the cleanup that `start` returned, as it does for a frontend's `render()` ([Front-ends and extension points](Rewrite-1.1.8#registering-a-front-end)).
Every opening starts the plugins again, so nothing a plugin kept of one board outlives it.
Code that runs with no UI, or longer than a UI stays mounted, runs from `start`, as blockr.viz's control bridge hears what renderers emit and sets block state, and as the assistant's turn goes on once its panel closes:

```ts
start: ({ core, signal }) => {                    // blockr.viz's control bridge
  const stop = core.outputEvents.subscribe(event => forwardSelection(core, event));
  signal.addEventListener("abort", stop);
},
```

A plugin needs no member to stop, since the signal stops it, so core could suspend a plugin one day by aborting its signal and resume it by calling `start` again, with no change to the plugin.

### A plugin's requests

A plugin class that needs R gives its requests through a method of `plugin_requests()` for its class, as blockr.md does to export a document.
One that lives in the browser alone, such as the DAG's, gives R nothing but its constructor, for app scripts, as a block class's UI lives in the browser and its `expr` in R.
Core answers a plugin's requests as a type of request of its own, `plugin`, beside the four types that [blockr.core#484](https://github.com/BristolMyersSquibb/blockr.core/pull/484) built, as it answers a board option's through `board_option_requests()` ([Wire protocol](Rewrite-1.1.9#requests)).
So a package adds no request type for its plugins, and the dock none for its extensions, which that pull request left to it.

Whoever calls `CoreApi.request()` names a plugin of the board by its id, and the message names the plugin's class by the class's id, by which R finds the method.
R calls the request's function with the args that the client passes, by name, with the request's body in `file` where the function takes it, and with the blocks that the request reads in `reads`, by block id, each a list of the block's `result` and its block expression `expr`.
Core has those blocks evaluated first, even off screen, as for a one-time evaluation ([Evaluation in the client](Rewrite-1.1.10#demand)).
A plugin's request may write, so the client never keeps its answer ([Wire protocol](Rewrite-1.1.9#requests)).
It may answer with a file, through `new_reply_body()`, and report how far it has come through `report_progress()`.
On a locked board, R runs it only where its package says that it may run there ([Wire protocol](Rewrite-1.1.9#locked-boards)).

The plugin of blockr.md shows both sides.
Its live document needs no R: its UI renders the markdown in the browser, and mounts the output of each block that `![caption](blockr://a)` embeds with `core.mountOutput()`, as a frontend does on a card.
It demands those blocks while it shows them, as a frontend demands the blocks it shows ([Evaluation in the client](Rewrite-1.1.10#demand)).
Its export is a request, which binds every block's result under the block's id and renders the document in that environment, as today's download hands `filter_md()` every block's result by id ([blockr.md R/md-server.R#L212-L240](https://github.com/BristolMyersSquibb/blockr.md/blob/32e088884d825813fb7ff0afc7d023df9e70a3b6/R/md-server.R#L212-L240)):

```r
plugin_requests.md_plugin <- function(x, ...) {                        # in blockr.md
  list(
    html = function(content, reads) {
      env <- list2env(lapply(reads, `[[`, "result"), parent = globalenv())   # every block's result under its id
      src <- tempfile(fileext = ".Rmd")
      writeLines(content, src)
      new_reply_body(rmarkdown::render(src, envir = env, quiet = TRUE), "text/html", name = "report.html")
    }
  )
}
```

```ts
const file = await core.request("report", "html", { content },        // the board's plugin "report"
  { reads: Object.keys(core.store.board().blocks), progress: show });   // every block, since a chunk may name any
```

### A plugin's state

A plugin's state takes the place of a board class's properties, with the same machinery under the plugin's id ([Board updates](Rewrite-1.1.2#board-classes-and-attributes)):

- A change inside it is a patch at a path under the plugin's state, as `/plugins/dag/state/positions/a`.
- The store checks the state against its class's schema after every change, keeps the inverse patches for undo, and saves the state with the board.
- The store calls a class's `update` once for each of its plugins, with every change it applies, in the same step, and refuses a patch that an `update` returns outside the state of the plugin it was called for ([Board updates](Rewrite-1.1.2#applying-a-delta)).
- The commands of a plugin's class change its state, naming the plugin by its id, and everything else changes it through them, which is external control ([Board updates](Rewrite-1.1.2#commands)).
- A JSON board records in `versions` the version of each class whose plugins it holds, by the class's id, and the class's package in `packages`, and the class's `migrate` takes the state of each of its plugins at an older version ([Serialization](Rewrite-1.1.4#migrations)).

Each plugin class gives the state of its plugins a shape of its own, so the dock's views and the layout of another frontend share nothing.
What a plugin keeps about one of core's objects is an entry in its state keyed by the object's id, as the DAG keeps a block's position, in place of the properties that a board class adds to blocks ([Locked boards and the properties of blocks](Rewrite-1.1.11)).

A board with the dock, the DAG and two documents of blockr.md, with illustrative states:

```json
{
  "format": 1,
  "packages": { "blockr.core": "0.2.0", "blockr.dock": "0.2.1", "blockr.dag": "0.2.0", "blockr.md": "0.2.0" },
  "board": {
    "id": "curious_otter",
    "versions": { "blockr.dock-dock_plugin": 2, "blockr.dag-dag_plugin": 1, "blockr.md-md_plugin": 1 },
    "name": "Sales review",
    "blocks": {
      "a": { "registry_id": "blockr.core-dataset_block", "version": 1, "state": { "dataset": "iris", "package": "datasets" }, "name": "Iris" }
    },
    "links": {},
    "stacks": {},
    "options": {},
    "plugins": {
      "dock": { "class": "blockr.dock-dock_plugin", "name": "Dock", "state": { "views": { "main": { "name": "Main", "grid": ["a", "notes"] } }, "active": "main" } },
      "dag": { "class": "blockr.dag-dag_plugin", "name": "DAG", "state": { "positions": { "a": { "x": 120, "y": 80 } } } },
      "notes": { "class": "blockr.md-md_plugin", "name": "Notes", "state": { "content": "# Notes" } },
      "report": { "class": "blockr.md-md_plugin", "name": "Report", "state": { "content": "# Report\n\n![Iris](blockr://a)" } }
    }
  }
}
```

### What a frontend offers other plugins

Part of what [The dock's services](Rewrite-1.2.6) gives the dock's extensions, every frontend gives every plugin through `CoreApi`, so a plugin that uses it works under any frontend:

- Notifications, which the frontend draws, as it draws what the store refused and what R dropped when a board opened ([Front-ends and extension points](Rewrite-1.1.8#cores-basic-front-end)).
- Which block has focus, which the frontend sets and the assistant reads to tell which block the user is looking at ([Assistant as a client extension](Rewrite-1.4)).
  Core holds it for the page, outside the board, since only one person's screen needs it ([Board objects](Rewrite-1.1.1#extending-cores-objects)).

With illustrative names:

```ts
interface CoreApi {
  // as Front-ends and extension points has it, plus:
  plugins: {
    register(def: PluginClass): () => void;            // a plugin class, from its package's startup module
    running(): Record<PluginId, Plugin>;               // the open board's plugins whose classes are registered
    classOf(plugin: PluginId): PluginClass;            // the definition of a running plugin's class
  };
  mountPlugin(el: HTMLElement, plugin: PluginId): () => void;                               // the plugin's UI module, until the cleanup runs
  request<T = Json>(plugin: PluginId, name: string, args?: Json, opts?: RequestOpts): Promise<T | Blob>;   // a plugin's request, in place of an extension's
  notifications: { notify(note: Note): void; subscribe(fn: (note: Note) => void): () => void };   // a plugin notifies, and the frontend hears and draws each note
  focus: { get(): BlockId | null; set(block: BlockId | null): void; subscribe(fn: (block: BlockId | null) => void): () => void };
}

interface Note {
  message: string;
  severity: "message" | "warning" | "error";
}
```

### What goes

- Board classes: the board class that `core.store.register()` takes today, a board's `class` and its `versions` by class, the R generics `board_front_end()` and `board_version()`, and the rule that the client builds a board as the first class in its `class` that a loaded package defines ([Board objects](Rewrite-1.1.1#the-board)).
- The dock board as a class, `dock_board`, with its `extensions`, whose entries become plugins of their own.
- Core's nine plugin classes and `known_plugins()`, of which only storage keeps a class in core.
- The `plugins` argument of `serve()`, with `custom_plugins()` and `blockr_app_plugins()`, since a board holds all its plugins.
- Registering a front-end through its board class ([Front-ends and extension points](Rewrite-1.1.8#registering-a-front-end)), which the frontend plugin replaces, while what core gives a frontend, starting the page, switching frontends, core's basic frontend and renderers stay on that page.

On `js-state`, the board classes of [blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474) become plugin state: the patches, the schema checks, `update` and `migrate` keep their code, with each state under its plugin's id and each definition under its plugin class's id, rather than under a board class.

### Boards and app scripts from today

- The conversion outside core ([Serialization](Rewrite-1.1.4#files)) turns a dock board into a board that holds the dock plugin, whose state takes the dock board's `views` and `grids`, and one plugin for each extension, under the key the board gave the extension and with the extension's name, whose state takes the extension's, each class at version 1.
  So a board with two documents of blockr.md keeps both.
- An app script's `new_dock_board()` keeps working, as a board that holds the dock plugin and the plugins its `extensions` give, which [Saved boards and app scripts across the switch](Rewrite-1.2.2) settles in detail.
- An app script that sets storage through `serve(plugins = custom_plugins(manage_project()))` puts blockr.session's storage plugin on its board instead.
- An app script that sets code export through `serve(plugins = custom_plugins(generate_flat_code()))`, as blockr.code's README does ([blockr.code README.Rmd#L43-L56](https://github.com/BristolMyersSquibb/blockr.code/blob/72b20d6911496e4edc9ee64db758e70ebf3f50ca/README.Rmd#L43-L56)), puts blockr.code's plugin on its board instead.

### Testing

The `CoreApi` for tests that core ships ([Front-ends and extension points](Rewrite-1.1.8#testing)) runs a plugin on a board in a test runner, its `update` and `migrate` included, so testing a plugin, a frontend among them, needs neither R nor a browser.

## Open questions

None.

<details><summary>Notes for implementers</summary>

The board classes to replace on `js-state`, at `3536c4d`: the board class and its registration in `srcts/store/registrations.ts`, the board's `class` in `srcts/types/board.ts`, building a board as a class in `srcts/store/store.ts`, the classes in the reply to `hello` in `srcts/protocol/messages.ts` and `R/loaded-reply.R`, `board_front_end()` and `board_version()` in `R/board-class.R`, the modules of front-ends in `R/pkg-modules.R`, and a board's `class` and `versions` in `R/utils-serdes.R`.

A plugin's request carries the type `plugin` and the id of the plugin's class, beside the fields that every request has ([blockr.core#484](https://github.com/BristolMyersSquibb/blockr.core/pull/484)):

```json
{ "id": "40", "kind": "request", "type": "plugin", "plugin": "blockr.md-md_plugin", "name": "html",
  "args": { "content": "# Report" }, "reads": [ { "block": "a", "revision": 2 } ] }
```

R reads it into an object of class `plugin_request`, and its method of `request_call()` dispatches `plugin_requests()` on an object of class `c("md_plugin", "plugin")`, which it makes from the class's id, as the method for board options makes one with `new_board_option()`, and binds the args with `request_call_args()`, as that method does, with `reads` and `file` reserved.

Once this page settles, the change reaches the root page, which says that core keeps no plugin or extension type of its own, [Client-owned board state](Rewrite-1.1), the settled [Board objects](Rewrite-1.1.1), [Board updates](Rewrite-1.1.2), [Defining a board in R](Rewrite-1.1.3), [Serialization](Rewrite-1.1.4), [UI modules in JS](Rewrite-1.1.7), [Front-ends and extension points](Rewrite-1.1.8) and [Wire protocol](Rewrite-1.1.9), the draft [Locked boards and the properties of blocks](Rewrite-1.1.11), the [Glossary](Glossary), and Rewrite 1.2 to 1.6, whose extensions become plugins.
The same change writes "frontend" for "front-end" and "plugin" for "extension" on every page, but in the names of today's code, such as `new_dock_extension()`.
The issues that restate what changes are [blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434), [blockr.core#436](https://github.com/BristolMyersSquibb/blockr.core/issues/436), [blockr.core#440](https://github.com/BristolMyersSquibb/blockr.core/issues/440), [blockr.core#441](https://github.com/BristolMyersSquibb/blockr.core/issues/441), [blockr.core#442](https://github.com/BristolMyersSquibb/blockr.core/issues/442), [blockr.core#443](https://github.com/BristolMyersSquibb/blockr.core/issues/443), [blockr.core#445](https://github.com/BristolMyersSquibb/blockr.core/issues/445) and [blockr.core#487](https://github.com/BristolMyersSquibb/blockr.core/issues/487), and [blockr.code#8](https://github.com/BristolMyersSquibb/blockr.code/issues/8), which recasts the code export as a dock extension.

</details>
