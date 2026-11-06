# Board options and blockr options
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): the two kinds of option, board options and blockr options, what sets them apart, and how each reaches the code that reads it, in the client and in R.
It takes over what [Board objects](Rewrite-1.1.1#board-options) and [Defining a board in R](Rewrite-1.1.3#blockr-options) said about them, and shapes `CoreApi` and starting the page ([blockr.core#440](https://github.com/BristolMyersSquibb/blockr.core/issues/440)), core's basic front-end ([blockr.core#441](https://github.com/BristolMyersSquibb/blockr.core/issues/441)), the lock ([blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434)) and the migration notes for app scripts ([blockr.core#445](https://github.com/BristolMyersSquibb/blockr.core/issues/445)), each an item in the Work list of [Client-owned board state](Rewrite-1.1#work).
How a delta sets a board option's value is [Board updates](Rewrite-1.1.2#deltas)'s, how a JSON board records the value is [Serialization](Rewrite-1.1.4#board-options)'s, the hosts through which a module reads it are [UI modules in JS](Rewrite-1.1.7#the-contract)'s, and the `blockr_options` message is [Wire protocol](Rewrite-1.1.9#blockr-options)'s.
Each blockr option belongs to the page of the code that reads it, as the three that the scheduler reads belong to [Evaluation in the client](Rewrite-1.1.10#scheduling).

## What must hold

1. A board option is defined once, in the client, by the package that ships it, and R holds only its id and a value that a script gives it.
2. Each component that reads a board option's value names the board option in its own definition: a board class, a renderer, a board option's UI, or a block class in its UI module, which also names every board option that the class's requests read.
   The board holds a value for the board option before that component first reads it, on a locked board too.
3. A board holds a value only for a board option that something on the page has required since the board opened, or that a script, a file or a command has set.
4. A change to a board option's value evaluates no block, since no board option reaches `expr`, and neither undo nor redo changes a board option's value.
5. A blockr option is fixed when the app starts or is deployed, by an R option or an environment variable, and neither a board nor a file holds one.
6. Client code reads a blockr option only by asking R for it by name, and nothing declares a blockr option in R.
7. A board option takes a blockr option's value only as its default, which its definition in the client reads, so that R computes no default.

## Today

Both kinds live in R today.
A board option is an S3 object of a class of its own, such as `n_rows_option`, which `new_board_option()` makes with its id, default, Shiny UI and server, transform, category, label and constructor ([R/board-option.R#L16-L37](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L16-L37)).
R dispatches on that class, as for the check `validate_board_option.n_rows_option()` ([R/board-option.R#L366-L378](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L366-L378)).
Its constructor reads its default from a blockr option, as `new_n_rows_option(value = blockr_option("n_rows", 50L))` does ([R/board-option.R#L330-L363](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L330-L363)).
A board holds `default_board_options()` unless its script gives others ([R/board-options.R#L44-L51](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-options.R#L44-L51)).
The app then collects the board options of the board, of its blocks and of every registered block class, through `blockr_app_options()` and the methods of `board_options()` ([R/utils-serve.R#L167-L178](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L167-L178)).

A blockr option is a value that `blockr_option()` reads from an R option `blockr.<name>` or an environment variable `BLOCKR_<NAME>`, which a deployment such as Connect sets without touching the script ([R/utils-misc.R#L247-L276](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-misc.R#L247-L276)).
Today's packages read 56 of them, such as core's `show_conditions` and the dock's `view_tabs`.

## Proposal

### The two kinds

A value that the user changes while the app runs is a board option, and a value that the app or its deployment fixes is a blockr option.
So a board's JSON describes the board in full, and holds nothing of the deployment.

| | Board option | Blockr option |
|---|---|---|
| Example | `n_rows`, the number of rows on a page of a table output | `gate_visibility`, which has core demand every block when it is `FALSE` |
| Set by | The user through its UI, the assistant or an extension through a command, a script through its constructor, or a file | The app through an R option `blockr.<name>`, or a deployment through an environment variable `BLOCKR_<NAME>` |
| Changes | Whenever a command sets it | Never while the app runs |
| Held by | The board, under the board option's id | Nobody: R reads it where its code needs it, and the client keeps what it asked R for until the page closes |
| Saved | With the board, and never undone | Never |
| Defined | Once, in the client, by the package that ships it | Nowhere: the code that reads it names it and gives a fallback |
| Read by | Only a component that names it, as a block class does in its UI module, and the board option's own UI | Any code, through `blockr_option()` in R and `CoreApi.blockrOption()` in the client |

### Defining a board option

A board option is an instance of one type, `Option`, rather than a type of its own ([State in JS](Rewrite-1#principles)).
What R's methods for a board option's class do today becomes data or a function on the instance, so nothing dispatches on a board option's type.
The package defines it in the client because what a new value does on the page, such as switching the theme for `dark_mode`, is code that the board option's Shiny `server` runs in R today ([R/board-option.R#L572-L582](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L572-L582)), which R could not describe to the client.
The package that ships a board option registers it from its startup module, through `core.options.register()`, before the store opens a board ([UI modules in JS](Rewrite-1.1.7#startup-modules)).
Core registers its own three, `n_rows`, `show_conditions` and `dark_mode`, which `coreOptions(core)` makes, as it starts the page.

```ts
interface Option {                                 // as the package that ships it registers it in the client
  id: OptionId;                                    // "n_rows", stable, the key of its value in the board
  label: string;                                   // "Preview rows", what the user sees
  category: string;                                // "Table options"
  schema: JsonSchema;                              // the values it takes, with a description for a model
  default: Json | (() => Promise<Json>);           // what core adds where the board lacks a value, or a function core calls for it
  ui: OptionModule;                                // its UI module, which gets an OptionHost
  onChange?(value: Json, core: CoreApi): void;     // what a new value does on the page, such as switching the theme
  migrate?(value: Json, version: number): Json;    // converts a value that a JSON board records at an older version of its shape
}
```

The `n_rows` board option is the instance that `nRows()` makes, which takes its default from the blockr option `n_rows`, as today's R constructor does:

```ts
const nRows = (core: CoreApi): Option => ({
  id: "n_rows",
  label: "Preview rows",
  category: "Table options",
  schema: {
    type: "integer",
    minimum: 1,                                    // a page of a table holds a row at least
    description: "How many rows of a table a block's output shows",
  },
  default: () => core.blockrOption("n_rows", 50),  // the blockr option n_rows where it is set, else 50
  ui: nRowsInput,                                  // the module blockr.core ships for it
});

// and in the board, once a component that requires it has come onto the page: options: { n_rows: 50 }
```

The id says which board option it is and never changes, while the label is only what the user sees.
The user does not rename a board option, so its label takes the place of a name.
The client holds one definition per id, and a second registration of an id fails.
The store checks every value that a delta sets against the board option's schema ([Board objects](Rewrite-1.1.1#what-the-store-checks)), and R writes a value that a script gives by the copy of the schema that the board option's package ships beside its startup module ([UI modules in JS](Rewrite-1.1.7#packaging)).

A definition's `default` is a value, or a function that core calls the first time the board option is required after a board opens.
Core keeps the function's result until the next board opens, so nothing is read for a board option that nothing requires.
A default that reads a blockr option whose value the schema refuses, such as an `n_rows` of `"many"`, reports the value and takes its fallback.
Core calls `onChange` with each value that the board takes for the board option, both as a board opens holding one and as a delta changes it, which `dark_mode` needs to switch the page's theme.
The `migrate` function converts a value that a JSON board records at a version of its shape below the one that the package's method of `board_option_version()` gives in R ([Serialization](Rewrite-1.1.4#board-options)).

### Which board options a board holds

A board option comes onto a board through the components that require it.
Each component names the board options it requires in its own definition:

- A board class, in the `options` of its definition ([Board objects](Rewrite-1.1.1#the-board)).
- A renderer, in the `options` of its module, an array of ids beside `render()`, as core's table renderer names `n_rows`.
- A board option's UI, in the `options` of its module, as a renderer does, for the board options it reads besides its own.
- A block class, in the `options` of its UI module, those that its requests read included.

The UI module is the one place where a block class names its board options.
A request's `options` in R says only which of them the request reads, so that R binds them to its function's arguments and the client sends their values with it ([Board option values in R](#board-option-values-in-r)).
The block registry entry carries each request's board options to the client by id.
Core refuses a module whose `options` leaves out a board option that a request of its class names, as it refuses one that declares another major of its JS API ([UI modules in JS](Rewrite-1.1.7#the-contract)).
It shows the error in the block's element, naming the module, the request and the board option, so that the gap shows on the first mount rather than as a request that reaches R without the value.

Core adds each board option that a component requires and the board lacks, with its definition's `default`:

1. A board class's, as the store opens the board.
2. A block class's, before core first calls its module's `render()` after the board opens.
3. A renderer's, before core first asks R for an output that the renderer draws, which the block registry entry makes possible ([The renderer before the first output](#the-renderer-before-the-first-output)).
4. Those of a board option's UI, before core first calls its module's `render()`.

So a board opened later gets them as a page that starts with that board would ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).
Core adds a value through its command `blockr.core-set_option`, under core's own origin, by which a locked board tells it apart ([Locked boards](#locked-boards)).
A board option that a board class requires but no loaded package defines refuses the board, naming the board option and the class, before any default runs, and so does a required default that fails or does not fit its schema ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)).
For a renderer, a board option's UI or a block class, core reports such a board option, naming it and what requires it, and mounts the module without it.

From then on the board holds the value: a command changes it, a save writes it, and opening the saved board restores it ([Serialization](Rewrite-1.1.4#board-options)).
So a board holds no value for a board option that nothing has required since it opened, and nothing yet removes the value of one whose component has gone.
A script gives a board option only to set a value other than its default, and nothing in R decides which board options a board has.

Undo never takes a value back, nor does redo set it again, since a board option never changes what the board computes, and most say only how it shows: a step's inverse holds no board option values, and a step that sets only those is no undo step ([Board updates](Rewrite-1.1.2#undo)).

### The renderer before the first output

R makes an output only with the board options its coercion reads.
The coercion `as_table_output()`, for one, pages a data frame by `n_rows`, and has no fallback of its own.
The client, though, learns the renderer that requires them from the output itself ([Front-ends and extension points](Rewrite-1.1.8#renderers)).
Without more, a fresh board's first table could never draw: R needs `n_rows` to make the output, and core adds `n_rows` only once an output has named its renderer.
R therefore also names the renderer of a block class's outputs in the class's registry entry ([Block classes in R](Rewrite-1.1.5#registration)):

1. An output class gives its coercion through its method of `output_coercion()`, as `output_coercion.table_output()` returns `as_table_output`.
2. R finds the output class whose coercion the block class names in `output`.
3. R puts into the entry's `renderer` what that output class's method of `output_renderer()` gives, which takes the app's choice in the blockr option `renderers` into account.
4. The client loads that renderer and adds the board options it names, and only then asks R for the block's first output.

An output of a subclass that has a renderer of its own still names that renderer, and core draws it with that one, adding its board options as it mounts it.
An entry names no renderer where no output class gives the coercion that its block class names, and the first output request then carries every board option that the board holds.

### Board option values in R

In R a board option is its id and the value a script gives it, as `new_board_option(id, value)` makes it.
Its constructor, such as `new_n_rows_option(25)`, takes the value alone and computes nothing: no default from a blockr option, no transform and no check, since the board option's definition in the client holds all of that.
The `new_board()` function holds no board options unless a script gives some, as `new_board(options = new_n_rows_option(25))` does, and R writes each such value under its id, with the version of its shape ([Serialization](Rewrite-1.1.4#board-options)).

R code reads a board option's value only where it names the board option:

- A block class's request names which of the class's board options it reads through `new_block_request(fun, options = )`, each one that the class's UI module names ([Which board options a board holds](#which-board-options-a-board-holds)).
  Given one constructor, its function takes that board option's value in its argument `options`.
  Given a list of constructors named by arguments, its function takes each value in the argument of that name.
  No argument is matched to a board option by its name, and a value comes whole, whatever its shape ([Block classes in R](Rewrite-1.1.5#requests)).
- An output class's coercion gets, in its `options`, the values of the board options that the renderer's module names, as `as_table_output(df, options = list(n_rows = 50L))` pages by `n_rows` ([Block classes in R](Rewrite-1.1.5#outputs)).
  A board option that the coercion reads is part of the class's contract, so every renderer of the class requires it.

Registration calls each constructor that a request names once, to read the board option's id for the registry entry, and drops the object.
The client sends a block class's request the values of the board options that the request names, and an output request those that the renderer names, each as the board holds it, by id.
It keeps the answer or the output by those values, so that a change to any other board option leaves it alone ([UI modules in JS](Rewrite-1.1.7#the-contract)).
A board option's own requests, which its package registers in R under the board option's id, get only the args that its UI passes, as blockr.io's data directory board option has R list a directory that its UI names ([Front-ends and extension points](Rewrite-1.1.8#what-a-package-declares-in-r)).
No board option reaches `expr` or `block_eval()`, so a change to one evaluates no block, and one that shapes outputs redraws them without evaluating ([Client-owned board state](Rewrite-1.1#proposal)).

### Reading a board option in the client

- A block class's UI module gets, in its context, the values of the board options it names, so that it shows what depends on them, as blockr.io's path field shows the data directory as its prefix ([UI modules in JS](Rewrite-1.1.7#the-contract)).
- A renderer gets, through its output host's `options()`, the values of the board options its module names, as the output it holds was asked with.
- A board option's UI gets an `OptionHost`, whose `value()` gives the board's value, or else the board option's default, which core resolves before it calls the module's `render()`, and whose `submit()` runs `blockr.core-set_option` ([UI modules in JS](Rewrite-1.1.7#the-contract)).
  A front-end mounts it with `mountOption()` where it shows the board options that the board holds, as core's basic front-end does in its toolbar and the dock in its options sidebar ([Front-ends and extension points](Rewrite-1.1.8#what-core-gives-a-front-end)).
  An app replaces it with a renderer that it names in the blockr option `renderers` ([Front-ends and extension points](Rewrite-1.1.8#renderers)).
- Other client code reads the values in `store.board().options` and follows them through `store.subscribe()` ([Board updates](Rewrite-1.1.2#following-the-board)).

### Locked boards

A locked board keeps the board options that the app set, as it keeps its blocks, links and stacks ([Wire protocol](Rewrite-1.1.9#locked-boards)).
A board option still comes with the component that requires it, so core adds one that a component requires and the board lacks, with its default, since the app set no value for it ([Which board options a board holds](#which-board-options-a-board-holds)).
The store tells that delta apart by core's origin and lets it through, and refuses every other delta that sets or removes a board option's value, so that nothing else adds a board option to a locked board or changes one.
R takes a request's own value for a board option that the app script set none for, so the default that core added reaches R, while R keeps a value that the app set whatever a request carries.

### Blockr options

An app fixes its blockr options when it starts or is deployed, as today, and the mechanism carries over: `blockr_option()` reads each one from an R option or an environment variable.
The blockr options follow the code that reads them, since each part keeps, drops or adds blockr options as it translates its code rather than copying it ([State in JS](Rewrite-1#principles)).
R reads the blockr options that its own code needs where it needs them, as today.
The client can read neither an R option nor an environment variable of the server, so client code asks R for a blockr option by name, through `CoreApi.blockrOption(name, fallback)`, which passes the values in rather than having code read a global ([Front-ends and extension points](Rewrite-1.1.8#what-core-gives-a-front-end)):

1. Core asks R the first time code reads a blockr option, with a `blockr_options` request, and the names that code reads within one task go in one request ([Wire protocol](Rewrite-1.1.9#blockr-options)).
2. R replies with the value of each blockr option it has a value for, as `blockr_option()` reads it.
3. Core keeps each value until the page closes, since a blockr option is fixed for the app, and gives the code its fallback where R has no value.

A value that an environment variable sets arrives as a string, which core converts to the fallback's type, a number or a logical, since only the code that reads a blockr option knows its type.
R writes `Inf` as `null`, which core reads as `Infinity` where the fallback is a number.
Nothing declares a blockr option in R: the code that reads one names it and gives its fallback.
R answers for any blockr option, since a client can read whatever the R process can ([State in JS](Rewrite-1#proposal)).
Core asks for the blockr options its scheduler reads as soon as R has answered its `hello`, so that they are there before the scheduler starts ([Evaluation in the client](Rewrite-1.1.10#scheduling)).
A blockr option whose value R cannot write as JSON, such as `renderers`, which holds renderer objects, is read by R's code alone.

A constructor argument that configures rather than holds state is lost to the JSON, which keeps what the board holds and nothing else.
Such an argument becomes a blockr option where it is a value, and it moves to the code that calls it where it is a function.
The assistant's system prompt is a function of this kind: `new_assistant_extension()` takes it as `system_prompt` ([vignettes/intro.Rmd#L124-L153](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/vignettes/intro.Rmd#L124-L153)), and a board restored from a file loses it already ([R/ext-server.R#L1229-L1231](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/ext-server.R#L1229-L1231)).
It is R code only because ellmer runs the agent loop in R, and it becomes JS logic of the assistant extension once that loop runs in the browser ([Assistant as a client extension](Rewrite-1.4)).

### Where the two meet

A board option's definition may take its default from a blockr option, through `CoreApi.blockrOption()`, as core's `n_rows`, `show_conditions` and `dark_mode` each read the blockr option of their own id, with today's fallback.
So a deployment that sets `BLOCKR_N_ROWS=25` gives 25 rows per page to every board that holds no value for `n_rows`.
The default applies only where the board lacks a value: a value that a script gives wins over it, and a board saved with 50 rows per page opens with 50 under any deployment.
Where no blockr option sets `dark_mode`, its default is the theme that the user's system prefers, read from `prefers-color-scheme`, as today's fallback of `NULL` has the page follow that theme.
That is the only link between the two kinds.
R computes no default for a board option, a blockr option never changes a value that the board holds, and nothing sets a blockr option from a board option.
The blockr option `renderers` also replaces a board option's UI (above), which changes how the value is drawn and never the value.

## Open questions

None.

<details><summary>Notes for implementers</summary>

The departures that this page takes in come from the bodies of [blockr.core#451](https://github.com/BristolMyersSquibb/blockr.core/pull/451) (requests name their board options through `new_block_request()`), [blockr.core#460](https://github.com/BristolMyersSquibb/blockr.core/pull/460) (a board option's R object holds its id and value, with a table of today's functions and what replaced each), [blockr.core#468](https://github.com/BristolMyersSquibb/blockr.core/pull/468) (a module names its board options in `options`), [blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474) (board classes require board options), [blockr.core#480](https://github.com/BristolMyersSquibb/blockr.core/pull/480) (core's definitions and the output host's `options()`) and [blockr.core#494](https://github.com/BristolMyersSquibb/blockr.core/pull/494) (the renderer in the registry entry, the caller of `onChange` and the reads of blockr options).

On `js-state`, core adds the board options that a module names in `addOptions()` in `srcts/mount/block.ts`, as this page has it, but does not check them against those that the `requests` of the class's registry entry name.
This page has core refuse there a module that leaves one of them out, before it adds the module's board options.
The reads of blockr options are `createBlockrOptions()` in `srcts/core/blockr-options.ts`, and core's definitions are `nRows()`, `showConditions()`, `darkMode()` and `coreOptions()` in `srcts/options/`.
In R, `new_block_request()` is in `R/block-request.R` and `output_coercion()` in `R/output-class.R`.
On `js-state`, `commit()` in `srcts/store/commit.ts` keeps a step's board option values in its inverse, which this page leaves out, as settled on [blockr#503](https://github.com/orgs/BristolMyersSquibb/discussions/503#discussioncomment-19358997).

An origin is a string that any caller of `store.apply()` or `commands.run()` may give ([Board updates](Rewrite-1.1.2#the-store)), so code that holds `CoreApi` could give core's own.
That opens no hole in the lock: the store's refusals keep the user and front-ends from changing what the app fixed, while R holds the lock for what it evaluates, keeping a value that the app set whatever a request carries ([blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434)).

</details>
