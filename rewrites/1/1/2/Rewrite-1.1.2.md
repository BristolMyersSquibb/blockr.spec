# Board updates: deltas, commands and undo
Status: settled on 2026-10-28. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how the board changes, core's objects and the properties that its board class adds, with what its front-end's extensions carry, alike. It builds on the [board objects proposal](Rewrite-1.1.1) and shapes the store ([blockr.core#432](https://github.com/BristolMyersSquibb/blockr.core/issues/432)), the command registry ([blockr.core#433](https://github.com/BristolMyersSquibb/blockr.core/issues/433)), loading the packages that a board names in R ([blockr.core#429](https://github.com/BristolMyersSquibb/blockr.core/issues/429)) and locking a board ([blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434)), each an item in the Work list of [Client-owned board state](Rewrite-1.1#work). Which blocks a change makes R evaluate is the evaluation proposal ([Evaluation in the client](Rewrite-1.1.10)), and how a board class's properties are written to a file is the [serialization proposal](Rewrite-1.1.4).

## What must hold

1. Every change to the board, to core's objects or to the properties that its board class adds, is one delta, whoever makes it: a user's input, a menu, a shortcut, an extension or the assistant. Core's objects change in the `add`, `mod` and `rm` shape of today's `update()`, and a board class's properties by patches at nested paths.
2. A delta reaches everything in the board that refers to what it changes in the same step, so removing a block takes it out of the dock and the DAG at once, and undo brings it back in one step.
3. A delta applies entirely or not at all.
4. Menus, shortcuts, extensions and the assistant's tools all edit through one command registry, to which every package adds its own commands.
5. Anything can follow the board's changes as they happen, such as a session package saving drafts.
6. Opening a board, at startup or later, replaces the board instead of changing it, and leaves the app exactly as opening the same board in a fresh app would, so that nothing of the board it replaces lingers, the front-end included.
7. A board class adds properties of its own to the board, such as the dock's views, and keeps there what its front-end's extensions carry, such as the DAG's positions or blockr.md's document, without changing core or another package. Anything reads those properties as it reads core's objects, and changes them through the commands their owner registers.
8. What a package defines describes itself, a board class's property by its schema and a command by its description and args, so that another package reads the property and runs the command with no code of its own for that package, as `new_ext_meta()` lets the assistant drive any extension today.

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
  | { opened: Board; dropped: Dropped[] };                   // an opened board, and what the store dropped as it opened it, as in Board objects

interface Store {
  board(): Board;                                            // the current board, whose changes subscribe() announces
  subscribe(fn: (change: Change, board: Board) => void): () => void;   // after every commit and every open

  apply(delta: Delta | Delta[], origin?: Origin): void;      // expands, checks, commits and announces the deltas as one step, or throws what rejected them
  open(saved: string | HelloReply): Promise<Dropped[]>;      // opens a saved board, given as the file's text, having R load the packages it names, or the opening board in R's reply to hello, then replaces the board

  undo(origin?: Origin): void;                               // takes that origin's last step back, as a new edit (below)
  redo(origin?: Origin): void;
  canUndo(origin?: Origin): boolean;
  canRedo(origin?: Origin): boolean;

  register(def: BoardClass | Attribute): () => void;        // adds a board class, with the properties it adds, or a block attribute (below)
  registered(): (BoardClass | Attribute)[];                  // what is registered, with its schemas
  registerMigration(pkg: string, fn: Migration): () => void; // a package's one migration of its saved state (below)
}
```

Besides the board, the store keeps the undo and redo steps of each origin, its subscribers, what is registered, and the edit id of each block and of each property that a board class adds: the number of the step that last changed it, from one count of the steps, the opening of a board, an undo and a redo included, so that no number names two versions of one object. It holds no board until it opens one and refuses every delta until then, so that nothing builds on a board that no opening made. Core creates it with `createStore({ client, loaded })`: `client` is what core's client sends R its requests through, which gives each request its id over the transport and resolves with R's reply to it ([blockr.core#455](https://github.com/BristolMyersSquibb/blockr.core/pull/455)), and `loaded(reply, classes)` is what the store awaits once R has replied to an opening and before it migrates or drops anything, given the board's `class`, where core initializes the startup modules the opening brings, which define their board classes, and switches the page to the front-end of the first class in `classes` that a loaded package defines. The store then builds the board as that class ([Switching front-ends](Rewrite-1.1.8#switching-front-ends)). On a locked board it refuses every `store.open()` of a file's text and every delta the lock does not leave open, such as one that adds a block or changes a locked block's state, which R backs by evaluating only the opening board's blocks ([Wire protocol](Rewrite-1.1.9#locked-boards)).

### Deltas

```ts
interface Delta {
  blocks?:   { add?: Record<BlockId, Block>; mod?: Record<BlockId, { edit?: number; state?: Partial<State>; unset?: string[]; name?: string; attrs?: Values }>; rm?: BlockId[] };
  links?:    { add?: Record<LinkId, Link>; mod?: Record<LinkId, Partial<Link>>; rm?: LinkId[]; before?: Record<LinkId, LinkId> };
  stacks?:   { add?: Record<StackId, Stack>; mod?: Record<StackId, Partial<Stack>>; rm?: StackId[] };
  options?:  Values<OptionId>;                // board option values to set and to remove
  name?:     string;                           // the board's new name
  patches?:  Patch[];                         // changes inside the properties that the board's class adds (below)
}

interface Values<K extends string = string> {  // values by name to set, and names whose values to remove
  set?: Record<K, Json>;
  unset?: K[];
}
```

The shape is today's payload, with four differences: a block's `mod` takes any of its state args and attributes, since every block can be controlled from outside, and removes the state args its `unset` names, since an arg without a default starts unset ([Block classes in R](Rewrite-1.1.5#the-block-class)) and a `null` would reach `expr` as `NULL`; it names the block's edit id it was built on, which a command leaves out and the command registry fills in from the board `run()` read, and which only the block's own edits change, so that a delta built on an older board is refused rather than applied over a newer edit; a link's `mod` changes the link in place and keeps its id; and board options, the board's name and the properties that its class adds are part of it, so nothing bypasses it. A link's placement among a variadic target's inputs is given by `before`, as today. Board option values and attributes are set and removed as a collection entry's fields are, by `set` and `unset`, so that undo removes what its step set where there was none in a delta that survives JSON, as a delta has to where it travels between peers or through the assistant's plans.

### Board classes and attributes

Besides core's objects, a board holds the properties that its board class adds ([Board objects](Rewrite-1.1.1#the-board)), such as a dock board's views, its grids and which view is active, and its `extensions`, which hold what the dock's extensions carry by each extension's id, as today's dock board writes them ([blockr.dock R/utils-serdes.R#L46-L96](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L46-L96)), such as the DAG's positions, blockr.md's document or the assistant's threads. An attribute is a value that is not state, kept on every block, such as core's `visible`, which says which sections of a block's card show.

A package defines each board class it ships from its startup module, under the class's R name. The definition names the class's parent, its front-end, the board options it requires ([Board objects](Rewrite-1.1.1#board-options)) and the properties it adds, each with a schema and a default, and gives one function that keeps those properties consistent with the rest of the board (below), while what sits inside a property is the class's own design. The store registers nothing inside a property: it checks a property's whole value against its schema after every change, keeps what a change replaced for undo, and saves the property with the board. An attribute is registered under a name, `visible` for core's, which a block's `mod` sets, and registering a name that another package registered fails. With illustrative names:

```ts
type Patch = { op: "add" | "remove" | "replace"; path: string; value?: Json };   // JSON Patch's, at a path from the board's top, as "/views/main/panels/1"

interface BoardClass {
  class: string;                                       // "dock_board", the R class it defines
  parent: string;                                      // "board"
  frontEnd: string;                                    // "blockr.dock-dock", the module that draws its boards
  options?: OptionId[];                                // the board options it requires (Board objects)
  properties: Record<string, { schema: JsonSchema; default: Json }>;   // what it adds beside core's properties
  update?(delta: Delta, board: Board): Patch[];        // patches to its own properties that follow from a change (below)
}

interface Attribute {
  name: string;                                        // "visible"
  schema: JsonSchema;
  initial?: Json;                                      // what it holds where nothing set it
}

store.register({                                       // the dock's, from its startup module
  class: "dock_board",
  parent: "board",
  frontEnd: "blockr.dock-dock",
  properties: {
    views: { schema: views, default: {} },
    extensions: { schema: extensions, default: {} },
  },
  update: (delta, board) => dropPanels(delta.blocks?.rm ?? [], board),   // a removed block's panels go with it
});
```

A change inside a property is a patch at a path from the board's top, as `{ "op": "remove", "path": "/views/main/panels/1" }` removes one panel, which the store applies without knowing the property's structure, while core's objects change by core's `add`, `mod` and `rm`. The store checks the patched property against its schema, keeps the inverse patches for undo, and tells followers of the patches, so the DAG's paste adds blocks, their links and their positions in one delta, which one undo takes back. The package that defines a board class registers the commands for the operations on its properties, such as `blockr.dock-add_view`, and an extension of its front-end does so for its own state, such as `blockr.dag-change_position`, each checking its args and returning patches. Everything else, menus, shortcuts and the assistant, changes the properties through those commands, which is external control (below). No property is closed to others, as `external_ctrl` closes an extension's other variables today: its owner's commands are open to anyone, and the property's schema keeps it valid whoever runs them.

What a package keeps about one of core's objects is an entry of its own property, keyed by the object's id, as the DAG keeps a block's position, so that core's objects hold only core's properties ([Board objects](Rewrite-1.1.1#extending-cores-objects)). A change that someone else makes can leave such an entry stale, as removing a block leaves its panel in a view. So each board class gives core one function, `update` above, which the store calls with every change it applies and which returns patches for the class's own properties, applied in the same step ([Applying a delta](#applying-a-delta)). The function reads only the change and the board: it calls no R and reads nothing on screen, so that every peer that applies a change computes the same patches. It mints an id only into the step it is part of, while one that repairs a board after two changes merged mints none. Its patches belong to the step that caused them, which is what is undone, saved and, one day, sent to a peer. ProseMirror's `appendTransaction` lets a plugin add to another's transaction in the same way ([ProseMirror](https://prosemirror.net/docs/ref/#state.PluginSpec.appendTransaction)), and tldraw's side effects run inside the change that triggered them ([StoreSideEffects](https://tldraw.dev/reference/store/StoreSideEffects)).

A property's schema describes it, in the `description` and `examples` keywords, as `new_ext_meta()` describes an extension's state today, and its package ships it as JSON beside its startup module too, so that R writes the property by it ([UI modules in JS](Rewrite-1.1.7#packaging), [Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)).

A package migrates what it saved as a whole, so that it can rename, split and merge the parts of its properties between versions and still read every format it ever wrote, as [Board objects](Rewrite-1.1.1#extending-cores-objects) has it. It registers one migration, which rewrites what a file holds, the properties that board classes add and every block's state, with its own package's part in today's shape: the properties its board classes add and the states of the blocks of its block classes, which no migration in R migrates any more ([Serialization](Rewrite-1.1.4#migrations)). Attributes and board option values are not migrated: one that its schema refuses is dropped as the board opens, so that it reads as its initial value or default.

```ts
type Saved = {
  properties: Record<string, Json>;                    // the properties that board classes add, as the file holds them
  blocks: Record<BlockId, { registry_id: RegistryId; state: Record<string, Json> }>;   // every block's class and state
};

type Migration = (saved: Saved, version: string | null) => Saved;   // version: the package's, as the file records it, or null where it records none
```

When a board opens, the store runs the migration of every package whose saved version differs from the one loaded, a package the board holds nothing of included, one after another in the order in which their packages' startup modules register them, which puts a package's after those of the packages it imports ([UI modules in JS](Rewrite-1.1.7#startup-modules)). Each takes the file as the migration before it left it and returns it, changing only its own package's part, which only its package enforces, and the board opens with the properties and block states the last one returns, so that what a migration leaves out is gone, as a property that a package renamed is. A migration changes nothing on a board in today's shape, so that a board saved and opened again comes back as it was, and what a board reads where nothing set a value comes from what packages define, a property's `default`, an attribute's `initial` and a board option's `default`, rather than from a migration, which only a file's opening runs. Only then does the store drop every property that the class it builds the board as defines neither itself nor through its parents, such as the dock's views on a board opened in a core app, and every attribute and board option value that no package loaded in the app registered, such as those of a package whose startup module failed ([UI modules in JS](Rewrite-1.1.7#startup-modules)), without naming them, so a board saved afterwards is written without them. Every package therefore defines its board classes and registers its attributes, board options and migration before the store opens a board, from its startup module, which core initializes before the store opens any board ([UI modules in JS](Rewrite-1.1.7#startup-modules)).

### Applying a delta

```ts
store.apply(delta);
```

The store expands a delta, checks it, commits it and tells whoever follows it:

1. The store expands the delta with what follows from it. Core's part expands as today's augment step does, so removing a block removes its links and takes it out of its stack ([R/board-server.R#L2072-L2134](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L2072-L2134)), and the board's class through its `update`, a pure function from the delta and the board to patches of that class's own properties, so the dock drops a removed block's panels. It runs `update` again on what the last round added, until it adds nothing, as `augment_board_update()` runs today ([#L2357-L2368](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L2357-L2368)).
2. It checks the invariants of [Board objects](Rewrite-1.1.1) on the result, the schema of each property a patch changed, and that every block and property a `mod` or a patch changes still has the edit id it names, and a failing check rejects the whole delta, so nothing is ever half applied, with an error that names each failure and its property.
3. It makes the new board, sharing what did not change with the old one, and keeps the inverse of the expanded delta for undo, taken from the board it replaces, so that no package writes undo code: a removed block, link or stack comes back whole and in its place, a patched property gets its old value, and a state arg, field, attribute or board option value that the delta set where there was none is unset again.
4. It hands the expanded delta and the new board to whoever follows the board.

Several deltas, as a command's `run()` or a plan returns them, apply in order as one step: each is expanded and checked on the board the one before it left, while the edit ids they name are checked against those the board had as the step started, since `run()` and `plan()` build all of a step's deltas on one board, none is committed unless all pass, and followers are told of each in turn. Each call to `apply()` applies in full before the next, so no write replaces another. A subscriber does not apply a delta while it is told of one, since what follows from a delta is an `expand`, and `apply()` called from one throws. So `apply()` always applies at once, and throws what rejects a delta.

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

Core's commands cover what its plugins and the dock's actions do today: add, remove and rename a block, set or unset its state args, append, prepend or insert one on a link, add, change and remove links, add, change, rename and remove stacks, rename the board, and set a board option, and set a block's attribute, typed by the schema it registers. Every package registers its own, such as the dock's view commands, among them `blockr.dock-add_view`, and the DAG's copy, cut, paste, relayout and `blockr.dag-change_position`, and anything else changes a board class's properties through those of its owner, while any package runs another's. Every edit runs through a command, whoever makes it, and the command registry applies what the command returns with the origin `commands.run()` is given. A command that has to wait, as the DAG's relayout waits for elkjs, does so in `prepare()`, after which the command registry calls `run()` with what it prepared and the current board, and the store applies the deltas at once, so that a delta is always built on the board it applies to. The assistant's tools are commands too, named by their ids, described by their `description` and typed by their `args`, which for a block's state come from the schema its class's UI ships, described by its arg specs, and for a board class's property from the args its owner's commands declare, and its staging is `commands.plan()`, with a commit passing what it planned to `store.apply()` as one step. A front-end binds the shortcuts, and a block's `submit()` runs the command that sets its state.

### Opening a board

```ts
await store.open(saved);   // replaces the board once R has loaded the packages it names
await store.open(hello);   // the opening board in R's reply to hello, for which R has loaded them already
```

Opening a board replaces the board the store holds rather than changing it, so it is no delta: it starts a new undo history, and `store.subscribe()` tells followers of it without a delta, so a session package saving drafts sees the new board. A board may come from another app or from older versions of its packages ([Board objects](Rewrite-1.1.1)), and the store opens it itself, as it opens the board R sends at startup ([Defining a board in R](Rewrite-1.1.3#the-opening-board)), needing nothing of R but that the packages the board names are loaded, with their block classes registered, and the block registry's entries for them. The `store.open()` call parses the saved file's text and sends R an `open` naming the packages its `packages` lists ([Wire protocol](Rewrite-1.1.9#opening-a-board)), while given R's reply to `hello` it sends none, since R has loaded the opening board's packages and sent their block registry's entries with the reply: a reply's `file` opens as that file, and its `board`, which an app script built, keyed and with each id it lacks minted ([Board objects](Rewrite-1.1.1#ids)), opens as the saved file it would be, recording the versions R loaded, so that every board goes the same way from there and ends as the same board, whether an app script defined it, R passed on the file `serve()` was given, the client opened a file or a user built it up with deltas. Once R replies, the store replaces its block registry with R's entries, awaits what core runs for the packages the opening loaded (above), runs the migration of every package whose saved version differs from the one R loaded (above), drops what the app cannot rebuild, naming the blocks it drops and the class it builds the board as where it skips one ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)), and replaces its board, while the board options packages define stay as they are. A block whose class the block registry lacks is dropped as a delta removes it, through core's expansion and the board class's `update`, so that what the class keeps about it goes with its links and its places in stacks. A file of today's stack is converted to a saved file outside core first ([Serialization](Rewrite-1.1.4#files)).

A board that the store builds as a class whose front-end is another than the page's opens as it is, and core switches the page to that front-end, in place, as a fresh app serving the board would draw it ([Front-ends and extension points](Rewrite-1.1.8#switching-front-ends)), where a restore today is a `session$reload()` that builds the page for the restored board's class ([Client-owned board state](Rewrite-1.1)). Nothing converts the board, so its board option values stay, while the store drops the properties of a class whose package is not installed ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)). The properties of the board's class that it lacks take their defaults, and so do the board options its classes require, as far as the board lacks them ([Board objects](Rewrite-1.1.1#board-options)). Otherwise the client redraws from the new board as after any other change, with no page reload.

### Undo

The deltas of one command are one undo step, which `store.undo()` takes back and `store.redo()` applies again, each for one origin, so that the assistant's steps undo apart from the user's. Undo works as it does in Figma, Google Slides and tldraw, as a new edit on the board as it is: it applies the inverse the store kept where what the step changed is still there, over what another origin changed since, the last writer winning, does nothing where it is gone, and is expanded, checked and announced as any delta, covering the properties of the board's class as it covers core's objects. It keeps what it replaced for redo, so that undoing and then redoing leaves the board as it was, whatever another origin changed in between, which is Figma's principle ([How Figma's multiplayer technology works](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/)). Undo and redo are steps of their own, so edit ids only grow and refuse a delta built on an older board, such as the assistant's plans, but no undo. Steps never merge. An input that changes with every keystroke or pointer move, a block's or an extension's, submits only once the user pauses or lets go, since each submit to a block has R evaluate what is demanded downstream of it and each delta reaches every follower, so a burst of typing is one edit and one step. Edits that must undo together are one delta or one command, such as a `submit()` that sets several args.

### Following the board

```ts
store.board();                                     // the current board
store.board().extensions["blockr.dag-dag"].positions;   // an extension's state, in a dock board's property, read as core's objects are
store.subscribe((change, board) => { /* ... */ });  // after every commit, with the expanded delta, and every open
```

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's extension mechanism maps onto this proposal: `external_ctrl` and the payload's `extensions` become the extensions' state in the dock board's `extensions`, which each extension's commands change; the description, per-variable arg specs, examples and guidance of `new_ext_meta()` become the `description` and `examples` keywords of each property's schema, and the descriptions and args of the commands that change it; the `views` the dock adds to the payload become the dock board's properties and commands; its methods of `validate_board_update()`, `augment_board_update()` and `apply_board_update()` become the properties' schemas, the dock board class's `update` and the store's own apply; the environment through which extensions read each other's state becomes `store.board().extensions`; and the assistant's `list_extensions`, `describe_extension` and `modify_extension` give way to the command registry, where each package's commands stand.

The store merges the patches that an `update` returns into the delta and stops once a round adds nothing new, so an `update` may return what the delta holds already, and after a fixed number of rounds it rejects the delta, naming the class that kept adding. What an `update` returns never overrides what the delta given to the store says, so that an undo that puts back a property's old value puts back that value, and not one that an `update` makes up for a new object. An `update` gets the board before the delta, so that it sees what the delta removes. Once a command's `prepare()` resolves, the command registry checks `enabled()` again before it calls `run()`, since the board may have changed while the command waited, and opening a board drops every command still in its `prepare()`. An `update` leaves the edit ids out, as a command does, since it builds on the board the delta applies to. Within a collection's part of a delta, `rm` applies before `add`, as core's parts do, since a delta may reuse an id it drops, and `mod` applies last, while patches apply in their order, after core's parts. The store checks a property's schema only where a patch changed the property. The inverse of a removal records each entry's place in its collection, so that undo puts it back where it was.

The precedents for expanding in rounds: a tldraw after handler, such as one that deletes a frame when its last child goes, runs "when the outermost store operation completes, so changes made inside them belong to the same transaction and the same undo step" ([tldraw side effects](https://tldraw.dev/sdk-features/side-effects)), and ProseMirror calls a plugin's `appendTransaction` "again with the new state and new transactions" whenever another plugin appends one ([plugin.ts#L34-L40](https://github.com/ProseMirror/prosemirror-state/blob/ffad5d9450a0b93438be53a801deee1a223a81bf/src/plugin.ts#L34-L40)). VS Code has an extension describe a tool it offers a model in the terms a command uses here, a `modelDescription` and an `inputSchema` ([Language model tools](https://code.visualstudio.com/api/extension-guides/ai/tools)).

</details>
