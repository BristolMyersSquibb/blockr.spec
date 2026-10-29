# Serialization of the client-owned board
Status: settled on 2026-10-28. Design for [Client-owned board state](Rewrite-1.1).

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

A file written by the new stack is the board as the client holds it ([Board objects](Rewrite-1.1.1#the-board)), under `board`, with three things beside it that R needs to open it: `format`, the version of the file format, which today's files lack, so that R tells the two apart; `packages`, the version of every package that the board's block types, its front-end and its fields come from, which migrations key on; and `definitions`, the source of each block type defined outside a package, under its registry id ([Board objects](Rewrite-1.1.1#block-types-outside-a-package)). It names no R class or constructor, since the client holds none: when R opens the file, it finds each block's type in its block registry by registry id, and the board's front-end by its `front_end`. The client writes it from its board and from the package versions and definitions R sends with the block registry, and the one other writer is R's `blockr_ser()`, for an app's opening board, which writes the same file for the same board wherever a schema gives each value's shape (below), as fixtures that both test suites round-trip check ([Defining a board in R](Rewrite-1.1.3#writing-the-opening-board)). R refuses a file whose `format` is higher than any it knows, with an error that names both versions, as a client stops on a major protocol version it does not speak ([Wire protocol](Rewrite-1.1.9#handshake)).

A board with two blocks, one of them of a type defined outside a package, a link and an option:

```json
{
  "format": 1,
  "packages": { "blockr.core": "0.2.0" },
  "definitions": {
    "my_block": "blockr.core::block_constructor(blockr.core::block_type(\"my_block\", inputs = \"data\", expr = function(n = 3L) bquote(utils::head(data, n = .(n)))))"
  },
  "board": {
    "id": "curious_otter",
    "front_end": "blockr.core-basic",
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

A file from today's stack has another shape, in which every object, the board, its blocks, links, stacks and options and the collections that hold them, is an `object`, its class vector, a `payload`, its constructor's args, and a `constructor`, the function with its package and that package's version at save time ([R/utils-serdes.R#L124-L142](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L124-L142)), and a dock board writes `extensions`, `views` and `grids` next to `blocks`, `links`, `stacks` and `options`, each extension with its class, its state and its constructor ([blockr.dock R/utils-serdes.R#L47-L95](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L47-L95)). R maps its constructors to registry ids and a front-end as it opens it ([Board objects](Rewrite-1.1.1#the-board)), and the state packages added onto fields by a convention that follows today's shape alone. A component the board adds next to core's `blocks`, `links`, `stacks` and `options` is a field of the package of the board's constructor, named after the component, so the dock's `views` and `grids` become fields of blockr.dock, except where it holds objects that name constructors of their own, each of which gives its constructor's package a field for each of its args, so the `positions` of the DAG's entry in the dock's `extensions` become `blockr.dag-positions`. Each field carries the version of its package that the nearest constructor records. A key of a block's payload that is neither a state arg nor `block_name`, such as the dock's `visible`, becomes an attribute of the block ([Board objects](Rewrite-1.1.1#blocks)).

Writing one is `JSON.stringify()` in the browser. Opening one goes through R, as every opening of a board does ([Board updates](Rewrite-1.1.2)), whether `store.open()` sends it, the `hello` after R restarts or `serve()` given its path, and R does the same for each ([Defining a board in R](Rewrite-1.1.3#the-opening-board)), while the client sends a file as its text, which R parses. R parses a file that has a `format` as plain JSON, with the decoding below, and one without, from today's stack, with typedjson, since only typedjson resolves the tags today's core writes, such as `"by": {"~t":"character","~v":[]}` for a merge block's empty `by`, and it reads a file blockr.session wrote as `rack_load()` does (notes). It does so in a mode that refuses symbols, calls, closures and environments, which typedjson 0.1.2 lacks: that version turns the tags a crafted file holds into code, which `bquote()` then splices into a block's expression, whatever the `load_definitions` option says, against condition 5.

R reads a file of the new stack by its ids, loading the packages that `packages` names, and works on its JSON, building no R object, while it reads one from today's stack with `blockr_deser()`, which dispatches on its class vectors and builds R objects to convert it. On the way it registers every block's type, from the type's definition where the `load_definitions` option allows it and no type of the block's class is registered, or from its installed package, which it loads. It leaves unread the closures today's files hold, drops what it cannot rebuild and names it ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)), runs the block migrations below on the states the file holds, and gives each option the file lacks the app's initial value. It builds nothing from a package's fields and hands them to the client as saved, with the version that saved them, for the package to migrate in JS ([Board objects](Rewrite-1.1.1#extending-cores-objects)), and the store drops the fields and attributes of packages the app does not load ([Board updates](Rewrite-1.1.2#fields)).

### State values between the client and R

The client's board holds state as its UI wrote it, plain JSON, in the shape of the JSON Schema that the type's UI module ships beside it ([UI modules in JS](Rewrite-1.1.7#packaging)). The UI owns that shape, since R takes an arg in several forms and could declare them only through unions of types (notes), and the type's author makes the values fit the expression its `expr` builds from them, since they enter through the UI.

R decodes what the client sends with yyjsonr, turning neither an array of objects into a data frame nor an array of arrays into a matrix, and reading a 64-bit integer as a double: an array of one type becomes an atomic vector, an array of several types a list, an object a named list, and a string stays a string, so that nothing becomes code by being decoded ([Wire protocol](Rewrite-1.1.9#decoding)). A type's author writes `expr` against that decoding, as a Shiny author writes against an input's value. The jsonlite package decodes the same, except that it turns `[1, "a"]` into `c("1", "a")` (notes).

R writes state only where it makes it: for an app's opening board ([Defining a board in R](Rewrite-1.1.3)), for a block whose type's `migrate` gives it a new state, and for every block of a file from today's stack, which R converts through R objects (below). R opens a board of the new stack on its JSON, building no R board ([Defining a board in R](Rewrite-1.1.3#the-opening-board)), so every other state passes through R as the client wrote it, and comes back to the client unchanged. Where R writes state, it writes each value by the schema of its type's state, which R sends with the type's registry entry, since R's lack of scalars stays in R ([State in JS](Rewrite-1#principles)): a value of length one as an array where the schema has an array, and bare where the schema has a scalar or allows either, as the union `string | string[]` does, as condition 3 asks. A type whose UI ships no schema has such values written bare, so its UI takes either form. The arg specs keep describing args for models and tools ([Client-owned board state](Rewrite-1.1)), while the schema gives their shapes.

R writes the rest of a board it writes by schema too, so that no shape depends on R's JSON writer: core's objects by a JSON Schema of the board that core generates from the TypeScript types of [Board objects](Rewrite-1.1.1#the-board), so that a stack's `blocks` stays an array and an empty collection an object, and a field by the schema its package ships beside its module ([Board updates](Rewrite-1.1.2#fields)). That needs no JSON writer of its own: R marks a value that the schema has as an array with `I()`, and an empty one that it has as an object as a named list, which yyjsonr, jsonlite and Shiny's encoder all keep (notes).

### Migrations

A block saved by an older version of its type migrates through the type's `migrate` function, which maps the state the file holds to the type's current state, given the version of the package that saved it, from `packages` ([Block types in R](Rewrite-1.1.5#the-block-type)). R runs it on the saved state while it opens the board, building no block ([Board updates](Rewrite-1.1.2)), since the function lives in R. A file from today's stack migrates as today, through the `blockr_deser()` methods its package has for each block's class, which read the version its `constructor` records or the shape of its payload, as blockr.dplyr's sixteen do ([R/legacy-deser.R#L30-L310](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/bdac6b38f7097425bfe96883032531cc919f6ee7/R/legacy-deser.R#L30-L310)). What packages add migrates in JS, through the one migration each package registers, which reads everything the file holds for every package, its fields, the blocks' attributes and the option values, and returns its own package's state in today's shape, given the version of the package that saved it, from `packages` or, in a file from today's stack, from the constructor nearest each node ([Board updates](Rewrite-1.1.2#fields)). A package can thus rename, split and merge its fields, attributes and options between versions, and take over state that an earlier version of another package kept, and the store drops what no loaded package registered only once every migration has run. A package's migration reads today's nodes as R writes them after typedjson read them, with a value of length one bare, so it takes either form there.

### Options

A saved board holds each option's value under its id and nothing else of it. When R opens a board, it collects again the options that the board's parts require, its front-end and the block types the block registry holds, as it collects them for an app's board, keeping one per id, gives each one the file lacks its initial value and passes the values the file holds through, while the package that ships an option defines it in the client ([Board objects](Rewrite-1.1.1#options)). A package's migration converts its options' values with the rest of its state (above), and the store then drops and names a value that no option claims, as it drops a field no loaded package registered, while an option that a part requires but no installed package defines is an error naming both. In a file from today's stack, R ignores an option's category and label, since its definition supplies them.

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

At its defaults `jsonlite::fromJSON()` turns the array of objects into a data frame and the array of arrays into a matrix. Shiny reads a message with `simplifyVector = FALSE` ([shiny R/server.R#L100-L109](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/server.R#L100-L109)) and then unlists an input value that is an unnamed list ([R/server-input-handlers.R#L78-L98](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/server-input-handlers.R#L78-L98)), so a message sent with `Shiny.setInputValue()` that is an array of requests reaches R as one flat named character vector. The other way, Shiny writes what `session$sendCustomMessage()` sends with `auto_unbox = TRUE`, which unboxes every length-one vector not wrapped in `I()`, and inserts a string of class `json` as it is ([R/shiny.R#L34-L52](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/shiny.R#L34-L52)), so R marks each value that a schema has as an array with `I()`, and yyjsonr's and jsonlite's writers, with `auto_unbox = TRUE`, keep `I()` the same way. Marked as `list(stacks = setNames(list(), character()), s1 = list(blocks = I("a"), name = "Input"), cols = I(character()), na = NA_character_)`, a value comes out of all three as `{"stacks":{},"s1":{"blocks":["a"],"name":"Input"},"cols":[],"na":null}`, while unmarked, a one-block stack's `blocks` comes out bare and an empty `stacks` as `[]`. A schema is JSON Schema, so R reads where it has an array from its `type`, `items`, `properties` and `additionalProperties`, follows `$ref` into `$defs`, which Zod's `z.toJSONSchema()` writes for a type used twice, and takes `anyOf` and `oneOf` as allowing either form.

A file from today's core holds typedjson's tags wherever plain JSON cannot say a type, such as `"by": {"~t":"character","~v":[]}` for a merge block's empty `by`, which `JSON.parse()` reads as an object and only typedjson resolves to `character(0)`. Read with typedjson, a file blockr.session wrote comes back as `rack_load()` reads it. Version 0.1.2 also turns `{"~t":"language","~v":["~:Sys.getenv","HOME"]}` into the call `Sys.getenv("HOME")`, which `bquote()` splices into an expression, and the string `"~:x"` into the symbol `x`, so the mode R reads today's files in refuses those tags, a mode that typedjson has yet to add ([nbenn/typedjson#121](https://github.com/nbenn/typedjson/issues/121)). R tells the two stacks apart by parsing every file with yyjsonr first, which turns no tag into code, and parsing one without a `format` again with typedjson.

Of the 177 state args of the 46 types that blockr.core 0.1.4, blockr.dplyr 0.2.0.9035, blockr.dm 0.0.92, blockr.ggplot 0.1.1.9010 and blockr.io 0.1.0.9015 register, 29 declare no type in R today: seven args of blockr.dm's crossfilter block, the `state` of its two filter blocks and the `args` of its read block, the `args` of blockr.io's read, write and download blocks and the write block's `mode`, nine labels and settings of blockr.ggplot's plot block, five args of blockr.dplyr's pivot, rename, separate and slice blocks, and the `volumes` of core's file browser, a named character vector, which plain JSON brings back as a named list. No `arg_object()` describes a free-form `args` list, since it describes a closed record, while the read block's UI knows which of its settings are arrays.

</details>
