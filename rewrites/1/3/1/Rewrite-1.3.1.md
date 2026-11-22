# The DAG's state, commands and placement
Status: settled on 2026-11-22. Design for [Client-drawn DAG](Rewrite-1.3).

One of the design pages of the client-drawn DAG ([Client-drawn DAG](Rewrite-1.3)): what the DAG plugin keeps in its state, the commands that change it, its class's `update`, `afterStep` and `start`, how it places the blocks and stacks that someone adds, pastes a copied board, makes room around a stack that collapses or expands, snaps positions and lays the whole board out again, how an app script writes its state in R, how boards saved today cross, and what the DAG does on a locked board.
It shapes the Work items of [Client-drawn DAG](Rewrite-1.3#work) that make the DAG a plugin in R and build its class in the client, and the spike that decides between dagre and elkjs.
What the DAG draws, its menus, its own board actions and its toolbar are [Drawing the DAG](Rewrite-1.3.2)'s, and what a plugin's state is and how the store keeps it are [Plugins](Rewrite-1.1.12#a-plugins-state)'s.

## What must hold

Conditions 2, 4, 6 and 7 of [Client-drawn DAG](Rewrite-1.3#what-must-hold) rest on this page.

1. The state holds a position for every block of the board and for every stack that holds no block, the layout's direction, spacing, placement and snapping, and the stacks that the DAG shows collapsed, in the shape of one JSON Schema, which describes each part for the assistant.
2. Adding a block, or a stack that holds no block, gives it a position in the same step, so that undo takes back the object and its position together, and moves no other block.
3. A block moves only when someone moves it, runs `blockr.dag-relayout`, or collapses or expands a stack near it.
4. The class's `update` reads only the change and the board, and its `afterStep` only the boards before and after the step, so that both give the same patches wherever they run ([Board updates](Rewrite-1.1.2#plugins)).
5. A board saved today opens with its positions and its layout's direction and spacing, and a position keeps its meaning across the switch.
6. On a locked board, the DAG's commands move no block unless the deployment leaves rearranging to readers, while collapsing a stack stays open.
7. Collapsing or expanding a stack moves the blocks around it, the most next to the stack and less further away, so that the blocks close up on a stack that collapses and clear the box of one that expands, while blocks far from the stack stay where they are and each other stack keeps its shape.
8. Whatever the DAG places, pastes, lays out or moves to make room overlaps no other node, with the spacing's gap around it, and comes out the same for the same board wherever it runs, but for a place that someone gives, which the block takes as given.

## Today

Today's DAG keeps `positions` and `layout` as the state of its extension, which the board update's `extensions` sets from outside, and keeps them in step with the canvas through two guards against the echo ([R/srv.R#L114-L275](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/srv.R#L114-L275)).
Its positions are those of blocks alone, so a saved board keeps no place for a stack that holds no block.
Which stacks are collapsed lives on the canvas alone, so a saved board reopens with every stack expanded.
A block that is added goes to the last position of the mouse on the canvas, and blocks added at once stack 130 px apart below it ([R/g6r.R#L904-L923](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/g6r.R#L904-L923)).
A block inserted into a link goes between the link's two ends, and the block that the link fed moves on by one gap, with every block downstream of it, to make room ([R/g6r.R#L856-L903](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/g6r.R#L856-L903)).
The layout of the whole board is G6's dagre, whose spacing presets are tuned around the padding of a stack's box, which dagre does not know ([R/layout.R#L66-L96](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/layout.R#L66-L96)), and G6 lays the board out again as blocks come ([blockr.dag#40](https://github.com/BristolMyersSquibb/blockr.dag/issues/40)).

## Proposal

### The state

With illustrative names:

```ts
interface DagState {                                     // the state of blockr.dag-dag_plugin, at version 1
  positions: Record<BlockId, { x: number; y: number }>;  // the centre of each block's mark, in pixels of the canvas
  stack_positions: Record<StackId, { x: number; y: number }>;   // the centre of the box of each stack that holds no block
  layout: {
    direction: "TB" | "LR";                              // top to bottom, or left to right
    spacing: "compact" | "normal" | "loose";             // the gaps between blocks and between ranks
    placement: "repulsion" | "beside";                   // how a block that someone adds gets its place
    snap: boolean;                                       // whether every position that the DAG sets snaps to snap_size
    snap_size: number;                                   // in pixels of the canvas
  };
  collapsed: Record<StackId, true>;                      // the stacks that the DAG shows collapsed
}
```

Its default is `{ "positions": {}, "stack_positions": {}, "layout": { "direction": "TB", "spacing": "normal", "placement": "repulsion", "snap": false, "snap_size": 20 }, "collapsed": {} }`, and a board holds it under the class's id:

```json
"blockr.dag-dag_plugin": {
  "positions": { "a": { "x": 120, "y": 80 }, "b": { "x": 120, "y": 200 } },
  "stack_positions": { "s2": { "x": 360, "y": 80 } },
  "layout": { "direction": "TB", "spacing": "normal", "placement": "repulsion", "snap": false, "snap_size": 20 },
  "collapsed": { "s1": true }
}
```

A position is the centre of the block's mark, as today's positions are, so that converted positions keep their meaning.
Today's node is the mark alone, 32 px across, which G6 places by its centre, and G6 draws the block's name below it ([R/g6r.R#L667-L670](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/g6r.R#L667-L670), [#L209](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/g6r.R#L209)).
React Flow places a node by its top left corner, and a node in a group relative to the group, so the DAG converts as it draws ([Drawing the DAG](Rewrite-1.3.2#nodes)).
A stack has a position only while it holds no block, the centre of its box, since the box of a stack with blocks fits them ([Drawing the DAG](Rewrite-1.3.2#stacks)).
The positions of stacks are kept apart from those of blocks, since an id is unique only within its collection ([Board objects](Rewrite-1.1.1#ids)).
Each part keeps what one use needs: the positions, so that a board reopens as the user arranged it; `stack_positions`, so that a stack that holds no block stays where the user put it, for blocks to be dropped on it; the layout, so that a layout run later, the place of an added block, the snapping of positions and the sides of the ports follow what the user picked; and `collapsed`, so that a board reopens with its stacks as the user left them.
The stacks in `collapsed` are keyed by their ids, as the positions are by the blocks' ids, so that a patch names a stack rather than an index of an array, which may hold another stack by the time undo or redo applies the patch ([Plugins](Rewrite-1.1.12#a-plugins-state), [Board updates](Rewrite-1.1.2#undo)).

The schema's `description` keywords say what `dag_ext_meta()` says today, so that the assistant needs no code of its own for the DAG ([R/ext.R#L54-L109](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L54-L109), [Board updates](Rewrite-1.1.2#plugins)).
A position is a point on the canvas, with x to the right and y downwards, and a block is about 50 px across, so a block beside another sits about 150 px from it.
Laying the board out again moves every block, so the assistant runs it before it places blocks by hand.

### Commands

| Command | Args | Undo step | What it does |
|---|---|---|---|
| `blockr.dag-change_position` | `positions`, points by block id, and `stack_positions`, points by stack id, each optional | Yes | Sets the positions given, as a drag or a run of presses of the arrow keys ends with every block and every stack without blocks that it moved, or as a step puts an added block or stack at the place given (Placing added blocks) |
| `blockr.dag-relayout` | `direction` and `spacing`, each optional | Yes | Sets the settings given and lays the whole board out again with them (Laying the board out again) |
| `blockr.dag-set_placement` | `placement` | No | Sets how added blocks get their place, and moves no block |
| `blockr.dag-set_snap` | `snap` and `snap_size`, each optional | No | Sets whether the DAG snaps the positions that it sets, and to what size, and moves no block, so that the next operation or drag snaps (How the DAG moves blocks) |
| `blockr.dag-collapse_stack` | `stack`, `collapsed` | Yes | Collapses a stack or expands it, and moves the blocks around it (Collapsing and expanding a stack) |
| `blockr.dag-paste` | `board`, the text of a JSON board, and `at`, a point | Yes | Adds the blocks, links and stacks of a copied board under new ids, with their positions (Pasting) |

The commands that name a block or a stack fail their preflight where the board lacks it, so that the state keys nothing by an id that the board does not hold.
The preflight of `blockr.dag-change_position` also refuses a position for a stack that holds a block, since the box of such a stack fits its blocks.
The preflight of `blockr.dag-collapse_stack` refuses a stack that holds no block, since such a stack shows as a collapsed one does already.
The commands `blockr.dag-set_placement` and `blockr.dag-set_snap` have `undo: false`, since they move no block.
So a user who drags a block, then turns snapping on, and then presses Undo takes back the drag, while the store still saves the settings with the board ([Board updates](Rewrite-1.1.2#undo)).
Each command's `description` and `args` describe it to the assistant's tools ([The assistant's tools](Rewrite-1.4.2#the-tools)).
The commands declare no `shortcut`, since the DAG binds its keys within its own element ([Drawing the DAG](Rewrite-1.3.2#keys)).
Copying and cutting are no commands of the DAG's: Copy changes nothing on the board, and Cut is Copy followed by core's commands that remove, so both are board actions ([Drawing the DAG](Rewrite-1.3.2#the-dags-board-actions)).

### The class's `update` and `afterStep`

With every delta that the store applies, the class's `update` drops the position of each block that the delta removes, and the entry in `collapsed` and the position of each stack that the delta removes ([Board updates](Rewrite-1.1.2#plugins)).
Once the last delta of the step is in, its `afterStep` brings the state in line with the board that the step leaves:

1. It places each block that has no position yet, and each stack that holds no block and has none, through the strategy (Placing added blocks).
2. A stack that the step leaves without blocks takes the centre of the box that its blocks spanned on the board before the step, rather than a place from the strategy.
3. It drops the position of each stack that holds a block.
4. It drops from `collapsed` each stack that holds no block, which shows as a collapsed stack does already, so that a block that joins the stack later shows.

So a batch that adds a block and then links it places the block by its link, which `update` would not see yet as it is given the block's delta, and a batch that empties a stack and fills it again leaves the stack with no position.
Both read nothing on the page, so that they give the same patches wherever they run.

The `afterStep` leaves alone a block that had no position before the step either, and a stack that held no block and had no position before the step either.
Only a board that has just opened holds such a block or stack, and the class's `start` gives each a position (Starting on a board).
So where the frontend takes a step before `start` runs, as the dock does when it adds its first view, `start` still lays out a board that opened without positions.

### Starting on a board

As a board opens, the class's `start` gives a position to every block that lacks one, and to every stack that holds no block and lacks one:

1. Where the board holds no position for any block or stack, as a board that a script builds without positions or a converted file that holds none, it lays the whole board out (Laying the board out again).
2. Where it lacks the positions of some blocks or stacks only, it places those through the strategy, as it places added blocks.

In the same delta, it drops each position and each entry in `collapsed` that names a block or a stack that the board lacks, as an app script may give one, the position of each stack that holds a block, and the entry in `collapsed` of each stack that holds no block.
It names every entry that it drops in one warning about the DAG, of the code `dag_state_dropped`, which holds until the next board opens, as core's note of what the store dropped does, and it logs the same at warn ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)).
A board that the DAG saved holds no such entry, since `update` and `afterStep` keep the state in line with the board, so only a mistake in an app script or a file written elsewhere raises the warning.
The delta has the origin `blockr.dag-dag_plugin` and `undo: false`, as the dock adds its first view, so that undo never takes the board back to blocks without positions ([The dock's state](Rewrite-1.2.1#starting-on-a-board)).
Core calls `start` once the frontend's `render()` has returned ([Plugins](Rewrite-1.1.12#running-a-plugin)).
So a step that the frontend takes as it starts, such as the dock's step that adds its first view, comes before `start`, and `afterStep` leaves to `start` what lacked a position as the board opened (The class's `update` and `afterStep`).
A fresh start of the same app takes the same step on the same board, since both the layout and the strategies give the same positions for the same board ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).

### How the DAG moves blocks

Five operations give blocks their positions, each with a mechanism of its own:

| Operation | When it runs | What it moves | How |
|---|---|---|---|
| Laying the board out | Someone runs `blockr.dag-relayout`, or `start` opens a board that holds no positions | Every block, and every stack without blocks | dagre or elkjs, as the spike decides (Laying the board out again) |
| Placing what is added | `afterStep` and `start`, for whatever has no position and no place given | Only the added blocks and stacks | Repulsion by default, or Beside (Placing added blocks) |
| Making room around a stack | `blockr.dag-collapse_stack` | The blocks around the stack, less the further away they are | Repulsion (Collapsing and expanding a stack) |
| Pasting | `blockr.dag-paste` | Only the pasted blocks and stacks | Moved together to the point, and on together where they would overlap another node (Pasting) |
| Snapping | After any of the others, and with every `blockr.dag-change_position`, while `snap` is on | Only what the operation or the command moved | Rounds each position to a multiple of `snap_size` |

Each of them gives the same positions for the same board wherever it runs, since it reads nothing on the page.
Each leaves no two nodes closer than the spacing's gap, but for a place that the user or the assistant gives, which the block takes as given, snapped where `snap` is on.
What each cannot do:

- Placing never moves another block, so on a crowded board a new block can land further from the blocks that it reads from.
- Making room keeps the arrangement around the stack, but not the ranks of a board that was laid out, which laying out again restores.
- Pasting keeps the arrangement that the blocks were copied in, so on a crowded board the pasted blocks can land further from the point.
- Snapping moves a node by up to half of `snap_size`.
  Where that brings a node that one of the other operations moved closer to another node than the gap, the node moves on to the nearest multiple of `snap_size` that keeps the gap, while a place that someone gives only rounds.
- All of them work from a node's nominal size, so a long name can still overlap the name of a block beside it (notes).

How these rules feel is judged in an app once the DAG draws the board, and they are settled again where they feel wrong ([Client-drawn DAG](Rewrite-1.3#work)).

Turning `snap` on, or changing `snap_size`, moves no block until the next operation or drag, as picking another placement moves none.
Laying the board out again snaps every block at once while `snap` is on, since the DAG snaps every position that the layout gives (Laying the board out again).
During a drag, the DAG snaps the centre of each node that moves, so that the drag ends on the point that `blockr.dag-change_position` keeps ([Drawing the DAG](Rewrite-1.3.2#gestures)).
The pages call this snapping, and its size the snap size, since a grid is how the dock arranges a view's panels, while a label on the page may still say "Snap to grid".

### Placing added blocks

A block, or a stack that holds no block, that someone adds lands at the place given, where there is one, and otherwise where the placement strategy that the state names puts it:

- A place is given where the user right-clicks the canvas and adds a block or a stack from its menu, and where the user drops a link on the canvas, which triggers Append block or Prepend block at the drop ([Drawing the DAG](Rewrite-1.3.2#gestures)).
  The DAG adds `blockr.dag-change_position` with that point to the step of the board action, through the `extend` of `core.boardActions.menu()` or `trigger()`, and the block lands exactly there ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).
  Where the board action adds several blocks, as a template that a package's command adds would, the point goes to the first of them in the order of their links, and `afterStep` places the others against it, so that they do not land on one another.
- The assistant gives a place by adding `blockr.dag-change_position` to the edit that adds the block, or leaves the place to the strategy, as the schema's `description` keywords tell it.
- No place is given where a board action adds a block from the menu of a block or a link, as Append block on a block does, nor where another plugin adds one, as the dock's "+" on a tab group does.
- The toolbar's Add block and Create stack give no place either, but the DAG runs the strategy for what they add from the middle of the view, and adds `blockr.dag-change_position` with the result through `trigger()`'s `extend`, since what they add is linked to none and would otherwise start after the last block of the first rank, which may be out of view.

The class's `afterStep` places every block, and every stack without blocks, that the step adds and gives no place, through the strategy, so that one undo takes back the object and its place together.

A placement strategy takes every existing position as fixed, and returns positions for the added blocks and stacks alone, with illustrative names:

```ts
type Placed = Pick<DagState, "positions" | "stack_positions">;

interface Placement {
  id: "repulsion" | "beside";
  place(args: { board: Board; fixed: Placed; added: { blocks: BlockId[]; stacks: StackId[] }; preferred: Placed; layout: Layout }): Placed;
}
```

- Repulsion, the default, starts a block where Beside would start it, or at its preferred start, and lets d3-force push it off the nodes around it, which stay pinned, and off the box of every stack that it is not in, while its links pull it towards the blocks that it is linked to, from a seeded random source and for a fixed number of ticks without timers, so that it gives the same positions each time (notes).
- Beside starts a block one rank after the blocks it reads from, below them from top to bottom or to their right from left to right, across from their middle.
  A block that reads from none but feeds others starts one rank before the blocks that it feeds, and a block linked to none starts after the last block of the first rank, the blocks level with the topmost block from top to bottom, or with the leftmost from left to right.
  Then it moves the block to the nearest spot where its node overlaps no other node that shows, and no box of a stack that the block is not in, with the spacing's gap around it.
- Both place a stack that holds no block as a block that reads from none, with the size of its box, which holds the stack's name and the number of its blocks, as a collapsed stack's box does ([Drawing the DAG](Rewrite-1.3.2#stacks)).
- The gaps are those of today's presets, 50 px when compact, 70 px when normal and 100 px when loose, between two nodes and between two ranks alike ([R/layout.R#L66-L76](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/layout.R#L66-L76)).
- A strategy works from a node's nominal size, its mark with room for its label, rather than from what the page measures, since `afterStep` reads nothing on the page (notes).
- A strategy places a block by the links of the board that the step leaves, so that a batch that adds a block and then links it places the block by that link, as Append block does ([Board actions](Rewrite-1.1.16#cores-board-actions)).
  A block that one step adds and a later step links stays where it landed, as where the assistant edits through a tool for each command ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).
  So the description of `blockr.core-add_block`, which the assistant's model reads, tells it to link a block that reads from another in the same batch ([blockr.core#750](https://github.com/BristolMyersSquibb/blockr.core/pull/750)).
- Several blocks that one step adds are placed in the order of their links, each against the blocks placed before it, so that a new chain comes out as a chain ([blockr.dag#117](https://github.com/BristolMyersSquibb/blockr.dag/issues/117)).
- A strategy starts a block from the point that `preferred` gives it, where there is one, as for the toolbar's Add block, and moves it from there off what it would overlap.
- An inserted block, which reads from one block and feeds another, starts between the two, and no block moves to make room for it, unlike today's.

### Laying the board out again

The command `blockr.dag-relayout` lays every block out with dagre or elkjs, whichever the spike picks ([Client-drawn DAG](Rewrite-1.3#proposal)):

1. In `prepare()`, it loads the layout's library where it has not loaded yet, and lays the board out with the direction and the spacing that the state holds or that its args give, each stack as a cluster that holds its blocks, a stack that holds no block as one node of its box's size, and a collapsed stack as one node of its collapsed size, whose hidden blocks move with it and keep their places in the stack, so that the board stays compact while the stack is collapsed, and expanding it makes room later (Collapsing and expanding a stack).
2. Its `run()` returns the positions that the layout gave the blocks still on the board and the stacks that hold no block, snapped while `snap` is on, and the settings that it was given, as patches to the DAG's state, so that one undo puts every block back ([Board updates](Rewrite-1.1.2#commands)).
   A block that someone added while the layout ran keeps the place that `afterStep` gave it.

The DAG draws a stack's box with the padding that the layout gives a cluster, so the spacing needs no tuning around a padding that the layout does not know, as today's presets do.
The DAG's board action Layout runs the command, and so may the assistant ([Drawing the DAG](Rewrite-1.3.2#the-dags-board-actions)).

### Collapsing and expanding a stack

A collapsed stack's box is centred where its expanded box is, around its blocks, which keep their positions while they hide.
Dragging the small box moves the stack's hidden blocks by the same distance, in one `blockr.dag-change_position`, so that the stack expands around where the box sits ([Drawing the DAG](Rewrite-1.3.2#stacks)).
The state holds nothing of its own for a collapsed stack, so its blocks stay the one source of where it is.
The command `blockr.dag-collapse_stack` changes `collapsed` and moves the blocks around the stack in the same delta:

- Collapsing shrinks the box to its collapsed size, and the blocks around it move towards its centre, so that they close up on it.
- Expanding grows the box back around its blocks, and the blocks around it move away from its centre until none overlaps the box with the spacing's gap around it.
- A block or another stack next to the stack moves the most, and one further away less, so that blocks far from the stack stay where they are and the board around them keeps its shape.

Repulsion makes the room: the blocks next to the stack move freely, blocks further away are held to their places the more firmly the further they sit, and the stack's box pushes them apart.
Each other stack moves as one node of its box's size, so that it keeps its shape, and its blocks, hidden or not, move with it by one distance, as laying the board out moves the hidden blocks of a collapsed stack.
The spike checks it against criteria fixed before it runs, on the largest real board with stacks added ([Client-drawn DAG](Rewrite-1.3#work)).

The command takes an undo step, since it moves blocks, so that one undo expands or collapses the stack again and puts every block back exactly where it was, which expanding a collapsed stack does not, as the moves taper off.
So it differs from the dock's `blockr.dock-collapse_rail`, which changes only what the user looks at and takes none ([The dock's state](Rewrite-1.2.1#commands)).

### Pasting

The command `blockr.dag-paste` takes the text of a JSON board, as the DAG's Copy writes one, and a point:

1. In `prepare()`, it reads the board through `core.store.read()`, which gives the board that opening the text would give, its blocks migrated by the versions that it records, and what opening it would drop, holding nothing, as `check()` does for opening ([Board updates](Rewrite-1.1.2#the-store)).
2. In `run()`, it mints a new id for each block, link and stack, and points the pasted links and stacks at the new ids.
   The blocks keep their names, and the name of each stack gains " (copy)", as today's paste has it ([R/subboard.R#L119-L158](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/subboard.R#L119-L158)).
3. It moves the pasted positions together, so that their middle lands at the point.
   Where a pasted block would then overlap another node, with the spacing's gap around it, it moves them all on together, to the nearest spot where none does, so that they keep the arrangement that they were copied in (notes).
4. It returns one delta with the blocks, links and stacks, the positions of the blocks and those of the stacks that hold no block, so that one undo takes the paste back ([Board updates](Rewrite-1.1.2#plugins)).

A block whose class the app lacks is left out of the paste, with a notification that names it, as opening a board drops such a block ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)).
A pasted block that the copied board gives no position, as a board copied without the DAG's state would, gets its place from `afterStep`, as any added block does.

### Defining the state in R

```r
new_dag_plugin <- function(positions = list(), layout = dag_layout(), collapsed = character()) {   # in blockr.dag
  collapsed <- stats::setNames(rep(list(TRUE), length(collapsed)), collapsed)   # the stacks by id, as the state keys them
  new_plugin(
    list(positions = positions, stack_positions = list(), layout = unclass(layout), collapsed = collapsed),
    "dag_plugin"
  )
}

dag_layout <- function(direction = c("TB", "LR"), spacing = c("normal", "compact", "loose"),
                       placement = c("repulsion", "beside"), snap = FALSE, snap_size = 20) {
  structure(
    list(direction = match.arg(direction), spacing = match.arg(spacing), placement = match.arg(placement),
         snap = snap, snap_size = snap_size),
    class = "dag_layout"
  )
}
```

The package lists the class in its `._BLOCKR_MODULES_` with the id `dag_plugin`, the constructor `new_dag_plugin()`, the name "Workflow" and its module ([Plugins](Rewrite-1.1.12#a-plugin)).
An app script names the collapsed stacks as a character vector, as `collapsed = "s1"`, which the constructor keys by id.
The constructor takes no position for a stack, since `start` places each stack that holds no block.
R writes the state by the JSON Schema that the package ships beside the module, so that an empty `positions`, `stack_positions` or `collapsed` stays a JSON object, where R would otherwise write the empty array that it writes for an empty list.
The class has no method of `plugin_version()`, so its state is at version 1.
An app script that gives the DAG a state passes the plugin in the board's `plugins`, as `new_board(blocks, plugins = list(new_dag_plugin(positions = pos)))`, and one that passes none gets the default state, which `start` lays out.

### Boards saved today

The method of blockr.convert for the DAG's extension makes the plugin with `new_dag_plugin()` from the extension's `positions` and `layout`, whose `placement`, `snap` and `snap_size` take their defaults, and with no stack collapsed and no position for a stack, since today's files keep neither, so that `start` places each stack that holds no block ([The conversion and the migration notes](Rewrite-1.9#the-methods-of-other-packages)).
It passes on the positions as the file holds them, so that a position of a block that the file lacks reaches `start`, which names it as it drops it.
A file of blockr.dock 0.1.2 holds no state of the DAG, since the dock wrote every extension's state empty then, so the board opens with the default state, and `start` lays it out ([Saved boards and app scripts across the switch](Rewrite-1.2.2)).

### On a locked board

The store applies a patch inside the DAG's state on a locked board, and leaves its lock to the DAG's commands, as for the dock's ([The dock's state](Rewrite-1.2.1#on-a-locked-board)):

- Under the board lock, `blockr.dag-change_position`, `blockr.dag-relayout`, `blockr.dag-set_placement` and `blockr.dag-set_snap` fail their preflight, unless the blockr option `lock_rearrange` is `FALSE`, which the class reads once as it starts, through `core.blockrOption()`.
- The command `blockr.dag-collapse_stack` passes it, but moves no other block under the board lock unless `lock_rearrange` is `FALSE`, so that the stack's box only shrinks or grows in place there, and an expanded stack may cover the blocks around it.
- The command `blockr.dag-paste` fails it, since the store refuses the blocks that it would add ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).
- The delta of `start` still applies, so that the DAG can draw a locked board that holds no positions.

Core's `blockr.core-set_plugin_state` fails its preflight on a locked board, so nothing else moves a block there ([Plugins](Rewrite-1.1.12#a-plugins-state)).

### Testing

The state, the class's `update`, `afterStep` and `start`, the commands and the strategies run on core's `CoreApi` for tests, with neither a browser nor R ([Plugins](Rewrite-1.1.12#testing)), and `new_dag_plugin()` and `dag_layout()` in R's tests.

## Open questions

None.

<details><summary>Notes for implementers</summary>

The nominal size of a node is to settle in the issue that builds the strategies: the mark is 32 px across, as today's node is, and the label below it needs a width from its length, such as the width that the label's font gives its characters, capped where today's labels break.

Version 3.0.1 of d3-force (ISC, 5.7 KB gzipped) keeps a node with `fx` and `fy` where they say, takes a seeded `randomSource()` and steps through `tick()` without timers ([d3-force](https://d3js.org/d3-force/simulation)).
Its `forceX` and `forceY` take a strength for each node, which holds a block to its place the more firmly the further it sits from a stack that makes room, and `forceCollide` keeps nodes apart ([forceX and forceY](https://d3js.org/d3-force/position), [forceCollide](https://d3js.org/d3-force/collide)).
That force treats each node as a circle, so a stack's box, which is no circle, pushes blocks off through a force of the DAG's own.

React Flow's own snapping rounds the top left corner of a node that the user drags rather than its centre, so the DAG snaps a drag itself ([Drawing the DAG](Rewrite-1.3.2#gestures)).

Today's code, at `898a097`: the state and its external control are `new_dag_extension()`, `dag_ext_meta()` and `dag_positions_description()` in `R/ext.R` and `setup_layout_ctrl()`, `push_layout()` and `setup_positions_ctrl()` in `R/srv.R`; the layout is `R/layout.R`; placing is `add_nodes()` and `space_spliced_node()` in `R/g6r.R`; and copy and paste are `R/subboard.R` and `R/action.R`.

The method of blockr.convert reads today's `layout` as `dag_layout()` writes it, with `direction` and `spacing`, and today's `positions` as block ids to points.

Between the deltas of a step, an added block has no position yet, since `afterStep` places it as the step ends, so the DAG draws from `core.store.board()` once the store has announced a change, rather than from the board that comes with each delta.
Between the opening of a board and the delta of `start`, a block may have no position either, so the DAG draws no node for a block without one ([Drawing the DAG](Rewrite-1.3.2#the-canvas)).

On `js-state`, core hands each command a context beside the board and its args, with the locks and `mintId()`, and with `blockrOption()`, which returns a promise ([srcts/commands/commands.ts#L63-L85](https://github.com/BristolMyersSquibb/blockr.core/blob/7ee69688488a140917cad5863101aeaf168a06e6/srcts/commands/commands.ts#L63-L85)).
So the preflights read the board lock from the context, and the paste mints its ids with the context's `mintId()`.
A preflight cannot wait for a promise, so the class keeps the value of `lock_rearrange` that its `start` reads for the board that is open, and it keeps the `CoreApi` for the paste's `core.store.read()`.

The paste looks for the nearest spot in rings around the point, one gap apart, and takes the first spot where no pasted block overlaps another node, so that the same paste on the same board lands in the same place.

The layout is given the blocks and links in the order that the board holds them, since dagre's result depends on the order in which it is given nodes and edges, and the same board has to give the same positions.

</details>
