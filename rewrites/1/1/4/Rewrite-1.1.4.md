# Serialization of the client-owned board
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how a board is written to a file and read back, and how state values travel between the client and R. It builds on the [board objects proposal](Rewrite-1.1.1), which says what the board holds, and shapes opening boards in R, exporting the block registry, writing saved boards in the client and the JSON decoding of the wire protocol document, each an item in the Work list of [Client-owned board state](Rewrite-1.1#work). How R opens a board is the [board updates proposal](Rewrite-1.1.2#opening-a-board), and where a board is saved, to a download, Connect or a draft, is session management's ([Session management as a client extension](Rewrite-1.6)): core owns what a saved board is, not saving it.

## What must hold

1. Boards written by today's `blockr_ser()` open in the new stack, with the dock's views and layouts and the DAG's positions, for block types that have been ported, as condition 4 of [State in JS](Rewrite-1#what-must-hold) asks: their blocks through `blockr_deser()` and the migrations packages already have, and the state packages added through those packages' own migrations in JS.
2. A board saved by the new stack is written in the browser, so saving needs no R and works while R is busy or gone.
3. The client's board holds state values its UI can use as they are, so an arg that is a vector is always an array, whatever its length.
4. A file written by the new stack is the board as the client holds it, with only what R needs to rebuild it beside it, and names no R class or constructor, while R reads the files of both stacks.
5. Reading a file runs no code from it, other than the definitions the `load_definitions` option lets R evaluate, as condition 3 of [Wire protocol](Rewrite-1.1.9#what-must-hold) asks of everything the client sends.

## Today

The `blockr_ser()` function returns R lists, and the JSON is up to the caller. Core's own download and upload write them with typedjson ([R/plugin-serdes.R#L76-L78](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-serdes.R#L76-L78), [#L179-L181](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-serdes.R#L179-L181)), which writes a length-one vector bare ([format](https://github.com/nbenn/typedjson/blob/371144d1170eb738395e85c875c368fe8e787b43/README.md)), while blockr.session writes with `jsonlite::write_json()`, which keeps it in an array, and reads with `jsonlite::fromJSON()`, simplifying neither data frames nor matrices ([R/rack.R#L249-L254](https://github.com/BristolMyersSquibb/blockr.session/blob/5f9b8e6aff54a58f84d2658963194c60e8a4262a/R/rack.R#L249-L254), [#L469-L473](https://github.com/BristolMyersSquibb/blockr.session/blob/5f9b8e6aff54a58f84d2658963194c60e8a4262a/R/rack.R#L469-L473)). A one-block stack therefore comes out as `"blocks": "a"` in one file and `"blocks": ["a"]` in the other, and JSON written with length-one vectors bare is what broke the dock's layout restore in [blockr.dock#91](https://github.com/BristolMyersSquibb/blockr.dock/issues/91).

## Proposal

### Files

A file written by the new stack is the board as the client holds it ([Board objects](Rewrite-1.1.1#the-board)), under `board`, with three things beside it that R needs to rebuild it: `format`, the version of the file format, which today's files lack, so that R tells the two apart; `packages`, the version of every package that the board's block types, its front-end and its fields come from, which migrations key on; and `definitions`, the source of each block type defined outside a package, under its registry id ([Board objects](Rewrite-1.1.1#block-types-outside-a-package)). It names no R class or constructor, since the client holds none: when R opens the file, it maps each block's registry id to its type's constructor through its block registry, and the board's `front_end` to that front-end. The client writes it from its board and from the package versions and definitions R sends with the block registry, and the one other writer is R's `blockr_ser()`, for an app's opening board, which writes the same file for the same board, as fixtures that both test suites round-trip check ([Defining a board in R](Rewrite-1.1.3#writing-the-opening-board)).

A board with two blocks, one of them of a type defined outside a package, a link and an option:

```json
{
  "format": 1,
  "packages": { "blockr.core": "0.2.0" },
  "definitions": {
    "my_block": "blockr.core::block_constructor(blockr.core::block_type(\"my_block\", parent = blockr.core::transform_block, inputs = \"data\", state = function(n = 3L) list(n = n), expr = quote(utils::head(.(data), n = .(n)))))"
  },
  "board": {
    "id": "curious_otter",
    "front_end": "blockr.core",
    "name": "Sales review",
    "blocks": {
      "a": { "registry_id": "blockr.core-dataset_block", "state": { "dataset": "iris", "package": "datasets" }, "name": "Iris", "attrs": {} },
      "b": { "registry_id": "my_block", "state": { "n": 3 }, "name": "Mine", "attrs": {} }
    },
    "links": { "ab": { "from": "a", "to": "b", "input": "data", "name": "" } },
    "stacks": {},
    "options": { "n_rows": 50 },
    "fields": {}
  }
}
```

A file from today's stack has another shape, in which every object, the board, its blocks, links, stacks and options and the collections that hold them, is an `object`, its class vector, a `payload`, its constructor's args, and a `constructor`, the function with its package and that package's version at save time ([R/utils-serdes.R#L124-L142](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L124-L142)), and a dock board writes `extensions`, `views` and `grids` next to `blocks`, `links`, `stacks` and `options`, each extension with its class, its state and its constructor ([blockr.dock R/utils-serdes.R#L47-L95](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L47-L95)). R maps its constructors to registry ids and a front-end as it opens it ([Board objects](Rewrite-1.1.1#the-board)), and the state packages added onto fields by convention, since today's files hold that state as constructor args: an extension's fields are its constructor's args, so the `positions` of the DAG's extension become `blockr.dag-positions`, and a front-end's fields are the components its board adds, so the dock's `views` and `grids` become fields of blockr.dock, each with the version of its package that the constructor beside it records. A key of a block's payload that is neither a state arg nor `block_name`, such as the dock's `visible`, becomes an attribute of the block ([Board objects](Rewrite-1.1.1#blocks)).

Writing one is `JSON.stringify()` in the browser. Opening one goes through R, as every opening of a board does ([Board updates](Rewrite-1.1.2)), whether `store.open()` sends it, the `hello` after R restarts, or `serve()`, given a file's path or a board it writes as a file first ([Defining a board in R](Rewrite-1.1.3#the-opening-board)), and the client sends a file as its text, which R parses. R parses a file that has a `format` as plain JSON, with the decoding below, and one without, from today's stack, with typedjson, since only typedjson resolves the tags today's core writes, such as `"by": {"~t":"character","~v":[]}` for a merge block's empty `by`, and it reads a file blockr.session wrote as `rack_load()` does (notes). It does so in a mode that refuses symbols, calls, closures and environments, which typedjson 0.1.2 lacks: that version turns the tags a crafted file holds into code, which `bquote()` then splices into a block's expression, whatever the `load_definitions` option says, against condition 5.

R reads a file of the new stack by its ids, loading the packages that `packages` names, and one from today's stack with `blockr_deser()`, which dispatches on its class vectors. On the way it registers every block's type, from the type's definition where the `load_definitions` option allows it and no type of the block's class is registered, or from its installed package, which it loads. It leaves unread the closures today's files hold, drops what it cannot rebuild and names it ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)), runs the block migrations below, and builds each R block with its type's constructor. It builds nothing from a package's fields and hands them to the client as saved, with the version that saved them, for the package to migrate in JS ([Board objects](Rewrite-1.1.1#extending-cores-objects)), and the store drops the fields and attributes of packages the app does not load ([Board updates](Rewrite-1.1.2#fields)).

### State values between the client and R

The client's board holds state as its UI wrote it, plain JSON, in the shape of the schema that the type's UI module declares in TypeScript and ships beside it as JSON Schema ([UI modules in JS](Rewrite-1.1.7#packaging)). The UI owns that shape, since R takes an arg in several forms and could declare them only through unions of types (notes), and the type's author makes the values fit the expression `interpolate` builds from them, since they enter through the UI.

R decodes what the client sends with yyjsonr, turning neither an array of objects into a data frame nor an array of arrays into a matrix, and reading a 64-bit integer as a double: an array of one type becomes an atomic vector, an array of several types a list, an object a named list, and a string stays a string, so that nothing becomes code by being decoded ([Wire protocol](Rewrite-1.1.9#decoding)). A type's author writes `validate` and `interpolate` against that decoding, as a Shiny author writes against an input's value. The jsonlite package decodes the same, except that it turns `[1, "a"]` into `c("1", "a")` (notes).

R writes state wherever it builds a board: for an app's opening board ([Defining a board in R](Rewrite-1.1.3)), and for every board it opens, files from today's stack included, whose blocks it rebuilds, migrating those saved by older versions of their types, before it replies with the board ([Board updates](Rewrite-1.1.2#opening-a-board)). There it writes each value by the schema of its type's state, which R sends with the type's registry entry, since R's lack of scalars stays in R ([State in JS](Rewrite-1#principles)): a value of length one as an array where the schema has an array, and bare elsewhere, as condition 3 asks. A type whose UI ships no schema has such values written bare, so its UI takes either form. The arg specs keep describing args for models and tools ([Client-owned board state](Rewrite-1.1)), while the schema gives their shapes.

### Migrations

A block saved by an older version of its type migrates through the `blockr_deser()` methods its package has for the block's class, which R takes from the type's entry in its block registry where a file names only the registry id. A method can read the version of the package that saved the block, in `packages` or, in a file from today's stack, in its `constructor`, or the shape of its payload, as blockr.dplyr's sixteen do ([R/legacy-deser.R#L30-L310](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/bdac6b38f7097425bfe96883032531cc919f6ee7/R/legacy-deser.R#L30-L310)). R runs them while it opens the board ([Board updates](Rewrite-1.1.2)), since the methods and the constructors live in R. A field migrates through the package that registers it, in JS, keyed by the version of that package in `packages`, or in a file from today's stack the version its node's `constructor` records, as the dock's fields are by the version of blockr.dock the board's `constructor` records, and the dock's conversion of today's grids moves to the client, as [Client-drawn dock and extensions](Rewrite-1.2) has it.

### Options

A saved board holds each option's value under its id and nothing else of it. When R opens a board, it collects again the options that the board's parts require, its front-end and the block types the block registry holds, as it collects them for an app's board, keeping one per id, and gives each the value the file holds for its id, while the package that ships an option defines it in the client ([Board objects](Rewrite-1.1.1#options)). A value for an option that no part requires is dropped and named, as a field no loaded package registered is, and an option that a part requires but no installed package defines is an error naming both. In a file from today's stack, R ignores an option's category and label, since its definition supplies them.

## Open questions

None.

<details><summary>Notes for implementers</summary>

Decoding the JSON a client writes, measured on the 4-core dev workspace with R 4.5.3, yyjsonr 0.1.22, jsonlite 2.0.0, typedjson 0.1.2 and shiny 1.14.0, each value inside an object as a block's state holds it, and yyjsonr with `obj_of_arrs_to_df`, `arr_of_objs_to_df` and `arr_of_arrs_to_matrix` off and `int64 = "double"`:

| JSON | yyjsonr | `jsonlite::fromJSON()`, no data frames or matrices | `typedjson::json_read_str()` | Shiny's input value |
|---|---|---|---|---|
| `["a"]` | `"a"` | `"a"` | `"a"` | `list("a")` |
| `[]` | `list()` | `list()` | `list()` | `list()` |
| `[1, "a"]` | `list(1L, "a")` | `c("1", "a")` | `list(1L, "a")` | `list(1L, "a")` |
| `[1, null]` | `c(1L, NA)` | `c(1L, NA)` | `list(1L, NULL)` | `list(1L, NULL)` |
| `[{"col": "a", "vals": ["x"]}]` | `list(list(col = "a", vals = "x"))` | the same | the same | `list(list(col = "a", vals = list("x")))` |
| `[[1, 2], [3, 4]]` | `list(1:2, 3:4)` | the same | the same | `list(list(1L, 2L), list(3L, 4L))` |
| `3`, `3.0` | `3L`, `3` | the same | the same | the same |
| `"~:x"`, `"~~a"` | `"~:x"`, `"~~a"` | the same | the symbol `x`, `"~a"` | `"~:x"`, `"~~a"` |

At its defaults `jsonlite::fromJSON()` turns the array of objects into a data frame and the array of arrays into a matrix. Shiny reads a message with `simplifyVector = FALSE` ([shiny R/server.R#L100-L109](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/server.R#L100-L109)) and then unlists an input value that is an unnamed list ([R/server-input-handlers.R#L78-L98](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/server-input-handlers.R#L78-L98)), so a message sent with `Shiny.setInputValue()` that is an array of requests reaches R as one flat named character vector. The other way, Shiny writes what `session$sendCustomMessage()` sends with `auto_unbox = TRUE`, which unboxes every length-one vector not wrapped in `I()`, and inserts a string of class `json` as it is ([R/shiny.R#L34-L52](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/shiny.R#L34-L52)), so R either wraps each value its type's schema has as an array in `I()` or writes the JSON itself, and yyjsonr's writer, with `auto_unbox = TRUE`, keeps `I()` the same way. A schema is JSON Schema, so R reads where it has an array from its `type`, `items`, `properties` and `additionalProperties`.

A file from today's core holds typedjson's tags wherever plain JSON cannot say a type, such as `"by": {"~t":"character","~v":[]}` for a merge block's empty `by`, which `JSON.parse()` reads as an object and only typedjson resolves to `character(0)`. Read with typedjson, a file blockr.session wrote comes back as `rack_load()` reads it. Version 0.1.2 also turns `{"~t":"language","~v":["~:Sys.getenv","HOME"]}` into the call `Sys.getenv("HOME")`, which `bquote()` splices into an expression, and the string `"~:x"` into the symbol `x`, so the mode R reads today's files in refuses those tags, a mode that typedjson has yet to add ([nbenn/typedjson#121](https://github.com/nbenn/typedjson/issues/121)). R tells the two stacks apart by parsing every file with yyjsonr first, which turns no tag into code, and parsing one without a `format` again with typedjson.

Of the 177 state args of the 46 types that blockr.core 0.1.4, blockr.dplyr 0.2.0.9035, blockr.dm 0.0.92, blockr.ggplot 0.1.1.9010 and blockr.io 0.1.0.9015 register, 29 declare no type in R today: seven args of blockr.dm's crossfilter block, the `state` of its two filter blocks and the `args` of its read block, the `args` of blockr.io's read, write and download blocks and the write block's `mode`, nine labels and settings of blockr.ggplot's plot block, five args of blockr.dplyr's pivot, rename, separate and slice blocks, and the `volumes` of core's file browser, a named character vector, which plain JSON brings back as a named list. No `arg_object()` describes a free-form `args` list, since it describes a closed record, while the read block's UI knows which of its settings are arrays.

</details>
