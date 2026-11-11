# Serialization of the client-owned board
Status: settled on 2026-10-28. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how a board is written to a file and read back, and how state values travel between the client and R.
It builds on the [board objects proposal](Rewrite-1.1.1), which says what the board holds, and shapes the JSON decoding of the wire protocol document ([blockr.core#420](https://github.com/BristolMyersSquibb/blockr.core/issues/420)), exporting the block registry ([blockr.core#426](https://github.com/BristolMyersSquibb/blockr.core/issues/426)), writing a board's JSON in R by schema ([blockr.core#428](https://github.com/BristolMyersSquibb/blockr.core/issues/428)), reading a JSON board in R ([blockr.core#429](https://github.com/BristolMyersSquibb/blockr.core/issues/429)), saving JSON boards in the client ([blockr.core#436](https://github.com/BristolMyersSquibb/blockr.core/issues/436)), the plugins that a JSON board holds and their migrations ([blockr.core#504](https://github.com/BristolMyersSquibb/blockr.core/issues/504)) and refusing a board that holds a value its schema refuses ([blockr.core#509](https://github.com/BristolMyersSquibb/blockr.core/issues/509)), each an item in the Work list of [Client-owned board state](Rewrite-1.1#work).
How the client opens a board is the [board updates proposal](Rewrite-1.1.2#opening-a-board), and where a board is saved, to Connect or a draft, is session management's ([Session management as a client extension](Rewrite-1.6)), beside the download that core's own storage plugin offers ([Plugins](Rewrite-1.1.12#storage)): core owns what a JSON board is, and saves one itself only as a download.

## What must hold

1. Boards written by today's `blockr_ser()` open in the new stack, with the dock's views and layouts and the DAG's positions, for block classes that have been ported, as condition 4 of [State in JS](Rewrite-1#what-must-hold) asks: converted to JSON boards once, outside core, their blocks through `blockr_deser()` and the migrations packages already have, after which the client opens them as any JSON board, the state of plugins through the migrations of their classes, in JS.
2. A board saved by the new stack is written in the browser, so saving needs no R and works while R is busy or gone.
3. The client's board holds state values its UI can use as they are, so an arg that is a vector is always an array, whatever its length.
4. A JSON board, the one format of a board outside the store, is the board as the client holds it, with only what opening it needs, and names no R class or constructor, while a file of today's stack is converted to one outside core.
5. Reading a file decodes it into plain values, as condition 3 of [Wire protocol](Rewrite-1.1.9#what-must-hold) has it for what the client sends.
6. What a JSON board holds migrates by the version of its shape, which never depends on the version of the package that wrote it.

## Today

The `blockr_ser()` function returns R lists, and the JSON is up to the caller.
Core's own download and upload write them with typedjson ([R/plugin-serdes.R#L76-L78](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-serdes.R#L76-L78), [#L179-L181](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-serdes.R#L179-L181)), which writes a length-one vector bare ([format](https://github.com/nbenn/typedjson/blob/371144d1170eb738395e85c875c368fe8e787b43/README.md)), while blockr.session writes with `jsonlite::write_json()`, which keeps it in an array, and reads with `jsonlite::fromJSON()`, simplifying neither data frames nor matrices ([R/rack.R#L249-L254](https://github.com/BristolMyersSquibb/blockr.session/blob/5f9b8e6aff54a58f84d2658963194c60e8a4262a/R/rack.R#L249-L254), [#L469-L473](https://github.com/BristolMyersSquibb/blockr.session/blob/5f9b8e6aff54a58f84d2658963194c60e8a4262a/R/rack.R#L469-L473)).
A one-block stack therefore comes out as `"blocks": "a"` in one file and `"blocks": ["a"]` in the other, and JSON written with length-one vectors bare is what broke the dock's layout restore in [blockr.dock#91](https://github.com/BristolMyersSquibb/blockr.dock/issues/91).

## Proposal

### Files

A JSON board is the one format of a board outside the store: the board as the client holds it ([Board objects](Rewrite-1.1.1#the-board)), under `board`, with two things beside it that opening it needs: `format`, the version of the format, which today's files lack, so that a file still to convert is told apart; and `packages`, the version of every package that the board's block classes and plugin classes come from, which names what to install, since the client names each package that a JSON board lists and the app does not name ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)).
Inside the board, each block records the version of its class's state in `version`, the board in `versions` the version of the state of each plugin class whose plugins' state it holds, by the class's id, and each board option the version of its value's shape beside the value, which migrations key on (below).
A block of a class defined outside a package is there by its registry id alone, as any other, and nothing of its class is ([Board objects](Rewrite-1.1.1#block-classes-outside-a-package)).
It names no constructor and no R class: when the client opens the file, it finds each block's class among the block registry's entries by registry id, and each plugin's class among the plugin classes that the app's packages register, by the class's id ([Board objects](Rewrite-1.1.1#the-board)).
The client saves a board as one, from its board and from the versions of packages and of classes that R sends with the block registry.
R's `blockr_ser()` writes an app's opening board as one too, with every id, since R draws each id the script left out ([Board objects](Rewrite-1.1.1#ids)), writing each value as the client does wherever a schema gives the value's shape (below), as fixtures that both test suites round-trip check ([Defining a board in R](Rewrite-1.1.3#writing-the-opening-board)).
The packages that R and the client record are those of the classes whose plugins' state the board holds, which each class's id names, and those of its blocks' classes.
The client refuses a file whose `format` is higher than any it knows, with an error that names both versions, as it stops on a major protocol version it does not speak ([Wire protocol](Rewrite-1.1.9#handshake)), and so does R for the file `serve()` is given.
Where both locks are on, R also refuses a file that it cannot read as today's packages write one ([Locked boards and the properties of blocks](Rewrite-1.1.11#serving-a-json-board-locked)).

A board with two blocks, one of them of a class defined outside a package, a link, a board option and the DAG:

```json
{
  "format": 1,
  "packages": { "blockr.core": "0.2.0", "blockr.dag": "0.2.0" },
  "board": {
    "id": "curious_otter",
    "versions": { "blockr.dag-dag_plugin": 1 },
    "name": "Sales review",
    "blocks": {
      "a": { "registry_id": "blockr.core-dataset_block", "version": 1, "state": { "dataset": "iris", "package": "datasets" }, "name": "Iris", "locked": null },
      "b": { "registry_id": "my_block", "version": 2, "state": { "n": 3 }, "name": "Mine", "locked": null }
    },
    "links": { "ab": { "from": "a", "to": "b", "input": "data" } },
    "stacks": {},
    "options": { "n_rows": { "value": 50, "version": 1 } },
    "plugins": { "dag": { "class": "blockr.dag-dag_plugin", "state": { "positions": { "a": { "x": 120, "y": 80 } } } } }
  }
}
```

A file from today's stack has another shape, in which every object, the board, its blocks, links, stacks and board options and the collections that hold them, is an `object`, its class vector, a `payload`, its constructor's args, and a `constructor`, the function with its package and that package's version at save time ([R/utils-serdes.R#L124-L142](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serdes.R#L124-L142)), and a dock board writes `extensions`, `views` and `grids` next to `blocks`, `links`, `stacks` and `options`, each extension with its class, its state and its constructor ([blockr.dock R/utils-serdes.R#L47-L95](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serdes.R#L47-L95)).
A conversion outside core turns it into a JSON board once: it maps its constructors to registry ids, and turns what the dock added to the board into the state of plugins, which keeps today's shape ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)).
A dock board becomes a board that holds the state of the dock plugin, taken from the dock board's `views` and `grids`, and the state of a plugin for each entry of its `extensions` that keeps any, of the class that takes the extension's place, under the name the board gave the extension and taken from the args of the extension's constructor, so the `positions` of the DAG's entry become `positions` in the state of the DAG's plugin, and a board with two documents of blockr.md keeps both.
The converted file records in `packages` the version of each package that the nearest constructor records, each block at the version that its class's state has, since `blockr_ser()` writes the block's state from the R block that `blockr_deser()` builds, and each plugin class at version 1, since the conversion keeps its plugins' state in today's shape, so that a plugin class whose state changes shape in the new stack starts at version 2, and its migration from version 1 reads converted files.
A property of a block's payload that is neither a state arg nor `block_name` goes into the dock plugin's state, under the same name and keyed by the block's id, so the dock's `visible` becomes the dock plugin's `visible`, as `{ "a": ["outputs"] }` ([Locked boards and the properties of blocks](Rewrite-1.1.11#what-a-plugin-keeps-about-a-block)).
Every block gets `null` for its `locked`, which follows the board lock ([Board objects](Rewrite-1.1.1#blocks)), and a dock stack's `color`, which core keeps now, becomes the stack's `color` ([Board objects](Rewrite-1.1.1#stacks)).
The conversion writes a colour of three digits, such as `#fc8`, with six digits, as `#ffcc88`.
A stack that is no dock stack has no colour today, and gets `null`.

Writing one is `JSON.stringify()` in the browser, through the store's `save()`, which gives its text, as a file holds it ([Board updates](Rewrite-1.1.2#the-store)).
The text is indented by two spaces and ends in a newline, as R writes the fixtures (above), so that a saved file reads like them.
Opening one is the client's too, whether the user opens it with `store.open()`, a startup module names it, or `serve()` was given its path, which R passes on as it is, having read nothing of it but its format unless both locks are on ([Defining a board in R](Rewrite-1.1.3#the-opening-board), [Board updates](Rewrite-1.1.2#opening-a-board), [Locked boards and the properties of blocks](Rewrite-1.1.11#serving-a-json-board-locked)).
A file without a `format`, from today's stack, is converted first, outside core, by a conversion that reads it with typedjson, since only typedjson resolves the tags today's core writes, such as `"by": {"~t":"character","~v":[]}` for a merge block's empty `by`, and a file blockr.session wrote as `rack_load()` does (notes).
It does so in a mode that refuses symbols, calls, closures and environments, `code = FALSE`, which typedjson added after 0.1.2 ([nbenn/typedjson#122](https://github.com/nbenn/typedjson/pull/122)), since 0.1.2 turns the tags a crafted file holds into code, which `bquote()` would then splice into a block's expression, against condition 5.

The client opens a JSON board by its ids, with the block registry of the reply to `hello`, which holds the classes of every package that the app names and those its script registered, since R loads no package for a board, and with the plugin classes that those packages register ([Plugins](Rewrite-1.1.12#a-plugin)), runs the migrations below on what it holds, block states included, and drops what the app cannot rebuild, naming the blocks and the plugins it drops and the packages it lists that the app does not offer ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)).
The conversion of a file from today's stack reads it with `blockr_deser()`, which dispatches on its class vectors and builds R objects to convert it, and leaves unread the closures today's files hold.

### State values between the client and R

The client's board holds state as its UI wrote it, plain JSON, in the shape of the JSON Schema that the class's UI module ships beside it ([UI modules in JS](Rewrite-1.1.7#packaging)).
The UI owns that shape, since R takes an arg in several forms and could declare them only through unions of types (notes), and the class's author makes the values fit the expression its `expr` builds from them, since they enter through the UI.

R decodes what the client sends with yyjsonr, turning neither an array of objects into a data frame nor an array of arrays into a matrix, keeping a string in an array of numbers a string, and reading a 64-bit integer as a double: an array of one type becomes an atomic vector, an array of several types a list, an object a named list, and a string stays a string, so that nothing becomes code by being decoded ([Wire protocol](Rewrite-1.1.9#decoding)).
A class's author writes `expr` against that decoding, as a Shiny author writes against an input's value.
The jsonlite package decodes the same, except that it turns `[1, "a"]` into `c("1", "a")` (notes).

R writes state only where it makes it: for an app's opening board ([Defining a board in R](Rewrite-1.1.3)) and for a class's starting state in its block registry entry ([Block classes in R](Rewrite-1.1.5#registration)), while the conversion writes the state of every block of a file from today's stack, which it converts through R objects (above).
R opens no board, so every other state stays in the client as the client wrote it.
Where R writes state, it writes each value by the schema of its class's state, which R sends with the class's registry entry, since R's lack of scalars stays in R ([State in JS](Rewrite-1#principles)): a value of length one as an array where the schema has an array, and bare where the schema has a scalar or allows either, as the union `string | string[]` does, as condition 3 asks.
A class whose UI ships no schema has such values written bare, so its UI takes either form.
The arg specs keep describing args for models and tools ([Client-owned board state](Rewrite-1.1)), while the schema gives their shapes.

R writes the rest of a board it writes by schema too, so that no shape depends on R's JSON writer: core's objects by a JSON Schema of a JSON board that core generates from the TypeScript types of [Board objects](Rewrite-1.1.1#the-board), so that a stack's `blocks` stays an array and an empty collection an object, and a plugin's state or a board option's value by the schema its package ships beside its startup module ([UI modules in JS](Rewrite-1.1.7#packaging)), so that `show_conditions` set to `"error"` in a script still reaches the client as the array its schema has.
That needs no JSON writer of its own: R marks a value that the schema has as an array with `I()`, and an empty one that it has as an object as a named list, which yyjsonr, jsonlite and Shiny's encoder all keep (notes).

### Migrations

The state of plugins, the blocks' states and the board options' values migrate in JS, as the client opens a JSON board, by the version of each shape that it records, never by the version of a package, which says when the package was released rather than what shape its content has, so that a package keys no migration on its releases, and the `packages` that a JSON board lists serve only to name what to install.
A block records the version of its class's state, which `new_block_class()` takes as `version` ([Block classes in R](Rewrite-1.1.5#the-block-class)), the board the version of each class whose plugins' state it holds, which the class's method of `plugin_version()` gives ([Plugins](Rewrite-1.1.12#a-plugin)), and each board option's value the version of its shape, which the board option's method of `board_option_version()` gives (below), each a whole number from 1 that a package raises as it changes the shape.
A plugin class migrates the state of each of its plugins in its `migrate`, a board option its value in its own, and a package registers the migration of each of its block classes' states under the class's registry id, each given what the JSON board holds and the version it records, and returning it in today's shape ([Board updates](Rewrite-1.1.2#plugins)).
The store runs a plugin class's migration where the board records a version below the one R gives, a block's where the block records one below its class's, and a board option's where the board records its value at a version below the one R gives, refuses a version above, since no migration converts back, and leaves alone a class that the board records no version of, since its writer knew none.
It checks and migrates the versions of the state of a board's plugins only once it has dropped the state of those that the app does not hold, since it drops a plugin's state for its id or its class, never for its version ([Board updates](Rewrite-1.1.2#plugins)).
A block class's UI owns the shape of its state and ships its schema (above), so the package that ships the UI migrates the state when that shape changes, raising the class's version, and no migration runs in R.
A class can thus rename, split and merge the parts of its plugins' state or its state args between versions, and what a migration leaves out is gone, while the store drops the blocks and the board option values that no loaded package registered only once every migration has run.
A file from today's stack migrates once, as its conversion outside core reads it, through the `blockr_deser()` methods its package has for each block's class, which read the version its `constructor` records or the shape of its payload, as blockr.dplyr's sixteen do ([R/legacy-deser.R#L30-L310](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/bdac6b38f7097425bfe96883032531cc919f6ee7/R/legacy-deser.R#L30-L310)), and the client's migrations take over from the versions the converted file records (above), reading a plugin's state at version 1 as the conversion writes it after typedjson read it, with a value of length one bare, so that it takes either form there.

### Board options

A JSON board holds each board option's value under its id with the version of the value's shape, as `"n_rows": { "value": 50, "version": 1 }`, and nothing else of it, while the board holds the value alone.
It holds every value that the board held, each one that a script, a file or a command set, and no default, so a board opened from one gets back the values that someone chose, whatever its page then shows, and takes the defaults of the app that opens it for the rest ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)).
The package that defines a board option gives the version in R, through its method of `board_option_version()` for the board option's class, which is its id followed by `_option`, as `board_option_version.n_rows_option()`, and a board option without one is at version 1, so that R writes the values of the opening board at the versions the client saves, while R sends the versions in its reply to `hello`, in `option_versions` ([Wire protocol](Rewrite-1.1.9#handshake)).
The store migrates a value that the board records at a version below the one R gives in the board option's `migrate` (above), refuses one above, and refuses the board, naming the board option, where its schema refuses the value once migrated ([Board updates](Rewrite-1.1.2#opening-a-board)), while it drops a value that no board option claims and names it by its id, and what core does where a plugin's class requires a board option that no loaded package defines is [Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)'s.
The conversion of a file from today's stack drops a board option's category and label, since its definition supplies them.

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

At its defaults `jsonlite::fromJSON()` turns the array of objects into a data frame and the array of arrays into a matrix.
Shiny reads a message with `simplifyVector = FALSE` ([shiny R/server.R#L100-L109](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/server.R#L100-L109)) and then unlists an input value that is an unnamed list ([R/server-input-handlers.R#L78-L98](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/server-input-handlers.R#L78-L98)), so a message sent with `Shiny.setInputValue()` that is an array of requests reaches R as one flat named character vector.
The other way, Shiny writes what `session$sendCustomMessage()` sends with `auto_unbox = TRUE`, which unboxes every length-one vector not wrapped in `I()`, and inserts a string of class `json` as it is ([R/shiny.R#L34-L52](https://github.com/rstudio/shiny/blob/dffc756a2867533fafc0858baf4c3fdbed165692/R/shiny.R#L34-L52)), so R marks each value that a schema has as an array with `I()`, and yyjsonr's and jsonlite's writers, with `auto_unbox = TRUE`, keep `I()` the same way.
Marked as `list(stacks = setNames(list(), character()), s1 = list(blocks = I("a"), name = "Input"), cols = I(character()), na = NA_character_)`, a value comes out of all three as `{"stacks":{},"s1":{"blocks":["a"],"name":"Input"},"cols":[],"na":null}`, while unmarked, a one-block stack's `blocks` comes out bare and an empty `stacks` as `[]`.
A schema is JSON Schema, so R reads where it has an array from its `type`, `items`, `properties` and `additionalProperties`, follows `$ref` into `$defs`, which Zod's `z.toJSONSchema()` writes for a type used twice, and takes `anyOf` and `oneOf` as allowing either form.

A file from today's core holds typedjson's tags wherever plain JSON cannot say a type, such as `"by": {"~t":"character","~v":[]}` for a merge block's empty `by`, which `JSON.parse()` reads as an object and only typedjson resolves to `character(0)`.
Read with typedjson, a file blockr.session wrote comes back as `rack_load()` reads it.
Version 0.1.2 also turns `{"~t":"language","~v":["~:Sys.getenv","HOME"]}` into the call `Sys.getenv("HOME")`, which `bquote()` splices into an expression, and the string `"~:x"` into the symbol `x`, so the conversion reads today's files in the mode that refuses those tags, `code = FALSE`, which typedjson added after 0.1.2 ([nbenn/typedjson#122](https://github.com/nbenn/typedjson/pull/122)).
A file of today's stack is told by its missing `format`.

Of the 177 state args of the 46 classes that blockr.core 0.1.4, blockr.dplyr 0.2.0.9035, blockr.dm 0.0.92, blockr.ggplot 0.1.1.9010 and blockr.io 0.1.0.9015 register, 29 declare no type in R today: seven args of blockr.dm's crossfilter block, the `state` of its two filter blocks and the `args` of its read block, the `args` of blockr.io's read, write and download blocks and the write block's `mode`, nine labels and settings of blockr.ggplot's plot block, five args of blockr.dplyr's pivot, rename, separate and slice blocks, and the `volumes` of core's file browser, a named character vector, which plain JSON brings back as a named list.
No `arg_object()` describes a free-form `args` list, since it describes a closed record, while the read block's UI knows which of its settings are arrays.

</details>
