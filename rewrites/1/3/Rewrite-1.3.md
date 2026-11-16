# Client-drawn DAG
Status: draft. Part of [State in JS](Rewrite-1).

This part covers blockr.dag, which becomes the DAG plugin, of the plugin class `blockr.dag-dag_plugin`: a plugin drawn in the browser, which draws the board's blocks, links and stacks, edits them through commands, and keeps the blocks' positions, its layout's direction, spacing and placement, and which stacks are collapsed in its state.
It builds on [Client-owned board state](Rewrite-1.1), whose plugins take the place of today's extensions ([Plugins](Rewrite-1.1.12)), works under every frontend, the dock among them ([Client-drawn dock](Rewrite-1.2)), and takes the design system's colours from core's tokens, without blockr.ui's code for now ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend), [UI kit and design system for the client](Rewrite-1.7)).

## Problem

The DAG is an htmlwidget driven from R: blockr.dag configures G6's behaviors and plugins through g6R ([R/g6r.R#L284-L460](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/g6r.R#L284-L460)) and keeps the blocks' positions and the layout as the state of a Shiny-module extension, `new_dag_extension(positions, layout)` ([R/ext.R#L37-L47](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L37-L47)).
That state lives twice, in reactive values of the extension's server and in the canvas.
Two guards keep the copies in step: one compares positions to the whole pixel and reads a drag's positions only once they have stayed put for 250 ms, and the other keeps R from sending the browser back a layout that the browser has just reported ([R/srv.R#L114-L275](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/srv.R#L114-L275)).
The DAG follows the board by applying the raw payload of `update()` to G6 by hand, removing before it adds, so that a delta that reuses an id draws right ([R/srv.R#L276-L366](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/srv.R#L276-L366)).
It reaches the dock through the dock's internals, which the notes of [Client-drawn dock](Rewrite-1.2) list.
With the board held by the client ([Client-owned board state](Rewrite-1.1)) and the dock drawn in the browser ([Client-drawn dock](Rewrite-1.2)), there is no R board left for it to read or update.

## What must hold

1. The DAG draws the board's blocks, links and stacks in the browser, without g6R, from the board alone, so that it shows every change, whoever makes it.
2. Every edit that the DAG makes is a command, core's for blocks, links and stacks and its own for its state, so that undo and save cover it, and none of it reaches R.
3. It works under every frontend through `CoreApi` alone, as condition 2 of [Plugins](Rewrite-1.1.12#what-must-hold) asks of every plugin.
4. The blocks' positions, the layout's direction, spacing and placement, and which stacks are collapsed are the DAG plugin's state, open to external control, and boards saved today open with theirs, through the conversion in blockr.convert ([The conversion and the migration notes](Rewrite-1.9#the-methods-of-other-packages)).
5. What blockr.dag offers today carries over, but for what Today drops with its reason.
6. A block that someone adds gets a place without any other block moving, and the whole board is laid out again only when someone asks for it, as [blockr.dag#40](https://github.com/BristolMyersSquibb/blockr.dag/issues/40) asks.

## Today

| Today, at `898a097` | Lines | Where it goes |
|---|---|---|
| The extension and its state: `new_dag_extension()` with `positions` and `layout`, the description of both for the assistant, `dag_ext_meta()`, and their external control, which keeps reactive values in step with the canvas | 365 | Replaced by the DAG plugin, which `new_dag_plugin()` makes in R ([Plugins](Rewrite-1.1.12#a-plugin)), whose state holds `positions` and `layout`, with the `description` keywords of the state's schema in place of `dag_ext_meta()`, and the DAG's commands and core's `blockr.core-set_plugin_state` in place of external control ([Plugins](Rewrite-1.1.12#a-plugins-state)), so that nothing keeps two copies in step |
| Layouts: `dag_layout()`, the spacing presets tuned around dagre, which does not know a stack's padding, and the toolbar's layout menu | 114, and 252 of JS | `dag_layout()` kept for app scripts, with the placement of new blocks beside its direction and spacing, the layout run by dagre or elkjs, as the spike decides, and the menu carried over as the quick action of the DAG's board action Layout (Proposal) |
| Drawing with G6: g6R's options and behaviors, ids, a node for each block with its mark and its ports, a link with its ports and its label on hover, a combo for each stack in its colour, and the script and styles that give the canvas the design system's tokens | 709, 177 of JS and 391 of CSS | Replaced by React Flow (Proposal), with a node for each block that draws its mark from the icon of the block class's entry in the block registry ([Block classes in R](Rewrite-1.1.5#registration)), on its category's colour from core's tokens, which take the place of the script that resolves tokens for the canvas, its ports from its class's inputs, and each stack in the colour that core keeps on it ([Board objects](Rewrite-1.1.1#stacks)) |
| Following the board: the observer that applies `update()` to the canvas, the server that wires the extension, and the placing of a block that is added or spliced into a link | 399 | Replaced by drawing from the board through `store.subscribe()` ([Board updates](Rewrite-1.1.2#following-the-board)), so nothing applies a delta by hand, while the class's `update` places an added block without moving another, where today an inserted block pushes the blocks below it down (Proposal) |
| Status badges: the DAG's method of `extension_block_callback()`, which draws the badge that `blockr.dock::block_status_badge()` specs | 111 | Replaced by `scheduler.status()` and the notifications of `CoreApi`, read for every block ([Plugins](Rewrite-1.1.12#a-plugin)), drawn as the dock's card draws its status dot, in core's status tokens ([Block cards in the dock](Rewrite-1.2.7#the-status-dot)) |
| The context menu: the generic `context_menu_items()` with `new_context_menu_entry()`, the request that fetches the entries, and the DAG's fourteen entries, on a block, a link, a stack and the canvas | 624 | The entries carried over as board actions, core's and the DAG's, which the DAG's menus of a node, a link, a stack, its canvas and its selection offer through core, and the generic dropped (Proposal, [Board actions](Rewrite-1.1.16#the-menus-of-board-objects)) |
| The toolbar: the generic `toolbar_items()` with `new_toolbar_item()`, and the DAG's eight items | 329 | Search, zoom and fit carried over as the DAG's own controls, the layout menu as the quick action of the DAG's board action Layout, and the items that add a block or a stack and remove the selection as buttons of the board actions on the board and on the selection, with the generic dropped (Proposal) |
| Actions: the DAG's own, which draw a link, remove the selection, copy, cut and paste, and the wiring that fires them and the dock's twelve by id | 310 | Core's board actions for the dock's twelve edits and for removing the selection, with their block picker and their editors of links, inputs and stacks ([Board actions](Rewrite-1.1.16#cores-board-actions)), and the DAG's own board actions for copy, cut and paste |
| Copy and paste: the part of the board that a selection covers, written to the clipboard, and new ids for what a paste adds | 186, and 93 of JS | Carried over as the DAG's commands `blockr.dag-copy`, `blockr.dag-cut` and `blockr.dag-paste`, with the pasted blocks' positions in the same delta ([Board updates](Rewrite-1.1.2#plugins)) |
| Selection and the dock: a selected node shows its block in the active view through a `views$mod` of its own, and a pinned editor follows the selection through `sidebar_owned_by()` | 95 | Replaced by `core.show()` ([Plugins](Rewrite-1.1.12#showing-a-block-or-a-plugin)), and by `core.boardActions.select()`, whose selection a pinned advanced action follows ([Board actions](Rewrite-1.1.16#the-advanced-action)) |
| Keyboard shortcuts: Backspace removes the selection, Ctrl or Cmd with C, X and V copy, cut and paste, and a drag with Alt held selects | 38, and 10 of JS | Carried over, bound by the DAG within its own element (Proposal) |
| Search and the outline of the board, g6R's `g6_search()` and `g6_outline()` | 27 | Carried over as the DAG's own components |
| The empty board's line, "No blocks yet. Right-click to add one." | 18, and 8 of JS | Carried over |
| Utilities and the hooks of the end-to-end tests | 78 | Dropped, with the tests that need them |
| The R option `blockr.dag.svg_renderer` and the options of g6R that the user guide documents | | Dropped with g6R |
| The vignettes: the user guide, and three on extending the context menu, the toolbar and the block callback | 492 | The user guide rewritten for the plugin, the three dropped with the hooks they document, and the migration notes added (Work) |
| The app scripts of the examples | 105 | Kept, changed as the migration notes say |
| The tests, which drive the DAG in a browser through shinytest2 | 2,757 | Replaced by tests of the plugin class on core's `CoreApi` for tests ([Plugins](Rewrite-1.1.12#testing)) and of its constructor in R |

## Proposal

- The DAG is a plugin of class `blockr.dag-dag_plugin`, named "Workflow", as today's extension is, whose class sets `state`, `update`, `ui` and `commands`, and which works on the board through `CoreApi` alone ([Plugins](Rewrite-1.1.12#a-plugin)).
  It asks nothing of a frontend beyond what core's `PluginClass` holds, so every frontend places it as it places any plugin with a `ui`, the dock in a panel and core's basic frontend in a section ([Plugins](Rewrite-1.1.12#plugin-classes)).
  It sizes itself from the element that the frontend gives it ([Places the dock offers plugins](Rewrite-1.2.4#a-plugins-panel)), where today it sizes its canvas through dockview's markup.
- In R, `new_dag_plugin(positions, layout)` makes the plugin, as `new_dag_extension()` makes the extension today, and `dag_layout()` gives the layout's direction and spacing, as today ([R/layout.R#L1-L33](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/layout.R#L1-L33)).
  The package lists the class in its `._BLOCKR_MODULES_` and ships the JSON Schema of its state beside its module ([Plugins](Rewrite-1.1.12#a-plugin)).
  The plugin gives R no requests, since it lives in the browser alone ([Plugins](Rewrite-1.1.12#a-plugins-requests)).
- The state keeps the positions, so that a board reopens as the user arranged it, and the layout's direction, spacing and placement, so that a layout run later, the place of a new block and the sides of the blocks' ports follow what the user picked, and which stacks are collapsed, so that a board reopens with its stacks as the user left them, where today's DAG keeps that on its canvas alone.
  The `description` keywords of its schema tell the assistant what `dag_ext_meta()` tells it today: that a position is a point on the canvas, and how to place a block beside another ([R/ext.R#L54-L109](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L54-L109)).
  The assistant moves blocks through the DAG's commands or through `blockr.core-set_plugin_state` ([Plugins](Rewrite-1.1.12#a-plugins-state)).
- The DAG is drawn with React Flow (`@xyflow/react`), in place of G6.
  It is React, so a node is a component in the DAG's own React root that reads core's store, since the DAG's UI shares no React context with the dock's ([Plugins](Rewrite-1.1.12#plugin-classes)).
  Its nodes are elements of the page, so they take the design system's tokens from CSS, where today's canvas needs a script that resolves each token through a canvas of one pixel ([inst/assets/js/dag-chrome.js#L1-L25](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/inst/assets/js/dag-chrome.js#L1-L25)).
  Langflow, Flowise and Dify are built on it, and it is 88 KB gzipped at 13.0.0, against 400 KB for G6 (notes).
  The prototype [cynkra/blockr.react](https://github.com/cynkra/blockr.react) drew the DAG with React Flow as a dock extension, with links drawn by dragging, menus, and copy and paste (notes).
- React Flow lays nothing out ("We have not implemented our own layouting solution yet", [layouting](https://reactflow.dev/learn/layouting/layouting)), so the DAG lays blocks out with dagre, through `@dagrejs/dagre`, or with elkjs, as a spike decides before the rebuild, against criteria that the notes fix beforehand.
  Today's DAG lays its stacks out with dagre already, which keeps each stack's blocks together as a cluster ([R/layout.R#L80-L96](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/layout.R#L80-L96)).
  React Flow's docs warn that a dagre issue "prevents it from laying out sub-flows correctly" where a node in a group links to one outside it, but the issue concerns an edge from a node to the group that holds it ([dagre#238](https://github.com/dagrejs/dagre/issues/238)), and no link draws one, since a link joins two blocks.
  So the spike tries dagre first, at 16 KB gzipped, and elkjs, at 447 KB, only where dagre fails a criterion, in which case the DAG loads elkjs only when it lays blocks out, which drawing a saved board does not need.
- Stacks become group nodes with a `parentId` ([sub flows](https://reactflow.dev/learn/layouting/sub-flows)), and collapsing one is the DAG's own code, since React Flow collapses nothing itself and its example of it is one of its paid examples ([Expand and Collapse](https://reactflow.dev/examples/layout/expand-collapse)).
  The command `blockr.dag-collapse_stack` collapses or expands one, with `undo: false`, since it changes only what the user looks at, as the dock's `blockr.dock-collapse_rail` does ([The dock's state](Rewrite-1.2.1#commands)), and the class's `update` drops a removed stack from the state, as it drops a removed block's position.
- The DAG draws from the board alone: every node, link and stack follows `store.board()` and `store.subscribe()`, so that a change shows at once, whether the user, another plugin, the assistant or an undo makes it ([Plugins](Rewrite-1.1.12#a-plugins-state)).
  Its class's `update` drops the position of a removed block in the same step ([Plugins](Rewrite-1.1.12#a-plugin)).
- The DAG draws each node's mark and status badge itself, as the dock's card does, without blockr.ui's code for now ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
  The mark is the icon of the block class's registry entry on the colour of its category, and the badge comes from `scheduler.status()` and the notifications of `CoreApi`, in the colours of core's tokens, `--bc-color-category-*` and `--bc-color-status-*`, so that they match the dock's card by construction ([Block cards in the dock](Rewrite-1.2.7#the-status-dot)).
  Which status draws a filled dot and which a ring follows the table of [Block cards in the dock](Rewrite-1.2.7#the-status-dot), which a test in blockr.dag checks, and the DAG draws its tooltips in the design system's style, as the dock does, until blockr.ui offers the three as one module ([UI kit and design system for the client](Rewrite-1.7)).
  It demands no block of its own, so a block that nothing demands reads `unevaluated` or `stale` there until something demands it or an app has R evaluate in the background ([Evaluation in the client](Rewrite-1.1.10#demand)), where today's badge keeps the outcome of the block's last check ([R/ext.R#L538-L580](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L538-L580)).
- The DAG places a block that someone adds without moving any other block, and lays the whole board out again only when someone asks, where G6 lays the board out again as blocks come ([blockr.dag#40](https://github.com/BristolMyersSquibb/blockr.dag/issues/40)):
  1. The state holds a position for every block.
  2. The class's `update` places the blocks that a change adds, in the same step, so that undo takes back a block and its position together, whoever adds it: the DAG's own gestures, a dock card's Append block or the assistant ([Plugins](Rewrite-1.1.12#a-plugin)).
  3. It places them through a placement strategy, which takes every existing position as fixed and returns positions for the added blocks alone (notes).
     Beside, the default, puts a block one step after the block it reads from, below it or to its right as the direction says, then moves it to the nearest spot where it overlaps nothing, and Grid snaps it to the nearest free cell of a grid that follows the spacing.
  4. A block that the user drops or clicks into place starts from that point, which the DAG adds to the board action's step, and the strategy only moves it off what it would overlap ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).
     Several blocks added at once, as the assistant adds them, are placed in the order of their links, so that a new chain comes out as a chain ([blockr.dag#117](https://github.com/BristolMyersSquibb/blockr.dag/issues/117)).
  5. The command `blockr.dag-relayout` lays the whole board out again with dagre or elkjs, as one undo step, from the toolbar's Layout or the assistant.
  6. A board that opens without the position of any block gets them from one such layout as the DAG starts, and one that lacks the positions of some blocks gets theirs from the strategy, as added blocks do.
     Either is one delta of the origin `blockr.dag-dag_plugin` with `undo: false`, as the dock adds its first view ([The dock's state](Rewrite-1.2.1#starting-on-a-board)).

  A strategy sees only the board and the change, since `update` gives the same patches wherever it runs, so it works from a node's nominal size, its mark with room for its label, rather than from what the page measures ([Board updates](Rewrite-1.1.2#plugins)).
  The user picks the strategy in Layout's quick action, and an inserted block no longer pushes the blocks below it down, as today's does ([R/g6r.R#L856-L903](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/g6r.R#L856-L903)).
  Repulsion fits the same interface, through d3-force, which pins nodes and takes a seeded random source, and comes in should Beside and Grid prove too rigid (notes).
- Every edit runs a command, so that undo and save cover it:
  - Core's commands add, append, prepend, insert and remove blocks, add, change and remove links and stacks, and edit a block's inputs, which today's DAG asks of the dock's actions ([Board updates](Rewrite-1.1.2#commands)).
  - The DAG's own commands change its state: `blockr.dag-change_position` moves blocks as a drag ends, and `blockr.dag-relayout` lays the board out again, waiting for the layout in `prepare()`, with the direction and spacing that the layout menu picks ([Board updates](Rewrite-1.1.2#commands)).
  - Its `blockr.dag-copy`, `blockr.dag-cut` and `blockr.dag-paste` carry over today's copy and paste ([R/action.R#L103-L200](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/action.R#L103-L200)).
    Copy puts on the clipboard a JSON board of the selected blocks, the links between them, the stacks that they fill and their positions, so that a paste migrates what an older version copied, as opening a board does ([Serialization](Rewrite-1.1.4#migrations)).
    Paste adds them under new ids, with their positions, in one step ([Board updates](Rewrite-1.1.2#plugins)).
- The DAG's menus of a node, a link, a stack, its canvas and its selection are the menus of board actions that core draws, or the frontend through its hook, so that each offers what every menu of the same object offers, core's board actions and every package's ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).
  So the DAG draws no block picker and no editor of links, inputs or stacks of its own, since those are the quick actions and advanced actions of core's board actions ([Board actions](Rewrite-1.1.16#cores-board-actions)).
  A link that the user drops on the canvas triggers Append block from the link's block at the drop, or Prepend block where the link starts from an input, and the DAG adds the new block's position to the step ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).
  The DAG tells core of every node, link and stack that the user selects, through `core.boardActions.select()`, so that a pinned advanced action follows the selection, where today the DAG asks the dock's `sidebar_owned_by()` ([R/srv.R#L444-L474](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/srv.R#L444-L474)).
- The DAG registers board actions of its own: Copy and Cut on a node, a stack or a selection, and Paste and Layout on the board, which run its commands ([Board actions](Rewrite-1.1.16#a-board-action)).
  So the generics `context_menu_items()` and `toolbar_items()` go, with `new_context_menu_entry()` and `new_toolbar_item()`, since a package adds what it offers in a menu as a board action, which every menu of the object then offers.
  The toolbar holds the DAG's own controls, search, zoom and fit, and a button for each board action on the board, core's Add block and Create stack and the DAG's Paste and Layout, whose quick action holds Lay out again with the direction, the spacing and the placement.
  While the user has selected something, it also holds a button for each board action on the selection, such as Remove, so that a board action that another package registers on the board or on a selection shows there too, as in the DAG's menus ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).
- Selecting a node shows its block through core's `show()`, which every frontend carries out in its own way, the dock in the active view, where today the DAG sends the dock a `views$mod` of its own ([R/srv.R#L90-L112](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/srv.R#L90-L112), [Plugins](Rewrite-1.1.12#showing-a-block-or-a-plugin)).
  A selection of several nodes shows none, as today.
- The DAG binds its shortcuts within its own element, since they act on its selection, which it alone holds.
  So they never fire while the user types in a block's UI, as listeners on the whole document did in the prototype (notes).
  Its commands declare no `shortcut`, which a frontend would bind for the whole page ([Board updates](Rewrite-1.1.2#commands)).
- Under the board lock, the DAG draws no control for what the lock fixes, as a frontend draws none ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
  So its menus offer only the board actions that the lock leaves, it draws no link from a drag and drops no block into a stack, while zoom, pan, selection, search and the outline work as on any board ([Locked boards and the properties of blocks](Rewrite-1.1.11#plugins-on-a-locked-board), [Board actions](Rewrite-1.1.16#cores-board-actions)).
- Boards saved today cross through blockr.convert, whose method for the DAG's extension makes the plugin with `new_dag_plugin()` from the extension's `positions` and `layout` ([The conversion and the migration notes](Rewrite-1.9#the-methods-of-other-packages)).
  App scripts pass `new_dag_plugin()` in the board's `plugins` in place of `new_dag_extension()`, as the migration notes say ([Saved boards and app scripts across the switch](Rewrite-1.2.2#app-scripts)), since the old function goes without an alias ([State in JS](Rewrite-1#migration)).

## Open questions

- Whether a user can move blocks in the DAG on a locked board, as today, where nothing stops a drag.
  It blocks the DAG's locked mode, and the user settles it.

## Work

- Lay out the largest real board with dagre and with elkjs, and draw it in React Flow with stacks that collapse, against the criteria in the notes, to decide between the two layouts, in blockr.dag
- Make the DAG a plugin in R, with `new_dag_plugin()` and `dag_layout()`, the class listed in `._BLOCKR_MODULES_` and the JSON Schema of its state, in place of `new_dag_extension()`, in blockr.dag
- Build the DAG plugin's class in the client, with its state, its `update`, which places added blocks through the strategies Beside and Grid, and its commands for positions, layouts, collapsed stacks and copy and paste, tested on core's `CoreApi` for tests, in blockr.dag
- Draw the board in the DAG, with blocks, their marks, ports and status badges, links, stacks that collapse and expand, zoom, pan, dragging, a selection that shows a block, search and the outline, in blockr.dag
- Open core's menus of board actions from the DAG's nodes, links, stacks, canvas and selection, register the DAG's board actions for copy, cut, paste and layout, draw its toolbar with the board actions on the board and on the selection, and bind its shortcuts, in blockr.dag
- Remove the extension, its R UI and server, g6R and the hooks of its menus, and rewrite the user guide for the plugin, in blockr.dag
- Write the migration notes for app scripts that use the DAG as a vignette, which lists each change that such a script needs, for an AI to apply, in blockr.dag

<details><summary>Notes for implementers</summary>

The rows of Today by file, at `898a097`: the extension and its state are `new_dag_extension()`, `dag_ext_meta()` and `dag_positions_description()` in `R/ext.R`, `setup_layout_ctrl()`, `push_layout()` and `setup_positions_ctrl()` in `R/srv.R`, and the position helpers of `R/g6r.R`; layouts are `R/layout.R` and `inst/assets/js/layout-menu.js`; drawing is the rest of `R/g6r.R` up to `g6_data_from_board()`, `R/graph.R`, `R/meta.R`, `R/ui.R`, `inst/assets/js/dag-chrome.js` and `inst/assets/css/dag.css`; following the board is `dag_ext_srv()` and `update_observer()` in `R/srv.R` and the proxy helpers of `R/g6r.R` from `remove_nodes()` to `update_combos()`; status badges are `extension_block_callback.dag_extension()` and `status_badges()` in `R/ext.R`; the context menu is `R/ctx.R` and `context_menu_items.dag_extension()`; the toolbar is `R/tool.R` and `toolbar_items.dag_extension()`; actions are `R/action.R` and `actions_observers()`; copy and paste are `R/subboard.R` and `inst/assets/js/copy-paste.js`; selection is `reveal_panel_delta()` and `setup_sidebar_retarget()` in `R/srv.R`; shortcuts are `setup_remove_elements_kbd()`, `setup_copy_paste_kbd()` and `inst/assets/js/rm-sel.js`; and the utilities are `R/utils.R` and `R/pkg.R`.

Today's behaviors in g6R are `zoom_canvas()`, `drag_canvas()`, `drag_element()`, `click_select(multiple = TRUE)`, `brush_select()` with Alt, `collapse_expand()`, `hover_activate()` for a link's label and `create_edge()`, and its plugins a context menu, a toolbar, the search and the outline ([R/g6r.R#L284-L460](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/g6r.R#L284-L460)).
A link dropped on the canvas appends a block to the node it starts from, or prepends one where it starts from an input port, through the "+" menu at the drop.
Stacks are combos laid out with dagre, which does not know a combo's padding, so the spacing presets are tuned around it ([R/layout.R#L66-L76](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/layout.R#L66-L76)).

The context menu's entries by target: on a block, Create link, Remove block, Append block, Edit inputs, Copy and Cut; on a link, Remove link, Edit link and Insert block; on a stack, Remove stack, Edit stack, Copy and Cut; and on the canvas, Add block, Create stack and Paste ([R/ext.R#L118-L419](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L118-L419)).
The toolbar's items: search, zoom in, zoom out, fit, the layout menu, add a block, add a stack and remove the selection ([R/ext.R#L422-L517](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L422-L517)).

A placement strategy, with illustrative names:

```ts
interface Placement {
  id: string;                                       // "beside", "grid"
  place(args: { board: Board; fixed: Positions; added: BlockId[]; preferred: Positions; layout: Layout }): Positions;   // positions for the added blocks alone
}
```

Today a block that is added goes to the last position of the mouse on the canvas, and blocks added at once stack 130 px apart below it ([R/g6r.R#L904-L923](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/g6r.R#L904-L923)).
Version 3.0.1 of d3-force (ISC, 5.7 KB gzipped) keeps a node with `fx` and `fy` where they say, takes a seeded `randomSource()` and steps through `tick()` without timers, so that it places new blocks with every existing one pinned and the same result each time ([d3-force](https://d3js.org/d3-force/simulation)).

A position today is the centre of a block's node, in pixels of the canvas.
React Flow places a node by its top left corner, and a node in a group relative to the group, so the DAG converts, while the state keeps today's meaning, so that converted positions keep theirs.

Safari writes to the clipboard only within the user's gesture, so today's copy starts the write at once and fills it once R has sent the selection ([inst/assets/js/copy-paste.js](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/inst/assets/js/copy-paste.js)).
In the client the selection is at hand, so copy writes it within the gesture.

The prototype [cynkra/blockr.react](https://github.com/cynkra/blockr.react), of 2026-04-02 to 2026-07-22 at `e4e5c35`, is a dock extension that draws with React Flow 12 and lays out with dagre, which it runs on the blocks alone before it draws each stack's box around its blocks ([srcjs/DAGCanvas.jsx#L65-L148](https://github.com/cynkra/blockr.react/blob/e4e5c35ff8ae3759aa416a1870fb34360b8306d2/srcjs/DAGCanvas.jsx#L65-L148)).
Its findings that carry over: keys bound on the canvas rather than the document, since a listener on the document fired Delete while the user edited an input and took copies of selected text; a clipboard of its own beside the system's, since `navigator.clipboard.readText()` fails in Safari and in headless browsers; and `fitView` once on mount, since the prop fits the view again on every change of the nodes.
React Flow 13.0.0 drops the rule that a group come before its nodes, which the prototype ordered by hand, and adds `changeParent()`, which moves a node into a group or out of it without computing its new position, which the prototype did by hand.

The spike runs on the clinical data explorer's board, the largest of the five boards saved in blockr.sandbox, with 99 blocks and 108 links ([dev/json/cdex-board-latest.json](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/f938c30bad1710dd702024a8c96d03ed8a77f248/dev/json/cdex-board-latest.json)).
None of the five holds a stack, so the spike adds five to it, of 2 to 20 blocks each, some of them linked to blocks outside their stack.
Its criteria, fixed before it runs:

1. Laid out with each stack as a cluster that holds its blocks, the board has no two stacks that overlap, no block of another stack or of none inside a stack's box, and each link between a block in a stack and one outside it running from port to port.
2. The DAG collapses and expands every stack in React Flow: collapsed, the stack hides its blocks and their links end on the stack, and expanded, its blocks are back where they were.
3. The layout returns within one second, and React Flow draws the board no slower than today's DAG draws it, both measured on one machine, which the result names.

The DAG lays out with dagre where dagre meets all three, and with elkjs where dagre fails one that elkjs meets.

The dock coupling to replace is listed in [Client-drawn dock](Rewrite-1.2).

Versions on npm on 2026-11-16: `@xyflow/react` 13.0.0 (MIT), released that day, `@dagrejs/dagre` 3.1.3 (MIT), of 2026-10-24, `elkjs` 0.12.1 (EPL-2.0 or GPL-3.0-or-later, so blockr.dag, GPL (>= 3), can bundle it under the GPL), `@antv/g6` 5.1.1 (MIT).
Weekly downloads for 2026-11-09 to 15: `@xyflow/react` 21.9 million, `elkjs` 20.9 million, `@dagrejs/dagre` 9.0 million, `@antv/g6` 325,000.
Gzipped sizes from bundlephobia: `@xyflow/react` 88 KB at 13.0.0 and 60 KB at 12.12.0, `@dagrejs/dagre` 16 KB, `elkjs` 447 KB and `@antv/g6` 400 KB.
Today's dagre is G6's, version 0.8.5 of the unscoped `dagre`, through `@antv/layout` 2.0.0, while `@dagrejs/dagre` is the line that the dagrejs organisation maintains.

Other libraries weighed and not chosen: Cytoscape.js 3.35.0 (MIT) has compound nodes and collapsing through an extension, but draws on a canvas and is made for network graphs, so marks, ports and badges would be HTML laid over the canvas, and links drawn by another extension; Rete.js 2.0.6 (MIT) is a node editor with ports that React can draw, with 135,000 weekly downloads and no release of its core since 2025-06-30; and `@joint/core` 4.3.4 (MPL-2.0) and `@maxgraph/core` 0.25.1 (Apache-2.0) draw diagrams in SVG from models of their own, which React Flow's nodes, plain React components, do not need.

</details>
