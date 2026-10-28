# Board updates: deltas, commands and undo
Status: settled on 2026-10-28. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how the board changes, core's objects and the fields that packages such as the dock and its extensions add to it alike. It builds on the [board objects proposal](Rewrite-1.1.1) and shapes the store and the command registry, an item in the Work list of [Client-owned board state](Rewrite-1.1#work). Which blocks a change makes R evaluate is the evaluation proposal ([Evaluation in the client](Rewrite-1.1.10)), and how a field is written to a file is the [serialization proposal](Rewrite-1.1.4).

## What must hold

1. Every change to the board, to core's objects or to the state a package adds, is one delta in the `add`, `mod` and `rm` shape of today's `update()`, whoever makes it: a user's input, a menu, a shortcut, an extension or the assistant.
2. A delta reaches everything in the board that refers to what it changes in the same step, so removing a block takes it out of the dock and the DAG at once, and undo brings it back in one step.
3. A delta applies entirely or not at all.
4. Menus, shortcuts, extensions and the assistant's tools all edit through one command registry, to which every package adds its own commands.
5. Anything can follow the board's changes as they happen, such as a session package saving drafts.
6. Opening a board, at startup or later, replaces the board instead of changing it, and ends in the same place either way.
7. A package adds state of its own to the board, such as the DAG's positions or blockr.md's document, without changing core, the front-end or another package, and every package reads and changes that state as it reads and changes core's objects.
8. What a package registers describes itself, a field by its schema and a command by its description and args, so that another package reads, changes and runs it with no code of its own for that package, as `new_ext_meta()` lets the assistant drive any extension today.

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
  board(): Board;                                            // the current board, as a signal
  subscribe(fn: (change: Change, board: Board) => void): () => void;   // after every commit and every open

  apply(delta: Delta | Delta[], origin?: Origin): void;      // expands, checks, commits and announces the deltas as one step, or throws what rejected them
  open(saved: Json): Promise<Dropped[]>;                     // has R open a saved board, then replaces the board

  undo(origin?: Origin): void;                               // reverts that origin's last step
  redo(origin?: Origin): void;
  canUndo(origin?: Origin): boolean;
  canRedo(origin?: Origin): boolean;

  register(field: Field): () => void;                        // adds a package's field to the board (below)
  fields(): Field[];                                         // the registered fields, with their schemas
}
```

Besides the board, the store keeps the undo and redo steps of each origin, its subscribers, the registered fields, and the edit version of each block and of each field's entries or value. On a locked board it refuses every `store.open()` and every delta the lock does not leave open, such as one that adds a block, which R backs by evaluating only the opening board's blocks ([Wire protocol](Rewrite-1.1.9#locked-boards)).

### Deltas

```ts
interface Delta {
  blocks?:   { add?: Record<BlockId, Block>; mod?: Record<BlockId, { edit?: number; state?: Partial<State>; name?: string }>; rm?: BlockId[] };
  links?:    { add?: Record<LinkId, Link>; mod?: Record<LinkId, Partial<Link>>; rm?: LinkId[]; before?: Record<LinkId, LinkId> };
  stacks?:   { add?: Record<StackId, Stack>; mod?: Record<StackId, Partial<Stack>>; rm?: StackId[] };
  options?:  Record<OptionId, Json>;          // values to set
  name?:     string;                           // the board's new name
  fields?:   Record<FieldId, FieldDelta>;      // changes to the fields packages add (below)
}
```

The shape is today's payload, with four differences: a block's `mod` takes any of its state args, since every block can be controlled from outside; it names the block's edit version it was built on, which a command leaves out and the command registry fills in from the board `run()` read, and which counts only the block's own edits, so that a delta built on an older board is refused rather than applied over a newer edit; a link's `mod` changes the link in place and keeps its id; and options, the board's name and the fields packages add are part of it, so nothing bypasses it. A link's placement among a variadic target's inputs is given by `before`, as today.

### Fields

A field is state that a package adds to the board, such as the dock's views, the DAG's positions, blockr.md's document or the assistant's threads, and registers with the store when its module loads. The board holds each field under its id in `fields` ([Board objects](Rewrite-1.1.1#extending-cores-objects)), and the id is named as a registry id is, `{pkg}-{name}`, so that two packages that do not know of each other cannot clash. A field is a collection, entries keyed by id in insertion order, as the board's blocks are, which a delta changes by `add`, `mod` and `rm`, or a value, as the board's name is, which a delta sets:

```ts
type Entry = Record<string, Json>;                     // a collection's entry is an object

type FieldDelta =
  | { add?: Record<string, Entry>; mod?: Record<string, { edit?: number; set: Entry }>; rm?: string[] }   // a collection's, by entry id
  | { edit?: number; set: Json };                                                                         // a value's

interface Field {
  id: FieldId;                                         // "blockr.dag-positions"
  kind: "collection" | "value";
  schema: JsonSchema;                                  // an entry's or the value's, with descriptions and examples
  initial?: Json;                                      // what a value holds on a board that has none; a collection starts empty
  expand?(delta: Delta, board: Board): FieldDelta | undefined;   // what follows in this field from a delta (below)
  check?(value: Json, board: Board): string[];         // what the schema cannot say, each failure in a sentence
  migrate?(saved: Json, version: string): Json;        // a value an older version of the package saved, in today's shape
  repair?(value: Json, board: Board): Json;            // the value fitted to a board edited where the field was not registered
}

store.register({
  id: "blockr.dag-positions",
  kind: "collection",
  schema: position,                                    // { x, y } in canvas pixels, keyed by block id
  expand: (delta, board) => {                          // a removed block's position goes with it
    const gone = (delta.blocks?.rm ?? []).filter(id => id in board.fields["blockr.dag-positions"]);
    return gone.length ? { rm: gone } : undefined;
  },
  check: (positions, board) =>
    Object.keys(positions).filter(id => !(id in board.blocks)).map(id => `There is no block "${id}" to place.`),
});
```

A field's `mod` gives an entry the keys its `set` names, as a link's `mod` does, and a `mod` or a value's `set` names the edit version of what it changes, as a block's `mod` does. A field belongs to the package that registers it, which alone says what it holds, through its schema and `check`, and what follows in it from a change anywhere in the board, through `expand`. Every other package changes it as it changes core's objects, through core's commands for fields and through those its own package registers (below), and the store applies, checks and undoes a field's part of a delta as it does core's, so the DAG's paste adds blocks, their links and their positions in one delta, which one undo takes back. No field is closed to other packages, as `external_ctrl` closes an extension's other variables today: that opt-in exposed state held in reactive values, while a field is plain data that its schema and `check` keep valid whoever writes it.

What a package keeps about one of core's objects is an entry in a field of its own, keyed by the object's id, as the DAG keeps a block's position, so that core's objects hold only core's keys ([Board objects](Rewrite-1.1.1#extending-cores-objects)) and a package fills in its entry for an object another package creates, through `expand` and in the same delta. The tldraw SDK lets an app add record types of its own in the same way, which then "live in the store like any other: validated, migrated, persisted, and synced according to the scope you pick" ([tldraw store](https://tldraw.dev/sdk-features/store)).

A field's schema describes it, in the `description` and `examples` keywords, as `new_ext_meta()` describes an extension's state today. The store keeps a field that no loaded package registered as it is, with the version of the package that saved it, such as the dock's views on a dock board in a core app, and rejects a delta to it, since nothing could check one. When a field is registered, and whenever a board opens, the store brings the field from the version that saved it to today's shape with `migrate`, so a package reads every format it ever wrote in one place, as [Board objects](Rewrite-1.1.1#extending-cores-objects) has it, and then fits it to the board with `repair`, since the board may have been edited where the field's package was not loaded, which can leave the dock's views naming removed blocks.

### Applying a delta

```ts
store.apply(delta);
```

The store expands a delta, checks it, commits it and tells whoever follows it:

1. The store expands the delta with what follows from it. Core's part expands as today's augment step does, so removing a block removes its links and takes it out of its stack ([R/board-server.R#L2072-L2134](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L2072-L2134)), and each field's part through the field's `expand`, a pure function from the delta and the board to a delta of that field alone, so the dock drops a removed block's panels and the DAG its position. It runs every `expand` again on what the last round added, until none adds anything, as `augment_board_update()` runs today ([#L2357-L2368](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L2357-L2368)).
2. It checks the invariants of [Board objects](Rewrite-1.1.1) on the result, each field's schema and `check`, and that every block, entry and value a `mod` or `set` changes is still at the edit version it names, and a failing check rejects the whole delta, so nothing is ever half applied, with an error that names each failure and its field.
3. It makes the new board, sharing what did not change with the old one, and keeps the inverse of the expanded delta for undo, taken from the board it replaces, so that no package writes undo code: a removed entry comes back whole and in its place, and a changed key or value gets its old one.
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

Core's commands cover what its plugins and the dock's actions do today: add, remove and rename a block, set its state, append, prepend or insert one on a link, add, change, rename and remove links and stacks, rename the board, and set an option, and for every registered field, add, change and remove its entries or set its value, typed by the field's schema. Every package registers its own, such as the dock's view commands and the DAG's copy, cut, paste and relayout, and any package runs another's. Every edit runs through a command, whoever makes it, and the command registry applies what the command returns with the origin `commands.run()` is given. A command that has to wait, as the DAG's relayout waits for elkjs, does so in `prepare()`, after which the command registry calls `run()` with what it prepared and the current board, and the store applies the deltas at once, so that a delta is always built on the board it applies to. The assistant's tools are commands too, named by their ids, described by their `description` and typed by their `args`, which for a block's state come from its type's arg specs and for a field from its schema, and its staging is `commands.plan()`, with a commit passing what it planned to `store.apply()` as one step. A front-end binds the shortcuts, and a block's `submit()` runs the command that sets its state.

### Opening a board

```ts
await store.open(saved);   // replaces the board once R has opened it
```

Opening a board replaces the board the store holds rather than changing it, so it is no delta: it starts a new undo history, and `store.subscribe()` tells followers of it without a delta, so a session package saving drafts sees the new board. A board may come from another app or from older versions of its packages, or define block types the R process has not registered ([Board objects](Rewrite-1.1.1)), so opening one goes through R, within a session as at startup ([Defining a board in R](Rewrite-1.1.3)) and as a file from today's stack does already ([Serialization](Rewrite-1.1.4)). The `store.open()` call sends the board to R in a request of [Wire protocol](Rewrite-1.1.9), in the form of a saved file ([Serialization](Rewrite-1.1.4)), and R loads the packages it names, registers the block types it defines where the `load_definitions` option allows it, migrates blocks saved by older versions of their types ([Serialization](Rewrite-1.1.4)), builds its R board and replies with the board as it rebuilt it, each package's fields as they were saved, with the version that saved them, the block registry's entries and the board's options, and the store replaces its board, its block registry and its options with them. R drops what it cannot rebuild and names it in its reply, so the client tells the user what did not open ([Board objects](Rewrite-1.1.1)).

A board whose class differs from the app's opens the way S3 dispatch would treat it:

- A board whose class vector contains the app's class, such as a dock board in a core app, opens as it is, drawn by the app's front-end, with the dock's fields kept as they are (above).
- A board whose class the app's class extends, such as a core board in a dock app, is converted while R opens it, through the app class's `as_*()` method, as `as_dock_board()` gives a plain board one default view ([blockr.dock R/dock-board.R#L176-L183](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L176-L183)), keeping the board's option values, which `as_dock_board()` drops today.
- Any other board is refused, naming both classes.

Where edits made without a field's package left the field naming removed blocks, the store repairs it as the board opens (above). Opening never changes the front-end, so the client redraws from the new board as after any other change, with no page reload, where a restore today is a `session$reload()` ([Client-owned board state](Rewrite-1.1)).

### Undo

The deltas of one command are one undo step, which `store.undo()` reverts and `store.redo()` applies again, each for one origin, so that the assistant's steps undo apart from the user's. Undo applies the inverse the store kept, which needs no expansion since it was taken from the expanded delta, and covers the fields packages add as it covers core's objects. The inverse names the edit versions the step left, as a `mod` names those it was built on, so undo, and redo likewise, is refused where another origin has since changed the same block, entry or value, rather than setting it back over that change. Steps never merge. An input that changes with every keystroke or pointer move, a block's or an extension's, submits only once the user pauses or lets go, since each submit to a block has R evaluate everything downstream of it and each delta reaches every follower, so a burst of typing is one edit and one step. Edits that must undo together are one delta or one command, such as a `submit()` that sets several args.

### Following the board

```ts
store.board();                                     // the current board, as a signal
store.board().fields["blockr.dag-positions"];       // a package's field, read as core's objects are
store.subscribe((change, board) => { /* ... */ });  // after every commit, with the expanded delta, and every open
```

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's extension mechanism maps onto this proposal: `external_ctrl` and the payload's `extensions` become fields, which core's commands for fields change; the description, per-variable arg specs, examples and guidance of `new_ext_meta()` become the `description` and `examples` keywords of each field's schema; the `views` the dock adds to the payload become the dock's fields and commands; its methods of `validate_board_update()`, `augment_board_update()` and `apply_board_update()` become schemas and checks, `expand`, and the store's own apply; the environment through which extensions read each other's state becomes `store.board().fields`; and the assistant's `list_extensions`, `describe_extension` and `modify_extension` give way to the command registry, where core's commands for fields stand beside each package's own.

The store merges what each `expand` returns into the delta and stops once a round adds nothing new, so an `expand` may return what the delta holds already, and after a fixed number of rounds it rejects the delta, naming the fields that kept adding. An `expand` gets the board before the delta and a `check` the board after it. Once a command's `prepare()` resolves, the command registry checks `enabled()` again before it calls `run()`, since the board may have changed while the command waited, and opening a board drops every command still in its `prepare()`. An `expand` leaves the edit versions out, as a command does, since it builds on the board the delta applies to. Within a collection's part of a delta, `rm` applies before `add`, as core's parts do, since a delta may reuse an id it drops, and `mod` applies last. Every check runs on every delta, so a field's `check` looks up its entries rather than scanning the board. The inverse of a removal records each entry's place in its collection, so that undo puts it back where it was.

The precedents for expanding in rounds: a tldraw after handler, such as one that deletes a frame when its last child goes, runs "when the outermost store operation completes, so changes made inside them belong to the same transaction and the same undo step" ([tldraw side effects](https://tldraw.dev/sdk-features/side-effects)), and ProseMirror calls a plugin's `appendTransaction` "again with the new state and new transactions" whenever another plugin appends one ([plugin.ts#L34-L40](https://github.com/ProseMirror/prosemirror-state/blob/ffad5d9450a0b93438be53a801deee1a223a81bf/src/plugin.ts#L34-L40)). VS Code has an extension describe a tool it offers a model in the terms a command uses here, a `modelDescription` and an `inputSchema` ([Language model tools](https://code.visualstudio.com/api/extension-guides/ai/tools)).

</details>
