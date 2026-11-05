# Locked boards and the properties of blocks
Status: draft. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): who holds a board's lock, which blocks it leaves open, and the properties of a block besides its state, core's and those that a board class adds.
It shapes the lock ([blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434)) and the properties that board classes add to blocks, which no issue asks for yet.
The lock's part of the protocol, its place in the reply to `hello` and what R refuses, is [Wire protocol](Rewrite-1.1.9#locked-boards)'s, and the rest of what a block is, [Board objects](Rewrite-1.1.1#blocks)'.
Block attributes, which said which of a block's sections show and which blocks a lock left open, are gone ([blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474), [blockr#503](https://github.com/orgs/BristolMyersSquibb/discussions/503#discussioncomment-19354484)), and this page settles what takes their place.

## What must hold

These conditions are proposed and not yet agreed (Open questions, below).

1. On a locked board that R built or read itself, R evaluates only the opening board's blocks, with their opening links, and every locked block with its opening state, whatever a client sends, as condition 2 of [Client-owned board state](Rewrite-1.1#what-must-hold) asks, and it does so for a JSON board that `serve()` is given as for a script's board.
2. An app may lock a board that the client opened, or let a locked board open others, and such a lock is kept by the client alone: the store refuses what it fixes and a front-end draws no control for it, while R evaluates what it is sent.
3. Whether a lock leaves a block open is a property of that block, which a script or a JSON board sets, and never what a front-end shows.
4. A board class adds properties to blocks without a change to core, as it adds properties to the board, such as the dock's record of which sections of a card show, and core carries them without reading them: it checks each against its schema, saves and undoes it, and drops it where no loaded class adds it.
5. A script sets every property of a block in the block's constructor, and a misspelled state arg still fails there.
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

### Properties that a board class adds to blocks

A board class's definition gives the properties that it adds to every block, as it gives those that it adds to the board, each with a schema and a default ([Board objects](Rewrite-1.1.1#extending-cores-objects)), such as the dock's `visible`, the sections of a card that show.
The store checks each against its schema after every change, a JSON board saves it, undo takes it back, and opening a board drops it where the class that the board is built as does not add it, while changing it bumps no revision, since it is not the block's state.
A block carries them wherever it goes, so a copied block keeps them, and the class's commands change them.

### Block properties in R

A block constructor takes `block_name` and `locked` besides its state args, and in `...` the properties that board classes add to blocks, as `new_head_block(n = 10L, locked = FALSE, visible = "outputs")`.
The JSON Schema of a JSON board knows only core's properties, so the package that adds a property gives its shape in the schema beside its startup module, laid out like the board under `blocks`, which R applies to the whole board as it applies every such schema, and which the package's build writes from its board class's definition, so that the shape has one source.
The constructor refuses a name in `...` that no loaded package's schema declares as a property of blocks, so that a misspelled state arg still fails, and a name that is both a state arg and such a property, naming both.

## Open questions

- Whether conditions 1 to 6 are the right ones, which every section of the proposal is argued against, and which the user settles.
- Whether one blockr option for opening other boards decides who holds the lock, and what the option is called, which shapes [blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434) and the dock's lock.
- Whether `locked` is true by default and locks nothing on a board that is not locked, which shapes the JSON board and every block constructor.
- Whether a block carries the properties that a board class adds, or the class keeps them in a property of the board keyed by block id, as the DAG keeps its positions, which needs nothing new in core.
- Whether block constructors take those properties in `...`, with the check above, or whether the package that adds them offers a function of its own that sets them on an R block, which keeps constructors as they are.
- Whether R refuses to lock a JSON board at another version than today's, or locks only the blocks whose versions match.
- What the page is called, once the rest is settled.

<details><summary>Notes for implementers</summary>

The page was started from the session of [blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474), which removed `attrs`, core's `visible` and `blockr.core-set_block_attribute`, and left the lock's list of open blocks to this page.
R applies every startup schema to the board in `shape_json_board()`, in `R/utils-serdes.R` on `js-state`, before core's schema of a JSON board, and core's build writes the schemas of its board options next to its runtime with `runtimeSchemas()` in `srcts/build/build.ts`, which a package's build can follow for the properties that its board class adds.

</details>
