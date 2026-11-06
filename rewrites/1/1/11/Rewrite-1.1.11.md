# Locked boards and the properties of blocks
Status: draft. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): who holds a board's lock, which blocks it leaves open, and the properties of a block besides its state, which are core's, while what a plugin keeps about a block lives in the plugin's state ([Plugins](Rewrite-1.1.12#a-plugins-state)).
It shapes the lock ([blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434)) and core's properties of a block, such as `locked`.
The lock's part of the protocol, its place in the reply to `hello` and what R refuses, is [Wire protocol](Rewrite-1.1.9#locked-boards)'s, and the rest of what a block is, [Board objects](Rewrite-1.1.1#blocks)'.
Block attributes, which said which of a block's sections show and which blocks a lock left open, are gone ([blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474), [blockr#503](https://github.com/orgs/BristolMyersSquibb/discussions/503#discussioncomment-19354484)), and this page settles what takes their place.

## What must hold

These conditions are proposed and not yet agreed (Open questions, below).

1. On a locked board that R built or read itself, R evaluates only the opening board's blocks, with their opening links, and every locked block with its opening state, whatever a client sends, as condition 2 of [Client-owned board state](Rewrite-1.1#what-must-hold) asks, and it does so for a JSON board that `serve()` is given as for a script's board.
2. An app may lock a board that the client opened, or let a locked board open others, and such a lock is kept by the client alone: the store refuses what it fixes and a front-end draws no control for it, while R evaluates what it is sent.
3. Whether a lock leaves a block open is a property of that block, which a script or a JSON board sets, and never what a front-end shows.
4. What a plugin keeps about a block, such as the dock's record of which sections of a card show, lives in the plugin's state, keyed by the block's id, so core needs nothing new for it: the store checks it against the plugin class's schema, saves and undoes it, and drops it with the plugin.
5. A block constructor takes the block's state args and core's properties alone, so a misspelled state arg still fails there, and a script sets what a plugin keeps about a block in the plugin's constructor.
6. R writes every property of a block by a schema, so a value of length one that its schema has as an array stays an array.

## Today

An app locks a board through the blockr option `locked` ([R/board-lock.R#L39-L47](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-lock.R#L39-L47)), and a locked core board drops every update that changes the board, while a block's own inputs stay editable unless a front-end reports them hidden ([R/board-server.R#L377-L386](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L377-L386)).
The dock freezes every block on a locked board, from what the client reports its cards show ([blockr.dock R/board-server.R#L386-L433](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/board-server.R#L386-L433)), and restores any board in locked mode, since "locking is about preventing layout / structural mutations, not blocking a wholesale state import/export" ([blockr.dock#125](https://github.com/BristolMyersSquibb/blockr.dock/pull/125)).
A deployment that only hides the authoring controls uses a separate option of the dock's, which refuses nothing ([blockr.dock#475](https://github.com/BristolMyersSquibb/blockr.dock/issues/475)).
The dock writes which sections of a card show into the block's payload as it saves ([blockr.dock R/utils-serdes.R#L12-L33](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L12-L33)), and `new_block()` passes its `...` on to the block as R attributes ([R/block-class.R#L180-L184](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L180-L184)).

## Proposal

The proposal is a first sketch, to be argued against the conditions once they are agreed.

### Who holds a lock

R can hold a lock only on a board that it has itself and that no other board replaces, since a client that may open another board can open one it made, and R's lock then covers nothing.
So there is one lock, and an app decides through one blockr option beside `locked` whether a locked board may open other boards.
Without it, R holds the lock, as [Wire protocol](Rewrite-1.1.9#locked-boards) has it, for the board that the app script built or that `serve()` was given.
With it, the client alone keeps the lock, for every board the app shows, the opening board included, and so it does for a board that a startup module opens in place of the opening board.
The dock's restoring in locked mode becomes that option, while hiding the authoring controls stays an option of the dock's own.

### Which blocks a lock leaves open

Every block holds `locked`, a property of core's beside `name`, which is true unless a script or a command sets it false.
On a locked board a block whose `locked` is true keeps its opening state, which R builds its block expression from as the app starts where R holds the lock, while the store refuses every change to `locked` and to a locked block's state.
On a board that is not locked it locks nothing, so an author marks the blocks a reader may change in an app that edits the board, saves it and serves the JSON board locked.
So `locked` set to `TRUE` alone locks every block, as today.

### Serving a JSON board locked

Where R holds the lock on a JSON board that `serve()` was given, R reads the board's blocks, links and their `locked` to hold it, where it passes any other JSON board on unread.
Migrations run in the client ([Serialization](Rewrite-1.1.4#migrations)), so R refuses to lock a JSON board that records a version of a shape other than today's, and the deployer opens and saves the board once with today's packages.

### What a plugin keeps about a block

What a plugin keeps about a block lives in the plugin's state, keyed by the block's id, as the DAG keeps a block's position, so core adds nothing to blocks for it ([Plugins](Rewrite-1.1.12#a-plugins-state)).
The dock keeps in its state which sections of each card show, as `visible: { a: ["outputs"] }`.
The store checks that state against the plugin class's schema after every change, a JSON board saves it, undo takes it back, and the plugin's `update` drops a removed block's entry in the same step, while changing it bumps no revision, since it is not the block's state.
A block that a command copies gets what each plugin's `update` gives a new block, or what the command adds itself, as the DAG's paste adds the pasted blocks' positions in the same delta ([Board updates](Rewrite-1.1.2#board-classes-and-attributes)).

### Block properties in R

A block constructor takes `block_name` and `locked` besides its state args, and nothing else, as `new_head_block(n = 10L, locked = FALSE)`, so a misspelled state arg still fails there.
What a plugin keeps about a block, a script gives the plugin's constructor, keyed by the block's id, as `new_dock_plugin(visible = list(a = "outputs"))`, and R writes it by the schema of the plugin class's state, which the plugin's package ships beside its startup module ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)).

## Open questions

- Whether conditions 1 to 6 are the right ones, which every section of the proposal is argued against, and which the user settles.
- Whether one blockr option for opening other boards decides who holds the lock, and what the option is called, which shapes [blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434) and the dock's lock.
- Whether `locked` is true by default and locks nothing on a board that is not locked, which shapes the JSON board and every block constructor.
- Whether R refuses to lock a JSON board at another version than today's, or locks only the blocks whose versions match.
- What the page is called, once the rest is settled.

<details><summary>Notes for implementers</summary>

The page was started from the session of [blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474), which removed `attrs`, core's `visible` and `blockr.core-set_block_attribute`, and left the lock's list of open blocks to this page.
The other pages still describe attributes, since what takes their place is this page's to settle, so settling it chases their removal through 1.1, 1.1.1, 1.1.2, 1.1.3, 1.1.5, 1.1.7, 1.1.8, 1.1.9, 1.1.10, the Glossary's Block, Attribute, Lock, Extension state and External control, and the pages of [Client-drawn dock and extensions](Rewrite-1.2) that name `visible`.
R applies every startup schema to the board in `shape_json_board()`, in `R/utils-serdes.R` on `js-state`, before core's schema of a JSON board, and core's build writes the schemas of its board options next to its runtime with `runtimeSchemas()` in `srcts/build/build.ts`, which a package's build can follow for the state of its plugin classes.

</details>
