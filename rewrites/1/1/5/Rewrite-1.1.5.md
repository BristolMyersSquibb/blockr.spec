# Block types in R for the client-owned board
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how a package defines and registers a block type in R, and how R evaluates a block with it. It shapes defining block types, a block type's output, exporting the block registry, the per-session evaluator and the guide for block type authors, each an item in the Work list of [Client-owned board state](Rewrite-1.1#work). A block type's UI, a module that meets the contract, is the UI modules proposal ([UI modules in JS](Rewrite-1.1.7)), the messages that carry a block's recipe and its result are the [wire protocol proposal](Rewrite-1.1.9), how state values travel between the client and R is the [serialization proposal](Rewrite-1.1.4), which renderer draws an output is [Front-ends and extension points](Rewrite-1.1.8#renderers)'s, and when a block is evaluated is the [evaluation proposal](Rewrite-1.1.10).

## What must hold

1. A block type is defined once, as a value, and the constructor made from it returns an S3 block whose args are the block's state; types are registered as today, under a registry id ([Board objects](Rewrite-1.1.1)).
2. Its R side is plain functions, with no Shiny module server and no reactives.
3. The generics packages implement today keep working wherever they still have a job.
4. Nothing about a type is copied into its blocks, and nothing builds a block to learn about its type.
5. A package plugs into another package's type only through a hook that type offers, or by deriving a type of its own.
6. A front-end or any other package can replace how core draws a kind of output, such as a table, without changing a block type.

## Today

A block type calls `new_block(server, ui, class, ctor, ctor_pkg, dat_valid, allow_empty_state, block_name, expr_type, external_ctrl, block_metadata, ...)` or one of its specializations ([R/block-class.R#L180](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L180)). The server is a Shiny module whose formals name the data inputs and which returns `expr`, a reactive expression, and `state`, reactives naming every constructor formal ([R/block-server.R#L969](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L969)). The head block keeps its args in `reactiveVal()`s, syncs them with its inputs through observers, and caps `n` at the number of rows with `updateNumericInput()` ([R/transform-head.R#L27-L91](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/transform-head.R#L27-L91)).

## Proposal

### The block type

A block type is a value made by `block_type()`, holding everything that is the same for every block of the type, and its constructor is a function that `block_constructor()` makes from it. The head block, written to the new contract, with illustrative names:

```r
head_block <- block_type(
  "head_block",
  parent      = transform_block,
  inputs      = "data",
  state       = function(n = 6L, direction = c("head", "tail")) {
    list(n = n, direction = match.arg(direction))
  },
  ui          = js_module("head-block.js"),
  requests    = list(n_max = \(data) nrow(data)),
  expr_type   = "bquoted",
  interpolate = function(x, state, inputs) {
    fn <- if (identical(state$direction, "tail")) quote(utils::tail) else quote(utils::head)
    bbquote(.(fn)(.(data), n = .(n)), list(fn = fn, n = state$n))
  },
  dat_valid   = function(data) stopifnot(is.data.frame(data))
)

new_head_block <- block_constructor(head_block)
```

The constructor has the formals of `state`, a `block_name` and `...`, so an app script calls `new_head_block(n = 10L)` as today, and the checks in `state`, such as `match.arg()`, run when it does. It returns a block that holds its state, its name and the attributes `...` passes, such as the dock's `visible` ([Board objects](Rewrite-1.1.1#blocks)), and refers to its type, which every head block shares and none copies. The name keeps today's argument, `block_name`, since `attr()` matches attribute names partially: on a block, a list of its state, that has no `name` attribute, `attr(blk, "name")` returns the block's `names`, as it did when `new_block()` took a `name`. A package exports both: the type, which other types can name as their parent, and the constructor, which app scripts call. An abstract type, such as `transform_block`, has no constructor.

A type's fields:

- The `class` and `parent` arguments give the type's class, which with its parent's makes a block's class vector, `c("head_block", "transform_block", "block")`, and the type it inherits from. A field the type leaves out comes from its parent.
- The `state` field is a function from the constructor's args to the block's state, with their defaults and checks. Called without args, it gives the state a new block starts with.
- The `inputs` field names the data input slots, `"data"`, `c("x", "y")` for a merge, or `"...args"` for a variadic block. Every concrete type declares its own, since arity is not what a parent such as `transform_block` stands for.
- The `ui` field names the type's UI, a module written against the contract of [UI modules in JS](Rewrite-1.1.7), in plain TypeScript as core's own are or in TSX with React, which ships the schema of the block's state beside it ([UI modules in JS](Rewrite-1.1.7#packaging)), and the `requests` field takes a named list of R functions for whatever the UI asks of R, such as the head block's `n_max`, whose arguments name the inputs and state args they read.
- The `expr` field takes a template, with `.(arg)` placeholders for state args and the inputs referred to as `expr_type` says, by `.(data)` placeholders or by symbol, as today, which the root type's `interpolate` fills in. A type whose expression changes shape with its state or its data, as the head block's does with its direction, gives an `interpolate` of its own instead.
- The `validate`, `interpolate`, `evaluate` and `summary` fields are the functions R evaluates a block with (below).
- The `output` field describes a result for the client, as an output of a kind that a renderer draws (below), and the `options` field names the board options its blocks use, by the constructors that give each option's id and initial value, while the package that ships an option defines it in the client ([Board objects](Rewrite-1.1.1)).
- The `migrate` field maps a state saved by an older version of the type's package to the current state, given that version, and R runs it on the state a file holds when it opens a board ([Serialization](Rewrite-1.1.4#migrations)). The root type's leaves a state as it is.
- The `dat_valid` and `expr_type` fields stay as they are, while `allow_empty_state`, `external_ctrl` and `block_metadata` go: the root type's `validate` accepts every state, every block's state can now be set from outside, and a type's metadata comes from its registration (below).

A type has no say in when its blocks are evaluated: a block that must run with nothing on screen, such as a write block in auto mode, is demanded by a rule its package registers in the client ([Evaluation in the client](Rewrite-1.1.10#demand)).

The functions R evaluates and outputs a block with, `validate`, `interpolate`, `evaluate`, `summary` and `output`, take the type as their first argument, `x`, as an S3 method takes its object, so that the root type's `interpolate` can fill in the template a child gives as `expr`, and a field can call its parent's, `x$parent$output(x, ...)`, as a method calls `NextMethod()`. The other function fields name what they read instead: `state` the constructor's args, a request the inputs and state args it reads, `migrate` the state and the version that saved it, and `dat_valid` the data inputs, as today, since a type whose inputs are `x` and `y`, as the merge block's are, could not also take itself as `x` ([R/transform-merge.R#L109](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/transform-merge.R#L109)). A type's `options` add to its parent's instead of replacing them, as `board_options()` methods combine with `NextMethod()` today. The `block_type()` function checks a type when it is defined, such as that no input slot and state arg share a name, since a request's arguments would not say which they mean, and that no state arg is called `block_name`, so no block is checked for being well formed again.

### Core's types and hooks

Core's root type, `block`, gives every field its default: `validate` accepts every state, `interpolate` fills in `expr`, `evaluate` runs the expression with the inputs bound, as `block_eval()` and `eval_env()` do today, `summary` gives the result's class and dimensions, and `output` prints the result, as an output of kind `blockr.core-text` (below). The specializations become types without constructors, which a package names as its parent:

```r
transform_block <- block_type(
  "transform_block",
  parent  = block,
  output  = function(x, result, options, info, meta) tabular_output(result, options, info, meta),
  options = list(new_n_rows_option)
)
```

The other specializations, `data_block`, `parser_block`, `plot_block`, `text_block` and `file_block`, follow with the output and options of their kind, and `plot_block` with an `evaluate` that uses `evaluate::evaluate()`, as core's plot block evaluates today, and an `output` that draws the recorded plot at the size and in the theme `info` gives, as an output of kind `blockr.core-plot`, where today the block re-evaluates when the theme changes ([R/plot-block.R#L59-L68](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plot-block.R#L59-L68)).

A type's fields belong to its package, so another package cannot change a type in place, as an S3 method registered for the type's class can today. Instead, a type offers hooks where other packages are meant to plug in, by calling a generic from a field: `tabular_output()` dispatches on the result's class, so a package that knows another class of table, such as dbplyr's lazy tables, which it pages in the database, registers a method that returns the same kind of output, which every renderer of that kind then draws. How an output looks is no hook of a type at all, since any package can replace the renderer of a kind (below). Otherwise, a package derives a type of its own, naming the other package's type as its parent. No package in the workspace overrides another's block methods today, and the two registrations across packages, blockr.sandbox's methods for blockr.ai's `data_schema()` and `data_effect()` and for blockr.assistant's `describe_result()`, dispatch on result classes and work as before ([blockr.sandbox R/composer.R#L1401-L1418](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/afa235e346145e61af6dd01151b5b14f0ef12549/R/composer.R#L1401-L1418), [R/describe-composed.R#L178-L186](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/afa235e346145e61af6dd01151b5b14f0ef12549/R/describe-composed.R#L178-L186)).

### Registration

The `register_block()` and `register_blocks()` functions keep their arguments but `classes` ([R/block-registry.R#L80](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-registry.R#L80)), and so does the roclet that writes `inst/registry/blocks.yml` from `@block` tags: they take the constructor, as today, and read its type from it, which gives the classes (notes). The `uid` argument sets the name part of the registry id, `{pkg}-{name}`, whose name defaults to the constructor's name without `new_` ([Board objects](Rewrite-1.1.1)). The block registry keeps one entry per type, and `registry_id_from_block()` finds a block's entry by the type the block refers to. Registering no longer builds a block: the block registry reads the type's classes, inputs, UI, the schema its UI ships, requests and options, and its default state from `state` called without args, keeps them by registry id so that R resolves a request without a block, and sends all but the classes to the client ([Board objects](Rewrite-1.1.1#what-lives-where)). A type defined outside a package keeps the code it was defined by, since the constructor `block_constructor()` makes holds none of its type in its own source. The block registry sends that code to the client, wrapped in `block_constructor()`, as the type's definition, which a file holds once for the type, under its registry id ([Serialization](Rewrite-1.1.4#files)): the escape hatch of [Board objects](Rewrite-1.1.1#block-types-outside-a-package). The arg specs default to every state arg, since `external_ctrl_vars()` goes, and describe each for models and tools, while its shape is the schema's ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)).

### Evaluation

R calls a constructor only where an app script builds a board, and where `blockr_deser()` converts a file from today's stack ([Board objects](Rewrite-1.1.1#the-board)), and keeps no block while the app runs. To evaluate a block, it looks the type up by the recipe's registry id and calls the type's functions with the recipe's state and inputs:

- The `validate(x, state)` function checks a state before anything runs and returns `TRUE`, or `FALSE` with an optional `"message"` attribute, on which R runs nothing and replies `invalid` with the message ([Wire protocol](Rewrite-1.1.9)).
- The `interpolate(x, state, inputs)` function builds the expression from the state and the data inputs, a pairlist named by slot, so a variadic block reads its arity off the names. Where the type's `expr_type` is `"bquoted"`, R then replaces each input's placeholder with its slot's symbol, as `eval_impl()` does today ([R/block-server.R#L754-L768](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L754-L768)), so that an `evaluate` of a type's own, such as the plot block's, gets code it can run, and the reply carries that code ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)).
- The `evaluate(x, expr, inputs)` function runs the expression with the data inputs bound.
- The `summary(x, result)` function describes the result in a few words, such as `<data.frame> [150 × 5]`, which R sends with its reply for the header of the block's card ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)). The root type's gives the result's class and dimensions, as `block_summary()` does today ([R/plugin-block.R#L299-L320](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-block.R#L299-L320)), so a front-end has it without asking R again.

R keeps each block's latest result, with its version and expression, in an environment keyed by block id ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)), and binds it as an input of every block downstream, so nothing a type runs may change its inputs in place: copy-on-modify covers most R objects, but not a data.table changed by reference, an environment or an R6 object, whose change would reach the upstream block's result.

### Outputs

A type's `output(x, result, options, info, meta)` returns the result's output for the client: a description in JSON whose `type` names its kind, `{pkg}-{name}` as a registry id is, with whatever else that kind holds, and at most one binary body with its MIME type, such as a plot's PNG ([Wire protocol](Rewrite-1.1.9#outputs)). A kind is a shape that the package defining it documents, as a MIME type is: core defines `blockr.core-table`, a table's columns, the rows of one page and its total row count, `blockr.core-text` and `blockr.core-plot`. What draws an output is a renderer, a module that a package declares in R for the kinds it draws, of which R picks one per kind, from the app's blockr options, the front-end, other packages and the package that defines the kind, in that order ([Front-ends and extension points](Rewrite-1.1.8#renderers)). So a block type never names what draws its output, and blockr.ui's table preview takes the place of core's plain table for every block whose output is a table.

The `meta` is what the renderer keeps and R reads, such as the page a table shows and its sort, which the renderer changes through its host, asking R for the output again, so an output of kind `blockr.core-table` holds the page `meta` asks for, sorted as it says, with `n_rows` rows to a page unless it gives a page size. A renderer draws an output nested in its own through its host, with the renderer R picked for the nested output's kind. The output blockr.dm draws today through `block_ui()` and `block_output()` methods ([R/dm-block.R#L504-L627](https://github.com/BristolMyersSquibb/blockr.dm/blob/8b37981838cfac63a5d40e270a19857e5ef9ea90/R/dm-block.R#L504-L627)) becomes, with illustrative names, an output of a kind of its own, whose renderer draws the diagram and has the selected table drawn by the app's renderer for tables:

```r
dm_block <- block_type(
  "dm_block",
  parent = transform_block,
  # inputs, state, ui and interpolate left out
  output = function(x, result, options, info, meta) {
    list(
      type    = "blockr.dm-dm",
      diagram = dm_keylines_meta(result),
      preview = if (length(meta$table)) tabular_output(result[[meta$table]], options, info, meta)
    )
  }
)

register_renderer("dm", js_module("dm-output.js"), kinds = "blockr.dm-dm")   # in .onLoad()
```

### Generics

| Generic | Becomes |
|---|---|
| `block_output(x, result, session)` | the type's `output`, returning an output whose kind a renderer draws (above) |
| `block_ui(id, x)`, `block_render_trigger()` | gone, since a renderer draws the output and options are arguments |
| `tabular_output(x, result, block, session)` | `tabular_output(result, options, info, meta)`, dispatching on the result rather than a display and returning an output of kind `blockr.core-table` (above) |
| `tabular_display()`, `tabular_ui()`, `tabular_trigger()`, `tabular_options()` | gone, with the display classes and the `tabular_display` blockr option, since a renderer of `blockr.core-table` takes a display's place, with the board options it brings (above) |
| `block_eval(x, expr, env, ...)` | the type's `evaluate` |
| none | the type's `validate` and `interpolate` |
| `block_eval_trigger()` | gone, since options never re-evaluate and any component can invalidate a block |
| `board_options(x)` | the type's `options`, while a board class keeps its own `board_options()` method |
| `blockr_ser()`, `blockr_deser()` | kept, `blockr_ser()` to write a script's board and `blockr_deser()` to convert files from today's stack, while a file of the new stack migrates through the type's `migrate` |
| `block_summary(x, data)` | the type's `summary`, which R sends with every evaluation's reply (above) |
| `block_server()`, `expr_server()`, `expr_ui()` | gone |
| `block_inputs(x)` | the type's `inputs` |
| `external_ctrl_vars(x)` | gone |
| `block_metadata(x, fields)` | the type's entry in the block registry, read by registry id |
| `str_value(x)` | kept for printing R objects, without the `*` that marks the args `external_ctrl_vars()` names, while blockr.assistant, which describes a board to a model with it, runs its agent loop in the browser ([Assistant as a client extension](Rewrite-1.4)) |

### JS-driven blocks

The JS-driven blocks of blockr.dplyr are close to this already: `new_select_block()` passes `state` and `expr_fn` to its factory, `new_js_transform_block()`, whose server only keeps JS and R in step ([R/select_block.R#L29-L52](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/68e1b54d2d1e028c96b77d03f8887b12b6d872b8/R/select_block.R#L29-L52)). Under the contract the factory becomes a parent type and its server goes, the JS becomes a module, `expr_fn` the type's `interpolate`, and the columns the JS receives as messages a request.

### Testing

Core ships helpers to test a block type without Shiny: its `validate`, `interpolate` and `evaluate` with sample states and inputs, its requests, its `output`, and its module against a stub host. They replace `testServer()`. A type's R tests and its module tests share one fixture file in its package's `tests/`, since the type's two halves meet only in JSON: the file lists states, the R tests record into it what the type's requests answer on sample inputs and check that `interpolate` builds code that runs for each state, and the module tests serve the recorded answers through the stub host and check that the module submits only listed states, the pattern of consumer-driven contract tests ([Pact](https://docs.pact.io/)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

A type defined outside a package, where the caller's `topenv()` is no namespace, keeps the call `block_type()` was made with, from `match.call()`, rather than having its value written out later. Written out, a field such as `parent` takes the whole parent type in the internal layout of the core that saved it, where the developer wrote `transform_block`, and a later core may lay it out differently. The definition is that call wrapped in `blockr.core::block_constructor()`, with the package objects it names qualified, `transform_block` as `blockr.core::transform_block`, and a parent type the script defines written as its own call, nested. Nothing else the call or its functions take from the script, such as a helper or a data frame, can go into a file, so `block_type()` warns about each such name when the type is defined, finding them with `codetools::findGlobals()` and resolving them from the caller's environment. A UI the type names by file is a plain JS module, which goes into the definition as the file's text, so that a file brings the UI along, since core loads JS only ([UI modules in JS](Rewrite-1.1.7#packaging)).

Today `register_block()` builds a block to read its classes and, without `arguments`, its arg specs, and checks the specs' examples against it ([R/block-registry.R#L143-L162](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-registry.R#L143-L162)). The type gives the first two, and the examples are checked against `state()` instead.

</details>
