# Serialization of the client-owned board
Status: draft. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how a board is written to a file and read back, and how state values travel between the client and R. It builds on the [board objects proposal](Rewrite-1.1.1), which says what the board holds, and shapes opening boards in R, exporting the block registry, writing saved boards in the client and the JSON decoding of the wire protocol document, each an item in the Work list of [Client-owned board state](Rewrite-1.1#work). How R opens a board is the [board updates proposal](Rewrite-1.1.2#opening-a-board), and where a board is saved, to a download, Connect or a draft, is session management's ([Session management as a client extension](Rewrite-1.6)): core owns what a saved board is, not saving it.

## What must hold

1. Boards written by today's `blockr_ser()` open in the new stack, with the dock's views and layouts and the DAG's positions, for block types that have been ported, through `blockr_deser()` and the migrations packages already have, as condition 4 of [State in JS](Rewrite-1#what-must-hold) asks.
2. A board saved by the new stack is written in the browser, so saving needs no R and works while R is busy or gone.
3. The client's board holds state values its UI can use as they are, so an arg that is a vector is always an array, whatever its length.
4. A file written by the new stack keeps the shape of today's, so that one reader opens both, and departs from it only where this proposal gives a reason.

## Today

The `blockr_ser()` function returns R lists, and the JSON is up to the caller. Core's own download and upload write them with typedjson ([R/plugin-serdes.R#L76-L78](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-serdes.R#L76-L78), [#L179-L181](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-serdes.R#L179-L181)), which writes a length-one vector bare ([format](https://github.com/nbenn/typedjson/blob/371144d1170eb738395e85c875c368fe8e787b43/README.md)), while blockr.session writes with `jsonlite::write_json()`, which keeps it in an array, and reads with `jsonlite::fromJSON()`, simplifying neither data frames nor matrices ([R/rack.R#L249-L254](https://github.com/BristolMyersSquibb/blockr.session/blob/5f9b8e6aff54a58f84d2658963194c60e8a4262a/R/rack.R#L249-L254), [#L469-L473](https://github.com/BristolMyersSquibb/blockr.session/blob/5f9b8e6aff54a58f84d2658963194c60e8a4262a/R/rack.R#L469-L473)). A one-block stack therefore comes out as `"blocks": "a"` in one file and `"blocks": ["a"]` in the other, and JSON written with length-one vectors bare is what broke the dock's layout restore in [blockr.dock#91](https://github.com/BristolMyersSquibb/blockr.dock/issues/91).

## Proposal

### Files

A saved board keeps the shape `blockr_ser()` writes today: every object, the board, its blocks, links, stacks and options and the collections that hold them, is an `object`, its class vector, a `payload`, its constructor's args, and a `constructor`, the function with its package and that package's version at save time ([R/utils-serdes.R#L124-L142](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L124-L142)). A file thus says how R calls the constructors that rebuild the board, as a startup script does ([Board objects](Rewrite-1.1.1)). It is not the client's board: R turns a file into the board when it opens it ([Board updates](Rewrite-1.1.2)), and the client writes a file from the board and what R sends with it: the block registry, with the constructor of every block type or the definition of one defined outside a package, and each front-end's constructors for its boards and stacks ([Board objects](Rewrite-1.1.1#what-lives-where)). The one other writer is R's `blockr_ser()`, for an app's opening board, and fixtures that both test suites round-trip keep the two in step ([Defining a board in R](Rewrite-1.1.3#writing-the-opening-board)). A board subclass adds its own components as further nodes of the board's payload, in the same shape, as a dock board writes `extensions`, `views` and `grids` next to `blocks`, `links`, `stacks` and `options` today, each extension with its class, its state and its constructor ([blockr.dock R/utils-serdes.R#L47-L95](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L47-L95)).

A file written by the new stack departs from today's in five places:

- A `format` field gives the version of the file format. Today's files lack it, so the reader tells the two apart.
- A block type defined outside a package has a `definition` in place of the serialized closure today's files hold: the code the type was defined by, wrapped in `block_constructor()`, as a string that evaluates to its constructor ([Board objects](Rewrite-1.1.1#block-types-outside-a-package)).
- The board's options hold only their values, by id, as `{ "n_rows": 50 }`, since R collects the board's options again when it opens it ([Board objects](Rewrite-1.1.1#options)).
- Links and the board carry a `name`, since every object has one ([Board objects](Rewrite-1.1.1)): a link's sits in its payload, and the board's next to its `id`, in place of the `board_name` option.
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
          "constructor": { "object": "blockr_ctor", "constructor": "new_dataset_block", "package": "blockr.core", "version": "0.2.0" }
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
          "constructor": { "object": "blockr_ctor", "constructor": "new_link", "package": "blockr.core", "version": "0.2.0" }
        }
      }
    },
    "stacks": { "object": "stacks", "payload": {} },
    "options": { "object": "board_options", "payload": { "n_rows": 50 } }
  },
  "constructor": { "object": "blockr_ctor", "constructor": "new_board", "package": "blockr.core", "version": "0.2.0" },
  "version": "0.2.0",
  "id": "curious_otter",
  "name": "Sales review"
}
```

Writing one is `JSON.stringify()` in the browser and reading one `JSON.parse()`. Opening one goes through R, as every opening of a board does ([Board updates](Rewrite-1.1.2)), whether `store.open()` sends it, the `hello` after R restarts, or `serve()`, given a file's path or a board it writes as a file first ([Defining a board in R](Rewrite-1.1.3#the-opening-board)): R reads files of both stacks with `blockr_deser()`. On the way it registers every block's type, from the type's definition where the `load_definitions` option allows it and no type of the block's class is registered, or from the constructor of an installed package, which it loads. It leaves unread the closures today's files hold, drops what it cannot rebuild and names it ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)), and runs the migrations below.

### State values between the client and R

The client's board holds state as its UI wrote it, plain JSON. R decodes it with one decoding, still to be chosen (below), and a block type's author writes its `validate` and `interpolate` against that decoding, as a Shiny author writes against an input's value, so the arg specs describe args for LLMs and tools and convert nothing R reads ([Client-owned board state](Rewrite-1.1)). R writes state wherever it builds a board: for an app's opening board ([Defining a board in R](Rewrite-1.1.3)), and for every board it opens, files from today's stack included, whose blocks it rebuilds, migrating those saved by older versions of their types, before it replies with the board ([Board updates](Rewrite-1.1.2#opening-a-board)). There it writes each arg by the type its arg spec declares, since R's lack of scalars stays in R ([State in JS](Rewrite-1#principles)): a scalar as a bare value, and an array as an array whatever its length, as condition 3 asks. The spec shapes the JSON and checks nothing. Every state arg of a block type therefore declares its type, which 29 of the 177 state args of today's registered block types leave out (notes).

### Migrations

A block saved by an older version of its type migrates through the `blockr_deser()` methods its package has for the block's class, which can read the package version its `constructor` records or the shape of its payload, as blockr.dplyr's sixteen do ([R/legacy-deser.R#L30-L310](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/bdac6b38f7097425bfe96883032531cc919f6ee7/R/legacy-deser.R#L30-L310)). R runs them while it opens the board ([Board updates](Rewrite-1.1.2)), since the methods and the constructors live in R. A field migrates through the package that registers it, in JS, keyed by the version of that package the file records, as the dock's fields are by the version of blockr.dock the board's `constructor` records, and the dock's conversion of today's grids moves to the client, as [Client-drawn dock and extensions](Rewrite-1.2) has it.

### Options

A saved board holds each option's value under its id and nothing else of it, since R collects the board's options again when it opens it, as it collects them for an app's board, and gives each the value the file holds for its id, while the option itself, with its label and category, is what R sends the client ([Board objects](Rewrite-1.1.1#options)). In a file from today's stack, R ignores an option's category and label, since its constructor supplies them.

## Open questions

- How the fields packages register map onto the nodes a file holds, such as the DAG's positions onto the `positions` of its extension in the dock's `extensions`, which the loader and the client's writer both need: through a hook each package registers beside its fields, or by a convention, such as an extension's fields being its constructor's args ([Board updates](Rewrite-1.1.2#fields)). Either way R builds each extension as an R object, since it collects the options an extension ships from it ([blockr.dock R/utils-serve.R#L1-L9](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serve.R#L1-L9)), and [Front-ends and extension points](Rewrite-1.1.8#extensions) has a file name an extension's constructor next to its state, as today.
- Which one decoding R applies to the JSON the client sends, which the wire protocol leaves to this page ([Wire protocol](Rewrite-1.1.9#decoding)) and which blocks the protocol document's decoding and the guide for block type authors: jsonlite's `fromJSON()` simplifying neither data frames nor matrices, as blockr.session reads boards today, or typedjson in a mode that reads plain JSON, which 0.1.2 lacks, since its reader turns the string `"~:x"` into the symbol `x` (notes). Shiny's own decoding is ruled out, since it leaves every array a list and flattens a message that is itself an array (notes). A file from today's core needs typedjson's reader for the tags it holds, but in a mode that refuses code, since 0.1.2 also turns `{"~t":"language","~v":["~:Sys.getenv","HOME"]}` into a call that `bquote()` splices into a block's expression, whatever the `load_definitions` option says.

<details><summary>Notes for implementers</summary>

Decoding the JSON a client writes, measured on the 4-core dev workspace with R 4.5.3, jsonlite 2.0.0, typedjson 0.1.2 and shiny 1.14.0, each value inside an object as a block's state holds it:

| JSON | `jsonlite::fromJSON()`, no data frames or matrices | `typedjson::json_read_str()` | Shiny's input value |
|---|---|---|---|
| `["a"]` | `"a"` | `"a"` | `list("a")` |
| `[]` | `list()` | `list()` | `list()` |
| `[1, "a"]` | `c("1", "a")` | `list(1L, "a")` | `list(1L, "a")` |
| `[1, null]` | `c(1L, NA)` | `list(1L, NULL)` | `list(1L, NULL)` |
| `[{"col": "a", "vals": ["x"]}]` | `list(list(col = "a", vals = "x"))` | the same | `list(list(col = "a", vals = list("x")))` |
| `[[1, 2], [3, 4]]` | `list(1:2, 3:4)` | the same | `list(list(1L, 2L), list(3L, 4L))` |
| `3`, `3.0` | `3L`, `3` | the same | the same |
| `"~:x"`, `"~~a"` | `"~:x"`, `"~~a"` | the symbol `x`, `"~a"` | `"~:x"`, `"~~a"` |

At its defaults `jsonlite::fromJSON()` turns the array of objects into a data frame and the array of arrays into a matrix. Shiny reads a message with `simplifyVector = FALSE` ([shiny R/server.R#L100-L109](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/server.R#L100-L109)) and then unlists an input value that is an unnamed list ([R/server-input-handlers.R#L78-L98](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/server-input-handlers.R#L78-L98)), so a message sent with `Shiny.setInputValue()` that is an array of requests reaches R as one flat named character vector. The other way, Shiny writes what `session$sendCustomMessage()` sends with `auto_unbox = TRUE`, which unboxes every length-one vector not wrapped in `I()`, and inserts a string of class `json` as it is ([R/shiny.R#L34-L52](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/shiny.R#L34-L52)), so R either wraps each arg its spec declares an array in `I()` or writes the JSON itself.

A file from today's core holds typedjson's tags wherever plain JSON cannot say a type, such as `"by": {"~t":"character","~v":[]}` for a merge block's empty `by`, which `JSON.parse()` reads as an object and only typedjson resolves to `character(0)`. Read with typedjson, a file blockr.session wrote comes back as `rack_load()` reads it.

Of the 177 state args of the 46 types that blockr.core 0.1.4, blockr.dplyr 0.2.0.9035, blockr.dm 0.0.92, blockr.ggplot 0.1.1.9010 and blockr.io 0.1.0.9015 register, 29 have no type: seven args of blockr.dm's crossfilter block, the `state` of its two filter blocks and the `args` of its read block, the `args` of blockr.io's read, write and download blocks and the write block's `mode`, nine labels and settings of blockr.ggplot's plot block, five args of blockr.dplyr's pivot, rename, separate and slice blocks, and the `volumes` of core's file browser, a named character vector, which plain JSON brings back as a named list. No `arg_object()` describes a free-form `args` list, since it describes a closed record.

</details>
