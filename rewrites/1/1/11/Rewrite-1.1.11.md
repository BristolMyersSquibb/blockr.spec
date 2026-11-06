# Locked boards and the properties of blocks
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): who holds a board's lock, which blocks it leaves open, what it fixes of a board's plugins, and the properties of a block besides its state, which are core's, while what a plugin keeps about a block lives in the plugin's state ([Plugins](Rewrite-1.1.12#a-plugins-state)).
It shapes the lock ([blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434)) and core's properties of a block, such as `locked`.
The lock's part of the protocol, its place in the reply to `hello` and what R refuses, is [Wire protocol](Rewrite-1.1.9#locked-boards)'s, and the rest of what a block is, [Board objects](Rewrite-1.1.1#blocks)'.
Block attributes, which said which of a block's sections show and which blocks a lock left open, are gone ([blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474), [blockr#503](https://github.com/orgs/BristolMyersSquibb/discussions/503#discussioncomment-19354484)), and this page settles what takes their place.

## What must hold

1. On a locked board that loads no other board, R evaluates only the opening board's blocks, with their opening links, and every locked block with its opening state, whatever a client sends, as condition 2 of [Client-owned board state](Rewrite-1.1#what-must-hold) asks, for a JSON board that `serve()` is given as for a script's board.
2. A deployment may let a locked board load others, and the lock is then kept by the client alone, on every board it loads: the store refuses what the lock fixes and a front-end draws no control for it, while R evaluates what it is sent.
3. Whether a lock leaves a block open is a property of that block, which a script or a JSON board sets, and never what a front-end shows, and the blockr option `locked` set to `TRUE` alone locks every block, as the dock does today.
4. What a plugin keeps about a block, such as the dock's record of which sections of a card show, lives in the plugin's state, keyed by the block's id, so core needs nothing new for it: the store checks it against the plugin class's schema, saves and undoes it, and drops it with the plugin.
5. A block constructor takes the block's state args and core's properties alone, so a misspelled state arg still fails there, and a script sets what a plugin keeps about a block in the plugin's constructor.
6. A locked board keeps the plugins it holds, its frontend and storage plugin among them, while what a plugin keeps in its state is the plugin's own to lock.

## Today

An app locks a board through the blockr option `locked` ([R/board-lock.R#L39-L47](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-lock.R#L39-L47)), and a locked core board drops every update that changes the board, while a block's own inputs stay editable unless a front-end reports them hidden ([R/board-server.R#L377-L386](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L377-L386)).
The dock freezes every block on a locked board, from what the client reports its cards show ([blockr.dock R/board-server.R#L386-L433](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/board-server.R#L386-L433)), and restores any board in locked mode, since "locking is about preventing layout / structural mutations, not blocking a wholesale state import/export" ([blockr.dock#125](https://github.com/BristolMyersSquibb/blockr.dock/pull/125)).
A deployment that only hides the authoring controls uses a separate option of the dock's, which refuses nothing ([blockr.dock#475](https://github.com/BristolMyersSquibb/blockr.dock/issues/475)).
The dock writes which sections of a card show into the block's payload as it saves ([blockr.dock R/utils-serdes.R#L12-L33](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L12-L33)), and `new_block()` passes its `...` on to the block as R attributes ([R/block-class.R#L180-L184](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L180-L184)).
So a script can set a block's sections in its constructor, as `new_head_block(visible = "outputs")`, which the dock reads with `attr(blk, "visible")`, showing both sections where a block has none ([blockr.dock R/plugin-block.R#L38-L40](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/plugin-block.R#L38-L40)), while no app script, example or vignette of the blockr packages does so.

## Proposal

### Who holds a lock

R can hold a lock only on a board that it has itself and that no other board replaces, since a client that may load another board can load one it made, and R's lock then covers nothing.
So there is one lock, and the blockr option `lock_load` decides who holds it, as it decides whether a locked board loads other boards.
Like the dock's `lock_resize` and `lock_rearrange`, it says what else a locked board locks, is on unless a deployment sets it false, and does nothing on a board that is not locked ([blockr.dock R/utils-dock.R#L311-L343](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-dock.R#L311-L343)).
While it is on, a locked board loads no other board, and R holds the lock, as [Wire protocol](Rewrite-1.1.9#locked-boards) has it, for the board that the app script built or that `serve()` was given.
Set false, it lets a locked board load others, through its storage plugin's `open()` ([Plugins](Rewrite-1.1.12#storage)) or a startup module, and the client alone keeps the lock, on every board the app shows, the opening board included.
The dock's restoring in locked mode becomes `lock_load` set false, while hiding the authoring controls stays an option of the dock's own.
R sends the lock with its reply to `hello` as `{ "load": true }`, or `{ "load": false }` where a deployment set `lock_load` false, and `null` where the app locks nothing, so that the client knows whether the board is locked and whether it may load others, while each block's `locked` says whether the lock leaves the block open ([Which blocks a lock leaves open](#which-blocks-a-lock-leaves-open)), in place of the list of open blocks that [Wire protocol](Rewrite-1.1.9#locked-boards) has the reply carry.

### Which blocks a lock leaves open

Every block holds `locked`, a property of core's beside `name`: `TRUE` locks the block, `FALSE` leaves it open, and `NA`, which a JSON board holds as `null`, follows the board's lock.
It is `NA` unless a script or a command sets it, and a board that today's packages saved opens with `NA` in every block, so that the blockr option `locked` set to `TRUE` alone locks every block, as the dock does today.
Core fixes a block's state only where both the board and the block are locked, which on a locked board is every block whose `locked` is not `FALSE`, and the store says which blocks it fixes, so that no front-end reads `null` as open.
On a locked board a locked block keeps its opening state, which R builds its block expression from as the app starts where R holds the lock, while the store refuses every change to `locked` and to a locked block's state.
So an author leaves a block open to readers by setting its `locked` to `FALSE` in an app that edits the board, saves it and serves the JSON board locked.
On a board that is not locked, core fixes no block, and what a block whose `locked` is `TRUE` does there is the front-end's to decide, such as drawing its inputs read-only until the author unlocks it.

### Plugins on a locked board

A board holds its plugins in `plugins`, a property of core's board ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)), so a locked board keeps them as it keeps its blocks: which plugins it holds, with their classes and names.
The store refuses every patch on a locked board but those under a plugin's state, such as `/plugins/dag/state/positions/a`, so that no command adds, removes or renames a plugin, and no frontend replaces the one the board holds.
What sits inside a plugin's state stays the plugin's own to lock, as [Wire protocol](Rewrite-1.1.9#locked-boards) has it for what a front-end and its extensions keep.
So the store applies a patch under a plugin's state on a locked board, and the plugin's commands refuse what the plugin locks.
A locked dock, for example, still lets a reader switch views, though the active view is part of the dock's state, while it offers no view to add, rename or remove, as today ([blockr.dock R/dock-view.R#L32-L35](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-view.R#L32-L35), [Client-drawn dock and extensions](Rewrite-1.2)).
R reads no plugin's state, so a plugin's lock is the client's alone, and R runs a plugin's request on a locked board only where the plugin's package says that it may ([Plugins](Rewrite-1.1.12#a-plugins-requests)).

### Serving a JSON board locked

Where R holds the lock on a JSON board that `serve()` was given, R reads the board's blocks, links, their `locked` and its board option values to hold it, where it passes any other JSON board on unread.
R builds every block as the app starts and runs no migration, since migrations run in the client ([Serialization](Rewrite-1.1.4#migrations)).
So R refuses to lock a JSON board that it cannot read as today's packages write one: a board with a block whose class the block registry lacks, or with a block's state or a board option's value recorded at a version other than the one R gives.
Its error names each such block and board option, and the deployer opens and saves the board once with today's packages, which migrate it in the client.
Locking only the blocks that R can read would leave the others open, against condition 1, or show readers a board without them.
R ignores the versions of plugin classes, since it reads no plugin's state ([Plugins](Rewrite-1.1.12#a-plugins-state)).

### What a plugin keeps about a block

What a plugin keeps about a block lives in the plugin's state, keyed by the block's id, as the DAG keeps a block's position, so core adds nothing to blocks for it ([Plugins](Rewrite-1.1.12#a-plugins-state)).
The dock keeps in its state which sections of each card show, as `visible: { a: ["outputs"] }`.
The store checks that state against the plugin class's schema after every change, a JSON board saves it, undo takes it back, and the plugin's `update` drops a removed block's entry in the same step, while changing it bumps no revision, since it is not the block's state.
A block that a command copies gets what each plugin's `update` gives a new block, or what the command adds itself, as the DAG's paste adds the pasted blocks' positions in the same delta ([Board updates](Rewrite-1.1.2#board-classes-and-attributes)).

### Block properties in R

A block constructor takes `block_name` and `locked` besides its state args, and nothing else, as `new_head_block(n = 10L, locked = FALSE)`, so a misspelled state arg still fails there, and `locked` is `NA` unless a script gives it.
What a plugin keeps about a block, a script gives the plugin's constructor, keyed by the block's id, as `new_dock_plugin(visible = list(a = "outputs"))`, and R writes it by the schema of the plugin class's state, which the plugin's package ships beside its startup module ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

The page was started from the session of [blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474), which removed `attrs`, core's `visible` and `blockr.core-set_block_attribute`, and left the lock's list of open blocks to this page.
The other pages still describe attributes, and a lock that R alone holds and that lists the blocks it leaves open, since this page settles what takes their place, so settling it chases the change through 1.1, 1.1.1, 1.1.2, 1.1.3, 1.1.4, 1.1.5, 1.1.7, 1.1.8, 1.1.9, 1.1.10, the Glossary's Block, Attribute, Lock, Extension state and External control, the pages of [Client-drawn dock and extensions](Rewrite-1.2) that name `visible`, and [blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434).
R applies every startup schema to the board in `shape_json_board()`, in `R/utils-serdes.R` on `js-state`, before core's schema of a JSON board, and core's build writes the schemas of its board options next to its runtime with `runtimeSchemas()` in `srcts/build/build.ts`, which a package's build can follow for the state of its plugin classes.
Both yyjsonr and jsonlite write `NA` as `null` but read `null` in an object back as `NULL`, so R reads a block's `locked` by the schema of core's block, which turns `null` into `NA`.

</details>
