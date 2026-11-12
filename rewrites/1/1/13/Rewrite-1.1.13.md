# Board options and blockr options
Status: settled on 2026-11-08. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): the two kinds of option, board options and blockr options, what sets them apart, and how each reaches the code that reads it, in the client and in R.
It takes over what [Board objects](Rewrite-1.1.1#board-options) and [Defining a board in R](Rewrite-1.1.3#blockr-options) said about them, shaped `CoreApi` and starting the page ([blockr.core#440](https://github.com/BristolMyersSquibb/blockr.core/issues/440)) and core's basic frontend ([blockr.core#441](https://github.com/BristolMyersSquibb/blockr.core/issues/441)), which are built, and shapes the locks ([blockr.core#434](https://github.com/BristolMyersSquibb/blockr.core/issues/434)), the migration notes for app scripts ([blockr.core#445](https://github.com/BristolMyersSquibb/blockr.core/issues/445)), refusing a block class's UI module that leaves out a board option its requests read ([blockr.core#502](https://github.com/BristolMyersSquibb/blockr.core/issues/502)), leaving board option values out of undo and redo ([blockr.core#503](https://github.com/BristolMyersSquibb/blockr.core/issues/503)), resolving the defaults of the board options that plugin classes name ([blockr.core#506](https://github.com/BristolMyersSquibb/blockr.core/issues/506)), core's basic frontend's among them ([blockr.core#507](https://github.com/BristolMyersSquibb/blockr.core/issues/507)), keeping the defaults beside the board and calling `onChange` as each board opens ([blockr.core#508](https://github.com/BristolMyersSquibb/blockr.core/issues/508)), refusing a board that holds a value its schema refuses ([blockr.core#509](https://github.com/BristolMyersSquibb/blockr.core/issues/509)), answering a `blockr_options` request name by name ([blockr.core#510](https://github.com/BristolMyersSquibb/blockr.core/issues/510)), naming the package of a board option in its errors ([blockr.core#514](https://github.com/BristolMyersSquibb/blockr.core/issues/514)) and telling a package in the guide to give its output class's coercion ([blockr.core#516](https://github.com/BristolMyersSquibb/blockr.core/issues/516)), each an item in the Work list of [Client-owned board state](Rewrite-1.1#work).
How a delta sets a board option's value is [Board updates](Rewrite-1.1.2#deltas)'s, how a JSON board records the value is [Serialization](Rewrite-1.1.4#board-options)'s, the hosts through which a module reads it are [UI modules in JS](Rewrite-1.1.7#the-contract)'s, and the `blockr_options` message is [Wire protocol](Rewrite-1.1.9#blockr-options)'s.
Each blockr option belongs to the page of the code that reads it, as the three that the scheduler reads belong to [Evaluation in the client](Rewrite-1.1.10#scheduling).

## What must hold

1. A board option is defined once, in the client, by the package that ships it, and R holds only its id and a value that a script gives it, beside what its package gives in R for the board option's class `{id}_option`: the version of the value's shape and the board option's own requests.
2. Each component that reads a board option's value names the board option in its own definition: a plugin class, a renderer of outputs, or a block class in its UI module, which also names every board option that the class's requests read, while a board option's UI reads its own value alone.
   Core gives that component the board's value, or else the board option's default, before it first reads it, on a locked board too, unless no loaded package defines the board option or its default fails or does not fit its schema, which core reports.
3. A board holds a value only for a board option that a script, a file or a command has set, so that it saves what someone chose and no default.
4. A change to a board option's value evaluates no block, since no board option reaches `expr`, and neither undo nor redo changes a board option's value.
5. A blockr option is fixed when the app starts or is deployed, by an R option or an environment variable, and neither a board nor a file holds one.
6. Client code reads a blockr option only by asking R for it by name, but for the two locks, `lock_load` and `locked`, which R sends in the reply to `hello`, and nothing declares a blockr option in R.
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

A board option is a value that the user changes while the app runs, meant above all for how the board is shown, and a value that the app or its deployment fixes is a blockr option.
So a board's JSON describes the board in full, and holds nothing of the deployment.
A board option is no substitute for a plugin's state, where a setting of the plugin's own goes first ([Plugins](Rewrite-1.1.12#a-plugins-state)).

| | Board option | Blockr option |
|---|---|---|
| Example | `n_rows`, the number of rows on a page of a table output | `gate_visibility`, which has core demand every block when it is `FALSE` |
| Set by | The user through its UI, the assistant or another plugin through a command, a script through its constructor, or a file | The app through an R option `blockr.<name>`, or a deployment through an environment variable `BLOCKR_<NAME>` |
| Changes | Whenever a command sets it | Never while the app runs |
| Held by | The board, under the board option's id, once someone sets it, and otherwise core, which resolves its default for each opening | Nobody: R reads it where its code needs it, and the client keeps what it asked R for until the page closes |
| Saved | With the board where someone set it, and never undone | Never |
| Defined | Once, in the client, by the package that ships it | Nowhere: the code that reads it names it and gives a fallback |
| Read by | Only a component that names it, as a block class does in its UI module, and the board option's own UI | Any code, through `blockr_option()` in R and `CoreApi.blockrOption()` in the client |

### Defining a board option

A board option is an instance of one type, `Option`, rather than a type of its own ([State in JS](Rewrite-1#principles)).
What R's methods for a board option's class do today becomes data or a function on the instance, so nothing in the client dispatches on a board option's type.
The package defines it in the client because what a new value does on the page, such as switching the theme for `dark_mode`, is code that the board option's Shiny `server` runs in R today ([R/board-option.R#L572-L582](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L572-L582)), which R could not describe to the client.
The package that ships a board option lists it in R with one module, whose default export is the board option's `Option` without its id, and core registers it from there before the store opens a board ([UI modules in JS](Rewrite-1.1.7#modules-of-plugin-classes-and-board-options), [blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)).
Core lists its own three, `n_rows`, `show_conditions` and `dark_mode`, as any package lists its board options, each with a module of its own, which core registers as it starts the page and again as each board opens, since an opening ends the board options registered before it ([Drawing the board](Rewrite-1.1.8#opening-a-board), [blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)).

```ts
interface Option {                                 // as core registers it in the client, from its module's default export, which leaves out the id
  id: OptionId;                                    // "n_rows", stable, which the board holds its value under
  label: string;                                   // "Preview rows", what the user sees
  category: string;                                // "Table options"
  schema: JsonSchema;                              // the values it takes, with a description for a model
  default: Json | ((core: CoreApi) => Promise<Json>);   // what readers get where the board holds no value, or a function core calls for it with CoreApi
  ui: OptionModule;                                // its UI module, which gets an OptionHost
  onChange?(value: Json, core: CoreApi): void;     // what a new value does on the page, such as switching the theme
  migrate?(value: Json, version: number): Json;    // converts a value that a JSON board records at an older version of its shape
}
```

The `n_rows` board option is the default export of the module that core lists for it, which takes its default from the blockr option `n_rows`, as today's R constructor does, through the `CoreApi` that core passes its `default` ([blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)):

```ts
export default {                                   // the module of n_rows, which core lists under that id
  label: "Preview rows",
  category: "Table options",
  schema: {
    type: "integer",
    minimum: 1,                                    // a page of a table holds a row at least
    description: "How many rows of a table a block's output shows",
  },
  default: (core) => core.blockrOption("n_rows", 10),   // the blockr option n_rows where it is set, else 10, through the CoreApi that core passes
  ui: nRowsInput,                                  // its UI, which the module holds
} satisfies Omit<Option, "id">;

// and in the board only once someone sets it, as options: { n_rows: 25 }, while every reader gets 10 until then
```

The id says which board option it is and never changes, while the label is only what the user sees.
The user does not rename a board option, so its label takes the place of a name.
The client holds one definition per id, which R makes sure of first: two packages that list one id stop the app as `serve()` is called, naming both, since the reply holds one entry for each id ([blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)).
The store checks every value that a delta sets against the board option's schema, and refuses a value for a board option that no loaded package defines ([Board objects](Rewrite-1.1.1#what-the-store-checks)), while it refuses a JSON board that holds a value the schema refuses once migrated, naming the board option, and the page stays as it was ([Board updates](Rewrite-1.1.2#opening-a-board)).
R writes a value that a script gives by the schema that the board option's package ships beside its module, as core does for its own three ([UI modules in JS](Rewrite-1.1.7#packaging)).

A definition's `default` is a value, or a function that core calls the first time the board option is required after a board opens, or as the board opens where the board option has an `onChange` (below).
Core keeps the function's result until the next board opens, so nothing is read for a board option that nothing requires and that has no `onChange`.
A default that reads a blockr option whose value does not convert to the fallback's type, such as an `n_rows` of `"many"`, reports the value and takes the fallback ([Blockr options](#blockr-options)).
Core calls `onChange` as each board opens, for every board option that has one, with the board's value or else the board option's default, which it resolves then whether or not anything on the page requires the board option, and again as a delta sets or removes the board's value, so that what `onChange` does on the page follows the board that is open, as the theme that `dark_mode` switches does ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).
The `migrate` function converts a value that a JSON board records at a version of its shape below the one that the package's method of `board_option_version()` gives in R ([Serialization](Rewrite-1.1.4#board-options)).

### Which board options a board holds

A board option comes onto the page through the components that require it, and into the board only once someone sets its value.
Each component names the board options it requires in its own definition:

- A plugin class, in the `options` of its definition ([Plugins](Rewrite-1.1.12#a-plugin)), as core's basic frontend names `show_conditions`, the severities of the conditions that its cards show, and `dark_mode`, the theme it draws in.
- A renderer of outputs, in the `options` of its module, an array of ids beside `render()`, as core's table renderer names `n_rows`.
- A block class, in the `options` of its UI module, those that its requests read included.

The UI module is the one place where a block class names its board options.
A request's `options` in R says only which of them the request reads, so that R binds them to its function's arguments and the client sends their values with it ([Board option values in R](#board-option-values-in-r)).
The block registry entry carries each request's board options to the client by id.
Core refuses a module whose `options` leaves out a board option that a request of its class names, as it refuses one that declares another major of its JS API ([UI modules in JS](Rewrite-1.1.7#the-contract)).
It shows the error in the block's element, naming the module, the request and the board option, so that the gap shows on the first mount rather than as a request that reaches R without the value.

Core resolves the `default` of each board option that a component requires and the board holds no value for:

1. A plugin class's, as a board opens with one of its plugins, before core calls the plugin's `start` or mounts its UI module ([Running a plugin](Rewrite-1.1.12#running-a-plugin)).
   Core's basic frontend is such a plugin, so it gets `show_conditions` and `dark_mode` before it draws ([Plugins](Rewrite-1.1.12#the-frontend)).
2. A block class's, before core first calls its module's `render()` after the board opens.
3. A renderer's, before core first asks R for an output that the renderer draws, which the block registry entry makes possible ([The renderer before the first output](#the-renderer-before-the-first-output)).

So a board opened later gets them as a page that starts with that board would ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).
Core keeps each default it resolves beside the board for the opening, never in it, and every reader gets the board's value or else that default ([Reading a board option in the client](#reading-a-board-option-in-the-client)), as do the requests that carry the board option to R ([Board option values in R](#board-option-values-in-r)).
Where no loaded package defines a board option that a component requires, or its default fails or does not fit its schema, core reports the board option, naming it and what requires it, and runs the plugin or mounts the module without it.

A value that a script, a file or a command sets is the board's: a delta changes or removes it, a save writes it, and opening the saved board restores it ([Serialization](Rewrite-1.1.4#board-options)).
Removing it gives every reader the default, which core resolves then where it has not yet, and the value stays when the component that required it goes, since someone chose it.
So a saved board holds the values that someone chose and no default, and a default that a blockr option gives reaches every board that holds no value for the board option ([Where the two meet](#where-the-two-meet)).
A script gives a board option only to set a value other than its default, and nothing in R decides which board options a board has.

Undo never takes a value back, nor does redo set it again, since a board option never changes what the board computes, and most say only how it shows: a step's inverse holds no board option values, and a step that sets or removes only those is no undo step ([Board updates](Rewrite-1.1.2#undo)).

### The renderer before the first output

R makes an output only with the board options its coercion reads.
The coercion `as_table_output()`, for one, pages a data frame by `n_rows`, and has no fallback of its own.
The client, though, learns the renderer that requires them from the output itself ([Drawing the board](Rewrite-1.1.8#renderers)).
Without more, a fresh board's first table could never draw: R needs `n_rows` to make the output, and core resolves `n_rows` only once an output has named its renderer.
R therefore also names the renderer of a block class's outputs in the class's registry entry ([Block classes in R](Rewrite-1.1.5#registration)):

1. An output class gives its coercion through its method of `output_coercion()`, as `output_coercion.table_output()` returns `as_table_output`.
2. R finds the output class whose coercion the block class names in `output`.
3. R puts into the entry's `renderer` what that output class's method of `output_renderer()` gives, which takes the app's choice in the blockr option `renderers` into account.
4. The client loads that renderer and resolves the board options it names, and only then asks R for the block's first output.

An output of a subclass that has a renderer of its own still names that renderer, and core loads that one, resolves the board options it names and, where the output was asked without their values, asks R for it again with them.
An entry names no renderer where no output class gives the coercion that its block class names, and the first output request then carries the value of every board option that a loaded package defines, the board's or else its default, so that a coercion that wraps `as_table_output()` gets `n_rows` on a fresh board too.

### Board option values in R

In R a board option is its id and the value a script gives it, as `new_board_option(id, value)` makes it.
Its constructor, such as `new_n_rows_option(25)`, takes the value alone and computes nothing: no default from a blockr option, no transform and no check, since the board option's definition in the client holds all of that, and the store checks the value as it opens the board ([Defining a board option](#defining-a-board-option)).
A constructor called without a value, as registration calls it (below), makes a board option with none, which leaves the board without a value for it.
A board that `new_board()` makes holds no board options unless a script gives some, as `new_board(options = new_n_rows_option(25))` does, and R writes each such value under its id, with the version of its shape ([Serialization](Rewrite-1.1.4#board-options)).

R code reads a board option's value only where it names the board option:

- A block class's request names which of the class's board options it reads through `new_block_request(fun, options = )`, each one that the class's UI module names ([Which board options a board holds](#which-board-options-a-board-holds)).
  Given one constructor, its function takes that board option's value in its argument `options`.
  Given a list of constructors named by arguments, its function takes each value in the argument of that name.
  No argument is matched to a board option by its name, and a value comes whole, whatever its shape ([Block classes in R](Rewrite-1.1.5#requests)).
- An output class's coercion gets, in its `options`, the values of the board options that the renderer's module names, as `as_table_output(df, options = list(n_rows = 50L))` pages by `n_rows` ([Block classes in R](Rewrite-1.1.5#outputs)).
  A request of the output class, or of the renderer, gets in its `options` the values that its output was asked with, as the download in [Drawing the board](Rewrite-1.1.8#what-a-package-declares-in-r) does.
  A board option that the coercion reads is part of the class's contract, so every renderer of the class requires it.

Registration calls each constructor that a request names once, to read the board option's id for the registry entry, and drops the object.
The client sends a block class's request the values of the board options that the request names, and an output request those that the renderer names, each the board's value or else its default, by id, while a request of an output class or a renderer carries those its output was asked with ([Wire protocol](Rewrite-1.1.9#requests)).
It keeps the answer or the output by those values, so that a change to any other board option leaves it alone ([UI modules in JS](Rewrite-1.1.7#the-contract)).
A board option's own requests, which its package gives in R through its method of `board_option_requests()` for the board option's class, get only the args that its UI passes, as blockr.io's data directory board option has R list a directory that its UI names ([Drawing the board](Rewrite-1.1.8#what-a-package-declares-in-r)).
No board option reaches `expr` or `block_eval()`, so a change to one evaluates no block, and one that shapes outputs redraws them without evaluating ([Client-owned board state](Rewrite-1.1#proposal)).

### Reading a board option in the client

Every reader gets the board's value, or else the default that core resolved for the opening:

- A block class's UI module gets, in its context, the values of the board options it names, so that it shows what depends on them, as blockr.io's path field shows the data directory as its prefix ([UI modules in JS](Rewrite-1.1.7#the-contract)).
- A renderer gets, through its output host's `options()`, the values of the board options its module names, as the output it holds was asked with.
- A board option's UI gets an `OptionHost`, whose `value()` gives the board's value, or else the board option's default, which core resolves before it calls the module's `render()`, and whose `submit()` runs `blockr.core-set_option` ([UI modules in JS](Rewrite-1.1.7#the-contract)).
  A frontend mounts it with `mountOption()` where it shows the board options that `core.options.inUse()` lists, those that something on the page requires or that the board holds a value for, as core's basic frontend does in its toolbar and the dock in its options sidebar ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
  An app replaces it with a renderer that it names in the blockr option `renderers` ([Drawing the board](Rewrite-1.1.8#renderers)).
- A plugin reads the values of the board options that its class names through `core.options.value()`, and follows a change of the board's through `store.subscribe()` ([Board updates](Rewrite-1.1.2#following-the-board)).

### Locked boards

A locked board leaves its board options open, so that a reader may switch to dark mode or show more rows of a table on it, as on any other board.
The store applies a delta that sets or removes a board option's value on a locked board as on any other, and core resolves the defaults of those that something on the page requires there too ([Which board options a board holds](#which-board-options-a-board-holds)).
No lock fixes a board option, so R takes the values that a request carries on a locked board as on any other ([Locked boards and the properties of blocks](Rewrite-1.1.11#board-options-on-a-locked-board)).

### Blockr options

An app fixes its blockr options when it starts or is deployed, as today, and the mechanism carries over: `blockr_option()` reads each one from an R option or an environment variable.
The blockr options follow the code that reads them, since each part keeps, drops or adds blockr options as it translates its code rather than copying it ([State in JS](Rewrite-1#principles)).
R reads the blockr options that its own code needs where it needs them, as today.
The client can read neither an R option nor an environment variable of the server, so client code asks R for a blockr option by name, through `CoreApi.blockrOption(name, fallback)`, which passes the values in rather than having code read a global ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)):

1. Core asks R the first time code reads a blockr option, with a `blockr_options` request, and the names that code reads within one task go in one request ([Wire protocol](Rewrite-1.1.9#blockr-options)).
2. R replies with the value of each blockr option it has a value for, as `blockr_option()` reads it.
   It leaves out one that it cannot read, as where its R option and its environment variable disagree, which `blockr_option()` refuses, or whose value it cannot write as JSON, such as `renderers`, which holds renderer objects, and warns in its log, naming it, so that the code reading it takes its fallback while the request's other names get their values.
3. Core keeps each value until the page closes, since a blockr option is fixed for the app, and gives the code its fallback where R has no value.

A value that an environment variable sets arrives as a string, which core converts to the fallback's type, a number or a logical, since only the code that reads a blockr option knows its type.
R writes `Inf` as `null`, which core reads as `Infinity` where the fallback is a number.
Nothing declares a blockr option in R: the code that reads one names it and gives its fallback.
R answers for any blockr option, since a client can read whatever the R process can ([State in JS](Rewrite-1#proposal)).
Core asks for the blockr options that its synchronous code reads as soon as R has answered its `hello`: those its scheduler reads, so that they are there before the scheduler starts ([Evaluation in the client](Rewrite-1.1.10#scheduling)), and `rand_id`, the shape of the ids that its commands mint ([Board objects](Rewrite-1.1.1#ids)).

A constructor argument that configures rather than holds state is lost to the JSON, which keeps what the board holds and nothing else.
Such an argument becomes a blockr option where it is a value, and it moves to the code that calls it where it is a function.
The assistant's system prompt is a function of this kind: `new_assistant_extension()` takes it as `system_prompt` ([vignettes/intro.Rmd#L124-L153](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/vignettes/intro.Rmd#L124-L153)), and a board restored from a file loses it already ([R/ext-server.R#L1229-L1231](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/ext-server.R#L1229-L1231)).
It is R code only because ellmer runs the agent loop in R, and it becomes JS logic of the assistant's plugin once that loop runs in the browser ([Assistant as a client extension](Rewrite-1.4)).

### Where the two meet

A board option's definition may take its default from a blockr option, through `CoreApi.blockrOption()`, as core's `n_rows`, `show_conditions` and `dark_mode` each read the blockr option of their own id, with today's fallback but for `n_rows`, which falls back on 10 rather than 50, so that a card's table fits its output without scrolling ([blockr.core#501](https://github.com/BristolMyersSquibb/blockr.core/pull/501)).
So a deployment that sets `BLOCKR_N_ROWS=25` gives 25 rows per page to every board that holds no value for `n_rows`.
The default applies only where the board holds no value: a value that a script, a file or a command gives wins over it, so a board on which someone set 50 rows per page opens with 50 under any deployment, and one on which nobody set it takes the deployment's.
Where no blockr option sets `dark_mode`, its default is the theme that the user's system prefers, read from `prefers-color-scheme`, so that each reader's page follows their own system's theme until someone picks one, as with today's fallback of `NULL`.
A definition converts what it reads: R writes a blockr option of length one bare, as an environment variable gives it, so `show_conditions` takes a lone severity as an array of one, and `dark_mode` takes today's `TRUE` and `FALSE` as dark and light.
That is the only link between the values of the two kinds.
R computes no default for a board option, a blockr option never changes a value that the board holds, and nothing sets a blockr option from a board option.
The blockr option `renderers` also replaces a board option's UI (above), which changes how the value is drawn and never the value.

## Open questions

None.

<details><summary>Notes for implementers</summary>

The departures that this page takes in come from the bodies of [blockr.core#451](https://github.com/BristolMyersSquibb/blockr.core/pull/451) (requests name their board options through `new_block_request()`), [blockr.core#460](https://github.com/BristolMyersSquibb/blockr.core/pull/460) (a board option's R object holds its id and value, with a table of today's functions and what replaced each), [blockr.core#468](https://github.com/BristolMyersSquibb/blockr.core/pull/468) (a module names its board options in `options`), [blockr.core#474](https://github.com/BristolMyersSquibb/blockr.core/pull/474) (board classes require board options, as plugin classes do here), [blockr.core#480](https://github.com/BristolMyersSquibb/blockr.core/pull/480) (core's definitions and the output host's `options()`), [blockr.core#494](https://github.com/BristolMyersSquibb/blockr.core/pull/494) (the renderer in the registry entry, the caller of `onChange` and the reads of blockr options) and [blockr.core#501](https://github.com/BristolMyersSquibb/blockr.core/pull/501) (the fallback of `n_rows`).

On `js-state`, core adds the board options that a module names in `addOptions()` in `srcts/mount/block.ts`, but does not check them against those that the `requests` of the class's registry entry name.
This page has core refuse there a module that leaves one of them out, before it adds the module's board options.
The reads of blockr options are `createBlockrOptions()` in `srcts/core/blockr-options.ts`, and core's definitions are `nRows()`, `showConditions()`, `darkMode()` and `coreOptions()` in `srcts/options/`.
In R, `new_block_request()` is in `R/block-request.R` and `output_coercion()` in `R/output-class.R`.
On `js-state`, `mountOption()` in `srcts/mount/option.ts` also adds the board options that a board option's UI module names, which this page leaves out, since such a UI reads its own value alone ([blockr.core#508](https://github.com/BristolMyersSquibb/blockr.core/issues/508)).
On `js-state`, `addOptions()` writes each default into the board through `blockr.core-set_option`, for block and output mounts alike, where this page has core keep it beside the board for the opening, and an output mount that knows no renderer sends only the values that the board holds, in `values()` in `srcts/mount/output.ts` ([blockr.core#508](https://github.com/BristolMyersSquibb/blockr.core/issues/508)).
On `js-state`, `answer_blockr_options()` in `R/evaluator-answer.R` fails the whole request where it cannot send one of the blockr options, which this page has R leave out, and the client then takes the fallback of every name in the request ([blockr.core#510](https://github.com/BristolMyersSquibb/blockr.core/issues/510)).
On `js-state`, core's commands mint ids in the shape `adjective_animal`, through `mintId()` in `srcts/store/ids.ts`, and read no `rand_id` ([blockr.core#510](https://github.com/BristolMyersSquibb/blockr.core/issues/510)).
On `js-state`, the store drops a board option value that its schema refuses without naming it, in `srcts/store/open.ts`, where this page has it refuse the board and name every such value ([blockr.core#509](https://github.com/BristolMyersSquibb/blockr.core/issues/509)).
On `js-state`, a subscription in `srcts/core/core.ts` calls `onChange` only for the values that the board holds, as a board opens and as a delta sets one, where this page has core call it as each board opens for every board option that has one, with the board's value or else its default, and as a delta removes the value ([blockr.core#508](https://github.com/BristolMyersSquibb/blockr.core/issues/508)).
On `js-state`, `commit()` in `srcts/store/commit.ts` keeps a step's board option values in its inverse, which this page leaves out, as settled on [blockr#503](https://github.com/orgs/BristolMyersSquibb/discussions/503#discussioncomment-19358997).

On `js-state`, `CORE_BOARD` in `srcts/store/registrations.ts`, core's board class `board`, requires `show_conditions` and `dark_mode`, which core's basic frontend names instead once plugins replace board classes ([Plugins](Rewrite-1.1.12), [blockr.core#507](https://github.com/BristolMyersSquibb/blockr.core/issues/507)).

</details>
