# Serialization of the client-owned board
Status: draft. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how a board is written to a file and read back, and how state values travel between the client and R. It builds on the [document model](Rewrite-1.1.1) and shapes the loader ([blockr.core#402](https://github.com/BristolMyersSquibb/blockr.core/issues/402)), the registry export ([blockr.core#396](https://github.com/BristolMyersSquibb/blockr.core/issues/396)) and the JSON question that the protocol issue leaves open ([blockr.core#393](https://github.com/BristolMyersSquibb/blockr.core/issues/393)).

## What must hold

1. Boards saved today open in the new stack, for block types that have been ported, through `blockr_deser()` and the migrations packages already have ([blockr.core#402](https://github.com/BristolMyersSquibb/blockr.core/issues/402)).
2. A board saved by the new stack is written in the browser, so saving needs no R and works while R is busy or gone.
3. The client's board holds state values its UI can use as they are, so an arg that is a vector is always an array, whatever its length.
4. Opening a file drops what R cannot rebuild and names it, so that nothing goes missing silently.
5. A file written by the new stack keeps the shape of today's, so that one reader opens both, and departs from it only where this proposal gives a reason.

## Today

The `blockr_ser()` function returns R lists, and the JSON is up to the caller. Core's own download and upload write them with typedjson ([R/plugin-serdes.R#L76-L78](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-serdes.R#L76-L78), [#L179-L181](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-serdes.R#L179-L181)), which writes a length-one vector bare ([format](https://github.com/nbenn/typedjson/blob/371144d1170eb738395e85c875c368fe8e787b43/README.md)), while blockr.session writes with jsonlite's defaults, which keep it in an array, and reads with `jsonlite::fromJSON()` ([R/rack.R#L249-L254](https://github.com/BristolMyersSquibb/blockr.session/blob/5f9b8e6aff54a58f84d2658963194c60e8a4262a/R/rack.R#L249-L254), [#L469-L473](https://github.com/BristolMyersSquibb/blockr.session/blob/5f9b8e6aff54a58f84d2658963194c60e8a4262a/R/rack.R#L469-L473)). A one-block stack therefore comes out as `"blocks": "a"` in one file and `"blocks": ["a"]` in the other, and JSON written with length-one vectors bare is what broke the dock's layout restore in [blockr.dock#91](https://github.com/BristolMyersSquibb/blockr.dock/issues/91).

## Proposal

### Files

A saved board keeps the shape `blockr_ser()` writes today: every object, the board, its blocks, links, stacks and options and the collections that hold them, is an `object`, its class vector, a `payload`, its constructor's args, and a `constructor`, the function with its package and that package's version at save time ([R/utils-serdes.R#L124-L142](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L124-L142)). A file thus says how R calls the constructors that rebuild the board, as a startup script does ([Document model](Rewrite-1.1.1)). It is not the client's document: R turns a file into the document when it opens it ([Board updates](Rewrite-1.1.2)), and the client writes a file from the document and the registry export, which carries the constructor of every block type, or the definition of one defined outside a package, and of every board, stack, link and option class ([blockr.core#396](https://github.com/BristolMyersSquibb/blockr.core/issues/396)). A board subclass adds its own components as further nodes of the board's payload, in the same shape, as a dock board writes `extensions`, `views` and `grids` next to `blocks`, `links`, `stacks` and `options` today, each extension with its class, its state and its constructor ([blockr.dock R/utils-serdes.R#L47-L95](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L47-L95)).

A file written by the new stack departs from today's in five places:

- A `format` field gives the version of the file format. Today's files lack it, so the reader tells the two apart.
- A block type defined outside a package has a `definition` in place of the serialized closure today's files hold: the code the type was defined by, wrapped in `block_constructor()`, as a string that evaluates to its constructor ([Document model](Rewrite-1.1.1#block-types-outside-a-package)).
- An option's payload holds its value, named after its constructor's arguments as today, and no longer its category and label, which its constructor supplies.
- Links and the board carry a `name`, since every object has one ([Document model](Rewrite-1.1.1)): a link's sits in its payload, and the board's next to its `id`, in place of the `board_name` option.
- Class vectors leave out `vctrs_vctr`, `vctrs_rcrd` and `list`, which only R's containers need: `blockr_deser()` dispatches on `blocks`, `link` or `block` without them, and the client has no R container classes to write.

```json
{
  "format": 1,
  "object": "board",
  "payload": {
    "blocks": {
      "object": "blocks",
      "payload": {
        "a": {
          "object": ["dataset_block", "data_block", "block"],
          "payload": { "dataset": "iris", "package": "datasets", "block_name": "Iris" },
          "constructor": { "object": "blockr_ctor", "constructor": "new_dataset_block", "package": "blockr.core", "version": "0.1.4" }
        },
        "b": {
          "object": ["my_block", "transform_block", "block"],
          "payload": { "n": 3, "block_name": "Mine" },
          "constructor": { "object": "blockr_ctor", "definition": "blockr.core::block_constructor(blockr.core::block_type(\"my_block\", parent = blockr.core::transform_block, inputs = \"data\", state = function(n = 3L) list(n = n), expr = quote(utils::head(.(data), n = .(n)))))" }
        }
      }
    },
    "links": {
      "object": "links",
      "payload": {
        "ab": {
          "object": "link",
          "payload": { "from": "a", "to": "b", "input": "data", "name": "" },
          "constructor": { "object": "blockr_ctor", "constructor": "new_link", "package": "blockr.core", "version": "0.1.4" }
        }
      }
    },
    "stacks": { "object": "stacks", "payload": {} },
    "options": {
      "object": "board_options",
      "payload": [
        {
          "object": ["n_rows_option", "board_option"],
          "payload": { "value": 50 },
          "constructor": { "object": "blockr_ctor", "constructor": "new_n_rows_option", "package": "blockr.core", "version": "0.1.4" }
        }
      ]
    }
  },
  "constructor": { "object": "blockr_ctor", "constructor": "new_board", "package": "blockr.core", "version": "0.1.4" },
  "version": "0.1.4",
  "id": "curious_otter",
  "name": "Sales review"
}
```

Writing one is `JSON.stringify()` in the browser and reading one `JSON.parse()`. Opening one goes through R, as every opening of a board does ([Board updates](Rewrite-1.1.2)), whether `store.open()` sends it, the `hello` after R restarts or `serve()` given its path: R reads files of both stacks with `blockr_deser()`. On the way it registers every block's type, from the type's definition where the `load_definitions` option allows it and no type of the block's class is registered, or from the constructor of an installed package, which it loads. It leaves unread the closures today's files hold, drops what it cannot build ([Document model](Rewrite-1.1.1#the-board)) and runs the migrations below. Where a board is saved, to a download, Connect or a draft, is session management's ([Session management extension](Rewrite-1.6)): core owns what a saved board is, not saving it.

### State values between the client and R

The client's board holds state as its UI wrote it, plain JSON. R decodes it with the one decoding [blockr.core#393](https://github.com/BristolMyersSquibb/blockr.core/issues/393) settles, and a block type's author writes its `validate` and `interpolate` against that decoding, as a Shiny author writes against an input's value, so the arg specs describe args for LLMs and tools and convert nothing ([Client-owned board state](Rewrite-1.1)). R writes state only where it builds it: for an app's opening board ([Defining a board in R](Rewrite-1.1.3)), for a board it opens, as it migrates blocks saved by older versions of their types ([Board updates](Rewrite-1.1.2)), and for files from today's stack ([blockr.core#402](https://github.com/BristolMyersSquibb/blockr.core/issues/402)).

### Migrations

A block saved by an older version of its type migrates through the `blockr_deser()` methods its package has, keyed by the block's class and by the package version its `constructor` records, such as blockr.dplyr's sixteen ([R/legacy-deser.R#L30-L310](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/bdac6b38f7097425bfe96883032531cc919f6ee7/R/legacy-deser.R#L30-L310)). R runs them while it opens the board ([Board updates](Rewrite-1.1.2)), since the methods and the constructors live in R. A field migrates through the package that registers it, in JS, keyed by the version of that package the file records, as the dock's fields are by the version of blockr.dock the board's `constructor` records, and the dock's conversion of today's grids moves to the client, as [Client-drawn dock and extensions](Rewrite-1.2) has it.

### Options

A saved board holds each option with its value and its constructor, as it holds a block, so R rebuilds the options a block package or an extension ships as it rebuilds blocks, and the client's document holds them as objects, with the labels and categories their constructors give them ([Document model](Rewrite-1.1.1)). A file from today's stack has its categories and labels ignored, since an option's constructor supplies them.

### Objects that cannot be rebuilt

R drops, when it opens a file, every object it cannot rebuild, because the package its constructor names is not installed or no longer has the constructor, as in [blockr.core#386](https://github.com/BristolMyersSquibb/blockr.core/issues/386), or R does not evaluate its definition, or it holds a closure from today's stack and no type of its class is registered, together with the links and stack places that refer to a dropped block, and the fields of a package that is missing. It names each dropped object, with the package to install, so the client tells the user what did not open, and a board saved afterwards is written without them ([Document model](Rewrite-1.1.1)).

## Open questions

- How the fields packages register map onto the nodes a file holds, such as the DAG's positions onto the `positions` of its extension in the dock's `extensions`, which the loader and the client's writer both need: through a hook each package registers beside its fields, or by a convention, such as an extension's fields being its constructor's args ([Board updates](Rewrite-1.1.2#fields)).
- How R writes a length-one vector where it builds state, since R has no scalars: always as an array, leaving a scalar arg's UI to unwrap it; by the type an arg spec declares, which shapes the JSON without checking anything; or as typedjson, whose integer markers and tags `JSON.parse()` drops.
