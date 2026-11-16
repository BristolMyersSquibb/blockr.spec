# The DAG's state, commands and placement
Status: review. Design for [Client-drawn DAG](Rewrite-1.3).

One of the design pages of the client-drawn DAG ([Client-drawn DAG](Rewrite-1.3)): what the DAG plugin keeps in its state, the commands that change it, its class's `update` and `start`, how it places the blocks that someone adds and lays the whole board out again, how an app script writes its state in R, how boards saved today cross, and what the DAG does on a locked board.
It shapes the Work items of [Client-drawn DAG](Rewrite-1.3#work) that make the DAG a plugin in R and build its class in the client, and the spike that decides between dagre and elkjs.
What the DAG draws, its menus, its own board actions and its toolbar are [Drawing the DAG](Rewrite-1.3.2)'s, and what a plugin's state is and how the store keeps it are [Plugins](Rewrite-1.1.12#a-plugins-state)'s.

## What must hold

Conditions 4, 6 and 7 of [Client-drawn DAG](Rewrite-1.3#what-must-hold) rest on this page.

1. The state holds a position for every block of the board, the layout's direction, spacing and placement, and the stacks that the DAG shows collapsed, in the shape of one JSON Schema, which describes each part for the assistant.
2. Adding a block gives it a position in the same step, so that undo takes back the block and its position together, and moves no other block.
3. Only `blockr.dag-relayout` moves every block at once, and only when someone runs it.
4. The class's `update` reads only the change and the board, so that it gives the same patches wherever it runs ([Board updates](Rewrite-1.1.2#plugins)).
5. A board saved today opens with its positions and its layout's direction and spacing, and a position keeps its meaning across the switch.
6. On a locked board, the DAG's commands move no block unless the deployment leaves rearranging to readers, while collapsing a stack stays open.

## Today

Today's DAG keeps `positions` and `layout` as the state of its extension, which the board update's `extensions` sets from outside, and keeps them in step with the canvas through two guards against the echo ([R/srv.R#L114-L275](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/srv.R#L114-L275)).
Which stacks are collapsed lives on the canvas alone, so a saved board reopens with every stack expanded.
A block that is added goes to the last position of the mouse on the canvas, and blocks added at once stack 130 px apart below it ([R/g6r.R#L904-L923](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/g6r.R#L904-L923)).
A block inserted into a link goes between the link's two ends, and every block below it moves down to make room ([R/g6r.R#L856-L903](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/g6r.R#L856-L903)).
The layout of the whole board is G6's dagre, whose spacing presets are tuned around the padding of a stack's box, which dagre does not know ([R/layout.R#L66-L96](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/layout.R#L66-L96)), and G6 lays the board out again as blocks come ([blockr.dag#40](https://github.com/BristolMyersSquibb/blockr.dag/issues/40)).

## Proposal

### The state

With illustrative names:

```ts
interface DagState {                                     // the state of blockr.dag-dag_plugin, at version 1
  positions: Record<BlockId, { x: number; y: number }>;  // the centre of each block's node, in pixels of the canvas
  layout: {
    direction: "TB" | "LR";                              // top to bottom, or left to right
    spacing: "compact" | "normal" | "loose";             // the gaps between blocks and between ranks
    placement: "beside" | "grid";                        // how a block that someone adds gets its place
  };
  collapsed: StackId[];                                  // the stacks that the DAG shows collapsed
}
```

Its default is `{ "positions": {}, "layout": { "direction": "TB", "spacing": "normal", "placement": "beside" }, "collapsed": [] }`, and a board holds it under the class's id:

```json
"blockr.dag-dag_plugin": {
  "positions": { "a": { "x": 120, "y": 80 }, "b": { "x": 120, "y": 200 } },
  "layout": { "direction": "TB", "spacing": "normal", "placement": "beside" },
  "collapsed": ["s1"]
}
```

A position is the centre of the block's node, as today's positions are, so that converted positions keep their meaning.
React Flow places a node by its top left corner, and a node in a group relative to the group, so the DAG converts as it draws ([Drawing the DAG](Rewrite-1.3.2#nodes)).
Each part keeps what one use needs: the positions, so that a board reopens as the user arranged it; the layout, so that a layout run later, the place of an added block and the sides of the ports follow what the user picked; and `collapsed`, so that a board reopens with its stacks as the user left them.

The schema's `description` keywords say what `dag_ext_meta()` says today, so that the assistant needs no code of its own for the DAG ([R/ext.R#L54-L109](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L54-L109), [Board updates](Rewrite-1.1.2#plugins)).
A position is a point on the canvas, with x to the right and y downwards, and a block is about 50 px across, so a block beside another sits about 150 px from it.
Laying the board out again moves every block, so the assistant runs it before it places blocks by hand.

### Commands

| Command | Args | Undo step | What it does |
|---|---|---|---|
| `blockr.dag-change_position` | `positions`, points by block id | Yes | Sets the positions given, as a drag ends with every block that it moved, or as the step of a board action puts a block where the user pointed |
| `blockr.dag-relayout` | `direction` and `spacing`, each optional | Yes | Sets the settings given and lays the whole board out again with them (Laying the board out again) |
| `blockr.dag-set_placement` | `placement` | Yes | Sets how added blocks get their place, and moves no block |
| `blockr.dag-collapse_stack` | `stack`, `collapsed` | No, with `undo: false` | Collapses a stack or expands it, which changes only what the user looks at, as the dock's `blockr.dock-collapse_rail` does ([The dock's state](Rewrite-1.2.1#commands)) |
| `blockr.dag-paste` | `board`, the text of a JSON board, and `at`, a point | Yes | Adds the blocks, links and stacks of a copied board under new ids, with their positions (Pasting) |

Each command's `description` and `args` describe it to the assistant's tools ([The assistant's tools](Rewrite-1.4.2#the-tools)).
The commands declare no `shortcut`, since the DAG binds its keys within its own element ([Drawing the DAG](Rewrite-1.3.2#keys)).
Copying and cutting are no commands of the DAG's: Copy changes nothing on the board, and Cut is Copy followed by core's commands that remove, so both are board actions ([Drawing the DAG](Rewrite-1.3.2#the-dags-board-actions)).

### The class's `update`

With every change that the store applies, the class's `update` returns patches to the DAG's state in the same step ([Board updates](Rewrite-1.1.2#plugins)):

1. It drops the position of each block that the change removes, and each stack that the change removes from `collapsed`.
2. It places each block that the change adds and that has no position yet (Placing added blocks).

It reads only the change and the board, and nothing on the page, so that it gives the same patches wherever it runs.

### Starting on a board

As a board opens, the class's `start` gives a position to every block that lacks one:

1. Where the board holds no position for any block, as a board that a script builds without positions or a converted file that holds none, it lays the whole board out (Laying the board out again).
2. Where it lacks the positions of some blocks only, it places those through the strategy, as it places added blocks.

Either is one delta of the origin `blockr.dag-dag_plugin` with `undo: false`, as the dock adds its first view, so that undo never takes the board back to blocks without positions ([The dock's state](Rewrite-1.2.1#starting-on-a-board)).
A fresh start of the same app takes the same step on the same board, since both the layout and the strategies give the same positions for the same board ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).

### Placing added blocks

A placement strategy takes every existing position as fixed, and returns positions for the added blocks alone, with illustrative names:

```ts
interface Placement {
  id: "beside" | "grid";
  place(args: { board: Board; fixed: Positions; added: BlockId[]; preferred: Positions; layout: Layout }): Positions;
}
```

- Beside, the default, starts a block one rank after the blocks it reads from, below them from top to bottom or to their right from left to right, across from their middle.
  A block that reads from none starts after the last block of the first rank.
  Then it moves the block to the nearest spot where its node overlaps no other node with the spacing's gap around it.
- Grid snaps a block to the nearest free cell of a grid whose cells are a node with the spacing's gap around it, starting from where Beside would start it.
- The gaps are those of today's presets, 50 px when compact, 70 px when normal and 100 px when loose, between two nodes and between two ranks alike ([R/layout.R#L66-L76](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/layout.R#L66-L76)).
- A strategy works from a node's nominal size, its mark with room for its label, rather than from what the page measures, since `update` reads nothing on the page (notes).
- Several blocks that one change adds, as the assistant adds them, are placed in the order of their links, each against the blocks placed before it, so that a new chain comes out as a chain ([blockr.dag#117](https://github.com/BristolMyersSquibb/blockr.dag/issues/117)).
- Where the user points, as by dropping a link on the canvas, the DAG runs the strategy itself with that point as the block's preferred start, and adds `blockr.dag-change_position` with the result to the step of the board action that adds the block ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).
  So the block lands where the user pointed, moved only off what it would overlap.
- An inserted block starts between the two ends of the link that it splits, and no block moves to make room for it, unlike today's.

Repulsion fits the same interface, through d3-force, which pins the existing nodes, takes a seeded random source and runs its ticks without timers, so that it gives the same positions each time (notes).
It comes in should Beside and Grid prove too rigid.

### Laying the board out again

The command `blockr.dag-relayout` lays every block out with dagre or elkjs, whichever the spike picks ([Client-drawn DAG](Rewrite-1.3#proposal)):

1. In `prepare()`, it loads the layout's library where it has not loaded yet, and lays the board out with the direction and the spacing that the state holds or that its args give, each stack as a cluster that holds its blocks, and a collapsed stack as one node of its collapsed size.
2. Its `run()` returns the positions of every block and the settings that it was given, as patches to the DAG's state, so that one undo puts every block back ([Board updates](Rewrite-1.1.2#commands)).

The DAG draws a stack's box with the padding that the layout gives a cluster, so the spacing needs no tuning around a padding that the layout does not know, as today's presets do.
The DAG's board action Layout runs the command, and so may the assistant ([Drawing the DAG](Rewrite-1.3.2#the-dags-board-actions)).

### Pasting

The command `blockr.dag-paste` takes the text of a JSON board, as the DAG's Copy writes one, and a point:

1. It reads the board through `core.store.read()`, which gives the board that opening the text would give, its blocks migrated by the versions that it records, and what opening it would drop, holding nothing, as `check()` does for opening ([Board updates](Rewrite-1.1.2#the-store)).
2. It mints a new id for each block, link and stack, and points the pasted links and stacks at the new ids.
3. It moves the pasted positions together, so that their middle lands at the point, and then each block off what it would overlap, as Beside does.
4. It returns one delta with the blocks, links and stacks and their positions, so that one undo takes the paste back ([Board updates](Rewrite-1.1.2#plugins)).

A block whose class the app lacks is left out of the paste, with a notification that names it, as opening a board drops such a block ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)).

### Defining the state in R

```r
new_dag_plugin <- function(positions = list(), layout = dag_layout(), collapsed = character()) {   # in blockr.dag
  new_plugin(list(positions = positions, layout = unclass(layout), collapsed = collapsed), "dag_plugin")
}

dag_layout <- function(direction = c("TB", "LR"), spacing = c("normal", "compact", "loose"),
                       placement = c("beside", "grid")) {
  structure(
    list(direction = match.arg(direction), spacing = match.arg(spacing), placement = match.arg(placement)),
    class = "dag_layout"
  )
}
```

The package lists the class in its `._BLOCKR_MODULES_` with the id `dag_plugin`, the constructor `new_dag_plugin()`, the name "Workflow" and its module ([Plugins](Rewrite-1.1.12#a-plugin)).
R writes the state by the JSON Schema that the package ships beside the module, so that `collapsed` with one stack stays an array.
The class has no method of `plugin_version()`, so its state is at version 1.
An app script that gives the DAG a state passes the plugin in the board's `plugins`, as `new_board(blocks, plugins = list(new_dag_plugin(positions = pos)))`, and one that passes none gets the default state, which `start` lays out.

### Boards saved today

The method of blockr.convert for the DAG's extension makes the plugin with `new_dag_plugin()` from the extension's `positions` and `layout`, whose `placement` takes its default, and with no stack collapsed, since today's files keep none ([The conversion and the migration notes](Rewrite-1.9#the-methods-of-other-packages)).
A file of blockr.dock 0.1.2 holds no state of the DAG, since the dock wrote every extension's state empty then, so the board opens with the default state, and `start` lays it out ([Saved boards and app scripts across the switch](Rewrite-1.2.2)).

### On a locked board

The store applies a patch inside the DAG's state on a locked board, and leaves its lock to the DAG's commands, as for the dock's ([The dock's state](Rewrite-1.2.1#on-a-locked-board)):

- Under the board lock, `blockr.dag-change_position`, `blockr.dag-relayout` and `blockr.dag-set_placement` fail their preflight, unless the blockr option `lock_rearrange` is `FALSE`, which the class reads once as it starts, through `core.blockrOption()`.
- The command `blockr.dag-collapse_stack` passes it, since it changes only what the reader looks at.
- The command `blockr.dag-paste` fails it, since the store refuses the blocks that it would add ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).
- The delta of `start` still applies, so that the DAG can draw a locked board that holds no positions.

Core's `blockr.core-set_plugin_state` fails its preflight on a locked board, so nothing else moves a block there ([Plugins](Rewrite-1.1.12#a-plugins-state)).

### Testing

The state, the class's `update` and `start`, the commands and the strategies run on core's `CoreApi` for tests, with neither a browser nor R ([Plugins](Rewrite-1.1.12#testing)), and `new_dag_plugin()` and `dag_layout()` in R's tests.

## Open questions

None.

<details><summary>Notes for implementers</summary>

The nominal size of a node is to settle in the issue that builds the strategies: the mark is 32 px across, as today's node is, and the label below it needs a width from its length, such as the width that the label's font gives its characters, capped where today's labels break.

Version 3.0.1 of d3-force (ISC, 5.7 KB gzipped) keeps a node with `fx` and `fy` where they say, takes a seeded `randomSource()` and steps through `tick()` without timers ([d3-force](https://d3js.org/d3-force/simulation)).

Today's code, at `898a097`: the state and its external control are `new_dag_extension()`, `dag_ext_meta()` and `dag_positions_description()` in `R/ext.R` and `setup_layout_ctrl()`, `push_layout()` and `setup_positions_ctrl()` in `R/srv.R`; the layout is `R/layout.R`; placing is `add_nodes()` and `space_spliced_node()` in `R/g6r.R`; and copy and paste are `R/subboard.R` and `R/action.R`.

The method of blockr.convert reads today's `layout` as `dag_layout()` writes it, with `direction` and `spacing`, and today's `positions` as block ids to points.

</details>
