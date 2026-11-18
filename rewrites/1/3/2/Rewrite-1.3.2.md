# Drawing the DAG: nodes, links, stacks, menus and the toolbar
Status: review. Design for [Client-drawn DAG](Rewrite-1.3).

One of the design pages of the client-drawn DAG ([Client-drawn DAG](Rewrite-1.3)): how the DAG draws the board with React Flow, its nodes, links and stacks, the gestures on them, the menus of board actions that it opens, its own board actions, its toolbar, search and the outline, its keys, its look and the DAG on a locked board.
It shapes the Work items of [Client-drawn DAG](Rewrite-1.3#work) that draw the board, open its menus, register its board actions and draw its toolbar, and the spike's drawing of stacks that collapse.
What the DAG keeps and the commands that change it are [The DAG's state, commands and placement](Rewrite-1.3.1)'s, and what a board action is, with the menus that offer one, is [Board actions](Rewrite-1.1.16)'s.

## What must hold

Conditions 1, 3 and 5 of [Client-drawn DAG](Rewrite-1.3#what-must-hold) rest on this page.

1. The DAG draws every node, link and stack from the board and from its state alone, and follows `store.subscribe()`, so that every change shows at once, whoever makes it.
2. Every menu that the DAG opens offers what every menu of the same object offers, and every gesture that changes the board runs a board action or a command, as one step.
3. A node's mark and status badge show the same colours as the dock's card shows for the same block.
4. What today's DAG lets a user do carries over, but for what [Client-drawn DAG](Rewrite-1.3#today) drops: zoom, pan and fit, dragging blocks, selecting by a click and by a rectangle, drawing a link by dragging, dropping a link on the canvas to add a block, a link's label on hover, collapsing and expanding stacks, the menus, the toolbar, search and the outline, copy, cut and paste, and the keys.
5. The DAG's keys act only while the keyboard's focus is within the DAG, and never while the user types in a field.
6. On a locked board, the DAG offers no control for what the lock fixes.

## Proposal

### The canvas

The DAG's `ui` module draws React Flow in a React root of its own, on the one copy of React that core ships ([UI modules in JS](Rewrite-1.1.7#react)).
The canvas fills the element that the frontend gives the module, and sizes itself from it ([Places the dock offers plugins](Rewrite-1.2.4#a-plugins-panel)).
It fits the view to the board once, as it mounts, and never again by itself, since fitting on every change of the nodes moved the view under the user in the prototype (notes).
A drag on the canvas pans it, the wheel zooms it, and the toolbar zooms and fits it (The toolbar).

The nodes, links and group nodes that React Flow draws are made from the board and the DAG's state on every change.
While the user drags a node, React Flow reports each move through `onNodesChange`, and the DAG keeps the new positions in its component alone.
As the drag ends, the DAG runs `blockr.dag-change_position` once, so that a drag is one step (Gestures).

### Nodes

Each block is a node:

- Its mark, 32 px across, is the icon of its class's entry in the block registry on a tint of its category's colour, from core's token, as `--bc-color-category-input` ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
  The block's name shows below the mark, as today.
- The status dot sits on the mark's upper right corner, filled or a ring as the table of [Block cards in the dock](Rewrite-1.2.7#the-status-dot) says, in the colour of core's token for the status, as `--bc-color-status-failed`, with the table's tooltip.
  The DAG works the dot out from the block's status and the notifications that concern the block, through its copy of the dock's function, which a test checks against that table.
  So the dot reads `failed` where an error about the block's output concerns the block, as the card's dot does.
  It follows `scheduler.subscribe()` and the notifications of `CoreApi`, and the DAG demands no block for it ([Evaluation in the client](Rewrite-1.1.10#demand)).
- It has a handle for each data input of its class, named after the input, or one for a variadic block, which takes any number of links, and one handle for its result.
  From top to bottom, the inputs sit on top and the result at the bottom, and from left to right on the left and the right, as today's layout menu turns the ports.

A node's box is its mark, and the block's name hangs below the box, as G6 draws today's label outside the node.
So the centre of the box is the block's position in the DAG's state, as the centre of today's node is, and a converted position keeps its meaning ([The DAG's state, commands and placement](Rewrite-1.3.1#the-state)).
React Flow places a node by its top left corner, so the DAG places the node 16 px left of the position and 16 px above it.
A node in a stack is placed relative to the stack's group node, as React Flow places a node with a `parentId` ([sub flows](https://reactflow.dev/learn/layouting/sub-flows)).

### Links

Each link is an edge from the result of the block that it comes from into the handle of the input that it feeds.
It is a curve with an arrow at its end, which runs downwards from top to bottom and sideways from left to right, as today's.
The input's name shows on the edge while the pointer is over it, as today's label does.

### Stacks

Each stack is a group node behind its blocks, in the colour that core keeps on the stack, with its name above it.
A stack whose `color` is `null` takes the theme's colour for borders, a default of the DAG's own ([Board objects](Rewrite-1.1.1#stacks)).
Its box fits its blocks, with the padding that the layout gives a cluster ([The DAG's state, commands and placement](Rewrite-1.3.1#laying-the-board-out-again)).
A stack that holds no block shows as a box that holds its name and the number of its blocks, as a collapsed stack does, at its position in the DAG's state ([The DAG's state, commands and placement](Rewrite-1.3.1#the-state)).
A block dropped on that box joins the stack, whose box then fits the block.

A stack that the DAG's state names in `collapsed` shrinks to a box that holds its name and the number of its blocks, centred where its expanded box is.
Its blocks hide, and each link from or into one of them ends on the box.
Dragging the small box moves the stack's hidden blocks by the same distance, in one `blockr.dag-change_position`, so that the stack expands around where the box sits.
Expanding it brings its blocks back where they were in the stack, while the blocks around the stack move to make room, as they close up on a stack that collapses ([The DAG's state, commands and placement](Rewrite-1.3.1#collapsing-and-expanding-a-stack)).
A double click on the stack's box, or its collapse control, runs `blockr.dag-collapse_stack`.
It takes an undo step, since it moves the blocks around the stack, so one undo collapses or expands the stack again and puts every block back ([The DAG's state, commands and placement](Rewrite-1.3.1#collapsing-and-expanding-a-stack)).
React Flow collapses nothing itself, and its example of it is one of its paid examples, so this is the DAG's own code ([Expand and Collapse](https://reactflow.dev/examples/layout/expand-collapse)).

A block that the user drops on the box of a stack that it is not in joins that stack, through `blockr.core-change_stack`, with its move in the same step.
A block that the user drags out of its stack's box stays in the stack, whose box grows, as today's does ([blockr.dag#38](https://github.com/BristolMyersSquibb/blockr.dag/issues/38)), and leaves the stack through Edit stack ([Board actions](Rewrite-1.1.16#cores-board-actions)).

### Gestures

- Dragging a node, the selected nodes or a stack's box moves them, a stack with its blocks, as today.
  While snapping is on, the drag snaps each position to a multiple of the snap size as it moves (notes).
  As the drag ends, the DAG runs `blockr.dag-change_position` with every block that moved, and with a stack without blocks that moved, as one step.
- Dragging from a block's result to another block's input, or from an input to another block's result, draws a link, as today's ports do.
  The DAG checks nothing while the user drags.
  As the user drops the link on a handle, the DAG runs `blockr.core-add_link`, whose preflight refuses a link that would close a cycle, join a block to itself or feed an input that a link feeds already ([Board actions](Rewrite-1.1.16#cores-board-actions)).
  Where the command is refused, the board gains no link, so the DAG draws none.
  The DAG then shows the user why where the link was dropped, with the reason that the refusal gives, as every plugin with a UI shows what fails of what the user did in it, and takes the command's notifications through its `notifier`, so that core raises none ([Notifications, logging and tracing](Rewrite-1.1.14#taking-a-calls-notifications)).
- Dropping a link on the canvas, away from every node and stack, triggers Append block from a block's result, or Prepend block from an input, at the drop.
  The DAG adds `blockr.dag-change_position` with the drop to the board action's step, through `trigger()`'s `extend`, so that the new block lands at the drop ([The DAG's state, commands and placement](Rewrite-1.3.1#placing-added-blocks)).
  A link dropped on a node or on a stack's box, away from its handles, adds nothing, as today's does.
- A click selects a node, a link or a stack, and a click on the canvas clears the selection.
  A click with Shift adds to the selection, as today.
  A drag with Alt held selects what its rectangle covers, as today.
- A selection of one node shows its block through `core.show()`, which every frontend carries out in its own way, the dock in the active view ([Plugins](Rewrite-1.1.12#showing-a-block-or-a-plugin)), while a selection of several shows none, as today.
- Every selection goes to `core.boardActions.select()`, which a pinned advanced action follows ([Board actions](Rewrite-1.1.16#the-advanced-action)).
- A right click on a node, a link, a stack or the canvas opens that object's menu through `core.boardActions.menu()`, at the pointer ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).
  Where the object belongs to a selection of several, the right click opens the selection's menu instead, and so does a right click on the box that React Flow draws around a selection.
  For the canvas, the DAG passes `menu()` an `extend` that puts each block, or stack that holds no block, that the board action adds where the user right-clicked, through `blockr.dag-change_position` ([The DAG's state, commands and placement](Rewrite-1.3.1#placing-added-blocks)).

### The DAG's board actions

The DAG registers four board actions, beside core's, which every menu of their objects offers ([Board actions](Rewrite-1.1.16#a-board-action)):

| Board action | On | Group | What it does |
|---|---|---|---|
| Copy | A block, a stack or a selection | Clipboard | Puts on the clipboard, at once, a JSON board of the blocks and stacks that it acts on, the blocks of those stacks, the links between those blocks, any other stack that holds a block and whose blocks are all copied, and their positions, as today's copy does |
| Cut | A block, a stack or a selection | Clipboard | Copies, then runs core's commands that remove them, as one step |
| Paste | The board | Clipboard | Reads the clipboard and runs `blockr.dag-paste` with what it holds, at the point where the menu opened, or at the middle of the view from the toolbar or a key |
| Layout | The board | Edit | Its quick action offers Lay out again, the two directions and the three spacings, which run `blockr.dag-relayout`, the two placements, Repulsion and Beside, which run `blockr.dag-set_placement`, and snapping, on or off and with its snap size, which run `blockr.dag-set_snap` ([The DAG's state, commands and placement](Rewrite-1.3.1#commands)) |

Copy writes to the system's clipboard within the user's gesture, as Safari requires.
The selection is at hand in the client, so Copy writes it at once, where today's copy starts a write that waits for R to send the board ([inst/assets/js/copy-paste.js](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/inst/assets/js/copy-paste.js)).
Copy also keeps its last copy for the page.
Paste reads the system's clipboard, which carries a copy from another tab or app.
Where the browser refuses to read it, as Safari and headless browsers do, Paste takes the page's last copy instead.
Paste leaves the board alone where the text it reads is no JSON board, as today's paste does.
Paste reads the clipboard before it returns its command, so its `run` returns a promise ([Board actions](Rewrite-1.1.16#a-board-action)).

### The toolbar

The toolbar floats in a column at the canvas's top left, as today, and holds, in this order:

1. The DAG's own controls: search, zoom in, zoom out and fit.
2. A button for each board action on the board: core's Add block and Create stack, and the DAG's Paste and Layout.
3. While the user has selected something, a button for each board action on the selection, such as core's Remove and Create stack and the DAG's Copy and Cut.

Each button shows its board action's icon, has the board action's label as its tooltip, and opens its quick action below it, or runs it where it asks nothing ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).
A board action that another package registers on the board or on a selection gets a button too, as it gets a row in the DAG's menus.
A block, or a stack that holds no block, that the toolbar's Add block or Create stack adds starts from the middle of the view, where the DAG runs the placement strategy for it ([The DAG's state, commands and placement](Rewrite-1.3.1#placing-added-blocks)).

### Search and the outline

Search and the outline of the board carry over as one panel of the DAG, in place of g6R's `g6_search()` and `g6_outline()`, and name things as the board does: block, stack and link.
The toolbar's search button opens the panel beside the toolbar, and Escape, a click outside the panel or a pick closes it, as today.

- A field at the top narrows the panel to the blocks and stacks whose name or id holds what the user types, the stacks first.
- Below the field, the outline, "Board contents", lists each stack as a row that folds, with its blocks in the order of their links and the number of its blocks, and then the blocks in no stack.
- Picking a row moves the view to the block or the stack and selects it, so that picking a block shows it, as a click on its node does.
  Picking a block of a collapsed stack expands the stack first, through `blockr.dag-collapse_stack`, as today's search does.
  The expand moves the blocks around the stack and takes an undo step, as any expand does (Stacks).
- A stack that is collapsed on the canvas shows folded in the outline, while folding a row leaves the canvas alone, as today.

### Keys

The DAG binds its keys on its own element rather than on the whole document.
They act on the DAG's selection, which only the DAG holds.
So they never fire while the user types in a block's UI, as the prototype's listeners on the whole document did (notes):

- Cmd or Ctrl with Backspace triggers Remove on the selection.
  Today only Ctrl with Backspace does, and Cmd joins it, as it does for copying.
- Cmd or Ctrl with C, X and V triggers Copy, Cut and Paste, but for C and X while the user has selected text, which the browser copies as usual, as today's copy does.

Undo and redo are the frontend's keys, since the store keeps one history for the page ([Board updates](Rewrite-1.1.2#undo)).

### The empty board

While the board holds no block, the canvas says "No blocks yet.
Right-click to add one.", in the design system's style for an empty place, as today.

### Its look

The DAG takes the design system's colours from core's tokens, without blockr.ui's code for now ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)): the category and status tokens for its nodes, and the theme's tokens for surfaces, text and borders, from which it sets React Flow's own styles.
It follows the theme that core's board option `dark_mode` switches the page to.
It draws its tooltips in the design system's style, as the dock draws its own, until blockr.ui offers them in one module with the mark and the status dot ([UI kit and design system for the client](Rewrite-1.7)).
Core or the frontend draws its menus and quick actions ([Board actions](Rewrite-1.1.16#what-a-frontend-gives)).

### On a locked board

Under the board lock, the DAG draws no link from a drag, drops no block into a stack, and drags no node unless the blockr option `lock_rearrange` is `FALSE` ([The DAG's state, commands and placement](Rewrite-1.3.1#on-a-locked-board)).
Zoom, pan, fit, selection, search, the outline and collapsing a stack work as on any board, while collapsing or expanding a stack moves no other block there ([The DAG's state, commands and placement](Rewrite-1.3.1#on-a-locked-board)).
Its menus and toolbar offer only the board actions that the lock leaves ([Board actions](Rewrite-1.1.16#cores-board-actions)).
Of the DAG's own, Copy stays, Cut and Paste fail their `offers`, since the store refuses what they run, and Layout fails it unless `lock_rearrange` is `FALSE`.

### Testing

The DAG's components run on happy-dom with core's `CoreApi` for tests, with the stand-ins for `ResizeObserver` and `DOMMatrixReadOnly` that React Flow's guide gives for a page that measures nothing ([testing](https://reactflow.dev/learn/advanced-use/testing)), while the gestures that drag run in a browser, as the guide advises.

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's behaviors in g6R are `zoom_canvas()`, `drag_canvas()`, `drag_element()`, `click_select(multiple = TRUE)`, `brush_select()` with Alt, `collapse_expand()`, `hover_activate()` for a link's label and `create_edge()`, and its plugins a context menu, a toolbar, the search and the outline ([R/g6r.R#L284-L460](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/g6r.R#L284-L460)).
On a node with links out of it, `collapse_expand()` and the node's collapse button hide the blocks downstream of the node, which the DAG drops ([Client-drawn DAG](Rewrite-1.3#today)).
A link dropped on the canvas appends a block to the node that it starts from, or prepends one where it starts from an input, through the "+" menu at the drop.

The context menu's entries by target, which board actions take over: on a block, Create link, Remove block, Append block, Edit inputs, Copy and Cut; on a link, Remove link, Edit link and Insert block; on a stack, Remove stack, Edit stack, Copy and Cut; and on the canvas, Add block, Create stack and Paste ([R/ext.R#L118-L419](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L118-L419)).
The toolbar's items: search, zoom in, zoom out, fit, the layout menu, add a block, add a stack and remove the selection ([R/ext.R#L422-L517](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L422-L517)).
Today's layout menu turns a node's ports to its sides from left to right, and draws links as horizontal curves ([inst/assets/js/layout-menu.js](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/inst/assets/js/layout-menu.js)).
Search and the outline are one panel today, which the toolbar's "Search blocks" opens beside the toolbar, since `g6_outline()` hangs under `g6_search(collapsed = TRUE)` ([R/g6r.R#L426-L447](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/g6r.R#L426-L447), [inst/assets/css/dag.css#L116-L130](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/inst/assets/css/dag.css#L116-L130)).
Search expands a collapsed stack as today's does, although expanding now moves the blocks around the stack, so the issue that builds search tries it on the largest board that blockr.sandbox saves, with stacks added as for the spike ([Client-drawn DAG](Rewrite-1.3#work)).
Today's keys listen on the whole document.
Ctrl with Backspace removes the selection, even while the user types in a field ([inst/assets/js/rm-sel.js](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/inst/assets/js/rm-sel.js)).
Ctrl or Cmd with C, X and V copy, cut and paste outside fields, but for C and X while the page holds selected text ([inst/assets/js/copy-paste.js](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/inst/assets/js/copy-paste.js)).

The prototype [cynkra/blockr.react](https://github.com/cynkra/blockr.react), at `e4e5c35`, holds the findings that this page takes over: keys bound on the canvas rather than the document, since a listener on the document fired Delete while the user edited an input and took copies of selected text; a clipboard of its own beside the system's, since `navigator.clipboard.readText()` fails in Safari and in headless browsers; and `fitView` once on mount, since the prop fits the view again on every change of the nodes.
React Flow 13.0.0 drops the rule that a group come before its nodes, which the prototype ordered by hand, and adds `changeParent()`, which moves a node into a group or out of it without computing its new position, which the prototype did by hand.

React Flow 13.0.0 binds keys of its own: Backspace removes what is selected, Shift with a drag draws the selection's rectangle, and Cmd on a Mac or Ctrl elsewhere adds to a selection ([src/container/ReactFlow/index.tsx#L67-L73](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/react/src/container/ReactFlow/index.tsx#L67-L73)).
So the DAG sets `deleteKeyCode` to `null`, `selectionKeyCode` to `"Alt"` and `multiSelectionKeyCode` to `"Shift"`.
A drag snaps through React Flow's props `snapToGrid` and `snapGrid`, which the DAG sets while the layout's `snap` is on, with `snapGrid` at `[snap_size, snap_size]`.
React Flow's rectangle selects every link of each node that it covers, links to nodes outside it among them ([src/container/Pane/index.tsx#L241-L254](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/react/src/container/Pane/index.tsx#L241-L254)).
So the DAG keeps only the links whose two blocks the rectangle covers.
The DAG gives React Flow no `isValidConnection`, so React Flow, in its default strict mode, takes a link from any result to any input, or from an input to a result, and leaves the rest to `blockr.core-add_link`.
A drop that reaches no handle comes to `onConnectEnd`, which the DAG takes for a drop on the canvas only where no node lies under the pointer.
Since 13.0.0, React Flow's `onConnectEnd` gives the point where a link was dropped in the canvas's coordinates, which is where the new block lands ([xyflow#6117](https://github.com/xyflow/xyflow/pull/6117)).
The quick action opens at the pointer's place on the screen, which the event gives.

React Flow 13.0.0 sets `color-scheme: light dark` on its root, so that it follows the system's theme unless an ancestor carries `data-theme` or the class `dark` or `light`, or its prop `forceColorMode` sets one ([packages/system/src/styles/init.css#L3-L48](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/system/src/styles/init.css#L3-L48)).
Core switches the theme through the attribute `data-bc-theme` on the page's root instead, in `setTheme()` of `srcts/options/options.ts` on blockr.core's `js-state` at `7fd739c`.
So the DAG's stylesheet sets the canvas's `color-scheme` from that attribute.
The stylesheet's rules win over React Flow's, which 13.0.0 puts in the cascade layer `xyflow` ([xyflow#5844](https://github.com/xyflow/xyflow/pull/5844)).

</details>
