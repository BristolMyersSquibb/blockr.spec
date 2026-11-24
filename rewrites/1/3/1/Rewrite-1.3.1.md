# The DAG's state, commands and placement
Status: settled on 2026-11-23. Design for [Client-drawn DAG](Rewrite-1.3).

One of the design pages of the client-drawn DAG ([Client-drawn DAG](Rewrite-1.3)): what the DAG plugin keeps in its state, the commands that change it, its class's `update`, `afterStep` and `start`, how it places whatever a step adds, one block or many, makes room around what it places and around a stack that collapses or expands, snaps positions and lays the whole board out again, how an app script writes its state in R, how boards saved today cross, and what the DAG does on a locked board.
It shapes the issues of [Client-drawn DAG](Rewrite-1.3#work) that make the DAG a plugin in R, [blockr.graph#2](https://github.com/BristolMyersSquibb/blockr.graph/issues/2), and build its class in the client, [blockr.graph#3](https://github.com/BristolMyersSquibb/blockr.graph/issues/3).
The issues that draw the board, open its menus, and write its user guide and its migration notes rely on it too: [blockr.graph#4](https://github.com/BristolMyersSquibb/blockr.graph/issues/4), [blockr.graph#5](https://github.com/BristolMyersSquibb/blockr.graph/issues/5), [blockr.graph#6](https://github.com/BristolMyersSquibb/blockr.graph/issues/6) and [blockr.graph#7](https://github.com/BristolMyersSquibb/blockr.graph/issues/7).
What the DAG draws, its menus, its own board actions and its toolbar are [Drawing the DAG](Rewrite-1.3.2)'s, and what a plugin's state is and how the store keeps it are [Plugins](Rewrite-1.1.12#a-plugins-state)'s.

## What must hold

Conditions 2, 4, 6 and 7 of [Client-drawn DAG](Rewrite-1.3#what-must-hold) rest on this page.

1. The state holds a position for every block of the board and for every stack that holds no block, the layout's direction, spacing, placement and snapping, and the stacks that the DAG shows collapsed, with what collapsing each moved, in the shape of one JSON Schema, which describes each part for the assistant.
2. Whatever a step adds, blocks and stacks that hold no block, one or many, gets its positions in the same step, so that undo takes back the objects and their positions together.
   Under Beside, adding moves no other block, and under Repulsion it moves only the blocks near what it adds, in the same step.
3. A block moves only when someone moves it, runs `blockr.graph-relayout`, collapses or expands a stack near it, or adds a block or a stack near it under Repulsion.
4. The class's `update` reads only the change and the board, and its `afterStep` only the boards before and after the step, so that both give the same patches wherever they run ([Board updates](Rewrite-1.1.2#plugins)).
5. A board saved today opens through blockr.convert with its blocks arranged as they were saved, and with its layout's direction and spacing.
6. On a locked board, the DAG locks nothing of its own, so that a reader moves blocks, lays the board out and collapses stacks as on any board, while the store refuses what the board lock fixes.
7. Where the DAG makes room, for what Repulsion places or around a stack that collapses or expands, the blocks next to it move the most and those further away less, with a reach that grows with the stack, but for blocks lined up a gap apart in the way of what it places, which move on together.
   So the blocks clear what Repulsion places and the box of a stack that expands, and close up on a stack that collapses.
   No two blocks within two gaps of each other swap sides, a collapsed stack moves as one, and the blocks of an expanded stack move one by one, as blocks in no stack do.
8. Whatever the DAG places, lays out or moves to make room overlaps no other node, with the spacing's gap around it, and comes out the same for the same board wherever it runs, but for a block that someone moves to a place of their own, which it takes as given, and two nodes that sat closer than the gap before the DAG made room, which keep what they had.
9. Expanding a stack puts the board back as if the stack had never collapsed, whatever stacks collapsed or expanded since, but for what someone moved or added meanwhile, which stays where it is unless it lies in the stack's box, out of which it moves.

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
interface GraphState {                                     // the state of blockr.graph-graph_plugin, at version 1
  positions: Record<BlockId, { x: number; y: number }>;  // where React Flow places each block's node, in pixels of the canvas
  stacks: Record<StackId,                                // what the DAG keeps about a stack, where it keeps anything
    | { x: number; y: number }                           // a stack that holds no block: where its box sits
    | { collapsed: number; moved: Moved }>;              // a stack with blocks that the DAG shows collapsed: its place among the collapses, and what its collapse moved
  layout: {
    direction: "TB" | "LR";                              // top to bottom, or left to right
    spacing: "compact" | "normal" | "loose";             // the gaps between blocks and between ranks
    placement: "repulsion" | "beside";                   // how what a step adds gets its place
    snap: boolean;                                       // whether every position that the DAG sets snaps to snap_size
    snap_size: number;                                   // in pixels of the canvas
  };
}

type Moved = {                                           // what a collapse moved, by id, from where to where
  positions: Record<BlockId, { from: { x: number; y: number }; to: { x: number; y: number } }>;
  stacks: Record<StackId, { from: { x: number; y: number }; to: { x: number; y: number } }>;   // stacks that hold no block
};
```

Its default is `{ "positions": {}, "stacks": {}, "layout": { "direction": "TB", "spacing": "normal", "placement": "repulsion", "snap": false, "snap_size": 20 } }`, and a board holds it under the class's id:

```json
"blockr.graph-graph_plugin": {
  "positions": { "a": { "x": 120, "y": 80 }, "b": { "x": 120, "y": 200 } },
  "stacks": {
    "s1": { "collapsed": 1, "moved": { "positions": { "b": { "from": { "x": 120, "y": 240 }, "to": { "x": 120, "y": 200 } } }, "stacks": {} } },
    "s2": { "x": 360, "y": 80 }
  },
  "layout": { "direction": "TB", "spacing": "normal", "placement": "repulsion", "snap": false, "snap_size": 20 }
}
```

A position is where React Flow places the block's node on the canvas ([Drawing the DAG](Rewrite-1.3.2#nodes)), and a converted board keeps today's positions as its file holds them (Boards saved today).
A stack has an entry in `stacks` only where the DAG keeps something about it, which is one of two things that never meet:

- A stack that holds no block has a position, where its box sits, since the box of a stack with blocks fits them ([Drawing the DAG](Rewrite-1.3.2#stacks)).
- A stack with blocks that the DAG shows collapsed has `collapsed`, its place among the collapses in the order they were made, and `moved`, what its collapse moved, since a stack that holds no block shows as a collapsed stack does already (Collapsing and expanding a stack).

The entries of stacks are kept apart from the positions of blocks, since an id is unique only within its collection ([Board objects](Rewrite-1.1.1#ids)).
Each part keeps what one use needs: the positions, so that a board reopens as the user arranged it; the position of a stack, so that a stack that holds no block stays where the user put it, for blocks to be dropped on it; `collapsed`, so that a board reopens with its stacks as the user left them; `moved`, so that expanding a stack puts back what its collapse moved, on a board that has reopened since too; and the layout, so that a layout run later, the place of an added block, the snapping of positions and the sides of the handles that no link uses follow what the user picked.
Both `positions` and `stacks` are keyed by the ids of what they describe, as a plugin keeps what it knows about core's objects ([Plugins](Rewrite-1.1.12#a-plugins-state)), so that a patch names a block or a stack rather than an index of an array, which may hold another by the time undo or redo applies the patch ([Board updates](Rewrite-1.1.2#undo)).

The schema's `description` keywords say what `dag_ext_meta()` says today, so that the assistant needs no code of its own for the DAG ([R/ext.R#L54-L109](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L54-L109), [Board updates](Rewrite-1.1.2#plugins)).
A position is a point on the canvas, with x to the right and y downwards, and a block is about 50 px across, so a block beside another sits about 150 px from it.
Laying the board out again moves every block, so the assistant runs it before it places blocks by hand.

### Commands

| Command | Args | Undo step | What it does |
|---|---|---|---|
| `blockr.graph-change_position` | `positions`, points by block id, and `stacks`, points by stack id, each optional | Yes | Sets the positions given, as a drag or a run of presses of the arrow keys ends with every block and every stack without blocks that it moved, while a position that it gives what the same step adds is where placing starts it (Placing added blocks) |
| `blockr.graph-relayout` | `direction` and `spacing`, each optional | Yes | Sets the settings given and lays the whole board out again with them (Laying the board out again) |
| `blockr.graph-set_placement` | `placement` | No | Sets how added blocks get their place, and moves no block |
| `blockr.graph-set_snap` | `snap` and `snap_size`, each optional | No | Sets whether the DAG snaps the positions that it sets, and to what size, and moves no block, so that the next operation or drag snaps (How the DAG moves blocks) |
| `blockr.graph-collapse_stack` | `stack`, `collapsed` | Yes | Collapses a stack, as the blocks around it close up on it, or expands it, putting back what its collapse moved (Collapsing and expanding a stack) |

The commands that name a block or a stack fail their preflight where the board lacks it, so that the state keys nothing by an id that the board does not hold.
The preflight of `blockr.graph-change_position` also refuses a position for a stack that holds a block, since the box of such a stack fits its blocks.
The preflight of `blockr.graph-collapse_stack` refuses a stack that holds no block, since such a stack shows as a collapsed one does already.
The commands `blockr.graph-change_position` and `blockr.graph-relayout` drop each block and stack that they move from what collapses moved, so that no expand puts it back (Collapsing and expanding a stack).
The commands `blockr.graph-set_placement` and `blockr.graph-set_snap` have `undo: false`, since they move no block.
So a user who drags a block, then turns snapping on, and then presses Undo takes back the drag, while the store still saves the settings with the board ([Board updates](Rewrite-1.1.2#undo)).
Each command's `description` and `args` describe it to the assistant's tools ([The assistant's tools](Rewrite-1.4.2#the-tools)).
The commands declare no `shortcut`, since the DAG binds its keys within its own element ([Drawing the DAG](Rewrite-1.3.2#keys)).
Copying, cutting and pasting are no commands of the DAG's: Copy changes nothing on the board, Cut is Copy followed by core's commands that remove, and Paste runs core's commands that add, so all three are board actions ([Drawing the DAG](Rewrite-1.3.2#the-dags-board-actions)).

### The class's `update` and `afterStep`

With every delta that the store applies, the class's `update` drops the position of each block that the delta removes, the entry in `stacks` of each stack that the delta removes, and what each collapse moved of either ([Board updates](Rewrite-1.1.2#plugins)).
Once the last delta of the step is in, its `afterStep` brings the state in line with the board that the step leaves:

1. It places every block and every stack without blocks that the step adds, from where the step puts it, through the strategy, which under Repulsion makes room around them (Placing added blocks).
   It drops each block and stack that making room moves from what collapses moved, so that no expand puts it back (Collapsing and expanding a stack).
2. A stack that the step leaves without blocks gets a position, its box centred where the box that its blocks spanned before the step was, rather than a place from the strategy.
   The position takes the place of `collapsed` and `moved` in its entry, since a stack that holds no block shows as a collapsed stack does already, so that a block that joins the stack later shows, and what the stack's collapse moved stays where it is.
3. It drops the entry of each stack that holds a block and has a position.

So a batch that adds a block and then links it places the block by its link, which `update` would not see yet as it is given the block's delta, and a batch that empties a stack and fills it again leaves the stack with no position.
Both read nothing on the page, so that they give the same patches wherever they run.

The `afterStep` leaves alone a block that had no position before the step either, and a stack that held no block and had no position before the step either.
Only a board that has just opened holds such a block or stack, and the class's `start` gives each a position (Starting on a board).
So where the frontend takes a step before `start` runs, as the dock does when it adds its first view, `start` still lays out a board that opened without positions.

### Starting on a board

As a board opens, the class's `start` gives a position to every block that lacks one, and to every stack that holds no block and lacks one:

1. Where the board holds no position for any block or stack, as a board that a script builds without positions or a converted file that holds none, it lays the whole board out (Laying the board out again).
2. Where it lacks the positions of some blocks or stacks only, it places those as Beside places what a step adds, whatever the placement, so that every block that has a position opens where it was saved.

In the same delta, it drops each position, each entry in `stacks` and each entry in what a collapse moved that names a block or a stack that the board lacks, as an app script may give one, the entry of each stack that holds a block and has a position, and `collapsed` and `moved` in the entry of each stack that holds no block, which then gets a position.
It names every entry that it drops in one warning about the DAG, of the code `graph_state_dropped`, which holds until the next board opens, as core's note of what the store dropped does, and it logs the same at warn ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)).
A board that the DAG saved holds no such entry, since `update` and `afterStep` keep the state in line with the board, so only a mistake in an app script or a file written elsewhere raises the warning.
The delta has the origin `blockr.graph-graph_plugin` and `undo: false`, as the dock adds its first view, so that undo never takes the board back to blocks without positions ([The dock's state](Rewrite-1.2.1#starting-on-a-board)).
Core calls `start` once the frontend's `render()` has returned ([Plugins](Rewrite-1.1.12#running-a-plugin)).
So a step that the frontend takes as it starts, such as the dock's step that adds its first view, comes before `start`, and `afterStep` leaves to `start` what lacked a position as the board opened (The class's `update` and `afterStep`).
A fresh start of the same app takes the same step on the same board, since both the layout and the strategies give the same positions for the same board ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).

### How the DAG moves blocks

Four operations give blocks their positions, each with a mechanism of its own:

| Operation | When it runs | What it moves | How |
|---|---|---|---|
| Laying the board out | Someone runs `blockr.graph-relayout`, or `start` opens a board that holds no positions | Every block, and every stack without blocks | dagre (Laying the board out again) |
| Placing what is added | `afterStep`, for whatever a step adds, and `start`, for what a board opens without, as Beside places it | The added blocks and stacks, and under Repulsion the blocks around them | Repulsion by default, which makes room around them, or Beside, which moves no other block (Placing added blocks) |
| Making room | Placing under Repulsion, and `blockr.graph-collapse_stack` | The blocks around what is placed or around the stack, less the further away they are | A projection that keeps every two neighbours in their order and apart (Making room) |
| Snapping | After any of the others, and with every `blockr.graph-change_position`, while `snap` is on | Only what the operation or the command moved | Rounds each position to a multiple of `snap_size` |

Each of them gives the same positions for the same board wherever it runs, since it reads nothing on the page.
Each leaves no two nodes closer than the spacing's gap, but for a block that the user or the assistant moves to a place of their own, which it takes as given, snapped where `snap` is on, and two nodes that sat closer before the DAG made room, which keep what they had.
What each cannot do:

- Placing under Beside moves no other block, so on a crowded board a new block can land further from the blocks that it reads from, and pasted blocks further from the point.
- Making room keeps the arrangement around what it makes room for, but not the ranks of a board that was laid out, which laying out again restores.
- Making room keeps every two neighbours in their order, so a stack's place closes only as far as that lets it: the blocks beside a tall stack keep their rows, and leave room above and below its collapsed box.
  And a block inserted among blocks lined up a gap apart, as in a column of a board that was laid out, pushes on the blocks lined up beyond it, as far as the line runs.
- Snapping moves a node by up to half of `snap_size`.
  Where that brings a node that one of the other operations moved closer to another node than the gap, the node moves on to the nearest multiple of `snap_size` that keeps the gap, while a block that someone moves only rounds.
- All of them work from a node's nominal size, so a long name can still overlap the name of a block beside it (notes).

How these rules feel is judged in an app once the DAG draws the board, and they are settled again where they feel wrong ([Client-drawn DAG](Rewrite-1.3#work)).

Turning `snap` on, or changing `snap_size`, moves no block until the next operation or drag, as picking another placement moves none.
Laying the board out again snaps every block at once while `snap` is on, since the DAG snaps every position that the layout gives (Laying the board out again).
During a drag, the DAG snaps each node that moves, so that the drag ends on the point that `blockr.graph-change_position` keeps ([Drawing the DAG](Rewrite-1.3.2#gestures)).
The pages call this snapping, and its size the snap size, since a grid is how the dock arranges a view's panels, while a label on the page may still say "Snap to grid".

### Placing added blocks

The class's `afterStep` places everything that a step adds, one block or stack or many, in one go, whoever adds it: a menu of the DAG, a paste, a template that a package's command adds, or an edit of the assistant.
It places the blocks and the stacks that hold no block in the same step, so that one undo takes them back with their places and with the room that the DAG made for them, in two parts:

1. Each of them starts where the step puts it, through `blockr.graph-change_position`, and otherwise where the strategy starts it (below).
2. The placement strategy that the state names then fits them all in at once: Repulsion keeps them where they start and makes room around them, and Beside moves them on together, so that none of them overlaps another node.

A step puts what it adds at a place of its own in four cases:

- The user right-clicks the canvas and adds a block or a stack from its menu, or drops a link on the canvas, which triggers Append block or Prepend block at the drop ([Drawing the DAG](Rewrite-1.3.2#gestures)).
  The DAG adds `blockr.graph-change_position` with that point to the step of the board action, through the `extend` of `core.boardActions.menu()` or `trigger()` ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).
  Where the board action adds several blocks, as a template that a package's command adds would, the point goes to the first of them in the order of their links, and the others start against it.
- The toolbar's Add block and Create stack put what they add at the middle of the view, through `trigger()`'s `extend`, since what they add is linked to none and would otherwise start after the last block of the first rank, which may be out of view.
- The DAG's Paste puts the blocks and stacks that it adds where they sat as they were copied, moved together so that their middle lands at the point where the user pastes ([Drawing the DAG](Rewrite-1.3.2#the-dags-board-actions)).
- The assistant gives a block a place by adding `blockr.graph-change_position` to the edit that adds it, or leaves the place to the strategy, as the schema's `description` keywords tell it.

Nothing gives a place where a board action adds a block from the menu of a block or a link, as Append block on a block does, nor where another plugin adds one, as the dock's "+" on a tab group does.

A placement strategy returns the positions of the added blocks and stacks, and under Repulsion those of the blocks and stacks that it moves to make room, with illustrative names:

```ts
type Placed = { positions: GraphState["positions"]; stacks: Record<StackId, { x: number; y: number }> };   // the positions of blocks, and of stacks that hold no block

interface Placement {
  id: "repulsion" | "beside";
  place(args: { board: Board; current: Placed; added: { blocks: BlockId[]; stacks: StackId[] }; given: Placed; layout: Layout }): Placed;   // what it adds, and what it moves to make room
}
```

Where the step gives an added block no place, both strategies start it alike, so that it joins the blocks around it in the way their links already run, and the placement decides only what gives way:

- Where the blocks that it reads from already feed other blocks, a block starts one gap past the last of those, level with it: to the right of the rightmost of them where their links run up or down, and below the lowest of them where their links run across.
  So where block A feeds block B below it, a block appended to A starts to the right of B, rather than on B's spot, which B would have to leave.
- Where the blocks that it reads from feed no other block yet, a block starts one rank past them, across from their middle, in the way that the links into them run, and by the layout's direction where no link runs into them: below them from top to bottom, or to their right from left to right.
  So where the user has dragged block A to the right of block X, which feeds it, a block appended to A starts to the right of A, even on a board laid out from top to bottom.
- The DAG reads the way that links run from where their blocks sit, as today's DAG reads the axis of a link from where its two ends sit as it inserts a block ([R/g6r.R#L870-L872](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/g6r.R#L870-L872)), so that a new block follows how the user arranged the blocks around it (notes).
- A block that reads from none but feeds others starts in the same way upstream: one gap past the last of the other blocks that feed the blocks it feeds, level with it, and where none does, one rank before the blocks it feeds, against the way that the links out of them run, or by the layout's direction where no link runs out of them.
- A block linked to none starts after the last block of the first rank, the blocks level with the topmost block from top to bottom, or with the leftmost from left to right.
- An inserted block, which reads from one block and feeds another, starts between the two.
- A stack that holds no block starts as a block linked to none, with the size of its box, which holds the stack's name and the number of its blocks, as a collapsed stack's box does ([Drawing the DAG](Rewrite-1.3.2#stacks)).
- Several blocks that one step adds start in the order of their links, each against those that start before it and off the ones that it would overlap, so that a new chain comes out as a chain ([blockr.dag#117](https://github.com/BristolMyersSquibb/blockr.dag/issues/117)).
- A strategy starts a block by the links of the board that the step leaves, so that a batch that adds a block and then links it places the block by that link, as Append block does ([Board actions](Rewrite-1.1.16#cores-board-actions)).
  A block that one step adds and a later step links stays where it landed, as where the assistant edits through a tool for each command ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).
  So the description of `blockr.core-add_block`, which the assistant's model reads, tells it to link a block that reads from another in the same batch ([blockr.core#750](https://github.com/BristolMyersSquibb/blockr.core/pull/750)).

Then each strategy fits in what the step adds:

- Repulsion, the default, keeps every added block and stack where it starts, while the DAG makes room around them (Making room).
  So an inserted block stays between the two blocks, and the blocks around it make room, the block that the link fed the most.
- Beside moves everything that the step adds on together, keeping how it sits, to the nearest spot where no added node overlaps another node that shows, or the box of a stack that it is not in, with the spacing's gap around it, and moves no other block (notes).
  So an inserted block moves to the nearest free spot, and a paste keeps the arrangement that its blocks were copied in.
- Neither pushes every block downstream of an inserted block on by one gap, as today's DAG does.
- The gaps are those of today's presets, 50 px when compact, 70 px when normal and 100 px when loose, between two nodes and between two ranks alike ([R/layout.R#L66-L76](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/layout.R#L66-L76)).
- A strategy works from a node's nominal size, its mark with room for its label, rather than from what the page measures, since `afterStep` reads nothing on the page (notes).

### Laying the board out again

The command `blockr.graph-relayout` lays every block out with dagre, which the spike picked ([Client-drawn DAG](Rewrite-1.3#proposal)):

1. In `prepare()`, it loads dagre where it has not loaded yet, and lays the board out with the direction and the spacing that the state holds or that its args give, each stack as a cluster that holds its blocks, a stack that holds no block as one node of its box's size, and a collapsed stack as one node of its collapsed size, whose hidden blocks move with it and keep their places in the stack, so that the board stays compact while the stack is collapsed, and expanding it makes room later (Collapsing and expanding a stack).
2. Its `run()` returns the positions that the layout gave the blocks still on the board and the stacks that hold no block, snapped while `snap` is on, and the settings that it was given, as patches to the DAG's state, so that one undo puts every block back ([Board updates](Rewrite-1.1.2#commands)).
   A block that someone added while the layout ran keeps the place that `afterStep` gave it.
   It empties what each collapse moved, since every block moves, so that expanding a stack later makes room around its box (Collapsing and expanding a stack).

The DAG draws a stack's box with the padding that the layout gives a cluster, so the spacing needs no tuning around a padding that the layout does not know, as today's presets do.
The DAG's board action Layout runs the command, and so may the assistant ([Drawing the DAG](Rewrite-1.3.2#the-dags-board-actions)).

### Making room

The DAG makes room for what Repulsion places, and around a stack that collapses or expands, through one projection: each node has a target, and the DAG finds the places nearest the targets that keep what the board held (notes).

- Every two nodes within two gaps of each other keep their order along each axis along which they sit at least half a gap apart, by at least half a gap, and stay apart along the axis along which they sit apart, by the spacing's gap, or by what they had where they sat closer.
- What the DAG makes room for stays where it is: the blocks and stacks that a step adds, with a block that the same step moves, as where the assistant moves a block in the edit that adds another beside it, or the stack's box.
  The nodes within the gap of what a step adds move off it, and so do the nodes that lie in the box of a stack that expands, each taking along the nodes in its way.
- No node comes into the box of a stack that it is not in.
- A collapsed stack moves as one node of its collapsed size, whose hidden blocks move with it by one distance, as laying the board out moves them, while the blocks of an expanded stack move one by one, as blocks in no stack do.

Each node's target is where it sits, so that only what is in the way moves, but around a stack that collapses, where the targets close up on the stack (Collapsing and expanding a stack).
Once the nodes have their places, the DAG averages each node's move with the mean move of the nodes within two gaps of it, and runs the projection once more from there, so that the moves taper off rather than stop at the last node that had to move.
Each axis is one quadratic programme, which VPSC solves exactly, so making room gives the same positions for the same board wherever it runs (notes).

The spike checked it against criteria fixed before it ran, on the largest real board with stacks added and on generated boards, as stacks collapse and expand in any order and as Repulsion adds blocks to the board's most crowded part, and the notes of [Client-drawn DAG](Rewrite-1.3) give the results.

### Collapsing and expanding a stack

A collapsed stack's box is centred where its expanded box is, around its blocks, which keep their positions while they hide.
Dragging the small box moves the stack's hidden blocks by the same distance, in one `blockr.graph-change_position`, so that the stack expands around where the box sits ([Drawing the DAG](Rewrite-1.3.2#stacks)).
The state holds no position for a collapsed stack, so its blocks stay the one source of where it is.
Its entry holds `collapsed`, its place among the collapses, and `moved`, what its collapse moved, from where and to where.
The command `blockr.graph-collapse_stack` sets the entry or drops it, and makes room around the stack in the same delta (Making room):

- Collapsing shrinks the box to its collapsed size, and gives each node around it a target that closes up on it.
  The target lies on the line from the stack's centre through the node, nearer the centre by a share of how far the box's edge moves along that line, exp(-s² / 2σ²), where s is how far the node sits beyond the expanded box's edge, and σ is three times the furthest that the box's edge moves, or the gap where that is more.
  So the blocks next to the stack close up on it the most, those further away less, and the larger the stack, the further the moves reach.
  The collapse takes the place after the last collapse, and keeps in `moved` each block, and each stack that holds no block, that it moved, from where and to where.
- Expanding a stack undoes the collapses made after it, latest first, then its own, putting back each block and stack that still sits where a collapse moved it.
  It then grows the box back around its blocks and makes room around it, so that whatever lies in it moves out, and collapses the stacks that collapsed after it again, in their order, each keeping its moves anew.
  So the board ends as if the stack had never collapsed, in whatever order the stacks collapse and expand, and once every stack is expanded, every block is back where it was, but for what someone moved meanwhile.
- A block, or a stack that holds no block, that someone moves through `blockr.graph-change_position` drops out of what each collapse moved, and so does one that Repulsion moves to make room, so that no expand puts it back.
  Laying the board out again empties what each collapse moved, so that expanding a stack after it makes room around the stack's box alone.

The command takes an undo step, since it moves blocks, so that one undo takes back a collapse or an expand with all that it moved.
So it differs from the dock's `blockr.dock-collapse_rail`, which changes only what the user looks at and takes none ([The dock's state](Rewrite-1.2.1#commands)).

### Defining the state in R

```r
new_graph_plugin <- function(positions = list(), layout = graph_layout(), collapsed = character()) {   # in blockr.graph
  stacks <- stats::setNames(   # an entry for each collapsed stack, by its id, in the order given, with nothing moved
    lapply(seq_along(collapsed), function(i) list(collapsed = i, moved = list(positions = list(), stacks = list()))),
    collapsed
  )
  new_plugin(
    list(positions = positions, stacks = stacks, layout = unclass(layout)),
    "graph_plugin"
  )
}

graph_layout <- function(direction = c("TB", "LR"), spacing = c("normal", "compact", "loose"),
                       placement = c("repulsion", "beside"), snap = FALSE, snap_size = 20) {
  structure(
    list(direction = match.arg(direction), spacing = match.arg(spacing), placement = match.arg(placement),
         snap = snap, snap_size = snap_size),
    class = "graph_layout"
  )
}
```

The package lists the class in its `._BLOCKR_MODULES_` with the id `graph_plugin`, the constructor `new_graph_plugin()`, the name "Workflow" and its module ([Plugins](Rewrite-1.1.12#a-plugin)).
An app script names the collapsed stacks as a character vector, as `collapsed = "s1"`, which the constructor turns into an entry for each stack, by its id, in the vector's order and with nothing moved, so that expanding such a stack makes room around its box alone.
The constructor takes no position for a stack, since `start` places each stack that holds no block.
R writes the state by the JSON Schema that the package ships beside the module, so that an empty `positions`, `stacks` or part of `moved` stays a JSON object, where R would otherwise write the empty array that it writes for an empty list.
The class has no method of `plugin_version()`, so its state is at version 1.
An app script that gives the DAG a state passes the plugin in the board's `plugins`, as `new_board(blocks, plugins = list(new_graph_plugin(positions = pos)))`, and one that passes none gets the default state, which `start` lays out.

### Boards saved today

The method of blockr.convert for blockr.dag's extension makes blockr.graph's plugin with `new_graph_plugin()` from the extension's `positions` and `layout`, whose `placement`, `snap` and `snap_size` take their defaults, and with no stack collapsed and no position for a stack, since today's files keep neither, so that `start` places each stack that holds no block ([The conversion and the migration notes](Rewrite-1.8.3#the-methods-of-other-packages)).
It passes on the positions as the file holds them, so that a position of a block that the file lacks reaches `start`, which names it as it drops it.
A file of blockr.dock 0.1.2 holds no state of the DAG, since the dock wrote every extension's state empty then, so the board opens with the default state, and `start` lays it out ([Saved boards and app scripts across the switch](Rewrite-1.2.2)).

### On a locked board

The store applies a patch inside a plugin's state on a locked board, and leaves it to the plugin's commands to lock what the plugin alone keeps ([Locked boards and the properties of blocks](Rewrite-1.1.11#plugins-on-a-locked-board)).
The DAG locks none of it, so that a reader can explore a locked board as any other: every command of the DAG's passes its preflight there, and a stack that collapses or expands makes room as on any board.
What the DAG keeps changes how the board shows, never what it computes, and today's DAG locks nothing of its own either.
The store still refuses what the board lock fixes, so no block is added, linked or removed there, whichever board action asks ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).
The DAG reads no `lock_rearrange`, which stays the dock's, for its panels ([The dock's state](Rewrite-1.2.1#on-a-locked-board)).
Core's `blockr.core-set_plugin_state` fails its preflight on a locked board, so the DAG's own commands are the only ones that change its state there ([Plugins](Rewrite-1.1.12#a-plugins-state)).

### Testing

The state, the class's `update`, `afterStep` and `start`, the commands and the strategies run on core's `CoreApi` for tests, with neither a browser nor R ([Plugins](Rewrite-1.1.12#testing)), and `new_graph_plugin()` and `graph_layout()` in R's tests.

## Open questions

None.

<details><summary>Notes for implementers</summary>

The nominal size of a node is to settle in the issue that builds the strategies: the mark is 32 px across, as today's node is, and the label below it needs a width from its length, such as the width that the label's font gives its characters, capped where today's labels break.

VPSC finds, along one axis, the places nearest the nodes' targets, each weighted, under constraints that each keep one node at least a given distance after another, and solves that exactly (Dwyer, Marriott and Stuckey, "Fast Node Overlap Removal", Graph Drawing 2005).
WebCola 3.4.0 (MIT) ships it as `Variable`, `Constraint` and `Solver`, in 554 lines of TypeScript, which the DAG can import or copy ([src/vpsc.ts#L345](https://github.com/tgdwyer/WebCola/blob/39539f2dccb04cb321fa9e2ee9532f9e1a9b456d/src/vpsc.ts#L345)).
What the DAG makes room for keeps its place through a weight far above a node's.
Each constraint orders its two nodes as they sat, so the constraints of an axis never form a cycle, and the projection always finds places.
After it, the DAG adds a constraint for each two nodes that have come within the gap of each other, along the axis along which they sat apart, and solves again, up to eight times.
In the spike, the DAG compared every two nodes to find those within two gaps of each other, and a collapse took up to 53 ms on boards of up to 100 blocks, and 139 ms on one of 281 ([Client-drawn DAG](Rewrite-1.3), notes).

React Flow's own snapping rounds only the first node of a drag that moves several, and moves the others by as much, so the DAG snaps a drag itself ([Drawing the DAG](Rewrite-1.3.2#gestures)).

Today's code, at `898a097`: the state and its external control are `new_dag_extension()`, `dag_ext_meta()` and `dag_positions_description()` in `R/ext.R` and `setup_layout_ctrl()`, `push_layout()` and `setup_positions_ctrl()` in `R/srv.R`; the layout is `R/layout.R`; placing is `add_nodes()` and `space_spliced_node()` in `R/g6r.R`; and copy and paste are `R/subboard.R` and `R/action.R`.

The method of blockr.convert reads today's `layout` as `dag_layout()` writes it, with `direction` and `spacing`, and today's `positions` as block ids to points.

Between the deltas of a step, an added block has no position yet, since `afterStep` places it as the step ends, so the DAG draws from `core.store.board()` once the store has announced a change, rather than from the board that comes with each delta.
Between the opening of a board and the delta of `start`, a block may have no position either, so the DAG draws no node for a block without one ([Drawing the DAG](Rewrite-1.3.2#the-canvas)).

Beside looks for the nearest spot in rings around where what a step adds starts, one gap apart, and takes the first spot where no added node overlaps another node, so that the same step on the same board lands in the same place.

The DAG reads the way that links run from the mean offset between the positions of their two blocks, over the links that a rule of Placing added blocks names.
Their axis is the layout's direction's, unless that mean is less than half a rank along it, as for blocks that the user put in a row across a board laid out from top to bottom, where the axis is the other one.
Their way along the axis is the sign of the mean along it, and the layout's direction's where that is zero, as for two links that run opposite ways.
So a link to a block one rank below and far to the side still runs down, as the links to blocks spread across a rank do, where comparing the two offsets of one link, as today's DAG does, would read it as running across and start the next block of a chain beside it.

The layout is given the blocks and links in the order that the board holds them, since dagre's result depends on the order in which it is given nodes and edges, and the same board has to give the same positions.

</details>
