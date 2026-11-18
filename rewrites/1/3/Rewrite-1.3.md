# Client-drawn DAG
Status: review. Part of [State in JS](Rewrite-1).

This part covers blockr.dag, which becomes the DAG plugin, of the plugin class `blockr.dag-dag_plugin`: a plugin drawn in the browser, which draws the board's blocks, links and stacks, edits them through commands, and keeps the positions of the blocks and of the stacks that hold no block, its layout's direction, spacing, placement and snapping, and which stacks are collapsed in its state.
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
4. The positions of the blocks and of the stacks that hold no block, the layout's direction, spacing, placement and snapping, and which stacks are collapsed are the DAG plugin's state, open to external control, and boards saved today open with theirs, through the conversion in blockr.convert ([The conversion and the migration notes](Rewrite-1.9#the-methods-of-other-packages)).
5. What blockr.dag offers today carries over, but for what Today drops with its reason.
6. A block that someone adds gets a place without any other block moving, and the whole board is laid out again only when someone asks for it, as [blockr.dag#40](https://github.com/BristolMyersSquibb/blockr.dag/issues/40) asks.
7. On a locked board, the DAG offers nothing that the lock fixes, and keeps its blocks where they are, unless the deployment leaves rearranging to readers.

## Today

| Today, at `898a097` | Lines | Where it goes |
|---|---|---|
| The extension and its state: `new_dag_extension()` with `positions` and `layout`, the description of both for the assistant, `dag_ext_meta()`, and their external control, which keeps reactive values in step with the canvas | 365 | Replaced by the DAG plugin, which `new_dag_plugin()` makes in R ([Plugins](Rewrite-1.1.12#a-plugin)), whose state holds the positions, the layout and the collapsed stacks, with the `description` keywords of the state's schema in place of `dag_ext_meta()`, and the DAG's commands and core's `blockr.core-set_plugin_state` in place of external control, so that nothing keeps two copies in step ([The DAG's state, commands and placement](Rewrite-1.3.1#the-state)) |
| Layouts: `dag_layout()`, the spacing presets tuned around dagre, which does not know a stack's padding, and the toolbar's layout menu | 114, and 252 of JS | `dag_layout()` kept for app scripts, with the placement of added blocks and snapping beside its direction and spacing, the layout run by dagre or elkjs, as the spike decides ([The DAG's state, commands and placement](Rewrite-1.3.1#laying-the-board-out-again)), and the menu carried over as the quick action of the DAG's board action Layout ([Drawing the DAG](Rewrite-1.3.2#the-dags-board-actions)) |
| Drawing with G6: g6R's options and behaviors, ids, a node for each block with its mark, its ports and a control that hides the blocks downstream of it, a link with its ports and its label on hover, a combo for each stack in its colour, and the script and styles that give the canvas the design system's tokens | 709, 177 of JS and 391 of CSS | Replaced by React Flow (Proposal), with a node for each block that draws its mark from the icon of the block class's entry in the block registry ([Block classes in R](Rewrite-1.1.5#registration)), on its category's colour from core's tokens, which take the place of the script that resolves tokens for the canvas, its ports from its class's inputs, and each stack in the colour that core keeps on it ([Board objects](Rewrite-1.1.1#stacks)). The control that hides the blocks downstream of a node is dropped. A board is not a tree: a block downstream of the collapsed node may also read from blocks that stay in view, so hiding it would hide links of blocks that the user still sees. Stacks already fold a part of the board |
| Following the board: the observer that applies `update()` to the canvas, the server that wires the extension, and the placing of a block that is added or spliced into a link | 399 | Replaced by drawing from the board through `store.subscribe()` ([Board updates](Rewrite-1.1.2#following-the-board)), so nothing applies a delta by hand, while the class's `afterStep` places an added block without moving another, where today an inserted block pushes on the block that the link fed, with every block downstream of it ([The DAG's state, commands and placement](Rewrite-1.3.1#placing-added-blocks)) |
| Status badges: the DAG's method of `extension_block_callback()`, which draws the badge that `blockr.dock::block_status_badge()` specs | 111 | Replaced by `scheduler.status()` and the notifications of `CoreApi`, read for every block ([Plugins](Rewrite-1.1.12#a-plugin)), drawn as the dock's card draws its status dot, in core's status tokens ([Block cards in the dock](Rewrite-1.2.7#the-status-dot)) |
| The context menu: the generic `context_menu_items()` with `new_context_menu_entry()`, the request that fetches the entries, and the DAG's fourteen entries, on a block, a link, a stack and the canvas | 624 | The entries carried over as board actions, core's and the DAG's, which the DAG's menus of a node, a link, a stack, its canvas and its selection offer through core, and the generic dropped ([Drawing the DAG](Rewrite-1.3.2#gestures), [Board actions](Rewrite-1.1.16#the-menus-of-board-objects)) |
| The toolbar: the generic `toolbar_items()` with `new_toolbar_item()`, and the DAG's eight items | 329 | Search, zoom and fit carried over as the DAG's own controls, the layout menu as the quick action of the DAG's board action Layout, and the items that add a block or a stack and remove the selection as buttons of the board actions on the board and on the selection, with the generic dropped ([Drawing the DAG](Rewrite-1.3.2#the-toolbar)) |
| Actions: the DAG's own, which draw a link, remove the selection, copy, cut and paste, and the wiring that fires them and the dock's twelve by id | 310 | Core's board actions for the dock's twelve edits and for removing the selection, with their block picker and their editors of links, inputs and stacks ([Board actions](Rewrite-1.1.16#cores-board-actions)), and the DAG's own board actions for copy, cut and paste |
| Copy and paste: the part of the board that a selection covers, written to the clipboard, and new ids for what a paste adds | 186, and 93 of JS | Carried over as the DAG's board actions Copy, Cut and Paste and its command `blockr.dag-paste`, which adds the pasted blocks' positions in the same delta ([Drawing the DAG](Rewrite-1.3.2#the-dags-board-actions), [The DAG's state, commands and placement](Rewrite-1.3.1#pasting)) |
| Selection and the dock: a selected node shows its block in the active view through a `views$mod` of its own, and a pinned editor follows the selection through `sidebar_owned_by()` | 95 | Replaced by `core.show()` ([Plugins](Rewrite-1.1.12#showing-a-block-or-a-plugin)), and by `core.selection`, which the DAG sets and which the dock's pinned sidebar follows ([Board actions](Rewrite-1.1.16#the-advanced-action)) |
| Keyboard shortcuts: Ctrl with Backspace removes the selection, Ctrl or Cmd with C, X and V copy, cut and paste, and a drag with Alt held selects | 38, and 10 of JS | Carried over, bound by the DAG within its own element, with Cmd beside Ctrl for removing, as for copying ([Drawing the DAG](Rewrite-1.3.2#keys)) |
| Search and the outline of the board, g6R's `g6_search()` and `g6_outline()` | 27 | Carried over as the DAG's own components ([Drawing the DAG](Rewrite-1.3.2#search-and-the-outline)) |
| The empty board's line, "No blocks yet. Right-click to add one." | 18, and 8 of JS | Carried over ([Drawing the DAG](Rewrite-1.3.2#the-empty-board)) |
| Utilities and the hooks of the end-to-end tests | 78 | Dropped, with the tests that need them |
| The R option `blockr.dag.svg_renderer` and the options of g6R that the user guide documents | | Dropped with g6R |
| The vignettes: the user guide, and three on extending the context menu, the toolbar and the block callback | 492 | The user guide rewritten for the plugin, the three dropped with the hooks they document, and the migration notes added (Work) |
| The app scripts of the examples | 105 | Kept, changed as the migration notes say |
| The tests, which drive the DAG in a browser through shinytest2 | 2,757 | Replaced by tests of the plugin class on core's `CoreApi` for tests ([Plugins](Rewrite-1.1.12#testing)) and of its constructor in R |

## Proposal

- The DAG is a plugin of class `blockr.dag-dag_plugin`, named "Workflow", as today's extension is, whose class sets `state`, `update`, `start`, `ui`, `commands` and `boardActions`, and which works on the board through `CoreApi` alone ([Plugins](Rewrite-1.1.12#a-plugin)).
  It asks nothing of a frontend beyond what core's `PluginClass` holds, so every frontend places it as it places any plugin with a `ui`, the dock in a panel and core's basic frontend in a section ([Plugins](Rewrite-1.1.12#plugin-classes)).
  It gives R no requests, since it lives in the browser alone ([Plugins](Rewrite-1.1.12#a-plugins-requests)).
- Its state holds a position for every block and for every stack that holds no block, its layout's direction, spacing, placement and snapping, and which stacks are collapsed, so that a board reopens as the user left it, and app scripts write it through `new_dag_plugin()` and `dag_layout()` ([The DAG's state, commands and placement](Rewrite-1.3.1#the-state)).
  The `description` keywords of its schema tell the assistant what `dag_ext_meta()` tells it today, so that the assistant moves blocks through the DAG's commands or `blockr.core-set_plugin_state`, with no code of its own for the DAG ([Plugins](Rewrite-1.1.12#a-plugins-state)).
- The DAG places a block, or a stack that holds no block, that someone adds in the same step: at the point where the user right-clicked the canvas or dropped a link, or that the assistant gives, and otherwise through a placement strategy that keeps every other block where it is.
  It lays the whole board out again only when someone asks, through `blockr.dag-relayout`, where G6 lays the board out again as blocks come ([blockr.dag#40](https://github.com/BristolMyersSquibb/blockr.dag/issues/40)).
  Repulsion through d3-force, the default, starts a block near the blocks that it links to and pushes it off its neighbours, and Beside starts it after the blocks that it reads from ([The DAG's state, commands and placement](Rewrite-1.3.1#placing-added-blocks)).
  Repulsion also makes room around a stack that collapses or expands, and while the user has snapping on, every position that the DAG sets snaps to the snap size ([The DAG's state, commands and placement](Rewrite-1.3.1#how-the-dag-moves-blocks)).
- The DAG is drawn with React Flow (`@xyflow/react`), in place of G6.
  It is React, so a node is a component in the DAG's own React root that reads core's store, since the DAG's UI shares no React context with the dock's ([Plugins](Rewrite-1.1.12#plugin-classes)).
  Its nodes are elements of the page, so they take the design system's tokens from CSS, where today's canvas needs a script that resolves each token through a canvas of one pixel ([inst/assets/js/dag-chrome.js#L1-L25](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/inst/assets/js/dag-chrome.js#L1-L25)).
  Langflow, Flowise and Dify are built on it, and it is 88 KB gzipped at 13.0.0, against 400 KB for G6 (notes).
  The prototype [cynkra/blockr.react](https://github.com/cynkra/blockr.react) drew the DAG with React Flow as a dock extension, with links drawn by dragging, menus, and copy and paste (notes).
- React Flow lays nothing out ("We have not implemented our own layouting solution yet", [layouting](https://reactflow.dev/learn/layouting/layouting)), so the DAG lays blocks out with dagre, through `@dagrejs/dagre`, or with elkjs, as a spike decides before the rebuild, against criteria that the notes fix beforehand.
  Today's DAG lays its stacks out with dagre already, which keeps each stack's blocks together as a cluster ([R/layout.R#L80-L96](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/layout.R#L80-L96)).
  React Flow's docs warn that a dagre issue "prevents it from laying out sub-flows correctly" where a node in a group links to one outside it, but the issue concerns an edge from a node to the group that holds it ([dagre#238](https://github.com/dagrejs/dagre/issues/238)), and no link draws one, since a link joins two blocks.
  So the spike tries dagre first, at 16 KB gzipped, and elkjs, at 447 KB, only where dagre fails a criterion, in which case the DAG loads elkjs only when it lays blocks out, which drawing a saved board does not need.
- The DAG draws from the board alone, so that a change shows at once, whoever makes it, and its nodes draw their marks and status badges in core's tokens, as the dock's card does, without blockr.ui's code for now ([Drawing the DAG](Rewrite-1.3.2#nodes)).
  Stacks are group nodes, which the DAG collapses itself, since React Flow collapses nothing ([Drawing the DAG](Rewrite-1.3.2#stacks)).
- Its menus are core's menus of board actions, so that it draws no block picker and no editor of its own, and it registers board actions for copy, cut, paste and layout, which its toolbar offers beside its own controls, with every board action on the board or on the selection ([Drawing the DAG](Rewrite-1.3.2#the-dags-board-actions), [Board actions](Rewrite-1.1.16)).
  So the generics `context_menu_items()` and `toolbar_items()` go, since a package adds what it offers in a menu as a board action.
- Selecting a node shows its block through core's `show()`, where today the DAG sends the dock a `views$mod` of its own, and the DAG sets every selection in `core.selection`, which the dock's pinned sidebar follows, where today the DAG asks the dock's `sidebar_owned_by()` ([Drawing the DAG](Rewrite-1.3.2#gestures)).
- Its keys act on its own element alone, so that they never fire while the user types in a block's UI ([Drawing the DAG](Rewrite-1.3.2#keys)).
- On a locked board, the DAG offers nothing that the lock fixes, and keeps its blocks where they are unless the deployment sets the blockr option `lock_rearrange` to `FALSE`, as the dock keeps its panels, while collapsing a stack stays open ([The DAG's state, commands and placement](Rewrite-1.3.1#on-a-locked-board), [Drawing the DAG](Rewrite-1.3.2#on-a-locked-board)).
- Boards saved today cross through blockr.convert, whose method for the DAG's extension makes the plugin with `new_dag_plugin()`, and app scripts pass `new_dag_plugin()` in the board's `plugins` in place of `new_dag_extension()`, which goes without an alias ([The DAG's state, commands and placement](Rewrite-1.3.1#boards-saved-today), [Saved boards and app scripts across the switch](Rewrite-1.2.2#app-scripts), [State in JS](Rewrite-1#migration)).

## Open questions

None.

## Work

- Lay out the largest real board with dagre and with elkjs, draw it in React Flow with stacks that collapse, and make room around each stack through Repulsion as it collapses and expands, against the criteria in the notes, to decide between the two layouts and to check Repulsion, in blockr.dag
- Add `afterStep` to plugin classes, which the store calls once the last delta of a step is in and whose patches join the step, and name the parameter of `commands.run()` and `commands.plan()` `batch`, in blockr.core
- Have the description of `blockr.core-add_block` tell the assistant to link a block that reads from another in the same batch, so that the DAG places the block by its link, in blockr.core ([blockr.core#695](https://github.com/BristolMyersSquibb/blockr.core/issues/695))
- Make the DAG a plugin in R, with `new_dag_plugin()` and `dag_layout()`, the class listed in `._BLOCKR_MODULES_` and the JSON Schema of its state, in place of `new_dag_extension()`, in blockr.dag
- Build the DAG plugin's class in the client, with its state, its `update`, its `afterStep`, which places added blocks and stacks through the strategies Repulsion and Beside, and its commands for positions, layouts, snapping, collapsed stacks, which make room through Repulsion, and copy and paste, tested on core's `CoreApi` for tests, in blockr.dag
- Draw the board in the DAG, with blocks, their marks, ports and status badges, links, stacks that collapse and expand, zoom, pan, dragging, a selection that shows a block, search and the outline, in blockr.dag
- Open core's menus of board actions from the DAG's nodes, links, stacks, canvas and selection, register the DAG's board actions for copy, cut, paste and layout, draw its toolbar with the board actions on the board and on the selection, and bind its shortcuts, in blockr.dag
- Remove the extension, its R UI and server, g6R and the hooks of its menus, and rewrite the user guide for the plugin, in blockr.dag
- Write the migration notes for app scripts that use the DAG as a vignette, which lists each change that such a script needs, for an AI to apply, in blockr.dag

## Design pages

- [The DAG's state, commands and placement](Rewrite-1.3.1): the DAG plugin's state, its commands, its class's `update`, `afterStep` and `start`, how it moves blocks, placing added blocks, laying the board out again, collapsing and expanding a stack, snapping, pasting, the state in R, boards saved today, and the DAG's commands on a locked board
- [Drawing the DAG: nodes, links, stacks, menus and the toolbar](Rewrite-1.3.2): the canvas, nodes, links, stacks and how they collapse, gestures, the DAG's board actions, the toolbar, search and the outline, keys, the empty board, its look and the locked board

<details><summary>Notes for implementers</summary>

The rows of Today by file, at `898a097`: the extension and its state are `new_dag_extension()`, `dag_ext_meta()` and `dag_positions_description()` in `R/ext.R`, `setup_layout_ctrl()`, `push_layout()` and `setup_positions_ctrl()` in `R/srv.R`, and the position helpers of `R/g6r.R`; layouts are `R/layout.R` and `inst/assets/js/layout-menu.js`; drawing is the rest of `R/g6r.R` up to `g6_data_from_board()`, `R/graph.R`, `R/meta.R`, `R/ui.R`, `inst/assets/js/dag-chrome.js` and `inst/assets/css/dag.css`; following the board is `dag_ext_srv()` and `update_observer()` in `R/srv.R` and the proxy helpers of `R/g6r.R` from `remove_nodes()` to `update_combos()`; status badges are `extension_block_callback.dag_extension()` and `status_badges()` in `R/ext.R`; the context menu is `R/ctx.R` and `context_menu_items.dag_extension()`; the toolbar is `R/tool.R` and `toolbar_items.dag_extension()`; actions are `R/action.R` and `actions_observers()`; copy and paste are `R/subboard.R` and `inst/assets/js/copy-paste.js`; selection is `reveal_panel_delta()` and `setup_sidebar_retarget()` in `R/srv.R`; shortcuts are `setup_remove_elements_kbd()`, `setup_copy_paste_kbd()` and `inst/assets/js/rm-sel.js`; and the utilities are `R/utils.R` and `R/pkg.R`.

The prototype [cynkra/blockr.react](https://github.com/cynkra/blockr.react), of 2026-04-02 to 2026-07-22 at `e4e5c35`, is a dock extension that draws with React Flow 12 and lays out with dagre, which it runs on the blocks alone before it draws each stack's box around its blocks ([srcjs/DAGCanvas.jsx#L65-L148](https://github.com/cynkra/blockr.react/blob/e4e5c35ff8ae3759aa416a1870fb34360b8306d2/srcjs/DAGCanvas.jsx#L65-L148)).

The spike runs on the clinical data explorer's board, the largest of the five boards saved in blockr.sandbox, with 99 blocks and 108 links ([dev/json/cdex-board-latest.json](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/f938c30bad1710dd702024a8c96d03ed8a77f248/dev/json/cdex-board-latest.json)).
None of the five holds a stack, so the spike adds five to it, of 2 to 20 blocks each, some of them linked to blocks outside their stack.
Its criteria, fixed before it runs:

1. Laid out with each stack as a cluster that holds its blocks, the board has no two stacks that overlap, no block of another stack or of none inside a stack's box, and each link between a block in a stack and one outside it running from port to port.
2. The DAG collapses and expands every stack in React Flow: collapsed, the stack hides its blocks and their links end on the stack, and expanded, its blocks are back where they were.
3. The layout returns within one second, and React Flow draws the board no slower than today's DAG draws it, both measured on one machine, which the result names.

The DAG lays out with dagre where dagre meets all three, and with elkjs where dagre fails one that elkjs meets.

As the spike collapses and expands each of the five stacks, Repulsion makes room around it, and has to meet these criteria, fixed before it runs:

1. After any stack expands, no block overlaps another block, or the box of a stack that it is not in, with the spacing's gap.
2. No two blocks swap sides: a block that sat left of another, or above it, still does.
3. The further a block sits from the stack, the less it moves, and blocks beyond the reach of the moves stay where they are.
4. Collapsing a stack and expanding it again puts every block back within one gap of where it was.
5. The moves take less than 50 ms, on the machine that the result names.

Where Repulsion fails one, the result says which, and how the blocks move is settled again before the DAG's class is built.

The dock coupling to replace is listed in [Client-drawn dock](Rewrite-1.2).

Versions on npm on 2026-11-16: `@xyflow/react` 13.0.0 (MIT), released that day, `@dagrejs/dagre` 3.1.3 (MIT), of 2026-10-24, `elkjs` 0.12.1 (EPL-2.0 or GPL-3.0-or-later, so blockr.dag, GPL (>= 3), can bundle it under the GPL), `@antv/g6` 5.1.1 (MIT).
Weekly downloads for 2026-11-09 to 15: `@xyflow/react` 21.9 million, `elkjs` 20.9 million, `@dagrejs/dagre` 9.0 million, `@antv/g6` 325,000.
Gzipped sizes from bundlephobia: `@xyflow/react` 88 KB at 13.0.0 and 60 KB at 12.12.0, `@dagrejs/dagre` 16 KB, `elkjs` 447 KB and `@antv/g6` 400 KB.
Today's dagre is G6's, version 0.8.5 of the unscoped `dagre`, through `@antv/layout` 2.0.0, while `@dagrejs/dagre` is the line that the dagrejs organisation maintains.

Other libraries weighed and not chosen: Cytoscape.js 3.35.0 (MIT) has compound nodes and collapsing through an extension, but draws on a canvas and is made for network graphs, so marks, ports and badges would be HTML laid over the canvas, and links drawn by another extension; Rete.js 2.0.6 (MIT) is a node editor with ports that React can draw, with 135,000 weekly downloads and no release of its core since 2025-06-30; and `@joint/core` 4.3.4 (MPL-2.0) and `@maxgraph/core` 0.25.1 (Apache-2.0) draw diagrams in SVG from models of their own, which React Flow's nodes, plain React components, do not need.

</details>
