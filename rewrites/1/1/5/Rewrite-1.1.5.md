# Block classes in R for the client-owned board
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how a package defines and registers a block class in R, and how R evaluates a block with it. It shapes defining block classes, a block class's output, exporting the block registry, the per-session evaluator and the guide for block class authors, each an item in the Work list of [Client-owned board state](Rewrite-1.1#work). A block class's UI, a module that meets the contract, is the UI modules proposal ([UI modules in JS](Rewrite-1.1.7)), the messages that carry a block's recipe and its result are the [wire protocol proposal](Rewrite-1.1.9), how state values travel between the client and R is the [serialization proposal](Rewrite-1.1.4), which renderer draws an output is [Front-ends and extension points](Rewrite-1.1.8#renderers)'s, and when a block is evaluated is the [evaluation proposal](Rewrite-1.1.10).

## What must hold

1. A block class is defined once, as a value, and the constructor made from it returns an S3 block whose args are the block's state; classes are registered as today, under a registry id ([Board objects](Rewrite-1.1.1)).
2. Its R side is plain functions, with no Shiny module server and no reactives.
3. The generics packages implement today keep working wherever they still have a job.
4. Nothing about a class is copied into its blocks, and nothing builds a block to learn about its class.
5. A package plugs into another package's class only through a hook that class offers, or by building a class of its own from that class's fields.
6. A front-end or any other package can replace how core draws an output family, such as tables, without changing a block class.

## Today

A block class calls `new_block(server, ui, class, ctor, ctor_pkg, dat_valid, allow_empty_state, block_name, expr_type, external_ctrl, block_metadata, ...)` or one of its specializations ([R/block-class.R#L180](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L180)). The server is a Shiny module whose formals name the data inputs and which returns `expr`, a reactive expression, and `state`, reactives naming every constructor formal ([R/block-server.R#L969](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L969)). The head block keeps its args in `reactiveVal()`s, syncs them with its inputs through observers, and caps `n` at the number of rows with `updateNumericInput()` ([R/transform-head.R#L27-L91](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/transform-head.R#L27-L91)).

## Proposal

### The block class

A block class is a value made by `new_block_class()`, holding everything that is the same for every block of the class, and its constructor is a function that `block_constructor()` makes from it. A class's `expr` is a function of the block's state args that returns the block's expression, from which R builds the line that it runs and that a script holds (below). The head block, written to the new contract, with illustrative names:

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
  requests  = list(n_max = function(data) nrow(data))
)

new_head_block <- block_constructor(head_block)
```

The constructor has the formals of `expr`, a `block_name` and `...`, so an app script calls `new_head_block(n = 10L)` as today, and the checks in `expr`, such as `match.arg()`, run when it does: it calls `expr` with its args and takes the block's state from the frame `expr` ran in, as the checks left it, `list(n = 10L, direction = "head")` (notes). It returns a block that holds its state, its name and the attributes `...` passes, such as core's `visible` ([Board objects](Rewrite-1.1.1#blocks)), and refers to its class, which every head block shares and none copies. The name keeps today's argument, `block_name`, since `attr()` matches attribute names partially: on a block, a list of its state, that has no `name` attribute, `attr(blk, "name")` returns the block's `names`, as it did when `new_block()` took a `name`. A package exports both: the class, from whose fields another class can be built, and the constructor, which app scripts call.

A class's fields:

- The `name` argument gives the class's name, which leads a block's class vector, `c("head_block", "block")`, and a field the class leaves out takes the root class's default (below).
- The `inputs` field gives the data inputs, apart from the state args, as the formals of the block's function (below), in one of three kinds: a character vector names them, `"data"`, `c("x", "y")` for a merge or `"..."` for a variadic block; a pairlist from `alist()` gives them with defaults where an input is optional or derived from another, `alist(x = , y = NULL)`; and a function gives them as its formals and checks them in its body, `function(data) stopifnot(is.data.frame(data))`, which takes the place of `dat_valid`. Every class with an `expr` declares its own. A block runs only once every input without a default is linked, and a variadic block once it has one link, which the client sees from the block registry, marking the block `waiting` until then without asking R ([Evaluation in the client](Rewrite-1.1.10#statuses)).
- The `expr` field is a function whose formals are the state args and whose body checks them, as a constructor checks its args today, and returns the block's expression (below). An arg without a default starts unset, as a merge's `by` does, and stays out of the block's state until something sets it. Called without args, `expr` gives the state a new block starts with, which may be one that cannot run yet (below).
- The `ui` field names the class's UI, a module written against the contract of [UI modules in JS](Rewrite-1.1.7), in plain TypeScript as core's own are or in TSX with React, which ships the schema of the block's state beside it ([UI modules in JS](Rewrite-1.1.7#packaging)), and the `requests` field takes a named list of R functions for whatever the UI asks of R, such as the head block's `n_max`, whose arguments name the inputs, state args and options they read and any parameters the UI passes (below).
- The `evaluate` and `summary` fields are the functions R runs a block's expression and describes its result with (below).
- The `output` field describes a result for the client, as an output of a family that a renderer draws (below), and the `options` field names the board options the class's own code reads, such as blockr.io's `data_dir`, the directory its read block lists files from, by the constructors that give each option's id and initial value, while the package that ships an option defines it in the client ([Board objects](Rewrite-1.1.1)), and a renderer brings the options it draws with, such as a table's `n_rows` ([Front-ends and extension points](Rewrite-1.1.8#renderers)).
- The `migrate` field maps a state saved by an older version of the class's package to the current state, given that version, and R runs it on the state a file holds when it opens a board ([Serialization](Rewrite-1.1.4#migrations)). The root class's leaves a state as it is.
- The `dat_valid`, `allow_empty_state`, `external_ctrl`, `expr_type` and `block_metadata` fields go. The checks of the data are the body of a function given as `inputs` (above), and they read the data inputs only. A state arg a block needs has no default, any other state that cannot run yet is for a class's `expr` to say (below), and a block waits for its inputs (above), so the glue block, which today renders its text with nothing linked, waits for a link. Every block's state can now be set from outside, R reads from an expression whether it marks its inputs, which `expr_type` declared, and a class's metadata comes from its registration (below).

A class has no say in when its blocks are evaluated: a block that must run with nothing on screen, such as a write block in auto mode, is demanded by a rule its package registers in the client ([Evaluation in the client](Rewrite-1.1.10#demand)).

The functions R runs a block's expression and outputs its result with, `evaluate`, `summary` and `output`, take the class as their first argument, `x`, as an S3 method takes its object, so that a field can read the class's other fields, and a class built from another's fields can call the field it extends, `head_block$output(x, ...)`, as a method calls `NextMethod()`. The other function fields name what they read instead: `expr` the state args, a request the inputs, state args and options it reads, `migrate` the state and the version that saved it, and a function given as `inputs` the data inputs. The `new_block_class()` function checks a class when it is defined, so that no block is checked for being well formed again: that no state arg is `...` or `block_name`; that no input shares a state arg's name, since a request's arguments would not say which they mean; that `inputs` is names, formals or a function of them; that the arguments of each request name inputs, state args or the class's options, but for its parameters, which have a default; that `expr`, called without args, returns a call or a string, or cannot run yet; and, once it reads the schema the class's UI ships, that the schema's properties are the state args. All but the last two read only the class's fields and the formals of its functions.

A sketch of `new_block_class()`, in which a field a class leaves out is the root class's and the checks run for every class with an `expr`:

```r
new_block_class <- function(name, inputs = NULL, expr = NULL, ui = NULL,
                            requests = NULL, evaluate = NULL, summary = NULL,
                            output = NULL, options = list(), migrate = NULL) {

  own <- Filter(Negate(is.null), list(
    inputs = inputs, expr = expr, ui = ui, requests = requests,
    evaluate = evaluate, summary = summary, output = output, migrate = migrate
  ))

  cls <- unclass(block)  # a field left out is the root class's (below)
  cls[names(own)] <- own
  cls$class <- c(name, "block")
  cls$options <- options

  if (!is.null(cls$expr)) {
    stopifnot("inputs are names, formals or a function of them" =
      is.null(cls$inputs) || is.character(cls$inputs) || is.list(cls$inputs) || is.function(cls$inputs))
    input_args <- if (is.character(cls$inputs)) cls$inputs else
      names(if (is.function(cls$inputs)) formals(cls$inputs) else cls$inputs)
    state_args <- names(formals(cls$expr))
    option_ids <- vapply(cls$options, function(new) board_option_id(new()), "")
    stopifnot(
      "no state arg is ... or block_name" = !any(c("...", "block_name") %in% state_args),
      "no input shares a state arg's name" = !any(input_args %in% state_args)
    )
    for (f in cls$requests) {
      params <- setdiff(names(formals(f)), c(input_args, state_args, option_ids))
      stopifnot("a request's other args are parameters, with defaults" =
        all(nzchar(vapply(formals(f)[params], deparse1, ""))))
    }
    res <- tryCatch(cls$expr(), invalid = function(e) NULL, missingArgError = function(e) NULL)
    stopifnot("expr() gives a call or a string" = is.null(res) || is.language(res) || is.character(res))
    # and, once it reads the schema the UI ships, that its properties are the state args
  }

  if (!isNamespace(topenv(parent.frame()))) {
    attr(cls, "call") <- match.call()  # the class's definition, for a file (notes)
  }

  structure(cls, class = "block_class")
}
```

A sketch of `block_constructor()`, which takes the block's state from the frame `expr` ran in and leaves out an arg that is still unset, with `invalid()`:

```r
block_constructor <- function(cls) {

  stopifnot("only a class with an expr has a constructor" = !is.null(cls$expr))

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
    block <- structure(
      mget(state_args[has_default | !unset], frame),  # the state, as the checks left it
      block_name = env$block_name, block_class = cls, class = cls$class
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

What a class's `expr` returns is the block's expression, which R takes in either of two forms, told apart by their R types rather than by a class of its own: a call, built with any tool, such as `bbquote()`, `rlang::expr()` or `call()`, or a string, built such as with `glue::glue()` or `sprintf()`, which R parses. A block is a function of its data inputs, called with its links: R builds the block's function from the formals of `inputs` and the expression, `as.function(c(formals, expression))`, and reduces its call to the expression alone where it can.

An expression marks its inputs, as core's `"bquoted"` blocks do today, `.(data)`, and R puts the id of the upstream block in place of each mark, so that the line a script holds for a head block downstream of block `a` is idiomatic R, `b <- utils::head(a, n = 10L)`. That is the default, which core's own classes use and the guide for authors leads with. Any tool that leaves the mark alone keeps it: `bbquote()` fills in only the values it finds, and `rlang::expr()`, `glue::glue()` and `sprintf()` never read it, while base `bquote()` would try to fill in `.(data)` as well, which is why core keeps `bbquote()`. A variadic block's expression marks its inputs with `...`, which R replaces with the ids of the upstream blocks, in link order and each named by its link's input, which is empty for a positional link ([Board objects](Rewrite-1.1.1#links)): `quote(rbind(...))` gives `rbind(a, b2 = b, c)`.

An expression that leaves its inputs unmarked, as `rlang::expr(utils::head(data, n = !!n))` does, R evaluates through the block's function instead, called with the links, `b <- (function(data) utils::head(data, n = 10L))(a)`, since putting an id in place of a bare name cannot tell the input from a column of the same name in an argument that a function evaluates non-standardly, which is what defeated substituting names in [blockr.core#17](https://github.com/BristolMyersSquibb/blockr.core/issues/17#issuecomment-2630544662). A mark settles that, so `bbquote(subset(.(data), threshold > .(threshold)))` keeps a column called `threshold`, and R trusts the marks: a bare name in an expression that marks its inputs is a column, as `y` in `a$y` is. A value of the state left unmarked looks like such a column too, so nothing catches it before it runs, and outside such an argument its first evaluation fails, with `object 'n' not found`.

An input's default stands in for it while it is unlinked: R puts the default in place of the input's marks, and fills the default's own marks the same way, so that a default written with marks keeps the line idiomatic. With only `data` linked to `a`, the line for this lm block is `m <- stats::lm.fit(as.matrix(a[setdiff(colnames(a), "y")]), a$y)$coefficients`, and with `y` and `x` linked to `c` and `d` as well, `m <- stats::lm.fit(as.matrix(d), c)$coefficients`:

```r
lm_block <- new_block_class(
  "lm_block",
  inputs = alist(y = .(data)$y, x = .(data)[setdiff(colnames(.(data)), "y")], data = ),
  expr   = function() quote(stats::lm.fit(as.matrix(.(x)), .(y))$coefficients)
)
```

A default that names an input without its mark, or a defaulted input the expression marks more than once, which inlining would evaluate once per use, keeps the block's function in the line, `m <- (function(y = data$y, data) y/sum(y))(data = a)`. An optional input's expression branches when it runs, as `if (is.null(.(y))) .(x) else merge(.(x), .(y), by = "id")` does, since `expr` cannot know whether the input is linked.

Whether R reduces the call or not, it evaluates the line a script holds, with each upstream block's result bound to its id (below), so the code a block shows and exports is the code that ran, labels included. Since `expr` never sees an input's data, a class whose expression depends on the data says so in the expression, as `utils::head(.(data), n = min(10L, nrow(.(data))))` caps `n` at the rows it gets, or gets what it needs into its state through a request. R calls `expr` with the args the block's state holds, so a body that uses an unset arg makes R reply `invalid`, naming the arg, as the merge block's does until its `by` is set:

```r
merge_block <- new_block_class(
  "merge_block",
  inputs   = c("x", "y"),
  expr     = function(by, all_x = FALSE, all_y = FALSE) {
    bbquote(merge(.(x), .(y), by = .(by), all.x = .(all_x), all.y = .(all_y)))
  },
  requests = list(shared = function(x, y) intersect(names(x), names(y)))
)
```

A body that can do without an unset arg tests it with `missing()`, as a merge by the columns its inputs share would with `if (missing(by)) bbquote(merge(.(x), .(y)))`, and a body given a state that is set but cannot run signals `invalid()` with a message, such as `invalid("Choose at least one column.")` for a selection the user emptied.

### Requests

A request is a function the UI calls through its host for whatever it needs from R, such as the head block's `n_max`, the maximum of its numeric input, which never enters the block's state ([UI modules in JS](Rewrite-1.1.7#the-contract)). R binds each of its arguments by name, as it calls the block's function: an input to the result of the upstream block at the version the UI's context names, or to its default where it is unlinked, a variadic block's `...` to its inputs in link order, named by their links' inputs, a state arg to the value the UI passes or else the block's state, leaving an unset one missing, an option the class names to the option's value, as blockr.io's read block lists the files under its `data_dir`, and any other argument to a parameter the UI passes, which must have a default, so that `new_block_class()` still catches a misspelled state arg written without one, as a state arg in a request needs none. A parameter holds only what the UI is showing, such as the column whose values a dropdown lists or the text typed into its search, never what the block computes. That holds by construction, since only requests take parameters and `expr` never sees them, so no parameter changes a block's result, expression or saved state:

```r
requests = list(
  values   = function(data, column = NULL, query = "", limit = 1000L) column_values(data, column, query, limit),
  list_dir = volatile(function(path = "") list_dir(path))
)
```

Core keeps each answer by registry id, name, state args, option values, parameters and the versions of the inputs read, as a snapshot of them, so that reopening a column's dropdown is answered without asking R, and data that changes behind an input, such as a database's, is read again once something invalidates the block that reads it ([Evaluation in the client](Rewrite-1.1.10#invalidation)). A request wrapped in `volatile()` is never kept and goes to R every time, which suits a cheap lookup outside the board, such as a directory listing, and nothing expensive. A request wrapped in `action()` acts rather than reads, such as a write block's manual save, which writes once per click outside the block's expression, or an upload, which receives the file the user picked, keeps it where its package decides and returns its path for the block's state: R runs it once per call and it may write, core never keeps or merges its answer, and on a locked board R runs it only if the class declares that it may run there ([UI modules in JS](Rewrite-1.1.7#the-contract)).

### Core's classes and hooks

Core's root class, `block`, gives every field but `inputs` and `expr` its default, and a class leaves out whatever it takes from it: `evaluate` runs the expression with the inputs bound, as `block_eval()` and `eval_env()` do today, `summary` gives the result's class and dimensions, and `output` picks the result's output family by the result's class, a table where `tabular_output()` has a method for it, a plot where it is a recorded plot, drawn at the size and in the theme `info` gives, where today the block re-evaluates when the theme changes ([R/plot-block.R#L59-L68](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plot-block.R#L59-L68)), and text otherwise (below). Today's specializations, `transform_block`, `data_block`, `parser_block`, `plot_block`, `text_block` and `file_block`, go, with `parent`. What they carry follows from a block's result rather than from the block ([R/transform-block.R#L24-L42](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/transform-block.R#L24-L42), [R/plot-block.R#L32-L68](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plot-block.R#L32-L68)): the output and UI of a table, a plot or text, which the root's `output` picks and a renderer draws; the table's board options, `n_rows`, `page_size` and `filter_rows`, which core's table renderer brings ([Front-ends and extension points](Rewrite-1.1.8#renderers)); and a plot's recording, which a class that draws with base graphics asks for by setting its `evaluate` to core's recording evaluator, the one that uses `evaluate::evaluate()`, as core's plot block evaluates today. Nothing outside core dispatches on their classes, which in the workspace appear only in the class vectors blocks are built with, in docs and in tests. Blocks group in other ways too, each with a home of its own rather than a place in one hierarchy: the menu's category, from `@blockCategory` at registration; the output family; a renderer's board options; a class's inputs; and the demand rules of [Evaluation in the client](Rewrite-1.1.10#demand).

A class's fields belong to its package, so another package cannot change a class in place, as an S3 method registered for the block's class can today. Instead, a class offers hooks where other packages are meant to plug in, by calling a generic from a field: `tabular_output()` dispatches on the result's class, so a package that knows another class of table, such as dbplyr's lazy tables, which it pages in the database, registers a method that returns an output of the same family, which every renderer of that family then draws. How an output looks is no hook of a class at all, since any package can replace the renderer of an output family (below). Otherwise, a package builds a class of its own from the other package's class's fields, `new_block_class("my_head", inputs = head_block$inputs, expr = head_block$expr, output = my_output)`, and calls the other class's field where it extends one. No package in the workspace overrides another's block methods today, and the two registrations across packages, blockr.sandbox's methods for blockr.ai's `data_schema()` and `data_effect()` and for blockr.assistant's `describe_result()`, dispatch on result classes and work as before ([blockr.sandbox R/composer.R#L1401-L1418](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/afa235e346145e61af6dd01151b5b14f0ef12549/R/composer.R#L1401-L1418), [R/describe-composed.R#L178-L186](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/afa235e346145e61af6dd01151b5b14f0ef12549/R/describe-composed.R#L178-L186)).

### Registration

The `register_block()` and `register_blocks()` functions keep their arguments but `classes` ([R/block-registry.R#L80](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-registry.R#L80)), and so does the roclet that writes `inst/registry/blocks.yml` from `@block` tags: they take the constructor, as today, and read its block class from it, which gives the class vector (notes). The `uid` argument sets the name part of the registry id, `{pkg}-{name}`, whose name defaults to the constructor's name without `new_` ([Board objects](Rewrite-1.1.1)). The block registry keeps one entry per class, and `registry_id_from_block()` finds a block's entry by the class the block refers to. Registering no longer builds a block: the block registry reads the block class's class vector, its inputs, with which of them have defaults, so that a front-end draws an optional input as such, its UI and the schema the UI ships, its requests and options, and its default state from `expr` called without args, keeps them by registry id so that R resolves a request without a block, and sends all but the classes to the client ([Board objects](Rewrite-1.1.1#what-lives-where)). A class defined outside a package keeps the code it was defined by, since the constructor `block_constructor()` makes holds none of its class in its own source. The block registry sends that code to the client, wrapped in `block_constructor()`, as the class's definition, which a file holds once for the class, under its registry id ([Serialization](Rewrite-1.1.4#files)): the escape hatch of [Board objects](Rewrite-1.1.1#block-classes-outside-a-package). The arg specs default to every state arg, since `external_ctrl_vars()` goes, and describe each for models and tools, while its shape is the schema's ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)).

### Evaluation

R calls a constructor only where an app script builds a board, and where `blockr_deser()` converts a file from today's stack ([Board objects](Rewrite-1.1.1#the-board)), and keeps no block while the app runs. To evaluate a block, it looks the class up by the recipe's registry id, runs the checks of a function given as `inputs` with the linked results, calls its `expr` with the recipe's state, builds from what it returns the line a script holds for the block (above), and evaluates that line with each upstream block's result bound to its id, so that the expression R runs is the one a script holds, labels included, such as the column names `cbind()` takes from its arguments, where today a block whose `expr_type` is `"bquoted"` is evaluated with its inputs' names and exported with the upstream ids in their place ([R/block-server.R#L754-L768](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L754-L768), [R/utils-code.R#L58-L69](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-code.R#L58-L69)). An `invalid()` that `expr` signals, or an unset arg its body uses, makes R run nothing and reply `invalid`, with the message or the arg's name. Otherwise R runs the expression, which its reply carries ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)):

- The `evaluate(x, expression, inputs)` function runs the expression with each upstream block's result bound to its id. The root class's runs it as it is, and core's recording evaluator records the plot.
- The `summary(x, result)` function describes the result in a few words, such as `<data.frame> [150 × 5]`, which R sends with its reply for the header of the block's card ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)). The root class's gives the result's class and dimensions, as `block_summary()` does today ([R/plugin-block.R#L299-L320](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-block.R#L299-L320)), so a front-end has it without asking R again.

R keeps each block's latest result, with its version and expression, in an environment keyed by block id ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)), and binds it as an input of every block downstream, so nothing a class runs may change its inputs in place: copy-on-modify covers most R objects, but not a data.table changed by reference, an environment or an R6 object, whose change would reach the upstream block's result.

### Outputs

A class's `output(x, result, options, info, meta)` returns the result's output for the client: a description in JSON whose `family` names its output family, `{pkg}-{name}` as a registry id is, with whatever else the family holds, and at most one binary body with its MIME type, such as a plot's PNG ([Wire protocol](Rewrite-1.1.9#outputs)). An output family is what such a description holds, which the package defining the family documents, as a MIME type's owner does: core defines `blockr.core-table`, a table's columns, the rows of one page and its total row count, `blockr.core-text` and `blockr.core-plot`. What draws an output is a renderer, a module that a package declares in R for the output families it draws, of which R picks one per family, from the app's blockr options, the front-end, other packages and the package that defines the family, in that order ([Front-ends and extension points](Rewrite-1.1.8#renderers)). An output family is the contract of the package that defines it, and only that package adds to it, in a later version whose new fields older renderers skip, as both sides of the protocol ignore fields they do not know ([Wire protocol](Rewrite-1.1.9#versions)). A package that needs to show more than a family holds, such as the SQL behind a lazy table's page in its database's dialect, takes a family of its own, whose renderer draws what it adds and nests the shared part with the renderer R picked for that part's family, as blockr.dm's view of a dm nests its table (below), while a lazy table with nothing more to show is a `blockr.core-table`, which R pages in the database, as blockr.ui's table preview pages one today ([R/table-preview-engine.R#L67-L68](https://github.com/BristolMyersSquibb/blockr.ui/blob/9bd8312a3408bbcbabff2b57d1d3fd5681843c94/R/table-preview-engine.R#L67-L68)). The client looks a renderer up by the output's one family, since walking a list of families would carry S3 dispatch into the client, which [State in JS](Rewrite-1#principles) keeps in R. So a block class never names what draws its output, and blockr.ui's table preview takes the place of core's plain table for every block whose output is a table.

The `meta` is what the renderer keeps and R reads, such as the page a table shows and its sort, which the renderer changes through its host, asking R for the output again, so an output of the family `blockr.core-table` holds the page `meta` asks for, sorted as it says, with `n_rows` rows to a page unless it gives a page size. A renderer draws an output nested in its own through its host, with the renderer R picked for the nested output's family. The output blockr.dm draws today through `block_ui()` and `block_output()` methods ([R/dm-block.R#L504-L627](https://github.com/BristolMyersSquibb/blockr.dm/blob/8b37981838cfac63a5d40e270a19857e5ef9ea90/R/dm-block.R#L504-L627)) becomes, with illustrative names, an output of a family of its own, whose renderer draws the diagram and has the selected table drawn by the app's renderer for tables:

```r
dm_block <- new_block_class(
  "dm_block",
  # inputs, expr, ui and requests left out
  output = function(x, result, options, info, meta) {
    list(
      family  = "blockr.dm-dm",
      diagram = dm_keylines_meta(result),
      preview = if (length(meta$table)) tabular_output(result[[meta$table]], options, info, meta)
    )
  }
)

register_renderer("dm", js_module("dm-output.js"), family = "blockr.dm-dm")   # in .onLoad()
```

### Generics

| Generic | Becomes |
|---|---|
| `block_output(x, result, session)` | the class's `output`, returning an output whose family a renderer draws (above) |
| `block_ui(id, x)`, `block_render_trigger()` | gone, since a renderer draws the output and options are arguments |
| `tabular_output(x, result, block, session)` | `tabular_output(result, options, info, meta)`, dispatching on the result rather than a display and returning an output of the family `blockr.core-table` (above) |
| `tabular_display()`, `tabular_ui()`, `tabular_trigger()`, `tabular_options()` | gone, with the display classes and the `tabular_display` blockr option, since a renderer of `blockr.core-table` takes a display's place, with the board options it brings (above) |
| `block_eval(x, expr, env, ...)` | the class's `evaluate` |
| `block_eval_trigger()` | gone, since options never re-evaluate and any component can invalidate a block |
| `board_options(x)` | the class's `options` and those of the renderers R picked, while a board class keeps its own `board_options()` method |
| `blockr_ser()`, `blockr_deser()` | kept, `blockr_ser()` to write a script's board and `blockr_deser()` to convert files from today's stack, while a file of the new stack migrates through the class's `migrate` |
| `block_summary(x, data)` | the class's `summary`, which R sends with every evaluation's reply (above) |
| `block_server()`, `expr_server()`, `expr_ui()` | gone |
| `block_inputs(x)` | the class's `inputs` |
| `external_ctrl_vars(x)` | gone |
| `block_metadata(x, fields)` | the class's entry in the block registry, read by registry id |
| `str_value(x)` | kept for printing R objects, without the `*` that marks the args `external_ctrl_vars()` names, while blockr.assistant, which describes a board to a model with it, runs its agent loop in the browser ([Assistant as a client extension](Rewrite-1.4)) |

### JS-driven blocks

The JS-driven blocks of blockr.dplyr are close to this already: `new_select_block()` passes `state` and `expr_fn` to its factory, `new_js_transform_block()`, whose server only keeps JS and R in step ([R/select_block.R#L29-L52](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/68e1b54d2d1e028c96b77d03f8887b12b6d872b8/R/select_block.R#L29-L52)). Under the contract the factory becomes a function that calls `new_block_class()` with the fields its classes share, and its server goes, the JS becomes a module, `expr_fn` the class's `expr`, which takes the state args rather than a list and returns the call `expr_fn` builds today, `.(data)` mark included ([R/expr-builders.R#L404-L409](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/68e1b54d2d1e028c96b77d03f8887b12b6d872b8/R/expr-builders.R#L404-L409)), and the columns the JS receives as messages a request.

### Testing

Core ships helpers to test a block class without Shiny: its `expr` with sample states, its `evaluate` with sample inputs, its requests, its `output`, and its module against a stub host. They replace `testServer()`. A class's R tests and its module tests share one fixture file in its package's `tests/`, since the class's two halves meet only in JSON: the file lists states, the R tests record into it what the class's requests answer for sample inputs, states and parameters and check that the expression built for each state runs, and the module tests serve the recorded answers through the stub host and check that the module submits only listed states, the pattern of consumer-driven contract tests ([Pact](https://docs.pact.io/)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

A class defined outside a package, where the caller's `topenv()` is no namespace, keeps the call `new_block_class()` was made with, from `match.call()`, rather than having its value written out later. Written out, a field taken from another class, such as `head_block$expr`, would be written in full, where the developer wrote `head_block$expr`, and a class's value in the internal layout of the core that saved it, which a later core may lay out differently. The definition is that call wrapped in `blockr.core::block_constructor()`, with the package objects it names qualified, `head_block` as `blockr.core::head_block`, and a class the script defines and this one takes fields from written as its own call, nested. Nothing else the call or its functions take from the script, such as a helper or a data frame, can go into a file, so `new_block_class()` warns about each such name when the class is defined, finding them with `codetools::findGlobals()` and resolving them from the caller's environment. A UI the class names by file is a plain JS module, which goes into the definition as the file's text, so that a file brings the UI along, since core loads JS only ([UI modules in JS](Rewrite-1.1.7#packaging)).

The constructor takes the state from the frame `expr` ran in, through a copy of `expr` that hands the frame over as it exits (above), so that what the checks in `expr` change, such as `match.arg()` picking `"head"` out of `c("head", "tail")`, is the state the block holds, as `initial_block_state()` reads a block's state from its server's environment today ([R/block-class.R#L719-L725](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-class.R#L719-L725)). An arg without a default stays out of the state while `missing()` finds it missing in the frame, so one the body assigns, such as a value it works out, is in it. The frame is kept when `expr` signals `invalid()` too, so a class checks its args before it signals. R tells a body's use of an unset arg by the class `missingArgError`, which R 4.5.0 added and `bbquote()` raises too when it fills in the mark of an unset arg, and in older R by the error's message, translated as R translates it. The `bbquote()` function reads only the names of the frame it runs in, so that the mark of an input, `.(data)`, stays for R to fill in, although `utils::data` exists. A pairlist from `alist()` holds each default unevaluated, as `formals()` gives a function's, so R reads a default as code. R puts the upstream id or, for an unlinked input, its default in place of an input's mark wherever it is, and in place of `...` wherever it is an argument of a call, but not inside a function the expression defines, whose `...` is its own.

Writing a class's expression gets a vignette of its own in blockr.core, within the guide for block class authors ([Client-owned board state](Rewrite-1.1#work)): the two forms `expr` returns and the three kinds of `inputs`; marking inputs with `.()`, in the expression and in defaults alike, and why that is the default; which tools keep a mark, and why base `bquote()` does not; the line a script holds for a marked input, an unmarked one, an unlinked one with a default and a variadic block's `...`; an optional input's branch; unset args, with `missing()` and `invalid()`; and a value of the state left unmarked, which nothing catches. Each case shows its line of the script.

Today `register_block()` builds a block to read its classes and, without `arguments`, its arg specs, and checks the specs' examples against it ([R/block-registry.R#L143-L162](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-registry.R#L143-L162)). The class gives the first two, and the examples are checked by calling `expr` with them instead.

</details>
