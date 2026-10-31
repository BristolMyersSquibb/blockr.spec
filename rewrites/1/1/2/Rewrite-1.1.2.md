# Board updates: deltas, commands and undo
Status: settled on 2026-10-28. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how the board changes, core's objects and the front-end's state, with what its extensions carry, alike. It builds on the [board objects proposal](Rewrite-1.1.1) and shapes the store ([blockr.core#432](https://github.com/BristolMyersSquibb/blockr.core/issues/432)), the command registry ([blockr.core#433](https://github.com/BristolMyersSquibb/blockr.core/issues/433)), opening boards in R ([blockr.core#429](https://github.com/BristolMyersSquibb/blockr.core/issues/429)) and locking a board ([blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434)), each an item in the Work list of [Client-owned board state](Rewrite-1.1#work). Which blocks a change makes R evaluate is the evaluation proposal ([Evaluation in the client](Rewrite-1.1.10)), and how the front-end's state is written to a file is the [serialization proposal](Rewrite-1.1.4).

## What must hold

1. Every change to the board, to core's objects or to the front-end's state, is one delta in the `add`, `mod` and `rm` shape of today's `update()`, whoever makes it: a user's input, a menu, a shortcut, an extension or the assistant.
2. A delta reaches everything in the board that refers to what it changes in the same step, so removing a block takes it out of the dock and the DAG at once, and undo brings it back in one step.
3. A delta applies entirely or not at all.
4. Menus, shortcuts, extensions and the assistant's tools all edit through one command registry, to which every package adds its own commands.
5. Anything can follow the board's changes as they happen, such as a session package saving drafts.
6. Opening a board, at startup or later, replaces the board instead of changing it, and leaves the app exactly as opening the same board in a fresh app would, so that nothing of the board it replaces lingers, the front-end included.
7. A front-end or an extension adds state of its own to the board, such as the dock's views, the DAG's positions or blockr.md's document, without changing core or another package, and anything reads and changes that state as it reads and changes core's objects.
8. What a package registers describes itself, a key of the front-end's state by its schema and a command by its description and args, so that another package reads, changes and runs it with no code of its own for that package, as `new_ext_meta()` lets the assistant drive any extension today.

## Today

Every payload goes through one `board_update` reactive value: one observer validates and augments it, another applies it ([R/board-server.R#L300-L446](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L300-L446)). A block's `mod` takes only its `external_ctrl_vars()` and its name, a link's `mod` becomes a removal and an addition ([#L1784-L1805](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L1784-L1805), [#L2165-L2168](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L2165-L2168)), and a second write in one flush replaces the first, so the dock and the assistant merge into it ([blockr.dock R/board-server.R#L370-L384](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/board-server.R#L370-L384)). Several edits bypass `update()` altogether: a block's own inputs, the dock's card sections, board options, the ctrl plugin and the state extensions keep, such as the DAG's positions as the user drags blocks, all of which the dock's serializer reads where they live at save time ([blockr.dock R/utils-serdes.R#L6-L40](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L6-L40), [R/plugin-control.R#L53-L87](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-control.R#L53-L87)). There is no undo anywhere, and a failed apply may leave a payload half applied ([blockr.assistant R/ext-server.R#L1138-L1170](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/ext-server.R#L1138-L1170)).

The dock extends the payload by S3 method with `views` and `extensions`, which its methods of `validate_board_update()`, `augment_board_update()` and `apply_board_update()` check, expand and apply ([blockr.dock R/dock-board.R#L268-L408](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L268-L408)). An extension adds nothing to the payload: it names the variables of its state that others may set, as `external_ctrl`, each of which must be a `reactiveVal` ([R/ext-class.R#L52-L74](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/ext-class.R#L52-L74), [#L231-L250](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/ext-class.R#L231-L250)), and describes them for a model with `new_ext_meta()` ([R/ext-meta.R#L49-L82](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/ext-meta.R#L49-L82)), while the payload's `extensions` only sets those variables, with no `add` or `rm` ([R/ext-delta.R#L1-L85](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/ext-delta.R#L1-L85)). The assistant drives them through its `list_extensions`, `describe_extension` and `modify_extension` tools, with no code for any one extension ([blockr.assistant R/tools-extension.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/tools-extension.R)), which reach the DAG's `positions` and `layout` ([blockr.dag R/ext.R#L37-L89](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/ext.R#L37-L89)) and blockr.md's `content`, one markdown string in which `![caption](blockr://<block_id>)` embeds a block's output ([blockr.md R/md-ext.R#L9-L26](https://github.com/BristolMyersSquibb/blockr.md/blob/32e088884d825813fb7ff0afc7d023df9e70a3b6/R/md-ext.R#L9-L26)). Extensions read each other's state through an environment of active bindings ([blockr.dock R/board-server.R#L158-L172](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/board-server.R#L158-L172)).

The dock's actions are Shiny modules fired through counter-bumped reactive values ([R/action-class.R#L43-L199](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/action-class.R#L43-L199)), core's plugins edit through their own modals, and the assistant has tools of its own for the same edits ([blockr.assistant R/tools-mutation.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/tools-mutation.R)). Only the DAG has shortcuts ([blockr.dag R/g6r.R#L1025-L1046](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/g6r.R#L1025-L1046)).

## Proposal

### The store

The store is the TypeScript object in core's JS API that holds a board and through which every change to it passes. There is one per board, which core creates when it opens the page's board and hands to front-ends, extensions and block modules through `CoreApi` ([Front-ends and extension points](Rewrite-1.1.8)) and the module host ([UI modules in JS](Rewrite-1.1.7)), rather than a global, so that tests, and a page that shows two boards one day, can create more than one. The command registry is an object of its own (below).

```ts
type Origin = string;                                        // "user" unless its maker names another, such as an extension like the assistant, or a peer once a sync add-on exists

type Change =
  | { delta: Delta; origin: Origin }                         // a committed delta, as expanded
  | { opened: Board; dropped: Dropped[] };                   // an opened board, and what R dropped, as in Board objects

interface Store {
  board(): Board;                                            // the current board, whose changes subscribe() announces
  subscribe(fn: (change: Change, board: Board) => void): () => void;   // after every commit and every open

  apply(delta: Delta | Delta[], origin?: Origin): void;      // expands, checks, commits and announces the deltas as one step, or throws what rejected them
  open(saved: string): Promise<Dropped[]>;                   // has R open a saved board, given as the file's text, then replaces the board

  undo(origin?: Origin): void;                               // reverts that origin's last step
  redo(origin?: Origin): void;
  canUndo(origin?: Origin): boolean;
  canRedo(origin?: Origin): boolean;

  register(def: StateKey | Attribute): () => void;          // adds a key of the front-end's state, or an attribute (below)
  registered(): (StateKey | Attribute)[];                    // what is registered, with its schemas
  registerMigration(pkg: string, fn: Migration): () => void; // a package's one migration of its saved state (below)
}
```

Besides the board, the store keeps the undo and redo steps of each origin, its subscribers, what is registered, and the edit id of each block and of each entry or value of the front-end's state. On a locked board it refuses every `store.open()` and every delta the lock does not leave open, such as one that adds a block or changes a locked block's state, which R backs by evaluating only the opening board's blocks ([Wire protocol](Rewrite-1.1.9#locked-boards)).

### Deltas

```ts
interface Delta {
  blocks?:   { add?: Record<BlockId, Block>; mod?: Record<BlockId, { edit?: number; state?: Partial<State>; unset?: string[]; name?: string; attrs?: Record<string, Json> }>; rm?: BlockId[] };
  links?:    { add?: Record<LinkId, Link>; mod?: Record<LinkId, Partial<Link>>; rm?: LinkId[]; before?: Record<LinkId, LinkId> };
  stacks?:   { add?: Record<StackId, Stack>; mod?: Record<StackId, Partial<Stack>>; rm?: StackId[] };
  options?:  Record<OptionId, Json>;          // values to set
  name?:     string;                           // the board's new name
  front_end?: { state?: { path: string[]; change: KeyDelta }[]; attrs?: Record<string, Json> };   // changes to the front-end's state and attributes (below)
}
```

The shape is today's payload, with four differences: a block's `mod` takes any of its state args and attributes, since every block can be controlled from outside, and removes the state args its `unset` names, since an arg without a default starts unset ([Block classes in R](Rewrite-1.1.5#the-block-class)) and a `null` would reach `expr` as `NULL`; it names the block's edit id it was built on, which a command leaves out and the command registry fills in from the board `run()` read, and which only the block's own edits change, so that a delta built on an older board is refused rather than applied over a newer edit; a link's `mod` changes the link in place and keeps its id; and board options, the board's name and the front-end's state and attributes are part of it, so nothing bypasses it. A link's placement among a variadic target's inputs is given by `before`, as today.

### The front-end's state and attributes

Besides core's objects, the board holds its front-end's object: the front-end's id, its state and its attributes ([Board objects](Rewrite-1.1.1#the-board)). The front-end's state is what the front-end adds to the board, such as the dock's views, its grids and which view is active, and what its extensions carry, which the dock nests under `extensions` by each extension's id, as today's dock board writes them ([blockr.dock R/utils-serdes.R#L46-L96](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L46-L96)), such as the DAG's positions, blockr.md's document or the assistant's threads. An attribute is a value that is not state, kept on every block, such as core's `visible`, which says which sections of a block's card show, or on the front-end beside its state, of which core defines none yet.

The module that owns a key of the front-end's state registers it with the store at its path there: the dock registers `views`, and the DAG registers `positions` under `extensions` and its own id, through what the dock offers its extensions ([Client-drawn dock and extensions](Rewrite-1.2)). A key holds a collection, entries keyed by id in insertion order, as the board's blocks are, which a delta changes by `add`, `mod` and `rm`, or a value, as the board's name is, which a delta sets. An attribute is registered under a name, `visible` for core's, which a block's `mod` sets, or the front-end's `attrs` for one of the front-end's, and registering a name that another package registered fails:

```ts
type Entry = Record<string, Json>;                     // a collection's entry is an object

type KeyDelta =
  | { add?: Record<string, Entry>; mod?: Record<string, { edit?: number; set?: Entry; unset?: string[] }>; rm?: string[] }   // a collection's, by entry id
  | { edit?: number; set: Json };                                                                         // a value's

interface StateKey {
  path: string[];                                      // ["extensions", "blockr.dag-dag", "positions"], where it sits in the front-end's state
  kind: "collection" | "value";
  schema: JsonSchema;                                  // an entry's or the value's, with descriptions and examples
  initial?: Json;                                      // what a value holds on a board that has none; a collection starts empty
  expand?(delta: Delta, board: Board): KeyDelta | undefined;   // what follows in this key from a delta (below)
  check?(value: Json, board: Board): string[];         // what the schema cannot say, each failure in a sentence
}

interface Attribute {
  name: string;                                        // "visible"
  on: "block" | "front_end";                           // what carries it
  schema: JsonSchema;
  initial?: Json;                                      // what it holds where nothing set it
}

store.register({                                       // the DAG's positions, which it registers through the dock
  path: ["extensions", "blockr.dag-dag", "positions"],
  kind: "collection",
  schema: position,                                    // { x, y } in canvas pixels, keyed by block id
  expand: (delta, board) => {                          // a removed block's position goes with it
    const positions = board.front_end.state.extensions["blockr.dag-dag"].positions;
    const gone = (delta.blocks?.rm ?? []).filter(id => id in positions);
    return gone.length ? { rm: gone } : undefined;
  },
  check: (positions, board) =>
    Object.keys(positions).filter(id => !(id in board.blocks)).map(id => `There is no block "${id}" to place.`),
});
```

A collection's `mod` gives an entry the keys its `set` names, as a link's `mod` does, and removes those its `unset` names, as a block's `mod` removes state args, and a `mod` or a value's `set` names the edit id of what it changes, as a block's `mod` does. A key belongs to whoever registers it, which alone says what it holds, through its schema and `check`, and what follows in it from a change anywhere in the board, through `expand`. Everything else changes it as it changes core's objects, through core's commands for the front-end's state and through those its owner registers (below), which is external control, and the store applies, checks and undoes the front-end's part of a delta as it does core's, so the DAG's paste adds blocks, their links and their positions in one delta, which one undo takes back. No key is closed to others, as `external_ctrl` closes an extension's other variables today: that opt-in exposed state held in reactive values, while the front-end's state is plain data that its schemas and checks keep valid whoever writes it.

What a front-end or an extension keeps about one of core's objects is an entry in a collection of its own, keyed by the object's id, as the DAG keeps a block's position, so that core's objects hold only core's keys ([Board objects](Rewrite-1.1.1#extending-cores-objects)) and its owner fills in its entry for an object that something else creates, through `expand` and in the same delta. The tldraw SDK lets an app add record types of its own in the same way, which then "live in the store like any other: validated, migrated, persisted, and synced according to the scope you pick" ([tldraw store](https://tldraw.dev/sdk-features/store)).

A key's schema describes it, in the `description` and `examples` keywords, as `new_ext_meta()` describes an extension's state today, and its package ships it as JSON beside its startup module too, so that R writes the key by it ([UI modules in JS](Rewrite-1.1.7#packaging), [Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)).

A package migrates its saved state as a whole, so that it can rename, split and merge its keys, attributes and board options between versions and still read every format it ever wrote, as [Board objects](Rewrite-1.1.1#extending-cores-objects) has it. It registers one migration, which reads everything a file holds for every package and returns, in today's shape, the keys, attributes and board options its package registers:

```ts
type Saved = {
  front_end: { state: Json; attrs: Record<string, Json> };   // the front-end's state and attributes, as the file holds them
  attrs: Record<BlockId, Record<string, Json>>;        // every block's attributes
  options: Record<OptionId, Json>;                     // every board option's value
};

type Migration = (saved: Saved, version: string | null) => Partial<Saved>;   // version: the package's, as the file records it, or null where it records none
```

When a board opens, the store runs the migration of every package whose saved version differs from the one loaded, a package the board holds nothing of included, each on the same saved state, so their order does not matter and a package can take over state an earlier version of another kept, while each writes only the keys, attributes and board options its own package registers. Only then does the store drop every key of the front-end's state, attribute and board option value that no package loaded in the app registered, such as the dock's views on a board opened in a core app, the keys of a package whose startup module failed ([UI modules in JS](Rewrite-1.1.7#startup-modules)), or those that a package's newer version no longer registers and its migration did not take over, and names them with what R dropped, since the app can do nothing with them, so a board saved afterwards is written without them. Every package therefore registers its keys, attributes, board options and migration before the store opens a board, from its startup module, which core initializes before the store opens any board ([UI modules in JS](Rewrite-1.1.7#startup-modules)).

### Applying a delta

```ts
store.apply(delta);
```

The store expands a delta, checks it, commits it and tells whoever follows it:

1. The store expands the delta with what follows from it. Core's part expands as today's augment step does, so removing a block removes its links and takes it out of its stack ([R/board-server.R#L2072-L2134](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L2072-L2134)), and each key of the front-end's state through its `expand`, a pure function from the delta and the board to a delta of that key alone, so the dock drops a removed block's panels and the DAG its position. It runs every `expand` again on what the last round added, until none adds anything, as `augment_board_update()` runs today ([#L2357-L2368](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L2357-L2368)).
2. It checks the invariants of [Board objects](Rewrite-1.1.1) on the result, each key's schema and `check`, and that every block, entry and value a `mod` or `set` changes still has the edit id it names, and a failing check rejects the whole delta, so nothing is ever half applied, with an error that names each failure and its key.
3. It makes the new board, sharing what did not change with the old one, and keeps the inverse of the expanded delta for undo, taken from the board it replaces, so that no package writes undo code: a removed entry comes back whole and in its place, a changed key or value gets its old one, and a state arg or key that the delta set where there was none is unset again.
4. It hands the expanded delta and the new board to whoever follows the board.

Several deltas, as a command's `run()` or a plan returns them, apply in order as one step: each is expanded and checked on the board the one before it left, none is committed unless all pass, and followers are told of each in turn. Each call to `apply()` applies in full before the next, so no write replaces another. A subscriber does not apply a delta while it is told of one, since what follows from a delta is an `expand`, and `apply()` called from one throws. So `apply()` always applies at once, and throws what rejects a delta.

### Commands

```ts
interface Command<A extends Json = Json, P = A> {
  id: string;                                  // "blockr.core-remove_block", named as a registry id is
  label: string;                               // for menus and a command palette
  description?: string;                        // what it does and when to use it
  args?: JsonSchema;                           // for forms and the assistant's tools
  shortcut?: string;                           // "Mod+Backspace"
  enabled?(board: Board, args: A): boolean;
  prepare?(board: Board, args: A): Promise<P>; // what has to wait, such as a layout that elkjs returns as a promise
  run(board: Board, args: P): Delta | Delta[]; // reads the board, returns deltas, changes nothing itself
}

interface Commands {
  register(command: Command): () => void;
  run(id: string, args?: Json, origin?: Origin): Promise<void>;   // applies, as one undo step of that origin
  plan(id: string, args?: Json): Promise<Delta[]>;                // the deltas, built on the current board, not applied
}

await commands.run("blockr.core-remove_block", { id: "b" });      // one step of "user"
await commands.plan("blockr.dag-relayout", { direction: "LR" });
```

Core's commands cover what its plugins and the dock's actions do today: add, remove and rename a block, set or unset its state args, append, prepend or insert one on a link, add, change and remove links, add, change, rename and remove stacks, rename the board, and set a board option, and for every registered key of the front-end's state, add, change and remove its entries or set its value, and set a block's attribute or the front-end's, typed by the schema each registers. Every package registers its own, such as the dock's view commands and the DAG's copy, cut, paste and relayout, and any package runs another's. Every edit runs through a command, whoever makes it, and the command registry applies what the command returns with the origin `commands.run()` is given. A command that has to wait, as the DAG's relayout waits for elkjs, does so in `prepare()`, after which the command registry calls `run()` with what it prepared and the current board, and the store applies the deltas at once, so that a delta is always built on the board it applies to. The assistant's tools are commands too, named by their ids, described by their `description` and typed by their `args`, which for a block's state come from the schema its class's UI ships, described by its arg specs, and for a key of the front-end's state from its schema, and its staging is `commands.plan()`, with a commit passing what it planned to `store.apply()` as one step. A front-end binds the shortcuts, and a block's `submit()` runs the command that sets its state.

### Opening a board

```ts
await store.open(saved);   // replaces the board once R has opened it
```

Opening a board replaces the board the store holds rather than changing it, so it is no delta: it starts a new undo history, and `store.subscribe()` tells followers of it without a delta, so a session package saving drafts sees the new board. A board may come from another app or from older versions of its packages ([Board objects](Rewrite-1.1.1)), so opening one goes through R, within a session as at startup ([Defining a board in R](Rewrite-1.1.3)) and as a file from today's stack does already ([Serialization](Rewrite-1.1.4)). The `store.open()` call sends the board to R in a request of [Wire protocol](Rewrite-1.1.9), as the text of a saved file, which R parses ([Serialization](Rewrite-1.1.4#files)), and R loads the packages it names, migrates blocks saved by older versions of their classes ([Serialization](Rewrite-1.1.4)), all on the board's JSON, building no R board, and replies with the board as it opened it, the front-end's state as it was saved, with the versions of the packages that saved it, and the block registry's entries, and the store replaces its board and its block registry with them, while the board options packages define stay as they are ([Board objects](Rewrite-1.1.1#board-options)). R drops what it cannot rebuild and names it in its reply, so the client tells the user what did not open ([Board objects](Rewrite-1.1.1)).

A board made for another front-end than the page's opens as it is, and core switches the page to the front-end it names, in place, as a fresh app serving the board would draw it ([Front-ends and extension points](Rewrite-1.1.8#switching-front-ends)), where a restore today is a `session$reload()` that builds the page for the restored board's class ([Client-owned board state](Rewrite-1.1)). Nothing in R converts the board, so its board option values stay, while R gives every board option its front-end requires and the file lacks its initial value ([Serialization](Rewrite-1.1.4#board-options)), R drops and names the state of a package that is not installed ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)), and a front-end fills in its own state where the board lacks it, through its package's migration. Otherwise the client redraws from the new board as after any other change, with no page reload.

### Undo

The deltas of one command are one undo step, which `store.undo()` reverts and `store.redo()` applies again, each for one origin, so that the assistant's steps undo apart from the user's. Undo applies the inverse the store kept, which needs no expansion since it was taken from the expanded delta, and covers the front-end's state as it covers core's objects. The inverse names the edit ids the step left, as a `mod` names those it was built on, so undo, and redo likewise, is refused where another origin has since changed the same block, entry or value, rather than setting it back over that change. Steps never merge. An input that changes with every keystroke or pointer move, a block's or an extension's, submits only once the user pauses or lets go, since each submit to a block has R evaluate what is demanded downstream of it and each delta reaches every follower, so a burst of typing is one edit and one step. Edits that must undo together are one delta or one command, such as a `submit()` that sets several args.

### Following the board

```ts
store.board();                                     // the current board
store.board().front_end.state.extensions["blockr.dag-dag"].positions;   // an extension's state, read as core's objects are
store.subscribe((change, board) => { /* ... */ });  // after every commit, with the expanded delta, and every open
```

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's extension mechanism maps onto this proposal: `external_ctrl` and the payload's `extensions` become the extensions' state in the dock's front-end state, which core's commands for that state change; the description, per-variable arg specs, examples and guidance of `new_ext_meta()` become the `description` and `examples` keywords of each key's schema; the `views` the dock adds to the payload become the dock's front-end state and commands; its methods of `validate_board_update()`, `augment_board_update()` and `apply_board_update()` become schemas and checks, `expand`, and the store's own apply; the environment through which extensions read each other's state becomes `store.board().front_end.state`; and the assistant's `list_extensions`, `describe_extension` and `modify_extension` give way to the command registry, where core's commands for the front-end's state stand beside each package's own.

The store merges what each `expand` returns into the delta and stops once a round adds nothing new, so an `expand` may return what the delta holds already, and after a fixed number of rounds it rejects the delta, naming the keys that kept adding. An `expand` gets the board before the delta and a `check` the board after it. Once a command's `prepare()` resolves, the command registry checks `enabled()` again before it calls `run()`, since the board may have changed while the command waited, and opening a board drops every command still in its `prepare()`. An `expand` leaves the edit ids out, as a command does, since it builds on the board the delta applies to. Within a collection's part of a delta, `rm` applies before `add`, as core's parts do, since a delta may reuse an id it drops, and `mod` applies last. Every check runs on every delta, so a key's `check` looks up its entries rather than scanning the board. The inverse of a removal records each entry's place in its collection, so that undo puts it back where it was.

The precedents for expanding in rounds: a tldraw after handler, such as one that deletes a frame when its last child goes, runs "when the outermost store operation completes, so changes made inside them belong to the same transaction and the same undo step" ([tldraw side effects](https://tldraw.dev/sdk-features/side-effects)), and ProseMirror calls a plugin's `appendTransaction` "again with the new state and new transactions" whenever another plugin appends one ([plugin.ts#L34-L40](https://github.com/ProseMirror/prosemirror-state/blob/ffad5d9450a0b93438be53a801deee1a223a81bf/src/plugin.ts#L34-L40)). VS Code has an extension describe a tool it offers a model in the terms a command uses here, a `modelDescription` and an `inputSchema` ([Language model tools](https://code.visualstudio.com/api/extension-guides/ai/tools)).

</details>
