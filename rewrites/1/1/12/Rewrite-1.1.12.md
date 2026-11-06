# Plugins for the client-owned board
Status: draft. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): what a plugin is in R and in JS, the plugin classes core defines in R, the frontend and storage plugins, which plugins a board has, and a plugin's state.
Plugins are core's second way to extend a board, beside block classes, and take the place of three mechanisms: core's plugins of today, the dock's extensions, and the board classes of [Board objects](Rewrite-1.1.1#the-board) and [Board updates](Rewrite-1.1.2#board-classes-and-attributes).
It changes what [Front-ends and extension points](Rewrite-1.1.8) says about registering a frontend and about extensions, and shapes `CoreApi` and starting the page ([blockr.core#440](https://github.com/BristolMyersSquibb/blockr.core/issues/440)), core's basic frontend ([blockr.core#441](https://github.com/BristolMyersSquibb/blockr.core/issues/441)), serving a board ([blockr.core#442](https://github.com/BristolMyersSquibb/blockr.core/issues/442)) and saving boards in the client ([blockr.core#436](https://github.com/BristolMyersSquibb/blockr.core/issues/436)), while no issue asks for plugins yet.
What core gives a frontend, starting the page and renderers stay with [Front-ends and extension points](Rewrite-1.1.8), and what the dock plugin keeps in its state and where it places other plugins stay with [Client-drawn dock and extensions](Rewrite-1.2).

## What must hold

1. Core has two ways to extend a board, block classes and plugins, and no other, so a board has no class of its own.
2. A plugin works under every frontend: it works on the board through `CoreApi`, keeps its state in the board, and offers its UI as a module that core mounts where the frontend puts it.
3. The frontend is a plugin, and every frontend places every plugin that has a UI, including one from a package it does not know.
4. A board names its plugins, all but the storage plugin (condition 5), and opening a board runs exactly those whose packages the app loads.
   So the page is what serving that board in a fresh app would give, whatever was open before, as condition 6 of [Board updates](Rewrite-1.1.2#what-must-hold) asks.
5. Where a page saves boards and opens them from is the app's choice, whichever board is open.
6. A plugin's state belongs to that plugin alone, keyed by its id: it is saved, undone and migrated with the board, and its shape is the plugin's own, so that the states of two frontends share nothing.
7. Boards saved by today's blockr.dock open with their views, their layouts and the state of their extensions, as condition 4 of [State in JS](Rewrite-1#what-must-hold) asks.

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
Its args are the state it gives the board an app script builds, such as the DAG's `positions`, as a block's args are its state.
Its id is `{pkg}-{name}_plugin`, as `blockr.dag-dag_plugin`.
The id joins the class to its package, the one its constructor lives in, as a registry id carries its package ([Board objects](Rewrite-1.1.1#registry-ids)).
The version of its state's shape is what its method of `plugin_version()` returns, 1 where it has none, in place of `board_version()`.
The board constructor takes the board's plugins in `plugins`, as `new_dock_board(extensions = ...)` takes extensions today:

```r
new_board(
  blocks = blks,
  plugins = list(new_dock_plugin(), new_dag_plugin(positions = pos), new_assistant_plugin())
)
```

R writes each plugin into the opening board under its id, with its state and its version ([Serialization](Rewrite-1.1.4#files)).
In the reply to `hello`, R sends the versions that loaded packages give their plugin classes, by plugin id, in `plugin_versions`, where a class without a method of `plugin_version()` is at version 1, as `option_versions` has it for board options ([Wire protocol](Rewrite-1.1.9#handshake)).
The client takes a plugin's package from its id, and where its UI module is served from the modules that packages offer each other, so R keeps no list of plugin classes.

In JS, the package's startup module registers each plugin under its id, where it registered a board class before ([UI modules in JS](Rewrite-1.1.7#startup-modules)).
Every plugin is an object of one type, `Plugin`, since R's classes stay in R ([State in JS](Rewrite-1#principles)).
What R knows by a plugin's class, the client knows by the plugin's members, as the methods of a board option became members of one `Option` ([Board objects](Rewrite-1.1.1#board-options)).
Core, the store or every frontend reads each member, with illustrative names:

```ts
interface Plugin {
  id: PluginId;                                     // "blockr.dag-dag_plugin", as R names it
  options?: OptionId[];                             // the board options it requires
  state?: { schema: JsonSchema; default: Json };    // what it keeps in the board, which the store reads, as it reads the next two
  update?(delta: Delta, board: Board): Patch[];     // patches to its own state that follow from a change
  migrate?(state: Json, version: number): Json;     // its state of an older version, in today's shape
  ui?: ModuleId;                                    // the module that every frontend places
  frontend?: ModuleId;                              // a frontend's: the module that draws the page, which core reads
  storage?: Storage;                                // a storage plugin's: what every frontend's save and open controls call
}

core.plugins.register({                            // blockr.dag's, from its startup module
  id: "blockr.dag-dag_plugin",
  state: { schema: dagState, default: { positions: {} } },
  update: (delta, board) => dropPositions(delta.blocks?.rm ?? [], board),   // a removed block's position goes with it
  ui: "blockr.dag-dag",
});
```

A plugin sets any mix of these members, or none of `ui`, `frontend` and `storage`, as blockr.viz's control bridge does.
Vite and Rollup take plugins in the same way, as one object whose optional hooks the bundler reads ([Vite](https://vite.dev/guide/api-plugin)), and so does ProseMirror, whose plugin spec holds an optional `state`, `props` and `appendTransaction` ([ProseMirror](https://prosemirror.net/docs/ref/#state.PluginSpec)).
Every other contract of core's client has this shape too, the module contract that follows anywidget's among them ([UI modules in JS](Rewrite-1.1.7#the-contract)).

A plugin registers its commands, board options and request types as any package does: commands through `core.commands.register()`, board options through `core.options.register()`, and request types in R through methods of `request_call()`, as [blockr.core#484](https://github.com/BristolMyersSquibb/blockr.core/pull/484) built them in place of the `register_requests()` of [Front-ends and extension points](Rewrite-1.1.8#what-a-package-declares-in-r) ([Wire protocol](Rewrite-1.1.9#requests)).
It works on the board through `CoreApi` alone, so the DAG adds a link by running core's command and draws its status badges from `scheduler.status()`, as [Front-ends and extension points](Rewrite-1.1.8#extensions) has it for extensions.

### Plugin classes

In R, core defines two plugin classes beside `plugin`, `frontend_plugin` and `storage_plugin`, since every page relies on what each does (below).
A package's class extends one of them or `plugin` itself, as blockr.session's is `c("session_plugin", "storage_plugin", "plugin")`.
R dispatches on these classes for a plugin's version and its requests.
The board constructor refuses a second frontend by them, and `serve()` refuses a `storage` that is no storage plugin.

In JS, no plugin has a class, and no plugin extends another.
A plugin with `frontend` is a frontend, and a plugin with `storage` is a storage plugin.
So the dock has its save and open controls call the page's storage plugin, whichever package that plugin comes from.

A frontend places every plugin that has a `ui`.
It gives `mountPlugin()` an element of its choosing, such as a panel in the dock or a drawer in core's basic frontend, and core mounts the module there, as `mountBlock()` mounts a block's UI ([Front-ends and extension points](Rewrite-1.1.8#what-core-gives-a-front-end)).
So every plugin with a UI works under every frontend.
A frontend may know a plugin by its id too, as the dock might know `blockr.dag-dag_plugin` to give the DAG a place of its own, but it needs nothing beyond core's members to place a plugin.
A plugin without a UI module, such as blockr.viz's control bridge, runs with no place on the screen.

A frontend may offer plugins more places than the one where it mounts their `ui`, such as items in the dock's navbar, through members of its own.
It declares each such member on core's type, which TypeScript's module augmentation lets a package do ([TypeScript](https://www.typescriptlang.org/docs/handbook/declaration-merging.html#module-augmentation)), and reads it from the plugins that run, while core reads nothing of it:

```ts
declare module "@blockr/core" {                    // in blockr.dock's types
  interface Plugin {
    dockNavbar?: { id: string; module: ModuleId; side: "left" | "right" }[];   // only the dock reads it
  }
}

const items = core.plugins.running().flatMap(p => p.dockNavbar ?? []);   // the dock, as it draws its navbar

core.plugins.register({                            // blockr.session's, with its avatar in the dock's navbar
  id: "blockr.session-session_plugin",
  ui: "blockr.session-browser",
  storage: { save: saveToConnect, open: pickOnConnect },
  dockNavbar: [{ id: "avatar", module: "blockr.session-avatar", side: "right" }],
});
```

Under another frontend, nothing reads `dockNavbar`, and blockr.session works all the same.
The package needs the dock's types only to build, so blockr.dock need not be loaded where it runs.
A package prefixes the members it adds, as `dockNavbar`, so that two packages never pick the same name, and TypeScript reports two declarations of one member with different types where a build sees both.
Such a member follows the open board by itself, since the frontend reads it from the plugins that run, so nothing is registered as a plugin starts or dropped as it stops ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).
Which places the dock offers is [The dock's contribution points](Rewrite-1.2.4)'s to settle.

A plugin's UI module meets the contract of a frontend's module: it exports the JS API major it was built against and a default whose `render({ el, core, signal })` core calls, here with the element the frontend gave, and which returns the cleanup ([Front-ends and extension points](Rewrite-1.1.8#registering-a-front-end)).
It is free of any framework, as a block's UI is, and may be written in React on the one copy that core ships ([UI modules in JS](Rewrite-1.1.7#react)).
Where [Client-drawn dock and extensions](Rewrite-1.2) has extensions render React components inside the dock's own tree, a plugin's UI renders in a root of its own, which shares no React context with the frontend's and takes its look from blockr.ui's design system ([UI kit and design system for the client](Rewrite-1.7)).

### The frontend

A frontend is a plugin with `frontend`, of class `frontend_plugin` in R, whose module draws the page, with the contract of the module above, called with the page's element.
A page has one frontend: the one that the open board names, where its package is loaded, and core's basic frontend otherwise.
A board names at most one frontend: the board constructor refuses a second, and the store refuses to open a JSON board that names two.
Core starts the page as [Front-ends and extension points](Rewrite-1.1.8#starting-the-page) has it, with the board's frontend in place of its class's front-end:

1. Core initializes the startup module of every package that R loaded.
2. Core opens the board, or the one a startup module names in its place.
3. Core imports the module of the board's frontend and calls its `render()`.
4. The scheduler sends nothing to R until `render()` has returned, so what the frontend first shows is evaluated first.

Opening a board that names another frontend than the page's switches the page in place, as [Front-ends and extension points](Rewrite-1.1.8#switching-front-ends) has it.
A frontend's state holds what it keeps of the board, as the dock's views, their layouts and which view is active, which were the dock board's properties ([The dock board: views and layouts](Rewrite-1.2.1)).
So a board that core's basic frontend draws, in an app that does not load blockr.dock, keeps the dock's state unchanged, and the dock draws it as it left it once the board opens in a dock app again.

### Storage

A storage plugin saves boards and opens them through the functions in its `storage`, which every frontend's save and open controls call.
With illustrative names:

```ts
interface Storage {
  save(board: string): Promise<void>;        // the JSON board's text, as the store writes it
  open(): Promise<string | null>;            // the text of the board the user picks, or null where they pick none
}
```

Core's own storage plugin saves a board as a download and opens an upload, as today's `preserve_board` does, and has no `ui`, since the frontend draws the controls.
The storage plugin of blockr.session saves to Connect and opens from it ([Session management as a client extension](Rewrite-1.6)), and shows its board list and versions through a UI module of its own.

The app sets its storage plugin, not the board, since where a page saves boards belongs to the deployment rather than to a board:

```r
serve(board, storage = new_session_plugin())
```

A board names no storage plugin, so opening a board never changes where the page saves.
Were storage among the plugins that a board names, this would go wrong:

1. A user saves a board as a download, in an app without Connect.
2. The user uploads it into a Connect app, through session management.
3. The board names no session management, so session management stops, in the middle of its own upload.

A storage plugin keeps no state in the board, since the record a board was opened from is the URL's and the plugin's own, as [Session management as a client extension](Rewrite-1.6) has it.
This settles the open question of [Session management as a client extension](Rewrite-1.6#open-questions) on whether storage becomes an interface of core.

### Which plugins a board has

A board holds its plugins in `plugins`, a property of core's board, keyed by plugin id, each with its state ([A plugin's state](#a-plugins-state)).
Opening a board runs exactly the plugins that it holds and whose packages the app loads, its frontend among them, and stops every plugin that only the board before it held.
So the page is what serving that board in a fresh app would give ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).
The plugins of the board that an app script builds are no different: opening another board stops those that it does not name.
Storage is the one exception, which the app sets for the page ([Storage](#storage)).

A plugin whose package the app does not load stays in the board with its state unchanged, so that it runs again in an app that loads the package.
The client names the package to install, as it names the package of a block it drops ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)).
The plugin's `update` does not run meanwhile, so its state may refer to blocks that the board no longer has, and the plugin drops such entries when it next runs.

Adding a plugin to the open board, or removing one, is an edit through core's commands like any other, so undo takes it back and saving keeps it.
The commands `blockr.core-add_plugin` and `blockr.core-remove_plugin` do it with a patch at the plugin's own path, as `/plugins/blockr.dag-dag_plugin`, which adds the plugin with the default of its state or removes it with its state.
So a board saved before an app offered the assistant takes the assistant up with one command.
Adding a frontend to a board that names one replaces that frontend, in the same step, and switches the page to the new one in place.

### A plugin's state

A plugin's state takes the place of a board class's properties, with the same machinery under the plugin's id ([Board updates](Rewrite-1.1.2#board-classes-and-attributes)):

- A change inside it is a patch at a path under the plugin's id, as `/plugins/blockr.dag-dag_plugin/positions/a`.
- The store checks the state against its schema after every change, keeps the inverse patches for undo, and saves the state with the board.
- The store calls each plugin's `update` with every change it applies, in the same step, and refuses a patch that an `update` returns outside its own plugin's state ([Board updates](Rewrite-1.1.2#applying-a-delta)).
- The plugin's commands change its state, and everything else changes it through them, which is external control ([Board updates](Rewrite-1.1.2#commands)).
- A JSON board records the version of each plugin's state in `versions`, by plugin id, and the plugin's package in `packages`, and the plugin's `migrate` takes a state of an older version ([Serialization](Rewrite-1.1.4#migrations)).

Each plugin's state has a shape of its own, so the dock's views and the layout of another frontend share nothing.
What a plugin keeps about one of core's objects is an entry in its state keyed by the object's id, as the DAG keeps a block's position, in place of the properties that a board class adds to blocks ([Locked boards and the properties of blocks](Rewrite-1.1.11)).

A board with the dock and the DAG, with illustrative states:

```json
{
  "format": 1,
  "packages": { "blockr.core": "0.2.0", "blockr.dock": "0.2.1", "blockr.dag": "0.2.0" },
  "board": {
    "id": "curious_otter",
    "versions": { "blockr.dock-dock_plugin": 2, "blockr.dag-dag_plugin": 1 },
    "name": "Sales review",
    "blocks": {
      "a": { "registry_id": "blockr.core-dataset_block", "version": 1, "state": { "dataset": "iris", "package": "datasets" }, "name": "Iris" }
    },
    "links": {},
    "stacks": {},
    "options": {},
    "plugins": {
      "blockr.dock-dock_plugin": { "views": { "main": { "name": "Main", "grid": ["a"] } }, "active": "main" },
      "blockr.dag-dag_plugin": { "positions": { "a": { "x": 120, "y": 80 } } }
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
  plugins: { register(plugin: Plugin): () => void; running(): Plugin[] };                 // running(): the open board's plugins whose packages are loaded, and the page's storage plugin
  mountPlugin(el: HTMLElement, plugin: PluginId): () => void;                               // the plugin's UI module, until the cleanup runs
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
- Registering a front-end through its board class ([Front-ends and extension points](Rewrite-1.1.8#registering-a-front-end)), which the frontend plugin replaces, while what core gives a frontend, starting the page, switching frontends, core's basic frontend and renderers stay on that page.

On `js-state`, the board classes of [blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474) become plugin state: the patches, the schema checks, `update` and `migrate` keep their code, keyed by plugin id rather than by class.

### Boards and app scripts from today

- The conversion outside core ([Serialization](Rewrite-1.1.4#files)) turns a dock board into a board that names the dock plugin, whose state takes the dock board's `views` and `grids`, and one plugin for each extension, whose state takes the extension's, each at version 1.
- An app script's `new_dock_board()` keeps working, as a board that names the dock plugin and the plugins its `extensions` give, which [Saved boards and app scripts across the switch](Rewrite-1.2.2) settles in detail.
- An app script that sets storage through `serve(plugins = custom_plugins(manage_project()))` sets it through `serve(storage = ...)`.
- An app script that sets code export through `serve(plugins = custom_plugins(generate_flat_code()))`, as blockr.code's README does ([blockr.code README.Rmd#L43-L56](https://github.com/BristolMyersSquibb/blockr.code/blob/72b20d6911496e4edc9ee64db758e70ebf3f50ca/README.Rmd#L43-L56)), names blockr.code's plugin on its board instead.

### Testing

The `CoreApi` for tests that core ships ([Front-ends and extension points](Rewrite-1.1.8#testing)) runs a plugin on a board in a test runner, its `update` and `migrate` included, so testing a plugin, a frontend among them, needs neither R nor a browser.

## Open questions

- Whether a board can hold two plugins of one class, as two documents of blockr.md, which needs an id for each plugin beside its class, as today's dock keys extensions by name ([Registering extensions with the dock](Rewrite-1.2.3#open-questions)).
  It blocks the shape of `plugins`.
- What a storage plugin's interface holds beyond saving and opening, such as listing boards, which session management needs ([Session management as a client extension](Rewrite-1.6)).
  It blocks rebuilding session management.
- Whether the assistant, which needs the deployment's credentials, is set by the app as storage is, rather than named by the board.
  It blocks [Assistant as a client extension](Rewrite-1.4).

<details><summary>Notes for implementers</summary>

The board classes to replace on `js-state`, at `3536c4d`: the board class and its registration in `srcts/store/registrations.ts`, the board's `class` in `srcts/types/board.ts`, building a board as a class in `srcts/store/store.ts`, the classes in the reply to `hello` in `srcts/protocol/messages.ts` and `R/loaded-reply.R`, `board_front_end()` and `board_version()` in `R/board-class.R`, the modules of front-ends in `R/pkg-modules.R`, and a board's `class` and `versions` in `R/utils-serdes.R`.

Once this page settles, the change reaches the root page, which says that core keeps no plugin or extension type of its own, [Client-owned board state](Rewrite-1.1), the settled [Board objects](Rewrite-1.1.1), [Board updates](Rewrite-1.1.2), [Defining a board in R](Rewrite-1.1.3), [Serialization](Rewrite-1.1.4) and [Front-ends and extension points](Rewrite-1.1.8), the draft [Locked boards and the properties of blocks](Rewrite-1.1.11), the [Glossary](Glossary), and Rewrite 1.2 to 1.6, whose extensions become plugins.
The same change writes "frontend" for "front-end" and "plugin" for "extension" on every page, but in the names of today's code, such as `new_dock_extension()`.
The issues that restate what changes are [blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434), [blockr.core#436](https://github.com/BristolMyersSquibb/blockr.core/issues/436), [blockr.core#440](https://github.com/BristolMyersSquibb/blockr.core/issues/440), [blockr.core#441](https://github.com/BristolMyersSquibb/blockr.core/issues/441), [blockr.core#442](https://github.com/BristolMyersSquibb/blockr.core/issues/442), [blockr.core#443](https://github.com/BristolMyersSquibb/blockr.core/issues/443), [blockr.core#445](https://github.com/BristolMyersSquibb/blockr.core/issues/445) and [blockr.core#487](https://github.com/BristolMyersSquibb/blockr.core/issues/487), and [blockr.code#8](https://github.com/BristolMyersSquibb/blockr.code/issues/8), which recasts the code export as a dock extension.

</details>
