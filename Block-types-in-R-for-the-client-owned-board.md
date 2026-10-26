Status: draft. Design for [Client-owned board state](Client-owned-board-state).

One of the API proposals for the client-owned board ([Client-owned board state](Client-owned-board-state)): how a package defines and registers a block type in R. It shapes the block type contract ([blockr.core#397](https://github.com/BristolMyersSquibb/blockr.core/issues/397)), a block type's output ([blockr.core#401](https://github.com/BristolMyersSquibb/blockr.core/issues/401)) and the registry export ([blockr.core#396](https://github.com/BristolMyersSquibb/blockr.core/issues/396)). The input elements a UI is composed of are the UI-in-R proposal ([Input elements](Input-elements-for-block-UIs-written-in-R)), and JS modules for richer UIs are the UI modules proposal ([UI modules in JS](UI-modules-in-JS)).

## What must hold

1. A block type is defined once, as a value, and the constructor made from it returns an S3 block whose args are the block's state; types are registered as today, under a registry id ([Document model](Document-model-for-the-client-owned-board)).
2. Its R side is plain functions, with no Shiny module server and no reactives.
3. A package can define a block type in R alone.
4. The generics packages implement today keep working wherever they still have a job.
5. Nothing about a type is copied into its blocks, and nothing builds a block to learn about its type.
6. A package plugs into another package's type only through a hook that type offers, or by deriving a type of its own.

## Today

A block type calls `new_block(server, ui, class, ctor, ctor_pkg, dat_valid, allow_empty_state, block_name, expr_type, external_ctrl, block_metadata, ...)` or one of its specializations ([R/block-class.R#L180](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L180)). The server is a Shiny module whose formals name the data inputs and which returns `expr`, a reactive expression, and `state`, reactives naming every constructor formal ([R/block-server.R#L969](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L969)). The head block keeps its args in `reactiveVal()`s, syncs them with its inputs through observers, and caps `n` at the number of rows with `updateNumericInput()` ([R/transform-head.R#L27-L91](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/transform-head.R#L27-L91)).

## Proposal

### The block type

A block type is a value made by `block_type()`, holding everything that is the same for every block of the type, and its constructor is a function that `block_constructor()` makes from it. The head block, written to the new contract, with illustrative names for the input elements:

```r
head_block <- block_type(
  "head_block",
  parent      = transform_block,
  inputs      = "data",
  state       = function(n = 6L, direction = c("head", "tail")) {
    list(n = n, direction = match.arg(direction))
  },
  ui          = block_inputs(
    numeric_input("n", "Number of rows", min = 1L, max = \(data) nrow(data)),
    switch_input("direction", "Tail", on = "tail", off = "head")
  ),
  interpolate = function(x, state, inputs) {
    fn <- if (identical(state$direction, "tail")) quote(utils::tail) else quote(utils::head)
    bbquote(.(fn)(.(data), n = .(n)), list(fn = fn, n = state$n))
  },
  dat_valid   = function(x, data) stopifnot(is.data.frame(data))
)

new_head_block <- block_constructor(head_block)
```

The constructor has the formals of `state` and a `name`, so an app script calls `new_head_block(n = 10L)` as today, and the checks in `state`, such as `match.arg()`, run when it does. It returns a block that holds its state and its name and refers to its type, which every head block shares and none copies. A package exports both: the type, which other types can name as their parent, and the constructor, which app scripts call. An abstract type, such as `transform_block`, has no constructor.

A type's fields:

- The `class` and `parent` arguments give the type's class, which with its parent's makes a block's class vector, `c("head_block", "transform_block", "block")`, and the type it inherits from. A field the type leaves out comes from its parent.
- The `state` field is a function from the constructor's args to the block's state, with their defaults and checks. Called without args, it gives the state a new block starts with.
- The `inputs` field names the data input slots, `"data"`, `c("x", "y")` for a merge, or `"...args"` for a variadic block. Every concrete type declares its own, since arity is not what a parent such as `transform_block` stands for.
- The `ui` field takes the input elements composed in R or a JS module (`js_module("filter-block.js")`). A function in an element's attribute, such as `max = \(data) nrow(data)`, becomes a request of the type ([Input elements](Input-elements-for-block-UIs-written-in-R)), and the `requests` field takes a named list of further R functions for whatever else the UI asks of R, whose arguments name the inputs and state args they read.
- The `expr` field takes a template, with `.(arg)` placeholders for state args and the inputs referred to as `expr_type` says, by `.(data)` placeholders or by symbol, as today, which the root type's `interpolate` fills in. A type whose expression changes shape with its state or its data, as the head block's does with its direction, gives an `interpolate` of its own instead.
- The `validate`, `interpolate` and `evaluate` fields are the functions R evaluates a block with (below).
- The `output` field describes a result for the client ([blockr.core#401](https://github.com/BristolMyersSquibb/blockr.core/issues/401)), and the `options` field lists the board options the type ships ([Document model](Document-model-for-the-client-owned-board)).
- The `eager` field, `FALSE` by default, has a block of the type demanded even in a board that evaluates lazily ([Evaluation in the client](Evaluation-in-the-client)), as a block that writes a file needs. It takes `TRUE` or a function of the state, so that a write block is demanded only while its auto mode is on.
- The `dat_valid` and `expr_type` fields stay as they are, while `allow_empty_state`, `external_ctrl` and `block_metadata` go: the root type's `validate` accepts every state, every block's state can now be set from outside, and a type's metadata comes from its registration (below).

Every function field takes the type as its first argument, `x`, as an S3 method takes its object, so that the root type's `interpolate` can fill in the template a child gives as `expr`, and a field can call its parent's, `x$parent$output(x, ...)`, as a method calls `NextMethod()`. A type's `options` add to its parent's instead of replacing them, as `board_options()` methods combine with `NextMethod()` today. The `block_type()` function checks a type when it is defined, such as that no input slot and state arg share a name ([Input elements](Input-elements-for-block-UIs-written-in-R)), so no block is checked for being well formed again.

### Core's types and hooks

Core's root type, `block`, gives every field its default: `validate` accepts every state, `interpolate` fills in `expr`, `evaluate` runs the expression with the inputs bound, as `block_eval()` and `eval_env()` do today, and `output` prints the result. The specializations become types without constructors, which a package names as its parent:

```r
transform_block <- block_type(
  "transform_block",
  parent  = block,
  output  = function(x, result, options, info, meta) tabular_output(result, options, info, meta),
  options = tabular_options(tabular_display())
)
```

The other specializations, `data_block`, `parser_block`, `plot_block`, `text_block` and `file_block`, follow with the output and options of their kind, and `plot_block` with an `evaluate` that uses `evaluate::evaluate()`, as core's plot block evaluates today.

A type's fields belong to its package, so another package cannot change a type in place, as an S3 method registered for the type's class can today. Instead, a type offers hooks where other packages are meant to plug in, by calling a generic from a field: `tabular_output()` dispatches on the result's class, so a package that adds a kind of table, such as a gt table, registers `tabular_output.gt_tbl()`, as `tabular_display()` lets a package add a display today. Otherwise, a package derives a type of its own, naming the other package's type as its parent. No package in the workspace overrides another's block methods today, and the one registration across packages, blockr.sandbox's methods for blockr.ai's `data_schema()` and `data_effect()`, dispatches on result classes and works as before ([blockr.sandbox R/composer-ai-view.R#L139-L160](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/4a4cac59d159ea19ef42b943fece7ca9db0deca5/R/composer-ai-view.R#L139-L160)).

### Registration

The `register_block()` and `register_blocks()` functions keep their arguments ([R/block-registry.R#L80](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-registry.R#L80)), and so does the roclet that writes `inst/registry/blocks.yml` from `@block` tags: they take the constructor, as today, and read its type from it. The `uid` argument sets the name part of the registry id, `{pkg}-{name}`, whose name defaults to the constructor's name without `new_` ([Document model](Document-model-for-the-client-owned-board)). The registry keeps one entry per type, and `registry_id_from_block()` finds a block's entry by the type the block refers to. Registering no longer builds a block: the registry reads the type's classes, inputs, UI, requests, options and eagerness, and its default state from `state` called without args, keeps them by registry id so that R resolves a request without a block, and exports them to the client ([blockr.core#396](https://github.com/BristolMyersSquibb/blockr.core/issues/396)). A type defined in a script is one value, which a file holds as R source, the escape hatch of [Document model](Document-model-for-the-client-owned-board). The arg specs default to every state arg, since `external_ctrl_vars()` goes.

### Evaluation

R calls a constructor only where a board is built, in an app script and when a board is opened ([Document model](Document-model-for-the-client-owned-board)), and keeps no block while the app runs. To evaluate a block, it looks the type up by the recipe's registry id and calls the type's functions with the recipe's state and inputs:

- The `validate(x, state)` function checks a state before anything runs and returns `TRUE`, or `FALSE` with an optional `"message"` attribute, on which R runs nothing and replies `invalid` with the message ([Wire protocol](Wire-protocol-between-the-client-and-R)).
- The `interpolate(x, state, inputs)` function builds the expression from the state and the data inputs, a pairlist named by slot, so a variadic block reads its arity off the names.
- The `evaluate(x, expr, data)` function runs the expression with the data inputs bound.

R keeps each block's latest result, with its version and expression, in an environment keyed by block id ([blockr.core#400](https://github.com/BristolMyersSquibb/blockr.core/issues/400)).

### Generics

| Generic | Becomes |
|---|---|
| `block_output(x, result, session)` | the type's `output`, returning a description for the client ([blockr.core#401](https://github.com/BristolMyersSquibb/blockr.core/issues/401)) |
| `block_ui(id, x)`, `block_render_trigger()` | gone, since the output's client side draws it and options are arguments |
| `block_eval(x, expr, env, ...)` | the type's `evaluate` |
| none | the type's `validate` and `interpolate` |
| `block_eval_trigger()` | gone, since options never re-evaluate and any component can invalidate a block |
| `board_options(x)` | the type's `options`, while a board class keeps its own `board_options()` method |
| `blockr_ser()`, `blockr_deser()` | kept, for files and migrations |
| `block_summary(x, data)` | a request of every block type, answered from the result, for the card's header |
| `block_server()`, `expr_server()`, `expr_ui()` | gone |
| `block_inputs(x)` | the type's `inputs` |
| `external_ctrl_vars(x)` | gone |

### JS-driven blocks

The JS-driven blocks of blockr.dplyr are close to this already: `new_select_block()` passes `state` and `expr_fn` to its factory, `new_js_transform_block()`, whose server only keeps JS and R in step ([R/select_block.R#L29-L52](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/68e1b54d2d1e028c96b77d03f8887b12b6d872b8/R/select_block.R#L29-L52)). Under the contract the factory becomes a parent type and its server goes, the JS becomes a module, `expr_fn` the type's `interpolate`, and the columns the JS receives as messages a request.

### Testing

Core ships helpers to test a block type without Shiny: its `validate`, `interpolate` and `evaluate` with sample states and inputs, its requests, its `output`, and its module against a stub host. They replace `testServer()`.

## Open questions

- Whether the card's summary is a request, as proposed, or part of every evaluation reply.
