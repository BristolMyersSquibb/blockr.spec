# Plugins for the client-owned board
Status: settled on 2026-11-08. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): what a plugin is in R and in JS, the plugin classes core defines in R, the frontend and storage plugins, which plugins a board has, how a plugin runs, and a plugin's state.
Plugins are core's second way to extend a board, beside block classes, and take the place of three mechanisms: core's plugins of today, the dock's extensions, and the board classes that [blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474) built on `js-state`.
It changes what [blockr.core#494](https://github.com/BristolMyersSquibb/blockr.core/pull/494) built of `CoreApi` and starting the page, and core's basic frontend as [blockr.core#441](https://github.com/BristolMyersSquibb/blockr.core/issues/441) built it, and shapes the plugins that [blockr.core#504](https://github.com/BristolMyersSquibb/blockr.core/issues/504), [blockr.core#505](https://github.com/BristolMyersSquibb/blockr.core/issues/505), [blockr.core#506](https://github.com/BristolMyersSquibb/blockr.core/issues/506) and [blockr.core#507](https://github.com/BristolMyersSquibb/blockr.core/issues/507) build, serving a board ([blockr.core#442](https://github.com/BristolMyersSquibb/blockr.core/issues/442)), taking the app's plugins in `serve()` ([blockr.core#558](https://github.com/BristolMyersSquibb/blockr.core/issues/558)) and the migration notes for app scripts ([blockr.core#445](https://github.com/BristolMyersSquibb/blockr.core/issues/445)).
What core gives plugins through `CoreApi`, starting the page, opening a board, core's basic frontend and renderers are [Drawing the board](Rewrite-1.1.8)'s, and what the dock plugin keeps in its state and where it places other plugins stay with [Client-drawn dock](Rewrite-1.2).

## What must hold

1. Core has two ways to extend a board, block classes and plugins, and no other, so a board has no class of its own.
2. A plugin works under every frontend: it works on the board through `CoreApi`, keeps its state in the board, and offers its UI as a module that core mounts where the frontend puts it.
3. The frontend is a plugin, and every frontend places every plugin that has a UI, including one from a package it does not know.
4. The app's plugins, which `serve()` takes in `plugins`, every plugin of the available packages by default, are the plugins that run on every board that the app opens, the opening board among them, its frontend and its storage plugin included, each identified by its class's id and named by its class: a board keeps the state of each plugin of the app, under its class's id, and drops the state of every other plugin, naming the package of each, as it drops a block ([Board objects](Rewrite-1.1.1#what-must-hold)).
   So the page is what opening that board in a fresh app would give, whatever was open before, as condition 6 of [Board updates](Rewrite-1.1.2#what-must-hold) asks.
   A board gives only the state of its plugins, whether a script builds it or a file holds it, and a JSON board holds that of every plugin that ran on the page that saved it and keeps any, so that no board names a plugin that keeps nothing, such as core's basic frontend.
5. A plugin of the app whose state a board does not hold starts with its class's default state, and no plugin runs that the app does not hold, core's basic frontend and core's own storage plugin included, so that which plugins run, what draws the page and where it saves depend on the app alone, never on the board or on what was open before.
   So a plugin of the app reaches every board that the app opens, saved ones and a file given to `serve()` included, as a plugin that `serve()` takes reaches every board it serves today, and a file never changes the frontend or the storage plugin.
6. A plugin's state belongs to that plugin alone, keyed by its class's id: it is saved, undone and migrated with the board, and its shape is its class's own, so that the states of two frontends share nothing.
7. Boards saved by today's blockr.dock open with their views, their grids and the state of their extensions, as condition 4 of [State in JS](Rewrite-1#what-must-hold) asks.
8. An app runs at most one plugin of each class, one frontend and at most one storage plugin among them, and what a plugin keeps several of, such as blockr.md's documents or what a user adds more of while the app runs, lives in that plugin's state, as the dock's views do.
9. On a board that is not locked, every plugin, the assistant among them, can change another plugin's state as it can change a block's, whether or not the other's class registers a command for it, and the other plugin's UI shows the change at once, as a block's UI does.
10. Every frontend draws the controls of the app's storage plugin with its own components, whichever package gives that plugin, so that every storage plugin works under every frontend and looks like the rest of it.

## Today

Three mechanisms extend a board, two on main and one on `js-state`:

- **Core's plugins** are Shiny module pairs that `new_plugin(server, ui, validator, class)` makes, each of exactly one of the nine classes that `known_plugins()` lists, with its class as its id ([R/board-plugins.R#L38-L75](https://github.com/BristolMyersSquibb/blockr.core/blob/460afef170ed67ec926a75ed66021bc98ce61647/R/board-plugins.R#L38-L75)).
  The app sets them: `serve()` takes `plugins` as a function, which gives every board the app serves its plugins, restored boards included, and no file holds them ([R/utils-serve.R#L120-L160](https://github.com/BristolMyersSquibb/blockr.core/blob/460afef170ed67ec926a75ed66021bc98ce61647/R/utils-serve.R#L120-L160)).
  So an app swaps blockr.session's storage in for core's with `serve(plugins = custom_plugins(manage_project()))` ([README.Rmd#L38-L47](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/README.Rmd#L38-L47)).
- **The dock's extensions** are Shiny module pairs that `new_dock_extension()` makes, which `new_dock_board(extensions = ...)` puts on the board.
  The board sets them: saving writes each with its constructor, the constructor's package and its state, and restoring calls each constructor that the file names, loading its package where it is installed ([blockr.dock R/utils-serdes.R#L78-L185](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/utils-serdes.R#L78-L185), [R/utils-serdes.R#L518-L539](https://github.com/BristolMyersSquibb/blockr.core/blob/460afef170ed67ec926a75ed66021bc98ce61647/R/utils-serdes.R#L518-L539)).
- **Board classes**, on `js-state`, are defined in JS with the properties they add, each with a schema and a default, and with an `update` and a `migrate` for them, while R names each class's frontend and version through `board_front_end()` and `board_version()` ([blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474), [srcts/store/registrations.ts](https://github.com/BristolMyersSquibb/blockr.core/blob/3536c4dad52b09bb6f9adb220d4981b1350276b9/srcts/store/registrations.ts)).
  The dock board adds its views and grids as properties, and keeps the state of its extensions in its `extensions`.

| Today | Where it goes |
|---|---|
| `preserve_board`, with core's Import and Export | Core's storage plugin, which saves a board as a download and opens an upload, and which an app runs unless another available package gives a storage plugin ([Storage](#storage)) |
| `manage_project()` of blockr.session | Its storage plugin ([Session management as a storage plugin](Rewrite-1.6)) |
| `generate_code`, core's and blockr.code's `generate_flat_code()` ([blockr.code R/plugin.R#L31-L35](https://github.com/BristolMyersSquibb/blockr.code/blob/72b20d6911496e4edc9ee64db758e70ebf3f50ca/R/plugin.R#L31-L35)) | The plugin of blockr.code ([Code export as a plugin](Rewrite-1.5)) |
| `manage_blocks`, `manage_links`, `manage_stacks` and `edit_stack`, with the dock's Edit board extension | Core's Edit board plugin, which runs core's commands under every frontend and which `serve()` gives an app by default ([The Edit board plugin](Rewrite-1.1.15)) |
| `edit_block`, `notify_user` and `ctrl_block` | Where the notes of [Client-drawn dock](Rewrite-1.2) put them: core's commands, with the menus, cards and notifications of the frontend and the DAG |
| The `ctrl_block` of blockr.ai, `ai_ctrl_block()`, a chat on every block ([blockr.ai R/ai-ctrl-block.R#L51-L56](https://github.com/BristolMyersSquibb/blockr.ai/blob/7441767266cd982858bef0c633bcad5597698a0a/R/ai-ctrl-block.R#L51-L56)) | Dropped, since the assistant, a plugin, replaces it ([Assistant as a plugin](Rewrite-1.4)) |
| The dock's other extensions: the DAG, blockr.md's document, the assistant, blockr.viz's control bridge, and the outline, slides, report and minidag of blockr.outline | A plugin each, whose state is the extension's state |
| Board classes, the dock board among them | A frontend each, the dock plugin among them, whose state holds what the class's properties held, while core's own gives way to core's basic frontend, which `serve()` gives an app by default ([The frontend](#the-frontend)) |

## Proposal

### A plugin

In R, a plugin is an S3 object of class `c("{name}_plugin", ..., "plugin")`.
A package's constructor `new_{name}_plugin()` returns one, made with core's `new_plugin()`.
Its args are the state it gives the board an app script builds, such as the DAG's `positions`, as a block's args are its state, and nothing else, since a plugin's name is its class's (below).
The constructor passes `new_plugin()` the state as a list of its args by name, then the id of its class, and the plugin holds that list as its state:

```r
new_dag_plugin <- function(positions = list()) {   # in blockr.dag
  new_plugin(list(positions = positions), "dag_plugin")
}
```

So a constructor may check or convert its args before it passes them, and may call `new_plugin()` from a helper of its package.
A `new_plugin()` that read the state off the constructor would instead store every arg of the constructor, and would work only where the constructor calls it itself.
The class's id is the one that its package declares, and it alone identifies the class, in R and in JS, whatever class vector or object stands for the class on either side, as a block class's id identifies a block class ([Block classes in R](Rewrite-1.1.5#the-block-class)).
The `class` of `new_plugin()`, the class vector without `plugin`, defaults to the id and serves S3 dispatch alone, as core's basic frontend passes `c("basic_frontend_plugin", "frontend_plugin")`.
The id's full form is `{pkg}-{id}`, as `blockr.dag-dag_plugin`, which joins the class to its package, the one its constructor lives in, as a registry id carries its package ([Board objects](Rewrite-1.1.1#registry-ids)).
The class also has a name, the human-readable form of its id, such as "Document" for blockr.md's `md_plugin`, which its package lists beside the id, and which every plugin of the class bears.
The version of its state's shape is what its class's method of `plugin_version()` returns, 1 where it has none, in place of `board_version()`.

An app runs at most one plugin of each class, so a plugin is identified by its class's id, and a plugin that keeps several of something, such as blockr.md's documents, keeps them in its own state, as the dock keeps its views.
The app's plugins are the rows that `serve()` takes in `plugins`, each a plugin class by `package` and `id`, while the board constructor takes the state of the board's plugins in `plugins`, as `new_dock_board(extensions = ...)` takes extensions today ([Which plugins a board has](#which-plugins-a-board-has)).
Here, where blockr.dock, blockr.dag and blockr.md are installed beside core, the script passes no plugins:

```r
serve(
  new_board(
    blocks = blks,
    plugins = list(
      new_dag_plugin(positions = pos),
      new_md_plugin(content = "# Notes")
    )
  )
)
```

So the app runs the dock in place of core's basic frontend, core's storage and Edit board plugins, the DAG and blockr.md's plugin (below).
The board opens with the DAG's positions and the document's content, the dock starts with its class's default state, and the board holds nothing for core's storage plugin and its Edit board plugin, which keep no state.
Of each row that `serve()` takes, R reads the plugin class, and of each plugin in the board's list, its class's id and its state, so a constructor's args go in the board's list alone.
R writes the state of each plugin in the board's list into the opening board, under its class's id, where its constructor gives it any, and records the version of each such class ([Serialization](Rewrite-1.1.4#files)).
It sends the app's plugins in its reply to `hello`, in `plugins`, each by its class's id with its name and its class's version ([Wire protocol](Rewrite-1.1.9#handshake)).
As `serve()` runs, R refuses a board that the script builds with a plugin of a class that the app does not run, naming each such plugin, since the store would drop its state, while `new_board()` refuses two plugins of one class, since a board keeps one state for each class's id, and a name in its list of plugins, which would read as an id that the board does not use ([blockr.core#566](https://github.com/BristolMyersSquibb/blockr.core/pull/566)).
It writes the state by the JSON Schema of the class's state, which the package ships beside the class's module, as it ships those of its board options beside theirs, so that a value of length one that the schema has as an array stays an array ([UI modules in JS](Rewrite-1.1.7#packaging)).
A plugin class's version is the one that its package gives it, where a class without a method of `plugin_version()` is at version 1, as `options` has it for board options, and the reply holds none for a class that the app does not run, since the store drops the state of such a class's plugins before it migrates any ([blockr.core#566](https://github.com/BristolMyersSquibb/blockr.core/pull/566), [Wire protocol](Rewrite-1.1.9#handshake)).
The client takes a plugin's package from its class's id, and where its UI module is served from the modules that packages offer each other, while R lists the plugin classes of the available packages from their `._BLOCKR_MODULES_`, each with its id, its constructor and its name ([Which plugins a board has](#which-plugins-a-board-has)).

In JS, core registers the class of each of the app's plugins under the class's id before every board opens, from the default export of the class's module, which R names in the plugin's entry of the reply's `plugins`, where a package registered a board class before ([UI modules in JS](Rewrite-1.1.7#modules-of-plugin-classes-and-board-options), [blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)).
Every plugin class is defined by an object of one type, `PluginClass`, which the client looks up by the class's id, as it looks up block classes in the block registry, while R's class vectors stay in R ([State in JS](Rewrite-1#principles)).
What R knows by a plugin's class, the client knows by the members of the class's definition, as the methods of a board option became members of one `Option` ([Board options and blockr options](Rewrite-1.1.13#defining-a-board-option)).
Core, the store or every frontend reads each member, while the board holds the state of a plugin as plain data that names its class, as it holds a block, with illustrative names:

```ts
interface PluginClass {
  id: PluginClassId;                                // "blockr.dag-dag_plugin", as R names it
  options?: OptionId[];                             // the board options it requires, resolved as a board opens with one of its plugins
  state?: { schema: JsonSchema; default: Json };    // what each of its plugins keeps in the board, which holds nothing for a class without it, and which the store reads, as it reads the next two
  update?(delta: Delta, board: Board, plugin: PluginClassId): Patch[];   // patches to the state of its plugin that follow from a change
  migrate?(state: Json, version: number): Json;     // a plugin's state of an older version, in today's shape
  ui?: PluginModule;                                // what every frontend places for the class's plugin, which the class holds itself
  frontend?: FrontendModule;                        // a frontend's: what draws the page, which core calls with the page's element
  storage?: Storage;                                // a storage plugin's: the controls that every frontend draws
  commands?: Command[];                             // the commands that change its plugins' state, which core registers with the class
  start?({ core, plugin, signal }: { core: CoreApi; plugin: PluginClassId; signal: AbortSignal }): void | (() => void);   // runs from the opening of each board to the next
}

interface Plugin {                                  // one of the app's plugins, under its class's id, as core.plugins.appPlugins() gives it
  name: string;                                     // "Document", its class's name, which titles its panel
}

export default {                                   // blockr.dag's, from dag.js, the module that it lists for blockr.dag-dag_plugin
  state: { schema: dagState, default: { positions: {} } },
  update: (delta, board, plugin) => dropPositions(delta.blocks?.rm ?? [], board, plugin),   // a removed block's position goes with it
  ui: dagUi,
  commands: [relayout],
};
```

A plugin class sets any mix of these members, or none of `ui`, `frontend` and `storage`, as blockr.viz's control bridge does.
The board holds the state of a plugin whose class has `state` under its class's id, such as `"blockr.md-md_plugin": { "content": "# Notes" }`, and nothing for a plugin whose class has none, such as core's basic frontend, its storage plugin and its Edit board plugin ([Which plugins a board has](#which-plugins-a-board-has)).
Vite and Rollup take plugins in the same way, as one object whose optional hooks the bundler reads ([Vite](https://vite.dev/guide/api-plugin)), and so does ProseMirror, whose plugin spec holds an optional `state`, `props` and `appendTransaction` ([ProseMirror](https://prosemirror.net/docs/ref/#state.PluginSpec)).
Every other contract of core's client has this shape too, the module contract that follows anywidget's among them ([UI modules in JS](Rewrite-1.1.7#the-contract)).

A plugin class holds the commands that change its plugins' state, which core registers with the class, and a package lists the board options of its plugin classes as it lists any others, and gives their requests in R ([A plugin's requests](#a-plugins-requests), [blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)).
A plugin class names the board options it requires in `options`, and core resolves the default of each one that the board holds no value for before it starts the plugin or mounts its UI ([Which board options a board holds](Rewrite-1.1.13#which-board-options-a-board-holds)).
A plugin works on the board through `CoreApi` alone ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)), so the DAG adds a link by running core's command and draws its status badges from `scheduler.status()`, with no per-block callback.

A plugin class comes from a package, since only a package exports the object that lists it ([UI modules in JS](Rewrite-1.1.7#modules-of-plugin-classes-and-board-options)).
So an app script defines no plugin class, unlike a block class, which a script may define outside a package ([Board objects](Rewrite-1.1.1#block-classes-outside-a-package)), and `new_plugin()` raises an error where the constructor that calls it lives outside a package.
A test registers the plugin classes it needs itself ([Testing](#testing)).
A later version may let `serve()` take a listing of the app's own, whose plugin classes would have their name alone as their id, as a block class outside a package has ([Board objects](Rewrite-1.1.1#registry-ids)), and nothing here rules that out.

### Plugin classes

In R, core defines two plugin classes beside `plugin` for other classes to extend, `frontend_plugin` and `storage_plugin`, since every page relies on what each does (below).
A package's class extends one of them or `plugin` itself, as blockr.session's is `c("session_plugin", "storage_plugin", "plugin")`.
Core's own plugins do so too: its basic frontend is `c("basic_frontend_plugin", "frontend_plugin", "plugin")`, its storage plugin `c("file_storage_plugin", "storage_plugin", "plugin")` and its Edit board plugin `c("edit_board_plugin", "plugin")` ([The frontend](#the-frontend), [Storage](#storage), [The Edit board plugin](Rewrite-1.1.15#the-plugin)).
R's `serve()` reads them to run core's basic frontend and storage plugin only where no other row is a frontend or a storage plugin, and to refuse rows that hold no frontend, or two frontends or two storage plugins besides core's ([Which plugins a board has](#which-plugins-a-board-has)).
R calls a plugin class's methods of `plugin_version()` and `plugin_requests()` on an object of the class vector that the class's constructor gives, which it finds by the class's id among the classes that the available packages list, since a request names the plugin's class by its id alone ([A plugin's requests](#a-plugins-requests)).
For the app's frontend, it also calls the method of `frontend_args()` on such an object ([The frontend](#the-frontend)).
So only `serve()` reads `frontend_plugin` and `storage_plugin`.

In JS, no plugin class extends another, and nothing walks a chain of classes.
A plugin whose class has `frontend` is a frontend, and one whose class has `storage` is a storage plugin.
So the dock draws the controls of the app's storage plugin, whichever package that plugin comes from.

A frontend places every plugin whose class has a `ui`, each in a place of its own.
It gives `mountPlugin()` an element of its choosing, such as a panel in the dock or a section in core's basic frontend, and core mounts the module there, as `mountBlock()` mounts a block's UI ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
So every plugin with a UI works under every frontend.
A frontend may know a plugin class by its id too, as the dock might know `blockr.dag-dag_plugin` to give the DAG a place of its own, but it needs nothing beyond core's members to place a plugin.
A plugin without a UI module, such as blockr.viz's control bridge, runs from its class's `start` alone, with no place on the screen ([Running a plugin](#running-a-plugin)).

A plugin's module, the `ui` or the `frontend` of its class, meets the contract a block's UI module meets ([UI modules in JS](Rewrite-1.1.7#the-contract)), with `CoreApi` in place of a host: it exports the JS API major it was built against and a default whose `render()` core calls with an element, the id of the plugin it draws and a signal, and which returns the cleanup, so it never names its own id.
Core calls a plugin's `ui` with the element that the frontend gave `mountPlugin()`, and a frontend's module with the page's element ([The frontend](#the-frontend)):

```ts
export const api = 1;                                // the JS API major it was built against

export default {
  render({ el, core, plugin, signal }: { el: HTMLElement; core: CoreApi; plugin: PluginClassId; signal: AbortSignal }): () => void { /* draw the plugin, return the cleanup */ }
};
```

So one module draws the plugin of its class, from the plugin's state, which core names by the class's id.
It is free of any framework, as a block's UI is, and may be written in React on the one copy that core ships ([UI modules in JS](Rewrite-1.1.7#react)).
A plugin's UI renders in a root of its own, which shares no React context with the frontend's and takes its look from blockr.ui's design system ([UI kit and design system for the client](Rewrite-1.7)).
Core's own Edit board plugin cannot, since blockr.ui builds on blockr.core.
It builds on Tailwind CSS instead, as core's other UIs do ([The Edit board plugin](Rewrite-1.1.15#its-look)).

### The frontend

A frontend is a plugin whose class has `frontend`, the module that draws the page, and whose class in R extends `frontend_plugin`.
The module meets the contract of a UI module above, and core calls it with the page's element and with what the method of `frontend_args()` of its class returned.
Core defines that generic in R, and R calls the method as the app starts, with the arguments of `serve()` that core does not take itself ([Defining a board in R](Rewrite-1.1.3#the-serve-generic)).
A method takes the arguments that its frontend knows, refuses the rest, naming the frontend, and returns what the frontend reads of them as JSON, as the dock's returns the items of its bar from `navbar` ([The dock's navbar](Rewrite-1.2.5)).
The reply to `hello` carries the result in `frontend`, beside the app's plugins and outside the board, so that no file sets it and every board that the app opens gets the same ([Wire protocol](Rewrite-1.1.9#handshake)).
The method for `frontend_plugin` takes no argument, so core's basic frontend refuses every one.
A page has one frontend, the app's, since `serve()` refuses rows that hold none, or two besides core's basic frontend ([Plugin classes](#plugin-classes)).
Where core cannot register the class of the frontend that R names, as where the class's module failed to load, the page shows why in place of the board ([blockr.core#566](https://github.com/BristolMyersSquibb/blockr.core/pull/566)).
A block that `serve()` serves alone is the exception, since core draws it in a card of its own ([Defining a board in R](Rewrite-1.1.3#data-passed-to-serve)).
Core's basic frontend is a frontend like any other, which `new_basic_frontend_plugin()` makes, of class `c("basic_frontend_plugin", "frontend_plugin", "plugin")` and named Basic frontend after its class, which core lists with a module of its own, as any package lists a plugin class, and whose module holds its `frontend` ([blockr.core#566](https://github.com/BristolMyersSquibb/blockr.core/pull/566), [blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)).
It keeps no state, so the board holds nothing for it, and an app runs it unless its rows hold another frontend, as they do by default wherever another available package gives one ([Which plugins a board has](#which-plugins-a-board-has)).
Every board that the app opens runs the app's frontend, as it runs the app's other plugins, with the state that the board holds for it where its class has any.
So a dock app opens a board made in a core app with the dock's default layout, since that board holds nothing for the dock.
Core starts the page with the app's frontend, and starts the app's other plugins once the frontend has drawn, as [Drawing the board](Rewrite-1.1.8#starting-the-page) has it.
Every board that the app opens runs the same frontend, so the page never switches to another, and opening a board starts that frontend again, as [Drawing the board](Rewrite-1.1.8#opening-a-board) has it.
A frontend's state holds what it keeps of the board, as the dock's views, their grids and which view is active, which were the dock board's properties ([The dock's state: views, folders, grids and card sections](Rewrite-1.2.1)).
A board that holds the dock's state, opened in an app without the dock, drops that state, naming the dock's package, and opens with the app's frontend ([Which plugins a board has](#which-plugins-a-board-has)).

### Storage

A storage plugin saves boards and opens them, and the `storage` of its class gives the controls for it, which every frontend draws in a place of its own, such as the toolbar of core's basic frontend or the dock's navbar.
The storage plugin describes its controls, and the frontend draws them with its own components, so that they look like the rest of the frontend that draws them, whichever frontend that is.
VS Code draws the status bar items that its extensions describe in the same way ([Extending Workbench](https://code.visualstudio.com/api/extension-capabilities/extending-workbench#status-bar-item)), and so does JupyterLab with a toolbar item that names a command ([Extension points](https://jupyterlab.readthedocs.io/en/latest/extension/extension_points.html)).
With illustrative names:

```ts
interface Storage {
  controls({ core, plugin }: { core: CoreApi; plugin: PluginClassId }): StorageControl[];   // what a frontend draws, in this order
  subscribe?(listener: () => void): () => void;     // calls the listener when controls() would give something else, such as another save status
  load?({ core, plugin, signal }: { core: CoreApi; plugin: PluginClassId; signal: AbortSignal }): Promise<string | undefined>;   // the text of a board to open in place of R's, as the page starts
}

type StorageControl =
  | { kind: "button"; id: string; label: string; tooltip?: string; shortcut?: string; disabled?: boolean; run(): Promise<void> }
  | { kind: "menu"; id: string; label: string; items: StorageControl[] }   // its items open from it
  | { kind: "status"; id: string; text: string; tooltip?: string };   // text that runs nothing, such as "Saved"
```

A storage plugin gives as many controls of these three kinds as it needs, and a menu holds buttons, statuses and further menus.
A frontend draws each kind in its own look, and chooses where the controls go and how they give way on a narrow bar.
It draws them again whenever `subscribe()` calls back, and it binds the `shortcut` of each button, which takes the form of a command's ([Board updates](Rewrite-1.1.2#commands)).
It shows a `run()` that rejects as a notification ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)).
The controls do the saving and the opening themselves: they hand the JSON board that `core.store.save()` writes to where the plugin keeps boards, and open the text of a board with `core.store.open()` ([Serialization](Rewrite-1.1.4#files)).
They leave out what a lock fixes, such as opening another board under the load lock, since `controls()` reads `core.lock` ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).

Core's own storage plugin, which `new_file_storage_plugin()` makes, of class `c("file_storage_plugin", "storage_plugin", "plugin")` and named File storage after its class ([blockr.core#566](https://github.com/BristolMyersSquibb/blockr.core/pull/566)), gives two buttons, as today's `preserve_board` gives Import and Export.
Save saves the board as a download, and Open opens an upload, and the plugin leaves Open out under the load lock:

```ts
storage: {                                          // core's storage plugin's
  controls: ({ core }) => [
    { kind: "button", id: "save", label: "Save", run: async () => download(core.store.save()) },
    ...(core.lock.load ? [] : [{ kind: "button", id: "open", label: "Open", run: () => openUpload(core) }]),
  ],
}
```

Core lists its class with a module of its own, as it lists its basic frontend's, and it keeps no state, so the board holds nothing for it, while an app runs it unless its rows hold another storage plugin ([Which plugins a board has](#which-plugins-a-board-has)).
A frontend draws the controls of `core.plugins.storage()`, the `storage` of the app's storage plugin, and draws none where the app holds none ([What a frontend offers other plugins](#what-a-frontend-offers-other-plugins)).
The storage plugin of blockr.session saves to Connect and opens from it, and its controls show the workflow's name, its save status and its versions ([Session management as a storage plugin](Rewrite-1.6)).

An app holds its storage plugin as it holds any other, among the rows of `plugins`, so that an app with blockr.session installed saves to Connect by default, and one that keeps core's storage leaves blockr.session's plugin out:

```r
serve(new_board(blocks = blks), plugins = subset(available_plugins(), package != "blockr.session"))
```

An app holds at most one storage plugin, since `serve()` refuses a second besides core's.
Every board that the app opens saves through the app's storage plugin, as it runs the app's other plugins, while a frontend draws no storage controls in an app without one, as today's app without `preserve_board` has no Import and Export ([Which plugins a board has](#which-plugins-a-board-has)).
So a board that a user saved as a download through core's storage plugin saves to Connect once it opens in a Connect app, since neither storage plugin keeps anything in the board (below).
So a deployment alone chooses where its pages save, through the packages it installs and the rows its script passes to `serve()`.

The three kinds are core's, so a frontend draws the controls of every storage plugin, of a package it does not know too.
What a storage plugin cannot build from them, such as the sharing settings of session management or every version of a workflow, it draws in a dialog of its own, which one of its controls opens and which takes its look from blockr.ui's design system, as every plugin's UI does ([Plugin classes](#plugin-classes)).
A kind that core adds later needs a rule for a frontend built before it, such as skipping its controls, which the version of core that adds it settles.
A storage plugin keeps no state in the board, since the record a board was opened from is the URL's and the plugin's own, as [Session management as a storage plugin](Rewrite-1.6) has it.
Nor does it key a record on the board's name, which a rename changes at any time while some backends cannot rename a key, so a frontend's field for the name renames the board alone ([The dock's navbar](Rewrite-1.2.5#the-docks-own-parts)).
This settles the open question of [Session management as a storage plugin](Rewrite-1.6#open-questions) on whether storage becomes an interface of core.

### Which plugins a board has

A board holds the state of its plugins in `plugins`, a property of core's board, each under its class's id ([A plugin's state](#a-plugins-state)).
It holds the state of each plugin whose class has `state`, and nothing for any other, so that no board names a plugin that keeps nothing, and a plugin's name is its class's ([A plugin](#a-plugin)).
An app runs at most one plugin of each class, among them one frontend ([The frontend](#the-frontend)) and at most one storage plugin ([Storage](#storage)).

The app's plugins are those of the rows that `serve()` takes in `plugins`, which R sends in its reply to `hello`, and they run on every board that the app opens, the opening board among them, whatever state a board holds.
The rows are a data frame that gives each plugin's class in `package` and `id`, as the rows of `blocks` give block classes ([Block classes in R](Rewrite-1.1.5#registration)).
They default to `available_plugins()`, a row for each plugin class that an available package lists, so that an app runs every plugin that its packages offer unless its script narrows them, as it offers every available block class.
A script narrows them with plain R, as `subset(available_plugins(), package != "blockr.session")` does, and gives no YAML file, as it may for block classes, since an app runs few plugins, which its script chooses ([blockr.core#562](https://github.com/BristolMyersSquibb/blockr.core/pull/562)).
Core's basic frontend runs only where no other row is a frontend, and core's storage plugin only where no other row is a storage plugin, so that an app with blockr.dock installed draws with the dock, and one with blockr.session saves to Connect, without its script naming either.
Rows that hold two frontends or two storage plugins besides core's, or no frontend, stop the app as it starts, naming them, so that where two frontends are installed, the script drops one of them.
So an app whose script passes no plugins, where no other package gives a frontend or a storage plugin, draws the board with core's basic frontend, saves it as a download and opens an upload, and lets the user add blocks and edit links and stacks, as today's `serve()` gives a core board its UI, `preserve_board` and `manage_blocks` ([The Edit board plugin](Rewrite-1.1.15#what-serve-gives-by-default)).
Rows that a script passes replace the default, so they hold a frontend, which `serve()` refuses to do without, and a storage plugin wherever the app's pages save.
A board gives only the state of its plugins, whether the script builds it with `new_board()` or a file holds it.
Since a board and a JSON board are one thing, which plugins run is stated outside every board, so that no file sets them.
Opening a board starts them again, the frontend among them, once they have stopped as they ran on the board before, since core starts again as a board opens ([Drawing the board](Rewrite-1.1.8#opening-a-board)), so that a plugin starts again with the state of the board that opens.
So the page is what opening that board in a fresh app would give ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).

As a board opens, the store keeps the state that the board holds for each plugin of the app whose class has `state`, under the plugin's class's id, where a package that the app uses registers the class.
Such a plugin starts with that state, which its class's `migrate` brings to today's shape ([Board updates](Rewrite-1.1.2#plugins)).
The store drops every other state that the board holds, as it drops a block whose class the block registry lacks, and names its plugin with the package of the plugin's class, which the class's id gives ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)), but for the state of one of the app's plugins whose class keeps none, which it drops unnamed, since that plugin still runs and nothing is lost ([blockr.core#566](https://github.com/BristolMyersSquibb/blockr.core/pull/566)).
It drops them before it checks or migrates any version, since it drops a plugin's state for its class, never for its version ([Board updates](Rewrite-1.1.2#plugins)).
So no plugin starts from state that a board kept while it changed without the plugin's package, and a board saved afterwards is written without that state, as condition 4 of [Board objects](Rewrite-1.1.1#what-must-hold) has it for blocks.

Then each other plugin of the app whose class a package that the app uses registers, and has `state`, starts with its class's default state, which the board then holds for it.
So the app sets the plugins that run on every board that it opens, and the page runs, draws and saves a board as a fresh start of the same app would, whatever was open before:

- An app whose script passes no plugins, where no other package gives a frontend or a storage plugin, draws every board with core's basic frontend and saves it through core's storage plugin, whether its script built the board or `serve()` was given the board's file.
- A file that `serve()` is given gives only the state of its plugins too, so a core board that today's stack saved, which holds no plugin's state once converted, runs core's Edit board plugin from the default of `serve()` ([The Edit board plugin](Rewrite-1.1.15#what-serve-gives-by-default)).
- A board saved before an app added the assistant to its plugins runs the assistant as it opens, from its class's default state, as a plugin that `serve()` takes reaches every board today ([Today](#today)).
- A board keeps the state of its DAG and of blockr.md's plugin, with every document in it, where the app runs both, and drops the state of either where the app does not run it.
- A board made in a core app holds nothing for its frontend, since core's basic frontend keeps no state, so in a dock app the dock lays it out from its default, while a board that holds the state of a frontend of another class drops it.
- A board saved as a download holds nothing for core's storage plugin, and opened in a Connect app through session management it saves to Connect from then on ([Storage](#storage)).
- A board that the app's storage plugin names in place of the opening board, through its class's `storage.load()`, runs the app's plugins too, so a record that session management opens from a URL as the page starts runs the plugins that the app script passed to `serve()`, each with the state that the record holds for it.
- A dock board opened in an app without blockr.dock drops the dock's state, which the client names, and draws with the app's frontend, as in a core app.

No change adds a plugin or removes one, since the app sets the plugins: a patch changes a plugin's state at or below `/plugins/{id}`, as `/plugins/blockr.dag-dag_plugin/positions/a`, and the store refuses one that adds or removes what the board holds for a plugin, as an `add` or a `remove` at `/plugins/blockr.dag-dag_plugin` would ([Board updates](Rewrite-1.1.2#plugins)).
So the app alone decides which plugins run, what draws the page and where it saves, as `serve(plugins = ...)` does today, with no union of the board's plugins and the app's that would need a rule for each clash.
An app runs a plugin through the rows of `plugins`, and what a user adds more of while the app runs, such as another document, lives in the state of one plugin, as the dock's views do.
On a locked board, each plugin locks what it alone governs in its state, as the dock does the arrangement of its panels, while the board lock fixes no plugin's name, since each is its class's ([Locked boards and the properties of blocks](Rewrite-1.1.11#plugins-on-a-locked-board)).

### Running a plugin

Besides the store, which calls a plugin class's `migrate` as a board opens and its `update` with every change, core runs a plugin's code in two places: a frontend mounts its class's `ui` where it places the plugin, and core calls its class's `start`.
Core calls `start` for each of the app's plugins once the board has opened and the frontend's `render()` has returned, so that what the frontend first shows is evaluated first.
As the next board opens, core aborts the plugin's signal and runs the cleanup that `start` returned, as it does for a module's `render()` ([Plugin classes](#plugin-classes)), since no change adds or removes a plugin while a board is open.
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
So no package adds a request type of its own, as that pull request left the dock to do for its extensions, and `CoreApi.request()` sends a plugin's request alone.

Whoever calls `CoreApi.request()` names one of the app's plugins by its class's id, which the message carries, and by which R finds the method.
R calls the request's function with the args that the client passes, by name, with the request's body in `file` where the function takes it, and with the blocks that the request reads in `reads`, by block id, each a list of the block's `result` and its block expression `expr`.
Core has those blocks evaluated first, even off screen, as for a one-time evaluation ([Evaluation in the client](Rewrite-1.1.10#demand)).
A plugin's request may write, so the client never keeps its answer ([Wire protocol](Rewrite-1.1.9#requests)).
It may answer with a file, through `new_reply_body()`, and report how far it has come through `report_progress()`.
On a locked board, R runs it as on any other ([Locked boards and the properties of blocks](Rewrite-1.1.11#what-r-refuses)).

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

A plugin's state takes the place of a board class's properties, and the store keeps it as [Board updates](Rewrite-1.1.2#plugins) has it:

- A change inside it is a patch at a path under the plugin's state, as `/plugins/blockr.dag-dag_plugin/positions/a`.
- The store keeps an edit id for each plugin, as it kept one for each property, which a patch to the plugin names, so that the store refuses the patch where another edit to the plugin came first ([Board updates](Rewrite-1.1.2#deltas)).
- The store checks the state against its class's schema after every change, keeps the inverse patches for undo, and saves the state with the board.
- The store calls the `update` of each plugin's class with every change it applies, in the same step, and refuses a patch that an `update` returns outside the state of its own plugin ([Board updates](Rewrite-1.1.2#applying-a-delta)).
- Core's command `blockr.core-set_plugin_state` and the commands of the plugin's class change its state, naming the plugin by its class's id, and everything else changes it through them, which is external control ([Board updates](Rewrite-1.1.2#commands)).
- A JSON board records in `versions` the version of each class whose plugin's state it holds, by the class's id, and the class's package in `packages`, and the class's `migrate` takes its plugin's state at an older version ([Serialization](Rewrite-1.1.4#migrations)).

Core's command opens every plugin's state to every other plugin, as core's commands open every block's state ([Board updates](Rewrite-1.1.2#commands)).
It takes a plugin's class's id and patches at paths within the plugin's state, and returns them under the plugin's path, so that the store checks them against the class's schema and calls the class's `update` as it does with any other change:

```ts
await core.commands.run("blockr.core-set_plugin_state", {    // the assistant, moving a block in the DAG
  plugin: "blockr.dag-dag_plugin",
  patches: [{ op: "replace", path: "/positions/a", value: { x: 40, y: 80 } }],   // applied at /plugins/blockr.dag-dag_plugin/positions/a
}, "assistant");
```

So no part of a plugin's state is closed to other plugins, whether or not its class registers a command for it, and the assistant's tool for it is typed, for each plugin, by the schema of its class's state and described by that schema's `description` keywords, as its tool for a block's state is by the block class's schema.
A class's own commands stay for changes that need more than its schema keeps valid, as the dock adds a view with its layout.
Core's command is not enabled on a locked board, since there only a class's own commands know what the plugin locks ([Locked boards and the properties of blocks](Rewrite-1.1.11#plugins-on-a-locked-board)).

A plugin's module, its `ui` or its `frontend`, follows the plugin's state through `core.store.subscribe()`, as a block's UI follows the block's state through its host, and updates what it shows in place, leaving the input the user is editing, so that a change that another plugin, the assistant or an undo makes shows at once ([UI modules in JS](Rewrite-1.1.7#the-contract)).
So what others may change, such as which view the dock shows, lives in the plugin's state rather than in its module alone, while what only one person's screen needs, such as which block has focus, core holds for the page ([What a frontend offers other plugins](#what-a-frontend-offers-other-plugins)).

Each plugin class gives the state of its plugins a shape of its own, so the dock's views and the layout of another frontend share nothing.
What a plugin keeps about one of core's objects is an entry in its state keyed by the object's id, as the DAG keeps a block's position, so that core adds nothing to blocks for it ([Locked boards and the properties of blocks](Rewrite-1.1.11#what-a-plugin-keeps-about-a-block)).

A board with the dock, the DAG and blockr.md's plugin, with illustrative states:

```json
{
  "format": 1,
  "packages": { "blockr.core": "0.2.0", "blockr.dock": "0.2.1", "blockr.dag": "0.2.0", "blockr.md": "0.2.0" },
  "board": {
    "id": "curious_otter",
    "versions": { "blockr.dock-dock_plugin": 1, "blockr.dag-dag_plugin": 1, "blockr.md-md_plugin": 1 },
    "name": "Sales review",
    "blocks": {
      "a": { "registry_id": "blockr.core-dataset_block", "version": 1, "state": { "dataset": "iris", "package": "datasets" }, "name": "Iris", "locked": null }
    },
    "links": {},
    "stacks": {},
    "options": {},
    "plugins": {
      "blockr.dock-dock_plugin": { "views": { "main": { "name": "Main", "folder": null, "index": "a0", "grid": { "orientation": "horizontal", "children": [{ "panels": [{ "block": "a" }, { "plugin": "blockr.md-md_plugin" }], "active": { "block": "a" } }], "sizes": [1] } } }, "folders": {}, "active": "main", "visible": {} },
      "blockr.dag-dag_plugin": { "positions": { "a": { "x": 120, "y": 80 } } },
      "blockr.md-md_plugin": { "content": "# Notes\n\n![Iris](blockr://a)" }
    }
  }
}
```

### What a frontend offers other plugins

Part of what [The dock's services](Rewrite-1.2.6) gives the dock's extensions, every frontend gives every plugin through `CoreApi`, so a plugin that uses it works under any frontend:

- Notifications, which the frontend draws, core's own among them, such as what the store dropped when a board opened ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)).
- Which block has focus, which the frontend sets and the assistant reads to tell which block the user is looking at ([Assistant as a plugin](Rewrite-1.4)).
  Core holds it for the page, outside the board, since only one person's screen needs it ([Board objects](Rewrite-1.1.1#extending-cores-objects)).

They are the `notifications` and `focus` of `CoreApi`, which [Drawing the board](Rewrite-1.1.8#what-core-gives-plugins) gives in full, with the members that the sections above give plugins, `plugins`, `mountPlugin()` and `request()`.

### What goes

- Board classes: the board class that `core.store.register()` takes today, a board's `class`, the board classes in its `versions`, which holds plugin classes instead, the R generics `board_front_end()` and `board_version()`, and the rule that the client builds a board as the first class in its `class` that a loaded package defines ([blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474)).
- The `class` argument of `new_board()`, and the components that its `...` adds beside core's, which `plugins` replaces, so that every R board is of class `board`.
- The dock board as a class, `dock_board`, with its `extensions`, whose entries become plugins of their own.
- Core's nine plugin classes and `known_plugins()`.
  Storage keeps a class in core, `storage_plugin`, and `manage_blocks`, `manage_links` and `manage_stacks` become one, `edit_board_plugin` ([The Edit board plugin](Rewrite-1.1.15)).
- The function that `serve()` takes as `plugins` today, with `custom_plugins()` and `blockr_app_plugins()`, since `serve()` takes the app's plugins as a list, which names every plugin that the app runs ([Which plugins a board has](#which-plugins-a-board-has)).
- Registering a frontend through its board class, which the frontend plugin replaces ([The frontend](#the-frontend)).

On `js-state`, the board classes of [blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474) become plugin state: the patches, the schema checks, `update` and `migrate` keep their code, with each state and each definition under its plugin class's id, rather than under a board class.
On `js-state` too, core's basic frontend and core's own storage plugin stand in where a board holds no frontend or no storage plugin, and the board holds every plugin that runs, with its name, and with an empty state where its class has none.
Both become plugins of their own, and the board holds only the state of a plugin whose class has `state`, under its class's id, while a plugin's name is its class's ([blockr.core#558](https://github.com/BristolMyersSquibb/blockr.core/issues/558)).

### Boards and app scripts from today

- The conversion outside core ([Serialization](Rewrite-1.1.4#files)) turns a dock board into a board that holds the state of the dock plugin, taken from the dock board's `views` and `grids`, and the state of a plugin for each extension class that keeps any, under the class's id and taken from the extension's, each class at version 1.
  A board with two extensions of one class, such as two documents of blockr.md, converts into one state of that class's plugin that holds both, as the class's package has its conversion merge them.
- An app script keeps building its board with `new_dock_board()`, which returns a board that holds the state of the dock plugin and of the plugins that the script gives it in `plugins`, while the app runs those plugins where their packages are available, as by default, which [Saved boards and app scripts across the switch](Rewrite-1.2.2) settles in detail.
- An app script that sets storage through `serve(plugins = custom_plugins(manage_project()))` passes no plugins instead, since blockr.session's storage plugin runs by default where blockr.session is installed, from where it reaches every board that the app opens.
- An app script that sets code export through `serve(plugins = custom_plugins(generate_flat_code()))`, as blockr.code's README does ([blockr.code README.Rmd#L43-L56](https://github.com/BristolMyersSquibb/blockr.code/blob/72b20d6911496e4edc9ee64db758e70ebf3f50ca/README.Rmd#L43-L56)), passes no plugins either, since blockr.code's plugin runs by default where blockr.code is installed, from where it reaches every board that the app opens, as `serve()` gives it to every board today.
- Either script, for a core board, keeps core's basic frontend and its Edit board plugin without naming them, since both run by default too, as `custom_plugins()` kept every default that it did not replace, `preserve_board` and `manage_blocks` among them ([The Edit board plugin](Rewrite-1.1.15#boards-and-app-scripts-from-today)).
- An app script that defines a dock extension of its own with `new_dock_extension()` cannot define a plugin class in its place, since a plugin class comes from a package ([A plugin](#a-plugin)).
  Only four of blockr.dock's examples do so, `panel-ops` ([blockr.dock inst/examples/panel-ops/app.R#L79-L87](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/examples/panel-ops/app.R#L79-L87)), `sidebar-menus`, `sidebar-inputs` and `sidebar-owner`, which its browser tests run, and those tests move to the `CoreApi` for tests, where a test registers the plugin classes it needs ([Testing](#testing)).

### Testing

The `CoreApi` for tests that core ships ([Drawing the board](Rewrite-1.1.8#testing)) runs a plugin on a board in a test runner, its `update` and `migrate` included, so testing a plugin, a frontend among them, needs neither R nor a browser.
A test gives the `CoreApi` for tests the module of each plugin class it runs, by the id that a reply names it under, or registers a class through `core.plugins.register()`, as core does with each module's default export, so a class that only a test needs, such as one that drives the dock's panels, needs no package.

## Open questions

None.

<details><summary>Notes for implementers</summary>

The board classes to replace on `js-state`, at `d363b48`: the board class and its registration in `srcts/store/registrations.ts`, the board's `class` in `srcts/types/board.ts`, building a board as a class in `srcts/store/store.ts`, the classes in the reply to `hello` in `srcts/protocol/messages.ts` and `R/loaded-reply.R`, `board_front_end()` and `board_version()` in `R/board-class.R`, the modules of frontends in `R/pkg-modules.R`, a board's `class` and `versions` in `R/utils-serdes.R`, and the frontend of the class that a board is built as, which `srcts/core/start.ts` imports as the board opens and `srcts/core/frontends.ts` draws ([blockr.core#494](https://github.com/BristolMyersSquibb/blockr.core/pull/494)).

A plugin's request carries the type `plugin` and the id of the plugin's class, beside the properties that every request has ([blockr.core#484](https://github.com/BristolMyersSquibb/blockr.core/pull/484)):

```json
{ "id": "40", "kind": "request", "type": "plugin", "plugin": "blockr.md-md_plugin", "name": "html",
  "args": { "content": "# Report" }, "reads": [ { "block": "a", "revision": 2 } ] }
```

R reads it into an object of class `plugin_request`, and its method of `request_call()` dispatches `plugin_requests()` on an object of class `c("md_plugin", "plugin")`, which it makes from the class's id, as the method for board options makes one with `new_board_option()`, and binds the args with `request_call_args()`, as that method does, with `reads` and `file` reserved.

On `js-state`, at `d363b48`, `CoreApi.request()` still takes a request's type and its properties, as a request of a type that a package adds ([srcts/types/core-api.ts#L32-L34](https://github.com/BristolMyersSquibb/blockr.core/blob/d363b480c1db16451788d507b41c49cd99133d4a/srcts/types/core-api.ts#L32-L34)), which `srcts/core/requests.ts` sends, and core exports `request_call()` with an example of a package adding the type `code` ([R/request-types.R#L30-L69](https://github.com/BristolMyersSquibb/blockr.core/blob/d363b480c1db16451788d507b41c49cd99133d4a/R/request-types.R#L30-L69)).
Both go, since no package adds a type ([A plugin's requests](#a-plugins-requests)): `request()` takes a plugin's class's id, and core keeps the generic to itself.

Where a board holds state under the id of one of the app's plugins but for another class, the store drops it, and the app's plugin starts with its class's default state.

On `js-state`, at `1776bf1`, the store reads the app's plugins off the opening board with `openingPlugins()` in `srcts/store/open.ts` ([#L297](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/srcts/store/open.ts#L297), [#L339-L352](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/srcts/store/open.ts#L339-L352)), and `keptPlugins()` and `appPlugins()` in `srcts/store/plugins.ts` match a board against them.
The store takes them from the `plugins` of the reply to `hello` instead, which `R/loaded-reply.R` writes from the rows that `serve()` takes.
At that commit, `serve.board()` and `serve.character()` refuse `plugins` ([R/utils-serve.R#L70-L80](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/R/utils-serve.R#L70-L80)).
At `306e5af`, `appPlugins()` gives the board every plugin of the app with its name, and with its class's default state, `{}` for a class without `state` ([srcts/store/plugins.ts#L59-L71](https://github.com/BristolMyersSquibb/blockr.core/blob/306e5af6e64b69f01d9eca6efe73ff93c3d0f03d/srcts/store/plugins.ts#L59-L71)), where the store holds the state of a plugin whose class has `state` alone, under the class's id, and takes each plugin's name from the reply's `plugins`.
Core's basic frontend there is `BASIC_FRONTEND` in `srcts/core/plugins.ts`, which no board holds, so that `FrontendArgs` leaves its `plugin` out and `frontend()` falls back to it, while `storage()` falls back to `coreStorage()` from `srcts/storage/` ([srcts/core/plugins.ts#L41-L54](https://github.com/BristolMyersSquibb/blockr.core/blob/306e5af6e64b69f01d9eca6efe73ff93c3d0f03d/srcts/core/plugins.ts#L41-L54), [#L171-L186](https://github.com/BristolMyersSquibb/blockr.core/blob/306e5af6e64b69f01d9eca6efe73ff93c3d0f03d/srcts/core/plugins.ts#L171-L186)), and `srcts/core/start.ts` adds no board options for it.
Core registers a class for each instead, `blockr.core-basic_frontend_plugin`, whose `frontend` is `blockr.core-basic` and whose `options` are `show_conditions` and `dark_mode`, and `blockr.core-file_storage_plugin`, whose `storage` is `coreStorage()`, and every fallback goes.
On `js-state`, `Storage` holds `save()` and `open()` ([srcts/store/registrations.ts#L82-L88](https://github.com/BristolMyersSquibb/blockr.core/blob/a128742941e5263d955bfdafa0395782bdb6862c/srcts/store/registrations.ts#L82-L88)), which `controls()` and `subscribe()` replace, and the toolbar of core's basic frontend draws the storage plugin's controls in place of its own Save and Open ([srcts/modules/basic/toolbar.tsx#L45-L64](https://github.com/BristolMyersSquibb/blockr.core/blob/a128742941e5263d955bfdafa0395782bdb6862c/srcts/modules/basic/toolbar.tsx#L45-L64)).
In R, `new_board()` checks that a board holds at most one frontend and one storage plugin ([R/board-class.R#L150-L160](https://github.com/BristolMyersSquibb/blockr.core/blob/306e5af6e64b69f01d9eca6efe73ff93c3d0f03d/R/board-class.R#L150-L160)), which `serve()` checks of the app's rows instead, once core's basic frontend and storage plugin give way to any other, refusing rows without a frontend as well.
On `js-state`, R lists no plugin class, and finds one only through a method of `plugin_version()` ([R/plugin-class.R#L272-L304](https://github.com/BristolMyersSquibb/blockr.core/blob/cebaadeb809b56eb93efa95359c9d9b2b06309d4/R/plugin-class.R#L272-L304)), so `available_plugins()` lists core's three classes alone until each package lists its own in its `._BLOCKR_MODULES_` ([blockr.core#560](https://github.com/BristolMyersSquibb/blockr.core/issues/560)).

Rewrite 1.2 to 1.8, drafts written before this page, still have the dock's extensions where this page has plugins, and "front-end" where it has "frontend", and follow it as each is revised.

A plugin class's state has two defaults: its constructor's in R, which the plugins of a board that an app script builds take, and `state.default` in JS, which a plugin of the app takes where the board opens without its state, so its package keeps the two alike.

</details>
