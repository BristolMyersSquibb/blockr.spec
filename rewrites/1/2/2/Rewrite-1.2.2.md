# Saved boards and app scripts across the switch
Status: settled on 2026-11-12. Design for [Client-drawn dock](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock](Rewrite-1.2)): how what users made with today's blockr.dock crosses the switch.
It covers the boards that today's blockr.dock saved, which the conversion in blockr.convert turns into JSON boards that hold the dock plugin's state at version 1.
It also covers the app scripts that call blockr.dock's constructors, through `new_dock_board()` and the rest of what blockr.dock exports for scripts today.
It builds on [Serialization](Rewrite-1.1.4#files) and [Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today), which settle the conversion as a whole, and on [The dock's state: views, folders, grids and card sections](Rewrite-1.2.1), whose `migrate` takes the dock plugin's state from version 1 and whose R functions write a view and its grid.
Each of today's extensions becomes a plugin, whose state the extension's own package takes from the extension's, as [Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today) has it.
This page maps the extension's panels to that plugin's.

## What must hold

1. A board that today's blockr.dock opens converts once, through blockr.convert, into a JSON board, for block classes that have been ported, as condition 5 of [Client-drawn dock](Rewrite-1.2#what-must-hold) asks.
   A dock app opens it with the same views, in their order and with their names and grids, the same active view, the same sections on each card, the same stack colours and dock board option values, and the panels of the plugins that take the place of its extensions.
2. A converted board names nothing of today's stack, neither an R class, a constructor nor an extension's key, so that only the conversion reads today's names.
3. An app script that builds its board with `new_dock_board()`, with views and grids written by `dock_view()`, `dock_grid()`, `panels()`, `group()`, `rail()`, `blk()` and `ext()`, builds a board with the same views, grids, active view and card sections as today, once it makes the changes that the migration notes of blockr.core and blockr.dock list.
4. The migration notes of blockr.dock, a vignette, list every change that a dock app script needs, written so that an AI can apply them, since a function that the new stack replaces goes without an alias ([State in JS](Rewrite-1#migration)).
5. A script that gives its views or grids and a file that today's packages save from that script open into the same dock plugin's state, the script's board through `new_dock_board()` and the file through the conversion and the `migrate` of the dock plugin's class, while a script that gives neither gets the view that the dock adds to a board without views ([The dock's state](Rewrite-1.2.1#starting-on-a-board)).

## Today

A board that today's blockr.dock saves, through the dock's Import and Export or through blockr.session, holds `extensions`, `views` and `grids` beside core's `blocks`, `links`, `stacks` and `options`.
Each is wrapped in its class vector, its payload and, where it has one, its constructor, as every object of today's files is ([R/utils-serdes.R#L47-L95](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/utils-serdes.R#L47-L95)):

- The `views` hold the id of the active view, and each view under its id with its name and its members, the panels it shows, as the panel ids `block_panel-<id>` for a block and `ext_panel-<key>` for an extension.
- The `grids` hold the grid of each view that has one: its `orientation`, `children` and `sizes`, each leaf's `panels` and `active` tab, its `rails` by edge, and `focus` where a panel had focus ([R/dock-grid.R#L1-L32](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L1-L32)).
- The `extensions` hold each extension under its key, which is its name in the list that `new_dock_board()` takes or else its class without `_extension` ([R/dock-board.R#L17-L22](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-board.R#L17-L22)), with its class, its state as the args of its constructor, and that constructor.
- Each block's payload holds the dock's `visible` beside the block's state, the sections that its card shows, such as `"inputs"`.
- Each stack is a dock stack with its `color`, since `new_dock_board()` makes every stack one ([R/dock-stack.R#L171-L192](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-stack.R#L171-L192)).
- The `options` hold the values of the dock's board options, `compact`, `view_tabs` and `sync_rails`, beside core's.

Files have had this shape since blockr.dock 0.1.2, tagged on 2026-07-13.
Until [b66459a](https://github.com/BristolMyersSquibb/blockr.dock/commit/b66459ad4520e9050968276fb985327c58023983) on 2026-08-14, the dock wrote every extension's state empty, so a file of 0.1.2 holds neither the DAG's positions nor the outline's annotations.
A file of blockr.dock 0.1.0 holds one `layout` in place of `views` and `grids`, and today's blockr.dock does not open it: `blockr_deser()` stops with "no applicable method for 'blockr_deser' applied to an object of class "dock_layout"".

Among the app scripts that build dock boards, the CEDX board's in blockr.sandbox runs to 1,227 lines.
It builds ten views with `dock_grid()`, `group()`, `rail()`, `blk()` and `ext()`, and mounts four extensions of three packages, with the assistant as a fifth where its `assistant` argument is `TRUE`.
It closes the output section of every card by setting each block's `visible` attribute ([dev/cedx/board.R#L1220-L1227](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/d4df2e479564d463d267776563929f27cd4bf9a4/dev/cedx/board.R#L1220-L1227)).
A script beside it derives a board of one view from that board through `board_views()`, `board_grids()` and `dock_extensions()` ([dev/cedx/views.R#L70-L78](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/d4df2e479564d463d267776563929f27cd4bf9a4/dev/cedx/views.R#L70-L78)).
Six of blockr.dock's examples pass `new_edit_board_extension()`, and the `rails` example places its panel on a rail with `rail(ext("edit_board"))` ([inst/examples/rails/app.R#L18-L24](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/examples/rails/app.R#L18-L24)).

## Proposal

### Which files cross

The conversion reads what today's packages read, through the `blockr_deser()` methods they have ([Serialization](Rewrite-1.1.4#files)).
So the files that cross are those that today's blockr.dock opens: the files of blockr.dock 0.1.2 and later, up to the last version on main before the switch.
The conversion adds no reader that today's packages lack, so a file of blockr.dock 0.1.0 does not convert, as it does not open today.
Main keeps shipping fixes until the switch ([State in JS](Rewrite-1#migration)).
So a change on main to what the dock writes comes with the same change to the dock's methods for the conversion, and with a file that main wrote among the conversion's fixtures ([Testing](#testing)).

### The dock board

The methods of blockr.dock for the conversion, which it registers on the `blockr_deser()` of blockr.convert ([State in JS](Rewrite-1#migration)), turn a dock board into a board without a class of its own ([Board objects](Rewrite-1.1.1#the-board)).
That board holds the dock plugin's state under `blockr.dock-dock_plugin` at version 1, and the state of the plugin that takes the place of each extension that kept any ([Extensions](#extensions)).
The dock plugin's state at version 1 holds what the dock board holds of its views, in today's shape, and nothing of today's stack:

- Its `views` hold each view under its id, with its `name` and its `members`, in the order that the view shows them.
- Its `active` is the id of the active view.
- Its `grids` hold the grid of each view that has one, under the view's id, as today's file holds it, without `focus`, since only one person's screen needs focus ([Client-drawn dock](Rewrite-1.2#proposal)).
- Its `visible` holds the sections that each card shows, under the block's id, for each block whose payload holds the dock's `visible` ([Serialization](Rewrite-1.1.4#files)).

A panel id names a block's panel as today, as `block_panel-a`.
It names an extension's panel by the id of the class of the plugin that takes the extension's place, as `ext_panel-blockr.dag-dag_plugin`, since no extension's key reaches the new stack (condition 2).
Two extensions that become one plugin, as two documents of blockr.md become one plugin of blockr.md's ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)), leave that plugin one panel, where the first of the two stands in each view and grid.
An extension that no plugin takes the place of leaves no panel ([Extensions](#extensions)).
The conversion drops such panels from each view's members and each grid, as today's `new_dock_board()` drops a member that no block or extension backs and restricts each grid to its view's members ([R/dock-board.R#L117-L118](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-board.R#L117-L118)).

The conversion writes this state as typedjson read it, with each value of length one bare and an empty list as `[]`, as it writes the state of every plugin at version 1 ([Serialization](Rewrite-1.1.4#migrations)).
So the dock plugin class's `migrate` takes either form there, and gives the state that [The dock's state](Rewrite-1.2.1) defines.

The rest of the dock board is core's to convert ([Serialization](Rewrite-1.1.4#files)).
A dock stack's colour becomes the stack's `color`, with three digits written as six.
The values of the dock's board options stay under their ids, at version 1, without their category and label.

A board with two views, the DAG on a rail of the first, a stack, and a card that shows its output alone, converted from a file that blockr.dock 0.2.0 wrote:

```json
{
  "format": 1,
  "packages": { "blockr.core": "0.1.4", "blockr.dock": "0.2.0" },
  "board": {
    "id": "curious_otter",
    "versions": { "blockr.dock-dock_plugin": 1 },
    "name": "Curious otter",
    "blocks": {
      "a": { "registry_id": "blockr.core-dataset_block", "version": 1, "state": { "dataset": "iris", "package": "datasets" }, "name": "Dataset", "locked": null },
      "b": { "registry_id": "blockr.core-head_block", "version": 1, "state": { "n": 3, "direction": "head" }, "name": "Head", "locked": null }
    },
    "links": { "ab": { "from": "a", "to": "b", "input": "data" } },
    "stacks": { "s1": { "name": "Input", "blocks": ["a", "b"], "color": "#ffcc88" } },
    "options": {
      "dark_mode": { "value": "light", "version": 1 },
      "compact": { "value": false, "version": 1 },
      "view_tabs": { "value": false, "version": 1 },
      "sync_rails": { "value": true, "version": 1 }
    },
    "plugins": {
      "blockr.dock-dock_plugin": {
        "views": {
          "main": { "name": "Main", "members": ["block_panel-a", "block_panel-b", "ext_panel-blockr.dag-dag_plugin"] },
          "side": { "name": "Side", "members": "block_panel-b" }
        },
        "active": "side",
        "grids": {
          "main": {
            "orientation": "horizontal",
            "children": [{ "children": [{ "panels": "block_panel-a", "active": "block_panel-a" }, { "panels": "block_panel-b", "active": "block_panel-b" }], "sizes": [0.5, 0.5] }],
            "sizes": 1,
            "rails": { "right": { "position": "right", "panels": "ext_panel-blockr.dag-dag_plugin", "active": "ext_panel-blockr.dag-dag_plugin", "collapsed": true, "size": 300, "collapsed_size": 35 } }
          },
          "side": { "orientation": "horizontal", "children": [{ "panels": "block_panel-b", "active": "block_panel-b" }], "sizes": 1, "rails": [] }
        },
        "visible": { "b": "outputs" }
      }
    }
  }
}
```

The DAG kept no state in this file, so the board holds none for its plugin, which starts from its class's default.

### Extensions

The state of each of today's extensions becomes the state of the plugin of the class that takes its place, at version 1 and taken from the args of the extension's constructor ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)).
The extension's package gives it through a method for the extension's class, which it registers on the `blockr_deser()` of blockr.convert, as blockr.dock registers its own.
That method returns the plugin, which it makes with `new_plugin()` from the extension's state as the file holds it.
So the conversion learns the class's id even where the state is empty, and the board holds nothing for a plugin whose extension kept no state.

The Edit board extension is blockr.dock's own, so blockr.dock gives its method.
It returns core's Edit board plugin, so that the extension's panels become the panels of that plugin, which keeps no state ([The Edit board plugin](Rewrite-1.1.15#boards-and-app-scripts-from-today)).

Where no method gives a plugin, the conversion drops the extension with its panels, and names each such extension in a warning with its class and its package.
That happens where the extension's package gives no method, where the converting session lacks the package, and where an app script defined the extension with `new_dock_extension()`.
A user who installs a package that gives a method converts the file again.

### Opening a converted board

The client opens a converted board as it opens any JSON board ([Board updates](Rewrite-1.1.2#opening-a-board)).
The store runs the `migrate` of the dock plugin's class from version 1, which [The dock's state](Rewrite-1.2.1) gives, and that of every other plugin's class from version 1, which each plugin's package gives.

### App scripts

A script keeps building its board with `new_dock_board()`, which returns a board that `new_board()` builds, holding the dock plugin's state and the plugins of its `extensions` ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)):

```r
new_dock_board(blocks = list(), links = list(), stacks = list(),
               extensions = list(), views = NULL, grids = NULL, folders = list(), active = NULL,
               visible = list(), options = list(), id = NULL, name = NULL)
```

Its arguments are these:

- Its `blocks`, `links`, `stacks` and `options` are those that `new_board()` takes, with no board option by default, since a board holds only the values that a script sets ([Board options and blockr options](Rewrite-1.1.13#board-option-values-in-r)).
- Its `extensions` are the plugins whose state the board holds, each made by a plugin's constructor, as `new_dag_plugin()` makes the DAG's.
  A script may give a plugin a name there, as `list(analysis = new_dag_plugin())`, by which its views and grids place the plugin's panel without the id of the plugin's class, as a script names an extension there today.
- Its `views`, `grids` and `active` are written as today, beside the `folders` that [The dock's state](Rewrite-1.2.1#views-and-folders) adds, and it hands them to `new_dock_plugin()` with each name that the script gives a plugin turned into the id of the plugin's class, so that the dock plugin's state names each plugin by its class alone ([The dock's state](Rewrite-1.2.1#defining-the-state-in-r)).
  A reference to a plugin's panel, written with `plg()`, gives that name or the id of the plugin's class, so the `views` example's `ext("analysis")` ([inst/examples/views/app.R#L10-L23](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/examples/views/app.R#L10-L23)) becomes `plg("analysis")`, with `analysis = new_dag_plugin()` in the example's `extensions`.
  A plugin that a script leaves unnamed has no name, where today's dock names an extension after its class, as blockr.dm's `duckdb-remote-dm` example relies on with `ext("dag")` ([inst/examples/duckdb-remote-dm.R#L227-L247](https://github.com/BristolMyersSquibb/blockr.dm/blob/9a02bd76b2f39595aa656bf21257216ab345b4fb/inst/examples/duckdb-remote-dm.R#L227-L247)), so the migration notes have such a script name the plugin, as `list(dag = new_dag_plugin())`.
- Its `visible` gives the sections that each card shows, by block id, as `list(a = "outputs")`, and it hands that to `new_dock_plugin()` too.
  The argument takes the place of a block's `visible` attribute, which no longer reaches the board, since a block holds nothing beside its state, its name and its `locked` now ([Locked boards and the properties of blocks](Rewrite-1.1.11#block-properties-in-r)).
  So the migration notes move what a script such as CEDX's sets on its blocks into this argument, and the test of condition 5 fails for a script that still sets the attribute.
- Its `id` and `name` are the board's, which it hands to `new_board()`.
  So a script that passes its board's id to `serve()`, as `serve(new_dock_board(...), "my_board")` does, passes it here instead ([Defining a board in R](Rewrite-1.1.3#the-serve-generic)).

The function leaves a stack without a colour where the script gives it none, so such a stack holds `null`, which the dock draws in a default of its own ([Board objects](Rewrite-1.1.1#stacks)).
Today's `new_dock_board()` picks a colour for such a stack through `suggest_new_colors()` and the blockr option `stack_color` ([R/dock-stack.R#L90-L103](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-stack.R#L90-L103)), and both go.
The dock's stack editor keeps suggesting a colour for a stack that the user adds ([Client-drawn dock](Rewrite-1.2#today)).
The function drops `ctor`, `pkg`, `class` and `...`, as `new_board()` does ([Defining a board in R](Rewrite-1.1.3#the-script)).

The rest of what scripts call goes as follows:

| Today | In the new stack |
|---|---|
| `dock_view()`, `dock_grid()`, `panels()`, `group()`, `rail()`, `blk()` and `layout_panel_ids()` | Kept, writing the dock plugin's state, as [The dock's state](Rewrite-1.2.1) has it |
| `ext()` | Dropped in favour of `plg()`, which places a plugin's panel by the name that the script gives the plugin or by the id of its class (above), since the new stack has no extensions |
| `board_views()`, `board_grids()`, `active_view()`, `view_members()`, `view_name()` and `dock_extensions()` | Kept, reading the dock plugin's state and the other plugins of an R board, so that a script can derive one board from another, as CEDX's script of one view does |
| `board_views<-()`, `board_grids<-()`, `active_view<-()`, `view_name<-()`, `dock_extensions<-()` and `stack_color<-()` | Dropped, as core's setters are, since nothing changes a board in R ([Defining a board in R](Rewrite-1.1.3#the-script)) |
| `as_dock_board()` and `is_dock_board()` | Dropped, since no board has a class of its own ([Board objects](Rewrite-1.1.1#the-board)) |
| `new_dock_stack()`, with `as_dock_stack()`, `is_dock_stack()`, `stack_color()` and `suggest_new_colors()` | Dropped, since core's `new_stack()` keeps a stack's colour ([Board objects](Rewrite-1.1.1#stacks)) |
| `new_edit_board_extension()` | Dropped, since core's Edit board plugin runs by default, so a script names that plugin only where a grid places its panel ([The Edit board plugin](Rewrite-1.1.15#what-serve-gives-by-default)) |
| `new_compact_option()`, `new_view_tabs_option()` and `new_sync_rails_option()` | Kept, each taking its value alone ([Board options and blockr options](Rewrite-1.1.13#board-option-values-in-r)) |
| `dock_board_options()` | Dropped, since a board holds only the values that a script sets ([Board options and blockr options](Rewrite-1.1.13#board-option-values-in-r)) |
| `navbar_item()`, `custom_navbar()`, `default_navbar_items()` and the `navbar` that `serve()` passes on | [The dock's navbar](Rewrite-1.2.5)'s |
| `new_dock_extension()` and the rest of the extension API | Replaced by plugin classes, which only a package defines ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)) |

The migration notes for dock app scripts are a vignette of blockr.dock's, beside those of core ([blockr.core#445](https://github.com/BristolMyersSquibb/blockr.core/issues/445)), so that they ship with the package that the scripts call.
The vignette says how a board that today's dock saved converts through blockr.convert, and lists each departure of this page from today, with what takes the place of each function that goes, written so that an AI can apply it to a script ([State in JS](Rewrite-1#migration)).

### Testing

The conversion's tests hold files that today's packages wrote, each beside the JSON board that the conversion writes for it.
They are a file of each of blockr.dock's examples, written by blockr.dock 0.1.2 and by main at the switch, and a file of the CEDX board, once the packages it uses have been ported.
The client's tests open each JSON board with the dock plugin's class, and check its views, their names and order, their grids, the active view, the sections of each card and the stacks' colours against what today's dock shows for the file.
The script of each example that gives its views or grids and that of the CEDX board, changed as the migration notes say, then open into the same dock plugin's state as the conversion of the file that today's packages saved from the same script (condition 5).

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's code, at `655e323`: the serializer and the `blockr_deser()` methods of the dock board, its views, grids and extensions are in `R/utils-serdes.R`, that of a dock stack in `R/dock-stack.R`, and the pruning of views and grids on construction is `initialise_views()` in `R/dock-board.R`, with `drop_unknown_members()` in `R/dock-view.R` and `restrict_grids_to_views()` in `R/dock-grid.R`.
A package registers a method on blockr.convert's generic with roxygen's `@exportS3Method blockr.convert::blockr_deser`, which R registers once blockr.convert loads, so blockr.dock needs blockr.convert only in `Suggests`.
The `blockr_deser()` method of the dock board passes the version of blockr.dock that the file records down as `producer_version`, but no method reads it there, since today's dock reads one shape.
A dock board with no grid for a view writes none, so the view takes a default grid over its members, as `blockr_ser.dock_grids()` drops a grid that is `NULL` ([R/utils-serdes.R#L69-L75](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/utils-serdes.R#L69-L75)).

Written with typedjson 0.1.2, as core's Export writes it, a view's members come out as an array of arrays of one id each, as `[["block_panel-a"], ["block_panel-b"]]`, a grid's `sizes` of one ratio as `1.0`, a leaf's one panel as a string, and a grid without rails as `"rails": []`.
The conversion writes the members as one array of ids.

The CEDX board sets its cards' sections in `cedx_outputs_hidden()` ([dev/cedx/board.R#L1220-L1227](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/d4df2e479564d463d267776563929f27cd4bf9a4/dev/cedx/board.R#L1220-L1227)), passes `c(dock_board_options(), new_board_options(...))` as its options ([#L1196-L1202](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/d4df2e479564d463d267776563929f27cd4bf9a4/dev/cedx/board.R#L1196-L1202)), and mounts the DAG, the outline and slides of blockr.outline, the control bridge of blockr.viz and, with `assistant = TRUE`, the assistant ([#L1167-L1177](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/d4df2e479564d463d267776563929f27cd4bf9a4/dev/cedx/board.R#L1167-L1177)).
Its script of one view serves its board with `serve(plugins = custom_plugins(c(ai_ctrl_block(), manage_project())))` ([dev/cedx/views.R#L84-L91](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/d4df2e479564d463d267776563929f27cd4bf9a4/dev/cedx/views.R#L84-L91)), which core's migration notes cover ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)).

Today's `panel_id_map()` and `resolve_panel_ids()` resolve the name that a script gives an extension ([R/dock-view.R#L465-L521](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-view.R#L465-L521)), and the names of the plugins in `extensions` resolve the same way.
Where today's `check_panel_refs()` refuses a reference that names neither a block nor an extension of the board, R refuses no reference to a plugin, since it may name the class of a plugin that `serve()` adds, and the dock removes a panel of a plugin that the app does not run as it starts ([The dock's state](Rewrite-1.2.1#starting-on-a-board)).

</details>
