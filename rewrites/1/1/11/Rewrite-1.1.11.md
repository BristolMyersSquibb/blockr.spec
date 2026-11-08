# Locked boards and the properties of blocks
Status: settled on 2026-11-08. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): the three locks an app sets, on loading, on the board and on each block, what each fixes and what R refuses for them, and the properties of a block besides its state, which are core's, while what a plugin keeps about a block lives in the plugin's state ([Plugins](Rewrite-1.1.12#a-plugins-state)).
It shapes the locks ([blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434)) and core's properties of a block, such as `locked`.
The locks' part of the protocol, their place in the reply to `hello` and what R refuses, is [Wire protocol](Rewrite-1.1.9#locked-boards)'s, and the rest of what a block is, [Board objects](Rewrite-1.1.1#blocks)'.
Block attributes, which said which of a block's sections show and which blocks a lock left open, are gone ([blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474), [blockr#503](https://github.com/orgs/BristolMyersSquibb/discussions/503#discussioncomment-19354484)), and this page settles what takes their place.

## What must hold

1. Where the load lock and the board lock are both on, R evaluates only the opening board's blocks, with their opening links, and every locked block with its opening state, whatever a client sends, as condition 2 of [Client-owned board state](Rewrite-1.1#what-must-hold) asks, for a JSON board that `serve()` is given as for a script's board.
2. An app sets each lock on its own: the load lock fixes the app to its opening board, the board lock fixes what every board the app shows holds but its blocks' state, its board options and its plugins' state, and a block's lock fixes the block's state where the board lock is on.
3. Without the load lock, the board lock and the block locks hold for a client that plays by the rules: the store refuses what they fix, a front-end draws no control for it, and R refuses an evaluation that rebinds a block's data inputs or changes a locked block's state, while a client that opens a board it changed loosens them.
4. Whether the board lock leaves a block open is a property of that block, which a script or a JSON board sets, and never what a front-end shows, and a block for which neither sets it follows the board lock, so that the board lock locks every block of a board that today's packages saved, as the dock does today.
5. The board lock leaves board options open, such as dark mode, since no board option reaches what R evaluates.
6. The board lock keeps the plugins a board holds, its frontend and storage plugin among them, which go on running but change nothing that a lock fixes, while what a plugin keeps in its state is the plugin's own to lock.
7. What a plugin keeps about a block, such as the dock's record of which sections of a card show, lives in the plugin's state, keyed by the block's id, so core needs nothing new for it: the store checks it against the plugin class's schema, saves and undoes it, and drops it with the plugin.
8. A block constructor takes the block's state args and core's properties alone, so a misspelled state arg still fails there, and a script sets what a plugin keeps about a block in the plugin's constructor.

## Today

An app locks a board through the blockr option `locked` ([R/board-lock.R#L39-L47](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-lock.R#L39-L47)), and a locked core board drops every update that changes the board, while a block's own inputs stay editable unless a front-end reports them hidden ([R/board-server.R#L377-L386](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L377-L386)).
The dock freezes every block on a locked board, from what the client reports its cards show ([blockr.dock R/board-server.R#L386-L433](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/board-server.R#L386-L433)), and restores any board in locked mode, since "locking is about preventing layout / structural mutations, not blocking a wholesale state import/export" ([blockr.dock#125](https://github.com/BristolMyersSquibb/blockr.dock/pull/125)).
A deployment that only hides the authoring controls uses a separate option of the dock's, which refuses nothing ([blockr.dock#475](https://github.com/BristolMyersSquibb/blockr.dock/issues/475)).
The dock writes which sections of a card show into the block's payload as it saves ([blockr.dock R/utils-serdes.R#L12-L33](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L12-L33)), and `new_block()` passes its `...` on to the block as R attributes ([R/block-class.R#L180-L184](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L180-L184)).
So a script can set a block's sections in its constructor, as `new_head_block(visible = "outputs")`, which the dock reads with `attr(blk, "visible")`, showing both sections where a block has none ([blockr.dock R/plugin-block.R#L38-L40](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/plugin-block.R#L38-L40)), while no app script, example or vignette of the blockr packages does so.

## Proposal

### Three locks

An app sets three locks, each on its own, while a front-end or a plugin may lock more of what it alone keeps, as the dock locks the arrangement of its panels ([Client-drawn dock and extensions](Rewrite-1.2)).
The load lock fixes the app to its opening board, the board lock fixes what the board holds, its blocks and links above all, and a block's lock fixes the block's state.
They meet in two places: a block's lock takes effect only under the board lock, and R can guarantee the board lock and the block locks only where the load lock is on too ([What R refuses](#what-r-refuses)).
A locked board is one under the board lock, whatever the load lock says.

### The load lock

The blockr option `lock_load`, which an app sets as `blockr.lock_load` and a deployment as `BLOCKR_LOCK_LOAD`, fixes the app to its opening board, the one that the app script built or that `serve()` was given, and is off unless one of them sets it.
While it is on, the store refuses every `store.open()` of a board's text, so that no board that the storage plugin's `open()` returns replaces the opening board ([Plugins](Rewrite-1.1.12#storage)), a front-end draws no control for opening one, and core keeps the board R sent where a startup module names another, naming the package ([Drawing the board](Rewrite-1.1.8#starting-the-page)).
It fixes nothing of the opening board itself, so an app with the load lock alone shows one board that a user may still edit, while an app that shows a fixed setup to anyone on the internet sets the board lock too.

### The board lock

The blockr option `locked`, which an app sets as `blockr.locked` and a deployment as `BLOCKR_LOCKED`, as today, locks whichever board the app shows, and is off unless one of them sets it.
While it is on, the store refuses every change but three: one to the state of a block that the board lock leaves open ([Block locks](#block-locks)), one to a board option's value ([Board options on a locked board](#board-options-on-a-locked-board)), and one inside a plugin's state ([Plugins on a locked board](#plugins-on-a-locked-board)).
So it fixes the board's DAG, its blocks and links, and with it the board's name, every block's name and `locked`, the stacks, and which plugins the board holds, with their classes and names.
A front-end draws no control for what it fixes, and nor does a plugin.
Without the load lock, a reader may open other boards, each locked, but change the setup of none, as today's dock restores any board in locked mode ([blockr.dock#125](https://github.com/BristolMyersSquibb/blockr.dock/pull/125)), while a deployment that only hides the authoring controls keeps the dock's option for that, which refuses nothing ([blockr.dock#475](https://github.com/BristolMyersSquibb/blockr.dock/issues/475)).

### Block locks

Every block holds `locked`, a property of core's beside `name`: `TRUE` locks the block, `FALSE` leaves it open, and `NA`, which a JSON board holds as `null`, follows the board lock.
Core fixes a block's state only where both the board lock and the block's lock are on, which under the board lock is every block whose `locked` is `TRUE` or `NA`, and the store says which blocks it fixes, so that no front-end reads `null` as open.
A block's `locked` is `NA` unless a script or a command sets it, and a board that today's packages saved opens with `NA` in every block, so that the board lock locks every block of such a board, as the dock does today.
Under the board lock, a locked block keeps its opening state, and the store refuses every change to it.
So an author leaves a block open to readers by setting its `locked` to `FALSE` in an app without the board lock, saves the board and serves it with the board lock on.
Without the board lock, core fixes no block, and what a block whose `locked` is `TRUE` does there is the front-end's to decide, such as drawing its inputs read-only until the author unlocks it.

### Board options on a locked board

The board lock leaves board options open, so that a reader may switch to dark mode or show more rows of a table, as on any board.
A block class reads board options only in its requests, and an output class in its coercion, so no board option reaches a block expression ([Block classes in R](Rewrite-1.1.5#requests)), and a reader who changes one changes nothing that R evaluates.
So R takes the board option values that a request carries, under the board lock as without it, for an output, the requests of its output class and its renderer, and the requests of a block left open ([Wire protocol](Rewrite-1.1.9#locked-boards)).
Where the load lock is on too, R answers a locked block's request with the opening values instead, as it answers it with the block's opening state, since a board option may say what such a request reads, as `data_dir` names the directory that blockr.io's read block lists files from ([Block classes in R](Rewrite-1.1.5#the-block-class)).
Without the load lock, R knows no opening values, so it takes the request's for a locked block too.
A board option's own request runs under the board lock only where its package says that it may, as a plugin's does (below).

### Plugins on a locked board

A board holds its plugins in `plugins`, a property of core's board ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)), so the board lock fixes which plugins it holds, as it fixes its blocks.
While the board lock is on, the store refuses every patch but those inside a plugin's state, such as `/plugins/dag/state/positions/a`, so that no command adds, removes or renames a plugin, and no frontend replaces the one the board holds.
A plugin goes on running under the board lock, but only reads the board: the store refuses every change that a lock fixes, whichever plugin's command makes it, so that neither the DAG nor the assistant adds a block, links one or changes a locked block's state.
A plugin reads the board and its results as on any board, and draws no control for what a lock fixes, as a front-end draws none, by the locks that core's API holds ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
What sits inside a plugin's state stays the plugin's own to lock, as [Wire protocol](Rewrite-1.1.9#locked-boards) has it, so the store applies a patch inside a plugin's state under the board lock, and the plugin's commands refuse what the plugin locks.
A locked dock, for example, still lets a reader switch views, though the active view is part of the dock's state, while it offers no view to add, rename or remove, as today ([blockr.dock R/dock-view.R#L32-L35](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-view.R#L32-L35), [Client-drawn dock and extensions](Rewrite-1.2)).
R reads no plugin's state, so a plugin's own lock is the client's alone, and R runs a plugin's request under the board lock only where the plugin's package says that it may, as a package would for a request that only reads, such as the assistant's answer to a question about the board, and not for one that evaluates what the client sends, such as the assistant's trial of proposed args ([Plugins](Rewrite-1.1.12#a-plugins-requests), [Wire protocol](Rewrite-1.1.9#requests)).

### What R refuses

R refuses only what it can tell breaks the board lock or a block's lock, and nothing for the load lock, which the client keeps, since no message opens a board ([Wire protocol](Rewrite-1.1.9#opening-a-board)).
Under the board lock, R holds every block to its data inputs, which the board lock fixes, and every locked block to its state, which the block's lock fixes: it refuses an evaluation that binds a block's data inputs to other blocks or gives a locked block another state, and it runs no action of a locked block.
It also runs a board option's or a plugin's request under the board lock only where its package says that it may (above), which needs no board.
What R holds a block to depends on the load lock, since R can hold a block to a board only where it has that board itself and no other board replaces it, while a client that may load another board can load one it changed.
Where the load lock is on too, R holds every block to the opening board, which it built, or read where `serve()` was given a JSON board (below): it evaluates only that board's blocks, with their opening links, and every locked block with its opening state, whatever a client sends, as [Wire protocol](Rewrite-1.1.9#locked-boards) has it, so that the R process evaluates only what the deployer intends.
Without the load lock, R cannot tell which board the client shows, since the board is the client's, so it holds a block to what the client sent before.
An evaluation and an action carry the block's `locked`, which R reads as the store does, and once R has evaluated a block since the board opened, which starts the session afresh ([Wire protocol](Rewrite-1.1.9#opening-a-board)), it holds the block to the data inputs of that evaluation and, where the block is locked, to its state.
That holds against a defect, such as a store that applies a change it should refuse, but not against a client that sends another `locked`, adds a block or opens a board it changed, beforehand or through code of its own run in the page, so the board lock and the block locks are a guarantee only with the load lock.

### Serving a JSON board locked

Where the load lock and the board lock are both on, R reads the blocks, links, their `locked` and the board option values of a JSON board that `serve()` was given, to hold every block to it ([What R refuses](#what-r-refuses)), where it passes any other JSON board on unread.
R builds every block as the app starts and runs no migration, since migrations run in the client ([Serialization](Rewrite-1.1.4#migrations)).
So, with both locks on, R refuses a JSON board that it cannot read as today's packages write one: a board with a block whose class the block registry lacks, or with a block's state or a board option's value recorded at a version other than the one R gives.
Its error names each such block and board option, and the deployer opens and saves the board once with today's packages, which migrate it in the client.
Locking only the blocks that R can read would leave the others open, against condition 1, or show readers a board without them.
R ignores the versions of plugin classes, since it reads no plugin's state ([Plugins](Rewrite-1.1.12#a-plugins-state)).

### The locks in the reply to `hello`

R sends the locks with its reply to `hello`, as `{ "board": true, "load": true }`, with `false` for a lock that the app does not set, so that the client knows whether the board lock and the load lock are on, while each block's `locked` says whether the board lock leaves the block open ([Block locks](#block-locks), [Wire protocol](Rewrite-1.1.9#handshake)).

### What a plugin keeps about a block

What a plugin keeps about a block lives in the plugin's state, keyed by the block's id, as the DAG keeps a block's position, so core adds nothing to blocks for it ([Plugins](Rewrite-1.1.12#a-plugins-state)).
The dock keeps in its state which sections of each card show, as `visible: { a: ["outputs"] }`.
The store checks that state against the plugin class's schema after every change, a JSON board saves it, undo takes it back, and the plugin's `update` drops a removed block's entry in the same step, while changing it bumps no revision, since it is not the block's state.
A block that a command copies gets what each plugin's `update` gives a new block, or what the command adds itself, as the DAG's paste adds the pasted blocks' positions in the same delta ([Board updates](Rewrite-1.1.2#board-classes)).

### Block properties in R

A block constructor takes `block_name` and `locked` besides its state args, and nothing else, as `new_head_block(n = 10L, locked = FALSE)`, so a misspelled state arg still fails there, and `locked` is `NA` unless a script gives it.
What a plugin keeps about a block, a script gives the plugin's constructor, keyed by the block's id, as `new_dock_plugin(visible = list(a = "outputs"))`, and R writes it by the schema of the plugin class's state, which the plugin's package ships beside its startup module ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

The page was started from the session of [blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474), which removed `attrs`, core's `visible` and `blockr.core-set_block_attribute`, and left the lock's list of open blocks to this page.
R applies every startup schema to the board in `shape_json_board()`, in `R/utils-serdes.R` on `js-state`, before core's schema of a JSON board, and core's build writes the schemas of its board options next to its runtime with `runtimeSchemas()` in `srcts/build/build.ts`, which a package's build can follow for the state of its plugin classes.
Both yyjsonr and jsonlite write `NA` as `null` but read `null` in an object back as `NULL`, so R reads a block's `locked` by the schema of core's block, which turns `null` into `NA`.

</details>
