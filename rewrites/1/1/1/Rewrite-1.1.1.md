# Board objects: blocks, links, stacks, board options and board classes
Status: settled on 2026-10-27. Design for [Client-owned board state](Rewrite-1.1).

The first of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)). It covers the objects the client holds for a board, its blocks, links, stacks and board options, how the board names its class and a block its class by registry id, and the properties that a board class adds beside core's. It shapes the store, the TypeScript object in core's JS API that holds the board and through which every change to it passes (sketched in [Board updates](Rewrite-1.1.2), [blockr.core#432](https://github.com/BristolMyersSquibb/blockr.core/issues/432)), the command registry ([blockr.core#433](https://github.com/BristolMyersSquibb/blockr.core/issues/433)), defining block classes ([blockr.core#421](https://github.com/BristolMyersSquibb/blockr.core/issues/421)), exporting the block registry ([blockr.core#426](https://github.com/BristolMyersSquibb/blockr.core/issues/426)), the board's name and id ([blockr.core#427](https://github.com/BristolMyersSquibb/blockr.core/issues/427)), writing a board's JSON in R by schema ([blockr.core#428](https://github.com/BristolMyersSquibb/blockr.core/issues/428)), opening a board in R ([blockr.core#429](https://github.com/BristolMyersSquibb/blockr.core/issues/429)), writing a saved board in the client ([blockr.core#436](https://github.com/BristolMyersSquibb/blockr.core/issues/436)) and core's board options ([blockr.core#439](https://github.com/BristolMyersSquibb/blockr.core/issues/439)), each an item in the Work list of [Client-owned board state](Rewrite-1.1#work). How the board changes, through deltas, commands and undo, is the [board updates proposal](Rewrite-1.1.2), and the exact JSON format with its migrations is the [serialization proposal](Rewrite-1.1.4).

## What must hold

1. A board built in R by `new_board()` and the block, link, stack and board option constructors maps to the client's board and back without losing any of its state, and so does the JSON `blockr_ser()` writes today. An app can start from a saved file in place of a constructor call, as `serve()` takes a file's path today.
2. The board is plain data, so it serializes as is, and every change to it can be written as a delta and undone.
3. A board names its class, as blockr.dock makes boards of a class of its own today, and a board class keeps what it adds in properties of its own, beside core's, which core carries without reading them.
4. A board saved with a package that is not installed opens without the objects that need it, and the user learns which ones were dropped.
5. The board names its blocks' classes by registry id only, and its own class by its R class vector alone, while no other object in it, nor in the file it is saved to, carries an R class, names a constructor or holds a block class's source ([Serialization](Rewrite-1.1.4)).

## Proposal

### What lives where

Each piece of state has one writer. The board is the client's alone, and what R holds about it is either computed from the board at one moment, as a result is, or handed over once, as the opening board is. Neither is ever edited to follow the board, so nothing has to be kept in step with it. The board holds only what changes while the app runs, with the ids and registry ids that say what each value belongs to, while what nothing changes stays out of it: a block class's UI travels in the block registry's entries R sends the client, and a board option's label and the rest of its definition are the client's own, defined by the package that ships the board option.

| Object | Where | Lives | What it is for |
|---|---|---|---|
| Board, with its blocks, links, stacks, board option values and the properties its class adds | The client, in the store | Until another board is opened, and in files | The only copy of what the user built (this proposal) |
| Store | The client, one per board | The page | Holds the board and applies every change to it, with undo ([Board updates](Rewrite-1.1.2)) |
| Command registry | The client | The page | The edits that menus, shortcuts, extensions and the assistant run ([Board updates](Rewrite-1.1.2)) |
| Scheduler | The client | The page | Revisions, statuses, conditions and demand, computed from the board and R's replies ([Evaluation in the client](Rewrite-1.1.10)) |
| Block registry entries | The client | The page | Each block class by registry id, with its UI, inputs and arg specs and the schema of its state that its UI ships, which R sends with the versions of its packages when the client connects and whenever a board opens, for neither side to edit ([Block classes in R](Rewrite-1.1.5#registration)) |
| Board options | The client | The page | Each board option's definition, an `Option`, which the package that ships the board option registers from its JS, for neither side to edit, while the board holds its value ([Board options](#board-options)) |
| Blockr options | The client | The page | The values of the blockr options that core, front-ends and extensions read, each asked of R the first time client code reads it and kept for the page, since a blockr option is fixed for the app, for neither side to edit, while the board holds none of them ([Defining a board in R](Rewrite-1.1.3#blockr-options)) |
| Board classes | The client | The page | Each board class's definition, under its R class name: its parent class, its front-end, the board options it requires and the properties it adds, which the package that ships the class defines in JS, for neither side to edit, while the board holds the properties' values ([The board](#the-board)) |
| Front-end and extensions | The client | The page | Draw the board and work on it through the store, commands, demand and requests, keeping their data in the properties of the board's class ([Front-ends and extension points](Rewrite-1.1.8)) |
| Block registry | R | The process | Each registered block class, a value holding its UI, inputs, `expr`, requests, output and board options, with its constructor and metadata ([Block classes in R](Rewrite-1.1.5)) |
| R board | R | While R converts it | Built by an app script's constructor calls, whose board options R collects and whose block classes it registers, then converted to the client's board and dropped, so it never exists beside the client's board |
| Results | R | Until the client forgets the block | For each block R has evaluated, the revision, value, block expression and registry id of its latest evaluation, with the previous value kept while the next computes. They hold no state, which each evaluation brings, so they cannot fall out of step with the board ([Block classes in R](Rewrite-1.1.5#evaluation)) |
| Saved board | A file | As long as the file | The board, with the versions of the packages that saved it, written by the client and read by R ([Serialization](Rewrite-1.1.4#files)) |

### Objects in R

R holds no copy of the board, so nothing in R has to follow it: an R object either exists only while a board is defined or opened or holds no state, and R reads the current state from the request that needs it.

- An R board, with its blocks, links, stacks and board options, exists only while R converts it to the client's board: the one an app script builds with constructors, whose board options R collects and whose block classes it registers. R hands it to the client as its board and drops it, while a board given as JSON, a saved file, it neither builds nor opens, since the client opens every board ([Board updates](Rewrite-1.1.2#opening-a-board)). Its S3 classes do their work there, in the constructors and in collecting board options, and only the board's class vector reaches the client, in the board's `class`, while the board names block classes by registry id (below).
- A block class is a value, defined once with `new_block_class()` and held by the block registry: its UI, inputs, requests, output and board options, and its `expr`, which checks a state and returns what the block expression is made from, while `block_eval()` runs that expression ([Block classes in R](Rewrite-1.1.5)). Nothing about a class is copied into a block.
- A block, as its constructor returns it, holds its state and name and refers to its class. R builds blocks only where a board is built, in an app script and when a board is opened, and keeps none while the app runs.
- Results are an environment keyed by block id, holding for each block R has evaluated the revision, value, block expression and registry id of its latest evaluation, with the previous value kept while the next computes. They hold no state: an evaluation brings the recipe's state, from which the class's `expr` builds the block expression that `block_eval()` runs, and the coercion its class names makes an output from a result ([Wire protocol](Rewrite-1.1.9#outputs)). R drops a block's results when the client says the block is gone ([Wire protocol](Rewrite-1.1.9)).
- A request carries the current state it needs: an evaluation its recipe ([Wire protocol](Rewrite-1.1.9)), a block class's request the state args its function names, and an output request, or a request of its output class, the values of the board options.

### The board

```ts
type Json = null | boolean | number | string | Json[] | { [key: string]: Json };

interface Board {
  id: string;                           // given by the script or minted by the client, and kept by saving and opening
  class: string[];                      // the R board's class vector, most specific first, as ["dock_board", "board"]
  name: string;                         // "Sales review", which core's board option board_name holds today
  blocks: Record<BlockId, Block>;
  links: Record<LinkId, Link>;
  stacks: Record<StackId, Stack>;
  options: Record<OptionId, Json>;      // each board option's value, { n_rows: 50 }
}                                       // and the properties that its class adds, such as a dock board's views (below)
```

The board holds no class instances, only plain data, so it serializes as is, a delta is a structural change, and undo replays deltas. It names its class in `class`, and a block names its block class by registry id (below), while nothing else in it has a class of its own: a stack and a link have core's properties and nothing else, and a board option is a value under its id. No other object carries an R class vector, and none names a constructor or a package, since the client dispatches on none of them, and neither does the file a board is saved to, which is the board with the versions of the packages that saved it ([Serialization](Rewrite-1.1.4#files)). When the client opens a file, it finds each block's class among the block registry's entries by registry id, and builds the board as the first class in its `class` that a loaded package defines (below), while a file from today's stack, which names constructors instead, is converted to a saved file outside core first ([Serialization](Rewrite-1.1.4#files)).

A board's `class` is the class vector of the R board it comes from, most specific class first, as `["dock_board", "board"]`, which R writes for the board an app script builds, and which the client keeps as it got it and saves back unchanged. A package defines each board class it ships in JS, under its R class name. The definition names the class's parent, its front-end, the board options it requires ([Board options](#board-options)) and the properties it adds beside core's, each with a schema and a default ([Extending core's objects](#extending-cores-objects)), so that the definition and R's class meet at the name, and R declares nothing for it. Core defines `board`, whose front-end is core's basic one, `blockr.core-basic`, and blockr.dock defines `dock_board`, whose front-end is the dock, `blockr.dock-dock` ([Front-ends and extension points](Rewrite-1.1.8#registering-a-front-end)). Opening a board, the client builds the first class in the list that a loaded package defines. So a board of class `["foo_board", "dock_board", "board"]` is built as a dock board where only blockr.dock is loaded, and as a core board where neither is, while a class that exists only in R, such as one a script adds for a method, has no definition and is skipped. The fallback follows the order of the list, and inheritance in JS decides only behavior.

R builds an R board only where an app script defines one, which it converts to JSON once, when `serve()` is called ([Defining a board in R](Rewrite-1.1.3#the-opening-board)). A board given as JSON, a saved file, R never opens: it passes the file `serve()` is given on as it is, and the client opens that one as it opens the one `store.open()` opens ([Board updates](Rewrite-1.1.2#opening-a-board)), having R load the packages the file names ([Wire protocol](Rewrite-1.1.9#opening-a-board)), so that every block's class is registered before a recipe names it:

1. A class defined outside a package is registered only by the script that defines it, so its blocks are dropped and named where it is not (below).
2. A class from an installed package is registered as R loads the package, which registers its classes.
3. A block whose package is not installed, or no longer has its class, is dropped and named (below).

A block is built by its class's constructor only where an app script calls it, while opening a board and evaluating a block build none ([Block classes in R](Rewrite-1.1.5#evaluation)). A board from a constructor call may hold blocks of classes nobody registered too, and R registers those from the class each block refers to, as classes from outside a package, under the ids the defaults below give, before it writes the board as JSON ([Defining a board in R](Rewrite-1.1.3)), so both ways in end with every class registered. R then turns the R board into the client's board and drops it. While the app runs, the client's board is the only board, so no edit changes an R object: R evaluates a block from its recipe with its class's `expr` and `block_eval()`, building no block, and keeps the result in an environment keyed by block id ([Block classes in R](Rewrite-1.1.5#evaluation)), and a request that needs more of the board than the blocks it reads carries it.

Collections are keyed by id and ordered by insertion, as `blockr_ser()` writes them as named payloads. Order matters, since cards follow it and a variadic input takes its links in order, and a JS object keeps insertion order only for keys that do not look like integers, which is why an id may not be made of digits alone (below).

### Blocks

```ts
type Block = {                          // held under its id in board.blocks
  registry_id: RegistryId;              // "blockr.core-head_block"
  state: Record<string, Json>;          // { n: 10, direction: "head" }
  name: string;                         // "Head", today's block_name
  attrs: Record<string, Json>;          // { visible: ["outputs"] }, its attributes, values that are not its state (below)
};
```

A block names its entry in the block registry rather than its constructor. The block registry holds the block class, a value wherever it was defined ([Block classes in R](Rewrite-1.1.5)), while a constructor reference can only name a package's function, and the client needs every class on a board in the block registry anyway, since that is where it gets a class's UI, inputs and arg specs. The dock's sidebar and the assistant create blocks by registry id already ([blockr.dock R/sidebar-block.R#L182-L184](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/sidebar-block.R#L182-L184), [blockr.assistant R/tools-typed.R#L13-L25](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/tools-typed.R#L13-L25)). A block carries no class, and neither does its entry in the block registry, since nothing in the client dispatches on one. Its registry id says which package R loads before the id can resolve, since an id splits at its first `-`, as `asNamespace()` loads a package when a constructor is looked up today ([R/utils-serdes.R#L518-L538](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L518-L538)), and which to install when it is missing. A block R cannot build when it opens a file is dropped and named (below).

A block's state is its constructor's args and nothing else, so calling its class's constructor with the state, its name and its `visible` rebuilds it, but for the attributes other packages keep on it in the client. An attribute is a value kept on every block that is not its state, core's own `visible` among them, which says which of a block's sections show, its inputs and its output, and which a locked board reads ([Wire protocol](Rewrite-1.1.9#locked-boards)), as the dock's card sections today travel as a `visible` field in the block's payload ([blockr.dock R/utils-serdes.R#L12-L33](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L12-L33)): whoever defines it registers it with the store, with a schema and an initial value ([Board updates](Rewrite-1.1.2#board-classes-and-attributes)), a block constructor takes core's `visible` as an argument of its own, while an attribute that another package defines is set in the client, by a command, and core carries it without reading it, so that a block copied or removed takes its attributes along. The name is a property of its own, since every block has one and the client titles cards and panels with it.

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

A block class defined outside a package is the norm in development, demos and examples, and works wherever the script that defines it registers it, as an app script does before its board opens ([Defining a board in R](Rewrite-1.1.3#the-opening-board)). A file holds the blocks of such a class by registry id, as it holds any block, and nothing of the class itself, so the app that saved a file reopens it fully, deployed or not, while a session where the class is not registered drops its blocks and names them, like any block R cannot build (below).

A file holds no class's source, because no form of it reproduces a class in general. Today `blockr_ser()` writes the constructor as a closure ([R/utils-serdes.R#L124-L142](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L124-L142)), which brings its environment along: Shiny sources an app.R into a new environment rather than the global one ([shiny R/shinyapp.R#L486-L494](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/shinyapp.R#L486-L494)), so for a block class defined in an app.R that reads an API key and loads a 3.8 MB data frame, `blockr_ser()` writes 4.0 MB with every block of that class, the key included, while a constructor defined at a script's top level loses the script's globals, since `serialize()` writes the global environment as a reference. The call that defined a class would reproduce it only where it names nothing else of the script, and not where `new_block_class()` is aliased, a field comes from a variable or a function of the script makes the class. A file from today's stack holds such a constructor as a closure, which its conversion outside core leaves unread ([Serialization](Rewrite-1.1.4#files)): a function saved today builds its block from a Shiny server, which the contract of [Block classes in R](Rewrite-1.1.5) replaces, so such a block keeps the name the file records as its registry id, and opens only where a block class of that name is registered, such as one the developer has rewritten to that contract, and is dropped and named otherwise.

### Links

```ts
interface Link {                        // held under its id in board.links
  from: BlockId;                        // "a"
  to: BlockId;                          // "c"
  input: string;                        // "x"
}
```

A link carries no name, as today, and no class, which a link cannot keep even today: the `links()` record keeps each link's fields as columns but drops its class and constructor ([R/links-class.R#L15-L47](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/links-class.R#L15-L47)), and a link read out of it is rebuilt by `new_link()` ([#L277-L292](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/links-class.R#L277-L292)). So every link `blockr_ser()` writes is a plain `link` made by `new_link()`, and so is a link read from a file that names a subclass. A package that keeps more about a link keeps it in a property of a board class, keyed by the link's id (below). Its input is always resolved for a target of fixed arity, so filling in a unary target's only input is the job of the command that adds the link, not of the board. For a variadic target, an empty input appends positionally, in link order, as today ([R/board-server.R#L1215-L1242](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L1215-L1242)).

### Stacks

```ts
interface Stack {                       // held under its id in board.stacks
  name: string;
  blocks: BlockId[];
}
```

### Board options

The board holds each board option's value under its id, which says which board option it is, such as `n_rows`. The value is the board option's state, which a command sets ([Board updates](Rewrite-1.1.2)). The rest of a board option is defined once, in the client, by the package that ships it: its label, its category, the schema of its value, its UI, and what a new value does on the page, such as switching the theme for `dark_mode`, which the board option's `server` does in R today ([R/board-option.R#L572-L582](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L572-L582)) and which R could not describe to the client. A board option comes onto the board through the components that require it. A component defined in JS, a board class, a renderer or a block class's UI module, names the board options it requires in its JS definition, as core's table renderer names `n_rows`. The client adds a component's board options when it first needs the component, each with the `default` of its definition where the board lacks it: a board class's as the board opens, and a renderer's or a UI module's the first time core loads the module on the page, as when it first draws a table. From then on the board holds the value, which a command changes, a save writes and an opening restores. So a board holds no value for a board option that nothing on its page has required, and nothing yet removes the value of one whose component has gone. In R, a board option is its id and the value a script gives it, as `new_n_rows_option(25)` does, and its constructor computes nothing, neither a default from a blockr option, as `new_dark_mode_option(value = blockr_option("dark_mode", NULL))` does today, nor a transform or a check, since its definition in the client holds all of that, and nothing else of a board option crosses the wire. A script gives a board option only to set a value other than its default, and nothing in R decides which board options a board has. A file keeps each board option's value under its id, and nothing else of it, so a board opened from one keeps the values it was saved with, and the store drops a value no board option claims once every package's migration has run ([Serialization](Rewrite-1.1.4#board-options)).

Every board option is an instance of one type, `Option`, rather than a type of its own, which the package that ships it registers in the client from its JS, keyed by the board option's id. R gives each board option a class so that methods can dispatch on it, such as the check `validate_board_option.n_rows_option()` ([R/board-option.R#L366-L378](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L366-L378)), and in JS what those methods do is data or a function on the instance, so nothing dispatches on a board option's type:

```ts
type Option = {                         // as the package that ships it registers it in the client
  id: OptionId;                         // "n_rows", stable, the key of the board option's value in the board
  label: string;                        // "Preview rows", what the user sees
  category: string;                     // "Table options"
  schema: JsonSchema;                   // which values it accepts, such as { enum: ["light", "dark"] }, with a description for a model
  default: Json | (() => Promise<Json>);   // what the client gives the board as it adds the board option, or a function that core calls the first time it adds it
  ui: OptionModule;                     // its UI module, which gets an `OptionHost`
  onChange?(value: Json, api: CoreApi): void;   // what a new value does on the page, such as switching the theme
};
```

The `n_rows` board option, for example, is the instance this constructor makes, which blockr.core's JS registers, taking its default from a blockr option as `new_n_rows_option(value = blockr_option("n_rows", 50L))` does in R today, and the board holds only its value:

```ts
const nRows = (core: CoreApi): Option => ({
  id: "n_rows",
  label: "Preview rows",
  category: "Table options",
  schema: {
    type: "integer",
    minimum: 0,                         // a count, as is_count() checks today
    description: "How many rows of a table a block's output shows",
  },
  default: () => core.blockrOption("n_rows", 50),   // the blockr option n_rows where it is set, else 50
  ui: nRowsInput,                       // the module blockr.core ships for it
});

// and in the board, once a component that requires it has come onto the page: options: { n_rows: 50 }
```

The id says which board option it is and never changes, while the label is only what the user sees. Ids are unique: R collects one board option per id, keeping the first, as `combine_board_options()` does today ([R/board-options.R#L435-L442](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-options.R#L435-L442)), and the client holds one definition per id. The schema says which values a board option takes, with a description for the assistant's model, as the schema of a property that a board class adds does ([Board updates](Rewrite-1.1.2#board-classes-and-attributes)), and the store checks every value a delta sets against it (below), while R writes a value a script gives by the copy of the schema that the board option's package ships beside its startup module ([UI modules in JS](Rewrite-1.1.7#packaging)). The board option's UI module gets an `OptionHost` with its value ([UI modules in JS](Rewrite-1.1.7)). A definition's `default` is a value, or a function that core calls the first time it adds the board option to a board and whose result it keeps, so that a definition takes its default from a blockr option through `CoreApi.blockrOption()` only once a component requires the board option ([Defining a board in R](Rewrite-1.1.3#blockr-options)), and nothing is read for a board option that nothing requires.

The user does not rename a board option, so its label, which its definition sets, takes the place of a name. The board's own name, which core's board option `board_name` holds today, becomes the board's `name`.

### Extending core's objects

A board class adds properties of its own to the board, beside core's, as the dock board adds views, grids and extensions today ([R/dock-board.R#L55-L79](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L55-L79)) and a color to every stack ([R/dock-stack.R#L24-L169](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-stack.R#L24-L169)), since `new_dock_board()` makes each of its stacks a dock stack ([#L171-L192](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-stack.R#L171-L192)). These become properties of the dock board, held as the dock's design has it ([Client-drawn dock and extensions](Rewrite-1.2)). Core carries each such property without reading it: it registers nothing inside it, and checks the property's whole value against the schema that the class's definition gives, after every change, while what sits inside, such as how the dock lays out its views or keeps its extensions' state, is the class's own design. Core's objects hold only core's properties, apart from a block's attributes, which core carries without reading them (above), and what a package keeps about a link, a stack or a block, such as the DAG's positions, sits in a property of a board class, keyed by the object's id. So core's commands and the assistant create blocks, links and stacks without knowing any board class. A change inside a property travels as a patch at a nested path, which the store applies without knowing the property's structure, and the package that defines the class registers the commands that change it ([Board updates](Rewrite-1.1.2#board-classes-and-attributes)). Whatever reads only core's properties, such as core's basic front-end, works on a board of any class. Core publishes TypeScript types for its own objects, and a JSON Schema of the board generated from them, by which R writes a board ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)), and a board class types its properties by extending core's `Board` interface, as the dock would type its board, with illustrative names:

```ts
interface DockBoard extends Board {
  views: Record<ViewId, View>;                                  // the dock's own
  extensions: Record<ExtensionId, Record<string, unknown>>;     // { "blockr.dag-dag": { positions: { a: { x: 120, y: 80 } } } }
}
```

Core carries a board class's properties without knowing them, as it does today: `new_dock_board()` passes its views, grids and extensions to `new_board()` as extra components ([blockr.dock R/dock-board.R#L66-L78](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L66-L78)), and `blockr_ser.board()` serializes each of them by dispatch ([R/utils-serdes.R#L218-L231](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L218-L231)). What lives today in the reactive state of the dock's extensions, such as the DAG's positions and layout ([R/ext.R#L37-L47](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/ext.R#L37-L47)), blockr.md's content ([R/md-ext.R#L9-L26](https://github.com/BristolMyersSquibb/blockr.md/blob/32e088884d825813fb7ff0afc7d023df9e70a3b6/R/md-ext.R#L9-L26)) and the assistant's threads ([R/ext-serdes.R#L2-L28](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/ext-serdes.R#L2-L28)), goes into the state of the extension it belongs to, which the dock board keeps in its `extensions`, rather than into the dock's own properties. Of what a board class and its front-end's extensions keep, the board holds what opening, saving and restoring it need, such as the dock's views, their layouts and which view is active, and leaves out what only one person's screen needs, such as the selection or which panel has focus, as [Client-drawn dock and extensions](Rewrite-1.2) has it for the dock, and each extension sorts its own state by the same rule.

A property that refers to core's objects stays consistent through the change that removes one. Each board class's definition gives core one function, which the store calls with every change it applies and which returns patches for the class's own properties, in the same step ([Board updates](Rewrite-1.1.2#applying-a-delta)). With it the dock drops a removed block's panels, while how the dock lets its extensions keep their state consistent in the same way is the dock's to offer ([Client-drawn dock and extensions](Rewrite-1.2)), so nothing keeps ghost entries, as the dock's grids do today ([R/dock-grid.R#L733-L748](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-grid.R#L733-L748)). A package migrates what it saved in JS as a whole, the properties its board classes add and the states of its block classes' blocks, by the version of it that the file records ([Board updates](Rewrite-1.1.2#board-classes-and-attributes)), as the dock reads the version of blockr.dock that the board's constructor records today as `producer_version` ([blockr.dock R/utils-serdes.R#L98-L131](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L98-L131)). R never opens a board, so the client hands each package's migration what the file holds, as the migrations before it left it, with the version that saved it, and a package reads every format it ever wrote in one place, beside its properties' schemas. Its R side only writes its properties for a script's board, while where a board opened in its app lacks a property of its class, the property's default fills it in, whichever way the board comes in ([Board updates](Rewrite-1.1.2#opening-a-board)).

### Ids

Every object, the board, a block, a link or a stack, has an id, and all but a link have a name. The id identifies the object, and is the key the board holds a block, a link or a stack under, so none of them repeats it: references and collection keys use it, it never changes, and it is unique within its collection. The name is what the user calls the object: free text the user can change at any time and nothing refers to, so renaming a block changes its name, as today. The client mints every id, in the adjective and animal style of today's `rand_names()` ([R/utils-misc.R#L66-L103](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-misc.R#L66-L103)), for the objects and boards it creates and for each object of a board that R sends without one, so that ids come from one place. R mints none: an app script may give an object its id, as it must for a block that a link or a stack refers to, or leave it out, and R keeps the ids it is given and sends an object without one as it is. A board that R sends therefore holds its blocks, links and stacks as arrays, in their order, each entry with its `id` where it has one, and its own `id` and `name` only where it has them ([Wire protocol](Rewrite-1.1.9#handshake)). The client keys each collection by id as it opens the board, minting an id where an entry has none, and names a board without a name after its id, in sentence case, as core's `board_name` board option does today ([R/board-option.R#L285-L296](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L285-L296)), so each session mints its own ids for what the script left out, where `serve()` draws one board id per process today, and a saved file, which the client writes, holds every id. An id is any string that is not empty and not made of digits alone, since a JS object, `JSON.parse()` included, puts keys that look like integers first, whatever the order they were inserted in. Nothing else about an id needs a rule: exported code backticks an id that is not a syntactic name, and the client escapes ids in CSS selectors or keeps them out of element ids, while the Shiny input names that [blockr.core#390](https://github.com/BristolMyersSquibb/blockr.core/issues/390) shows breaking are gone, since every message travels through one input ([Wire protocol](Rewrite-1.1.9)). The store refuses to open a board with an id made of digits alone, with an error that names the id.

### What the store checks

The store checks after every delta that ids are unique and well formed, that a link's endpoints exist, its target declares its input, a fixed input takes at most one link and no links form a cycle, as `validate_links()` and the board's checks do today ([R/links-class.R#L308-L368](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/links-class.R#L308-L368), [R/board-class.R#L64-L122](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-class.R#L64-L122)), that a stack names existing blocks and a block sits in at most one stack, and that every value a delta sets for a board option fits that board option's schema. It also checks that a block's class is in the block registry, since opening a board drops a block whose class it lacks, so that no delta makes a board that no opening would, and that a block, link or stack that a delta adds or changes has core's fields and nothing else, since deltas come from plain JS and from the assistant's tools too. These two look only at what a delta changed: on a board of 1,000 blocks they take 0.4 µs of an `apply()` that takes 3.8 ms, most of it in the checks of the whole board.

### Objects that cannot be rebuilt

When the client opens a board, it drops what the app cannot rebuild: a block whose class the block registry lacks, as when its package is not installed or no longer has the class, as in [blockr.core#386](https://github.com/BristolMyersSquibb/blockr.core/issues/386), or its class comes from no package and is not registered, together with the links and stack places that refer to it, and, once every package's migration has run, every property that the class it builds the board as does not define, and the attributes and board option values that no package loaded in the app registered, as those of a package that is missing ([Board updates](Rewrite-1.1.2#board-classes-and-attributes)). A board whose first class no loaded package defines, as when blockr.dock is missing, is built as the next class in its `class` that one does, as a dock board is built as a core board, so that only what the missing package's class adds goes, such as the dock's views. Its `class` keeps every class, so that the board is built as a dock board again where blockr.dock is installed, with the defaults of the dock's properties. The client names each block it drops with the package to install, which the block's registry id gives, and the class it builds the board as where it skips one, so the user learns what did not open, while it drops properties, attributes and board option values without naming them, which is the business of whoever keeps them, and a board saved afterwards is written without any of them. A board option that something needs but no loaded package defines is an error naming it. Today `blockr_deser()` drops blocks only with `deser_on_error = "drop"`, pruning their links and stacks, and logs them without telling the user ([R/utils-serdes.R#L379-L391](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L379-L391), [#L433-L457](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L433-L457)), and a board whose class's package is missing does not open at all, since reading its constructor fails ([#L518-L538](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L518-L538)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's classes, at `da3fcb4`: [`new_block()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L180-L254) with class `c(<class>, "block", "vctrs_vctr", "list")`, no stored version ([R/utils-serdes.R#L124-L142](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L124-L142)) and its state read from the block server at save time ([R/plugin-serdes.R#L138-L156](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-serdes.R#L138-L156)); [`new_link()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/link-class.R#L54-L161); [`new_stack()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/stack-class.R#L47-L78), a character vector of block ids, one stack per block ([R/stacks-class.R#L14-L103](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/stacks-class.R#L14-L103)); [`new_board_option()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L16-L37), with values in `session$userData` ([R/board-options.R#L150-L225](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-options.R#L150-L225)); [`new_board()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-class.R#L38-L62), which takes extra components through `...` and gets an id on restore ([R/utils-serdes.R#L402-L431](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L402-L431)).

The JSON today's `blockr_ser()` writes maps onto the client's board as follows: `object` is the class vector, which the client's board does not keep, since a block takes the registry id its constructor gives instead, the board the front-end R picks by its class, and a stack, a link and a board option need no class of their own; a block's `payload` is its state plus `block_name`; `constructor` gives the package and its version, and for a block the constructor that gives its registry id, and for the board the constructor whose class picks its front-end, unless a block's was saved as a closure, which R leaves unread, going by the block's class instead; a stack's `payload` is `{blocks, name}`; a link's is `{from, to, input}`; the board options' `payload` is a list of board option objects, each with its class (`n_rows_option`, giving the id) and a `payload` holding `value`, `category` and `label`, of which the board keeps the value under the board option's id, while the category and label come from the board option's definition in the client ([Serialization](Rewrite-1.1.4#board-options)); and the board's own `version` and `id` sit next to its `payload`, while its name is the value of its `board_name` board option. A board with three blocks, three links and a stack, written by blockr.core 0.1.4:

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

The board declares no index signature, so neither its members nor a board class's types for its properties need be assignable to `Json`, which `tsc` would demand of an interface under one (TS2411), and code that does not import a class's types reads its properties as `unknown`.

</details>
