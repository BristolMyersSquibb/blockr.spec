# Block types in R for the client-owned board
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how a package defines and registers a block type in R, and how R evaluates a block with it. It shapes defining block types, a block type's output, exporting the block registry, the per-session evaluator and the guide for block type authors, each an item in the Work list of [Client-owned board state](Rewrite-1.1#work). A block type's UI, a module that meets the contract, is the UI modules proposal ([UI modules in JS](Rewrite-1.1.7)), the messages that carry a block's recipe and its result are the [wire protocol proposal](Rewrite-1.1.9), how state values travel between the client and R is the [serialization proposal](Rewrite-1.1.4), which renderer draws an output is [Front-ends and extension points](Rewrite-1.1.8#renderers)'s, and when a block is evaluated is the [evaluation proposal](Rewrite-1.1.10).

## What must hold

1. A block type is defined once, as a value, and the constructor made from it returns an S3 block whose args are the block's state; types are registered as today, under a registry id ([Board objects](Rewrite-1.1.1)).
2. Its R side is plain functions, with no Shiny module server and no reactives.
3. The generics packages implement today keep working wherever they still have a job.
4. Nothing about a type is copied into its blocks, and nothing builds a block to learn about its type.
5. A package plugs into another package's type only through a hook that type offers, or by deriving a type of its own.
6. A front-end or any other package can replace how core draws an output family, such as tables, without changing a block type.

## Today

A block type calls `new_block(server, ui, class, ctor, ctor_pkg, dat_valid, allow_empty_state, block_name, expr_type, external_ctrl, block_metadata, ...)` or one of its specializations ([R/block-class.R#L180](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L180)). The server is a Shiny module whose formals name the data inputs and which returns `expr`, a reactive expression, and `state`, reactives naming every constructor formal ([R/block-server.R#L969](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L969)). The head block keeps its args in `reactiveVal()`s, syncs them with its inputs through observers, and caps `n` at the number of rows with `updateNumericInput()` ([R/transform-head.R#L27-L91](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/transform-head.R#L27-L91)).

## Proposal

### The block type

A block type is a value made by `block_type()`, holding everything that is the same for every block of the type, and its constructor is a function that `block_constructor()` makes from it. A type's `expr` is a function of the block's state args that returns the block's expression, in which each input appears by its name, and which R evaluates with the inputs bound (below). The head block, written to the new contract, with illustrative names:

```r
head_block <- block_type(
  "head_block",
  parent    = transform_block,
  inputs    = "data",
  expr      = function(n = 6L, direction = c("head", "tail")) {
    direction <- match.arg(direction)
    fn <- if (direction == "tail") quote(utils::tail) else quote(utils::head)
    bquote(.(fn)(data, n = .(n)))
  },
  ui        = js_module("head-block.js"),
  requests  = list(n_max = function(data) nrow(data)),
  dat_valid = function(data) stopifnot(is.data.frame(data))
)

new_head_block <- block_constructor(head_block)
```

The constructor has the formals of `expr`, a `block_name` and `...`, so an app script calls `new_head_block(n = 10L)` as today, and the checks in `expr`, such as `match.arg()`, run when it does: it calls `expr` with its args and takes the block's state from the frame `expr` ran in, as the checks left it, `list(n = 10L, direction = "head")` (notes). It returns a block that holds its state, its name and the attributes `...` passes, such as the dock's `visible` ([Board objects](Rewrite-1.1.1#blocks)), and refers to its type, which every head block shares and none copies. The name keeps today's argument, `block_name`, since `attr()` matches attribute names partially: on a block, a list of its state, that has no `name` attribute, `attr(blk, "name")` returns the block's `names`, as it did when `new_block()` took a `name`. A package exports both: the type, which other types can name as their parent, and the constructor, which app scripts call. An abstract type, such as `transform_block`, has no `inputs`, no `expr` and no constructor.

A type's fields:

- The `class` and `parent` arguments give the type's class, which with its parent's makes a block's class vector, `c("head_block", "transform_block", "block")`, and the type it inherits from. A field the type leaves out comes from its parent.
- The `inputs` field names the data inputs, `"data"`, `c("x", "y")` for a merge, or `"..."` for a variadic block. Every concrete type declares its own, since arity is not what a parent such as `transform_block` stands for. A block runs only once every input is linked, and a variadic block once it has one link, which the client sees from the block registry, marking the block `waiting` until then without asking R ([Evaluation in the client](Rewrite-1.1.10#statuses)).
- The `expr` field is a function whose formals are the state args and whose body checks them, as a constructor checks its args today, and returns the block's expression (below). An arg without a default starts unset, as a merge's `by` does, and stays out of the block's state until something sets it. Called without args, `expr` gives the state a new block starts with, which may be one that cannot run yet (below).
- The `ui` field names the type's UI, a module written against the contract of [UI modules in JS](Rewrite-1.1.7), in plain TypeScript as core's own are or in TSX with React, which ships the schema of the block's state beside it ([UI modules in JS](Rewrite-1.1.7#packaging)), and the `requests` field takes a named list of R functions for whatever the UI asks of R, such as the head block's `n_max`, whose arguments name the inputs and state args they read and any parameters the UI passes (below).
- The `evaluate` and `summary` fields are the functions R runs a block's expression and describes its result with (below).
- The `output` field describes a result for the client, as an output of a family that a renderer draws (below), and the `options` field names the board options its blocks use, by the constructors that give each option's id and initial value, while the package that ships an option defines it in the client ([Board objects](Rewrite-1.1.1)).
- The `migrate` field maps a state saved by an older version of the type's package to the current state, given that version, and R runs it on the state a file holds when it opens a board ([Serialization](Rewrite-1.1.4#migrations)). The root type's leaves a state as it is.
- The `dat_valid` field stays, with its arguments bound by name, as a request's are (below), so that it can read state args as well as inputs, such as to say that a chosen column is missing from the data.
- The `allow_empty_state`, `external_ctrl`, `expr_type` and `block_metadata` fields go. A state arg a block needs has no default, any other state that cannot run yet is for a type's `expr` to say (below), and a block waits for its inputs (above), so the glue block, which today renders its text with nothing linked, waits for a link. Every block's state can now be set from outside, every expression names its inputs, as a `"quoted"` one does today, and a type's metadata comes from its registration (below).

A type has no say in when its blocks are evaluated: a block that must run with nothing on screen, such as a write block in auto mode, is demanded by a rule its package registers in the client ([Evaluation in the client](Rewrite-1.1.10#demand)).

The functions R runs a block's expression and outputs its result with, `evaluate`, `summary` and `output`, take the type as their first argument, `x`, as an S3 method takes its object, so that a field can call its parent's, `x$parent$output(x, ...)`, as a method calls `NextMethod()`. The other function fields name what they read instead: `expr` the state args, a request the inputs and state args it reads, `migrate` the state and the version that saved it, and `dat_valid` the inputs and state args it reads. A type's `options` add to its parent's instead of replacing them, as `board_options()` methods combine with `NextMethod()` today. The `block_type()` function checks a type when it is defined, so that no block is checked for being well formed again: that no state arg is `...` or `block_name`; that no input shares a state arg's name, since a request's arguments would not say which they mean; that the arguments of `dat_valid` and of each request name inputs or state args, but for a request's parameters, which have a default; that `expr`, called without args, returns an expression or cannot run yet; and, once it reads the schema the type's UI ships, that the schema's properties are the state args. All but the last two read only `inputs` and the formals of the functions.

A sketch of `block_type()`, in which a field a type leaves out is its parent's and the checks run for every type with an `expr`:

```r
block_type <- function(class, parent = NULL, inputs = NULL, expr = NULL,
                       ui = NULL, requests = NULL, dat_valid = NULL,
                       evaluate = NULL, summary = NULL, output = NULL,
                       options = list(), migrate = NULL) {

  own <- Filter(Negate(is.null), list(
    inputs = inputs, expr = expr, ui = ui, requests = requests,
    dat_valid = dat_valid, evaluate = evaluate, summary = summary,
    output = output, migrate = migrate
  ))

  type <- if (is.null(parent)) list() else unclass(parent)  # a field left out is the parent's
  type[names(own)] <- own
  type$class <- c(class, parent$class)
  type$parent <- parent
  type$options <- c(parent$options, options)

  if (!is.null(type$expr)) {
    state_args <- names(formals(type$expr))
    known <- c(type$inputs, state_args)
    stopifnot(
      "no state arg is ... or block_name" = !any(c("...", "block_name") %in% state_args),
      "no input shares a state arg's name" = !any(type$inputs %in% state_args),
      "dat_valid names only inputs and state args" =
        is.null(type$dat_valid) || all(names(formals(type$dat_valid)) %in% known)
    )
    for (f in type$requests) {
      params <- setdiff(names(formals(f)), known)
      stopifnot("a request's other args are parameters, with defaults" =
        all(nzchar(vapply(formals(f)[params], deparse1, ""))))
    }
    res <- tryCatch(type$expr(), invalid = function(e) NULL, missingArgError = function(e) NULL)
    stopifnot("expr() gives an expression" = is.null(res) || is.language(res) || is.character(res))
    # and, once it reads the schema the UI ships, that its properties are the state args
  }

  if (!isNamespace(topenv(parent.frame()))) {
    attr(type, "call") <- match.call()  # the type's definition, for a file (notes)
  }

  structure(type, class = "block_type")
}
```

A sketch of `block_constructor()`, which takes the block's state from the frame `expr` ran in and leaves out an arg that is still unset, with `invalid()`:

```r
block_constructor <- function(type) {

  stopifnot("an abstract type has no constructor" = !is.null(type$expr))

  args <- formals(type$expr)
  state_args <- as.character(names(args))
  has_default <- nzchar(vapply(args, deparse1, ""))

  build <- function(env) {  # env is the constructor's frame
    given <- Filter(function(arg) !eval(call("missing", as.name(arg)), env), state_args)
    frame <- NULL
    framed <- type$expr     # a copy of expr that hands over its frame as it exits
    body(framed) <- bquote({
      on.exit(.(function(e) frame <<- e)(environment()))
      .(body(type$expr))
    })
    tryCatch(
      do.call(framed, mget(given, env), quote = TRUE),
      invalid = function(e) NULL, missingArgError = function(e) NULL
    )
    unset <- vapply(state_args, function(arg) eval(call("missing", as.name(arg)), frame), NA)
    block <- structure(
      mget(state_args[has_default | !unset], frame),  # the state, as the checks left it
      block_name = env$block_name, block_type = type, class = type$class
    )
    attrs <- eval(quote(list(...)), env)
    attributes(block)[names(attrs)] <- attrs
    block
  }

  ctor <- function() build(environment())
  formals(ctor) <- c(args, alist(block_name = NULL, ... = ))
  ctor
}

invalid <- function(message) {
  stop(structure(class = c("invalid", "error", "condition"), list(message = message, call = NULL)))
}
```

### Expressions

What a type's `expr` returns is the block's expression: a call, which its author builds with any tool, `bquote()`, `rlang::expr()` or `call()`, or a string, such as from `sprintf()`, which R parses. Each input appears in it by its name, and only the state is put into it, so that the head block's expression for `n = 10L` is `utils::head(data, n = 10L)` whatever block it is linked to, and R evaluates it with `data` bound to the upstream block's result, as core evaluates a block today (below). R runs exactly that expression, so the code a block shows and exports is the code that ran. Since `expr` never sees an input's data, a type whose expression depends on the data says so in the expression, as `utils::head(data, n = min(10L, nrow(data)))` caps `n` at the rows it gets, or gets what it needs into its state through a request. R calls `expr` with the args the block's state holds, so a body that uses an unset arg makes R reply `invalid`, naming the arg, as the merge block's does until its `by` is set:

```r
merge_block <- block_type(
  "merge_block",
  parent   = transform_block,
  inputs   = c("x", "y"),
  expr     = function(by, all_x = FALSE, all_y = FALSE) {
    bquote(merge(x, y, by = .(by), all.x = .(all_x), all.y = .(all_y)))
  },
  requests = list(shared = function(x, y) intersect(names(x), names(y)))
)
```

A body that can do without an unset arg tests it with `missing()`, as a merge by the columns its inputs share would with `if (missing(by)) quote(merge(x, y))`, and a body given a state that is set but cannot run signals `invalid()` with a message, such as `invalid("Choose at least one column.")` for a selection the user emptied.

A variadic block's expression stands for its inputs with `...`, which R replaces with the ids of the upstream blocks, in link order and named by link, so that `quote(rbind(...))` gives `rbind(a, b2 = b, c)`. Unlike an input's name, `...` cannot be a column, so putting the ids in its place has none of the ambiguity that defeated substituting names in [blockr.core#17](https://github.com/BristolMyersSquibb/blockr.core/issues/17#issuecomment-2630544662).

### Requests

A request is a function the UI calls through its host for whatever it needs from R, such as the head block's `n_max`, the maximum of its numeric input, which never enters the block's state ([UI modules in JS](Rewrite-1.1.7#the-contract)). R binds each of its arguments by name: an input to the result of the upstream block at the version the UI's context names, a state arg to the value the UI passes or else the block's state, leaving an unset one missing, and any other argument to a parameter the UI passes, which must have a default, so that `block_type()` still catches a misspelled state arg written without one, as a state arg in a request needs none. A parameter holds only what the UI is showing, such as the column whose values a dropdown lists or the text typed into its search, never what the block computes. That holds by construction, since only requests take parameters and `expr` never sees them, so no parameter changes a block's result, expression or saved state:

```r
requests = list(
  values   = function(data, column = NULL, query = "", limit = 1000L) column_values(data, column, query, limit),
  list_dir = volatile(function(path = "") list_dir(path))
)
```

Core keeps each answer by registry id, name, state args, parameters and the versions of the inputs read, as a snapshot of them, so that reopening a column's dropdown is answered without asking R, and data that changes behind an input, such as a database's, is read again once something invalidates the block that reads it ([Evaluation in the client](Rewrite-1.1.10#invalidation)). A request wrapped in `volatile()` is never kept and goes to R every time, which suits a cheap lookup outside the board, such as a directory listing, and nothing expensive.

### Core's types and hooks

Core's root type, `block`, gives every field but `inputs` and `expr` its default: `evaluate` runs the expression with the inputs bound, as `block_eval()` and `eval_env()` do today, `summary` gives the result's class and dimensions, and `output` prints the result, as an output of the family `blockr.core-text` (below). The specializations become types without `inputs`, `expr` or constructors, which a package names as its parent:

```r
transform_block <- block_type(
  "transform_block",
  parent  = block,
  output  = function(x, result, options, info, meta) tabular_output(result, options, info, meta),
  options = list(new_n_rows_option)
)
```

The other specializations, `data_block`, `parser_block`, `plot_block`, `text_block` and `file_block`, follow with their own output and options, and `plot_block` with an `evaluate` that uses `evaluate::evaluate()`, as core's plot block evaluates today, and an `output` that draws the recorded plot at the size and in the theme `info` gives, as an output of the family `blockr.core-plot`, where today the block re-evaluates when the theme changes ([R/plot-block.R#L59-L68](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plot-block.R#L59-L68)).

A type's fields belong to its package, so another package cannot change a type in place, as an S3 method registered for the type's class can today. Instead, a type offers hooks where other packages are meant to plug in, by calling a generic from a field: `tabular_output()` dispatches on the result's class, so a package that knows another class of table, such as dbplyr's lazy tables, which it pages in the database, registers a method that returns an output of the same family, which every renderer of that family then draws. How an output looks is no hook of a type at all, since any package can replace the renderer of an output family (below). Otherwise, a package derives a type of its own, naming the other package's type as its parent. No package in the workspace overrides another's block methods today, and the two registrations across packages, blockr.sandbox's methods for blockr.ai's `data_schema()` and `data_effect()` and for blockr.assistant's `describe_result()`, dispatch on result classes and work as before ([blockr.sandbox R/composer.R#L1401-L1418](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/afa235e346145e61af6dd01151b5b14f0ef12549/R/composer.R#L1401-L1418), [R/describe-composed.R#L178-L186](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/afa235e346145e61af6dd01151b5b14f0ef12549/R/describe-composed.R#L178-L186)).

### Registration

The `register_block()` and `register_blocks()` functions keep their arguments but `classes` ([R/block-registry.R#L80](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-registry.R#L80)), and so does the roclet that writes `inst/registry/blocks.yml` from `@block` tags: they take the constructor, as today, and read its type from it, which gives the classes (notes). The `uid` argument sets the name part of the registry id, `{pkg}-{name}`, whose name defaults to the constructor's name without `new_` ([Board objects](Rewrite-1.1.1)). The block registry keeps one entry per type, and `registry_id_from_block()` finds a block's entry by the type the block refers to. Registering no longer builds a block: the block registry reads the type's classes and inputs, its UI and the schema the UI ships, its requests and options, and its default state from `expr` called without args, keeps them by registry id so that R resolves a request without a block, and sends all but the classes to the client ([Board objects](Rewrite-1.1.1#what-lives-where)). A type defined outside a package keeps the code it was defined by, since the constructor `block_constructor()` makes holds none of its type in its own source. The block registry sends that code to the client, wrapped in `block_constructor()`, as the type's definition, which a file holds once for the type, under its registry id ([Serialization](Rewrite-1.1.4#files)): the escape hatch of [Board objects](Rewrite-1.1.1#block-types-outside-a-package). The arg specs default to every state arg, since `external_ctrl_vars()` goes, and describe each for models and tools, while its shape is the schema's ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)).

### Evaluation

R calls a constructor only where an app script builds a board, and where `blockr_deser()` converts a file from today's stack ([Board objects](Rewrite-1.1.1#the-board)), and keeps no block while the app runs. To evaluate a block, it looks the type up by the recipe's registry id, calls its `expr` with the recipe's state, which gives the block's expression, and evaluates that with each input's name bound to the result of the upstream block it comes from, as today, and a variadic block's with the upstream ids in place of `...` (above). A script binds the same names, as `b <- local({ data <- a; utils::head(data, n = 10L) })`, so that the expression R runs is the one a script holds for the block, labels included, such as the column names `cbind()` takes from its arguments, where today a block whose `expr_type` is `"bquoted"` is evaluated with its inputs' names and exported with the upstream ids in their place ([R/block-server.R#L754-L768](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L754-L768), [R/utils-code.R#L58-L69](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-code.R#L58-L69)). An `invalid()` that `expr` signals, or an unset arg its body uses, makes R run nothing and reply `invalid`, with the message or the arg's name. Otherwise R runs the expression, which its reply carries ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)):

- The `evaluate(x, expression, inputs)` function runs the expression with each input's upstream result bound to the input's name, or to the upstream block's id for a variadic block's. The root type's runs it as it is, and `plot_block`'s records the plot.
- The `summary(x, result)` function describes the result in a few words, such as `<data.frame> [150 × 5]`, which R sends with its reply for the header of the block's card ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)). The root type's gives the result's class and dimensions, as `block_summary()` does today ([R/plugin-block.R#L299-L320](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-block.R#L299-L320)), so a front-end has it without asking R again.

R keeps each block's latest result, with its version and expression, in an environment keyed by block id ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)), and binds it as an input of every block downstream, so nothing a type runs may change its inputs in place: copy-on-modify covers most R objects, but not a data.table changed by reference, an environment or an R6 object, whose change would reach the upstream block's result.

### Outputs

A type's `output(x, result, options, info, meta)` returns the result's output for the client: a description in JSON whose `family` lists its output families, each `{pkg}-{name}` as a registry id is, most specific first, as an R class vector lists classes, with whatever else they hold, and at most one binary body with its MIME type, such as a plot's PNG ([Wire protocol](Rewrite-1.1.9#outputs)). An output family is what such a description holds, which the package defining the family documents, as a MIME type's owner does: core defines `blockr.core-table`, a table's columns, the rows of one page and its total row count, `blockr.core-text` and `blockr.core-plot`. What draws an output is a renderer, a module that a package declares in R for the output families it draws, of which R picks one per family, from the app's blockr options, the front-end, other packages and the package that defines the family, in that order ([Front-ends and extension points](Rewrite-1.1.8#renderers)). An output family may extend another, as a `blockr.dm-lazy_table` would extend `blockr.core-table`: its outputs hold everything the parent's hold and only add to it, such as the SQL behind a page of rows, and list both families, so that the client draws one with the renderer R picked for the first of its families that has one, and a renderer that knows only tables draws it as a table. So a block type never names what draws its output, and blockr.ui's table preview takes the place of core's plain table for every block whose output is a table.

The `meta` is what the renderer keeps and R reads, such as the page a table shows and its sort, which the renderer changes through its host, asking R for the output again, so an output of the family `blockr.core-table` holds the page `meta` asks for, sorted as it says, with `n_rows` rows to a page unless it gives a page size. A renderer draws an output nested in its own through its host, with the renderer R picked for the nested output's family. The output blockr.dm draws today through `block_ui()` and `block_output()` methods ([R/dm-block.R#L504-L627](https://github.com/BristolMyersSquibb/blockr.dm/blob/8b37981838cfac63a5d40e270a19857e5ef9ea90/R/dm-block.R#L504-L627)) becomes, with illustrative names, an output of a family of its own, whose renderer draws the diagram and has the selected table drawn by the app's renderer for tables:

```r
dm_block <- block_type(
  "dm_block",
  parent = transform_block,
  # expr, ui and requests left out
  output = function(x, result, options, info, meta) {
    list(
      family  = "blockr.dm-dm",
      diagram = dm_keylines_meta(result),
      preview = if (length(meta$table)) tabular_output(result[[meta$table]], options, info, meta)
    )
  }
)

register_renderer("dm", js_module("dm-output.js"), families = "blockr.dm-dm")   # in .onLoad()
```

### Generics

| Generic | Becomes |
|---|---|
| `block_output(x, result, session)` | the type's `output`, returning an output whose family a renderer draws (above) |
| `block_ui(id, x)`, `block_render_trigger()` | gone, since a renderer draws the output and options are arguments |
| `tabular_output(x, result, block, session)` | `tabular_output(result, options, info, meta)`, dispatching on the result rather than a display and returning an output of the family `blockr.core-table` (above) |
| `tabular_display()`, `tabular_ui()`, `tabular_trigger()`, `tabular_options()` | gone, with the display classes and the `tabular_display` blockr option, since a renderer of `blockr.core-table` takes a display's place, with the board options it brings (above) |
| `block_eval(x, expr, env, ...)` | the type's `evaluate` |
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

The JS-driven blocks of blockr.dplyr are close to this already: `new_select_block()` passes `state` and `expr_fn` to its factory, `new_js_transform_block()`, whose server only keeps JS and R in step ([R/select_block.R#L29-L52](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/68e1b54d2d1e028c96b77d03f8887b12b6d872b8/R/select_block.R#L29-L52)). Under the contract the factory becomes a parent type and its server goes, the JS becomes a module, `expr_fn` the type's `expr`, which takes the state args rather than a list and returns the call `expr_fn` builds today, with `data` in place of its `.(data)` placeholder ([R/expr-builders.R#L404-L409](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/68e1b54d2d1e028c96b77d03f8887b12b6d872b8/R/expr-builders.R#L404-L409)), and the columns the JS receives as messages a request.

### Testing

Core ships helpers to test a block type without Shiny: its `expr` with sample states, its `evaluate` with sample inputs, its requests, its `output`, and its module against a stub host. They replace `testServer()`. A type's R tests and its module tests share one fixture file in its package's `tests/`, since the type's two halves meet only in JSON: the file lists states, the R tests record into it what the type's requests answer for sample inputs, states and parameters and check that the expression built for each state runs, and the module tests serve the recorded answers through the stub host and check that the module submits only listed states, the pattern of consumer-driven contract tests ([Pact](https://docs.pact.io/)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

A type defined outside a package, where the caller's `topenv()` is no namespace, keeps the call `block_type()` was made with, from `match.call()`, rather than having its value written out later. Written out, a field such as `parent` takes the whole parent type in the internal layout of the core that saved it, where the developer wrote `transform_block`, and a later core may lay it out differently. The definition is that call wrapped in `blockr.core::block_constructor()`, with the package objects it names qualified, `transform_block` as `blockr.core::transform_block`, and a parent type the script defines written as its own call, nested. Nothing else the call or its functions take from the script, such as a helper or a data frame, can go into a file, so `block_type()` warns about each such name when the type is defined, finding them with `codetools::findGlobals()` and resolving them from the caller's environment. A UI the type names by file is a plain JS module, which goes into the definition as the file's text, so that a file brings the UI along, since core loads JS only ([UI modules in JS](Rewrite-1.1.7#packaging)).

The constructor takes the state from the frame `expr` ran in, through a copy of `expr` that hands the frame over as it exits (above), so that what the checks in `expr` change, such as `match.arg()` picking `"head"` out of `c("head", "tail")`, is the state the block holds, as `initial_block_state()` reads a block's state from its server's environment today ([R/block-class.R#L719-L725](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L719-L725)). An arg without a default stays out of the state while `missing()` finds it missing in the frame, so one the body assigns, such as a value it works out, is in it. The frame is kept when `expr` signals `invalid()` too, so a type checks its args before it signals. R tells a body's use of an unset arg by the class `missingArgError`, which R 4.5.0 added, and in older R by the error's message, translated as R translates it. R puts the upstream ids in place of `...` wherever it is an argument of a call, but not inside a function the expression defines, whose `...` is its own.

Today `register_block()` builds a block to read its classes and, without `arguments`, its arg specs, and checks the specs' examples against it ([R/block-registry.R#L143-L162](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-registry.R#L143-L162)). The type gives the first two, and the examples are checked by calling `expr` with them instead.

</details>
