# Board updates: deltas, commands and undo
Status: settled on 2026-10-28. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how the board changes, core's objects and the state of its plugins alike.
It builds on the [board objects proposal](Rewrite-1.1.1) and shapes the store ([blockr.core#432](https://github.com/BristolMyersSquibb/blockr.core/issues/432)), the command registry ([blockr.core#433](https://github.com/BristolMyersSquibb/blockr.core/issues/433)), reading a JSON board in R ([blockr.core#429](https://github.com/BristolMyersSquibb/blockr.core/issues/429)), locking a board ([blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434)), starting core again as a board opens ([blockr.core#497](https://github.com/BristolMyersSquibb/blockr.core/issues/497)), leaving board option values out of undo and redo ([blockr.core#503](https://github.com/BristolMyersSquibb/blockr.core/issues/503)), plugins in the store ([blockr.core#504](https://github.com/BristolMyersSquibb/blockr.core/issues/504)), refusing a board that holds a value its schema refuses ([blockr.core#509](https://github.com/BristolMyersSquibb/blockr.core/issues/509)) and keeping an `update`'s append to an array that the delta appends to as well ([blockr.core#513](https://github.com/BristolMyersSquibb/blockr.core/issues/513)), each an item in the Work list of [Client-owned board state](Rewrite-1.1#work).
It shapes one undo history for the steps of every origin too ([blockr.core#608](https://github.com/BristolMyersSquibb/blockr.core/issues/608)).
Which blocks a change makes R evaluate is the evaluation proposal ([Evaluation in the client](Rewrite-1.1.10)), how a plugin's state is written to a file is the [serialization proposal](Rewrite-1.1.4), and what a plugin is and which plugins a board holds are [Plugins](Rewrite-1.1.12)'s.

## What must hold

1. Every change to the board, to core's objects or to its plugins, is one delta, whoever makes it: a user's input, a menu, a shortcut or a plugin, the assistant among them.
   Core's objects change in the `add`, `mod` and `rm` shape of today's `update()`, and its plugins by patches at nested paths.
2. A delta reaches everything in the board that refers to what it changes in the same step, so removing a block takes it out of the dock and the DAG at once, and undo brings it back in one step.
3. A delta applies entirely or not at all.
4. Menus, shortcuts, plugins and the assistant's tools all edit through one command registry, to which every package adds its own commands.
5. Anything can follow the board's changes as they happen, such as a session package saving drafts.
6. Opening a board, at startup or later, replaces the board instead of changing it, and leaves the app exactly as opening the same board in a fresh app would, so that nothing of the board it replaces lingers, the frontend included.
7. A plugin keeps its state in the board, such as the dock's views, the DAG's positions or blockr.md's document, without changing core or another package.
   Anything reads that state as it reads core's objects, and changes it through the commands its owner registers or, on a board that is not locked, core's command for a plugin's state.
8. What a package defines describes itself, a plugin's state by its class's schema and a command by its description and args, so that another package reads the state and runs the command with no code of its own for that package, as `new_ext_meta()` lets the assistant drive any extension today.

## Today

Every payload goes through one `board_update` reactive value: one observer validates and augments it, another applies it ([R/board-server.R#L300-L446](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L300-L446)).
A block's `mod` takes only its `external_ctrl_vars()` and its name, a link's `mod` becomes a removal and an addition ([#L1784-L1805](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L1784-L1805), [#L2165-L2168](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L2165-L2168)), and a second write in one flush replaces the first, so the dock and the assistant merge into it ([blockr.dock R/board-server.R#L370-L384](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/board-server.R#L370-L384)).
Several edits bypass `update()` altogether: a block's own inputs, the dock's card sections, board options, the ctrl plugin and the state extensions keep, such as the DAG's positions as the user drags blocks, all of which the dock's serializer reads where they live at save time ([blockr.dock R/utils-serdes.R#L6-L40](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L6-L40), [R/plugin-control.R#L53-L87](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-control.R#L53-L87)).
There is no undo anywhere, and a failed apply may leave a payload half applied ([blockr.assistant R/ext-server.R#L1138-L1170](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/ext-server.R#L1138-L1170)).

The dock extends the payload by S3 method with `views` and `extensions`, which its methods of `validate_board_update()`, `augment_board_update()` and `apply_board_update()` check, expand and apply ([blockr.dock R/dock-board.R#L268-L408](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L268-L408)).
An extension adds nothing to the payload: it names the variables of its state that others may set, as `external_ctrl`, each of which must be a `reactiveVal` ([R/ext-class.R#L52-L74](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/ext-class.R#L52-L74), [#L231-L250](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/ext-class.R#L231-L250)), and describes them for a model with `new_ext_meta()` ([R/ext-meta.R#L49-L82](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/ext-meta.R#L49-L82)), while the payload's `extensions` only sets those variables, with no `add` or `rm` ([R/ext-delta.R#L1-L85](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/ext-delta.R#L1-L85)).
The assistant drives them through its `list_extensions`, `describe_extension` and `modify_extension` tools, with no code for any one extension ([blockr.assistant R/tools-extension.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/tools-extension.R)), which reach the DAG's `positions` and `layout` ([blockr.dag R/ext.R#L37-L89](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/ext.R#L37-L89)) and blockr.md's `content`, one markdown string in which `![caption](blockr://<block_id>)` embeds a block's output ([blockr.md R/md-ext.R#L9-L26](https://github.com/BristolMyersSquibb/blockr.md/blob/32e088884d825813fb7ff0afc7d023df9e70a3b6/R/md-ext.R#L9-L26)).
Extensions read each other's state through an environment of active bindings ([blockr.dock R/board-server.R#L158-L172](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/board-server.R#L158-L172)).

The dock's actions are Shiny modules fired through counter-bumped reactive values ([R/action-class.R#L43-L199](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/action-class.R#L43-L199)), core's plugins edit through their own modals, and the assistant has tools of its own for the same edits ([blockr.assistant R/tools-mutation.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/tools-mutation.R)).
Only the DAG has shortcuts ([blockr.dag R/g6r.R#L1025-L1046](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/g6r.R#L1025-L1046)).

## Proposal

### The store

The store is the TypeScript object in core's JS API that holds a board and through which every change to it passes.
There is one per board, which core creates when it opens the page's board and hands to plugins, a frontend among them, and block modules through `CoreApi` ([Drawing the board](Rewrite-1.1.8)) and the module host ([UI modules in JS](Rewrite-1.1.7)), rather than a global, so that tests, and a page that shows two boards one day, can create more than one.
The command registry is an object of its own (below).

```ts
type Origin = string;                                        // "user" unless its maker names another, such as a plugin like the assistant, or a peer once a package syncs boards between people

type Change =
  | { delta: Delta; origin: Origin }                         // a committed delta, as expanded
  | { opened: Board; dropped: Dropped[] };                   // an opened board, and what the store dropped as it opened it, as in Board objects

interface Store {
  board(): Board;                                            // the current board, whose changes subscribe() announces
  hasBoard(): boolean;                                       // whether the store holds a board, which it does once it has opened one
  locked(block: BlockId): boolean;                           // whether a lock fixes the block's state: the board lock is on and its locked is not false (below)
  subscribe(fn: (change: Change, board: Board) => void): () => void;   // after every commit and every open

  apply(delta: Delta | Delta[], origin?: Origin, opts?: { undo?: false }): void;   // expands, checks, commits and announces the deltas as one step, or throws what rejected them, as no undo step with undo: false (Undo)
  open(given: string | HelloReply): Promise<Dropped[]>;      // opens the opening board in R's reply to hello, or a JSON board given as its text, with that reply's block registry and plugins, then replaces the board
  check(text: string): Promise<Dropped[]>;                   // what opening a JSON board's text would drop, or the error that would refuse it, holding nothing
  jsonBoard(): JsonBoard;                                    // the board as a JSON board holds it, to save (Serialization)
  save(): string;                                            // the text of jsonBoard(), as a file holds it, which open() opens (Serialization)

  undo(origin?: Origin): void;                               // takes back the history's last step, or that origin's last step, as a new edit (below)
  redo(): void;                                              // applies again the step that the last undo took back
  canUndo(origin?: Origin): boolean;
  canRedo(): boolean;

  readonly plugins: Plugins;                                 // the plugin classes that core registers from the modules that the reply names (Plugins)
  readonly options: Options;                                 // the board options that core registers from the modules that the reply names (Board options and blockr options)
  blockRegistry(): BlockRegistry;                            // the block registry's entries of the reply to hello that it opened its board with
  packages(): Record<string, string>;                        // the versions of the packages in that reply, which jsonBoard() records
  editId(of: { block: BlockId } | { plugin: PluginClassId }): number | undefined;   // the edit id of a block or a plugin, which the command registry fills into the deltas of a command (below)
}
```

Besides the board, the store keeps one history of the undo and redo steps of every origin, its subscribers, what is registered, and the edit id of each block and of each plugin: the number of the step that last changed it, from one count of the steps, the opening of a board, an undo and a redo included, so that no number names two versions of one object.
It holds no board until it opens one and refuses every delta until then, so that nothing builds on a board that no opening made.
Core creates a store for each board it opens, with `createStore({ hello, loaded, signal })`, given the reply to `hello` and a signal that ends the store as another board opens, and the store sends R nothing, since it opens its board with what the reply to `hello` holds, while a board that another replaces goes with its store, as core starts again ([Drawing the board](Rewrite-1.1.8#opening-a-board)).
The `loaded(reply)` callback is what the store awaits before it opens its board, given the reply to `hello`, while core registers the plugin classes and board options whose modules the reply names before it calls `open()` ([blockr.core#499](https://github.com/BristolMyersSquibb/blockr.core/pull/499), [blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)), so that the store opens the board with the class of every plugin of the app registered ([Plugins](Rewrite-1.1.12#a-plugin)).
Core imports the app's frontend once the store has opened the board, since which of the app's plugins run, its frontend among them, is settled only once the store has opened the board with those whose classes the app's packages register ([Drawing the board](Rewrite-1.1.8#starting-the-page)).
Under the load lock it refuses every `store.open()` of a file's text, and under the board lock every delta but one that changes the state of a block that the board lock leaves open, a board option's value or what sits inside a plugin's state, which the plugin locks itself ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)), and `locked()` says which blocks it fixes, since a block whose `locked` is `null` follows the board lock.
So it refuses a delta that adds a block or changes a locked block's state, which R backs by refusing an evaluation that rebinds a block's data inputs or gives a locked block another state ([Locked boards and the properties of blocks](Rewrite-1.1.11#what-r-refuses)).

### Deltas

```ts
interface Delta {
  blocks?:   { add?: Record<BlockId, Block>; mod?: Record<BlockId, { edit?: number; state?: Partial<State>; unset?: string[]; name?: string; locked?: boolean | null }>; rm?: BlockId[] };
  links?:    { add?: Record<LinkId, Link>; mod?: Record<LinkId, Partial<Link>>; rm?: LinkId[]; before?: Record<LinkId, LinkId> };
  stacks?:   { add?: Record<StackId, Stack>; mod?: Record<StackId, Partial<Stack>>; rm?: StackId[] };
  options?:  Values<OptionId>;                // board option values to set and to remove
  name?:     string;                           // the board's new name
  patches?:  Patch[];                         // changes inside the state of the board's plugins (below)
}

interface Values<K extends string = string> {  // values by name to set, and names whose values to remove
  set?: Record<K, Json>;
  unset?: K[];
}
```

The shape is today's payload, with four differences: a block's `mod` takes any of its state args, since every block can be controlled from outside, and its `locked` ([Locked boards and the properties of blocks](Rewrite-1.1.11#block-locks)), and removes the state args its `unset` names, since an arg without a default starts unset ([Block classes in R](Rewrite-1.1.5#the-block-class)) and a `null` would reach `expr` as `NULL`; it names the block's edit id it was built on, which a command leaves out and the command registry fills in from the board `run()` read, and which only the block's own edits change, so that a delta built on an older board is refused rather than applied over a newer edit, as a patch names the edit id of the plugin it changes; a link's `mod` changes the link in place and keeps its id; and board options, the board's name and its plugins are part of it, so nothing bypasses it.
A link's placement among a variadic target's inputs is given by `before`, as today.
Board option values are set and removed as a collection entry's properties are, by `set` and `unset`, so that a delta removes a value in a way that survives JSON, as a delta has to where it travels between peers or through the assistant's plans.

### Plugins

Besides core's objects, a board holds the state of its plugins in `plugins`, each under its class's id, for each plugin whose class has state ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)), such as the dock's views and which view is active, the DAG's positions, blockr.md's document or the assistant's threads, which today's dock board writes in properties of its own and, by each extension's id, in its `extensions` ([blockr.dock R/utils-serdes.R#L46-L96](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L46-L96)).

Core registers the class of each of the app's plugins under the class's id, from the module that the class's package lists for it ([Plugins](Rewrite-1.1.12#a-plugin), [blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)).
Of the class's members, the store reads the schema and the default of its plugins' state, one function that keeps that state consistent with the rest of the board, and one that migrates it (below), while what sits inside a plugin's state is the class's own design.
Registering a class checks that no registered class has its id already and that its state's default fits its schema.
The store registers nothing inside a plugin's state: it checks the state's whole value against its class's schema after every change, keeps what a change replaced for undo, and saves the state with the board.
With illustrative names:

```ts
type Patch = { op: "add" | "remove" | "replace"; path: string; value?: Json; edit?: number };   // JSON Patch's, at a path from the board's root, as "/plugins/blockr.dock-dock_plugin/views/main/grid/children/0/panels/1", with the edit id of the plugin it changes

export default {                                       // the dock's, from dock.js, the module that blockr.dock lists for blockr.dock-dock_plugin
  state: { schema: dockState, default: defaultLayout },
  update: (delta, board, plugin) => dropPanels(delta.blocks?.rm ?? [], board, plugin),   // a removed block's panels go with it
  frontend: dockFrontend,
  commands: [addView],                                 // blockr.dock-add_view, among others
};
```

A change inside a plugin's state is a patch at a path under it, as `{ "op": "remove", "path": "/plugins/blockr.dock-dock_plugin/views/main/grid/children/0/panels/1" }` removes one panel, which the store applies without knowing the state's structure, while core's objects change by core's `add`, `mod` and `rm`.
A patch changes the state of the board's plugins and never one of core's objects: a patch at or below `/plugins/{id}` changes a plugin's state, while the store refuses one that adds or removes what the board holds for a plugin, as an `add` or a `remove` at `/plugins/blockr.dag-dag_plugin` would, since the app sets which plugins run and their classes name them ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)).
The store checks the patched state against its class's schema, keeps the inverse patches for undo, and tells followers of the patches, so the DAG's paste adds blocks, their links and their positions in one delta, which one undo takes back.
A plugin class holds the commands for the operations on its plugins' state, which core registers with the class, such as `blockr.dock-add_view` and `blockr.dag-change_position`, each checking its args and returning patches, while core's `blockr.core-set_plugin_state` sets any part of any plugin's state ([Plugins](Rewrite-1.1.12#a-plugins-state)).
Everything else, menus, shortcuts and the assistant, changes a plugin's state through those commands, which is external control (below).
No part of a plugin's state is closed to others, as `external_ctrl` closes an extension's other variables today: the class's commands are open to anyone, and so is core's command on a board that is not locked, and the class's schema keeps the state valid whoever runs them.

What a package keeps about one of core's objects is an entry in its plugin's state, keyed by the object's id, as the DAG keeps a block's position, so that core's objects hold only core's properties ([Board objects](Rewrite-1.1.1#extending-cores-objects)).
A change that someone else makes can leave such an entry stale, as removing a block leaves its panel in a view.
So a plugin class gives core one function, `update` above, which the store calls for each of the class's plugins with every change it applies and which returns patches for that plugin's state, applied in the same step ([Applying a delta](#applying-a-delta)).
The store refuses a patch that an `update` returns outside the state of the plugin it was called for.
The function reads only the change and the board: it calls no R and reads nothing on screen, so that every peer that applies a change computes the same patches.
It mints an id only into the step it is part of, while one that repairs a board after two changes merged mints none.
Its patches belong to the step that caused them, which is what is undone, saved and, one day, sent to a peer.
ProseMirror's `appendTransaction` lets a plugin add to another's transaction in the same way ([ProseMirror](https://prosemirror.net/docs/ref/#state.PluginSpec.appendTransaction)), and tldraw's side effects run inside the change that triggered them ([StoreSideEffects](https://tldraw.dev/reference/store/StoreSideEffects)).

The schema of a plugin class's state describes it, in the `description` and `examples` keywords, as `new_ext_meta()` describes an extension's state today, and its package ships it as JSON beside the class's module, so that R writes the state by it ([UI modules in JS](Rewrite-1.1.7#packaging), [Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)).

What a JSON board holds migrates by the version of each shape that it records, never by a package's version ([Serialization](Rewrite-1.1.4#migrations)), so that a class can rename, split and merge the parts of its plugins' state or its blocks' state between versions and still read every shape it ever wrote, as [Board objects](Rewrite-1.1.1#extending-cores-objects) has it.
A plugin class migrates its plugins' state in its `migrate`, given the state of one plugin as the JSON board holds it and the version of the class that the board records, and returns it in the class's latest shape.
A block class's UI module exports the migration of the class's state as `migrate`, since the module owns the state's shape, and core imports it before the store opens or checks a board that holds an older state of the class, though the module loads for its UI only once core mounts a block, while no migration runs in R any more ([blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)).
A board option migrates its value in its definition's `migrate`, given the value and the version of its shape that the JSON board records ([Serialization](Rewrite-1.1.4#board-options)).

```ts
type Migration = (state: Record<string, Json>, version: number) => Record<string, Json>;   // version: the class's, as the block records it

export const migrate: Migration = (state, version) =>   // from the UI module of blockr.dplyr-filter_block
  version < 2 ? { ...state, conditions: [state.condition] } : state;
```

When a board opens, the store first drops the state of each plugin of a class that the app does not run, or that no package that the app uses registers, such as the dock's on a board opened in a core app ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)).
It names each such plugin with its class's package, and reads nothing more of its state.
Then it runs the `migrate` of each remaining plugin's class whose version the board records below the one R gives, the migration of each block's class where the block records a version below its class's, and the `migrate` of each board option whose value the board records at a version below the one R gives, each given what it migrates frozen, and the board opens with what they return, so that what a migration leaves out is gone, as a part of a plugin's state that its class renamed is.
A version above the one R gives refuses the board, since no migration converts back, while a class that the board records no version of keeps what the board holds, since its writer knew no version of it.
A plugin's state that the store dropped refuses nothing, whatever version of its class the board records, since the store drops a plugin's state for its id or its class, never for its version.
So a board saved with the DAG's plugin at version 2 opens without the DAG in an app without blockr.dag, where the DAG's class has no method of `plugin_version()` and so is at version 1 ([Plugins](Rewrite-1.1.12#a-plugin)).
What a board reads where nothing set a value comes from what packages define, the `default` of a plugin class's state and a board option's `default`, rather than from a migration, which only a JSON board's opening runs.
Only then does the store drop every block whose class the block registry lacks, since dropping a block calls the `update` of each plugin's class, which reads the plugin's state in the latest shape of its class.
It also drops then every board option value that no package that the app uses registers, such as that of a board option whose module failed to load ([UI modules in JS](Rewrite-1.1.7#modules-of-plugin-classes-and-board-options)), naming each by its id, so a board saved afterwards is written without them ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)).
Then it gives each of the app's plugins whose class has state, and whose state the board does not hold, its class's default state ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)).
Core therefore registers every plugin class and board option, and imports the migrations of the block classes whose older states the board holds, before the store opens a board, from the modules that the reply names ([UI modules in JS](Rewrite-1.1.7#modules-of-plugin-classes-and-board-options)).

### Applying a delta

```ts
store.apply(delta);
```

The store expands a delta, checks it, commits it and tells whoever follows it:

1. The store expands the delta with what follows from it.
   Core's part expands as today's augment step does, so removing a block removes its links and takes it out of its stack ([R/board-server.R#L2072-L2134](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L2072-L2134)), and each plugin's class through its `update`, a pure function from the delta, the board and the plugin's class's id to patches of that plugin's state, so the dock drops a removed block's panels.
   It runs `update` again on what the last round added, until it adds nothing, as `augment_board_update()` runs today ([#L2357-L2368](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L2357-L2368)).
2. It checks the invariants of [Board objects](Rewrite-1.1.1) on the result, the schema of each plugin's state that a patch changed, and that every block and plugin a `mod` or a patch changes still has the edit id it names, and a failing check rejects the whole delta, so nothing is ever half applied, with an error that names each failure and what it concerns.
3. It makes the new board, sharing what did not change with the old one, and keeps the inverse of the expanded delta for undo, taken from the board it replaces, so that no package writes undo code: a removed block, link, stack or plugin comes back whole and in its place, a patched plugin's state gets its old value, and a state arg or property that the delta set where there was none is unset again, while the inverse holds no board option values ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)).
4. It hands the expanded delta and the new board to whoever follows the board.

Several deltas, as a command's `run()` or a plan returns them, apply in order as one step: each is expanded and checked on the board the one before it left, while the edit ids they name are checked against those the board had as the step started, since the command registry fills them in from that board, for each command of a list too (Commands), none is committed unless all pass, and followers are told of each in turn.
Each call to `apply()` applies in full before the next, so no write replaces another.
A subscriber does not apply a delta while it is told of one, since what follows from a delta is what a plugin class's `update` returns, and `apply()` called from one throws.
So `apply()` always applies at once, and throws what rejects a delta.

### Commands

```ts
interface Command<A extends Json = Json, P = A> {
  id: string;                                  // "blockr.core-remove_block", named as a registry id is
  label: string;                               // for menus and a command palette
  description?: string;                        // what it does and when to use it
  args?: JsonSchema;                           // for forms and the assistant's tools
  shortcut?: string;                           // "Mod+Backspace"
  enabled?(board: Board, args: A): boolean;
  undo?: false;                                // its deltas take no undo step, as switching the dock's views takes none (Undo)
  prepare?(board: Board, args: A): Promise<P>; // what has to wait, such as a layout that elkjs returns as a promise
  run(board: Board, args: P): Delta | Delta[]; // reads the board, returns deltas, changes nothing itself
}

interface Commands {
  register(command: Command): () => void;
  registered(): Record<string, Command>;                         // the registered commands by id, for menus, a command palette and the assistant's tools
  enabled(id: string, args?: Json): boolean;                     // whether the command applies to the current board with these args
  run(id: string, args?: Json, origin?: Origin): Promise<void>;   // applies, as one undo step of that origin unless the command has undo: false
  run(list: { id: string; args?: Json }[], origin?: Origin): Promise<void>;   // applies the commands in order as one step of that origin, each planned on the board that those before it leave
  plan(id: string, args?: Json): Promise<Delta[]>;                // the deltas, built on the current board, not applied
  plan(list: { id: string; args?: Json }[]): Promise<Delta[]>;    // the deltas of the commands in order, each built on the board that those before it leave, not applied
}

await commands.run("blockr.core-remove_block", { id: "b" });      // one step of "user"
await commands.plan("blockr.dag-relayout", { direction: "LR" });
await commands.run([                                              // one step of "assistant": a block, its link and its panel
  { id: "blockr.core-add_block", args: { registry_id: "blockr.dplyr-filter_block", id: "f" } },
  { id: "blockr.core-add_link", args: { from: "data", to: "f" } },
  { id: "blockr.dock-add_panel", args: { view: "main", panel: { block: "f" }, near: { block: "data" }, side: "right" } },
], "assistant");
```

Core's commands cover what its plugins of today and the dock's actions do: add, remove and rename a block, set or unset its state args, append, prepend or insert one on a link, add, change and remove links, add, change, rename and remove stacks, rename the board, set a board option, and set a block's `locked`, as `blockr.core-set_block_lock` does, and they set a plugin's state ([Plugins](Rewrite-1.1.12#a-plugins-state)).
Changing a stack sets its blocks, its colour or both, and clears its colour with `null` ([Board objects](Rewrite-1.1.1#stacks)).
Every package registers its own, such as the dock's view commands, among them `blockr.dock-add_view`, and the DAG's copy, cut, paste, relayout and `blockr.dag-change_position`, and anything else changes a plugin's state through those of its owner or core's `blockr.core-set_plugin_state`, while any package runs another's.
Every edit runs through a command, whoever makes it, and the command registry applies what the command returns with the origin `commands.run()` is given.
A command that has to wait, as the DAG's relayout waits for elkjs, does so in `prepare()`, after which the command registry calls `run()` with what it prepared and the current board, and the store applies the deltas at once, so that a delta is always built on the board it applies to.
The assistant edits through commands as well, each named by its id, and its edit tool runs a list of them as one step of its origin ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).
Its tools give the model each command's `description` and `args`, the schema of a block class's state, which the class's UI ships and its arg specs describe, and the schema of a plugin class's state.
A list of commands runs as one step: the command registry plans each command on the board that the deltas of those before it leave, which the store works out without committing them, so that a command finds the block that an earlier one adds, as `blockr.core-add_link` needs both of its blocks on the board.
Then the store applies every delta of the list as one step of the origin given, which takes one undo step unless every command of the list has `undo: false`, or applies none where one command is refused, and the command registry names that command.
A frontend binds the shortcuts, and a block's `submit()` runs the command that sets its state.

### Opening a board

```ts
await store.open(text);    // a JSON board's text, as a file holds it
await store.open(hello);   // the opening board in R's reply to hello
```

Opening a board replaces the board rather than changing it, so it is no delta.
A store opens one board, which core has it open as core starts, and a later `store.open()` starts core again with the board given, in a new store ([Drawing the board](Rewrite-1.1.8#opening-a-board)), so that the undo history and everything else of the board before goes with the store that held it.
The store tells its followers of the board it opens without a delta, through `store.subscribe()`, while a session package saving drafts subscribes from its plugin's `start()`, which runs once each board has opened, and reads that board there ([blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)).
A board may come from another app or from older versions of its classes ([Board objects](Rewrite-1.1.1)), and the store opens it itself, as a JSON board, as it opens the board R sends at startup ([Defining a board in R](Rewrite-1.1.3#the-opening-board)), needing nothing of R but what the reply to `hello` holds: the block registry's entries, the app's plugins, each with its class's version and module, the board options, each with its version and module, the opening board, the locks and the versions of the packages that the app uses ([Wire protocol](Rewrite-1.1.9#opening-a-board)).
The `store.open()` call parses a JSON board's text and opens it with what the last reply to `hello` held, sending R nothing.
Given that reply, it opens the reply's `board`: the JSON board that an app script built, which R wrote with every id ([Board objects](Rewrite-1.1.1#ids)), or the one that `serve()` was given, which R passed on as it is.
So every board goes the same way and ends as the same board, whether an app script defined it, R passed on the file `serve()` was given, the client opened a file or a user built it up with deltas.
The store refuses a JSON board whose format is above any it reads, a file of today's stack, which has none, a version of a shape above the one its class gives, and a value that its schema refuses once migrated, whether a block's state, a plugin's state or a board option's value, while R's `serve()` refuses an app with no frontend, two frontends or two storage plugins ([Plugins](Rewrite-1.1.12#the-frontend)).
It names what it refuses, every value that a schema refuses among it, and leaves the page as it was, so that another board can be opened ([Drawing the board](Rewrite-1.1.8#opening-a-board)), while an opening board that it refuses, such as one that an app script built with a value of the wrong shape, leaves the page with the errors alone, for the deployment to fix.
It awaits what core runs before it opens a board, drops the state of the plugins that the app does not hold, migrates what the board holds in an older shape, drops the blocks and the board option values that the app cannot rebuild (above), gives the app's other plugins that keep state their classes' default ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)), and holds the board.
It names the blocks it dropped and the plugins whose state it dropped, and the packages that the JSON board lists and the app does not offer ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)).
A block whose class the block registry lacks is dropped as a delta removes it, through core's expansion and the `update` of each plugin's class, so that what a plugin keeps about it goes with its links and its places in stacks.
A file of today's stack is converted to a JSON board outside core first ([Serialization](Rewrite-1.1.4#files)).

A board opens with the app's plugins, each with the state that the board holds for it, and core draws it with the app's frontend, as a fresh app serving the board would ([Drawing the board](Rewrite-1.1.8#opening-a-board)), where a restore today is a `session$reload()` that builds the page for the restored board's class ([Client-owned board state](Rewrite-1.1)).
Nothing converts the board, so its board option values stay, but for those that no package of the app registers, and the store drops the state of the plugins that the app does not hold ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)).
Core resolves the defaults of the board options that the classes of its plugins require, where the board holds no value, and keeps them beside the board rather than in it, as [Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds) has it.

### Undo

The deltas of one command are one undo step, and the store keeps the steps of every origin in one history, in the order the board took them.
So `store.undo()` takes back the history's last step, whoever took it, and `store.redo()` applies again the step that the last undo took back, which is what the user expects of the frontend's Undo and Redo once the assistant edits beside them.
Given an origin, `store.undo()` takes back that origin's last step instead, past the steps of others after it, as the assistant's tool `undo_edit` does ([The assistant's tools](Rewrite-1.4.2#the-tools)).
An undo is a change of the origin that asks for it, the user's where none is given, so that the assistant hears the user's undo of its edit as the user's ([The system prompt](Rewrite-1.4.5#what-changed-under-the-model)).
A new step empties the redo steps, whoever takes it.
How a peer's steps undo, once a package syncs boards between people, is that package's to settle, and nothing here rules out keeping them apart.
Undo works as it does in Figma, Google Slides and tldraw, as a new edit on the board as it is: it applies the inverse the store kept where what the step changed is still there, over what another origin changed since, the last writer winning, does nothing where it is gone, and is expanded, checked and announced as any delta, covering the state of its plugins as it covers core's objects.
It leaves board option values alone, since a board option never changes what the board computes, so a step that sets only those is no undo step ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)).
For the same reason, a command whose definition has `undo: false` takes no undo step, as the dock's commands that switch views, show another tab and open or collapse a rail do, since they change only what the user looks at ([The dock's state](Rewrite-1.2.1#commands)), and as the assistant's commands do, since they change only its threads and their picks of the model ([The assistant's state](Rewrite-1.4.3#commands)).
The store applies, announces and saves the deltas of such a command as any others, keeps no inverse of them, and leaves the redo steps as they were.
It keeps what it replaced for redo, so that undoing and then redoing leaves the board as it was, which is Figma's principle ([How Figma's multiplayer technology works](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/)).
Undo and redo are steps of their own, so edit ids only grow and refuse a delta built on an older board, such as the assistant's plans, but no undo.
Undo leaves out a patch whose path no longer leads to what it changes, as it leaves out a change of a block that is gone, and a patch at an array's index changes whatever the array holds there by then.
A path holds no place among an object's members, so the store keeps the member that followed a removed one, as it keeps an entry's place in core's collections, and undo adds the member back before that one, or last where it is gone.
A repair that needs a class's knowledge, such as moving a panel whose group another origin removed, is the plugin class's, in its `update`, which the store calls on every change, undos included.
Steps never merge.
An input that changes with every keystroke or pointer move, a block's or a plugin's, submits only once the user pauses or lets go, since each submit to a block has R evaluate what is demanded downstream of it and each delta reaches every follower, so a burst of typing is one edit and one step.
Edits that must undo together are one delta or one command, such as a `submit()` that sets several args.

### Following the board

```ts
store.board();                                     // the current board
store.board().plugins.dag.state.positions;          // a plugin's state, read as core's objects are
store.subscribe((change, board) => { /* ... */ });  // after every commit, with the expanded delta, and every open
```

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's extension mechanism maps onto this proposal: `external_ctrl` and the payload's `extensions` become the state of the plugin that takes each extension's place, which core's `blockr.core-set_plugin_state` and the plugin's own commands change; the description, per-variable arg specs, examples and guidance of `new_ext_meta()` become the `description` and `examples` keywords of the schema of each plugin class's state, and the descriptions and args of the commands that change it; the `views` the dock adds to the payload become the dock plugin's state and commands; its methods of `validate_board_update()`, `augment_board_update()` and `apply_board_update()` become the schema of the dock plugin's state, its class's `update` and the store's own apply; the environment through which extensions read each other's state becomes `store.board().plugins`; and the assistant's `list_extensions`, `describe_extension` and `modify_extension` give way to the command registry, where each package's commands stand, core's for any plugin's state among them.

The store merges the patches that an `update` returns into the delta and stops once a round adds nothing new, so an `update` may return what the delta holds already, and after a fixed number of rounds it rejects the delta, naming the class that kept adding.
What an `update` returns never overrides what the delta given to the store says, so that an undo that puts back an old value in a plugin's state puts back that value, and not one that an `update` makes up for a new object.
So the store leaves out a patch of an `update` whose path lies at, under or above a path that one of the given delta's own patches changes.
An array is the exception: a patch at an array's index, or at its end as `-`, names no element.
A patch at an index changes whatever the array holds there by then, and one at `-` adds an element of its own.
So the paths of two patches that both index one array never overlap, even at the same index or below it, and both patches apply, as two appends at `/plugins/blockr.dock-dock_plugin/views/main/grid/children/-` do.
Where one of the delta's own patches and a patch of an `update` both replace the element at the same index, the update's patch applies last and wins.
A patch of the delta's own at the array itself, or above it, still leaves out what an `update` changes inside the array.
The store reads the board before the delta to tell an array's index from an object's member named by digits.
An `update` that adds something for a new object, such as a panel for a block that a delta adds, first checks whether the delta's own patches add it already, which it can, since it gets the delta.
An `update` that changes an element of an array checks the delta's own patches in the same way, since the store applies both patches there.
An `update` gets the board before the delta, so that it sees what the delta removes.
Once a command's `prepare()` resolves, the command registry checks `enabled()` again before it calls `run()`, since the board may have changed while the command waited, and opening a board drops every command still in its `prepare()`.
An `update` leaves the edit ids out, as a command does, since it builds on the board the delta applies to.
Within a collection's part of a delta, `rm` applies before `add`, as core's parts do, since a delta may reuse an id it drops, and `mod` applies last, while patches apply in their order, after core's parts.
The store checks a plugin's state against its class's schema only where a patch changed that state.
The inverse of a removal records each entry's place in its collection, so that undo puts it back where it was.

The precedents for expanding in rounds: a tldraw after handler, such as one that deletes a frame when its last child goes, runs "when the outermost store operation completes, so changes made inside them belong to the same transaction and the same undo step" ([tldraw side effects](https://tldraw.dev/sdk-features/side-effects)), and ProseMirror calls a plugin's `appendTransaction` "again with the new state and new transactions" whenever another plugin appends one ([plugin.ts#L34-L40](https://github.com/ProseMirror/prosemirror-state/blob/ffad5d9450a0b93438be53a801deee1a223a81bf/src/plugin.ts#L34-L40)).
VS Code has an extension describe a tool it offers a model in the terms a command uses here, a `modelDescription` and an `inputSchema` ([Language model tools](https://code.visualstudio.com/api/extension-guides/ai/tools)).

</details>
