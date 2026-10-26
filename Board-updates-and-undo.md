Status: draft. Design for [Board state owned by the client](Board-state-owned-by-the-client).

One of the API proposals for the client-owned board ([Board state owned by the client](Board-state-owned-by-the-client)): how the board changes. It builds on the [document model](Board-document-model) and shapes the store and the command registry ([blockr.core#394](https://github.com/BristolMyersSquibb/blockr.core/issues/394)). Which blocks a change makes R evaluate is the evaluation proposal ([Evaluation in the client](Evaluation-in-the-client)).

## What must hold

1. Every change to the board is one delta in the `add`, `mod` and `rm` shape of today's `update()`, whoever makes it: a user's input, a menu, a shortcut, an extension or the assistant.
2. A delta reaches everything in the board that refers to what it changes in the same step, so removing a block takes it out of the dock and the DAG at once, and undo brings it back in one step.
3. A delta applies entirely or not at all.
4. Menus, shortcuts, extensions and the assistant's tools all edit through one command registry.
5. Anything can follow the board's changes as they happen, such as a session package saving drafts.
6. Opening a board, at startup or later, replaces the document instead of changing it, and ends in the same place either way.

## Today

Every payload goes through one `board_update` reactive value: one observer validates and augments it, another applies it ([R/board-server.R#L300-L446](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L300-L446)). A block's `mod` takes only its `external_ctrl_vars()` and its name, a link's `mod` becomes a removal and an addition ([#L1784-L1805](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L1784-L1805), [#L2165-L2168](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L2165-L2168)), and a second write in one flush replaces the first, so the dock and the assistant merge into it ([blockr.dock R/board-server.R#L370-L384](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/board-server.R#L370-L384)). Several edits bypass `update()` altogether: a block's own inputs, the dock's card sections, board options, the ctrl plugin and the DAG's positions ([blockr.dock R/utils-serdes.R#L6-L21](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L6-L21), [R/plugin-control.R#L53-L87](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-control.R#L53-L87)). There is no undo anywhere, and a failed apply may leave a payload half applied ([blockr.assistant R/ext-server.R#L1138-L1170](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/ext-server.R#L1138-L1170)).

The dock's actions are Shiny modules fired through counter-bumped reactive values ([R/action-class.R#L43-L199](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/action-class.R#L43-L199)), core's plugins edit through their own modals, and the assistant has tools of its own for the same edits ([blockr.assistant R/tools-mutation.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/tools-mutation.R)). Only the DAG has shortcuts ([blockr.dag R/g6r.R#L1025-L1046](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/g6r.R#L1025-L1046)).

## Proposal

### The store

The store is the TypeScript object in core's JS API that holds a board and through which every change to it passes. There is one per board, which core creates when it opens the page's board and hands to front-ends, extensions and block modules through `CoreApi` ([Front-ends and extension points](Front-ends-and-extension-points)) and the module host ([blockr.core#398](https://github.com/BristolMyersSquibb/blockr.core/issues/398)), rather than a global, so that tests, and a page that shows two boards one day, can create more than one. The command registry is an object of its own (below).

```ts
type Origin = "user" | "assistant" | string;                 // a peer, once a sync add-on exists

type Change =
  | { delta: Delta; origin: Origin }                         // a committed delta, as expanded
  | { opened: Board; dropped: Dropped[] };                   // an opened board, and what R dropped (#405)

interface Store {
  board(): Board;                                            // the current board, as a signal
  subscribe(fn: (change: Change, board: Board) => void): () => void;   // after every commit and every open

  apply(delta: Delta, origin?: Origin): void;                // expands, checks, commits and announces a delta, in order
  open(saved: Json): Promise<Dropped[]>;                     // has R open a saved board, then replaces the document

  undo(origin?: Origin): void;                               // reverts that origin's last step
  redo(origin?: Origin): void;
  canUndo(origin?: Origin): boolean;
  canRedo(origin?: Origin): boolean;

  extend(boardClass: string, ext: {
    schema?: JsonSchema;                                     // validates the fields the subclass adds (#405)
    expand?: (delta: Delta, board: Board) => Delta;          // its part of the expansion step, below
  }): void;
}
```

Besides the board, the store keeps the undo and redo steps of each origin, the queue of deltas waiting to apply, its subscribers, the extensions registered per board class, and each block's edit version.

### Deltas

```ts
interface Delta {
  blocks?:   { add?: Record<BlockId, Block>; mod?: Record<BlockId, { state?: Partial<State>; name?: string }>; rm?: BlockId[] };
  links?:    { add?: Record<LinkId, Link>; mod?: Record<LinkId, Partial<Link>>; rm?: LinkId[]; before?: Record<LinkId, LinkId> };
  stacks?:   { add?: Record<StackId, Stack>; mod?: Record<StackId, Partial<Stack>>; rm?: StackId[] };
  options?:  Record<OptionId, Json>;          // values to set
  fields?:   Record<string, Json>;             // new values of fields a board subclass adds, such as the dock's views
  name?:     string;                           // the board's new name
}
```

The shape is today's payload, with three differences: a block's `mod` takes any of its state args, since every block can be controlled from outside; a link's `mod` changes the link in place and keeps its id; and options, the board's name and the fields a board subclass adds are part of it, so nothing bypasses it. A link's placement among a variadic target's inputs is given by `before`, as today. A field a board subclass adds is set to its new value, so core needs to know nothing of its shape.

### Applying a delta

```ts
store.apply(delta);
```

The store expands a delta, checks it, commits it and tells whoever follows it:

1. The store expands the delta with what follows from it, as today's augment step does: removing a block removes its links and takes it out of its stack ([R/board-server.R#L2072-L2134](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L2072-L2134)). For the fields a board subclass adds, the store calls the `expand` hook that `store.extend()` registered for the board's class, dispatched on its class vector, a pure function from the delta and the board to a delta of those fields, so the dock's method drops a removed block's panels and passes the delta on to its extensions, through which the DAG drops the block's position, and the store runs the hook until nothing changes, as `augment_board_update()` runs today ([#L2357-L2368](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L2357-L2368)).
2. It checks the invariants of [Document model](Board-document-model) on the result, and a failing check rejects the whole delta, so nothing is ever half applied.
3. It makes the new board, sharing what did not change with the old one, and keeps the inverse of the expanded delta for undo.
4. It hands the expanded delta and the new board to whoever follows the board.

Deltas queue and apply in order, so no write replaces another.

### Commands

```ts
interface Command<A extends Json = Json> {
  id: string;                                  // "core.block.remove"
  label: string;                               // for menus and a command palette
  args?: JsonSchema;                           // for forms and the assistant's tools
  shortcut?: string;                           // "Mod+Backspace"
  enabled?(board: Board, args: A): boolean;
  run(board: Board, args: A): Delta | Delta[];  // reads the board, returns deltas, changes nothing itself
}

commands.register(command);
commands.run("core.block.remove", { id: "b" });   // applies, as one undo step
commands.plan("core.block.remove", { id: "b" });  // returns the deltas without applying them
```

Core's commands cover what its plugins and the dock's actions do today: add, remove and rename a block, set its state, append, prepend or insert one on a link, add, change, rename and remove links and stacks, rename the board, and set an option. Packages register their own, such as the dock's view commands and the DAG's copy, cut and paste, and the fields a board subclass adds change only through its package's commands, which anyone may run. The assistant's tools are commands, named by their ids and typed by their `args`, which for a block's state come from its type's arg specs, and its staging is `commands.plan()`, with a commit applying what it planned as one step. A front-end binds the shortcuts, and a block's `submit()` runs the command that sets its state.

### Opening a board

```ts
await store.open(saved);   // replaces the document once R has opened the board
```

Opening a board replaces the document rather than changing it, so it is no delta: it starts a new undo history, and `store.subscribe()` tells followers of it without a delta, so a session package saving drafts sees the new board. A board may come from another app or from older versions of its packages, or define block types the R process has not registered ([Document model](Board-document-model)), so opening one goes through R, within a session as at startup ([Defining a board in R](Defining-a-board-in-R)) and as a file from today's stack does already ([blockr.core#402](https://github.com/BristolMyersSquibb/blockr.core/issues/402)). The `store.open()` call sends the board to R in a request of [Wire protocol](Wire-protocol-between-the-client-and-R), in the form of a saved file ([Serialization](Board-serialization)), and R loads the packages its constructors name, registers the block types it defines where the `load_definitions` option allows it, migrates blocks saved by older versions of their types ([Serialization](Board-serialization)), builds its R board and replies with the board as it rebuilt it and with the registry, and the store replaces its document and its registry with them. R drops what it cannot rebuild and names it in its reply, so the client tells the user what did not open ([Document model](Board-document-model)).

A board whose class differs from the app's opens the way S3 dispatch would treat it:

- A board whose class vector contains the app's class, such as a dock board in a core app, opens as it is, drawn as the app's class, with the fields its subclass adds left untouched.
- A board whose class the app's class extends, such as a core board in a dock app, is converted while R opens it, through the app class's `as_*()` method, as `as_dock_board()` gives a plain board one default view ([blockr.dock R/dock-board.R#L176-L183](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L176-L183)), keeping the board's option values, which `as_dock_board()` drops today.
- Any other board is refused, naming both classes.

Edits made where a subclass's hook is not loaded, such as a dock board's in a core app, can leave its fields referring to removed blocks, so a front-end repairs its own fields against the board's blocks when it opens one. Opening never changes the front-end, so the client redraws from the new document as after any other change, with no page reload, where a restore today is a `session$reload()` ([Board state owned by the client](Board-state-owned-by-the-client)).

### Undo

The deltas of one command are one undo step, which `store.undo()` reverts and `store.redo()` applies again, each for one origin, so that the assistant's steps undo apart from the user's. Undo applies the inverse the store kept, which needs no expansion since it was taken from the expanded delta. Edits of one state arg from one input in quick succession, such as typing into a text field, merge into one step.

### Following the board

```ts
store.board();                                     // the current board, as a signal
store.subscribe((change, board) => { /* ... */ });  // after every commit, with the expanded delta, and every open
```

## Open questions

- How quickly edits must follow each other to merge into one undo step, and whether a block's UI can mark a series of submits as one step instead.
