# Board objects: blocks, links, stacks, board options and plugins
Status: settled on 2026-10-27. Design for [Client-owned board state](Rewrite-1.1).

The first of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)).
It covers the objects the client holds for a board, its blocks, links, stacks, board options and plugins, how a block names its class by registry id, and how a package keeps what it adds to core's objects in a plugin's state.
It shapes the store, the TypeScript object in core's JS API that holds the board and through which every change to it passes (sketched in [Board updates](Rewrite-1.1.2), [blockr.core#432](https://github.com/BristolMyersSquibb/blockr.core/issues/432)), the command registry ([blockr.core#433](https://github.com/BristolMyersSquibb/blockr.core/issues/433)), defining block classes ([blockr.core#421](https://github.com/BristolMyersSquibb/blockr.core/issues/421)), exporting the block registry ([blockr.core#426](https://github.com/BristolMyersSquibb/blockr.core/issues/426)), the board's name and id ([blockr.core#427](https://github.com/BristolMyersSquibb/blockr.core/issues/427)), writing a board's JSON in R by schema ([blockr.core#428](https://github.com/BristolMyersSquibb/blockr.core/issues/428)), reading a JSON board in R ([blockr.core#429](https://github.com/BristolMyersSquibb/blockr.core/issues/429)), saving a JSON board in the client ([blockr.core#436](https://github.com/BristolMyersSquibb/blockr.core/issues/436)), core's board options ([blockr.core#439](https://github.com/BristolMyersSquibb/blockr.core/issues/439)), a stack's colour ([blockr.core#487](https://github.com/BristolMyersSquibb/blockr.core/issues/487)), plugins in the store and in R ([blockr.core#504](https://github.com/BristolMyersSquibb/blockr.core/issues/504)), refusing a board that holds a value its schema refuses ([blockr.core#509](https://github.com/BristolMyersSquibb/blockr.core/issues/509)), minting ids in the shape that `rand_id` names ([blockr.core#510](https://github.com/BristolMyersSquibb/blockr.core/issues/510)) and keeping links and stacks to core's properties ([blockr.core#511](https://github.com/BristolMyersSquibb/blockr.core/issues/511)), each an item in the Work list of [Client-owned board state](Rewrite-1.1#work).
How the board changes, through deltas, commands and undo, is the [board updates proposal](Rewrite-1.1.2), and the exact JSON format with its migrations is the [serialization proposal](Rewrite-1.1.4).
What a board option is, and the blockr options beside board options, are [Board options and blockr options](Rewrite-1.1.13)'s.
What a plugin is, and which plugins run on a board, are [Plugins](Rewrite-1.1.12)'s.

## What must hold

1. A board built in R by `new_board()` and the block, link, stack and board option constructors maps to the client's board and back without losing any of its state, and so does the JSON `blockr_ser()` writes today.
   An app can start from a JSON board in place of a constructor call, as `serve()` takes a file's path today.
2. The board is plain data, so it serializes as is, and every change to it can be written as a delta and undone, but for a board option's value, which undo leaves alone ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)), and the deltas of a command with `undo: false`, which take no undo step ([Board updates](Rewrite-1.1.2#undo)).
3. A board has no class of its own, and what a package adds to a board, as blockr.dock adds its views today, is the state of one of the board's plugins, beside core's objects, which core carries without reading it ([Plugins](Rewrite-1.1.12#what-must-hold)).
4. A board saved with a package that is not installed opens without the objects that need it, and the user learns which ones were dropped.
5. The board names its blocks' classes by registry id and its plugins' classes by their ids only, while no object in it, nor in the file it is saved to, carries an R class, names a constructor or holds a block class's source ([Serialization](Rewrite-1.1.4)).

## Proposal

### What lives where

Each piece of state has one writer.
The board is the client's alone, and what R holds about it is either computed from the board at one moment, as a result is, or handed over once, as the opening board is.
Neither is ever edited to follow the board, so nothing has to be kept in step with it.
The board holds only what changes while the app runs, with the ids and registry ids that say what each value belongs to, while what nothing changes stays out of it: a block class's UI travels in the block registry's entries R sends the client, and a board option's label and the rest of its definition are the client's own, defined by the package that ships the board option.

| Object | Where | Lives | What it is for |
|---|---|---|---|
| Board, with its blocks, links, stacks, board option values and plugins | The client, in the store | Until another board is opened, and in files | The only copy of what the user built (this proposal) |
| Store | The client, one per board | Until another board is opened | Holds the board and applies every change to it, with undo ([Board updates](Rewrite-1.1.2)) |
| Command registry | The client | Until another board is opened | The edits that menus, shortcuts and plugins, the assistant among them, run ([Board updates](Rewrite-1.1.2)) |
| Scheduler | The client | Until another board is opened | Revisions, statuses, conditions and demand, computed from the board and R's replies ([Evaluation in the client](Rewrite-1.1.10)) |
| Block registry entries | The client | The page | Each block class by registry id, with its UI, inputs and arg specs and the schema of its state that its UI ships, which R sends with the versions of its packages when the client connects, for neither side to edit ([Block classes in R](Rewrite-1.1.5#registration)) |
| Board options | The client | Until another board is opened | Each board option's definition, an `Option`, which the package that ships the board option registers from its JS, for neither side to edit, while the board holds a value that someone set, and core keeps the default it resolved for the opening beside the board ([Board options and blockr options](Rewrite-1.1.13#defining-a-board-option)) |
| Blockr options | The client | The page | The values of the blockr options that core and plugins read, each asked of R the first time client code reads it and kept for the page, since a blockr option is fixed for the app, for neither side to edit, while the board holds none of them ([Board options and blockr options](Rewrite-1.1.13#blockr-options)) |
| Plugin classes | The client | Until another board is opened | Each plugin class's definition, a `PluginClass` under the class's id, which core registers from the module that the class's package lists for it, with its version, which R sends from the class's method of `plugin_version()`, for neither side to edit, while the board holds the state of its plugins ([Plugins](Rewrite-1.1.12#a-plugin)) |
| Frontend and other plugins | The client | Until another board is opened | Draw the board and work on it through `CoreApi`, its store, commands, demand and requests, each keeping its data, where it has any, in its state in the board ([Plugins](Rewrite-1.1.12#running-a-plugin), [Drawing the board](Rewrite-1.1.8)) |
| Block registry | R | The process's for the process, each app's for the app | Each registered block class, a value holding its UI, inputs, `expr`, requests and output, with its constructor and metadata: the process's holds the classes that an app script registers and those that a package which lists none registers as it loads, and an app's, which `serve()` builds and the app's sessions read alone, the classes that the app offers, those that its script defines and those of its board's blocks ([Block classes in R](Rewrite-1.1.5#registration)) |
| R board | R | While R converts it | Built by an app script's constructor calls, whose block classes R registers, then converted to the client's board and dropped, so it never exists beside the client's board |
| Results | R | Until the client forgets the block | For each block R has evaluated, the revision, value, block expression and registry id of its latest evaluation, with the previous value kept while the next computes. They hold no state, which each evaluation brings, so they cannot fall out of step with the board ([Block classes in R](Rewrite-1.1.5#evaluation)) |
| JSON board | A file, or the reply to `hello` | As long as the file, and the process for the opening board | The board with every id, the versions of the shapes it holds and the versions of the packages its content comes from, which the client saves and R writes for the opening board ([Serialization](Rewrite-1.1.4#files)) |

### Objects in R

R holds no copy of the board, so nothing in R has to follow it: an R object either exists only while a board is defined or opened or holds no state, and R reads the current state from the request that needs it.

- An R board, with its blocks, links, stacks, board options and plugins, exists only while R converts it to the client's board: the one an app script builds with constructors, whose block classes R registers.
  R hands it to the client as its board and drops it, while it never opens a JSON board, since the client opens every board ([Board updates](Rewrite-1.1.2#opening-a-board)), and builds from one only where both locks are on ([Locked boards and the properties of blocks](Rewrite-1.1.11#serving-a-json-board-locked)).
  Its S3 classes do their work there, in the constructors, and none reaches the client, since the board names block classes by registry id and plugin classes by their ids (below).
- A block class is a value, defined once with `new_block_class()` and held by the block registry: its UI, inputs, requests and output, and its `expr`, which checks a state and returns what the block expression is made from, while `block_eval()` runs that expression ([Block classes in R](Rewrite-1.1.5)).
  Nothing about a class is copied into a block.
- A block, as its constructor returns it, holds its state and name and refers to its class.
  R builds blocks only where a board is built, in an app script, and, where both locks are on, from the JSON board that `serve()` is given, and keeps none while the app runs.
- Results are an environment keyed by block id, holding for each block R has evaluated the revision, value, block expression and registry id of its latest evaluation, with the previous value kept while the next computes.
  They hold no state: an evaluation brings the recipe's state, from which the class's `expr` builds the block expression that `block_eval()` runs, and the coercion its class names makes an output from a result ([Wire protocol](Rewrite-1.1.9#outputs)).
  R drops a block's results when the client says the block is gone ([Wire protocol](Rewrite-1.1.9)).
- A request carries the current state it needs: an evaluation its recipe ([Wire protocol](Rewrite-1.1.9)), a block class's request the state args its function names and the values of the board options that it names, and an output request, or a request of its output class, the values of the board options that the renderer names ([Board options and blockr options](Rewrite-1.1.13#board-option-values-in-r)), and a plugin's request the args that its caller passes and the revisions of the blocks it reads ([Plugins](Rewrite-1.1.12#a-plugins-requests)).

### The board

```ts
type Json = null | boolean | number | string | Json[] | { [key: string]: Json };

interface Board {
  id: string;                           // given by the script, drawn by R or minted by the client, and kept by saving and opening
  name: string;                         // "Sales review", which core's board option board_name holds today
  blocks: Record<BlockId, Block>;
  links: Record<LinkId, Link>;
  stacks: Record<StackId, Stack>;
  options: Record<OptionId, Json>;      // the board option values that someone set, { n_rows: 50 }
  plugins: Record<PluginClassId, Json>;   // the state of each plugin whose class has state, under its class's id, as Plugins has it
}
```

The board holds no class instances, only plain data, so it serializes as is, a delta is a structural change, and undo replays deltas.
A block names its block class by registry id (below), and a plugin its plugin class by the class's id ([Plugins](Rewrite-1.1.12#a-plugin)), while nothing else in it has a class of its own, the board included: a stack and a link have core's properties and nothing else, and a board option is a value under its id.
No object in it carries an R class vector, and none names a constructor or a package, since the client dispatches on none of them, and neither does a JSON board, the board as a file holds it, with the versions of the shapes it holds and of the packages its content comes from ([Serialization](Rewrite-1.1.4#files)).
When the client opens a JSON board, it finds each block's class among the block registry's entries by registry id, and each plugin's class among the plugin classes that the app's packages register, by the class's id ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)), while a file from today's stack, which names constructors instead, is converted to a JSON board outside core first ([Serialization](Rewrite-1.1.4#files)).

A board has no class of its own, so that every R board is of class `board`, and what a package adds to a board, such as the dock's views, is the state of one of the board's plugins, which `plugins` holds under its class's id ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)).
What a plugin is, which plugins run on a board as it opens, and the frontend, the plugin that draws the page, are [Plugins](Rewrite-1.1.12)'s.

R builds an R board only where an app script defines one, which it converts to JSON once, when `serve()` is called ([Defining a board in R](Rewrite-1.1.3#the-opening-board)).
A JSON board R never opens: it passes the one `serve()` is given on as it is, reading its blocks and links too where both locks are on ([Locked boards and the properties of blocks](Rewrite-1.1.11#serving-a-json-board-locked)), and the client opens that one as it opens the one `store.open()` opens, with the block registry of the reply to `hello` ([Board updates](Rewrite-1.1.2#opening-a-board)).
R loads no package for a board, since installing the packages whose block classes an app offers is the deployment's job, and the block classes that the app offers fill the app's block registry as `serve()` builds the app ([Block classes in R](Rewrite-1.1.5#registration)), so every block's class is registered before a recipe names it, or its block goes:

1. A class defined outside a package is registered only by the script that defines it, so its blocks are dropped and named where it is not (below).
2. A class from a package is registered where the app offers it, among the `blocks` of `serve()`.
3. A block whose class the app does not offer, as where its package is not available or no longer has the class, is dropped and named (below), but on the board that the script builds, whose blocks' classes R registers itself (below).

A block is built by its class's constructor only where an app script calls it, while opening a board and evaluating a block build none ([Block classes in R](Rewrite-1.1.5#evaluation)).
A board from a constructor call may hold blocks of classes nobody registered too, and `serve()` takes those into the app's block registry from the class each block refers to, under the registry id that the class gives (below), before it writes the board as JSON ([Defining a board in R](Rewrite-1.1.3)), so both ways in end with every class registered.
R then turns the R board into the client's board and drops it.
While the app runs, the client's board is the only board, so no edit changes an R object: R evaluates a block from its recipe with its class's `expr` and `block_eval()`, building no block, and keeps the result in an environment keyed by block id ([Block classes in R](Rewrite-1.1.5#evaluation)), and a request that needs more of the board than the blocks it reads carries it.

Collections are keyed by id and ordered by insertion, as `blockr_ser()` writes them as named payloads.
Order matters, since cards follow it and a variadic input takes its links in order, and a JS object keeps insertion order only for property names that do not look like integers, which is why an id may not be made of digits alone (below).

### Blocks

```ts
type Block = {                          // held under its id in board.blocks
  registry_id: RegistryId;              // "blockr.core-head_block"
  state: Record<string, Json>;          // { n: 10, direction: "head" }
  name: string;                         // "Head", today's block_name
  locked: boolean | null;               // whether the board lock fixes its state, null following the board lock (below)
};
```

A block names its entry in the block registry rather than its constructor.
The block registry holds the block class, a value wherever it was defined ([Block classes in R](Rewrite-1.1.5)), while a constructor reference can only name a package's function, and the client needs every class on a board in the block registry anyway, since that is where it gets a class's UI, inputs and arg specs.
The dock's sidebar and the assistant create blocks by registry id already ([blockr.dock R/sidebar-block.R#L182-L184](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/sidebar-block.R#L182-L184), [blockr.assistant R/tools-typed.R#L13-L25](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/tools-typed.R#L13-L25)).
A block carries no class, and neither does its entry in the block registry, since nothing in the client dispatches on one.
Its registry id says which package its class comes from, since an id splits at its first `-`, and so which to install when it is missing.
A block whose class the block registry lacks when the client opens a JSON board is dropped and named (below).
A JSON board holds each block with `version`, the version of its class's state, by which its class's migration converts a state of an older shape ([Serialization](Rewrite-1.1.4#migrations)).

A block's state is its constructor's args and nothing else, so calling its class's constructor with the state, its name and its `locked` rebuilds it.
Its `locked` says whether the board lock fixes its state: `true` locks it, `false` leaves it open, and `null`, which a block holds unless a script or a command sets it, follows the board lock ([Locked boards and the properties of blocks](Rewrite-1.1.11#block-locks)).
What another package keeps about a block, such as which of the dock's card sections show, which travel today as a `visible` property in the block's payload ([blockr.dock R/utils-serdes.R#L12-L33](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L12-L33)), sits outside the block, keyed by its id ([Extending core's objects](#extending-cores-objects)).
The name is a property of its own, since every block has one and the client titles cards and panels with it.

A block's state is part of the board and its status is not, because the board holds what someone wrote, while the scheduler holds what is computed from it, beside the board and keyed by block id ([Evaluation in the client](Rewrite-1.1.10)).
Both change while the app runs, so what separates them is where they come from:

| | State | Status, revision and result |
|---|---|---|
| Written by | The user or the assistant, through a command | The scheduler, from R's replies |
| Can be recomputed | No, it is the source | Yes, by evaluating again |
| Saved in a file | Yes | No |
| Undone | Yes | No |
| Sent to a collaborator | Yes | No, since results are per session |

A spreadsheet draws the same line between the formula in a cell and the value it shows, and today's R stack does too, keeping a block's result and status in the board server's reactives rather than on the block.
Code that draws a block need not see the split, since its host hands a block's UI its name and status beside its state ([UI modules in JS](Rewrite-1.1.7#the-contract)).

### Registry ids

A registry id is `{pkg}-{id}`, such as `blockr.core-head_block`: the package is the one whose code calls `new_block_class()`, which the class records, and the id is the one that `new_block_class()` takes, unique within the package, which R checks as it registers the package's classes ([blockr.core#561](https://github.com/BristolMyersSquibb/blockr.core/pull/561)).
A package name holds only letters, digits and dots, so an id splits at its first `-`, and two packages that do not know of each other cannot produce the same id.
The id is the class's own, declared with the class rather than read off its constructor's name or its class vector, so that a package that renames a constructor keeps the id and its saved boards keep working ([Block classes in R](Rewrite-1.1.5#the-block-class)).
For the 46 entries that blockr.core, blockr.dplyr, blockr.dm, blockr.ggplot and blockr.io register, only the prefix is new, since each class can take as its id the uid it has today, its constructor's name without `new_`, and each entry's package is its constructor's.
A class defined outside a package has its id alone as its registry id, which cannot equal a package's, since a class's id holds no `-`, and needs to be unique only within one app, whose `serve()` refuses a board with blocks of two such classes of one id ([Block classes in R](Rewrite-1.1.5#registration)).

R finds the entry of a block it holds by the class the block refers to, where `registry_id_from_block()` goes by class today ([R/block-registry.R#L304-L318](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-registry.R#L304-L318)), so each class has one entry ([Block classes in R](Rewrite-1.1.5)).

### Block classes outside a package

A block class defined outside a package is the norm in development, demos and examples, and works wherever the script that defines it registers it, as an app script does before its board opens ([Defining a board in R](Rewrite-1.1.3#the-opening-board)).
A file holds the blocks of such a class by registry id, as it holds any block, and nothing of the class itself, so the app that saved a file reopens it fully, deployed or not, while a session where the class is not registered drops its blocks and names them, like any block R cannot build (below).

A file holds no class's source, because no form of it reproduces a class in general.
Today `blockr_ser()` writes the constructor as a closure ([R/utils-serdes.R#L124-L142](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L124-L142)), which brings its environment along: Shiny sources an app.R into a new environment rather than the global one ([shiny R/shinyapp.R#L486-L494](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/shinyapp.R#L486-L494)), so for a block class defined in an app.R that reads an API key and loads a 3.8 MB data frame, `blockr_ser()` writes 4.0 MB with every block of that class, the key included, while a constructor defined at a script's top level loses the script's globals, since `serialize()` writes the global environment as a reference.
The call that defined a class would reproduce it only where it names nothing else of the script, and not where `new_block_class()` is aliased, a property comes from a variable or a function of the script makes the class.
A file from today's stack holds such a constructor as a closure, which its conversion outside core leaves unread ([Serialization](Rewrite-1.1.4#files)): a function saved today builds its block from a Shiny server, which the contract of [Block classes in R](Rewrite-1.1.5) replaces, so such a block keeps the name the file records as its registry id, and opens only where a block class of that name is registered, such as one the developer has rewritten to that contract, and is dropped and named otherwise.

### Links

```ts
interface Link {                        // held under its id in board.links
  from: BlockId;                        // "a"
  to: BlockId;                          // "c"
  input: string;                        // "x"
}
```

A link carries no name, as today, and no class, which a link cannot keep even today: the `links()` record keeps each link's fields as columns but drops its class and constructor ([R/links-class.R#L15-L47](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/links-class.R#L15-L47)), and a link read out of it is rebuilt by `new_link()` ([#L277-L292](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/links-class.R#L277-L292)).
So every link `blockr_ser()` writes is a plain `link` made by `new_link()`, and so is a link read from a file that names a subclass.
A package that keeps more about a link keeps it in its plugin's state, keyed by the link's id (below).
Its input is always resolved for a target of fixed arity, so filling in a unary target's only input is the job of the command that adds the link, not of the board.
For a variadic target, an empty input appends positionally, in link order, as today ([R/board-server.R#L1215-L1242](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L1215-L1242)).

### Stacks

```ts
interface Stack {                       // held under its id in board.stacks
  name: string;
  blocks: BlockId[];
  color: string | null;                 // "#66c2a5", the colour frontends draw the stack in, or null for none
}
```

A stack may carry a colour, which frontends draw it in, as the dock and the DAG do today.
The colour is a hex colour of six digits, such as `#66c2a5`.
That is the one form that `<input type="color">` takes, so a frontend hands a stack's colour to a colour input as it is.
A stack without a colour holds `null`, and a frontend draws it in a default of its own.
So every stack holds `color`, as every link holds `input`.
A command clears a colour by setting it to `null`, and undo does the same for a colour that its step set on a stack that had none.
A stack's change in a delta sets properties and removes none, so a stack that could lack `color` would leave undo no way to take a colour away ([Board updates](Rewrite-1.1.2#deltas)).
The colour is core's rather than the dock's.
So a board opened under any frontend keeps the colours of its stacks, and core's commands set them ([Board updates](Rewrite-1.1.2#commands)).
Today the dock keeps the colour on a `dock_stack`, which extends core's stack ([blockr.dock R/dock-stack.R#L24-L27](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-stack.R#L24-L27)).
It takes three digits too, as `#fc8`, which it expands to six before it fills a colour input ([R/utils-misc.R#L72-L85](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/utils-misc.R#L72-L85)).

### Board options

The board holds each board option's value under its id, such as `n_rows`, which a command sets ([Board updates](Rewrite-1.1.2)), and nothing else of the board option.
What a board option is, which board options a board holds and how code reads their values are [Board options and blockr options](Rewrite-1.1.13)'s.

### Extending core's objects

A package adds to the board through a plugin, whose state the board holds under its class's id, beside core's objects, where the dock board adds views, grids and extensions as properties of its own today ([R/dock-board.R#L55-L79](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L55-L79)).
These become the state of the dock plugin and of one plugin for each extension ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)), held as the dock's design has it ([Client-drawn dock](Rewrite-1.2)).
Today the dock also adds a colour to every stack, since `new_dock_board()` makes each of its stacks a dock stack ([R/dock-stack.R#L171-L192](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-stack.R#L171-L192)), and that colour becomes core's ([Stacks](#stacks)).
Core carries each plugin's state without reading it: it registers nothing inside it, and checks the state's whole value against the schema that the plugin's class gives, after every change, while what sits inside, such as how the dock lays out its views, is the class's own design ([Plugins](Rewrite-1.1.12#a-plugins-state)).
Core's objects hold only core's properties, and what a package keeps about a link, a stack or a block, such as the DAG's positions or which of the dock's card sections show, sits in the state of the package's plugin, keyed by the object's id.
So core's commands and the assistant create blocks, links and stacks without knowing any plugin class.
A change inside a plugin's state travels as a patch at a nested path, which the store applies without knowing the state's structure, and the package that defines the plugin's class registers the commands that change it, beside core's command for any plugin's state ([Board updates](Rewrite-1.1.2#plugins)).
Whatever reads only core's objects, such as core's basic frontend, works on every board, whichever plugins run on it.
Core publishes TypeScript types for its own objects, and a JSON Schema of a JSON board generated from them, by which R writes a board ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)), and a plugin class's package types the state of its plugins itself, as the dock would type its own, with illustrative names:

```ts
type DockState = {                      // blockr.dock's type for its plugin's state, which core holds as Json
  views: Record<ViewId, View>;          // { main: { name: "Main", folder: null, index: "a0", grid: { ... } } }
  folders: Record<FolderId, Folder>;    // { safety: { name: "Safety", folder: null, index: "a1" } }
  active: ViewId;                       // "main"
  visible: Record<BlockId, Section[]>;  // { a: ["outputs"] }, as The dock's state has it
};
```

Core carries a plugin's state without knowing it, as it carries a board's extra components today: `new_dock_board()` passes its views, grids and extensions to `new_board()` as extra components ([blockr.dock R/dock-board.R#L66-L78](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L66-L78)), and `blockr_ser.board()` serializes each of them by dispatch ([R/utils-serdes.R#L218-L231](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L218-L231)).
What lives today in the reactive state of the dock's extensions, such as the DAG's positions and layout ([R/ext.R#L37-L47](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/ext.R#L37-L47)), blockr.md's content ([R/md-ext.R#L9-L26](https://github.com/BristolMyersSquibb/blockr.md/blob/32e088884d825813fb7ff0afc7d023df9e70a3b6/R/md-ext.R#L9-L26)) and the assistant's threads ([R/ext-serdes.R#L2-L28](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/ext-serdes.R#L2-L28)), goes into the state of the plugin that takes the extension's place, rather than into the dock's state ([Plugins](Rewrite-1.1.12#a-plugins-state)).
Of what a plugin keeps, the board holds what opening, saving and restoring it need, such as the dock's views, their grids and which view is active, and leaves out what only one person's screen needs, such as the selection or which panel has focus, as [Client-drawn dock](Rewrite-1.2) has it for the dock, and each plugin sorts its own state by the same rule.

A plugin's state that refers to core's objects stays consistent through the change that removes one.
A plugin class gives core one function, its `update`, which the store calls for each of the class's plugins with every change it applies and which returns patches for that plugin's state, in the same step ([Board updates](Rewrite-1.1.2#applying-a-delta)).
With it the dock drops a removed block's panels and the DAG its position, as every plugin does for what it keeps, so nothing keeps ghost entries, as the dock's grids do today ([R/dock-grid.R#L733-L748](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-grid.R#L733-L748)).
A plugin class migrates its plugins' state in JS, by the version of its shape that a JSON board records for the class ([Serialization](Rewrite-1.1.4#migrations)), where the dock reads the version of blockr.dock that the board's constructor records today as `producer_version` ([blockr.dock R/utils-serdes.R#L98-L131](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L98-L131)), since a package's version says when it was released rather than what shape its content has.
R never opens a board, so the client hands a class's `migrate` what the JSON board holds with the version it records, and a class reads every shape it ever wrote in one place, beside its state's schema.
Its R side only writes its plugins' state for a script's board, while a board that opens without one of the app's plugins takes it over with its class's default state, whichever way the board comes in ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)).

### Ids

Every object, the board, a block, a link, a stack or a plugin, has an id, and all but a link have a name.
The id identifies the object, and the board holds a block, a link or a stack under it, so none of them repeats it: references and collections use it, it never changes, and it is unique within its collection.
The name is what the user calls the object: free text the user can change at any time and nothing refers to, so renaming a block changes its name, as today.
An app script may give an object its id, as it must for a block that a link or a stack refers to, or leave it out, and R draws each id it leaves out with `rand_names()`, in `new_board()` and in the containers of blocks, links and stacks, as today's stack does ([R/utils-misc.R#L66-L103](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-misc.R#L66-L103)), and names a board without a name after its id, in sentence case, as core's `board_name` board option does today ([R/board-option.R#L285-L296](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L285-L296)).
A plugin is identified by its class's id instead, since an app runs at most one plugin of each class ([Plugins](Rewrite-1.1.12#a-plugin)).
The client mints the ids of the objects and boards it creates, in the same shapes, which the blockr option `rand_id` names, such as `calm_heron`, and from the same words, which core ships, so that an id looks the same whichever side drew it.
So every board that reaches the client holds every id, with its collections keyed by id, as a JSON board does ([Serialization](Rewrite-1.1.4#files)), and R draws the opening board's ids once per process, as the script runs, so every session of an app opens the same ids.
An id is any string that is not empty and not made of digits alone, since a JS object, `JSON.parse()` included, puts property names that look like integers first, whatever the order they were inserted in.
Nothing else about an id needs a rule: exported code backticks an id that is not a syntactic name, and the client escapes ids in CSS selectors or keeps them out of element ids, while the Shiny input names that [blockr.core#390](https://github.com/BristolMyersSquibb/blockr.core/issues/390) shows breaking are gone, since every message travels through one input ([Wire protocol](Rewrite-1.1.9)).
The store refuses to open a board with an id made of digits alone, with an error that names the id.

### What the store checks

The store checks after every delta that ids are unique and well formed, that a link's endpoints exist, its target declares its input, a fixed input takes at most one link and no links form a cycle, as `validate_links()` and the board's checks do today ([R/links-class.R#L308-L368](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/links-class.R#L308-L368), [R/board-class.R#L64-L122](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-class.R#L64-L122)), that a stack names existing blocks and a block sits in at most one stack, and that every value a delta sets for a board option fits that board option's schema.
It also checks that a block's class is in the block registry, since opening a board drops a block whose class it lacks, so that no delta makes a board that no opening would, and that a block, link or stack that a delta adds or changes has core's properties and nothing else, since deltas come from plain JS and from the assistant's tools too.
These two look only at what a delta changed: on a board of 1,000 blocks they take 0.4 µs of an `apply()` that takes 3.8 ms, most of it in the checks of the whole board.
With the properties of a stack that a delta adds or changes, the store checks that its colour is `null` or a hex colour of six digits ([Stacks](#stacks)).
With the state of a plugin that a delta changes, the store checks that the plugin is one of the app's whose class is registered with `state`, since no change adds a plugin, while R's `serve()` checks that the app holds one frontend and at most one storage plugin ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)).

### Objects that cannot be rebuilt

When the client opens a board, it drops what the app cannot rebuild: a block whose class the block registry lacks, as when its package is not installed or no longer has the class, as in [blockr.core#386](https://github.com/BristolMyersSquibb/blockr.core/issues/386), or its class comes from no package and is not registered, together with the links and stack places that refer to it, the state of a plugin of a class that the app does not run, or that none of the packages that the app uses registers ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)), and, once the migrations have run, the board option values that no package that the app uses registers, as those of a package that is missing ([Board updates](Rewrite-1.1.2#plugins)).
So a board that holds the dock's state opens without it where blockr.dock is missing, with the app's frontend, so that only what the missing package's plugins keep goes, such as the dock's views ([Plugins](Rewrite-1.1.12#the-frontend)).
Saved and opened again in a dock app, it gets that app's dock, with the dock's default layout.
The client names each block it drops, and each plugin whose state it drops, with the package of its class, which the block's registry id and the plugin's class id give, and each package that the JSON board lists and the app does not offer, with the version it records, so the user learns what to install, and it names each board option value it drops by its id, while a board saved afterwards is written without any of them.
Core tells the user what it dropped in one notification as the board opens, which every frontend shows ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)).
What core does where a plugin's class requires a board option that no loaded package defines is [Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)'s.
Today `blockr_deser()` drops blocks only with `deser_on_error = "drop"`, pruning their links and stacks, and logs them without telling the user ([R/utils-serdes.R#L379-L391](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L379-L391), [#L433-L457](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L433-L457)), and a board whose class's package is missing does not open at all, since reading its constructor fails ([#L518-L538](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L518-L538)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's classes, at `da3fcb4`: [`new_block()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L180-L254) with class `c(<class>, "block", "vctrs_vctr", "list")`, no stored version ([R/utils-serdes.R#L124-L142](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L124-L142)) and its state read from the block server at save time ([R/plugin-serdes.R#L138-L156](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-serdes.R#L138-L156)); [`new_link()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/link-class.R#L54-L161); [`new_stack()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/stack-class.R#L47-L78), a character vector of block ids, one stack per block ([R/stacks-class.R#L14-L103](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/stacks-class.R#L14-L103)); [`new_board_option()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L16-L37), with values in `session$userData` ([R/board-options.R#L150-L225](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-options.R#L150-L225)); [`new_board()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-class.R#L38-L62), which takes extra components through `...` and gets an id on restore ([R/utils-serdes.R#L402-L431](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L402-L431)).

The JSON today's `blockr_ser()` writes maps onto the client's board as follows: `object` is the class vector, which the client's board does not keep, since a block takes the registry id its constructor gives instead, the board the plugins its class stands for, as a dock board the dock plugin ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)), and a stack, a link and a board option need no class of their own; a block's `payload` is its state plus `block_name`; `constructor` gives the package and its version, and for a block the constructor that gives its registry id, and for the board the constructor whose class gives its plugins, unless a block's was saved as a closure, which R leaves unread, going by the block's class instead; a stack's `payload` is `{blocks, name}`; a link's is `{from, to, input}`; the board options' `payload` is a list of board option objects, each with its class (`n_rows_option`, giving the id) and a `payload` holding `value`, `category` and `label`, of which the board keeps the value under the board option's id, while the category and label come from the board option's definition in the client ([Serialization](Rewrite-1.1.4#board-options)); and the board's own `version` and `id` sit next to its `payload`, while its name is the value of its `board_name` board option.
A board with three blocks, three links and a stack, written by blockr.core 0.1.4:

```json
{
  "object": "board",
  "payload": {
    "blocks": {
      "object": ["blocks", "vctrs_vctr", "list"],
      "payload": {
        "b": {
          "object": ["head_block", "transform_block", "block", "vctrs_vctr", "list"],
          "payload": { "n": 10, "direction": "head", "block_name": "Head" },
          "constructor": { "object": "blockr_ctor", "constructor": "new_head_block", "package": "blockr.core", "version": "0.1.4" }
        }
      }
    },
    "links": {
      "object": ["links", "vctrs_rcrd", "vctrs_vctr"],
      "payload": {
        "ab": {
          "object": ["link", "vctrs_vctr", "list"],
          "payload": { "from": "a", "to": "b", "input": "data" },
          "constructor": { "object": "blockr_ctor", "constructor": "new_link", "package": "blockr.core", "version": "0.1.4" }
        }
      }
    },
    "stacks": {
      "object": ["stacks", "vctrs_vctr", "list"],
      "payload": {
        "s1": {
          "object": "stack",
          "payload": { "blocks": ["a", "b"], "name": "Input" },
          "constructor": { "object": "blockr_ctor", "constructor": "new_stack", "package": "blockr.core", "version": "0.1.4" }
        }
      }
    },
    "options": {
      "object": ["board_options", "vctrs_vctr", "list"],
      "payload": [
        {
          "object": ["show_conditions_option", "board_option"],
          "payload": { "value": ["warning", "error"], "category": "Board options", "label": "Message types to display" },
          "constructor": { "object": "blockr_ctor", "constructor": "new_show_conditions_option", "package": "blockr.core", "version": "0.1.4" }
        }
      ]
    }
  },
  "constructor": { "object": "blockr_ctor", "constructor": "new_board", "package": "blockr.core", "version": "0.1.4" },
  "version": "0.1.4",
  "id": null
}
```

The dock's board subclass adds `extensions`, `views` and `grids` to the board ([R/dock-board.R#L55-L79](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L55-L79)): a view lists its panels as `block_panel-<id>` and `ext_panel-<key>` ([R/dock-view.R#L86-L182](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-view.R#L86-L182)), and a grid arranges them ([R/dock-grid.R#L49-L64](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-grid.R#L49-L64)).
No package other than blockr.dock subclasses a board or a stack, and none subclasses a link.

A plugin's state is `Json` in core's types, so a package that types the state of its plugins, as blockr.dock would type `DockState`, declares that type with `type` rather than `interface`, since only an object type that `type` declares is assignable to `Json`'s `{ [key: string]: Json }`.

</details>
