# Board objects: blocks, links, stacks, options and fields
Status: settled on 2026-10-27. Design for [Client-owned board state](Rewrite-1.1).

The first of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)). It covers the objects the client holds for a board, its blocks, links, stacks and options, how the board names the front-end it is made for and a block its class by registry id, and how packages extend these objects with fields of their own. It shapes the store, the TypeScript object in core's JS API that holds the board and through which every change to it passes (sketched in [Board updates](Rewrite-1.1.2)), exporting the block registry, opening a board in R and writing a saved board in the client, each an item in the Work list of [Client-owned board state](Rewrite-1.1#work). How the board changes, through deltas, commands and undo, is the [board updates proposal](Rewrite-1.1.2), and the exact JSON format with its migrations is the [serialization proposal](Rewrite-1.1.4).

## What must hold

1. A board built in R by `new_board()` and the block, link, stack and option constructors maps to the client's board and back without losing any of its state, and so does the JSON `blockr_ser()` writes today. An app can start from a saved file in place of a constructor call, as `serve()` takes a file's path today.
2. The board is plain data, so it serializes as is, and every change to it can be written as a delta and undone.
3. A board names the front-end it is made for, as blockr.dock makes boards of its own today, and every package, the front-end and each board extension alike, keeps its state in fields of its own.
4. A board saved with a package that is not installed opens without the objects that need it, and the user learns which ones were dropped.
5. The board names the front-end it is made for and its blocks' classes by registry id only, and no object in it, nor in the file it is saved to, carries an R class or names a constructor, while the file holds the source of block classes defined outside a package, which development, demos and examples rely on ([Serialization](Rewrite-1.1.4)).

## Proposal

### What lives where

Each piece of state has one writer. The board is the client's alone, and what R holds about it is either computed from the board at one moment, as a result is, or handed over once, as the opening board is. Neither is ever edited to follow the board, so nothing has to be kept in step with it. The board holds only what changes while the app runs, with the ids and registry ids that say what each value belongs to, while what nothing changes stays out of it: a block class's UI travels in the block registry's entries R sends the client, and an option's label and the rest of its definition are the client's own, defined by the package that ships the option.

| Object | Where | Lives | What it is for |
|---|---|---|---|
| Board, with its blocks, links, stacks and option values | The client, in the store | Until another board is opened, and in files | The only copy of what the user built (this proposal) |
| Store | The client, one per board | The page | Holds the board and applies every change to it, with undo ([Board updates](Rewrite-1.1.2)) |
| Command registry | The client | The page | The edits that menus, shortcuts, extensions and the assistant run ([Board updates](Rewrite-1.1.2)) |
| Scheduler | The client | The page | Revisions, statuses, conditions and demand, computed from the board and R's replies ([Evaluation in the client](Rewrite-1.1.10)) |
| Block registry entries | The client | The page | Each block class by registry id, with its UI, inputs and arg specs, the schema of its state that its UI ships, and its definition where it was defined outside a package, which R sends with the versions of its packages when the client connects and whenever a board opens, for neither side to edit ([Block classes in R](Rewrite-1.1.5#registration)) |
| Options | The client | The page | Each option's definition, an `Option`, which the package that ships the option registers from its JS, for neither side to edit, while the board holds its value ([Options](#options)) |
| Blockr options | The client | The page | The values of the blockr options that front-ends and extensions read, as R sends them with its reply to `hello`, for neither side to edit, while the board holds none of them ([Defining a board in R](Rewrite-1.1.3#blockr-options)) |
| Front-end and extensions | The client | The page | Draw the board and work on it through the store, commands, demand and requests, keeping their own state in the board ([Front-ends and extension points](Rewrite-1.1.8)) |
| Block registry | R | The process, and a class a file defines until another board opens | Each registered block class, a value holding its UI, inputs, requests, options and the functions that evaluate its blocks, with its constructor and metadata ([Block classes in R](Rewrite-1.1.5)) |
| R board | R | While R converts it | Built by an app script's constructor calls, whose options R collects and whose block classes it registers, or from a file of today's stack, then converted to the client's board and dropped, so it never exists beside the client's board |
| Results | R | Until the client forgets the block | For each block R has evaluated, the revision, value, block expression and registry id of its latest evaluation, with the previous value kept while the next computes. They hold no state, which each evaluation brings, so they cannot fall out of step with the board ([Block classes in R](Rewrite-1.1.5#evaluation)) |
| Saved board | A file | As long as the file | The board, with the versions of the packages that saved it and the source of block classes defined outside a package, written by the client and read by R ([Serialization](Rewrite-1.1.4#files)) |

### Objects in R

R holds no copy of the board, so nothing in R has to follow it: an R object either exists only while a board is defined or opened or holds no state, and R reads the current state from the request that needs it.

- An R board, with its blocks, links, stacks and options, exists only while R converts it to the client's board: the one an app script builds with constructors, whose options R collects and whose block classes it registers, and the one `blockr_deser()` builds from a file of today's stack. R hands it to the client as its board and drops it, while a board given as JSON of the new stack it opens without building one ([Board updates](Rewrite-1.1.2#opening-a-board)). Its S3 classes do their work there, in the constructors, in `blockr_deser()` and in collecting options, and none of them reaches the client, whose board names block classes by registry id (below).
- A block class is a value, defined once with `new_block_class()` and held by the block registry: its UI, inputs, requests and options, and the functions that validate a state, build the expression and evaluate it ([Block classes in R](Rewrite-1.1.5)). Nothing about a class is copied into a block.
- A block, as its constructor returns it, holds its state and name and refers to its class. R builds blocks only where a board is built, in an app script and when a board is opened, and keeps none while the app runs.
- Results are an environment keyed by block id, holding for each block R has evaluated the revision, value, block expression and registry id of its latest evaluation, with the previous value kept while the next computes. They hold no state: an evaluation brings the recipe's state, from which the class's `expr` builds the block expression that `block_eval()` runs, and the coercion its class names makes an output from a result ([Wire protocol](Rewrite-1.1.9#outputs)). R drops a block's results when the client says the block is gone ([Wire protocol](Rewrite-1.1.9)).
- A request carries the current state it needs: an evaluation its recipe ([Wire protocol](Rewrite-1.1.9)), a block class's request the state args its function names, and an output request the board's option values.

### The board

```ts
type Json = null | boolean | number | string | Json[] | { [key: string]: Json };

interface Fields {}                     // empty in core, which packages add their fields to (below)

interface Board {
  id: string;                           // set when the board is created, and kept by saving and opening
  front_end: string;                    // "blockr.dock-dock", the id of the front-end the board is made for
  name: string;                         // "Sales review", which core's board_name option holds today
  blocks: Record<BlockId, Block>;
  links: Record<LinkId, Link>;
  stacks: Record<StackId, Stack>;
  options: Record<OptionId, Json>;      // each option's value, { n_rows: 50 }
  fields: Partial<Fields> & Record<FieldId, unknown>;   // what packages add, by field id, such as the dock's views and the DAG's positions
}
```

The board holds no class instances, only plain data, so it serializes as is, a delta is a structural change, and undo replays deltas. It names the front-end it is made for, and a block names its block class by registry id (below), while nothing else in it has a class of its own: a stack and a link have core's keys and nothing else, and an option is a value under its id. No object carries an R class vector or names a constructor or a package, since the client dispatches on none of them, and neither does the file a board is saved to, which is the board with the versions of the packages that saved it ([Serialization](Rewrite-1.1.4#files)). When R opens a file, it finds each block's class in its block registry by registry id, and the board's front-end by its name, while a file from today's stack names constructors instead, which R maps to registry ids and a front-end.

A board names its front-end by the front-end's id, `{pkg}-{name}` as a registry id is, since a package declares each of its front-ends in R under a name, so that it can ship several: `blockr.core-basic` for core's basic front-end and `blockr.dock-dock` for the dock ([Front-ends and extension points](Rewrite-1.1.8#registering-a-front-end)). A board's constructor sets it, as `new_dock_board()` sets `blockr.dock-dock`, a file of the new stack holds it, and R reads it off a file from today's stack by building its board with the constructor the file names, so R reads a board's front-end off either.

R builds an R board only where an app script defines one, and converts it to JSON once, when `serve()` is called ([Defining a board in R](Rewrite-1.1.3#the-opening-board)). A board given as JSON, the file `serve()` is given, the board `store.open()` sends ([Board updates](Rewrite-1.1.2)) and the one a client sends with `hello` after R restarts ([Wire protocol](Rewrite-1.1.9#handshake)), R opens without building one: it works on the JSON and sends it on. It reads a file of the new stack by its registry ids, building no R object, and one from today's stack with `blockr_deser()`, which dispatches on each object's class ([R/utils-serdes.R#L291-L301](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L291-L301)) and calls the constructor the file names or defines, and on the way makes sure every block's class is registered:

1. A class defined outside a package is registered from the definition the file holds for it under its registry id (below).
2. A class from an installed package that nobody registered is registered from its constructor, once R has loaded the package.
3. A block whose package is not installed, or no longer has its constructor, is dropped and named (below).

A block is built by its class's constructor only where an app script calls it, or where `blockr_deser()` converts a file from today's stack, while opening a file of the new stack and evaluating a block build none ([Block classes in R](Rewrite-1.1.5#evaluation)). A board from a constructor call may hold blocks of classes nobody registered too, and R registers those from the constructor each block carries, under the ids the defaults below give, before it writes the board as JSON ([Defining a board in R](Rewrite-1.1.3)), so both ways in end with every class registered. R then turns the R board into the client's board and drops it. While the app runs, the client's board is the only board, so no edit changes an R object: R evaluates a block from its recipe with its class's `expr` and `block_eval()`, building no block, and keeps the result in an environment keyed by block id ([Block classes in R](Rewrite-1.1.5#evaluation)), and a request that needs more of the board than the blocks it reads carries it.

Collections are keyed by id and ordered by insertion, as `blockr_ser()` writes them as named payloads. Order matters, since cards follow it and a variadic input takes its links in order, and a JS object keeps insertion order only for keys that do not look like integers, which is why an id may not be made of digits alone (below).

### Blocks

```ts
type Block = {                          // held under its id in board.blocks
  registry_id: RegistryId;              // "blockr.core-head_block"
  state: Record<string, Json>;          // { n: 10, direction: "head" }
  name: string;                         // "Head", today's block_name
  attrs: Record<string, Json>;          // { visible: ["outputs"] }, what packages keep on every block (below)
};
```

A block names its entry in the block registry rather than its constructor. The block registry holds the block class, a value wherever it was defined ([Block classes in R](Rewrite-1.1.5)), while a constructor reference can only name a package's function, and the client needs every class on a board in the block registry anyway, since that is where it gets a class's UI, inputs and arg specs. The dock's sidebar and the assistant create blocks by registry id already ([blockr.dock R/sidebar-block.R#L182-L184](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/sidebar-block.R#L182-L184), [blockr.assistant R/tools-typed.R#L13-L25](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/tools-typed.R#L13-L25)). A block carries no class, and neither does its entry in the block registry, since nothing in the client dispatches on one. Its registry id says which package R loads before the id can resolve, since an id splits at its first `-`, as `asNamespace()` loads a package when a constructor is looked up today ([R/utils-serdes.R#L518-L538](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L518-L538)), and which to install when it is missing. A block R cannot build when it opens a file is dropped and named (below).

A block's state is its constructor's args and nothing else, so calling its class's constructor with the state, its name and its attributes rebuilds it. An attribute is what a package keeps on every block, core's own `visible` among them, which says which of a block's sections show, its inputs and its output, and which a locked board reads ([Wire protocol](Rewrite-1.1.9#locked-boards)), as the dock's card sections today travel as a `visible` field in the block's payload ([blockr.dock R/utils-serdes.R#L12-L33](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L12-L33)): the package registers it with the store, with a schema and an initial value ([Board updates](Rewrite-1.1.2#fields)), a block constructor takes it through `...`, as `new_block()` keeps such args today, and core carries another package's attribute without reading it, so that a block copied or removed takes its attributes along. The name is a key of its own, since every block has one and the client titles cards and panels with it.

A block's state is part of the board and its status is not, because the board holds what someone wrote, while the scheduler holds what is computed from it, beside the board and keyed by block id ([Evaluation in the client](Rewrite-1.1.10)). Both change while the app runs, so what separates them is where they come from:

| | State | Status, revision and result |
|---|---|---|
| Written by | The user or the assistant, through a command | The scheduler, from R's replies |
| Can be recomputed | No, it is the source | Yes, by evaluating again |
| Saved in a file | Yes | No |
| Undone | Yes | No |
| Sent to a collaborator | Yes | No, since results are per session |

A spreadsheet draws the same line between the formula in a cell and the value it shows, and today's R stack does too, keeping a block's result and status in the board server's reactives rather than on the block. Code that draws a block need not see the split, since its host hands a block's UI its name and status beside its state ([UI modules in JS](Rewrite-1.1.7#the-contract)).

### Registry ids

A registry id is `{pkg}-{name}`, such as `blockr.core-head_block`: the package is the one the constructor lives in, and the name is unique within it, which `register_block()` checks. A package name holds only letters, digits and dots, so an id splits at its first `-`, and two packages that do not know of each other cannot produce the same id. The name defaults to the constructor's name without `new_`, which a namespace keeps unique, and `uid` sets it for a package that renames a constructor and wants its saved boards to keep working. For the 46 entries that blockr.core, blockr.dplyr, blockr.dm, blockr.ggplot and blockr.io register, only the prefix is new, since each uid equals its constructor's name without `new_` and each entry's package is its constructor's. A class registered outside a package has the name alone as its id, which cannot equal a package's and only needs to be unique within one process, and since a function object comes without a name, its name defaults to the block's class.

R finds the entry of a block it holds by the class the block refers to, where `registry_id_from_block()` goes by class today ([R/block-registry.R#L304-L318](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-registry.R#L304-L318)), so each class has one entry ([Block classes in R](Rewrite-1.1.5)).

### Block classes outside a package

A block class defined outside a package is the norm in development, demos and examples, and the file a board is saved to keeps such classes working. For a package's class, the block registry keeps its constructor by reference, as `new_head_block` in blockr.core, and for a class defined outside a package the constructor itself, with the class's source: the code the class was defined by, wrapped in `block_constructor()`, since the constructor that `block_constructor()` makes refers to its class and holds none of it in its own source ([Block classes in R](Rewrite-1.1.5#registration)). The block registry carries that source as the class's definition, which the client writes into the file once for the class, under its registry id ([Serialization](Rewrite-1.1.4#files)). A definition holds the source text and never the closure, which brings its environment along: Shiny sources an app.R into a new environment rather than the global one ([shiny R/shinyapp.R#L486-L494](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/shinyapp.R#L486-L494)), so for a block class defined in an app.R that reads an API key and loads a 3.8 MB data frame, `blockr_ser()` writes 4.0 MB with every block of that class today ([R/utils-serdes.R#L124-L142](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L124-L142)), the key included.

R evaluates a definition only where no block class of the block's class name is registered, so a block class the app registers wins over the copy in the file, and only when the `load_definitions` option allows it, which it does by default in an interactive session, so a deployment evaluates no code from a file unless it opts in. A definition is an expression whose value is the constructor, so it binds no name: R evaluates it in a new environment whose parent is the global environment, as a script's top level runs, and registers the value under its class name, the id such a class takes by default. A class registered from a file goes when the next board opens, since opening forgets every block ([Wire protocol](Rewrite-1.1.9)), so a second file with a block class of the same name gets its own, while the classes that packages and the app script register stay. Where R does not evaluate a definition, the class's blocks are dropped and named like any block R cannot build. A file from today's stack holds such a constructor as a closure, which R leaves unread when it opens the file ([Serialization](Rewrite-1.1.4#files)): a function saved today builds its block from a Shiny server, which the contract of [Block classes in R](Rewrite-1.1.5) replaces, so such a block opens only where a block class of the name the file records is registered, such as one the developer has rewritten to that contract, and is dropped and named otherwise.

### Links

```ts
interface Link {                        // held under its id in board.links
  from: BlockId;                        // "a"
  to: BlockId;                          // "c"
  input: string;                        // "x"
}
```

A link carries no name, as today, and no class, which a link cannot keep even today: the `links()` record keeps each link's fields as columns but drops its class and constructor ([R/links-class.R#L15-L47](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/links-class.R#L15-L47)), and a link read out of it is rebuilt by `new_link()` ([#L277-L292](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/links-class.R#L277-L292)). So every link `blockr_ser()` writes is a plain `link` made by `new_link()`, and so is a link read from a file that names a subclass. A package that keeps more about a link keeps it in a field of its own, keyed by the link's id (below). Its input is always resolved for a target of fixed arity, so filling in a unary target's only input is the job of the command that adds the link, not of the board. For a variadic target, an empty input appends positionally, in link order, as today ([R/board-server.R#L1215-L1242](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L1215-L1242)).

### Stacks

```ts
interface Stack {                       // held under its id in board.stacks
  name: string;
  blocks: BlockId[];
}
```

### Options

The board holds each option's value under the option's id, which says which option it is, such as `n_rows`. The value is the option's state, which a command sets ([Board updates](Rewrite-1.1.2)). The rest of an option is defined once, in the client, by the package that ships it: its label, its category, the schema of its value, its UI, and what a new value does on the page, such as switching the theme for `dark_mode`, which the option's `server` does in R today ([R/board-option.R#L572-L582](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L572-L582)) and which R could not describe to the client. R names an option by its id and gives its initial value, which the option's constructor computes, as `new_dark_mode_option(value = blockr_option("dark_mode", NULL))` does today, and nothing else of an option crosses the wire. The board holds the values of the options that its parts require, its front-end, which declares those it requires ([Front-ends and extension points](Rewrite-1.1.8#registering-a-front-end)), and the block classes the block registry holds, which R collects as `blockr_app_options()` collects them today ([R/utils-serve.R#L172-L178](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L172-L178), [blockr.dock R/utils-serve.R#L1-L9](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serve.R#L1-L9)). A file keeps each option's value under its id, and nothing else of it: when R opens the board, it collects the options again and gives each one the file lacks its initial value, while it passes the values the file holds through, and the store drops a value no option claims once every package's migration has run ([Serialization](Rewrite-1.1.4#options)).

Every option is an instance of one type, `Option`, rather than a type of its own, which the package that ships it registers in the client from its JS, keyed by the option's id. R gives each option a class so that methods can dispatch on it, such as the check `validate_board_option.n_rows_option()` ([R/board-option.R#L366-L378](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L366-L378)), and in JS what those methods do is data or a function on the instance, so nothing dispatches on an option's type:

```ts
type Option = {                         // as the package that ships it registers it in the client
  id: OptionId;                         // "n_rows", stable, the key of the option's value in the board
  label: string;                        // "Preview rows", what the user sees
  category: string;                     // "Table options"
  schema: JsonSchema;                   // which values it accepts, such as { enum: ["light", "dark"] }, with a description for a model
  ui: OptionModule;                     // its UI module, which gets an option host
  onChange?(value: Json, api: CoreApi): void;   // what a new value does on the page, such as switching the theme
};
```

The `n_rows` option, for example, is this instance, which blockr.core's JS registers, and the board holds only its value:

```ts
const n_rows: Option = {
  id: "n_rows",
  label: "Preview rows",
  category: "Table options",
  schema: {
    type: "integer",
    minimum: 0,                         // a count, as is_count() checks today
    description: "How many rows of a table a block's output shows",
  },
  ui: nRowsInput,                       // the module blockr.core ships for it
};

// and in the board, with the initial value R gives it: options: { n_rows: 50 }
```

The id says which option it is and never changes, while the label is only what the user sees. Ids are unique: R collects one option per id, keeping the first, as `combine_board_options()` does today ([R/board-options.R#L435-L442](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-options.R#L435-L442)), and the client holds one definition per id. The schema says which values an option takes, with a description for the assistant's model, as a field's schema does ([Board updates](Rewrite-1.1.2#fields)), and the store checks every value a delta sets against it (below). The option's UI module gets an option host with its value ([UI modules in JS](Rewrite-1.1.7)).

The user does not rename an option, so its label, which its definition sets, takes the place of a name. The board's own name, which core's `board_name` option holds today, becomes a field of the board.

### Extending core's objects

A board names the front-end it is made for (above), and every package, the front-end and each board extension alike, adds state of its own to the board as fields, which the package registers with the store and every other package changes as it changes core's objects ([Board updates](Rewrite-1.1.2#fields)). Core's objects hold only core's keys, apart from a block's attributes, which core carries without reading them (above), and what a package keeps about a link or a stack, or about a block where it is no attribute, such as the DAG's positions, is an entry in a field of its own, keyed by the object's id, so that core's commands and the assistant create blocks, links and stacks without knowing any package, and each package fills in its entry for a new object through its field's `expand`, in the same delta. Today the dock board adds views, grids and extensions to the board ([R/dock-board.R#L55-L79](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L55-L79)) and a color to every stack ([R/dock-stack.R#L24-L169](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-stack.R#L24-L169)), since `new_dock_board()` makes each of its stacks a dock stack ([#L171-L192](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-stack.R#L171-L192)), and which fields these become is for the dock's design ([Client-drawn dock and extensions](Rewrite-1.2)). Core validates its own objects, and each field's package validates the field, through the schema it registers, while the store applies deltas to every field alike. Behavior attaches by registration, a front-end under its id ([Front-ends and extension points](Rewrite-1.1.8#registering-a-front-end)) and a field under its own id ([Board updates](Rewrite-1.1.2#fields)), never by dispatch on a class or through JS class inheritance, so the objects stay plain data. Whatever reads only core's objects, such as core's basic front-end, works on a board made for any front-end. Core publishes TypeScript types for all of them, and a JSON Schema of the board generated from them, by which R writes a board ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)), and a package types its fields by adding them to core's `Fields` interface, as a tldraw app types record types of its own ([tldraw store](https://tldraw.dev/sdk-features/store)):

```ts
declare module "@blockr/core" {
  interface Fields {
    "blockr.dag-positions": Record<BlockId, { x: number; y: number }>;   // { a: { x: 120, y: 80 } }
  }
}
```

Core carries a package's state without knowing it, as it does today: `new_dock_board()` passes its views, grids and extensions to `new_board()` as extra components ([blockr.dock R/dock-board.R#L66-L78](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L66-L78)), and `blockr_ser.board()` serializes each of them by dispatch ([R/utils-serdes.R#L218-L231](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L218-L231)). What lives today in the reactive state of the dock's extensions, such as the DAG's positions and layout ([R/ext.R#L37-L47](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/ext.R#L37-L47)), blockr.md's content ([R/md-ext.R#L9-L26](https://github.com/BristolMyersSquibb/blockr.md/blob/32e088884d825813fb7ff0afc7d023df9e70a3b6/R/md-ext.R#L9-L26)) and the assistant's threads ([R/ext-serdes.R#L2-L28](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/ext-serdes.R#L2-L28)), goes into fields of the package it belongs to rather than into the dock's. Of the state packages keep, the board holds what opening, saving and restoring it need, such as the dock's views, their layouts and which view is active, and leaves out what only one person's screen needs, such as the selection or which panel has focus, as [Client-drawn dock and extensions](Rewrite-1.2) has it for the dock, and each extension sorts its own state by the same rule.

A field that refers to blocks stays consistent through the update that removes one, since the [board updates proposal](Rewrite-1.1.2#applying-a-delta) expands a delta through the hook each field registers, with which the dock drops a removed block's panels and the DAG its position, so no field keeps ghost entries, as the dock's grids do today ([R/dock-grid.R#L733-L748](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-grid.R#L733-L748)). A package migrates its state in JS as a whole, its fields, the attributes it keeps on blocks and its options' values, by the version of it that the file records ([Board updates](Rewrite-1.1.2#fields)), as the dock reads the version of blockr.dock that the board's constructor records today as `producer_version` ([blockr.dock R/utils-serdes.R#L98-L131](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L98-L131)). When R opens a board, it builds no R object from a package's fields and hands them to the client as saved, with that version, so a package reads every format it ever wrote in one place, beside its fields' schemas, and its R side only writes its fields for a script's board, while its migration also fills in its state where a board opened in its app lacks it, as the dock gives a core board a default view ([Board updates](Rewrite-1.1.2#opening-a-board)).

### Ids

Every object, the board, a block, a link or a stack, has an id, and all but a link have a name. The id identifies the object, and is the key the board holds a block, a link or a stack under, so none of them repeats it: references and collection keys use it, it never changes, and it is unique within its collection. The name is what the user calls the object: free text the user can change at any time and nothing refers to, so renaming a block changes its name, as today. The client generates ids for new objects, and a board's when it creates the board, in the adjective and animal style of today's `rand_names()` ([R/utils-misc.R#L66-L103](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-misc.R#L66-L103)). An id is any string that is not empty and not made of digits alone, since a JS object, `JSON.parse()` included, puts keys that look like integers first, whatever the order they were inserted in. Nothing else about an id needs a rule: exported code backticks an id that is not a syntactic name, and the client escapes ids in CSS selectors or keeps them out of element ids, while the Shiny input names that [blockr.core#390](https://github.com/BristolMyersSquibb/blockr.core/issues/390) shows breaking are gone, since every message travels through one input ([Wire protocol](Rewrite-1.1.9)). Opening a board with an id made of digits alone fails with an error that names the id.

### What the store checks

The store checks after every delta that ids are unique and well formed, that a link's endpoints exist, its target declares its input, a fixed input takes at most one link and no links form a cycle, as `validate_links()` and the board's checks do today ([R/links-class.R#L308-L368](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/links-class.R#L308-L368), [R/board-class.R#L64-L122](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-class.R#L64-L122)), that a stack names existing blocks and a block sits in at most one stack, and that every option value a delta sets fits its option's schema.

### Objects that cannot be rebuilt

When R opens a board, it drops what it cannot rebuild: a block or option whose package is not installed or no longer has it, as in [blockr.core#386](https://github.com/BristolMyersSquibb/blockr.core/issues/386), or whose definition it does not evaluate, a block saved by today's stack with a closure for its constructor where no block class of its class name is registered, and the fields of a package that is missing, together with the links and stack places that refer to a dropped block. A board made for a front-end whose package is missing opens as one made for core's basic front-end, `blockr.core-basic`, and a stack in a file from today's stack whose constructor R cannot call opens from the name and blocks in its payload, so that only the missing package's fields go, such as the dock's views and its stack colors. R names each dropped object and field, with the package to install, so the client tells the user what did not open, and a board saved afterwards is written without them. The store drops the fields, attributes and option values that no package loaded in the app registered in the same way, once every package's migration has run, and names them with the rest ([Board updates](Rewrite-1.1.2#fields)), and an option that a part requires but no installed package defines is an error naming both, since a package ships the options it requires or depends on the package that does. Today `blockr_deser()` drops blocks only with `deser_on_error = "drop"`, pruning their links and stacks, and logs them without telling the user ([R/utils-serdes.R#L379-L391](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L379-L391), [#L433-L457](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L433-L457)), and a board whose class's package is missing does not open at all, since reading its constructor fails ([#L518-L538](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L518-L538)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's classes, at `da3fcb4`: [`new_block()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L180-L254) with class `c(<class>, "block", "vctrs_vctr", "list")`, no stored version ([R/utils-serdes.R#L124-L142](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L124-L142)) and its state read from the block server at save time ([R/plugin-serdes.R#L138-L156](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-serdes.R#L138-L156)); [`new_link()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/link-class.R#L54-L161); [`new_stack()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/stack-class.R#L47-L78), a character vector of block ids, one stack per block ([R/stacks-class.R#L14-L103](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/stacks-class.R#L14-L103)); [`new_board_option()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L16-L37), with values in `session$userData` ([R/board-options.R#L150-L225](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-options.R#L150-L225)); [`new_board()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-class.R#L38-L62), which takes extra components through `...` and gets an id on restore ([R/utils-serdes.R#L402-L431](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L402-L431)).

The JSON today's `blockr_ser()` writes maps onto the client's board as follows: `object` is the class vector, which the client's board does not keep, since a block takes the registry id its constructor gives instead, the board the front-end its constructor sets, and a stack, a link and an option need no class of their own; a block's `payload` is its state plus `block_name`; `constructor` gives the package and its version, and for a block the constructor that gives its registry id, and for the board its front-end, unless a block's was saved as a closure, which R leaves unread, going by the block's class instead; a stack's `payload` is `{blocks, name}`; a link's is `{from, to, input}`; the options' `payload` is a list of option objects, each with its class (`n_rows_option`, giving the id) and a `payload` holding `value`, `category` and `label`, of which the board keeps the value under the option's id, while the category and label come from the option's definition in the client ([Serialization](Rewrite-1.1.4#options)); and the board's own `version` and `id` sit next to its `payload`, while its name is the value of its `board_name` option. A board with three blocks, three links and a stack, written by blockr.core 0.1.4:

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

The dock's board subclass adds `extensions`, `views` and `grids` to the board ([R/dock-board.R#L55-L79](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L55-L79)): a view lists its panels as `block_panel-<id>` and `ext_panel-<key>` ([R/dock-view.R#L86-L182](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-view.R#L86-L182)), and a grid holds a view's layout ([R/dock-grid.R#L49-L64](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-grid.R#L49-L64)). No package other than blockr.dock subclasses a board or a stack, and none subclasses a link.

The board declares no index signature, so neither its members nor a package's types for its fields need be assignable to `Json`, which `tsc` would demand of an interface under one (TS2411): `Fields` declares none either, and `fields` is typed as `Partial<Fields>` together with a `Record<FieldId, unknown>` for the fields of packages whose types a module does not import.

</details>
