# Drawing the DAG: nodes, links, stacks, menus and the toolbar
Status: settled on 2026-11-22. Design for [Client-drawn DAG](Rewrite-1.3).

One of the design pages of the client-drawn DAG ([Client-drawn DAG](Rewrite-1.3)): how the DAG draws the board with React Flow, its nodes, links and stacks, the gestures on them, the menus of board actions that it opens and where their advanced actions show, its own board actions, its toolbar, search and the outline, its keys, its look and the DAG on a locked board.
It shapes the Work items of [Client-drawn DAG](Rewrite-1.3#work) that draw the board, open its menus, register its board actions and draw its toolbar, and the item that lets a row of a quick action show a check.
What the DAG keeps and the commands that change it are [The DAG's state, commands and placement](Rewrite-1.3.1)'s, and what a board action is, with the menus that offer one, is [Board actions](Rewrite-1.1.16)'s.

## What must hold

Conditions 1, 3 and 5 of [Client-drawn DAG](Rewrite-1.3#what-must-hold) rest on this page.
Conditions 2 and 7 rest on this page and on [The DAG's state, commands and placement](Rewrite-1.3.1) together.

1. The DAG draws every node, link and stack from the board and from its state alone, and follows `store.subscribe()`, so that every change shows at once, whoever makes it.
   The nodes that the user drags are the exception: they follow the pointer until the drag ends.
2. Every menu that the DAG opens offers what every menu of the same object offers, and every gesture that changes the board runs a board action or a command, as one step.
3. A node's mark and status dot show the same colours as the dock's card shows for the same block.
4. What today's DAG lets a user do carries over, but for what [Client-drawn DAG](Rewrite-1.3#today) drops: zoom, pan and fit, dragging blocks, selecting by a click and by a rectangle, drawing a link by dragging, dropping a link on the canvas to add a block, a link's label on hover, collapsing and expanding stacks, the menus, the toolbar, search and the outline, copy, cut and paste, and the keys.
5. The DAG's keys act only while the keyboard's focus is within the DAG, and never while the user types in a field.
6. Under the board lock, the DAG offers no control that adds, removes or renames a block or a stack, links two blocks, or changes which stack a block is in.
   Zoom, pan, fit, selection, search, the outline, moving blocks, collapsing and expanding stacks, laying the board out again and Copy work as on any board.
   The load lock and a block's lock change nothing in the DAG.

## Proposal

### The canvas

The DAG's `ui` module draws React Flow in a React root of its own, on the one copy of React that blockr.ui ships ([UI modules in JS](Rewrite-1.1.7#react)).
The canvas fills the element that the frontend gives the module, and sizes itself from it ([Places the dock offers plugins](Rewrite-1.2.4#a-plugins-panel)).
Core's basic frontend gives a plugin's section no height of its own, so there the canvas takes a height of its own (notes).
A drag on the canvas pans it, the wheel zooms it, and the toolbar zooms and fits it (The toolbar).

The DAG fits the view to the board as it first mounts on a board, at most at 100%, so that no block shows larger than its size.
On a board that opened without positions, it fits once the DAG's `start` has placed the blocks, since `start` runs after the DAG mounts ([The DAG's state, commands and placement](Rewrite-1.3.1#starting-on-a-board)).
It fits the view again once the user lays the board out again through Layout (The DAG's board actions), as today's DAG fits after each layout.
It fits on no other change, since fitting on every change of the nodes moved the view under the user in the prototype (notes).
The DAG keeps the zoom and the pan for the page, by the board's id, and restores them when it mounts again on the same board, as when the dock redraws a view ([Places the dock offers plugins](Rewrite-1.2.4#a-plugins-panel)).
They stay out of the DAG's state, since what one user looks at is no part of the board.

The nodes, links and group nodes that React Flow draws are made from the board and the DAG's state on every change.
A block that has no position yet gets no node until it has one.
While the user drags a node, React Flow reports each move through `onNodesChange`, and the DAG keeps the new positions in its component alone.
As the drag ends, the DAG runs `blockr.dag-change_position` once, so that a drag is one step (Gestures).

### Nodes

Each block is a node:

- Its mark, 32 px across, is the icon of its class's entry in the block registry on a tint of its category's colour, from blockr.ui's theme, which holds one for each category ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
  The block's name shows below the mark, as today.
- The status dot sits on the mark's upper right corner, filled or a ring as the table of [Block cards in the dock](Rewrite-1.2.7#the-status-dot) says, in the colour of blockr.ui's theme for the status, with the table's tooltip.
  The DAG works the dot out from the block's status and the notifications that concern the block, through its copy of the dock's function, which a test checks against that table.
  So the dot reads `failed` where an error about the block's output concerns the block, as the card's dot does.
  It follows `scheduler.subscribe()` and the notifications of `CoreApi`, and the DAG demands no block for it ([Evaluation in the client](Rewrite-1.1.10#demand)).
- It has a handle for each data input of its class, named after the input, and one handle for its result.
  A variadic block, which takes any number of links, has a handle for each link into it instead, labelled with the link's name where it has one, as `b2` in `rbind(a, b2 = b)`, or else with its place, and a placeholder handle for its next place.
  A handle sits on the side of the mark that faces the block at the other end of its link, and moves as either block moves, so that the link stays short (Links).
  A handle with several links, as a result often has, shows on each side that one of them uses, and several handles on one side spread along it, those of a variadic block in the order of their links.
  A handle that no link uses, a variadic block's placeholder among them, sits on the side that the layout's direction gives, as today's ports do: from top to bottom, an input on top of the mark and the result below it, and from left to right, an input on the mark's left and the result on its right.
  A handle on the bottom sits below the block's name, so that no link crosses the name.
  While the pointer is over a handle, the handle grows and takes the theme's accent colour, the link that feeds it shows as it does while the pointer is over the link (Links), and after a moment blockr.ui's `Tooltip` names the input, as `data`, with its source where a link feeds it, as `data, from Filter`, or "Next input" on a variadic block's placeholder.
  A handle takes the pointer only within its own size and a small margin around it, never over the node's body, so that a press on the node lands on the node, and a press on a handle is one that the user saw coming.

A node's box is its mark, and the block's name hangs below the box, as G6 draws today's label outside the node.
React Flow places the node at the block's position in the DAG's state ([The DAG's state, commands and placement](Rewrite-1.3.1#the-state)).
For a node in a stack, the DAG gives React Flow that position relative to the stack's group node, as React Flow takes the position of a node with a `parentId` ([sub flows](https://reactflow.dev/learn/layouting/sub-flows)).

### Links

Each link is an edge from the result of the block that it comes from into the handle of the input that it feeds, or into its own handle on a variadic block.
It leaves the mark of the block that it comes from and enters the mark of the block that it feeds on the sides that face each other, so that it stays short wherever the user moves either block (Nodes).
So where block `b` reads from block `a` and the user drags `b` above `a`, the link leaves the top of `a` and enters the bottom of `b`.
Today's link would loop around both blocks there.
It is a curve with an arrow at its end, as today's.
The input's name shows on the edge while the pointer is over it, as today's label does.

### Stacks

Each stack is a group node behind its blocks, in the colour that core keeps on the stack, with its name above it.
A stack whose `color` is `null` takes the theme's colour for borders, a default of the DAG's own ([Board objects](Rewrite-1.1.1#stacks)).
Its box fits its blocks, with the padding that the layout gives a cluster ([The DAG's state, commands and placement](Rewrite-1.3.1#laying-the-board-out-again)).
A stack that holds no block shows as a box that holds its name and the number of its blocks, as a collapsed stack does, at its position in the DAG's state ([The DAG's state, commands and placement](Rewrite-1.3.1#the-state)).
A block dropped on that box joins the stack, whose box then fits the block.

A stack whose entry in the DAG's state holds `collapsed` shrinks to a box that holds its name and the number of its blocks, centred where its expanded box is.
Its blocks hide.
A link between one of them and a block outside the stack ends on the box, and a link between two of them hides with them.
Dragging the small box moves the stack's hidden blocks by the same distance, in one `blockr.dag-change_position`, so that the stack expands around where the box sits.
Expanding it brings its blocks back where they were in the stack, and the blocks around it back where they were before it collapsed, as they close up on a stack that collapses ([The DAG's state, commands and placement](Rewrite-1.3.1#collapsing-and-expanding-a-stack)).
A double click on the stack's box, or the collapse button on the box, as today's stack has, runs `blockr.dag-collapse_stack`.
It takes an undo step, since it moves the blocks around the stack, so one undo collapses or expands the stack again and puts every block back ([The DAG's state, commands and placement](Rewrite-1.3.1#collapsing-and-expanding-a-stack)).
React Flow collapses nothing itself, and its example of it is one of its paid examples, so this is the DAG's own code ([Expand and Collapse](https://reactflow.dev/examples/layout/expand-collapse)).

A block that the user drops on the box of a stack that it is not in joins that stack, through `blockr.core-change_stack`, with its move in the same step.
A block that the user drags out of its stack's box stays in the stack, whose box grows, as today's does ([blockr.dag#38](https://github.com/BristolMyersSquibb/blockr.dag/issues/38)), and leaves the stack through Edit stack ([Board actions](Rewrite-1.1.16#cores-board-actions)).

### Gestures

- Dragging a node, the selected nodes or a stack's box moves them, a stack with its blocks, as today.
  While snapping is on, the drag snaps each node that it moves to a multiple of the snap size as it moves, so that the drag ends where `blockr.dag-change_position` keeps the node (notes).
  As the drag ends, the DAG runs `blockr.dag-change_position` with every block that moved, and with a stack without blocks that moved, as one step.
  A drag selects nothing, as today, so that moving blocks around shows none of them (notes).
- Dragging from a block's result to another block's input, or from an input to another block's result, draws a link, as today's ports do.
  The DAG checks nothing while the user drags.
  As the user drops the link on a handle, the DAG runs `blockr.core-add_link`, whose preflight refuses a link that would close a cycle, join a block to itself or feed an input that a link feeds already ([Board actions](Rewrite-1.1.16#cores-board-actions)).
  A link dropped on a variadic block's placeholder takes the block's next place, through an empty input, while one dropped on a handle that a link holds adds nothing, and the DAG says at the drop that the place is taken, as the preflight says of an input that a link feeds.
  Where the command is refused, the board gains no link, so the DAG draws none.
  The DAG then shows the user why where the link was dropped, with the reason that the refusal gives, as every plugin with a UI shows what fails of what the user did in it, and takes the command's notifications through its `notifier`, so that core raises none ([Notifications, logging and tracing](Rewrite-1.1.14#taking-a-calls-notifications)).
- Dropping a link on the canvas, away from every node and stack, triggers Append block from a block's result, or Prepend block on the input that the link came from, at the drop.
  The DAG triggers them through their roles, `append_block_role` and `prepend_block_role`, so that a board action that the app picks for either plays it here too ([Board actions](Rewrite-1.1.16#roles)).
  The DAG adds `blockr.dag-change_position` with the drop to the board action's step, through `trigger()`'s `extend`, so that the new block starts at the drop ([The DAG's state, commands and placement](Rewrite-1.3.1#placing-added-blocks)).
  A link dropped on a node or on a stack's box, away from its handles, adds nothing, as today's does.
- A click selects a node, a link or a stack, and a click on the canvas clears the selection.
  A click with Cmd on a Mac, or with Ctrl elsewhere, adds to the selection, as React Flow has it, where today's DAG takes Shift.
  A drag on the canvas with Shift held selects what its rectangle covers, as React Flow has it, where today's DAG takes Alt.
- Where the user selects one block alone in the DAG, by a click, a rectangle, the keyboard or a pick in search, the DAG shows the block through `core.show()`, which every frontend carries out in its own way, the dock in the active view ([Plugins](Rewrite-1.1.12#showing-a-block-or-a-plugin)).
  A selection of several shows none, as today, and neither does a selection of a link or a stack.
- The DAG puts every selection that the user makes in it into `core.selection`, which the dock's pinned sidebar follows, and so does the DAG's own pinned panel (Its advanced actions, [Board actions](Rewrite-1.1.16#the-advanced-action)).
  It also draws the selection that `core.selection` holds, whoever set it, as the checkboxes of the Edit board plugin do ([The Edit board plugin](Rewrite-1.1.15#what-it-shows)).
  So the blocks that the user ticks in the Edit board plugin show as selected in the DAG, and the DAG's toolbar and keys act on them.
- A right click on a node, a link, a stack or the canvas opens that object's menu through `core.boardActions.menu()`, at the pointer, and a right click on a node's input handle opens the menu of the link that feeds it, or where no link feeds it, the menu of the input, as `{ block: "b", input: "y" }`, or for a variadic block's placeholder `{ block: "b", input: "" }` ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).
  Where core offers a target nothing, as on the canvas under the board lock, the right click opens no menu.
  Where the object belongs to a selection of several, the right click opens the selection's menu instead, and so does a right click on the box that React Flow draws around a selection.
  A right click on a handle opens the handle's own menu whatever the selection holds, since no selection holds an input, and the handle's look under the pointer says that the click lands on it (Nodes).
  For the canvas, the DAG passes `menu()` an `extend` that starts the block, or the stack that holds no block, that the board action adds where the user right-clicked, or the first of several, through `blockr.dag-change_position` ([The DAG's state, commands and placement](Rewrite-1.3.1#placing-added-blocks)).
  The DAG passes `menu()` and `trigger()` a `notifier` as well, and shows a refused batch at the node, the link or the point where it opened the menu or triggered the board action, as it shows a refused link where the user dropped it ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).

### The DAG's board actions

The DAG registers four board actions, beside core's, which every menu of their objects offers ([Board actions](Rewrite-1.1.16#a-board-action)):

| Board action | On | Category | What it does |
|---|---|---|---|
| Copy | A block, a stack or a selection | Clipboard | Puts on the clipboard, at once, a JSON board of the blocks and stacks that it acts on, the blocks of those stacks, the links between those blocks, any other stack that holds a block and whose blocks are all copied, and their positions, as today's copy does |
| Cut | A block, a stack or a selection | Clipboard | Copies, then runs core's commands that remove them, as one step |
| Paste | The board | Clipboard | Reads the clipboard and adds the blocks, links and stacks that it holds under new ids, through core's commands, where they sat as they were copied, moved to the point where the menu opened, or to the middle of the view from the toolbar or a key |
| Layout | The board | Edit | Its quick action offers Lay out again, the two directions and the three spacings, which run `blockr.dag-relayout`, the two placements of new blocks, Repulsion and Beside, which run `blockr.dag-set_placement`, and Snap to grid, which turns snapping on or off, and the snap size, which run `blockr.dag-set_snap` ([The DAG's state, commands and placement](Rewrite-1.3.1#commands)). It checks the current direction, spacing and placement, and Snap to grid while snapping is on, as today's menu shows the current direction and spacing ([Board actions](Rewrite-1.1.16#the-quick-action)) |

Copy writes to the system's clipboard within the user's gesture, as Safari requires.
The selection is at hand in the client, so Copy writes it at once, where today's copy starts a write that waits for R to send the board ([inst/assets/js/copy-paste.js](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/inst/assets/js/copy-paste.js)).
Copy also keeps its last copy for the page.
Paste reads the system's clipboard, which carries a copy from another tab or app.
Where the browser refuses to read it, as Safari and headless browsers do, Paste takes the page's last copy instead.
Paste leaves the board alone where the text it reads is no JSON board, as today's paste does.
Paste reads the clipboard before it returns its batch, so its `run` returns a promise ([Board actions](Rewrite-1.1.16#a-board-action)).

From the text that it reads, as the DAG's Copy writes one, Paste's `run` builds its batch:

1. It reads the board through `core.store.read()`, which gives the board that opening the text would give, its blocks migrated by the versions that it records, and what opening it would drop, holding nothing, as `check()` does for opening ([Board updates](Rewrite-1.1.2#the-store)).
2. It mints a new id for each block, link and stack with `core.mintId()`, and points the pasted links and stacks at the new ids ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
   The blocks keep their names, and the name of each stack gains " (copy)", as today's paste has it ([R/subboard.R#L119-L158](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/subboard.R#L119-L158)).
3. It returns core's commands that add the blocks, links and stacks, and then `blockr.dag-change_position` with the positions that the copied board gives them, moved together so that their middle lands at the point.

The DAG's `afterStep` places what the batch adds from there, as it places whatever a step adds, so that one undo takes the paste back ([The DAG's state, commands and placement](Rewrite-1.3.1#placing-added-blocks)).
A block whose class the app lacks is left out of the paste, with a notification that names it, as opening a board drops such a block ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)).
A pasted block that the copied board gives no position, as a board copied without the DAG's state would, starts where the strategy starts any added block.

### The toolbar

The toolbar floats in a column at the canvas's top left, as today, and holds, in this order:

1. The DAG's own controls: search, zoom in, zoom out and fit.
2. A button for each board action on the board: core's Add block, Create link and Create stack, and the DAG's Paste and Layout.
3. While the user has selected something, a button for each board action on the selection, such as core's Remove and Create stack and the DAG's Copy and Cut.

Each button shows its board action's icon, has the board action's label as its tooltip, and opens its quick action below it, or its advanced action where it has no quick action on the board, as Create link, or runs it where it asks nothing ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).
A board action that another package registers on the board or on a selection gets a button too, as it gets a row in the DAG's menus.
A block, or a stack that holds no block, that the toolbar's Add block or Create stack adds starts at the middle of the view, from where the DAG places it ([The DAG's state, commands and placement](Rewrite-1.3.1#placing-added-blocks)).

### Its advanced actions

The DAG shows the advanced actions that its menus, its toolbar and its gestures open close to where the user opened them, rather than in the frontend's place.
It hands `menu()` and `trigger()` an `advanced`, through which core mounts an advanced action in a panel that the DAG draws on its canvas ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)):

1. The user opens Edit link on a link, through the link's menu and the open icon of its quick action.
2. Core calls the DAG's `advanced`.
3. The DAG draws its panel beside the link and has core mount the form there.
4. Once `done()` ends the advanced action, the DAG closes the panel.

For an advanced action on the board, such as the block picker of Add block, the DAG draws the panel beside its toolbar.
For one on a selection, such as the form of Create stack, it draws the panel beside the box that React Flow draws around the selection.

The DAG tries this first, and building it settles whether it works well, by two tests:

1. The panel, at least 420 px wide as every place of an advanced action is, leaves in view the node, the link or the stack that the advanced action is about, since the DAG places the panel beside it and pans the canvas where it must ([Board actions](Rewrite-1.1.16#the-advanced-action)).
2. The user can pin the panel, and a pinned panel stays open once `done()` ends its advanced action and follows the DAG's selection, as the dock's pinned sidebar does today ([blockr.dag#162](https://github.com/BristolMyersSquibb/blockr.dag/issues/162)).

Where the panel fails either test, the DAG hands core no `advanced`, and its advanced actions show in the frontend's place, as those of every other menu do, the dock's sidebar under the dock.
Where the canvas has no room for the panel beside the object, as in a narrow panel of the dock, the DAG hands that call no `advanced` either.

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
So they never fire while the user types in a block's UI, as the prototype's listeners on the whole document did (notes).
Within its element, the DAG leaves alone a key that the user presses in a field, such as its search field or a form in its panel of advanced actions, as today's copy and paste do.
Where today's DAG and React Flow bind a key or a gesture differently, the DAG follows React Flow, whose conventions users know from other editors.
The keys act on the selection that `core.selection` holds (Gestures):

- Backspace triggers Remove on the selection, through its role, `remove_selected_role`, as React Flow binds it, where today's DAG takes Ctrl with Backspace.
- Cmd or Ctrl with C, X and V triggers Copy, Cut and Paste, but for C and X while the user has selected text, which the browser copies as usual, as today's copy does.
- While a selected block has the keyboard's focus, each arrow key moves every selected block and stack, 5 px a press or 20 px with Shift, or by the snap size while snapping is on, as React Flow moves them (notes).
  The user reaches a block with Tab and selects it with Enter or Space, so that the keyboard alone can arrange the board, which today's DAG does not allow.
  Links take no focus, so that the first Tab reaches a block rather than every link of the board first, while a click still selects a link and a right click opens its menu (notes).
  The DAG runs `blockr.dag-change_position` once the user pauses, or once the focus leaves the block, so that a run of presses is one step, as [Board updates](Rewrite-1.1.2#undo) asks of every input that changes with each key press.

Undo and redo are the frontend's keys, since the store keeps one history for the page ([Board updates](Rewrite-1.1.2#undo)).

### The empty board

While the board holds no block, the canvas says "No blocks yet.
Right-click to add one.", in the design system's style for an empty place, as today.
Under the board lock, it says only "No blocks yet.", since the lock leaves nothing to add.

### Its look

The DAG takes its colours from the variables of blockr.ui's theme ([UI kit and design system for the client](Rewrite-1.7#what-the-theme-provides)): those of statuses and categories for its nodes, and the theme's jobs for surfaces, text and borders, from which it sets React Flow's own styles.
It follows the theme that core's board option `dark_mode` switches the page to.
It draws its own controls, such as the toolbar's buttons, the search field and the outline, and its tooltips with blockr.ui's components wherever blockr.ui has one, as every UI of blockr's packages does ([State in JS](Rewrite-1#what-must-hold), [UI modules in JS](Rewrite-1.1.7#react)).
It draws the block's mark and status dot itself, until blockr.ui offers them in one module ([UI kit and design system for the client](Rewrite-1.7)).
Core draws its menus and quick actions, with blockr.ui's components, in blockr.ui's look ([Board actions](Rewrite-1.1.16#what-a-frontend-gives)).
The canvas keeps React Flow's link to its website in a corner, as React Flow asks of those who do not subscribe to React Flow Pro (notes).

### On a locked board

Under the board lock, the DAG draws no link from a drag and drops no block into a stack, since the lock fixes the board's links and stacks.
Everything else works as on any board, so that a reader can explore the board: dragging nodes, the arrow keys, zoom, pan, fit, selection, search, the outline, and collapsing and expanding a stack, which makes room as anywhere ([The DAG's state, commands and placement](Rewrite-1.3.1#on-a-locked-board)).
Its menus and toolbar offer only the board actions that the lock leaves ([Board actions](Rewrite-1.1.16#cores-board-actions)).
Of the DAG's own, Copy and Layout stay, while Cut and Paste fail their `offers`, since the store refuses what they run.
The load lock and a block's lock change nothing in the DAG.
The load lock fixes only which board the app shows, and a block's lock fixes only the block's state, which the DAG never changes.

### Testing

The DAG's components run on happy-dom with core's `CoreApi` for tests, with the stand-ins for `ResizeObserver` and `DOMMatrixReadOnly` that React Flow's guide gives for a page that measures nothing ([testing](https://reactflow.dev/learn/advanced-use/testing)), while the gestures that drag run in a browser, as the guide advises, in the end-to-end tests that [Drawing the board](Rewrite-1.1.8#testing) runs through shinytest2.

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
Search expands a collapsed stack as today's does, although expanding now moves the blocks around the stack, so the issue that builds search tries it on the spike's board, with the stacks that the spike added to it ([Client-drawn DAG](Rewrite-1.3), notes).
Today's keys listen on the whole document.
Ctrl with Backspace removes the selection, even while the user types in a field ([inst/assets/js/rm-sel.js](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/inst/assets/js/rm-sel.js)).
Ctrl or Cmd with C, X and V copy, cut and paste outside fields, but for C and X while the page holds selected text ([inst/assets/js/copy-paste.js](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/inst/assets/js/copy-paste.js)).

The prototype [cynkra/blockr.react](https://github.com/cynkra/blockr.react), at `e4e5c35`, holds the findings that this page takes over: keys bound on the canvas rather than the document, since a listener on the document fired Delete while the user edited an input and took copies of selected text; a clipboard of its own beside the system's, since `navigator.clipboard.readText()` fails in Safari and in headless browsers; and `fitView` once on mount, since the prop fits the view again on every change of the nodes.
React Flow 13.0.0 drops the rule that a group come before its nodes, which the prototype ordered by hand, and adds `changeParent()`, which moves a node into a group or out of it without computing its new position, which the prototype did by hand.

Core's basic frontend makes a plugin's section as tall as what the section holds, on `js-state` at `7ee6968` ([srcts/modules/basic/plugins.tsx#L141-L142](https://github.com/BristolMyersSquibb/blockr.core/blob/7ee69688488a140917cad5863101aeaf168a06e6/srcts/modules/basic/plugins.tsx#L141-L142)).
React Flow needs an element with a height to draw in ([packages/system/src/utils/constants.ts#L9](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/system/src/utils/constants.ts#L9)).
So where the DAG's element has no height, the canvas takes one of its own, such as half the window's, which the issue that draws the board settles.

React Flow's free example Simple Floating Edges sticks each link to the top, right, bottom or left side of each node ([Simple Floating Edges](https://reactflow.dev/examples/edges/simple-floating-edges)).
Its Floating Edges example works out where each link ends from the positions of the link's two nodes, in an edge type of its own ([examples/react/src/examples/FloatingEdges/utils.ts](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/examples/react/src/examples/FloatingEdges/utils.ts)).
That edge reads both nodes through `useInternalNode`, which renders the edge again whenever any node changes ([useInternalNode](https://reactflow.dev/api-reference/hooks/use-internal-node)), so the issue that draws the board checks that a drag stays smooth on the spike's board.
A node whose handles move or change in number has React Flow measure them again through `useUpdateNodeInternals` ([useUpdateNodeInternals](https://reactflow.dev/api-reference/hooks/use-update-node-internals)).
React Flow shows a crosshair over a handle that takes links on its own ([init.css#L249-L252](https://github.com/xyflow/xyflow/blob/29ab9e001c2ba320c9d84b00c729c745132d9145/packages/system/src/styles/init.css#L249-L252)), which the DAG keeps beside its own look of a hovered handle.

React Flow 13.0.0 binds keys of its own: Backspace removes what is selected, Shift with a drag draws the selection's rectangle, and Cmd on a Mac or Ctrl elsewhere adds to a selection ([src/container/ReactFlow/index.tsx#L67-L73](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/react/src/container/ReactFlow/index.tsx#L67-L73)).
The DAG keeps `selectionKeyCode` and `multiSelectionKeyCode` as React Flow sets them, and sets `deleteKeyCode` to `null`, binding Backspace itself, so that it triggers Remove on `core.selection` through `remove_selected_role`, which the store can undo, rather than React Flow's removal of the nodes that it draws.
React Flow makes each node focusable, but not the canvas around the nodes ([src/components/NodeWrapper/index.tsx#L212-L213](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/react/src/components/NodeWrapper/index.tsx#L212-L213)).
So the DAG's element takes the keyboard's focus as the user presses on the canvas.
The DAG's keys then act after a click on the canvas or a drawn rectangle, as they do after a click on a node.
React Flow makes each link focusable as well, and draws the links before the nodes, so Tab reaches every link before the first block ([src/container/GraphView/index.tsx#L156-L181](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/react/src/container/GraphView/index.tsx#L156-L181), [src/components/EdgeWrapper/index.tsx#L57](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/react/src/components/EdgeWrapper/index.tsx#L57)).
On the spike's board, the first block came after 108 links, so the DAG sets `edgesFocusable` to `false`, after which the first Tab reached a block ([Client-drawn DAG](Rewrite-1.3), notes).
Whether a click selects a link, and whether a right click opens its menu, does not depend on its focus ([src/components/EdgeWrapper/index.tsx#L61](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/react/src/components/EdgeWrapper/index.tsx#L61)).

React Flow selects a node as the user starts to drag it, since its `selectNodesOnDrag` is `true` by default ([src/store/initialState.ts#L139](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/react/src/store/initialState.ts#L139)).
The DAG would then show every block that the user moves.
So the DAG sets `selectNodesOnDrag` to `false`.
React Flow then drags a node that is not selected alone, and clears the selection as the drag starts ([packages/system/src/xydrag/XYDrag.ts#L294-L306](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/system/src/xydrag/XYDrag.ts#L294-L306)).
React Flow's own snapping, through its props `snapToGrid` and `snapGrid`, rounds the position of the first node that a drag moves, and moves every other node of the drag by as much ([packages/system/src/xydrag/XYDrag.ts#L165-L191](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/system/src/xydrag/XYDrag.ts#L165-L191), [packages/system/src/xydrag/utils.ts#L134-L161](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/system/src/xydrag/utils.ts#L134-L161)).
A node that sat off the grid, as one placed before the user turned snapping on, would then end off it, and `blockr.dag-change_position` would move it as the drag ends.
So the DAG snaps a drag itself: it rounds the position of each node that moves as it applies the moves that `onNodesChange` reports, which React Flow 13 hands it as a `NodeChangeset`, read through `toArray()`.
In the spike, a drag of several selected blocks, one of them in a stack, moved that block by React Flow's drag threshold, 5 px, more than the others, so the DAG moves every node of a drag by the move of the node under the pointer ([Client-drawn DAG](Rewrite-1.3), notes).
React Flow moves the selected nodes with the arrow keys while one of them has the keyboard's focus, 5 px a press or 20 px with Shift, and by `snapGrid` instead while `snapToGrid` is on ([src/components/NodeWrapper/index.tsx#L119-L153](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/react/src/components/NodeWrapper/index.tsx#L119-L153), [src/hooks/useMoveSelectedNodes.ts#L28-L29](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/react/src/hooks/useMoveSelectedNodes.ts#L28-L29)).
It reports those moves through `onNodesChange`, as it reports a drag's, but outside any drag ([src/store/index.ts#L212-L233](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/react/src/store/index.ts#L212-L233)).
So the DAG keeps them in its component, as it keeps a drag's, until the user pauses.
While snapping is on, the DAG sets `snapToGrid`, with `snapGrid` at `[snap_size, snap_size]`, so that a press moves each selected block by the snap size, and React Flow rounds each position that the press reaches ([src/hooks/useMoveSelectedNodes.ts#L45-L47](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/react/src/hooks/useMoveSelectedNodes.ts#L45-L47)).
Enter and Space select a node that has the focus, and Escape takes it out of the selection ([packages/system/src/utils/constants.ts#L43](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/system/src/utils/constants.ts#L43)).
React Flow's rectangle selects every link of each node that it covers, links to nodes outside it among them ([src/container/Pane/index.tsx#L241-L254](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/react/src/container/Pane/index.tsx#L241-L254)).
So the DAG keeps only the links whose two blocks the rectangle covers.
The DAG gives React Flow no `isValidConnection`, so React Flow, in its default strict mode, takes a link from any result to any input, or from an input to a result, and leaves the rest to `blockr.core-add_link`.
A drop that reaches no handle comes to `onConnectEnd`, which the DAG takes for a drop on the canvas only where no node lies under the pointer.
Since 13.0.0, React Flow's `onConnectEnd` gives the point where a link was dropped in the canvas's coordinates, which is where the new block starts ([xyflow#6117](https://github.com/xyflow/xyflow/pull/6117)).
The quick action opens at the pointer's place on the screen, which the event gives.

A board action's `run` gets the board, its target and `CoreApi` alone ([Board actions](Rewrite-1.1.16#a-board-action)).
So Paste's `run` cannot see where the user opened a menu.
The DAG's class and its UI are one package's code, which can share that point:

1. Before the UI calls `menu()`, it notes where the menu opens.
2. Before it calls `trigger()` from the toolbar or a key, it notes the middle of its view.
3. Paste's `run` reads the point that the UI noted last.

React Flow 13.0.0 sets `color-scheme: light dark` on its root, so that it follows the system's theme unless an ancestor carries `data-theme` or the class `dark` or `light`, or its prop `forceColorMode` sets one ([packages/system/src/styles/init.css#L3-L48](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/system/src/styles/init.css#L3-L48)).
Core switches the theme through the attribute `data-bc-theme` on the page's root instead, in `setTheme()` of `srcts/options/options.ts` on blockr.core's `js-state` at `7fd739c`.
In the rewrite the attribute is blockr.ui's `data-bk-mode`, which core's board option `dark_mode` sets ([UI kit and design system for the client](Rewrite-1.7#prefixes)), so the DAG's stylesheet sets the canvas's `color-scheme` from that one.
The stylesheet's rules win over React Flow's, which 13.0.0 puts in the cascade layer `xyflow` ([xyflow#5844](https://github.com/xyflow/xyflow/pull/5844)).

React Flow draws its link in the bottom right corner unless `proOptions.hideAttribution` is set, and asks that only those who subscribe to React Flow Pro hide it, while its MIT licence lets anyone do so ([src/components/Attribution/index.tsx#L17-L37](https://github.com/xyflow/xyflow/blob/998523c4e3f056d4e1273e7cec216dc69e863315/packages/react/src/components/Attribution/index.tsx#L17-L37)).
The prototype hid it.
The DAG leaves `hideAttribution` unset, and moves the link to another corner through `attributionPosition` where it gets in the way.

</details>
