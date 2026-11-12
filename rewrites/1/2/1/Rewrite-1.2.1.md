# The dock's state: views, folders, grids and card sections
Status: settled on 2026-11-11. Design for [Client-drawn dock](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock](Rewrite-1.2)): the dock plugin's state, which holds the dock's views, the folders that group them in the navigation, each view's grid, which view is active and which sections of each block's card show.
It covers the commands that change that state, the `update` and the `migrate` of the dock plugin's class, the R functions that write the state for an app script, and how the client turns a grid into dockview's layout and back.
It builds on [Plugins](Rewrite-1.1.12#a-plugins-state) and [Board updates](Rewrite-1.1.2#plugins).
How boards saved today reach the dock plugin's state at version 1, through the conversion in blockr.convert, and how today's app scripts keep working are [Saved boards and app scripts across the switch](Rewrite-1.2.2)'s, while this page gives the `migrate` that brings that state to its own shape.
How the navbar draws the views and folders is [The dock's navbar](Rewrite-1.2.5)'s, and how a card draws its sections is [Block cards in the dock](Rewrite-1.2.7)'s.

## What must hold

Conditions 1 and 2 of [Client-drawn dock](Rewrite-1.2#what-must-hold) rest on this page, through these:

1. The dock's state holds what a board needs to open as it was saved: every view and folder with its id, its name and its place in the navigation, each view's grid, which view is active, and which sections each card shows.
   It holds nothing that only one person's screen needs, such as which block has focus or which folders are open in the navigation.
2. A view shows the panels that its grid places, each once, and nothing else decides which panels a view shows.
3. No change of arrangement reaches R: the dock writes what a gesture changed into its state in the client, through core's deltas.
4. No board depends on dockview: a grid is the dock's own format, with its sizes as ratios, so a board opens unchanged across dockview's releases and at any size of window.
5. Removing a block takes its panels out of every view and its entry out of the card sections, in the same step, which one undo takes back.
6. Folders group and order the navigation alone, at any depth, and removing a folder removes no view.
7. An app script writes views, folders and grids in R, as today, and R turns them into the dock's state as the app starts, with every id.
8. A board that holds no state for the dock opens with one view, with the default grid over its blocks and the app's plugins that have a `ui`, and no view shows a panel that the dock cannot draw.

## Today

A dock board keeps its `views`, `grids` and `extensions` beside core's objects ([R/dock-board.R#L55-L79](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-board.R#L55-L79)).
A view holds its members, the panels it shows, and a name, under an id that never changes, and the views together hold which view is active ([R/dock-view.R#L1-L45](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-view.R#L1-L45)).
A grid holds a view's splits, with sizes as ratios, its tab groups, each with the panel it shows, its rails, and the panel that has focus ([R/dock-grid.R#L1-L32](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L1-L32)).
The members decide which panels a view shows and the grid only arranges them, so the dock reconciles the two wherever it reads a view: a member that the grid omits gets a default place, and a panel in the grid that is no longer a member is dropped ([R/dock-grid.R#L461-L497](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L461-L497)).
The two have different writers.
R changes the members through the `views$mod` grammar of the board's updates, while the grid changes only when the browser's settled layout reaches R's grid mirror, which stores it where it differs from the stored grid by more than a tolerance ([R/board-server.R#L435-L520](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/board-server.R#L435-L520)).
The views form one flat list, in the order that the views menu shows and the user drags ([R/dock-view.R#L184-L199](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-view.R#L184-L199)).

## Proposal

### The state

The board holds the dock plugin's state under the class's id, at `/plugins/blockr.dock-dock_plugin` ([Plugins](Rewrite-1.1.12#a-plugins-state)), in this shape, with illustrative type names:

```ts
interface DockState {
  views: Record<ViewId, View>;           // every view, under its id
  folders: Record<FolderId, Folder>;     // every folder, under its id
  active: ViewId | null;                 // the active view, which a board opens on, or null while the state holds no view
  visible: Record<BlockId, Section[]>;   // the sections of a block's card that show, where they are not both
}

interface View {
  name: string;                          // "Adverse events", which the user picks
  folder: FolderId | null;               // the folder it sits in, or null at the top
  index: string;                         // "a1", which orders it among the views and folders of its folder
  grid: Grid;                            // which panels it shows, and where (Grids, below)
}

interface Folder {
  name: string;
  folder: FolderId | null;
  index: string;
}

type Section = "inputs" | "outputs";
```

A board with two views, one of them in a folder:

```json
{
  "views": {
    "overview": {
      "name": "Overview", "folder": null, "index": "a0",
      "grid": {
        "orientation": "horizontal",
        "children": [
          { "panels": [{ "block": "a" }, { "block": "b" }], "active": { "block": "b" } },
          { "children": [
              { "panels": [{ "block": "c" }], "active": { "block": "c" } },
              { "panels": [{ "plugin": "blockr.md-md_plugin" }], "active": { "plugin": "blockr.md-md_plugin" } }
            ],
            "sizes": [0.6, 0.4] }
        ],
        "sizes": [0.3, 0.7],
        "rails": {
          "left": { "panels": [{ "plugin": "blockr.dag-dag_plugin" }], "active": { "plugin": "blockr.dag-dag_plugin" },
                    "collapsed": false, "size": 260, "collapsed_size": 35 }
        }
      }
    },
    "ae": {
      "name": "Adverse events", "folder": "safety", "index": "a0",
      "grid": { "orientation": "horizontal", "children": [{ "panels": [{ "block": "d" }], "active": { "block": "d" } }], "sizes": [1] }
    }
  },
  "folders": { "safety": { "name": "Safety", "folder": null, "index": "a1" } },
  "active": "overview",
  "visible": { "c": ["outputs"] }
}
```

The view Overview shows a tab group of `a` and `b`, which shows `b`, in its left 30%, and in the rest `c` above blockr.md's document, with the DAG on a rail at its left edge.
The folder Safety follows it at the top and holds the view Adverse events, and the card of `c` shows its output alone.

### Views and folders

Every view and every folder has an id that never changes and a name that the user picks, as every object that others refer to has ([Principles](Principles#an-object-is-known-by-an-id-that-never-changes-and-its-name-is-only-a-label)).
The dock mints the id of a view or folder it adds as the client mints every id, in the shape that the blockr option `rand_id` names, and R draws the id of each one that an app script leaves out ([Board objects](Rewrite-1.1.1#ids)).

Unlike today's view, a view keeps no members beside its grid, since its grid alone says which panels it shows.
Today's members and grid had two writers whose results had to be reconciled, while here the store is the only writer, and one delta changes the blocks and the grids together ([Board updates](Rewrite-1.1.2#applying-a-delta)).

Folders are a departure from today's flat list of views, so that related views can be grouped.
A folder holds views and other folders, at any depth, and only groups and orders the navigation: a view shows its own grid whatever folder it sits in, and the active view is always a view.
Each view and folder names the folder it sits in, or `null` at the top, and its `index` orders it among the views and folders of that folder, by comparing the strings, so that a folder can sit between two views.
The dock makes a key between two neighbours with `generateKeyBetween()` of [fractional-indexing](https://github.com/rocicorp/fractional-indexing), as tldraw orders its pages and its nested shapes ([TLPage.ts#L34-L36](https://github.com/tldraw/tldraw/blob/1b1cd9f4029f66e8ba1fe53d8b5f4acec2df08a6/packages/tlschema/src/records/TLPage.ts#L34-L36), [TLBaseShape.ts#L61-L72](https://github.com/tldraw/tldraw/blob/1b1cd9f4029f66e8ba1fe53d8b5f4acec2df08a6/packages/tlschema/src/shapes/TLBaseShape.ts#L61-L72)) and as Figma describes ([Realtime editing of ordered sequences](https://www.figma.com/blog/realtime-editing-of-ordered-sequences/)).
So moving a view or folder changes only its own `folder` and `index`, and undo sets exactly those back, while a list of ids would have undo change whatever the list holds at an index by then ([Board updates](Rewrite-1.1.2#undo)).
A view's path also stays `/plugins/blockr.dock-dock_plugin/views/{id}` wherever it sits in the navigation.

Removing a folder moves the views and folders it holds up into the folder above, in the removed folder's place, so that removing a folder never removes a view.
No folder sits in itself or in a folder inside it, and removing the last view is refused, as today ([R/dock-view.R#L1034-L1041](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-view.R#L1034-L1041)).
Which folders are open in the navigation stays on the screen and out of the board, since only that screen needs it.
The same holds for which block has focus, which the dock sets in `CoreApi.focus` ([Plugins](Rewrite-1.1.12#what-a-frontend-offers-other-plugins)).

### Grids

A view's grid has the shape of today's `dock_grid`, without its `focus`, which only one person's screen needs ([Client-drawn dock](Rewrite-1.2#proposal)):

```ts
interface Grid {
  orientation: "horizontal" | "vertical";   // how the top split divides, while each split inside divides the other way
  children: Node[];                         // what the top split holds, in order
  sizes: number[];                          // the share of each child, ratios that sum to 1
  rails?: { left?: Rail; right?: Rail };    // its rails, by the edge each sits on
}

type Node = Split | TabGroup;

interface Split {
  children: Node[];
  sizes: number[];
}

interface TabGroup {
  panels: Panel[];                          // its tabs, in order
  active: Panel;                            // the panel it shows
}

interface Rail {
  panels: Panel[];
  active: Panel;
  collapsed: boolean;                       // whether it shows its tabs alone
  size: number;                             // its width in pixels when open, 260 by default
  collapsed_size: number;                   // its width when collapsed, 35 by default
}

type Panel = { block: BlockId } | { plugin: PluginClassId };
```

A split divides the other way from the split it sits in, as dockview's own grid does, so a grid stores the direction of its top split alone ([R/dock-grid.R#L12-L25](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L12-L25)).
Its shares are ratios, so that a board opens the same in any window, while a rail's widths are pixels, since a rail is sized against the dock rather than as a share of a split ([R/dock-rail.R#L10-L15](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-rail.R#L10-L15)).
A view that a script or a converted file gives no grid of its own gets the default grid over its panels: the plugins' panels in one tab group, beside the blocks' panels in another, as today's `default_grid()` does ([R/dock-grid.R#L760-L775](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L760-L775)).
A grid places each panel once, across its splits and its rails, since it says where each panel goes ([R/dock-grid.R#L217-L235](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L217-L235)).
Every view offers a rail on its left and its right edge, which shows only while it holds panels, and a grid holds a rail where it holds panels or where its width or collapse differs from the default, as today ([R/dock-rail.R#L239-L244](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-rail.R#L239-L244)).
Top and bottom rails stay out, as today, since the top edge is where every tab group's tabs sit ([R/dock-rail.R#L24-L30](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-rail.R#L24-L30)), and so do dockview's floating groups and popout windows, which today's dock does not offer either.

A panel shows the card of a block that the board holds, as `{ "block": "a" }`, or the `ui` of a plugin of the app, as `{ "plugin": "blockr.dag-dag_plugin" }`, which the dock mounts with `mountPlugin()` ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)), and its tab shows the block's name or the plugin's.
A grid names a panel by an object, in place of today's strings `block_panel-<id>` and `ext_panel-<key>`, since an object needs no parsing.
An object also leaves room for a plugin's panel per block, which [Places the dock offers plugins](Rewrite-1.2.4#places-besides-the-panel) leaves for later.
A string could join the two ids only with a separator, and a block id may hold any character ([Board objects](Rewrite-1.1.1#ids)).
A block or a plugin has at most one panel in a view, and may have one in several views, where core mounts its UI in each ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).

### Card sections

The state's `visible` holds, by block id, the sections of the block's card that show, `inputs`, `outputs` or both, as today's dock keeps them on each block ([Locked boards and the properties of blocks](Rewrite-1.1.11#what-a-plugin-keeps-about-a-block), [R/plugin-block.R#L38-L40](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L38-L40)).
A block without an entry shows both, as today, and the command that sets a card's sections removes the entry where both show, so that the state lists only the cards that hide a section.
A block that a command copies gets no entry, unless the command adds one in the same delta.
Today's third section, `ctrl`, which shows what a `ctrl_block` plugin adds to a card, goes with that plugin ([Plugins](Rewrite-1.1.12#today)), and plugins add no sections to a card ([Places the dock offers plugins](Rewrite-1.2.4#places-besides-the-panel)).

### Commands

The dock registers a command for each operation on its state, whose description and args describe it to menus and to the assistant's tools ([Board updates](Rewrite-1.1.2#commands)), while core's `blockr.core-set_plugin_state` sets any part of the state on a board that is not locked, which the schema keeps valid ([Plugins](Rewrite-1.1.12#a-plugins-state)).
A command that changes a view's grid replaces the grid whole, so that undo puts back the grid that was there, where a patch inside it would name an index that may hold something else by then ([Board updates](Rewrite-1.1.2#undo)).

| Command | Args | What it does |
|---|---|---|
| `blockr.dock-add_view` | `name`, `folder`, `before`, `grid` | Adds a view under a new id, named "View N", with N one more than the views there are, where no `name` is given, with an empty grid where no `grid` is given, at the end of its folder or before the view or folder that `before` names, and makes it the active view, as the views menu does today ([R/board-server.R#L1169-L1204](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/board-server.R#L1169-L1204)) |
| `blockr.dock-remove_view` | `view` | Removes a view, refusing the last one, and makes the first view of the navigation active where the view it removes was |
| `blockr.dock-rename_view` | `view`, `name` | Renames a view |
| `blockr.dock-move_view` | `view`, `folder`, `before` | Moves a view into a folder, or to the top, before the view or folder that `before` names or at the end |
| `blockr.dock-activate_view` | `view` | Makes a view the active one |
| `blockr.dock-add_folder` | `name`, `folder`, `before` | Adds a folder under a new id, placed as `blockr.dock-add_view` places a view |
| `blockr.dock-remove_folder` | `folder` | Removes a folder and moves what it holds up into its place |
| `blockr.dock-rename_folder` | `folder`, `name` | Renames a folder |
| `blockr.dock-move_folder` | `folder`, `into`, `before` | Moves a folder into another, or to the top, refusing a folder inside itself |
| `blockr.dock-add_panel` | `view`, `panel`, `near`, `side`, `rail` | Places a panel in a view that does not show it: in or beside the tab group of the panel `near` names, on the side that `side` names, `within`, `left`, `right`, `above` or `below`, on the rail that `rail` names, or at the default place (below), as the tab group that shows it |
| `blockr.dock-remove_panel` | `view`, `panel` | Takes a panel out of a view, as closing its tab does |
| `blockr.dock-move_panel` | `view`, `panel`, `near`, `side`, `rail` | Moves a panel within a view, placed as `blockr.dock-add_panel` places one |
| `blockr.dock-resize_panel` | `view`, `panel`, `size` | Sets the size of the tab group that holds a panel: its share of the split that holds it, a ratio between 0 and 1, with the other children sharing the rest in proportion, or, for a rail, its width in pixels |
| `blockr.dock-activate_panel` | `view`, `panel` | Makes a tab group or rail show the panel |
| `blockr.dock-show_panel` | `panel` | Shows a panel in the active view: has its tab group show it where the view holds it, and adds it at the default place where the view does not, as blockr.dag and the slides of blockr.outline reveal a block today ([blockr.dag R/srv.R#L90-L112](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/srv.R#L90-L112)) |
| `blockr.dock-set_grid` | `view`, `grid` | Sets a view's whole grid, as the dock does after a gesture (below) |
| `blockr.dock-collapse_rail` | `view`, `edge`, `collapsed` | Collapses a view's rail on the edge that `edge` names, or opens it, on every view at once while the board option `sync_rails` is on ([R/board-options.R#L155-L201](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/board-options.R#L155-L201)) |
| `blockr.dock-set_sections` | `block`, `sections` | Sets the sections of a block's card that show |

Three of them take no undo step, since they change only what the user looks at, as a step that sets only board option values takes none ([Board updates](Rewrite-1.1.2#undo)).
The commands `blockr.dock-activate_view`, `blockr.dock-activate_panel` and `blockr.dock-collapse_rail` have `undo: false`, so that a user who switches views and then undoes takes back the last edit rather than the switch, while their deltas are saved as any others.
Every other command of the dock's is one undo step, an arrangement made with a gesture among them.

The default place of a panel in a view is a new tab, which it shows, in the last tab group of the view's splits that holds no plugin's panel, in reading order, or a new tab group at the end of the top split where every tab group holds one, with the mean of its siblings' shares ([R/dock-grid.R#L478-L497](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L478-L497)).
So a block's panel never covers the DAG it was added from, as today, but for today's preference for the tab group that last had focus, which only one person's screen knows ([R/utils-ui.R#L130-L167](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/utils-ui.R#L130-L167)).
A menu that adds a block where the user points, such as a tab group's "+", gives the place in its command's own delta instead.

### The `update`

The dock plugin's class gives core an `update`, which the store calls with every change it applies, undos included, and whose patches join the same step ([Board updates](Rewrite-1.1.2#applying-a-delta)):

1. For each block that the delta removes, it takes the block's panel out of every grid that places it, drops each tab group, rail and split that this leaves empty, gives the shares of the dropped ones to their siblings in proportion, makes a tab group whose shown panel went show its first panel, and drops the block's entry in `visible`.
2. For each block that the delta adds, it places the block's panel in the active view at the default place, unless one of the delta's own patches places it in a view already, as today's dock adds a new block to the active view ([R/dock-board.R#L345-L363](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-board.R#L345-L363)).
3. Where a delta's own patches leave `active` naming no view, it makes the first view of the navigation active.
   Where they leave a view or folder naming a folder that the state lacks, it moves the view or folder up into the folder that held the removed one, which the board before the delta gives.

It reads only the delta and the board, never the screen, so that every peer that applies a change computes the same patches.
Only patches that someone sets with core's command can leave what the third rule repairs, since the dock's own commands leave nothing for it.

### Drawing a view

1. To draw the active view, the dock turns its grid into dockview's layout with `gridToLayout()`, ported from today's `grid_to_tree()` ([R/dock-layout.R#L276-L323](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-layout.R#L276-L323)): a dockview group for each tab group, a dockview edge group for each rail, and a dockview panel for each panel.
2. After each gesture that changes the arrangement, such as a drop, a released sash, a moved or closed tab, another tab shown, or a rail collapsed, opened or resized, the dock reads dockview's layout back into a grid with `layoutToGrid()`, ported from `tree_to_grid()` ([R/dock-layout.R#L325-L369](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-layout.R#L325-L369)).
3. It compares that grid with the stored one, ignoring shares that differ by less than the blockr option `dock_grid_size_tol`, 0.005 by default ([R/dock-grid.R#L293-L300](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L293-L300)), so that a window resize, which jitters the shares, changes nothing.
4. Where only the panel that a tab group or rail shows or a rail's collapse changed, it runs `blockr.dock-activate_panel` or `blockr.dock-collapse_rail`, which take no undo step, and where anything else changed, `blockr.dock-set_grid`, which takes one, as dragging a tab into another tab group, which shows it there, does.

A gesture commits once, when the user lets go, as [Board updates](Rewrite-1.1.2#undo) asks of every input that changes with every pointer move.
A rail keeps its stored width across a change in the dock's own width, since dockview narrows a rail that a narrow dock cannot hold and leaves it narrow, as today's grid mirror has it ([R/dock-grid.R#L419-L444](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L419-L444)).
Where the active view's stored grid changes otherwise, through an undo or another origin's command, the dock brings dockview to it by moving its panels, so that what core mounted in them stays mounted (notes).

In a window narrower than the blockr option `narrow_breakpoint`, the dock draws a view's tab groups and rails stacked in one column, each as tall as the wide grid makes it, up to the blockr option `narrow_group_fraction` of the window, as today ([R/dock-grid.R#L534-L630](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L534-L630)).
It reads nothing back there, so the board keeps its wide grid, while a command changes the stored grid as on a wide screen and the column follows.

### Starting on a board

The default of the dock plugin class's state holds no view, `{ "views": {}, "folders": {}, "active": null, "visible": {} }`, since the default of a plugin class's state is one value, which cannot list a board's blocks ([Plugins](Rewrite-1.1.12#a-plugin)).
The dock's state holds no view where the board was made in a core app, where it is a core board that today's stack saved and the conversion turned into a JSON board, or where its app script gives the dock neither views nor grids (below).

As the dock starts on a board, before it first draws, it applies one delta of its own where the state needs one, with the origin `blockr.dock-dock_plugin` and `undo: false` ([Board updates](Rewrite-1.1.2#undo)):

1. Where the state holds no view, it adds one, named "Page", and makes it active, with the default grid over the panels of the board's blocks and of the app's plugins whose class has a `ui` (Grids, above).
2. It removes every panel that it cannot draw, that of a plugin that the app does not run or whose class has no `ui`, as the store drops the state of a plugin that the app does not run as the board opens ([Board updates](Rewrite-1.1.2#plugins)).

So undo never takes the user back to an empty page or to a panel that the app cannot draw.
A fresh start of the same app takes the same step on the same board, so the page is what a fresh start would give ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).
A panel of a block that the board lacks needs no such step, since the store drops such a block as a delta removes it, through the class's `update` (above).

### The migration from version 1

A board that the conversion wrote holds the dock plugin's state at version 1, in today's shape ([Saved boards and app scripts across the switch](Rewrite-1.2.2#the-dock-board)): its views with their members, its `grids` beside them, its panels as the strings `block_panel-<id>` and `ext_panel-<id>`, the latter naming a plugin's class, and each value of length one bare, as typedjson read it.
The `migrate` of the dock plugin's class takes that state to the shape of this page, which is version 2 ([Board updates](Rewrite-1.1.2#plugins)):

1. It reads each value of length one as an array where this page's shape has one, as `"sizes": 1` and `"panels": "block_panel-a"`, and `"rails": []` as a grid without rails.
2. It turns each view's members and grid into one grid, as today's dock reads a view: the grid restricted to the members, each member that the grid lacks in a tab group of its own at the end of the top split, and the default grid over the members where the view has no grid (Grids, above) ([R/dock-grid.R#L725-L775](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L725-L775)).
3. It names each panel by an object, by the prefix of its id, as `block_panel-a` becomes `{ "block": "a" }` and `ext_panel-blockr.dag-dag_plugin` becomes `{ "plugin": "blockr.dag-dag_plugin" }`, and drops a rail's `position`, which the rail's edge gives.
4. It puts every view at the top, with an `index` in the order of the views, and gives the state no folders.
5. It names a view without a name after its id, as today's views menu labels one ([R/dock-view.R#L355-L366](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-view.R#L355-L366)), and keeps `active` and `visible`, with each value of `visible` as an array.

R applies the rule of the second step to an app script's views too (below), so that a script and the file that today's packages save from it give the same grids, as [Saved boards and app scripts across the switch](Rewrite-1.2.2#what-must-hold) asks.

### Defining the state in R

An app script writes the dock's state through `new_dock_board()`, which [Saved boards and app scripts across the switch](Rewrite-1.2.2#app-scripts) keeps for today's scripts, with its `views`, `grids` and `active` as today and its `visible`, which takes the place of a block's `visible` attribute.
It hands them to the dock plugin's constructor, with the `folders` that this page adds:

```r
new_dock_board(
  blocks = c(a = new_dataset_block(), b = new_head_block(), d = new_head_block()),
  views = list(
    overview = dock_view(c("a", "b", ext("blockr.dag-dag_plugin")), name = "Overview"),
    ae = dock_view("d", name = "Adverse events", folder = "safety")
  ),
  grids = list(overview = dock_grid(c("a", "b"), ext("blockr.dag-dag_plugin"), sizes = c(0.3, 0.7))),
  folders = list(safety = dock_folder("Safety")),
  active = "overview",
  visible = list(b = "outputs")
)

new_dock_plugin(views = NULL, grids = NULL, folders = list(), active = NULL, visible = list())   # its args, with their defaults
```

A view is written with `dock_view(members, name = NULL, folder = NULL)`, as today with the folder it sits in added, and a folder with `dock_folder(name, folder = NULL)`.
A grid is written with `dock_grid()`, `panels()`, `group()` and `rail()`, as today ([R/dock-grid.R#L809-L1008](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L809-L1008)).
A grid or a view's members name a block's panel by the block's id or `blk()`, and a plugin's by `ext()`, which takes the id of the plugin's class ([Saved boards and app scripts across the switch](Rewrite-1.2.2#app-scripts)), while R resolves a bare id to a block first, as today ([R/dock-view.R#L1237-L1262](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-view.R#L1237-L1262)).

R turns them into the state once, as the script runs, by today's rules: each view's grid comes from its members and its grid by the second step of the migration from version 1 (above), and a script that gives grids alone gets a view for each grid, with the grid's panels as its members ([R/dock-board.R#L81-L125](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-board.R#L81-L125)).
R draws the id of each view and folder that the script leaves out, names a view without a name after its id, as today's views menu labels one ([R/dock-view.R#L355-L366](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-view.R#L355-L366)), writes each `index` in the order that the script gives, makes the first view active where the script names none, and writes the state by the schema of the dock plugin class's state ([Plugins](Rewrite-1.1.12#a-plugin)).
Where the script gives neither views nor grids, R writes no view, and the dock adds one as it starts (Starting on a board, above), so that a board without views gets its view from one place, the client, which alone knows which plugins have a `ui`.
It refuses, as the script runs, a grid that places a panel twice or names a block that the board lacks, sizes that are not positive, and a folder that sits in itself, naming each, so that a broken layout fails where it is written, as today's `validate_dock_grid()` does ([R/dock-grid.R#L180-L238](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L180-L238)).

### On a locked board

On a locked board, the store applies a patch inside the dock's state and leaves its lock to the dock's commands, which lock what the dock alone keeps, as today ([Locked boards and the properties of blocks](Rewrite-1.1.11#plugins-on-a-locked-board)):

- A reader still switches views, has a tab group show another panel, and opens or collapses a rail.
- No command adds, renames, moves or removes a view or a folder, adds or removes a panel, or sets a card's sections, as a locked card offers no toggle today ([R/plugin-block.R#L128-L137](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L128-L137)).
- No command moves or resizes a panel unless a deployment leaves that to readers through the blockr options `lock_rearrange` and `lock_resize`, as today ([R/utils-dock.R#L311-L343](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/utils-dock.R#L311-L343)), so `blockr.dock-set_grid` refuses a grid that differs from the stored one in more than the lock leaves open.

Core's `blockr.core-set_plugin_state` is not enabled on a locked board ([Plugins](Rewrite-1.1.12#a-plugins-state)), so nothing changes the dock's state there past the dock's own commands.

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's code, at `655e323`, maps as follows: the grid's shape and its checks are `dock-grid.R`, which `canonicalize_grid()`, `validate_dock_grid()`, `prune_tree()` and `append_default_leaves()` serve as the client's checks, its pruning in `update` and its default place; the rails are `dock-rail.R`; the conversions are `grid_to_tree()`, `tree_to_grid()`, `rails_to_edges()` and `edge_to_rail()` in `dock-layout.R`; the views, their ids and names are `dock-view.R`, whose `views$mod` grammar the commands replace verb for verb, `add`, `rm`, `move`, `resize` and `select`, with the hints `near`, `side` and `rail` ([R/dock-view.R#L1098-L1107](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-view.R#L1098-L1107)); and placement is `hint_to_position()` in `panel-ops.R` and `determine_panel_pos()` in `utils-ui.R`.
The `size` hint that `add` records today for a later pass goes, since nothing reads it.

Dockview's group state names a group's panels `views` and the one it shows `activeView`, which `layoutToGrid()` reads into a tab group's `panels` and `active`.
Dockview addresses a split through a member panel, so `near` names a panel, while a rail's dockview group takes the id `rail-left` or `rail-right`, so that a position names it without the tree ([R/dock-layout.R#L247-L252](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-layout.R#L247-L252)).
Dockview needs a string id for each panel, which the dock derives from the panel, such as `JSON.stringify()` of it, since the grid names none.
Today's `grid_to_tree()` gives a node its ratio as its size and the root a size of 1, which dockview lays out in proportion.
Bringing dockview to a changed grid moves its panels with `moveGroupOrPanel()`, which keeps a panel's mounted content, rather than calling `fromJSON()`, which disposes and recreates every panel, as the prototype's findings in the notes of [Client-drawn dock](Rewrite-1.2) record.
On a locked board the dock passes dockview `locked` where resizing is locked and `disableDnd` where rearranging is, as today, while today's dock notes that dockview's lock did not reach edge groups ([dockview#1671](https://github.com/dockview/dockview/issues/1671)), an issue since closed.

The dock's commands write grids in their canonical form, which `gridToLayout()` draws without a repair: shares that sum to 1 in each split, no empty tab group, rail or split, and a tab group's or rail's `active` among its panels.
A patch set with core's command can leave a grid otherwise, which the schema cannot refuse, so `gridToLayout()` draws such a grid all the same: a tab group shows its first panel where `active` names none of them, a split divides evenly where its `sizes` do not fit its children, and a panel that a grid places twice shows where it comes first.
It draws a folder that sits in itself, which only such a patch can make, at the top.

The dock takes its step on starting within the `render()` of its frontend's module, which may be async, and which core awaits before it starts the scheduler, so that the first paint shows the default view ([Drawing the board](Rewrite-1.1.8#starting-the-page)).

The dock makes a new `index` with `generateKeyBetween()` of fractional-indexing 4.0.0, as `generateKeyBetween("a0", "a1")` gives `"a0V"`.
R writes the keys that `generateNKeysBetween(null, null, n)` gives for `n` items in a row, `a0` to `a9`, `aA` to `aZ` and `aa` to `az`, then `b00`, which a short function of the dock's R code yields.

</details>
