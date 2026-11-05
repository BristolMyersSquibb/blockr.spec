# Front-ends and extension points for the client-owned board
Status: settled on 2026-10-30. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): core's basic front-end, how a front-end such as blockr.dock replaces it, and what front-ends and their extensions hook into.
It builds on the [board objects proposal](Rewrite-1.1.1) and on the [board updates](Rewrite-1.1.2), evaluation ([Evaluation in the client](Rewrite-1.1.10)) and UI modules ([UI modules in JS](Rewrite-1.1.7)) proposals, and shapes removing the generics that draw UI from R ([blockr.core#418](https://github.com/BristolMyersSquibb/blockr.core/issues/418)), the toolchain of core's client ([blockr.core#419](https://github.com/BristolMyersSquibb/blockr.core/issues/419)), front-end registration with what else a package declares in R ([blockr.core#424](https://github.com/BristolMyersSquibb/blockr.core/issues/424)), board classes and their front-ends ([blockr.core#465](https://github.com/BristolMyersSquibb/blockr.core/issues/465)), renderers ([blockr.core#425](https://github.com/BristolMyersSquibb/blockr.core/issues/425)), the requests of the per-session evaluator ([blockr.core#430](https://github.com/BristolMyersSquibb/blockr.core/issues/430)), the UIs of core's built-in blocks ([blockr.core#438](https://github.com/BristolMyersSquibb/blockr.core/issues/438)), core's renderers and board options ([blockr.core#439](https://github.com/BristolMyersSquibb/blockr.core/issues/439)), `CoreApi` and starting the page ([blockr.core#440](https://github.com/BristolMyersSquibb/blockr.core/issues/440)), core's basic front-end ([blockr.core#441](https://github.com/BristolMyersSquibb/blockr.core/issues/441)), serving a board ([blockr.core#442](https://github.com/BristolMyersSquibb/blockr.core/issues/442)) and what core exports for end-to-end tests ([blockr.core#443](https://github.com/BristolMyersSquibb/blockr.core/issues/443)), each an item in the Work list of [Client-owned board state](Rewrite-1.1#work).
The dock's contribution points, such as its panels, navbar items and sidebar sections, are [Client-drawn dock and extensions](Rewrite-1.2)'s.

## What must hold

1. Core ships a basic front-end that draws any board, so a board serves without blockr.dock, and a front-end replaces it entirely, so that none of it runs underneath another, as core's stack generics run underneath the dock today.
2. A front-end draws everything around a block, its card, panel, menus and status, while core mounts the block's UI and output, so a block class works in every front-end.
3. A front-end and its extensions work on the board only through core's JS API: the store, commands, demand, statuses and requests.
4. Nothing in R draws or redraws UI.
5. Any package can supply a renderer for an output class or a board option.
   An app replaces an output class's default renderer, or a board option's UI, with such a renderer through a blockr option, with no change to a block class.
6. A startup module can open another board in place of the opening board before anything is drawn or evaluated, as `rack_loader()` resolves the board a URL names before today's page is drawn.
7. Opening a board leaves the page as serving that board in a fresh app would, its front-end included, as a restore does today, but with no reload ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).

## Today

Core's front-end is `board_ui.board()`: a toolbar of its plugins with a popover of board options, a bslib accordion of stacks and a bslib card per block, whose header and footer the `edit_block` plugin draws ([R/board-ui.R#L40-L140](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-ui.R#L40-L140)).
It computes a block's status without drawing it, and shows conditions as notifications ([R/plugin-notification.R#L76-L140](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-notification.R#L76-L140)).
It parks the blocks of collapsed stacks through `gate_stacks()`, the default `callbacks` of `board_server()`, so a stacked board is lazy under it ([R/board-server.R#L143-L158](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L143-L158)).
A front-end replaces it by implementing generics that dispatch on the board, `board_ui()`, `block_ui()`, `insert_block_ui()`, `remove_block_ui()` and more, and by passing `callbacks` of its own: blockr.dock implements those four and `blockr_app_ui()` and `blockr_app_server()`, through which it passes its callbacks ([blockr.dock R/utils-serve.R#L64-L86](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serve.R#L64-L86)), but none of the stack generics, which still fire underneath it ([R/stack-ui.R#L37-L255](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/stack-ui.R#L37-L255)).
The board's class also picks the page: `serve()` builds it with `blockr_app_ui()` for the board its loader returns at each request, and a restore stages the restored board and reloads the page, so a core board restored in a dock app brings core's UI along ([R/utils-serve.R#L227-L288](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L227-L288)).
Extensions hook in through `new_dock_extension()` and `extension_block_callback()`, which the DAG uses to draw status badges ([R/ext-class.R#L52](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/ext-class.R#L52), [blockr.dag R/ext.R#L521-L583](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/ext.R#L521-L583)).
Insertions and removals reach the page through R, and the dock's removal currently misses: the selector it passes to `removeUI()` is built from the board's id instead of the block's and lacks the `#`, so it matches no element, as [blockr.dock#527](https://github.com/BristolMyersSquibb/blockr.dock/issues/527) reports ([R/block-ui.R#L104](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/block-ui.R#L104)).

## Proposal

### Registering a front-end

A front-end is the UI module of a board class, the module that draws the boards that the client builds as that class, as a block class has a UI module.
A package offers it in R as it offers any module to others, under a name when it loads, so that R serves it and its id is `{pkg}-{name}`, as a registry id is ([UI modules in JS](Rewrite-1.1.7#packaging)), and a package can ship several.
The board class names the front-end that draws its boards in R, through its method of the generic `board_front_end()`, which returns the module's id whatever the board holds, and the version of the properties it adds through its method of `board_version()`, 1 where it has none ([Serialization](Rewrite-1.1.4#migrations)):

```r
register_module("dock", js_module("dock.js"))                    # in .onLoad()

board_front_end.dock_board <- function(x, ...) "blockr.dock-dock"   # exported as S3 methods
board_version.dock_board <- function(x, ...) 2L                     # where its properties changed shape once
```

The dock is then `blockr.dock-dock`, which blockr.dock's method for `dock_board` names, and core's basic front-end is `blockr.core-basic`, which core's method for `board` names.
The namespace that holds a class's method is the one of the package that defines the class, so R learns a class's package from its method, which a class name does not give, as the JSON board that R writes records it ([Serialization](Rewrite-1.1.4#files)), with no registry of board classes of its own, since S3 registers the methods.
R sends each board class that a loaded package names a front-end for, with its package, its front-end and its version, in the reply to `hello`, calling each method on an empty board of its class, while the class's definition in JS gives its parent, the board options it requires ([Board objects](Rewrite-1.1.1#board-options)), its properties and its functions ([Board updates](Rewrite-1.1.2#board-classes-and-attributes)).
A board names no front-end: the client builds the board as the first class in its `class` that a loaded package defines, and the front-end that R names for that class, or for its nearest parent that R names one for, draws it, which the store's `frontEnd()` gives ([Board objects](Rewrite-1.1.1#the-board)).
So a board of a class extending `dock_board` that no package defines is drawn by the dock, as is one of a class that a package defines in JS alone, with no method in R, which comes from no package, and every board by core's basic front-end at least, as S3 dispatch gives a board in R its parent's front-end.
R picks no board's front-end, whether an app script built the board or the client opens it from a file, but names each class's.

R tells the client where each front-end is served, by its id, among the modules that packages offer ([UI modules in JS](Rewrite-1.1.7#packaging)), and every board is drawn by the front-end that R names for the class it is built as: core imports the module of the first board's front-end once every startup module has initialized, and switches the page in place to the front-end of a board opened later (below).
Where a board lacks a property of its class, the property takes its default ([Board updates](Rewrite-1.1.2#board-classes-and-attributes)), and the store drops the properties of a class that no loaded package defines ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)).
Nothing in R converts a board, and R never needs a board's constructor to open one, nor builds a board to learn about a front-end.

The module meets the contract a block's UI module meets ([UI modules in JS](Rewrite-1.1.7#the-contract)), with `CoreApi` in place of a host: it exports the JS API major it was built against and a default whose `render()` core calls, so it never names its own id.

```ts
export const api = 1;                                // the JS API major it was built against

export default {
  render({ el, core, signal }: { el: HTMLElement; core: CoreApi; signal: AbortSignal }): () => void { /* draw the board, return the cleanup */ }
};
```

### What core gives a front-end

```ts
interface CoreApi {
  store: Store;                    // board(), subscribe(), apply(), open(), register(), from Board updates
  commands: Commands;              // run(), plan() and the command registry, for menus and shortcuts
  scheduler: Scheduler;            // demand(), evaluate(), invalidate(), status() and subscribe() alone, from Evaluation in the client
  blockRegistry: BlockRegistry;    // the block registry's entries by registry id, for pickers
  options: Options;                // register() and the board options packages define, by id
  lock: Lock | null;               // the blocks a locked board leaves open, { open: ["f"] }, from the reply to hello
  outputEvents: OutputEvents;      // what renderers report the user did, such as a selection, for extensions to act on
  request<T = Json>(extension: string, name: string, args?: Json, opts?: RequestOpts): Promise<T | Blob>;   // an extension's request, by the extension's id
  module<T = unknown>(id: string): Promise<T>;                // a module another package offers, by id
  blockrOption<T extends Json>(name: string, fallback: T): Promise<T>;   // a blockr option, asked of R once per page, or fallback where R has none
  mountBlock(el: HTMLElement, block: BlockId): () => void;    // the block's UI module
  mountOutput(el: HTMLElement, block: BlockId): () => void;   // its output, measured, fetched and drawn by the renderer R names in it
  mountOption(el: HTMLElement, option: OptionId): () => void; // a board option's UI, or the renderer R picked for it
}

interface RequestOpts {
  reads?: BlockId[];                                         // the blocks it reads, which core has evaluated first
  signal?: AbortSignal;                                      // cancels it, as a cancel does on the wire
  progress?(note: { value?: number; message?: string }): void;   // each progress note R sends for it
}

interface OutputEvents {
  subscribe(fn: (event: { block: BlockId; name: string; payload: Json }) => void): () => void;   // each event a renderer emits ([UI modules in JS](Rewrite-1.1.7#the-contract))
}
```

A front-end decides where things go and core fills them: it gives `mountBlock()` the body of a card or a panel, and core mounts the block's UI module there, so the dock's card sections stay the dock's business while what is in them stays core's.
A front-end may mount a block's UI or output in several places at once, such as two panels of one view, and mount it again as its panels move or reopen, since everything a mount draws from is core's and none of it is lost when a mount ends ([UI modules in JS](Rewrite-1.1.7#the-contract)), rather than moving one element around, as the dock parks each card in its offcanvas today and carries it into a panel and back ([blockr.dock R/block-ui.R#L188-L295](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/block-ui.R#L188-L295)).
Two mounts of one output share its parameters, which core keeps per block, so both show the same page and sort.
A front-end shows a block's UI and its output as core's attribute `visible` says, which its toggles set where the board is not locked, since a locked board leaves open only the blocks whose inputs show ([Board objects](Rewrite-1.1.1#blocks), [Wire protocol](Rewrite-1.1.9#locked-boards)).
The `mountOutput()` call measures its element for the output's `info`, asks R for the output unless core kept one asked with the same revision, board options, `info` and parameters ([UI modules in JS](Rewrite-1.1.7#the-contract)), draws it with the renderer R names in it (below), and redraws it when the block's revision, a board option, the `info` or the output's parameters change, while the block is `ready` ([Evaluation in the client](Rewrite-1.1.10#scheduling)).
A front-end draws a block's status, conditions and summary from `scheduler.status()`, and decides from the status what an output that is not current looks like, leaving it as it is, greying it out or hiding it, since core keeps drawing a block's last output whatever the block's status ([Evaluation in the client](Rewrite-1.1.10#statuses)).
It demands the blocks it shows, above the default evaluation priority ([Evaluation in the client](Rewrite-1.1.10#demand)), and follows the board through `store.subscribe()`, so a removed block's card goes away because the board changed, not because R said so.
It draws no control for what the lock fixes ([Wire protocol](Rewrite-1.1.9#locked-boards)), and its extensions reach R through `request()`, each through requests of its own, as code export and session management do ([Wire protocol](Rewrite-1.1.9#requests)).

### Starting the page

Core starts the page in the order that [UI modules in JS](Rewrite-1.1.7#startup-modules) gives startup modules: once R replies to `hello`, core initializes the startup module of every package R has loaded, one at a time, then opens the board R sent, or the one a startup module names in its place (below), then imports the module of the front-end that R names for the class the board is built as, since a module's imports run as it loads and may need what a startup module puts on the page, such as a library on another package's global ([UI modules in JS](Rewrite-1.1.7#startup-modules)), and only then starts the scheduler and calls the front-end's `render()`, so nothing is evaluated or drawn before every package has registered.
The scheduler sends nothing to R until `render()` has returned, or resolved where it is async, so a front-end demands what it first shows within `render()`, from the board, rather than from an effect that runs once it has drawn, as a React app's would, and those blocks are evaluated first ([Evaluation in the client](Rewrite-1.1.10#scheduling)).
A front-end's package defines its board class, with the properties the class adds, and registers its commands, from its startup module, and subscribes to the store there too, so that it sees the first board open, with what R dropped, which happens before `render()` ([Board updates](Rewrite-1.1.2#following-the-board)), while the front-end's module only draws.

A startup module's `initialize()` may resolve with the text of a JSON board, as session management's does with the board a URL names ([Session management as a client extension](Rewrite-1.6)), and core then opens that board instead of the one R sent, except on a locked board, which loads no other board, where core keeps the board R sent and names the package ([Wire protocol](Rewrite-1.1.9#locked-boards)), so nothing of the script's board is drawn or evaluated, while the page shows that it is loading, as today's page waits for `rack_loader()` ([Defining a board in R](Rewrite-1.1.3#the-opening-board)).
Should two resolve with a board, core opens the one R sent and names both packages.

### Switching front-ends

Opening a board switches the page to the front-end of the class the board is built as, with no reload.
Where that front-end is the page's already, core starts it again all the same, so that nothing it kept of the board before outlives the opening ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).
As the store opens a board, core imports the module of the front-end that `frontEnd()` gives for the board's class ([Board updates](Rewrite-1.1.2#the-store)), aborts the signal of the one on the page, which unmounts what it mounted and releases its demands, opens the board in the store, and calls the front-end's `render()`, holding the scheduler until it has returned, as at startup, so that what it first shows is evaluated first.
Nothing else is lost, since opening a board starts a new undo history and has R forget every block of the board it replaces, whatever draws it ([Board updates](Rewrite-1.1.2#opening-a-board), [Wire protocol](Rewrite-1.1.9#forgetting-blocks)), and a front-end releases what it holds when its signal aborts, as any module does when core unmounts it ([UI modules in JS](Rewrite-1.1.7#the-contract)).
So the page draws an opened board as a fresh app serving it would, as today's restore rebuilds the page for the restored board's class (Today) but without the reload: a core board opened in a dock app is drawn by core's basic front-end, a dock board opened in a core app by the dock, and a dock board opened in a dock app by a dock that starts again.

### Core's basic front-end

Core's own front-end does what today's does wherever core's commands and store do the work, so that it only draws: a toolbar for adding a block from the block registry's entries, editing links and stacks, setting the board options that the board holds and renaming the board, and downloading the board as a file and opening one, as today's `preserve_board` plugin does, since the client writes a saved board and opening one is `store.open()` ([Serialization](Rewrite-1.1.4#files)); stacks as groups; and a card per block with its name, a menu to rename or remove it or add a block before or after it, its UI, its output and its summary, as today's has, and its status and conditions, which today's computes but does not draw on the card, showing the severities that core's `show_conditions` board option names, with the output greyed out while the block is not `ready`, where today's clears it ([R/block-server.R#L63-L66](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L63-L66)).
It also binds undo and redo to their shortcuts, the one thing today's lacks, since the store keeps the steps and a front-end binds the shortcuts ([Board updates](Rewrite-1.1.2#undo)), and it tells the user what R dropped when a board opened and which edit the store refused ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)).
Code export stays blockr.code's, to which [Client-drawn dock and extensions](Rewrite-1.2) gives today's `generate_code` plugin, and the basic front-end takes no extensions, since contribution points of its own would be a second extension API beside the dock's.

It shows every block, so it demands every block, and a board served without the dock evaluates every block ([Evaluation in the client](Rewrite-1.1.10#demand)), where today's parks the blocks of collapsed stacks.
It is written in React, as TSX, as core's built-in block UIs and renderers are, on the one copy of React that core ships, and it mounts a block's UI as any front-end does, whatever the module is written in ([UI modules in JS](Rewrite-1.1.7#react)).
It builds on Tailwind CSS rather than on blockr.ui's design system, which the dock follows, since blockr.ui builds on blockr.core ([State in JS](Rewrite-1#what-must-hold)), and so do the UIs of core's built-in blocks and its renderers, which show under every front-end.
Their stylesheets keep Tailwind's utilities under core's prefix and leave out its reset of the whole page, so that nothing core loads styles another package's elements, the dock's included once the page has switched to it ([UI modules in JS](Rewrite-1.1.7#startup-modules)), and they take their colours, fonts and radii from the variables in which Tailwind CSS 4 keeps its theme, which a front-end or a UI kit may set to restyle them, as blockr.ui may under the dock ([UI kit and design system for the client](Rewrite-1.7)).

### Extensions

An extension is registered with the front-end it extends by its package's startup module ([UI modules in JS](Rewrite-1.1.7#startup-modules)), under an id, `{pkg}-{name}`, by which its package registers its requests in R (below) and `request()` names them ([Wire protocol](Rewrite-1.1.9#requests)), while how an extension registers with the dock is [Client-drawn dock and extensions](Rewrite-1.2)'s, since only the dock takes extensions.
It works on the board through the same `CoreApi`, so the DAG adds a link by running a command and draws its status badges from `scheduler.status()`, with no per-block callback.
What it contributes to the screen goes through the front-end's contribution points, which for the dock are [Client-drawn dock and extensions](Rewrite-1.2)'s.
Its state lives in a property of the board class whose front-end it extends, as a dock board holds it in its `extensions` by the extension's id, and other extensions and the assistant change it through the commands the extension registers ([Board updates](Rewrite-1.1.2#board-classes-and-attributes)).
How the dock lets an extension keep its state consistent with the rest of the board, as the DAG drops a removed block's position, is the dock's to offer ([Client-drawn dock and extensions](Rewrite-1.2)).
A file holds that state within the board and the version of the extension's package in its `packages`, while R reads the state a file from today's stack keeps next to the extension's constructor into the same place ([Serialization](Rewrite-1.1.4#files)).

### Renderers

A renderer is a module that draws the outputs of one output class ([Block classes in R](Rewrite-1.1.5#outputs)) or a board option's value.
A renderer of an output class is written against the class's contract, which the package that defines the class ships: a JSON Schema of its outputs, by which R writes them, with their TypeScript type, such as core's `TableOutput` for table outputs; the types of the parameters its coercion reads, such as `TableParams`, of the events its renderers emit, if they emit any, such as a chart's selection, and of the args and answers of its requests, if it has any, such as a download; and fixtures of sample outputs it is tested on, so that whoever builds another table knows what to draw and what to ask for.
Each output class has a default renderer, which the package that defines the class registers in R with the class, beside its JSON Schema and its requests (below), under the id `{pkg}-{class}`, as core registers `blockr.core-table_output` with its table outputs, and a board option has the `ui` its definition gives ([Board objects](Rewrite-1.1.1#board-options)).
Any package may declare other renderers in R, each for the one output class or board option it draws, which `class` or `option` names, under the id `{pkg}-{name}` that its package's name and the name it declares it under give, as blockr.ui declares its table preview, `blockr.ui-table_preview`, for table outputs, and one module may stand behind several renderers.
An app replaces a default or a board option's `ui` only by naming another renderer for it in the `renderers` blockr option, by the renderer's id, so that a renderer declared this way draws nothing until an app names it, and loading its package changes nothing.
R picks the renderer of each output class and each board option this way, whatever the board and its front-end.
For each output, R names in its JSON the renderer it picked for the most specific class in the output's class vector that has one, as S3 dispatch would, so that the outputs of a subclass registered without a renderer are drawn by their class's renderer, and the client mounts the renderer an output names, so neither class vectors nor dispatch reach it ([State in JS](Rewrite-1#principles)).
Another package thus supplies a renderer that an app names, extends the class with a subclass, or nests the class's outputs in its own ([Block classes in R](Rewrite-1.1.5#outputs)).
R sends the client the renderers it picked with the block registry's entries.
So an app changes how every table looks, with a UI kit's renderer or another's, without touching a block class, as a JupyterLab extension replaces the renderer of a MIME type by registering its own ([registry.ts#L232-L258](https://github.com/jupyterlab/jupyterlab/blob/a877aee5ac6f490272a5ac18ac16b62b0deb1223/packages/rendermime/src/registry.ts#L232-L258)):

```r
# blockr.core: its table outputs, with its plain table as their default, blockr.core-table_output
register_output_class("table_output", schema = "table-output.schema.json", renderer = js_module("basic-table.js"))

# blockr.ui: a richer table, blockr.ui-table_preview, with a request of its own for the columns' labels
register_renderer("table_preview", js_module("table-preview.js"), class = "table_output",
                  requests = list(labels = function(result) lapply(result, attr, "label", exact = TRUE)))

# an app that wants blockr.ui's table: an output class, and the id of its renderer
options(blockr.renderers = c(table_output = "blockr.ui-table_preview"))
```

A renderer gets an output host, or for a board option an `OptionHost` ([UI modules in JS](Rewrite-1.1.7#the-contract)), through which it calls the requests of its output class, such as a download of what it shows, and its own, such as the labels of a table's columns, and draws an output nested in its own, such as the table in blockr.dm's view of a dm, with the renderer R names in the nested output.
A block's UI has no renderer, since it ships the schema of its block's state ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)), so a different UI makes a block class of its own, built from the fields of the block's ([Block classes in R](Rewrite-1.1.5#cores-classes-and-hooks)).
A renderer's module names the board options it requires, as core's table renderer requires `n_rows` ([Board objects](Rewrite-1.1.1#board-options)).

### What a package declares in R

Besides its block classes, which `register_block()` registers ([Block classes in R](Rewrite-1.1.5#registration)), and its renderers (above), a package declares in R, from its `.onLoad()`, the rest of its client that R serves or answers for, each under a name that gives it the id `{pkg}-{name}`, as a registry id is.
With illustrative names:

```r
register_startup_module(js_module("startup.js"))                  # a package's one startup module
register_module("filter", js_module("filter.js"))                 # in blockr.dplyr, a module it offers others, blockr.dplyr-filter
register_module("dock", js_module("dock.js"))                     # in blockr.dock, its front-end, blockr.dock-dock,
board_front_end.dock_board <- function(x, ...) "blockr.dock-dock"  # which its board class names, as an exported S3 method
register_output_class("chart_output", schema = "chart-output.schema.json",    # in blockr.viz, with its renderer and a download
                      renderer = js_module("chart.js"),
                      requests = list(download = function(result, options, params, format, file) chart_pptx(result, file)))
register_requests(list(list_dir = function(path = "") list_dir(path)), option = "data_dir")   # in blockr.io, for its data directory
register_requests(list(script = function(reads) export_code(reads)),
                  extension = "code", allow_locked = "script")    # in blockr.code, for blockr.code-code
```

A package has at most one startup module ([UI modules in JS](Rewrite-1.1.7#startup-modules)), and a module it offers others, a front-end among them, is reached by its id through `host.module()` and `CoreApi.module()`.
A board class's front-end and version are S3 methods, of `board_front_end()` and `board_version()`, rather than declarations, so that R learns the class's package from the namespace that holds them (above).
An output class registers the JSON Schema of its outputs, by which R writes them, its default renderer, `blockr.viz-chart_output` here, and its requests, which R runs with the result the output was made from and resolves by the most specific class in the output's class vector that has them ([Block classes in R](Rewrite-1.1.5#outputs)).
A board option's requests are registered under its id and an extension's under the extension's name, which with its package's gives the id that `request()` names, each with `allow_locked` naming those that may run on a locked board ([Wire protocol](Rewrite-1.1.9#locked-boards)): R calls a board option's request with its args by name, and an extension's with its args by name and, in `reads`, the blocks it reads by id, each a list of its `result` and the block expression `expr` R built for it.
A package declares none of the blockr options its client reads, which the client asks R for by name ([Defining a board in R](Rewrite-1.1.3#blockr-options)).
A module's stylesheet and JSON Schema need no declaration, since they sit beside it ([UI modules in JS](Rewrite-1.1.7#packaging)).

### What goes from R

The generics that draw or redraw UI from R go: `board_ui()`, `block_ui()`, `insert_block_ui()`, `remove_block_ui()`, `toolbar_ui()`, the stack UI generics, `blockr_app_ui()` and `blockr_app_server()`, and so do the `callbacks` through which a front-end hooks into `board_server()`, which goes with the board server ([Client-owned board state](Rewrite-1.1#today)).
A front-end's R side shrinks to declaring its front-ends with their modules, its board classes' methods of `board_front_end()` and `board_version()`, its startup module and any renderers of its own (above), and the constructors that app scripts call, such as the dock's `new_dock_board()` and `new_dock_stack()`, whose components R writes as the dock board's properties ([Board objects](Rewrite-1.1.1#extending-cores-objects)).

### Testing

Core ships, beside the stubs of its hosts ([UI modules in JS](Rewrite-1.1.7#testing)), a `CoreApi` for tests whose store, commands and scheduler are core's own and whose replies from R come from fixtures, those the wire protocol's tests round-trip ([Wire protocol](Rewrite-1.1.9)), so that a front-end, an extension or a startup module runs in a test runner on a board, needing neither R nor a browser.

End-to-end tests run an app with R and a browser, through shinytest2 to start with, and core exports what they check.
R exports each block's latest result through `exportTestValues()`, as `blockr_test_exports()` does today ([R/utils-serve.R#L310-L331](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L310-L331)), which Shiny does only in the test mode shinytest2 starts an app in, and the client exposes the board and each block's status, read only, for `AppDriver$get_js()` to read, since they now live in the client.

## Open questions

None.
