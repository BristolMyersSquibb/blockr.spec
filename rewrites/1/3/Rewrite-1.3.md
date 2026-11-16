# Client-drawn DAG
Status: draft. Part of [State in JS](Rewrite-1).

This part covers blockr.dag, which becomes the DAG plugin, of the plugin class `blockr.dag-dag_plugin`: a plugin drawn in the browser, which draws the board's blocks, links and stacks, edits them through commands, and keeps the blocks' positions and the layout's direction and spacing in its state.
It builds on [Client-owned board state](Rewrite-1.1), whose plugins take the place of today's extensions ([Plugins](Rewrite-1.1.12)), works under every frontend, the dock among them ([Client-drawn dock](Rewrite-1.2)), and follows the design system of [UI kit and design system for the client](Rewrite-1.7).

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
4. The blocks' positions and the layout's direction and spacing are the DAG plugin's state, open to external control, and boards saved today open with theirs, through the conversion in blockr.convert ([The conversion and the migration notes](Rewrite-1.9#the-methods-of-other-packages)).
5. What blockr.dag offers today carries over, but for what Today drops with its reason.

## Today

| Today, at `898a097` | Lines | Where it goes |
|---|---|---|
| The extension and its state: `new_dag_extension()` with `positions` and `layout`, the description of both for the assistant, `dag_ext_meta()`, and their external control, which keeps reactive values in step with the canvas | 365 | Replaced by the DAG plugin, which `new_dag_plugin()` makes in R ([Plugins](Rewrite-1.1.12#a-plugin)), whose state holds `positions` and `layout`, with the `description` keywords of the state's schema in place of `dag_ext_meta()`, and the DAG's commands and core's `blockr.core-set_plugin_state` in place of external control ([Plugins](Rewrite-1.1.12#a-plugins-state)), so that nothing keeps two copies in step |
| Layouts: `dag_layout()`, the spacing presets tuned around dagre, which does not know a stack's padding, and the toolbar's layout menu | 114, and 252 of JS | `dag_layout()` kept for app scripts, the layout run by dagre or elkjs, as the spike decides (Proposal), and the menu carried over in the client, where it runs the DAG's command `blockr.dag-relayout` ([Board updates](Rewrite-1.1.2#commands)) |
| Drawing with G6: g6R's options and behaviors, ids, a node for each block with its mark and its ports, a link with its ports and its label on hover, a combo for each stack in its colour, and the script and styles that give the canvas the design system's tokens | 709, 177 of JS and 391 of CSS | Replaced by React Flow (Proposal), with a node for each block that draws its mark from the entry of the block's class in the block registry ([Block classes in R](Rewrite-1.1.5#registration)), its ports from its class's inputs, and each stack in the colour that core keeps on it ([Board objects](Rewrite-1.1.1#stacks)) |
| Following the board: the observer that applies `update()` to the canvas, the server that wires the extension, and the placing of a block that is added or spliced into a link | 399 | Replaced by drawing from the board through `store.subscribe()` ([Board updates](Rewrite-1.1.2#following-the-board)), so nothing applies a delta by hand, while where a new block goes is an open question |
| Status badges: the DAG's method of `extension_block_callback()`, which draws the badge that `blockr.dock::block_status_badge()` specs | 111 | Replaced by `scheduler.status()` and the notifications of `CoreApi`, read for every block ([Plugins](Rewrite-1.1.12#a-plugin)), drawn as the dock's card draws its status dot ([Block cards in the dock](Rewrite-1.2.7#the-status-dot)) |
| The context menu: the generic `context_menu_items()` with `new_context_menu_entry()`, the request that fetches the entries, and the DAG's fourteen entries, on a block, a link, a stack and the canvas | 624 | The entries carried over in the client, each running a command, and the generic dropped, since no other package adds an entry (Proposal) |
| The toolbar: the generic `toolbar_items()` with `new_toolbar_item()`, and the DAG's eight items | 329 | As the context menu |
| Actions: the DAG's own, which draw a link, remove the selection, copy, cut and paste, and the wiring that fires them and the dock's twelve by id | 310 | Core's commands for the dock's twelve edits ([Client-drawn dock](Rewrite-1.2#proposal)), with the DAG's own block picker and editors of links, inputs and stacks in place of the dock's "+" menu and sidebar ([Places the dock offers plugins](Rewrite-1.2.4#places-besides-the-panel)), and the DAG's commands for copy, cut and paste |
| Copy and paste: the part of the board that a selection covers, written to the clipboard, and new ids for what a paste adds | 186, and 93 of JS | Carried over as the DAG's commands `blockr.dag-copy`, `blockr.dag-cut` and `blockr.dag-paste`, with the pasted blocks' positions in the same delta ([Board updates](Rewrite-1.1.2#plugins)) |
| Selection and the dock: a selected node shows its block in the active view through a `views$mod` of its own, and a pinned editor follows the selection through `sidebar_owned_by()` | 95 | Replaced by `core.show()` ([Plugins](Rewrite-1.1.12#showing-a-block-or-a-plugin)), and by the DAG's own editors, which follow its selection themselves |
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
- The state keeps the positions, so that a board reopens as the user arranged it, and the layout's direction and spacing, so that a layout run later and the sides of the blocks' ports follow what the user picked.
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
- The DAG draws from the board alone: every node, link and stack follows `store.board()` and `store.subscribe()`, so that a change shows at once, whether the user, another plugin, the assistant or an undo makes it ([Plugins](Rewrite-1.1.12#a-plugins-state)).
  Its class's `update` drops the position of a removed block in the same step ([Plugins](Rewrite-1.1.12#a-plugin)).
- The DAG draws each block's status badge from `scheduler.status()` and the notifications of `CoreApi`, as the dock's card draws its status dot ([Block cards in the dock](Rewrite-1.2.7#the-status-dot)).
  It demands no block of its own, so a block that nothing demands reads `unevaluated` or `stale` there until something demands it or an app has R evaluate in the background ([Evaluation in the client](Rewrite-1.1.10#demand)), where today's badge keeps the outcome of the block's last check ([R/ext.R#L538-L580](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L538-L580)).
- Every edit runs a command, so that undo and save cover it:
  - Core's commands add, append, prepend, insert and remove blocks, add, change and remove links and stacks, and edit a block's inputs, which today's DAG asks of the dock's actions ([Board updates](Rewrite-1.1.2#commands)).
  - The DAG's own commands change its state: `blockr.dag-change_position` moves blocks as a drag ends, and `blockr.dag-relayout` lays the board out again, waiting for the layout in `prepare()`, with the direction and spacing that the layout menu picks ([Board updates](Rewrite-1.1.2#commands)).
  - Its `blockr.dag-copy`, `blockr.dag-cut` and `blockr.dag-paste` carry over today's copy and paste ([R/action.R#L103-L200](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/action.R#L103-L200)).
    Copy puts on the clipboard a JSON board of the selected blocks, the links between them, the stacks that they fill and their positions, so that a paste migrates what an older version copied, as opening a board does ([Serialization](Rewrite-1.1.4#migrations)).
    Paste adds them under new ids, with their positions, in one step ([Board updates](Rewrite-1.1.2#plugins)).
- The DAG draws the UI that gathers the args of the edits its menus make, a block picker and the editors of links, inputs and stacks, in its panel or in the top layer, and runs core's commands with what the user picks, since the dock offers plugins none of its own pickers or editors ([Places the dock offers plugins](Rewrite-1.2.4#places-besides-the-panel)).
  It keeps a pinned editor on the selection by itself, where today it asks the dock's `sidebar_owned_by()` ([R/srv.R#L444-L474](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/srv.R#L444-L474)).
- The context menu and the toolbar carry today's entries over (notes), and take none from other plugins, since no package but blockr.dag has a method of `context_menu_items()` or `toolbar_items()` today ([Places the dock offers plugins](Rewrite-1.2.4#today)).
  So both generics go, with `new_context_menu_entry()` and `new_toolbar_item()`, as the dock's cards offer plugins no entry.
  Entries that plugins add to a block's menu would come from core, for every menu of a block alike ([Backlog](Backlog#entries-of-a-blocks-menu-in-core)).
- Selecting a node shows its block through core's `show()`, which every frontend carries out in its own way, the dock in the active view, where today the DAG sends the dock a `views$mod` of its own ([R/srv.R#L90-L112](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/srv.R#L90-L112), [Plugins](Rewrite-1.1.12#showing-a-block-or-a-plugin)).
  A selection of several nodes shows none, as today.
- The DAG binds its shortcuts within its own element, since they act on its selection, which it alone holds.
  So they never fire while the user types in a block's UI, as listeners on the whole document did in the prototype (notes).
  Its commands declare no `shortcut`, which a frontend would bind for the whole page ([Board updates](Rewrite-1.1.2#commands)).
- Under the board lock, the DAG draws no control for what the lock fixes, as a frontend draws none ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
  So it offers no entry that adds, removes or links a block or changes a stack, draws no link from a drag and drops no block into a stack, while zoom, pan, selection, search and the outline work as on any board ([Locked boards and the properties of blocks](Rewrite-1.1.11#plugins-on-a-locked-board)).
- Boards saved today cross through blockr.convert, whose method for the DAG's extension makes the plugin with `new_dag_plugin()` from the extension's `positions` and `layout` ([The conversion and the migration notes](Rewrite-1.9#the-methods-of-other-packages)).
  App scripts pass `new_dag_plugin()` in the board's `plugins` in place of `new_dag_extension()`, as the migration notes say ([Saved boards and app scripts across the switch](Rewrite-1.2.2#app-scripts)), since the old function goes without an alias ([State in JS](Rewrite-1#migration)).

## Open questions

- When the DAG lays blocks out, and where a block goes that someone adds: on every change, or only on request, with every position that the board holds kept, as [blockr.dag#40](https://github.com/BristolMyersSquibb/blockr.dag/issues/40) asks.
  It blocks the shape of the state, the class's `update` and its commands, and the user settles it.
- Whether the state keeps which stacks are collapsed, so that a board reopens with them collapsed, or the DAG keeps them for the page alone, as today, where saving drops them.
  It blocks the schema of the state, and the user settles it.
- Where the DAG gets the status badge and the block's mark that its node shares with the dock's card, whose status dot the dock's client holds as one function ([Block cards in the dock](Rewrite-1.2.7#the-status-dot)): blockr.dag re-implements both, or both packages take them from blockr.ui.
  It blocks drawing the board in the DAG, and the place where [blockr.dock#579](https://github.com/BristolMyersSquibb/blockr.dock/issues/579) builds the function, and the user settles it.
- Whether a user can move blocks in the DAG on a locked board, as today, where nothing stops a drag.
  It blocks the DAG's locked mode, and the user settles it.

## Work

- Lay out the largest real board with dagre and with elkjs, and draw it in React Flow with stacks that collapse, against the criteria in the notes, to decide between the two layouts, in blockr.dag
- Make the DAG a plugin in R, with `new_dag_plugin()` and `dag_layout()`, the class listed in `._BLOCKR_MODULES_` and the JSON Schema of its state, in place of `new_dag_extension()`, in blockr.dag
- Build the DAG plugin's class in the client, with its state, its `update` and its commands for positions, layouts and copy and paste, tested on core's `CoreApi` for tests, in blockr.dag
- Draw the board in the DAG, with blocks, their marks, ports and status badges, links, stacks that collapse and expand, zoom, pan, dragging, a selection that shows a block, search and the outline, in blockr.dag
- Draw the DAG's context menu, toolbar, layout menu, block picker and editors of links, inputs and stacks, and bind its shortcuts, running core's commands and the DAG's, in blockr.dag
- Remove the extension, its R UI and server, g6R and the hooks of its menus, and rewrite the user guide for the plugin, in blockr.dag
- Write the migration notes for app scripts that use the DAG as a vignette, which lists each change that such a script needs, for an AI to apply, in blockr.dag

<details><summary>Notes for implementers</summary>

The rows of Today by file, at `898a097`: the extension and its state are `new_dag_extension()`, `dag_ext_meta()` and `dag_positions_description()` in `R/ext.R`, `setup_layout_ctrl()`, `push_layout()` and `setup_positions_ctrl()` in `R/srv.R`, and the position helpers of `R/g6r.R`; layouts are `R/layout.R` and `inst/assets/js/layout-menu.js`; drawing is the rest of `R/g6r.R` up to `g6_data_from_board()`, `R/graph.R`, `R/meta.R`, `R/ui.R`, `inst/assets/js/dag-chrome.js` and `inst/assets/css/dag.css`; following the board is `dag_ext_srv()` and `update_observer()` in `R/srv.R` and the proxy helpers of `R/g6r.R` from `remove_nodes()` to `update_combos()`; status badges are `extension_block_callback.dag_extension()` and `status_badges()` in `R/ext.R`; the context menu is `R/ctx.R` and `context_menu_items.dag_extension()`; the toolbar is `R/tool.R` and `toolbar_items.dag_extension()`; actions are `R/action.R` and `actions_observers()`; copy and paste are `R/subboard.R` and `inst/assets/js/copy-paste.js`; selection is `reveal_panel_delta()` and `setup_sidebar_retarget()` in `R/srv.R`; shortcuts are `setup_remove_elements_kbd()`, `setup_copy_paste_kbd()` and `inst/assets/js/rm-sel.js`; and the utilities are `R/utils.R` and `R/pkg.R`.

Today's behaviors in g6R are `zoom_canvas()`, `drag_canvas()`, `drag_element()`, `click_select(multiple = TRUE)`, `brush_select()` with Alt, `collapse_expand()`, `hover_activate()` for a link's label and `create_edge()`, and its plugins a context menu, a toolbar, the search and the outline ([R/g6r.R#L284-L460](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/g6r.R#L284-L460)).
A link dropped on the canvas appends a block to the node it starts from, or prepends one where it starts from an input port, through the "+" menu at the drop.
Stacks are combos laid out with dagre, which does not know a combo's padding, so the spacing presets are tuned around it ([R/layout.R#L66-L76](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/layout.R#L66-L76)).

The context menu's entries by target: on a block, Create link, Remove block, Append block, Edit inputs, Copy and Cut; on a link, Remove link, Edit link and Insert block; on a stack, Remove stack, Edit stack, Copy and Cut; and on the canvas, Add block, Create stack and Paste ([R/ext.R#L118-L419](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L118-L419)).
The toolbar's items: search, zoom in, zoom out, fit, the layout menu, add a block, add a stack and remove the selection ([R/ext.R#L422-L517](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L422-L517)).

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
