# Block classes in R for the client-owned board
Status: settled on 2026-10-30. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how a package defines and registers a block class in R, and how R evaluates a block with it. It shapes defining block classes, a block class's output, exporting the block registry, the per-session evaluator and the guide for block class authors, each an item in the Work list of [Client-owned board state](Rewrite-1.1#work). A block class's UI, a module that meets the contract, is the UI modules proposal ([UI modules in JS](Rewrite-1.1.7)), the messages that carry a block's recipe and its result are the [wire protocol proposal](Rewrite-1.1.9), how state values travel between the client and R is the [serialization proposal](Rewrite-1.1.4), which renderer draws an output is [Front-ends and extension points](Rewrite-1.1.8#renderers)'s, and when a block is evaluated is the [evaluation proposal](Rewrite-1.1.10).

## What must hold

1. A block class is defined once, as a value, and the constructor made from it returns an S3 block whose args are the block's state; classes are registered as today, under a registry id ([Board objects](Rewrite-1.1.1)).
2. Its R side is plain functions, with no Shiny module server and no reactives.
3. The generics packages implement today keep working wherever they still have a job.
4. Nothing about a class is copied into its blocks, and nothing builds a block to learn about its class.
5. A package plugs into another package's class only through a hook that class offers, or by building a class of its own from that class's fields.
6. A front-end or any other package can replace how core draws an output class, such as table outputs, without changing a block class.

## Today

A block class calls `new_block(server, ui, class, ctor, ctor_pkg, dat_valid, allow_empty_state, block_name, expr_type, external_ctrl, block_metadata, ...)` or one of its specializations ([R/block-class.R#L180](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L180)). The server is a Shiny module whose formals name the data inputs and which returns `expr`, a reactive expression, and `state`, reactives naming every constructor formal ([R/block-server.R#L969](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L969)). The head block keeps its args in `reactiveVal()`s, syncs them with its inputs through observers, and caps `n` at the number of rows with `updateNumericInput()` ([R/transform-head.R#L27-L91](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/transform-head.R#L27-L91)).

## Proposal

### The block class

A block class is a value made by `new_block_class()`, holding everything that is the same for every block of the class, and its constructor is a function that `block_constructor()` makes from it. A class's `expr` is a function of the block's state args, from whose result interpolation makes the block expression, which R evaluates and a script holds (below). The head block, written to the new contract, with illustrative names:

```r
head_block <- new_block_class(
  "head_block",
  inputs    = function(data) stopifnot(is.data.frame(data)),
  expr      = function(n = 6L, direction = c("head", "tail")) {
    direction <- match.arg(direction)
    fn <- if (direction == "tail") quote(utils::tail) else quote(utils::head)
    bbquote(.(fn)(.(data), n = .(n)))
  },
  ui        = js_module("head-block.js"),
  requests  = list(n_max = function(data) nrow(data)),
  output    = as_table_output
)

new_head_block <- block_constructor(head_block)
```

The constructor has the formals of `expr`, a `block_name` and a `visible`, so an app script calls `new_head_block(n = 10L)` as today, and the checks in `expr`, such as `match.arg()`, run when it does: it calls `expr` with its args and takes the block's state from the frame `expr` ran in, as the checks left it, `list(n = 10L, direction = "head")` (notes). It returns a block that holds its state, its name, which defaults to one from its class's, `"Head"` for `head_block`, as `default_block_name()` gives it today, and core's attribute `visible`, which says which of the block's sections show ([Board objects](Rewrite-1.1.1#blocks)), and refers to its class, which every head block shares and none copies. It takes no `...`, so a misspelled state arg fails as an unused argument, `new_head_block(m = 10L)` with `unused argument (m = 10)`, rather than becoming an attribute, and another package's attributes are set in the client only. The name keeps today's argument, `block_name`, since `attr()` matches the names of R attributes partially: on a block, a list of its state, that has no R attribute `name`, `attr(blk, "name")` returns the block's `names`, as it did when `new_block()` took a `name`. A package exports both: the class, from whose fields another class can be built, and the constructor, which app scripts call.

A class's fields:

- The `name` argument gives the class's name, which leads a block's class vector, `c("head_block", "block")`, and a field the class leaves out, which may be any but `expr` and `ui`, is `NULL`, for which R does what core does by default (below).
- The `inputs` field gives the data inputs, apart from the state args, as formals without defaults (below): a character vector names them, `"data"`, `c("x", "y")` for a merge or `"..."` for a variadic block; a list from `alist()` gives them as formals, `alist(x = , y = )`; and a function gives them as its formals and checks them in its body, `function(data) stopifnot(is.data.frame(data))`, which takes the place of `dat_valid`. A class's inputs are its own, and `NULL` for a class with none, such as a block that reads a file. No input has a default for now, so none is optional (notes). A block runs only once every input is linked, and a variadic block once it has one link, which the client sees from the block registry, showing the block as `waiting` until then without asking R ([Evaluation in the client](Rewrite-1.1.10#statuses)).
- The `expr` field, which every class has, is a function whose formals are the state args and whose body checks them, as a constructor checks its args today, and returns what interpolation makes the block expression from (below). An arg without a default starts unset, as a merge's `by` does, and stays out of the block's state until something sets it. Called without args, `expr` gives the state a new block starts with, which may be one that cannot run yet (below).
- The `ui` field names the class's UI with `js_module()`, which finds the file in the package's `inst/` when R serves it (notes), a module written against the contract of [UI modules in JS](Rewrite-1.1.7), in JS written by hand or built from TypeScript, as core's own are, or from TSX with React, which ships the schema of the block's state beside it ([UI modules in JS](Rewrite-1.1.7#packaging)). Every class names one, since the schema of its state comes with it, and a module may draw nothing, as core's static block's does, whose expression a script sets. The `requests` field takes a named list of R functions for whatever the UI asks of R, such as the head block's `n_max`, whose arguments name the inputs, state args and options they read and any parameters the UI passes (below).
- The `output` field names the coercion the class's results are shown through, such as `as_table_output`, which makes an output of its class from a result (below), and the `options` field names the board options the class's own code reads, such as blockr.io's `data_dir`, the directory its read block lists files from, by the constructors that give each option's id and initial value, while the package that ships an option defines it in the client ([Board objects](Rewrite-1.1.1)), and a renderer brings the options that it and its output class's coercion read, such as a table's `n_rows` ([Front-ends and extension points](Rewrite-1.1.8#renderers)).
- The `dat_valid`, `allow_empty_state`, `external_ctrl`, `expr_type` and `block_metadata` fields go. The checks of the data are the body of a function given as `inputs` (above), and they read the data inputs only. A state arg a block needs has no default, any other state that cannot run yet is for a class's `expr` to say (below), and a block waits for its inputs (above), so the glue block, which today renders its text with nothing linked, waits for a link. Every block's state can now be set from outside, the class of what `expr` returns says how interpolation makes the block expression from it, as `expr_type` declares today, and a class's metadata comes from its registration (below).

A class has no say in when its blocks are evaluated: a block that must run with nothing on screen, such as a write block in auto mode, is demanded by its package in the client ([Evaluation in the client](Rewrite-1.1.10#demand)), and a block whose block expression must run only when its UI asks, such as a write block in manual mode, has a `block_eval()` method that runs it only with the parameter the UI's one-time evaluation passes (below).

The function fields name what they read: `expr` the state args, a request the inputs, state args and options it reads, a function given as `inputs` the data inputs, and the coercion in `output` the result and what the renderer asks with, its `options`, `info` and `params` (below). How R evaluates a block, migrates a state a file saved and describes a result are generics rather than fields: `block_eval()` and `block_migrate()` dispatch on the block's class, which R gives the state it has, a recipe's or a file's, building no block, and `block_summary()` on the result's class (below). The `new_block_class()` function checks a class when it is defined, so that no block is checked for being well formed again: that no state arg is `...`, `block_name` or `visible`; that no input shares a state arg's name, since a request's arguments would not say which they mean; that `inputs` is names, formals or a function of them, with no default; that the arguments of each request name inputs, state args or the class's options, but for an action's `file` and its parameters, which have a default; and that `expr`, called without args, cannot run yet or returns a call, a string, a function whose formals are the inputs or an object of a class that inherits from `blockr_expr`, holding no function, such as the one base `bquote()` puts in for `.(data)`. All but the last read only the class's fields and the formals of its functions, while registration checks that the properties of the schema the class's UI ships are the state args, as it reads the schema (below).

A sketch of `new_block_class()`, in which a field a class leaves out is `NULL`:

```r
new_block_class <- function(name, inputs = NULL, expr, ui,
                            requests = NULL, output = NULL, options = NULL) {

  cls <- list(class = c(name, "block"), inputs = inputs, expr = expr, ui = ui,
              requests = requests, output = output, options = options)

  stopifnot("inputs are names, formals or a function of them" =
    is.null(inputs) || is.character(inputs) || is.list(inputs) || is.function(inputs))
  input_formals <- if (is.function(inputs)) formals(inputs) else if (is.list(inputs)) inputs
  input_args <- if (is.character(inputs)) inputs else names(input_formals)
  state_args <- names(formals(expr))
  option_ids <- vapply(options, function(new) board_option_id(new()), "")
  stopifnot(
    "no input has a default" = !any(nzchar(vapply(input_formals, deparse1, ""))),
    "no state arg is ..., block_name or visible" = !any(c("...", "block_name", "visible") %in% state_args),
    "no input shares a state arg's name" = !any(input_args %in% state_args)
  )
  for (f in requests) {
    params <- setdiff(names(formals(f)), c(input_args, state_args, option_ids, if (inherits(f, "action")) "file"))
    stopifnot("a request's other args are parameters, with defaults" =
      all(nzchar(vapply(formals(f)[params], deparse1, ""))))
  }
  res <- tryCatch(expr(), invalid = function(e) NULL, missingArgError = function(e) NULL)
  holds_function <- function(e) is.function(e) || (is.call(e) && any(vapply(as.list(e), holds_function, NA)))
  stopifnot(
    "expr() gives a call, a string, a function or a blockr_expr" = is.null(res) ||
      is.language(res) || is.character(res) || is.function(res) || inherits(res, "blockr_expr"),
    "a function expr() gives has the inputs as its formals" =
      !is.function(res) || identical(names(formals(res)), input_args),
    "expr() puts in no function, as base bquote() does for .(data)" =
      is.function(res) || !holds_function(res)
  )

  structure(cls, class = "block_class")
}
```

A sketch of `block_constructor()`, which takes the block's state from the frame `expr` ran in and leaves out an arg that is still unset, with `invalid()`:

```r
block_constructor <- function(cls) {

  args <- formals(cls$expr)
  state_args <- as.character(names(args))
  has_default <- nzchar(vapply(args, deparse1, ""))

  build <- function(env) {  # env is the constructor's frame
    given <- Filter(function(arg) !eval(call("missing", as.name(arg)), env), state_args)
    frame <- NULL
    framed <- cls$expr     # a copy of expr that hands over its frame as it exits
    body(framed) <- bquote({
      on.exit(.(function(e) frame <<- e)(environment()))
      .(body(cls$expr))
    })
    tryCatch(
      do.call(framed, mget(given, env), quote = TRUE),
      invalid = function(e) NULL, missingArgError = function(e) NULL
    )
    unset <- vapply(state_args, function(arg) eval(call("missing", as.name(arg)), frame), NA)
    structure(
      mget(state_args[has_default | !unset], frame),  # the state, as the checks left it
      block_name = env$block_name %||% default_block_name(cls$class), visible = env$visible,
      block_class = cls, class = cls$class
    )
  }

  ctor <- function() build(environment())
  formals(ctor) <- c(args, alist(block_name = NULL, visible = NULL))
  ctor
}

default_block_name <- function(class) {   # today's
  res <- gsub("_", " ", sub("_block$", "", class[1L]))
  paste0(toupper(substr(res, 1L, 1L)), substring(res, 2L))
}

invalid <- function(message) {
  stop(structure(class = c("invalid", "error", "condition"), list(message = message, call = NULL)))
}
```

### Expressions

What a class's `expr` returns says, by its class, how interpolation makes the block expression from it, which R evaluates and a script holds. R calls `expr` with the block state, which fills in the state args, and the generic `interpolate(x, inputs)` turns what it returns, `x`, into the block expression, given the upstream ids by input, `inputs`, as `list(data = "a")`, with a variadic block's under `...` in link order, `list(... = list("a", b2 = "b"))`, and dispatching on the class of `x`, whose default method takes any call or name, since R gives a call to `{`, `(` or `if` a class of its own. What `expr` returns is one of four:

- **A call,** built with any tool, such as `bquote()`, `rlang::expr()` or `call()`, which writes the data inputs bare: `rlang::expr(utils::head(data, n = !!n))`.
- **A string,** built such as with `glue::glue()` or `sprintf()`, which R parses into such a call.
- **A function** whose formals are the data inputs, written bare in its body, where `.()` stands for a value of the block state, which base `bquote()` fills in from the function's environment, the frame `expr` ran in: `function(data) utils::head(data, n = .(n))`.
- **An object of a class that inherits from `blockr_expr`,** which writes the data inputs as placeholders, such as what `bbquote()` returns, of class `c("bquoted_expr", "blockr_expr")`: `bbquote(utils::head(.(data), n = .(n)))`.

For a call, a string or a function, the block expression calls a function of the block's data inputs with the upstream ids, so that a head block downstream of block `a` whose `expr` returns a call gets `(function(data) utils::head(data, n = 10L))(data = a)`. A variadic block's `...` is a formal of that function, which the call binds to the ids in link order, each named by its link's input, which is empty for a positional link ([Board objects](Rewrite-1.1.1#links)): `(function(...) rbind(...))(a, b2 = b)`.

For a `blockr_expr`, the method of its class puts the upstream ids in place of its placeholders, so that the block expression is idiomatic R, `utils::head(a, n = 10L)`, which a script assigns to the block's id. In a `bquoted_expr`, `...` as an argument of a call stands for a variadic block's inputs, so `bbquote(rbind(...))` gives `rbind(a, b2 = b)`. That is the default, which core's own classes use and the guide for authors leads with. A package adds a class of its own that inherits from `blockr_expr`, with an `interpolate()` method, such as one that fills in a glue template's `{data}`, without changing core.

Putting an id in place of a bare name cannot tell the input from a column of the same name in an argument that a function evaluates non-standardly, which is what defeated substituting names in [blockr.core#17](https://github.com/BristolMyersSquibb/blockr.core/issues/17#issuecomment-2630544662). A placeholder settles that, so `bbquote(subset(.(data), threshold > .(threshold)))` keeps a column called `threshold`. Only a `blockr_expr` holds placeholders, and R never looks for one in a call or a string. The `bbquote()` function fills in only the values it finds in the frame `expr` ran in and leaves `.(data)` for interpolation, while base `bquote()` would try to fill in `.(data)` as well, which is why core keeps `bbquote()`. A state arg written bare rather than filled in, `n` rather than `.(n)`, looks like such a column too, so nothing catches it before it runs, and outside such an argument its first evaluation fails, with `object 'n' not found`.

Whatever `expr` returns, R evaluates the block expression a script holds, with each upstream block's result bound to its id (below), so the code a block shows and exports is the code that ran, labels included. Since `expr` never sees an input's data, a class whose expression depends on the data says so in the expression, as `utils::head(.(data), n = min(10L, nrow(.(data))))` caps `n` at the rows it gets, or gets what it needs into its state through a request. R calls `expr` with the args the block's state holds, so a body that uses an unset arg makes R reply `invalid`, naming the arg, as the merge block's does until its `by` is set:

```r
merge_block <- new_block_class(
  "merge_block",
  ui       = js_module("merge-block.js"),
  inputs   = c("x", "y"),
  expr     = function(by, all_x = FALSE, all_y = FALSE) {
    bbquote(merge(.(x), .(y), by = .(by), all.x = .(all_x), all.y = .(all_y)))
  },
  requests = list(shared = function(x, y) intersect(names(x), names(y)))
)
```

A body that can do without an unset arg tests it with `missing()`, as a merge by the columns its inputs share would with `if (missing(by)) bbquote(merge(.(x), .(y)))`, and a body given a state that is set but cannot run signals `invalid()` with a message, such as `invalid("Choose at least one column.")` for a selection the user emptied.

### Requests

A request is a function the UI calls through its host for whatever it needs from R, such as the head block's `n_max`, the maximum of its numeric input, which never enters the block's state ([UI modules in JS](Rewrite-1.1.7#the-contract)). R binds each of its arguments by name: an input to the result of the upstream block at the revision the request reads ([UI modules in JS](Rewrite-1.1.7#the-contract)), a variadic block's `...` to its inputs in link order, named by their links' inputs, a state arg to the value the request carries, which the host fills in from the block's state where the UI passes none ([Wire protocol](Rewrite-1.1.9)), leaving an unset one missing, an option the class names to the option's value, as blockr.io's read block lists the files under its `data_dir`, and any other argument to a parameter the UI passes, which must have a default, so that `new_block_class()` still catches a misspelled state arg written without one, as a state arg in a request needs none. A request's parameter holds only what the UI is showing, such as the column whose values a dropdown lists or the text typed into its search, never what the block computes. That holds by construction, since only requests, outputs and one-time evaluations take parameters, and `expr` never sees them, so no parameter changes a block's expression or saved state:

```r
requests = list(
  values   = function(data, column = NULL, query = "", limit = 1000L) column_values(data, column, query, limit),
  list_dir = volatile(function(path = "") list_dir(path))
)
```

R writes a request's answer, which no schema describes, with every vector as an array, a length-one vector included, so that a module reads a single value as `answer[0]`, while a request that answers with a file, such as a download, returns a reply body, `new_reply_body("report.pptx", type, name = "report.pptx")`, which R sends as its reply's binary body. Core keeps each answer by registry id, name, state args, option values, parameters and the revisions of the inputs read, as a snapshot of them, so that reopening a column's dropdown is answered without asking R, and data that changes behind an input, such as a database's, is read again once something invalidates the block that reads it ([Evaluation in the client](Rewrite-1.1.10#invalidation)). A request wrapped in `volatile()` is never kept and goes to R every time, which suits a cheap lookup outside the board, such as a directory listing, and nothing expensive. A request wrapped in `action()` acts rather than reads, such as an upload, which receives the file the user picked in its argument `file`, a list of the path of the temporary file R wrote the bytes to and the file's name, MIME type and size, as Shiny's `fileInput()` gives them today, keeps the file where its package decides and returns its path for the block's state: R runs it once per call and it may write, core never keeps or merges its answer, and on a locked board R runs it only for a block the lock leaves open ([Wire protocol](Rewrite-1.1.9#locked-boards)).

### Core's classes and hooks

A field a class leaves out is `NULL`, and R does what core does by default: where `output` is `NULL`, R shows the result as text, through `as_text_output()`, which prints it (below). Core's methods of the generics do the rest: `block_eval()` evaluates the block expression with each upstream block's result bound to its id, as `block_eval()` and `eval_env()` do today, and keeps whatever it draws as the result, as core's plot block does today with `evaluate::evaluate()`; `block_summary()` gives the result's class and dimensions; and `block_migrate()` leaves a state as it is. Today's specializations, `transform_block`, `data_block`, `parser_block`, `plot_block`, `text_block` and `file_block`, go. What they carry needs no hierarchy ([R/transform-block.R#L24-L42](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/transform-block.R#L24-L42), [R/plot-block.R#L32-L68](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plot-block.R#L32-L68)): the output and UI of a table, a plot or text, which a class names by its output's coercion and a renderer draws; the table's board options, `n_rows`, `page_size` and `filter_rows`, which core's table renderer brings ([Front-ends and extension points](Rewrite-1.1.8#renderers)); and a plot's recording, which core's `block_eval()` method does for every block. Nothing outside core dispatches on their classes, which in the workspace appear only in the class vectors blocks are built with, in docs and in tests. Blocks group in other ways too, each with a home of its own rather than a place in one hierarchy: the menu's category, from `@blockCategory` at registration; the output class; a renderer's board options; a class's inputs; and what packages demand in [Evaluation in the client](Rewrite-1.1.10#demand).

A class's fields belong to its package, so another package cannot change a class in place, as an S3 method registered for the block's class can today. Instead, an output class's coercion is a hook where other packages are meant to plug in: `as_table_output()` dispatches on the result's class, so a package that knows another class of table, such as dbplyr's lazy tables, which it pages in the database, registers a method that returns a table output, which every renderer of table outputs then draws. How an output looks is no hook of a block class at all, since any package can replace the renderer of an output class (below). Otherwise, a package builds a class of its own from the other package's class's fields, `new_block_class("my_head", inputs = head_block$inputs, expr = head_block$expr, ui = head_block$ui, output = as_text_output)`, and calls the other class's field where it extends one. No package in the workspace overrides another's block methods today, and the two registrations across packages, blockr.sandbox's methods for blockr.ai's `data_schema()` and `data_effect()` and for blockr.assistant's `describe_result()`, dispatch on result classes and work as before ([blockr.sandbox R/composer.R#L1401-L1418](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/afa235e346145e61af6dd01151b5b14f0ef12549/R/composer.R#L1401-L1418), [R/describe-composed.R#L178-L186](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/afa235e346145e61af6dd01151b5b14f0ef12549/R/describe-composed.R#L178-L186)).

### Registration

The `register_block()` and `register_blocks()` functions keep their arguments but `classes` ([R/block-registry.R#L80](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-registry.R#L80)), and so does the roclet that writes `inst/registry/blocks.yml` from `@block` tags: they take the constructor, as today, and read its block class from it, which gives the class vector (notes). The `uid` argument sets the name part of the registry id, `{pkg}-{name}`, whose name defaults to the constructor's name without `new_` ([Board objects](Rewrite-1.1.1)). A constructor registered by name comes with its package, as every package in the workspace registers its constructors today, while one registered as a function is from outside a package, since the environment of a function that `block_constructor()` makes, from which `register_block()` reads a constructor's package today, is blockr.core's for every class ([R/block-registry.R#L128-L135](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-registry.R#L128-L135)). The block registry keeps one entry per class, and `registry_id_from_block()` finds a block's entry by the class the block refers to. Registering no longer builds a block: the block registry reads the block class's class vector, its inputs, its UI and the schema the UI ships, whose properties must be the state args, its requests and options, and its default state from `expr` called without args, keeps them by registry id so that R resolves a request without a block, and sends all but the classes to the client ([Board objects](Rewrite-1.1.1#what-lives-where)). A class defined outside a package is registered by the script that defines it, and a file holds its blocks by registry id alone ([Board objects](Rewrite-1.1.1#block-classes-outside-a-package)). The arg specs default to every state arg, since `external_ctrl_vars()` goes, and describe each for models and tools, while its shape is the schema's ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)).

An entry is the metadata registration gives today, with its `link` as `url`, since a link is the board's, beside what the client can no longer read off a block class, now that the class stays in R: its inputs, module, schema, starting state, arg specs and requests:

```ts
interface RegistryEntry {
  id: RegistryId;                         // "blockr.core-head_block"
  name: string;                           // the metadata registration gives today: name, description,
  description: string;                    // details, url (register_block()'s link), guidance,
  details?: string;                       // keywords, category and icon
  url?: string;
  guidance?: string;
  keywords: string[];
  category: string;
  icon: string;
  inputs: string[];                       // ["data"], ["x", "y"], or ["..."] for a variadic block
  module: string;                         // the URL R serves the class's UI at
  schema: JsonSchema;                     // of the block's state, as its module ships it
  state: Record<string, Json>;            // what a new block starts with, from expr() called without args
  arguments: Record<string, ArgSpec>;     // the arg specs, which describe each state arg for models and tools
  requests: Record<string, {
    inputs: string[];                     // the data inputs its function names, which it reads
    state_args: string[];                 // the state args it names, which the host fills in
    options: OptionId[];                  // the board options it names, whose values R binds
    volatile?: true;                      // never kept
    action?: true;                        // acts rather than reads
  }>;
}
```

### Evaluation

R calls a constructor only where an app script builds a board, and where `blockr_deser()` converts a file from today's stack ([Board objects](Rewrite-1.1.1#the-board)), and keeps no block while the app runs. To evaluate a block, it looks the class up by the recipe's registry id, runs the checks of a function given as `inputs` with the linked results, calls its `expr` with the recipe's state, interpolates what it returns into the block expression (above), and evaluates that with `block_eval()`, with each upstream block's result bound to its id, so that the expression R runs is the one a script holds, labels included, such as the column names `cbind()` takes from its arguments, where today a block whose `expr_type` is `"bquoted"` is evaluated with its inputs' names and exported with the upstream ids in their place ([R/block-server.R#L754-L768](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L754-L768), [R/utils-code.R#L58-L69](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-code.R#L58-L69)). An `invalid()` that `expr` or a `block_eval()` method signals, or an unset arg that the body of `expr` uses or interpolation fills in, as in the `.()` of a function `expr` returns, makes R run nothing and reply `invalid`, with the message or the arg's name, while a check in the body of a function given as `inputs` that fails makes R reply `error`, as a failed `dat_valid` makes a block `failed` today. Conditions raised in interpolation come under the phase of `expr`, which builds the block expression ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)). Otherwise R runs the expression, which its reply carries ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)):

- The `block_eval(x, expr, env, ...)` generic, whose arguments keep today's names, so that a package's methods keep working, runs the block expression, `expr`, in `env`, where each upstream block's result is bound to its id, dispatching on the block's class, as `x` is the recipe's state with the class's class vector, which R gives it without calling the constructor, and gets in `...` the parameters of the one-time evaluation that asked for the block, if any ([Evaluation in the client](Rewrite-1.1.10#demand)). Core's method keeps whatever the block expression draws as the result, with a function that runs the block expression again, for `as_plot_output()` (below), and its value otherwise, and a package adds a method where its class runs otherwise, as blockr.ggplot builds a plot today so that a broken one fails as it is evaluated ([R/ggplot-transform.R#L50-L57](https://github.com/BristolMyersSquibb/blockr.ggplot/blob/289cb60f03d10caf13d143d06562f7eb663763d9/R/ggplot-transform.R#L50-L57)), and as blockr.io's write block runs its block expression, which holds the write, in manual mode only when its save button passes `save` (below). A method decides whether and how the block expression runs, never what it computes.
- The `block_summary(result)` generic describes the result in a few words, such as `<data.frame> [150 × 5]`, which R sends with its reply for the header of the block's card ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)), dispatching on the result's class rather than the block's, so that a package describes its results wherever they appear. Core's method gives the result's class and dimensions, as `block_summary()` does today ([R/plugin-block.R#L299-L320](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-block.R#L299-L320)), so a front-end has it without asking R again.

The write block of blockr.io writes in manual mode only when its save button asks, with illustrative names:

```r
block_eval.write_block <- function(x, expr, env, save = FALSE, ...) {
  if (!isTRUE(x$auto_write) && !save) invalid("Save to write the file.")
  NextMethod()
}
```

R keeps each block's latest result, with its revision, its block expression and the block's registry id, in an environment keyed by block id ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)), and binds it as an input of every block downstream, so nothing a class runs may change its inputs in place: copy-on-modify covers most R objects, but not a data.table changed by reference, an environment or an R6 object, whose change would reach the upstream block's result.

### Outputs

An output is an S3 object of an output class, whose class vector ends in `block_output`. The package that defines an output class gives it a contract, as a MIME type's owner does, and defines it in R with two functions: a constructor, which makes an output of the class and checks the fields its contract gives, and a coercion, a generic that makes one from a result, dispatching on the result's class, as `new_block()` and `as_block()` pair today. A block class names the coercion its results are shown through in its `output` field, and R calls it with the block's result and what the renderer asks with, its `options`, `info` and `params` (below), and sends the output as JSON, written by the schema its class's contract gives (below), naming the renderer R picked for it (below), with at most one binary body, such as a plot's PNG, which the output holds as a reply body and R sends beside the JSON rather than in it ([Wire protocol](Rewrite-1.1.9#outputs)). A reply body is made by `new_reply_body(x, type, name = NULL)` from a raw vector or a file's path, with its MIME type and, for a download, a file name, as a plot output's is, `new_plot_output(new_reply_body(png, "image/png"), width, height)`. Core defines three output classes: `table_output`, a table's columns, the rows of one page and its total row count, made by `new_table_output()` and, from a result, by `as_table_output()`; `text_output`, made by `new_text_output()` and `as_text_output()`, which prints any result; and `plot_output`, made by `new_plot_output()` and `as_plot_output()`, which draws a plot at the size `info` gives, with thematic set to its theme, so that a theme switch redraws every plot on screen with no new revision, where today the block re-evaluates when the theme changes ([R/plot-block.R#L59-L68](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plot-block.R#L59-L68)). The coercion prints a ggplot again, and for a base plot it replays the recording where only the size differs from the one it was drawn at, as today's plot block replays it on a resize ([#L33](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plot-block.R#L33)), and runs the block expression again where the theme does, since a recording keeps the colours it was drawn in. Core's `block_eval()` method gives it what that takes: for a block expression that draws, the result holds the recording with a function that runs the block expression again in its environment. A redraw runs code the plot's revision ran already, so an expression that draws random numbers draws a different plot on a theme switch, as it does today. The table output, with illustrative bodies:

```r
new_block_output <- function(x, class) structure(x, class = c(class, "block_output"))

new_table_output <- function(columns, rows, total, ..., class = character()) {
  stopifnot(is.data.frame(columns), identical(names(columns), c("name", "class")),
            is.data.frame(rows), length(total) == 1L)
  new_block_output(list(columns = columns, rows = rows, total = total, ...), c(class, "table_output"))
}

as_table_output <- function(result, options, info, params) UseMethod("as_table_output")

as_table_output.data.frame <- function(result, options, info, params) {
  size <- params$page_size %||% options$n_rows
  page <- params$page %||% 1L
  ord <- seq_len(nrow(result))
  if (length(params$sort)) ord <- order(result[[params$sort$column]], decreasing = isTRUE(params$sort$desc))
  idx <- ord[(page - 1L) * size + seq_len(size)]
  new_table_output(
    columns = data.frame(name = names(result), class = unname(vapply(result, function(col) class(col)[1L], ""))),
    rows = result[idx[!is.na(idx)], , drop = FALSE],
    total = nrow(result)
  )
}
```

For a head block's result, the first seven rows of `iris`, with `n_rows` at 3 and the renderer on page 2, R sends, where the app draws tables with core's plain renderer:

```json
{"renderer":"blockr.core-basic_table","columns":[{"name":"Sepal.Length","class":"numeric"},{"name":"Sepal.Width","class":"numeric"},{"name":"Petal.Length","class":"numeric"},{"name":"Petal.Width","class":"numeric"},{"name":"Species","class":"factor"}],"rows":[[4.6,3.1,1.5,0.2,"setosa"],[5,3.6,1.4,0.2,"setosa"],[5.4,3.9,1.7,0.4,"setosa"]],"total":7}
```

The contract is what a renderer of the class is written against: a JSON Schema of the class's outputs, by which R writes each output, as it writes a block's state by its class's schema ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)), with the TypeScript type that goes with it, as a module ships its state's schema beside its type ([UI modules in JS](Rewrite-1.1.7#packaging)); a type of the parameters its coercion reads; a type of the events its renderers emit, if they emit any, such as a chart's selection, which an extension may hear ([UI modules in JS](Rewrite-1.1.7#the-contract)); the types of the args and answers of its requests, if it has any (below); and fixtures of sample outputs, which R's constructor writes and every renderer of the class is tested on. So a data frame becomes rows wherever the schema wants arrays of arrays, and a length-one vector stays an array wherever the schema wants one. The defining package ships them beside its renderer, as core ships the types modules are written against ([UI modules in JS](Rewrite-1.1.7#packaging)), and a subclass's types extend its class's, as its class vector does. Core's contracts for its three output classes:

```ts
interface BlockOutput {
  renderer: string;                      // the renderer R picked, which R adds to every output
}

interface TableOutput extends BlockOutput {
  columns: { name: string; class: string }[];   // in R's order, so names such as "2019" and duplicates keep their places
  rows: Json[][];                        // one page of rows, in the order of columns
  total: number;                         // the total row count
}

interface TableParams {
  page?: number;                         // 1 unless the renderer pages
  page_size?: number;                    // n_rows unless the renderer sets one
  sort?: { column: string; desc?: boolean };
}

interface TextOutput extends BlockOutput {
  text: string;                          // the result as print() shows it, at R's own width, which the renderer scrolls
}

interface PlotOutput extends BlockOutput {
  width: number;                         // the size it was drawn at, from info, in CSS pixels
  height: number;                        // its PNG travels as the output's binary body
}
```

What draws an output is a renderer, a module that a package declares in R for an output class, of which R picks one per class, from the app's blockr options, the front-end, other packages and the package that defines the class, in that order, and names in each output the one it picked for the most specific class in the output's class vector that has one, as S3 dispatch would ([Front-ends and extension points](Rewrite-1.1.8#renderers)). The client mounts the renderer an output names, so neither class vectors nor dispatch reach it, as [State in JS](Rewrite-1#principles) keeps them in R. An output class is the contract of the package that defines it, and only that package adds fields to it, in a later version whose new fields older renderers skip, as both sides of the protocol ignore fields they do not know ([Wire protocol](Rewrite-1.1.9#versions)). Another package extends it with a subclass, whose outputs hold everything the class holds, such as a lazy table's output that adds the SQL behind its page in its database's dialect, of class `c("lazy_table_output", "table_output", "block_output")`, so a renderer of the subclass draws what it adds, and where no package declares one, the class's renderer draws what the class holds. A lazy table with nothing more to show is a table output, which R pages in the database, as blockr.ui's table preview pages one today ([R/table-preview-engine.R#L67-L68](https://github.com/BristolMyersSquibb/blockr.ui/blob/9bd8312a3408bbcbabff2b57d1d3fd5681843c94/R/table-preview-engine.R#L67-L68)). So a block class never names what draws its output, and blockr.ui's table preview takes the place of core's plain table for every block whose output is a table output.

An output's parameters are what its renderer keeps and the coercion reads, such as the page a table shows and its sort, which the renderer changes through its host, asking R for the output again, so a table output holds the page its parameters ask for, sorted as they say, with `n_rows` rows to a page unless they give a page size. A board option the coercion reads, such as `n_rows`, is part of the class's contract, so every renderer of the class brings it ([Front-ends and extension points](Rewrite-1.1.8#renderers)). A renderer draws an output nested in its own through its host, with the renderer R names in the nested output. An output that is composite rather than an extension of another nests the outputs it holds: the output blockr.dm draws today through `block_ui()` and `block_output()` methods ([R/dm-block.R#L504-L627](https://github.com/BristolMyersSquibb/blockr.dm/blob/8b37981838cfac63a5d40e270a19857e5ef9ea90/R/dm-block.R#L504-L627)) becomes, with illustrative names, an output class of its own, whose coercion makes a dm's output and nests the selected table's, and whose renderer draws the diagram and has the table drawn by the app's renderer for table outputs:

```r
new_dm_output <- function(diagram, preview = NULL) {
  stopifnot(is.null(preview) || inherits(preview, "table_output"))
  new_block_output(list(diagram = diagram, preview = preview), "dm_output")
}

as_dm_output <- function(result, options, info, params) UseMethod("as_dm_output")

as_dm_output.dm <- function(result, options, info, params) {
  new_dm_output(
    diagram = dm_keylines_meta(result),
    preview = if (length(params$table)) as_table_output(result[[params$table]], options, info, params$preview)
  )
}

dm_block <- new_block_class("dm_block", expr = dm_expr, ui = js_module("dm-block.js"), output = as_dm_output)   # inputs and requests left out

register_renderer("dm", js_module("dm-output.js"), class = "dm_output",
                  options = list(new_n_rows_option))   # in .onLoad(), for the nested table
```

An output class may have requests, for what its renderers offer beyond the output, such as a download of what they show, as blockr.viz's tables offer the frame on screen as xlsx, HTML and pptx today ([R/table-download.R#L3-L11](https://github.com/BristolMyersSquibb/blockr.viz/blob/332ce573ffafa86f5a41dc400b0f85e6800128f7/R/table-download.R#L3-L11)). The package that defines the class registers them in R under the class's name, and a renderer of the class calls them through its output host ([UI modules in JS](Rewrite-1.1.7#the-contract)). R runs one as it runs the coercion, with the block's result at the revision of the output the renderer holds and the board option values and parameters that output was asked with, which the request carries, and with the args the renderer passes and, in the argument `file`, a file it sends, such as the bitmap of a chart the browser drew, and the request answers as a block class's does, a download with a reply body. R resolves a request by the most specific class in the output's class vector that has it, as it picks a renderer, so that a subclass has its class's requests and may replace them. The client keeps an answer as it keeps the output, unless the request is wrapped in `volatile()`, and no request of an output class writes, so a locked board answers it as it draws the output ([Wire protocol](Rewrite-1.1.9#locked-boards)).

### Generics

| Generic | Becomes |
|---|---|
| `block_output(x, result, session)` | gone, since a class names its output's coercion in `output`, which makes an output from a result, while its name becomes the base of every output class (above) |
| `block_ui(id, x)`, `block_render_trigger()` | gone, since a renderer draws the output and options are arguments |
| `tabular_output(x, result, block, session)` | `as_table_output(result, options, info, params)`, the coercion to a table output, dispatching on the result rather than a display (above) |
| `tabular_display()`, `tabular_ui()`, `tabular_trigger()`, `tabular_options()` | gone, with the display classes and the `tabular_display` blockr option, since a renderer of table outputs takes a display's place, with the board options it brings (above) |
| `block_eval(x, expr, env, ...)` | kept, dispatching on the block's class, with core's method keeping what the block expression draws (above) |
| none | `interpolate(x, inputs)`, a generic on the class of what `expr` returns, which makes the block expression from it with the upstream ids by input, and whose method a package adds for a class of its own that inherits from `blockr_expr` (above) |
| `block_eval_trigger()` | gone, since options never re-evaluate and any component can invalidate a block |
| `board_options(x)` | the class's `options` and those of the renderers R picked, while a board class keeps its own `board_options()` method |
| `blockr_ser()`, `blockr_deser()` | kept, `blockr_ser()` to write a script's board and `blockr_deser()` to convert files from today's stack, while a file of the new stack migrates through `block_migrate()` |
| `block_summary(x, data)` | `block_summary(result)`, dispatching on the result's class rather than the block's, which R sends with every evaluation's reply (above) |
| none | `block_migrate(x, version)`, a generic on the block's class, whose method maps a state saved by an older version of the class's package to the current state, given that version: `x` is the saved state with the class's class vector, and the method returns the state. R calls it on the state a file holds when it opens a board ([Serialization](Rewrite-1.1.4#migrations)), but for a class from no package, which has no version, while core's method leaves a state as it is |
| `block_server()`, `expr_server()`, `expr_ui()` | gone |
| `block_inputs(x)` | the class's `inputs` |
| `external_ctrl_vars(x)` | gone |
| `block_metadata(x, fields)` | the class's entry in the block registry, read by registry id |
| `str_value(x)` | kept for printing R objects, without the `*` that flags the args `external_ctrl_vars()` names, while blockr.assistant, which describes a board to a model with it, runs its agent loop in the browser ([Assistant as a client extension](Rewrite-1.4)) |

### JS-driven blocks

The JS-driven blocks of blockr.dplyr are close to this already: `new_select_block()` passes `state` and `expr_fn` to its factory, `new_js_transform_block()`, whose server only keeps JS and R in step ([R/select_block.R#L29-L52](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/68e1b54d2d1e028c96b77d03f8887b12b6d872b8/R/select_block.R#L29-L52)). Under the contract the factory becomes a function that calls `new_block_class()` with the fields its classes share, and its server goes, the JS becomes a module, `expr_fn` the class's `expr`, which takes the state args rather than a list and returns the call `expr_fn` builds today, `.(data)` placeholder included ([R/expr-builders.R#L404-L409](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/68e1b54d2d1e028c96b77d03f8887b12b6d872b8/R/expr-builders.R#L404-L409)), and the columns the JS receives as messages a request. Most of its builders make that call with `bbquote()` already, so it is a `bquoted_expr`, and those that start from `quote()`, as the mutate builder does ([R/expr-builders.R#L226](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/68e1b54d2d1e028c96b77d03f8887b12b6d872b8/R/expr-builders.R#L226)), pass their result through `bbquote()` to make it one.

### Testing

Core ships helpers to test a block class without Shiny: its `expr` with sample states, its block expressions with sample inputs, its requests, its output's coercion with sample results, and its module against a stub host. They replace `testServer()`. A class's R tests and its module tests share one fixture file in its package's `tests/`, since the class's two halves meet only in JSON: the file lists states, the R tests record into it what the class's requests answer for sample inputs, states and parameters and check that the block expression built for each state runs, and the module tests serve the recorded answers through the stub host and check that the module submits only listed states, the pattern of consumer-driven contract tests ([Pact](https://docs.pact.io/)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

The constructor takes the state from the frame `expr` ran in, through a copy of `expr` that hands the frame over as it exits (above), so that what the checks in `expr` change, such as `match.arg()` picking `"head"` out of `c("head", "tail")`, is the state the block holds, as `initial_block_state()` reads a block's state from its server's environment today ([R/block-class.R#L719-L725](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L719-L725)). An arg without a default stays out of the state while `missing()` finds it missing in the frame, so one the body assigns, such as a value it works out, is in it. The frame is kept when `expr` signals `invalid()` too, so a class checks its args before it signals. R tells a body's use of an unset arg by the class `missingArgError`, which R 4.5.0 added and `bbquote()` and base `bquote()` raise too when they fill in the `.()` of an unset arg, and in older R by the error's message, translated as R translates it. The `bbquote()` function reads only the names of the frame it runs in, so that an input's placeholder, `.(data)`, stays for interpolation, although `utils::data` exists. The method of `bquoted_expr` puts the upstream id in place of a placeholder wherever it is, and in place of `...` wherever it is an argument of a call, but not inside a function the expression defines, whose `...` is its own. A placeholder is a call to `.` whose only argument is the name of a data input, so in a `bquoted_expr`, data.table's `.()`, which stands for `list()` in `j`, is a placeholder where it selects nothing but a column named like an input, `dt[, .(x)]` with an input `x`, which such a block writes as `dt[, list(x)]`. In the body of a function that `expr` returns, base `bquote()` fills in every `.()`, so data.table's is written `list()` there too, while in a call or a string, which hold no placeholders, it stays data.table's.

Data inputs have no defaults for now. An optional input, `y = NULL`, would need the block registry and every front-end to mark it, `waiting` to count only the inputs without one, and interpolation and requests to take its default, while no block in the workspace declares one, although core lets a block do so through `allow_empty_state` ([R/block-class.R#L137-L141](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L137-L141)). A default derived from another input, `y = data$y`, could not go into the block expression of a `blockr_expr` at all, since R cannot tell the input from a column of the same name in it, as in `dplyr::select(data, -y)`. A later core can add defaults without breaking a class, since a class without them stays valid.

The `js_module(path, package = utils::packageName())` function keeps the path, relative to the package's `inst/`, and the package whose code calls it, which `utils::packageName()` finds from the caller's environment, as core's `pkg_name()` does today, and R resolves them with `system.file()` when it serves the module. It resolves nothing when it runs, since a package's classes are defined while R installs it, when `system.file()` would give the staging directory, a path a staged install refuses to keep. Outside a package, where it finds none, it resolves the path against the working directory when it runs.

The `volatile()` and `action()` functions return the function they wrap with a class added, `c("volatile", "function")` or `c("action", "function")`, so that a request is still a function, whose formals `new_block_class()` reads, and the block registry marks each request by that class.

Writing a class's expression gets a vignette of its own in blockr.core, within the guide for block class authors ([Client-owned board state](Rewrite-1.1#work)): what `expr` returns, a call, a string, a function or a `blockr_expr`, and what `inputs` is, a character vector, a list from `alist()` or a function; writing inputs as placeholders with `bbquote()`, and why that is the default; which tools keep a placeholder, and why base `bquote()` does not; the block expression a script holds for each of the four and for a variadic block's `...`; a class of a package's own that inherits from `blockr_expr`, with its `interpolate()` method; unset args, with `missing()` and `invalid()`; a state arg written bare, which nothing catches; and data.table's `.()`, which `list()` replaces where it would read as a placeholder. Each case shows its block expression in the script.

Today `register_block()` builds a block to read its classes and, without `arguments`, its arg specs, and checks the specs' examples against it ([R/block-registry.R#L143-L162](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-registry.R#L143-L162)). The class gives the first two, and the examples are checked by calling `expr` with them instead.

</details>
