# Plugins for the client-owned board
Status: settled on 2026-11-08. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): what a plugin is in R and in JS, the plugin classes core defines in R, the frontend and storage plugins, which plugins a board has, how a plugin runs, and a plugin's state.
Plugins are core's second way to extend a board, beside block classes, and take the place of three mechanisms: core's plugins of today, the dock's extensions, and the board classes that [blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474) built on `js-state`.
It changes what [blockr.core#494](https://github.com/BristolMyersSquibb/blockr.core/pull/494) built of `CoreApi` and starting the page, and core's basic frontend as [blockr.core#441](https://github.com/BristolMyersSquibb/blockr.core/issues/441) built it, and shapes the plugins that [blockr.core#504](https://github.com/BristolMyersSquibb/blockr.core/issues/504), [blockr.core#505](https://github.com/BristolMyersSquibb/blockr.core/issues/505), [blockr.core#506](https://github.com/BristolMyersSquibb/blockr.core/issues/506) and [blockr.core#507](https://github.com/BristolMyersSquibb/blockr.core/issues/507) build, serving a board ([blockr.core#442](https://github.com/BristolMyersSquibb/blockr.core/issues/442)), taking the app's plugins in `serve()` ([blockr.core#558](https://github.com/BristolMyersSquibb/blockr.core/issues/558)) and the migration notes for app scripts ([blockr.core#445](https://github.com/BristolMyersSquibb/blockr.core/issues/445)).
What core gives plugins through `CoreApi`, starting the page, opening a board, core's basic frontend and renderers are [Drawing the board](Rewrite-1.1.8)'s, and what the dock plugin keeps in its state and where it places other plugins stay with [Client-drawn dock and extensions](Rewrite-1.2).

## What must hold

1. Core has two ways to extend a board, block classes and plugins, and no other, so a board has no class of its own.
2. A plugin works under every frontend: it works on the board through `CoreApi`, keeps its state in the board, and offers its UI as a module that core mounts where the frontend puts it.
3. The frontend is a plugin, and every frontend places every plugin that has a UI, including one from a package it does not know.
4. The app's plugins, which the app script passes to `serve()`, are the plugins of every board that the app opens, the opening board among them, its frontend and its storage plugin included: a board keeps each of its plugins that the app holds under the same id and of the same class, with the plugin's name and state, and drops the others, naming the package of each, as it drops a block ([Board objects](Rewrite-1.1.1#what-must-hold)).
   So the page is what opening that board in a fresh app would give, whatever was open before, as condition 6 of [Board updates](Rewrite-1.1.2#what-must-hold) asks.
   A board gives only the state of its plugins, whether a script builds it or a file holds it, and a JSON board holds that of every plugin that ran on the page that saved it.
5. A board gets each plugin of the app that it does not keep, under the same id and with the name that the app gives it, with its class's default state, and core's basic frontend or core's own storage plugin serves where the app holds no frontend or no storage plugin, so that which plugins run, what draws the page and where it saves depend on the app alone, never on the board or on what was open before.
   So a plugin that an app script passes to `serve()` reaches every board that the app opens, saved ones and a file given to `serve()` included, as a plugin that `serve()` takes reaches every board it serves today, and a file never changes the frontend or the storage plugin.
6. A plugin's state belongs to that plugin alone, keyed by its id: it is saved, undone and migrated with the board, and its shape is its class's own, so that the states of two frontends share nothing.
7. Boards saved by today's blockr.dock open with their views, their layouts and the state of their extensions, as condition 4 of [State in JS](Rewrite-1#what-must-hold) asks.
8. A board holds as many plugins of one class as the app holds, such as two documents of blockr.md, but at most one frontend and one storage plugin, and what a user adds more of while the app runs lives in the state of one plugin, as the dock's views do.
9. On a board that is not locked, every plugin, the assistant among them, can change another plugin's state as it can change a block's, whether or not the other's class registers a command for it, and the other plugin's UI shows the change at once, as a block's UI does.

## Today

Three mechanisms extend a board, two on main and one on `js-state`:

- **Core's plugins** are Shiny module pairs that `new_plugin(server, ui, validator, class)` makes, each of exactly one of the nine classes that `known_plugins()` lists, with its class as its id ([R/board-plugins.R#L38-L75](https://github.com/BristolMyersSquibb/blockr.core/blob/460afef170ed67ec926a75ed66021bc98ce61647/R/board-plugins.R#L38-L75)).
  The app sets them: `serve()` takes `plugins` as a function, which gives every board the app serves its plugins, restored boards included, and no file holds them ([R/utils-serve.R#L120-L160](https://github.com/BristolMyersSquibb/blockr.core/blob/460afef170ed67ec926a75ed66021bc98ce61647/R/utils-serve.R#L120-L160)).
  So an app swaps blockr.session's storage in for core's with `serve(plugins = custom_plugins(manage_project()))` ([README.Rmd#L38-L47](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/README.Rmd#L38-L47)).
- **The dock's extensions** are Shiny module pairs that `new_dock_extension()` makes, which `new_dock_board(extensions = ...)` puts on the board.
  The board sets them: saving writes each with its constructor, the constructor's package and its state, and restoring calls each constructor that the file names, loading its package where it is installed ([blockr.dock R/utils-serdes.R#L78-L185](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/utils-serdes.R#L78-L185), [R/utils-serdes.R#L518-L539](https://github.com/BristolMyersSquibb/blockr.core/blob/460afef170ed67ec926a75ed66021bc98ce61647/R/utils-serdes.R#L518-L539)).
- **Board classes**, on `js-state`, are defined in JS with the properties they add, each with a schema and a default, and with an `update` and a `migrate` for them, while R names each class's frontend and version through `board_front_end()` and `board_version()` ([blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474), [srcts/store/registrations.ts](https://github.com/BristolMyersSquibb/blockr.core/blob/3536c4dad52b09bb6f9adb220d4981b1350276b9/srcts/store/registrations.ts)).
  The dock board adds its views and layouts as properties, and keeps the state of its extensions in its `extensions`.

| Today | Where it goes |
|---|---|
| `preserve_board`, with core's Import and Export | Core's storage plugin, which saves a board as a download and opens an upload ([Storage](#storage)) |
| `manage_project()` of blockr.session | Its storage plugin ([Session management as a client extension](Rewrite-1.6)) |
| `generate_code`, core's and blockr.code's `generate_flat_code()` ([blockr.code R/plugin.R#L31-L35](https://github.com/BristolMyersSquibb/blockr.code/blob/72b20d6911496e4edc9ee64db758e70ebf3f50ca/R/plugin.R#L31-L35)) | The plugin of blockr.code ([Code export as a client extension](Rewrite-1.5)) |
| `manage_blocks`, `manage_links` and `manage_stacks`, with the dock's Edit board extension | Core's Edit board plugin, which runs core's commands under every frontend and which `serve()` gives an app by default ([The Edit board plugin](Rewrite-1.1.15)) |
| `edit_block`, `edit_stack`, `notify_user` and `ctrl_block` | Where the notes of [Client-drawn dock and extensions](Rewrite-1.2) put them: core's commands, with the menus, cards, stack editors and notifications of the frontend and the DAG |
| The `ctrl_block` of blockr.ai, `ai_ctrl_block()`, a chat on every block ([blockr.ai R/ai-ctrl-block.R#L51-L56](https://github.com/BristolMyersSquibb/blockr.ai/blob/7441767266cd982858bef0c633bcad5597698a0a/R/ai-ctrl-block.R#L51-L56)) | Dropped, since the assistant, a plugin, replaces it ([Assistant as a client extension](Rewrite-1.4)) |
| The dock's other extensions: the DAG, blockr.md's document, the assistant, blockr.viz's control bridge, and the outline, slides, report and minidag of blockr.outline | A plugin each, whose state is the extension's state |
| Board classes, the dock board among them | A frontend each, the dock plugin among them, whose state holds what the class's properties held ([The frontend](#the-frontend)) |

## Proposal

### A plugin

In R, a plugin is an S3 object of class `c("{name}_plugin", ..., "plugin")`.
A package's constructor `new_{name}_plugin()` returns one, made with core's `new_plugin()`.
Its args are the state it gives the board an app script builds, such as the DAG's `positions`, as a block's args are its state, and `plugin_name` gives its name, as `block_name` gives a block's.
The constructor passes `new_plugin()` the state as a list of its args by name, then `plugin_name` and the class vector without `plugin`, and the plugin holds that list as its state:

```r
new_dag_plugin <- function(positions = list(), plugin_name = "DAG") {   # in blockr.dag
  new_plugin(list(positions = positions), plugin_name, "dag_plugin")
}
```

So a constructor may check or convert its args before it passes them, and may call `new_plugin()` from a helper of its package.
A `new_plugin()` that read the state off the constructor would instead store every arg of the constructor, and would work only where the constructor calls it itself.
Its class's id is `{pkg}-{name}_plugin`, as `blockr.dag-dag_plugin`.
That id joins the class to its package, the one its constructor lives in, as a registry id carries its package ([Board objects](Rewrite-1.1.1#registry-ids)).
The version of its state's shape is what its class's method of `plugin_version()` returns, 1 where it has none, in place of `board_version()`.
An app script passes the app's plugins to `serve()` in `plugins`, as it passes today's plugins, and the board constructor takes the state of the board's plugins in `plugins`, as `new_dock_board(extensions = ...)` takes extensions today ([Which plugins a board has](#which-plugins-a-board-has)).
A plugin's id is its name in either list, so that the two lists name a plugin alike:

```r
serve(
  new_board(
    blocks = blks,
    plugins = list(
      new_dag_plugin(positions = pos),
      notes = new_md_plugin(content = "# Notes", plugin_name = "Notes")
    )
  ),
  plugins = list(
    new_dock_plugin(),
    new_dag_plugin(),
    notes = new_md_plugin(plugin_name = "Notes"),
    report = new_md_plugin(plugin_name = "Report"),
    new_edit_board_plugin()
  )
)
```

So the board opens with the DAG's positions and the notes' content, and with the dock, the report and the Edit board plugin each in its class's default state.
Of each plugin that `serve()` takes, R reads its class and its name, while its state is the board's, so a constructor's state args go in the board's list.
R writes each plugin of the board that the script builds into the opening board under its id, with its class's id, its name and its state, and records each class's version ([Serialization](Rewrite-1.1.4#files)).
It sends the app's plugins in its reply to `hello`, in `plugins`, each under its id with its class's id and its name ([Wire protocol](Rewrite-1.1.9#handshake)).
As `serve()` runs, R refuses a board that the script builds with a plugin that the app does not hold under the same id and of the same class, naming each such plugin, since the store would drop it as the board opens.
It writes the state by the JSON Schema of the class's state, which the package ships beside its startup module, as it ships those of its board options, so that a value of length one that the schema has as an array stays an array ([UI modules in JS](Rewrite-1.1.7#packaging)).
In the reply to `hello`, R sends the versions that the packages the app names give their plugin classes, by the class's id, in `plugin_versions`, where a class without a method of `plugin_version()` is at version 1, as `option_versions` has it for board options ([Wire protocol](Rewrite-1.1.9#handshake)).
The client takes a plugin's package from its class's id, and where its UI module is served from the modules that packages offer each other, so R keeps no list of plugin classes.

In JS, the package's startup module registers each of its plugin classes once, under the class's id, where it registered a board class before ([UI modules in JS](Rewrite-1.1.7#startup-modules)).
Every plugin class is defined by an object of one type, `PluginClass`, which the client looks up by the class's id, as it looks up block classes in the block registry, while R's class vectors stay in R ([State in JS](Rewrite-1#principles)).
What R knows by a plugin's class, the client knows by the members of the class's definition, as the methods of a board option became members of one `Option` ([Board options and blockr options](Rewrite-1.1.13#defining-a-board-option)).
Core, the store or every frontend reads each member, while the board holds each plugin as plain data that names its class, as it holds a block, with illustrative names:

```ts
interface PluginClass {
  id: PluginClassId;                                // "blockr.dag-dag_plugin", as R names it
  options?: OptionId[];                             // the board options it requires, resolved as a board opens with one of its plugins
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
A plugin class names the board options it requires in `options`, and core resolves the default of each one that the board holds no value for before it starts the plugin or mounts its UI ([Which board options a board holds](Rewrite-1.1.13#which-board-options-a-board-holds)).
A plugin works on the board through `CoreApi` alone ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)), so the DAG adds a link by running core's command and draws its status badges from `scheduler.status()`, with no per-block callback.

A plugin class comes from a package, since a startup module registers it and only a package declares one ([UI modules in JS](Rewrite-1.1.7#startup-modules)).
So an app script defines no plugin class, unlike a block class, which a script may define outside a package ([Board objects](Rewrite-1.1.1#block-classes-outside-a-package)), and `new_plugin()` raises an error where the constructor that calls it lives outside a package.
A test registers the plugin classes it needs itself ([Testing](#testing)).
A later version may let `serve()` take a startup module of the app's own, whose plugin classes would have their name alone as their id, as a block class outside a package has ([Board objects](Rewrite-1.1.1#registry-ids)), and nothing here rules that out.

### Plugin classes

In R, core defines two plugin classes beside `plugin` for other classes to extend, `frontend_plugin` and `storage_plugin`, since every page relies on what each does (below).
A package's class extends one of them or `plugin` itself, as blockr.session's is `c("session_plugin", "storage_plugin", "plugin")`.
Core's own Edit board plugin extends `plugin` itself, as `c("edit_board_plugin", "plugin")` ([The Edit board plugin](Rewrite-1.1.15#the-plugin)).
R's `serve()` refuses a second frontend or a second storage plugin among the app's plugins by them.
R calls a plugin class's methods of `plugin_version()` and `plugin_requests()` on an object of class `c("{name}_plugin", "plugin")`, which it makes from the class's id, since a request names the plugin's class by its id alone ([A plugin's requests](#a-plugins-requests)).
So only `serve()` reads `frontend_plugin` and `storage_plugin`.

In JS, no plugin class extends another, and nothing walks a chain of classes.
A plugin whose class has `frontend` is a frontend, and one whose class has `storage` is a storage plugin.
So the dock has its save and open controls call the storage plugin of the open board, whichever package that plugin comes from.

A frontend places every plugin whose class has a `ui`, once for each plugin, so that two documents of blockr.md get a panel each.
It gives `mountPlugin()` an element of its choosing, such as a panel in the dock or a section in core's basic frontend, and core mounts the module there, as `mountBlock()` mounts a block's UI ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
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
  .flatMap(id => core.plugins.pluginClass(id).dockNavbar?.(id) ?? []);

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

A plugin's module, the `ui` or the `frontend` of its class, meets the contract a block's UI module meets ([UI modules in JS](Rewrite-1.1.7#the-contract)), with `CoreApi` in place of a host: it exports the JS API major it was built against and a default whose `render()` core calls with an element, the id of the plugin it draws and a signal, and which returns the cleanup, so it never names its own id.
Core calls a plugin's `ui` with the element that the frontend gave `mountPlugin()`, and a frontend's module with the page's element ([The frontend](#the-frontend)):

```ts
export const api = 1;                                // the JS API major it was built against

export default {
  render({ el, core, plugin, signal }: { el: HTMLElement; core: CoreApi; plugin: PluginId; signal: AbortSignal }): () => void { /* draw the plugin, return the cleanup */ }
};
```

So one module draws each plugin of its class, as two documents of blockr.md, each from its own state.
It is free of any framework, as a block's UI is, and may be written in React on the one copy that core ships ([UI modules in JS](Rewrite-1.1.7#react)).
Where [Client-drawn dock and extensions](Rewrite-1.2) has extensions render React components inside the dock's own tree, a plugin's UI renders in a root of its own, which shares no React context with the frontend's and takes its look from blockr.ui's design system ([UI kit and design system for the client](Rewrite-1.7)).
Core's own Edit board plugin cannot, since blockr.ui builds on blockr.core.
It builds on Tailwind CSS instead, as core's other UIs do ([The Edit board plugin](Rewrite-1.1.15#its-look)).

### The frontend

A frontend is a plugin whose class has `frontend`, the module that draws the page, and whose class in R extends `frontend_plugin`.
The module meets the contract of a UI module above, and core calls it with the page's element.
A page has one frontend: the one that the open board holds, or core's basic frontend where it holds none.
A block that `serve()` serves alone is the exception, since core draws it in a card of its own ([Defining a board in R](Rewrite-1.1.3#data-passed-to-serve)).
No board holds core's basic frontend: it draws every board that holds no frontend, and it keeps no state.
A board holds the app's frontend, as it holds the app's other plugins, and core's basic frontend draws it where the app holds none ([Which plugins a board has](#which-plugins-a-board-has)).
So a dock app opens a board made in a core app with the dock's default layout.
An app holds at most one frontend, since `serve()` refuses a second.
Core starts the page with the board's frontend, and starts the board's plugins once the frontend has drawn, as [Drawing the board](Rewrite-1.1.8#starting-the-page) has it.
Every board that the app opens holds the same frontend, so the page never switches to another, and opening a board starts that frontend again, as [Drawing the board](Rewrite-1.1.8#opening-a-board) has it.
A frontend's state holds what it keeps of the board, as the dock's views, their layouts and which view is active, which were the dock board's properties ([The dock board: views and layouts](Rewrite-1.2.1)).
A board that holds the dock, opened in an app without the dock, opens without it, whose package the client names, and with the app's frontend ([Which plugins a board has](#which-plugins-a-board-has)).

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
No board holds it: it saves and opens for every board that holds no storage plugin, and it keeps no state.
A frontend's save and open controls call `core.plugins.storage()`, which gives the `storage` of the open board's storage plugin, or core's own where the board holds none ([What a frontend offers other plugins](#what-a-frontend-offers-other-plugins)).
The storage plugin of blockr.session saves to Connect and opens from it ([Session management as a client extension](Rewrite-1.6)).

An app holds its storage plugin as it holds any other, among the plugins that its script passes to `serve()`:

```r
serve(new_board(blocks = blks), plugins = list(new_dock_plugin(), new_session_plugin()))
```

An app holds at most one storage plugin, since `serve()` refuses a second.
A board holds the app's storage plugin, as it holds the app's other plugins, and saves through core's own where the app holds none ([Which plugins a board has](#which-plugins-a-board-has)).
So a board that a user saved as a download in an app without Connect, which holds no storage plugin, holds session management once it opens in a Connect app, and the page keeps saving to Connect.
A board drops a storage plugin that the app does not hold, as it drops any other such plugin.
So a deployment alone chooses where its pages save, through the plugins its script passes to `serve()` and the packages it names.

The interface holds only what every frontend's save and open controls call, and it can grow once a frontend needs more of every storage plugin.
A storage plugin offers the rest through its own UI, which every frontend places, as session management offers its board list, its versions and its sharing, and its `open()` may show a picker of its own before it resolves.
A storage plugin keeps no state in the board, since the record a board was opened from is the URL's and the plugin's own, as [Session management as a client extension](Rewrite-1.6) has it.
This settles the open question of [Session management as a client extension](Rewrite-1.6#open-questions) on whether storage becomes an interface of core.

### Which plugins a board has

A board holds its plugins in `plugins`, a property of core's board, each under its id, naming its class by the class's id, with its name and its state ([A plugin's state](#a-plugins-state)).
A plugin's id is its name in the list that `serve()` or the board constructor takes, as a block's id is its name among the blocks.
It keeps the rules of every id: it is unique among the board's plugins, and it is not made of digits alone ([Board objects](Rewrite-1.1.1#ids)).
Where the list gives no name, the id is the class's name without `_plugin`, as `dag`, as today's dock names an extension after its class.
So two plugins of one class need names of their own, as two extensions of one class do today.
A board holds as many plugins of a class as the app holds, as two documents of blockr.md, but at most one frontend ([The frontend](#the-frontend)) and one storage plugin ([Storage](#storage)).

The app's plugins are those that the app script passes to `serve()` in `plugins`, which R sends in its reply to `hello`, and they are the plugins of every board that the app opens, the opening board among them, whatever plugins a board held when it was saved or when the script built it.
A board gives only the state of its plugins, whether the script builds it with `new_board()` or a file holds it.
Since a board and a JSON board are one thing, which plugins run is stated outside every board, so that no file sets them.
Opening a board runs them, its frontend among them, and stops every plugin of the board before it, since core starts again as a board opens ([Drawing the board](Rewrite-1.1.8#opening-a-board)), so that a plugin starts again with the state of the board that opens.
So the page is what opening that board in a fresh app would give ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).

As a board opens, the store keeps each of its plugins that the app holds under the same id and of the same class, where a package that the app names registers the class.
Such a plugin keeps the name and the state that the board gives it, and its class's `migrate` brings the state to today's shape ([Board updates](Rewrite-1.1.2#plugins)).
The store drops every other plugin of the board, as it drops a block whose class the block registry lacks, and names it with its class's package, which its class's id gives ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)).
It drops them before it checks or migrates any version, since it drops a plugin for its id or its class, never for its version ([Board updates](Rewrite-1.1.2#plugins)).
So no plugin runs on a board that changed while its package was away, and a board saved afterwards is written without it, as condition 4 of [Board objects](Rewrite-1.1.1#what-must-hold) has it for blocks.

Then the board gets each other plugin of the app whose class a package that the app names registers, under the same id and with the name that the app gives it, with its class's default state.
Where the app holds no frontend, core's basic frontend draws the board, and where it holds no storage plugin, core's own storage plugin saves it.
So the app sets the plugins of every board that it opens, and the page runs, draws and saves a board as a fresh start of the same app would, whatever was open before:

- An app whose plugins hold no frontend draws every board with core's basic frontend, whether its script built the board or `serve()` was given the board's file, and one whose plugins hold no storage plugin saves through core's own.
- A file that `serve()` is given gives only the state of its plugins too, so a core board that today's stack saved, which holds no plugin once converted, gets core's Edit board plugin from the default of `serve()` ([The Edit board plugin](Rewrite-1.1.15#what-serve-gives-by-default)).
- A board saved before an app added the assistant to its plugins gets the assistant as it opens, with its class's default state, as a plugin that `serve()` takes reaches every board today ([Today](#today)).
- A board keeps the state of its DAG and of its documents of blockr.md where the app holds them under the same ids, and gets each other document of the app empty, while it drops a document under an id that the app does not hold.
- A board made in a core app holds no frontend, and opened in a dock app it gets the dock, which lays it out from its default, while a board that holds a frontend of another class drops it for the dock.
- A board saved as a download holds no storage plugin, and opened in a Connect app through session management it gets session management ([Storage](#storage)).
- A board that a startup module names in place of the opening board gets the app's plugins too, so a record that session management opens from a URL as the page starts holds the plugins that the app script passed to `serve()`, each with the state that the record gives it.
- A dock board opened in an app without blockr.dock loses the dock, which the client names, and gets the app's frontend, or core's basic frontend where the app holds none, as in a core app.

No change adds a plugin to the open board or removes one, since the app sets the plugins: a patch changes a plugin's name or its state, and the store refuses one at a plugin's own path, as `/plugins/dag`, which would set or remove the whole plugin ([Board updates](Rewrite-1.1.2#plugins)).
So the app alone decides which plugins run, what draws the page and where it saves, as `serve(plugins = ...)` does today, with no union of the board's plugins and the app's that would need a rule for each clash.
An app that offers a plugin passes it to `serve()`, and what a user adds more of while the app runs, such as another document, lives in the state of one plugin, as the dock's views do.
On a locked board the store refuses renaming a plugin, since the board lock fixes the names of the board's plugins as it fixes its blocks' names, while each plugin locks what it alone governs in its state, as the dock does the arrangement of its panels ([Locked boards and the properties of blocks](Rewrite-1.1.11#plugins-on-a-locked-board)).

### Running a plugin

Besides the store, which calls a plugin class's `migrate` as a board opens and its `update` with every change, core runs a plugin's code in two places: a frontend mounts its class's `ui` where it places the plugin, and core calls its class's `start`.
Core calls `start` for each plugin of the board once the board has opened and the frontend's `render()` has returned, so that what the frontend first shows is evaluated first.
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

Whoever calls `CoreApi.request()` names a plugin of the board by its id, and the message names the plugin's class by the class's id, by which R finds the method.
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

- A change inside it is a patch at a path under the plugin's state, as `/plugins/dag/state/positions/a`.
- The store keeps an edit id for each plugin, as it kept one for each property, which a patch to the plugin names, so that the store refuses the patch where another edit to the plugin came first ([Board updates](Rewrite-1.1.2#deltas)).
- The store checks the state against its class's schema after every change, keeps the inverse patches for undo, and saves the state with the board.
- The store calls a class's `update` once for each of its plugins, with every change it applies, in the same step, and refuses a patch that an `update` returns outside the state of the plugin it was called for ([Board updates](Rewrite-1.1.2#applying-a-delta)).
- Core's command `blockr.core-set_plugin_state` and the commands of the plugin's class change its state, naming the plugin by its id, and everything else changes it through them, which is external control ([Board updates](Rewrite-1.1.2#commands)).
- A JSON board records in `versions` the version of each class whose plugins it holds, by the class's id, and the class's package in `packages`, and the class's `migrate` takes the state of each of its plugins at an older version ([Serialization](Rewrite-1.1.4#migrations)).

Core's command opens every plugin's state to every other plugin, as core's commands open every block's state ([Board updates](Rewrite-1.1.2#commands)).
It takes a plugin's id and patches at paths within the plugin's state, and returns them under the plugin's path, so that the store checks them against the class's schema and calls the class's `update` as it does with any other change:

```ts
await core.commands.run("blockr.core-set_plugin_state", {    // the assistant, moving a block in the DAG
  plugin: "dag",
  patches: [{ op: "replace", path: "/positions/a", value: { x: 40, y: 80 } }],   // applied at /plugins/dag/state/positions/a
}, "assistant");
```

So no part of a plugin's state is closed to other plugins, whether or not its class registers a command for it, and the assistant's tool for it is typed, for each plugin, by the schema of its class's state and described by that schema's `description` keywords, as its tool for a block's state is by the block class's schema.
A class's own commands stay for changes that need more than its schema keeps valid, as the dock adds a view with its layout.
Core's command is not enabled on a locked board, since there only a class's own commands know what the plugin locks ([Locked boards and the properties of blocks](Rewrite-1.1.11#plugins-on-a-locked-board)).

A plugin's module, its `ui` or its `frontend`, follows the plugin's state through `core.store.subscribe()`, as a block's UI follows the block's state through its host, and updates what it shows in place, leaving the input the user is editing, so that a change that another plugin, the assistant or an undo makes shows at once ([UI modules in JS](Rewrite-1.1.7#the-contract)).
So what others may change, such as which view the dock shows, lives in the plugin's state rather than in its module alone, while what only one person's screen needs, such as which block has focus, core holds for the page ([What a frontend offers other plugins](#what-a-frontend-offers-other-plugins)).

Each plugin class gives the state of its plugins a shape of its own, so the dock's views and the layout of another frontend share nothing.
What a plugin keeps about one of core's objects is an entry in its state keyed by the object's id, as the DAG keeps a block's position, so that core adds nothing to blocks for it ([Locked boards and the properties of blocks](Rewrite-1.1.11#what-a-plugin-keeps-about-a-block)).

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
      "a": { "registry_id": "blockr.core-dataset_block", "version": 1, "state": { "dataset": "iris", "package": "datasets" }, "name": "Iris", "locked": null }
    },
    "links": {},
    "stacks": {},
    "options": {},
    "plugins": {
      "dock": { "class": "blockr.dock-dock_plugin", "name": "Dock", "state": { "views": { "main": { "name": "Main", "grid": [{ "block": "a" }, { "plugin": "notes" }] } }, "active": "main" } },
      "dag": { "class": "blockr.dag-dag_plugin", "name": "DAG", "state": { "positions": { "a": { "x": 120, "y": 80 } } } },
      "notes": { "class": "blockr.md-md_plugin", "name": "Notes", "state": { "content": "# Notes" } },
      "report": { "class": "blockr.md-md_plugin", "name": "Report", "state": { "content": "# Report\n\n![Iris](blockr://a)" } }
    }
  }
}
```

### What a frontend offers other plugins

Part of what [The dock's services](Rewrite-1.2.6) gives the dock's extensions, every frontend gives every plugin through `CoreApi`, so a plugin that uses it works under any frontend:

- Notifications, which the frontend draws, core's own among them, such as what the store dropped when a board opened ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)).
- Which block has focus, which the frontend sets and the assistant reads to tell which block the user is looking at ([Assistant as a client extension](Rewrite-1.4)).
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

On `js-state`, the board classes of [blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474) become plugin state: the patches, the schema checks, `update` and `migrate` keep their code, with each state under its plugin's id and each definition under its plugin class's id, rather than under a board class.

### Boards and app scripts from today

- The conversion outside core ([Serialization](Rewrite-1.1.4#files)) turns a dock board into a board that holds the dock plugin, whose state takes the dock board's `views` and `grids`, and one plugin for each extension, under the name the board gave the extension and with the extension's name, whose state takes the extension's, each class at version 1.
  So a board with two documents of blockr.md keeps both, and an app whose plugins hold both under the same ids opens them with their content.
- An app script's `new_dock_board()` keeps working, as a board that holds the state of the dock plugin and of the plugins its `extensions` give, while the script passes those plugins to `serve()`, which [Saved boards and app scripts across the switch](Rewrite-1.2.2) settles in detail.
- An app script that sets storage through `serve(plugins = custom_plugins(manage_project()))` passes blockr.session's storage plugin to `serve()` in a list instead, from where it reaches every board that the app opens.
- An app script that sets code export through `serve(plugins = custom_plugins(generate_flat_code()))`, as blockr.code's README does ([blockr.code README.Rmd#L43-L56](https://github.com/BristolMyersSquibb/blockr.code/blob/72b20d6911496e4edc9ee64db758e70ebf3f50ca/README.Rmd#L43-L56)), passes blockr.code's plugin to `serve()` in a list instead, from where it reaches every board that the app opens, as `serve()` gives it to every board today.
- Either script, for a core board, lists core's Edit board plugin in that list as well, since `custom_plugins()` kept `manage_blocks` among a core board's defaults, while a list that a script passes replaces the default ([The Edit board plugin](Rewrite-1.1.15#boards-and-app-scripts-from-today)).
- An app script that defines a dock extension of its own with `new_dock_extension()` cannot define a plugin class in its place, since a plugin class comes from a package ([A plugin](#a-plugin)).
  Only four of blockr.dock's examples do so, `panel-ops` ([blockr.dock inst/examples/panel-ops/app.R#L79-L87](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/examples/panel-ops/app.R#L79-L87)), `sidebar-menus`, `sidebar-inputs` and `sidebar-owner`, which its browser tests run, and those tests move to the `CoreApi` for tests, where a test registers the plugin classes it needs ([Testing](#testing)).

### Testing

The `CoreApi` for tests that core ships ([Drawing the board](Rewrite-1.1.8#testing)) runs a plugin on a board in a test runner, its `update` and `migrate` included, so testing a plugin, a frontend among them, needs neither R nor a browser.
A test registers the plugin classes it runs through `core.plugins.register()`, as a startup module does, so a class that only a test needs, such as one that drives the dock's panels, needs no package.

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
Both go, since no package adds a type ([A plugin's requests](#a-plugins-requests)): `request()` takes a plugin's id, and core keeps the generic to itself.

Where a board holds a plugin under the id of one of the app's plugins but of another class, the store drops the board's plugin, and the app's takes its id with its class's default state.

On `js-state`, at `1776bf1`, the store reads the app's plugins off the opening board with `openingPlugins()` in `srcts/store/open.ts` ([#L297](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/srcts/store/open.ts#L297), [#L339-L352](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/srcts/store/open.ts#L339-L352)), and `keptPlugins()` and `appPlugins()` in `srcts/store/plugins.ts` match a board against them.
The store takes them from the `plugins` of the reply to `hello` instead, which `R/loaded-reply.R` writes from the plugins that `serve()` takes.
At that commit, `serve.board()` and `serve.character()` refuse `plugins` ([R/utils-serve.R#L70-L80](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/R/utils-serve.R#L70-L80)).

Rewrite 1.2 to 1.8, drafts written before this page, still have the dock's extensions where this page has plugins, and "front-end" where it has "frontend", and follow it as each is revised.

A plugin class's state has two defaults: its constructor's in R, which the plugins of a board that an app script builds take, and `state.default` in JS, which a board's plugin takes where the board opens without it, so its package keeps the two alike.

</details>
