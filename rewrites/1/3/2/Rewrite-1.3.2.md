# Drawing the DAG: nodes, links, stacks, menus and the toolbar
Status: review. Design for [Client-drawn DAG](Rewrite-1.3).

One of the design pages of the client-drawn DAG ([Client-drawn DAG](Rewrite-1.3)): how the DAG draws the board with React Flow, its nodes, links and stacks, the gestures on them, the menus of board actions that it opens, its own board actions, its toolbar, search and the outline, its keys, its look and the DAG on a locked board.
It shapes the Work items of [Client-drawn DAG](Rewrite-1.3#work) that draw the board, open its menus, register its board actions and draw its toolbar, and the spike's drawing of stacks that collapse.
What the DAG keeps and the commands that change it are [The DAG's state, commands and placement](Rewrite-1.3.1)'s, and what a board action is, with the menus that offer one, is [Board actions](Rewrite-1.1.16)'s.

## What must hold

Conditions 1, 3 and 5 of [Client-drawn DAG](Rewrite-1.3#what-must-hold) rest on this page.

1. The DAG draws every node, link and stack from the board and from its state alone, and follows `store.subscribe()`, so that every change shows at once, whoever makes it.
2. Every menu that the DAG opens offers what every menu of the same object offers, and every gesture that edits runs a board action or a command, as one undo step.
3. A node's mark and status badge show the same colours as the dock's card shows for the same block.
4. What today's DAG lets a user do carries over: zoom, pan and fit, dragging blocks, selecting by a click and by a rectangle, drawing a link by dragging, dropping a link on the canvas to add a block, a link's label on hover, collapsing and expanding stacks, the menus, the toolbar, search and the outline, copy, cut and paste, and the keys.
5. The DAG's keys act only while the keyboard's focus is within the DAG, and never while the user types in a field.
6. On a locked board, the DAG offers no control for what the lock fixes.

## Proposal

### The canvas

The DAG's `ui` module draws React Flow in a React root of its own, on the one copy of React that core ships ([UI modules in JS](Rewrite-1.1.7#react)).
The canvas fills the element that the frontend gives the module, and sizes itself from it ([Places the dock offers plugins](Rewrite-1.2.4#a-plugins-panel)).
It fits the view to the board once, as it mounts, and never again by itself, since fitting on every change of the nodes moved the view under the user in the prototype (notes).
A drag on the canvas pans it, the wheel zooms it, and the toolbar zooms and fits it (The toolbar).

The nodes, links and groups that React Flow draws are made from the board and the DAG's state on every change.
React Flow holds a node's position by itself only while the user drags the node, until the drag ends and the DAG runs `blockr.dag-change_position` (Gestures).

### Nodes

Each block is a node:

- Its mark, 32 px across, is the icon of its class's entry in the block registry on a tint of its category's colour, from core's token, as `--bc-color-category-input` ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
  The block's name shows below the mark, as today.
- The status dot sits on the mark's upper right corner, filled or a ring as the table of [Block cards in the dock](Rewrite-1.2.7#the-status-dot) says, in the colour of core's token for the status, as `--bc-color-status-failed`, with the table's tooltip.
  It follows `scheduler.subscribe()`, and the DAG demands no block for it ([Evaluation in the client](Rewrite-1.1.10#demand)).
- It has a handle for each data input of its class, named after the input, or one for a variadic block, which takes any number of links, and one handle for its result.
  From top to bottom, the inputs sit on top and the result at the bottom, and from left to right on the left and the right, as today's layout menu turns the ports.

A node's place is its position in the DAG's state, the centre of the node, less half the node's size, since React Flow places a node by its top left corner ([The DAG's state, commands and placement](Rewrite-1.3.1#the-state)).
A node in a stack is placed relative to the stack's group, as React Flow places a node with a `parentId` ([sub flows](https://reactflow.dev/learn/layouting/sub-flows)).

### Links

Each link is an edge from the result of the block that it comes from into the handle of the input that it feeds.
It is a curve that runs downwards from top to bottom and sideways from left to right, as today's.
The input's name shows on the edge while the pointer is over it, as today's label does.

### Stacks

Each stack is a group node behind its blocks, in the colour that core keeps on the stack, with its name above it ([Board objects](Rewrite-1.1.1#stacks)).
Its box fits its blocks, with the padding that the layout gives a cluster ([The DAG's state, commands and placement](Rewrite-1.3.1#laying-the-board-out-again)).

A stack that the DAG's state names in `collapsed` shrinks to a box that holds its name and the number of its blocks.
Its blocks hide, and each link from or into one of them ends on the box.
Expanding it brings its blocks back where they were, since their positions never changed.
A double click on the stack's box, or its collapse control, runs `blockr.dag-collapse_stack`, which takes no undo step.
React Flow collapses nothing itself, and its example of it is one of its paid examples, so this is the DAG's own code ([Expand and Collapse](https://reactflow.dev/examples/layout/expand-collapse)).

A block that the user drags onto another stack's box joins that stack, through `blockr.core-change_stack`, with its move in the same step.
A block that the user drags out of its stack's box stays in the stack, whose box grows, as today's does ([blockr.dag#38](https://github.com/BristolMyersSquibb/blockr.dag/issues/38)), and leaves the stack through Edit stack ([Board actions](Rewrite-1.1.16#cores-board-actions)).

### Gestures

- Dragging a node, or the selected nodes, moves them, and as the drag ends the DAG runs `blockr.dag-change_position` with every block that moved, as one step.
- Dragging from a block's result to another block's input draws a link through `blockr.core-add_link`.
  React Flow refuses the connection where the link would close a cycle, join a block to itself or feed an input that a link feeds already, by the checks of core's Create link ([Board actions](Rewrite-1.1.16#cores-board-actions)).
- Dropping a link on the canvas triggers Append block from a block's result, or Prepend block from an input, at the drop.
  The DAG runs the placement with the drop as the new block's preferred start, and adds `blockr.dag-change_position` with the result to the board action's step ([The DAG's state, commands and placement](Rewrite-1.3.1#placing-added-blocks)).
- A click selects a node, a link or a stack, Shift or Cmd with a click adds to the selection, a drag with Alt held selects what its rectangle covers, as today, and a click on the canvas clears the selection.
- A selection of one node shows its block through `core.show()`, which every frontend carries out in its own way, the dock in the active view ([Plugins](Rewrite-1.1.12#showing-a-block-or-a-plugin)), while a selection of several shows none, as today.
- Every selection goes to `core.boardActions.select()`, which a pinned advanced action follows ([Board actions](Rewrite-1.1.16#the-advanced-action)).
- A right click on a node, a link, a stack, the canvas or the selection opens that object's menu through `core.boardActions.menu()`, at the pointer ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).

### The DAG's board actions

The DAG registers four board actions, beside core's, which every menu of their objects offers ([Board actions](Rewrite-1.1.16#a-board-action)):

| Board action | On | Group | What it does |
|---|---|---|---|
| Copy | A block, a stack or a selection | Clipboard | Puts on the clipboard a JSON board of the blocks, the links between them, the stacks that they fill and their positions, and acts at once |
| Cut | A block, a stack or a selection | Clipboard | Copies, then runs core's commands that remove them, as one step |
| Paste | The board | Clipboard | Reads the clipboard and runs `blockr.dag-paste` with what it holds, at the point where the menu opened, or at the middle of the view from the toolbar or a key |
| Layout | The board | Edit | Its quick action offers Lay out again, the two directions, the three spacings and the two placements, which run `blockr.dag-relayout` or, for a placement, `blockr.dag-set_placement` ([The DAG's state, commands and placement](Rewrite-1.3.1#commands)) |

Copy writes to the system's clipboard within the user's gesture, which Safari requires, since the selection is at hand in the client, where today's copy waits for R to send it ([inst/assets/js/copy-paste.js](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/inst/assets/js/copy-paste.js)).
It also keeps the last copy for the page, which Paste reads where the browser refuses to read the system's clipboard, as Safari and headless browsers do, while the system's clipboard carries a copy to another tab or app.
So Paste reads the clipboard before it returns its command, and its `run` returns a promise ([Board actions](Rewrite-1.1.16#a-board-action)).

### The toolbar

The toolbar floats at the canvas's top left, as today, and holds, in this order:

1. The DAG's own controls: search, zoom in, zoom out and fit.
2. A button for each board action on the board: core's Add block and Create stack, and the DAG's Paste and Layout.
3. While the user has selected something, a button for each board action on the selection, such as core's Remove and Create stack and the DAG's Copy and Cut.

Each button shows its board action's icon, has the board action's label as its tooltip, and opens its quick action below it, or runs it where it asks nothing ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).
A board action that another package registers on the board or on a selection gets a button too, as it gets a row in the DAG's menus.

### Search and the outline

Search and the outline of the board carry over as components of the DAG, in place of g6R's `g6_search()` and `g6_outline()`, and name things as the board does: block, stack and link.

- The search narrows to the blocks and stacks whose name or id holds what the user types, the stacks first, and picking one moves the view to it, selects it and shows its block.
- The outline, "Board contents", lists each stack as a row that folds, with its blocks in the order of their links and their number, and the blocks in no stack, and folding a row leaves the canvas alone.
- Searching for a block in a collapsed stack expands the stack, through `blockr.dag-collapse_stack`.

### Keys

The DAG binds its keys on its own element, since they act on its selection, which it alone holds, so that they never fire while the user types in a block's UI, as listeners on the whole document did in the prototype (notes):

- Backspace or Delete triggers Remove on the selection.
- Cmd or Ctrl with C, X and V triggers Copy, Cut and Paste, but for C and X while the user has selected text, which the browser copies as usual, as today's copy does.
- Escape clears the selection.

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
Zoom, pan, fit, selection, search, the outline and collapsing a stack work as on any board.
Its menus and toolbar offer only the board actions that the lock leaves ([Board actions](Rewrite-1.1.16#cores-board-actions)).

### Testing

The DAG's components run on happy-dom with core's `CoreApi` for tests, with the stand-ins for `ResizeObserver` and `DOMMatrixReadOnly` that React Flow's guide gives for a page that measures nothing ([testing](https://reactflow.dev/learn/advanced-use/testing)), while the gestures that drag run in a browser, as the guide advises.

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's behaviors in g6R are `zoom_canvas()`, `drag_canvas()`, `drag_element()`, `click_select(multiple = TRUE)`, `brush_select()` with Alt, `collapse_expand()`, `hover_activate()` for a link's label and `create_edge()`, and its plugins a context menu, a toolbar, the search and the outline ([R/g6r.R#L284-L460](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/g6r.R#L284-L460)).
A link dropped on the canvas appends a block to the node that it starts from, or prepends one where it starts from an input, through the "+" menu at the drop.

The context menu's entries by target, which board actions take over: on a block, Create link, Remove block, Append block, Edit inputs, Copy and Cut; on a link, Remove link, Edit link and Insert block; on a stack, Remove stack, Edit stack, Copy and Cut; and on the canvas, Add block, Create stack and Paste ([R/ext.R#L118-L419](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L118-L419)).
The toolbar's items: search, zoom in, zoom out, fit, the layout menu, add a block, add a stack and remove the selection ([R/ext.R#L422-L517](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L422-L517)).
Today's layout menu turns a node's ports to its sides from left to right, and draws links as horizontal curves ([inst/assets/js/layout-menu.js](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/inst/assets/js/layout-menu.js)).

The prototype [cynkra/blockr.react](https://github.com/cynkra/blockr.react), at `e4e5c35`, holds the findings that this page takes over: keys bound on the canvas rather than the document, since a listener on the document fired Delete while the user edited an input and took copies of selected text; a clipboard of its own beside the system's, since `navigator.clipboard.readText()` fails in Safari and in headless browsers; and `fitView` once on mount, since the prop fits the view again on every change of the nodes.
React Flow 13.0.0 drops the rule that a group come before its nodes, which the prototype ordered by hand, and adds `changeParent()`, which moves a node into a group or out of it without computing its new position, which the prototype did by hand.

</details>
