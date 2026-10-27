# Document model for the client-owned board
Status: draft. Design for [Client-owned board state](Doc-1.1).

The first of the API proposals for the client-owned board ([Client-owned board state](Doc-1.1)). It covers the objects the client holds for a board, its blocks, links, stacks and options, how a block names its type through the registry, and how packages extend these objects. It shapes the store, the TypeScript object in core's JS API that holds the board and through which every change to it passes ([blockr.core#394](https://github.com/BristolMyersSquibb/blockr.core/issues/394), sketched in [Board updates](Doc-1.1.2)), the registry export ([blockr.core#396](https://github.com/BristolMyersSquibb/blockr.core/issues/396)) and the loader ([blockr.core#402](https://github.com/BristolMyersSquibb/blockr.core/issues/402)). How the board changes, through deltas, commands and undo, is the [board updates proposal](Doc-1.1.2), and the exact JSON format with its migrations is the [serialization proposal](Doc-1.1.4).

## What must hold

1. A board built in R by `new_board()` and the block, link, stack and option constructors maps to the client's board and back without loss, and so does the JSON `blockr_ser()` writes today.
2. The board is plain data, so it serializes as is, and every change to it can be written as a delta and undone.
3. Packages extend core's objects by class, as blockr.dock extends boards and stacks today, and keep state of their own in the board.
4. A board saved with a package that is not installed opens without the objects that need it, and the user learns which ones were dropped.
5. The board names block types by registry id only, while the file it is saved to names each object's constructor, as today, and holds the source of block types defined outside a package, which development, demos and examples rely on ([Serialization](Doc-1.1.4)).

## Proposal

### What lives where

Each piece of state has one writer. The board is the client's alone, and what R holds about it is either computed from one version of it, as a result is, or handed over once, as the opening board is. Neither is ever edited to follow the board, so nothing has to be kept in step with it.

| Object | Where | Lives | What it is for |
|---|---|---|---|
| Board, with its blocks, links, stacks and options | The client, in the store | Until another board is opened, and in files | The only copy of what the user built (this proposal) |
| Store | The client, one per board | The page | Holds the board and applies every change to it, with undo ([Board updates](Doc-1.1.2)) |
| Command registry | The client | The page | The edits that menus, shortcuts, extensions and the assistant run ([Board updates](Doc-1.1.2)) |
| Scheduler | The client | The page | Versions, statuses, conditions and demand, computed from the board and R's replies ([Evaluation in the client](Doc-1.1.10)) |
| Registry export | The client | The page | Block types by registry id, with their UIs, inputs, arg specs, classes and constructors, and the UIs and constructors of option, board, stack and link classes, as R sends them when the client connects and when a board is opened, for neither side to edit ([blockr.core#396](https://github.com/BristolMyersSquibb/blockr.core/issues/396)) |
| Front-end and extensions | The client | The page | Draw the board and work on it through the store, commands, demand and requests, keeping their own state in the board ([Front-ends and extension points](Doc-1.1.8)) |
| Block registry | R | The process | Each registered block type, a value holding its UI, inputs, requests, options and the functions that evaluate its blocks, with its constructor and metadata ([Block types in R](Doc-1.1.5)) |
| R board | R | While a board is opened | Built from a constructor call or a file to serve the app, collect options and the registry, migrate and convert, then handed to the client as its board and dropped, so it never exists beside the client's board |
| Results | R | Until the client forgets the block | For each block R has evaluated, the version, value and expression of its latest evaluation, with the previous value kept while the next computes. They hold no state, which each evaluation brings, so they cannot fall out of step with the board ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)) |
| Saved board | A file | As long as the file | Today's `blockr_ser()` shape with each object's constructor, written by the client and read by R ([Serialization](Doc-1.1.4)) |

### Objects in R

R holds no copy of the board, so nothing in R has to follow it: an R object either exists only while a board is opened or holds no state, and R reads the current state from the request that needs it.

- An R board, with its blocks, links, stacks and options, exists only while a board is opened. R builds it with the constructors a startup script or a file names, uses it to serve the app, collect options and the registry, migrate and convert, hands it to the client as its board and drops it ([Board updates](Doc-1.1.2)).
- A block type is a value, defined once with `block_type()` and held by the registry: its UI, inputs, requests and options, and the functions that validate a state, build the expression and evaluate it ([Block types in R](Doc-1.1.5)). Nothing about a type is copied into a block.
- A block, as its constructor returns it, holds its state and name and refers to its type. R builds blocks only where a board is built, in an app script and when a board is opened, and keeps none while the app runs.
- Results are an environment keyed by block id, holding for each block R has evaluated the version, value and expression of its latest evaluation, with the previous value kept while the next computes. They hold no state: an evaluation brings the recipe's state, which the type's `validate` checks, `interpolate` builds the expression from and `evaluate` runs, and the type's `output` describes a result ([blockr.core#401](https://github.com/BristolMyersSquibb/blockr.core/issues/401)). R drops a block's results when the client says the block is gone ([Wire protocol](Doc-1.1.9)).
- A request carries the current state it needs: an evaluation its recipe ([Wire protocol](Doc-1.1.9)), a block type's request the state args its function names, and an output request the board's option values.

### The board

```ts
type Json = null | boolean | number | string | Json[] | { [key: string]: Json };

interface Board {
  id: string;                           // set when the board is created, and kept by saving and opening
  name: string;                         // "Sales review", which core's board_name option holds today
  class: string[];                      // ["dock_board", "board"]
  blocks: Record<BlockId, Block>;
  links: Record<LinkId, Link>;
  stacks: Record<StackId, Stack>;
  options: Record<OptionId, Option>;
  [field: string]: Json;                // fields a subclass adds, such as the dock's views and grids
}
```

The board holds no class instances, only plain data, so it serializes as is, a delta is a structural change, and undo replays deltas. The board, its stacks and its links carry their R class vector, without the vctrs internals, and a block carries its registry id instead. None of them names a constructor or a package: the file a board is saved to records each object's constructor, with its package and that package's version at save time, as `blockr_ser()` does today, which is what migrations key on, and R maps a block's constructor to its registry entry when it opens the file ([Serialization](Doc-1.1.4)). JS dispatches on the class vector the way S3 does.

R builds an R board only to open one, at startup and whenever `store.open()` opens another ([Board updates](Doc-1.1.2)), and builds the same R board from a saved board as from a constructor call, since `serve()` dispatches on it and `blockr_app_options()` reads its class and its blocks ([R/utils-serve.R#L172-L178](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L172-L178)). It reads the file with `blockr_deser()`, which dispatches on each object's class ([R/utils-serdes.R#L291-L301](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L291-L301)) and calls the constructor the file names, loading its package, as today, and registers the block types the file defines (below). A block is built by the constructor its file names when R opens a file, while an evaluation builds none ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)). A board from a constructor call may hold blocks of types nobody registered, and R registers those from the constructor each block carries, under the ids the defaults below give, while it builds the opening board, so both ways in end with every type registered. R then turns the board into the client's document and drops it. While the app runs, the client's board is the only board, so no edit changes an R object: R evaluates a block from its recipe with its type's `validate`, `interpolate` and `evaluate`, building no block, and keeps the result in an environment keyed by block id ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400), [Block types in R](Doc-1.1.5)), and a request that needs more of the board than the blocks it reads carries it.

Collections are keyed by id and ordered by insertion, as `blockr_ser()` writes them as named payloads. Order matters, since cards follow it and a variadic input takes its links in order, and a JS object keeps insertion order only for keys that do not look like integers, which is why an id may not be made of digits alone (below).

### Blocks

```ts
interface Block {
  registry_id: RegistryId;              // "blockr.core-head_block"
  state: Record<string, Json>;          // { n: 10, direction: "head" }
  name: string;                         // "Head", today's block_name
}
```

A block names its registry entry rather than its constructor. The registry holds the block type, a value wherever it was defined ([Block types in R](Doc-1.1.5)), while a constructor reference can only name a package's function, and the client needs every type on a board in the registry anyway, since the export ([blockr.core#396](https://github.com/BristolMyersSquibb/blockr.core/issues/396)) is where it gets a type's UI, inputs and arg specs. The dock's sidebar and the assistant create blocks by registry id already ([blockr.dock R/sidebar-block.R#L182-L184](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/sidebar-block.R#L182-L184), [blockr.assistant R/tools-typed.R#L13-L25](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/tools-typed.R#L13-L25)). A block carries no class, since the registry export has the classes of each entry. The constructor a block's file names says which package R loads before the block's registry id can resolve, as `asNamespace()` loads it when the constructor is looked up today ([R/utils-serdes.R#L518-L538](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L518-L538)), and which to install when it is missing. A block R cannot build when it opens a file is dropped and named (below).

A block's state is its constructor's args and nothing else, so calling its type's constructor with the state and its name rebuilds it. What another package keeps about a block goes into the fields its board subclass adds, keyed by the block's id: the dock's card sections, which today travel as a `visible` field in the block's payload ([blockr.dock R/utils-serdes.R#L12-L33](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L12-L33)), move to the dock board's fields. The name is a field of its own, since every block has one and the client titles cards and panels with it.

A block's state is part of the board and its status is not, because the board holds what someone wrote, while the scheduler holds what is computed from it, beside the board and keyed by block id ([Evaluation in the client](Doc-1.1.10)). Both change while the app runs, so what separates them is where they come from:

| | State | Status, version and result |
|---|---|---|
| Written by | The user or the assistant, through a command | The scheduler, from R's replies |
| Can be recomputed | No, it is the source | Yes, by evaluating again |
| Saved in a file | Yes | No |
| Undone | Yes | No |
| Sent to a collaborator | Yes | No, since results are per session |

A spreadsheet draws the same line between the formula in a cell and the value it shows, and today's R stack does too, keeping a block's result and status in the board server's reactives rather than on the block. Code that draws a block need not see the split, since the React SDK can hand a block's UI one object with its state, name and status ([blockr.core#399](https://github.com/BristolMyersSquibb/blockr.core/issues/399)).

### Registry ids

A registry id is `{pkg}-{name}`, such as `blockr.core-head_block`: the package is the one the constructor lives in, and the name is unique within it, which `register_block()` checks. A package name holds only letters, digits and dots, so an id splits at its first `-`, and two packages that do not know of each other cannot produce the same id. The name defaults to the constructor's name without `new_`, which a namespace keeps unique, and `uid` sets it for a package that renames a constructor and wants its saved boards to keep working. For the 46 entries that blockr.core, blockr.dplyr, blockr.dm, blockr.ggplot and blockr.io register, only the prefix is new, since each uid equals its constructor's name without `new_` and each entry's package is its constructor's. A type registered outside a package has the name alone as its id, which cannot equal a package's and only needs to be unique within one process, and since a function object comes without a name, its name defaults to the block's class.

R finds the entry of a block it holds by the type the block refers to, where `registry_id_from_block()` goes by class today ([R/block-registry.R#L304-L318](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-registry.R#L304-L318)), so each type has one entry ([Block types in R](Doc-1.1.5)).

### Block types outside a package

A block type defined outside a package is the norm in development, demos and examples, and the file a board is saved to keeps such types working: a block of such a type is saved with a definition in place of its constructor's name, a string of R code that evaluates to the constructor: its type's value written as R source, wrapped in `block_constructor()` ([Serialization](Doc-1.1.4), [Block types in R](Doc-1.1.5)). R registers the type when it opens the file, and the client writes the definition from the registry export, which carries each such type's source. A definition holds the source text and never the closure, which brings its environment along: Shiny sources an app.R into a new environment rather than the global one ([shiny R/shinyapp.R#L486-L494](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/shinyapp.R#L486-L494)), so for a block type defined in an app.R that reads an API key and loads a 3.8 MB data frame, `blockr_ser()` writes 4.0 MB with every block of that type today ([R/utils-serdes.R#L124-L142](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L124-L142)), the key included.

R evaluates a definition only where no type of the block's class is registered, so a block type the app registers wins over the copy in the file, and only when the `load_definitions` option allows it, which it does by default in an interactive session, so a deployment evaluates no code from a file unless it opts in. Where R does not evaluate it, the type's blocks are dropped and named like any block R cannot build. A file from today's stack holds such a constructor as a closure, which the loader ([blockr.core#402](https://github.com/BristolMyersSquibb/blockr.core/issues/402)) leaves unread: a function saved today builds its block from a Shiny server, which the contract of [Block types in R](Doc-1.1.5) replaces, so the loader looks the ported type up by the class the file records, which is the id such a type takes by default.

### Links

```ts
interface Link {
  class: string[];                      // ["link"]
  name: string;                         // "", until the user names it
  from: BlockId;                        // "a"
  to: BlockId;                          // "c"
  input: string;                        // "x"
  [field: string]: Json;                // fields a subclass adds
}
```

A link carries its class, so a package can extend links as it extends stacks, although none does today, and a name, empty until the user gives it one. In R, the `links()` record keeps only `from`, `to` and `input` ([R/links-class.R#L15-L47](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/links-class.R#L15-L47)), so links need it to keep each link's class and name, and the fields a subclass adds. Its input is always resolved for a target of fixed arity, so filling in a unary target's only input is the job of the command that adds the link, not of the board. For a variadic target, an empty input appends positionally, in link order, as today ([R/board-server.R#L1215-L1242](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L1215-L1242)).

### Stacks

```ts
interface Stack {
  class: string[];                      // ["dock_stack", "stack"]
  name: string;
  blocks: BlockId[];
  [field: string]: Json;                // fields a subclass adds, such as the dock stack's color
}
```

### Options

```ts
interface Option {
  class: string[];                      // ["n_rows_option", "board_option"]
  value: Json;                          // 50
  label: string;                        // "Preview rows"
  category: string;                     // "Table options"
}
```

An option is an object like a block or a stack. Its class says which option it is, gives its id, as `n_rows_option` gives `n_rows`, and dispatches its UI, which the registry export carries per class ([blockr.core#396](https://github.com/BristolMyersSquibb/blockr.core/issues/396)). Its value is its state, which a command sets ([Board updates](Doc-1.1.2)). Its label and category are the static attributes its constructor gave it, as `new_n_rows_option(value, category, label)` takes them, which R sets when it builds the board and nothing changes afterwards. The board holds the options R collects for it, those of its class, its extensions and the block types the registry holds, as `blockr_app_options()` collects them today ([R/utils-serve.R#L172-L178](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L172-L178), [blockr.dock R/utils-serve.R#L1-L9](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serve.R#L1-L9)). A file keeps each option's value and constructor, and the constructor supplies the rest when R opens the board again ([Serialization](Doc-1.1.4)).

An option's id, its key in `options`, says which setting it is, and its class what kind of setting, which dispatches its UI. Today `new_board_option()` derives the class from the id, so each class has one option, but nothing in the board relies on that. The user does not rename an option, so its label, which its constructor sets, takes the place of a name. The board's own name, which core's `board_name` option holds today, becomes a field of the board.

### Extending core's objects

Packages extend core's objects by class, as in R. A subclass prepends its class and may add fields of its own, as `dock_stack` adds a color ([R/dock-stack.R#L24-L169](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-stack.R#L24-L169)), `dock_board` adds views, grids and extensions ([R/dock-board.R#L55-L79](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L55-L79)), and a link subclass would add its own. Core validates its own fields, and the subclass validates the ones it adds, through a schema it registers. The store keeps fields it does not own and applies deltas to them. Behavior attaches by dispatch on the class vector, S3 style, through generics later proposals define, such as how a stack is drawn and what a new one defaults to, never through JS class inheritance, so the objects stay plain data. Core publishes TypeScript types for all of them, and a package types its subclass with an interface of its own:

```ts
interface DockBoard extends Board {
  views: DockViews;
  grids: DockGrids;
  extensions: DockExtensions;
}
```

Core carries a subclass's state without knowing it, as it does today: `new_dock_board()` passes its views, grids and extensions to `new_board()` as extra components ([blockr.dock R/dock-board.R#L66-L78](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L66-L78)), and `blockr_ser.board()` serializes each of them by dispatch ([R/utils-serdes.R#L218-L231](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L218-L231)). The dock's board takes what lives today on its subclass or in its extensions' reactive state: its views, grids and card sections, the DAG's positions and layout ([R/ext.R#L37-L47](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/ext.R#L37-L47)), blockr.md's content ([R/md-ext.R#L9-L26](https://github.com/BristolMyersSquibb/blockr.md/blob/32e088884d825813fb7ff0afc7d023df9e70a3b6/R/md-ext.R#L9-L26)) and the assistant's threads ([R/ext-serdes.R#L2-L28](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/ext-serdes.R#L2-L28)), the last three through the dock's extensions, since [Client-drawn dock and extensions](Doc-1.2) makes the dock "the one extension mechanism, since core has none". Of that state, the board holds only what everyone who opens it shares, such as the views and their layouts, and leaves out what belongs to one person's screen, such as which view is active, the selection or which panel has focus, as [Client-drawn dock and extensions](Doc-1.2) has it for the dock, and each extension sorts its own state by the same rule.

A field that refers to blocks stays consistent through the update that removes one, since the [board updates proposal](Doc-1.1.2) expands a delta through a hook dispatched on the board's class, through which the dock drops a removed block's panels and passes the delta on to its extensions, so no field keeps ghost entries, as the dock's grids do today ([R/dock-grid.R#L733-L748](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-grid.R#L733-L748)). The dock migrates its fields by the version of blockr.dock that the board's constructor records in its file ([Serialization](Doc-1.1.4)), which it reads today as `producer_version` ([blockr.dock R/utils-serdes.R#L98-L131](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L98-L131)), and a board restored from JSON hands them back to `new_dock_board()` as the arguments they came from.

### Ids

Every object, the board, a block, a link or a stack, has an id and a name. The id identifies the object: references and collection keys use it, it never changes, and it is unique within its collection. The name is what the user calls the object: free text the user can change at any time and nothing refers to, so renaming a block changes its name, as today. The client generates ids for new objects, and a board's when it creates the board, in the adjective and animal style of today's `rand_names()` ([R/utils-misc.R#L66-L103](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-misc.R#L66-L103)). An id is any string that is not empty and not made of digits alone, since a JS object, `JSON.parse()` included, puts keys that look like integers first, whatever the order they were inserted in. Nothing else about an id needs a rule: exported code backticks an id that is not a syntactic name, and the client escapes ids in CSS selectors or keeps them out of element ids, while the Shiny input names that [blockr.core#390](https://github.com/BristolMyersSquibb/blockr.core/issues/390) shows breaking are gone, since every message travels through one input ([Wire protocol](Doc-1.1.9)). Opening a board with an id made of digits alone fails with an error that names the id.

### What the store checks

The store checks after every delta that ids are unique and well formed, that a link's endpoints exist, its target declares its input, a fixed input takes at most one link and no links form a cycle, as `validate_links()` and the board's checks do today ([R/links-class.R#L308-L368](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/links-class.R#L308-L368), [R/board-class.R#L64-L122](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-class.R#L64-L122)), and that a stack names existing blocks and a block sits in at most one stack.

### Objects that cannot be rebuilt

When R opens a board, it drops what it cannot rebuild: a block, link, stack or option whose package is not installed, whose package no longer has its constructor, as in [blockr.core#386](https://github.com/BristolMyersSquibb/blockr.core/issues/386), or whose definition it does not evaluate, and the fields a board subclass adds when its package is missing, together with the links and stack places that refer to a dropped block. It names each dropped object, with the package to install, so the client tells the user what did not open, and a board saved afterwards is written without them. Today `blockr_deser()` drops blocks only with `deser_on_error = "drop"`, pruning their links and stacks, and logs them without telling the user ([R/utils-serdes.R#L379-L391](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L379-L391), [#L433-L457](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L433-L457)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's classes, at `da3fcb4`: [`new_block()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L180-L254) with class `c(<class>, "block", "vctrs_vctr", "list")`, no stored version ([R/utils-serdes.R#L124-L142](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L124-L142)) and its state read from the block server at save time ([R/plugin-serdes.R#L138-L156](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-serdes.R#L138-L156)); [`new_link()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/link-class.R#L54-L161); [`new_stack()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/stack-class.R#L47-L78), a character vector of block ids, one stack per block ([R/stacks-class.R#L14-L103](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/stacks-class.R#L14-L103)); [`new_board_option()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L16-L37), with values in `session$userData` ([R/board-options.R#L150-L225](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-options.R#L150-L225)); [`new_board()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-class.R#L38-L62), which takes extra components through `...` and gets an id on restore ([R/utils-serdes.R#L402-L431](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L402-L431)).

The JSON `blockr_ser()` writes maps onto the client's board as follows: `object` is the class vector, less `vctrs_vctr`, `vctrs_rcrd` and `list`, which a board, a stack and a link keep and a block exchanges for its registry id; a block's `payload` is its state plus `block_name`; `constructor` gives the package and its version, and for a block the constructor that finds its registry entry, unless it was saved as a closure, which the loader reads by class instead; a stack's `payload` is `{blocks, name}`; a link's is `{from, to, input}`; the options' `payload` is a list of option objects, each with its class (`n_rows_option`, giving the id) and a `payload` holding `value`, `category` and `label`, which become the board's option objects; and the board's own `version` and `id` sit next to its `payload`, while its name is the value of its `board_name` option. A board with three blocks, three links and a stack, written by blockr.core 0.1.4:

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

</details>
