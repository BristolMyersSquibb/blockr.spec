# Front-ends and extension points for the client-owned board
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): core's basic front-end, how a front-end such as blockr.dock replaces it, and what front-ends and their extensions hook into. It builds on the [board objects proposal](Rewrite-1.1.1) and on the [board updates](Rewrite-1.1.2), evaluation ([Evaluation in the client](Rewrite-1.1.10)) and UI modules ([UI modules in JS](Rewrite-1.1.7)) proposals, and shapes front-end registration and `CoreApi`, renderers, core's basic front-end and removing the generics that draw UI from R, each an item in the Work list of [Client-owned board state](Rewrite-1.1#work). The dock's contribution points, such as its panels, navbar items and sidebar sections, are [Client-drawn dock and extensions](Rewrite-1.2)'s.

## What must hold

1. Core ships a basic front-end that draws any board, so a board serves without blockr.dock, and a front-end replaces it entirely, so that none of it runs underneath another, as core's stack generics run underneath the dock today.
2. A front-end draws everything around a block, its card, panel, menus and status, while core mounts the block's UI and output, so a block class works in every front-end.
3. A front-end and its extensions work on the board only through core's JS API: the store, commands, demand, statuses and requests.
4. Nothing in R draws or redraws UI.
5. A front-end or any other package can replace the renderer that draws an output class or a board option, and an app picks among them through a blockr option, with no change to a block class.
6. A startup module can open another board in place of the opening board before anything is drawn or evaluated, as `rack_loader()` resolves the board a URL names before today's page is drawn.

## Today

Core's front-end is `board_ui.board()`: a toolbar of its plugins with a popover of board options, a bslib accordion of stacks and a bslib card per block, whose header and footer the `edit_block` plugin draws ([R/board-ui.R#L40-L140](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-ui.R#L40-L140)). It computes a block's status without drawing it, and shows conditions as notifications ([R/plugin-notification.R#L76-L140](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-notification.R#L76-L140)). It parks the blocks of collapsed stacks through `gate_stacks()`, the default `callbacks` of `board_server()`, so a stacked board is lazy under it ([R/board-server.R#L143-L158](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L143-L158)). A front-end replaces it by implementing generics that dispatch on the board, `board_ui()`, `block_ui()`, `insert_block_ui()`, `remove_block_ui()` and more, and by passing `callbacks` of its own: blockr.dock implements those four and `blockr_app_ui()` and `blockr_app_server()`, through which it passes its callbacks ([blockr.dock R/utils-serve.R#L64-L86](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serve.R#L64-L86)), but none of the stack generics, which still fire underneath it ([R/stack-ui.R#L37-L255](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/stack-ui.R#L37-L255)). The board's class also picks the page: `serve()` builds it with `blockr_app_ui()` for the board its loader returns at each request, and a restore stages the restored board and reloads the page, so a core board restored in a dock app brings core's UI along ([R/utils-serve.R#L227-L288](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L227-L288)). Extensions hook in through `new_dock_extension()` and `extension_block_callback()`, which the DAG uses to draw status badges ([R/ext-class.R#L52](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/ext-class.R#L52), [blockr.dag R/ext.R#L521-L583](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/ext.R#L521-L583)). Insertions and removals reach the page through R, and the dock's removal currently misses: the selector it passes to `removeUI()` is built from the board's id instead of the block's and lacks the `#`, so it matches no element, as [blockr.dock#527](https://github.com/BristolMyersSquibb/blockr.dock/issues/527) reports ([R/block-ui.R#L104](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/block-ui.R#L104)).

## Proposal

### Registering a front-end

A front-end is a module that a package declares in R under a name when it loads, as a block class names its UI module, so that its id is `{pkg}-{name}`, as a registry id is, and a package can ship several. The declaration also names the board options the front-end requires, which R gives a board it opens as JSON, since such a board has no class for `board_options()` to dispatch on ([Defining a board in R](Rewrite-1.1.3#options)):

```r
register_front_end("dock", js_module("dock.js"), options = dock_board_options)
```

The dock is then `blockr.dock-dock`, and core's basic front-end is `blockr.core-basic`. A board names the front-end it is made for by that id in its `front_end`, which the board's constructor sets, as `new_dock_board()` sets `blockr.dock-dock` ([Board objects](Rewrite-1.1.1#the-board)). The page loads the module of the front-end the app's board is made for, and that front-end draws every board opened later, whatever front-end it was made for, so the front-end never changes while the page lives ([Board updates](Rewrite-1.1.2#opening-a-board)): the store drops the state of packages the app does not load, and a front-end fills in its own state where a board lacks it, from its package's migration, as the dock gives a core board one default view, where today a restore reloads the page for the restored board's class (Today). Nothing in R converts a board, and R never needs a board's constructor to open one, nor builds a board to learn about a front-end.

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
  scheduler: Scheduler;            // demand(), evaluate(), invalidate(), status(), subscribe(), from Evaluation in the client
  blockRegistry: BlockRegistry;    // the block registry's entries by registry id, for pickers
  options: Options;                // register() and the board options packages define, by id
  blockrOptions: BlockrOptions;    // the blockr options the client reads, by package, from the reply to hello
  lock: Lock | null;               // the blocks a locked board leaves open, { open: ["f"] }, from the reply to hello
  request<T = Json>(pkg: string, name: string, args?: Json, reads?: BlockId[]): Promise<T | Blob>;   // a package's request, which evaluates the blocks it reads first
  module<T = unknown>(id: string): Promise<T>;                // a module another package offers, by id
  mountBlock(el: HTMLElement, block: BlockId): () => void;    // the block's UI module
  mountOutput(el: HTMLElement, block: BlockId): () => void;   // its output, measured, fetched and drawn by the renderer R names in it
  mountOption(el: HTMLElement, option: OptionId): () => void; // a board option's renderer
}
```

A front-end decides where things go and core fills them: it gives `mountBlock()` the body of a card or a panel, and core mounts the block's UI module there, so the dock's card sections stay the dock's business while what is in them stays core's. A front-end shows a block's UI and its output as core's attribute `visible` says, which its toggles set where the board is not locked, since a locked board leaves open only the blocks whose inputs show ([Board objects](Rewrite-1.1.1#blocks), [Wire protocol](Rewrite-1.1.9#locked-boards)). The `mountOutput()` call measures its element for the output's `info`, asks R for the output unless core kept one asked with the same revision, board options, size and `meta` ([UI modules in JS](Rewrite-1.1.7#the-contract)), draws it with the renderer R names in it (below), and redraws it when the block's revision, a board option, the size or the output's `meta` changes, while the block is `ready` ([Evaluation in the client](Rewrite-1.1.10#scheduling)). A front-end draws a block's status, conditions and summary from `scheduler.status()`, and decides from the status what an output that is not current looks like, leaving it as it is, greying it out or hiding it, since core keeps drawing a block's last output whatever the block's status ([Evaluation in the client](Rewrite-1.1.10#statuses)). It demands the blocks it shows, above the default evaluation priority ([Evaluation in the client](Rewrite-1.1.10#demand)), and follows the board through `store.subscribe()`, so a removed block's card goes away because the board changed, not because R said so. It draws no control for what the lock fixes ([Wire protocol](Rewrite-1.1.9#locked-boards)), and it and its extensions reach R through `request()`, as code export and session management do ([Wire protocol](Rewrite-1.1.9#requests)).

### Starting the page

Core starts the page in the order that [UI modules in JS](Rewrite-1.1.7#startup-modules) gives startup modules: once R replies to `hello`, core initializes the startup module of every package R has loaded, one at a time, then opens the board R sent, or the one a startup module names in its place (below), and only then starts the scheduler and calls the front-end's `render()`, so nothing is evaluated or drawn before every package has registered, while the scheduler sends nothing to R until `render()` has returned, so that what the front-end first shows is evaluated first ([Evaluation in the client](Rewrite-1.1.10#scheduling)). A front-end's package registers what the front-end adds, such as the dock's fields and commands, from its startup module, so the front-end's module only draws.

A startup module's `initialize()` may resolve with the text of a saved file, as session management's does with the board a URL names ([Session management as a client extension](Rewrite-1.6)), and core then opens that board instead of the one R sent, except on a locked board, which loads no other board, where core keeps the board R sent and names the package ([Wire protocol](Rewrite-1.1.9#locked-boards)), so nothing of the script's board is drawn or evaluated, while the page shows that it is loading, as today's page waits for `rack_loader()` ([Defining a board in R](Rewrite-1.1.3#the-opening-board)). Should two resolve with a board, core opens the one R sent and names both packages.

### Core's basic front-end

Core's own front-end does what today's does wherever core's commands and store do the work, so that it only draws: a toolbar for adding a block from the block registry's entries, editing links and stacks, setting the board's options and renaming the board, and downloading the board as a file and opening one, as today's `preserve_board` plugin does, since the client writes a saved board and opening one is `store.open()` ([Serialization](Rewrite-1.1.4#files)); stacks as groups; and a card per block with its name, a menu to rename or remove it or add a block before or after it, its UI, its output and its summary, as today's has, and its status and conditions, which today's computes but does not draw on the card, with the output greyed out while the block is not `ready`, where today's clears it ([R/block-server.R#L63-L66](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L63-L66)). It also binds undo and redo to their shortcuts, the one thing today's lacks, since the store keeps the steps and a front-end binds the shortcuts ([Board updates](Rewrite-1.1.2#undo)), and it tells the user what R dropped when a board opened and which edit the store refused ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)). Code export stays blockr.code's, to which [Client-drawn dock and extensions](Rewrite-1.2) gives today's `generate_code` plugin, and the basic front-end takes no extensions, since contribution points of its own would be a second extension API beside the dock's.

It shows every block, so it demands every block, and a board served without the dock evaluates every block ([Evaluation in the client](Rewrite-1.1.10#demand)), where today's parks the blocks of collapsed stacks. It is written in plain TypeScript, as core's built-in block UIs are, since core ships no React, and it mounts a block UI written in React as any front-end does, since the module brings its React from the one copy a package puts on the page ([UI modules in JS](Rewrite-1.1.7#react)). It follows blockr.ui's design system, as condition 6 of [State in JS](Rewrite-1#what-must-hold) asks of core's client, while where the design tokens live is an open question of [UI kit and design system for the client](Rewrite-1.7).

### Extensions

An extension is registered with the front-end it extends by its package's startup module ([UI modules in JS](Rewrite-1.1.7#startup-modules)), and works on the board through the same `CoreApi`, so the DAG adds a link by running a command and draws its status badges from `scheduler.status()`, with no per-block callback. What it contributes to the screen goes through the front-end's contribution points, which for the dock are [Client-drawn dock and extensions](Rewrite-1.2)'s. Its state lives in fields it registers with the store, which other extensions and the assistant change as they change core's objects, and which stay consistent through the `expand` each field registers ([Board updates](Rewrite-1.1.2#fields)). A file holds those fields within the board and the version of the extension's package in its `packages`, while R reads the state a file from today's stack keeps next to the extension's constructor into the same fields ([Serialization](Rewrite-1.1.4#files)).

### Renderers

A renderer is a module that draws the outputs of one output class ([Block classes in R](Rewrite-1.1.5#outputs)) or a board option's value. A package declares its renderers in R, as it declares a front-end, each for the one output class or board option it draws, with the board options it uses, as a block class names its own, and one module may stand behind several renderers: core declares a plain renderer for each output class it defines, blockr.ui declares its table preview for `table_output`, and a front-end may declare renderers of its own. A renderer of an output class brings the board options the class's coercion reads in R too, such as `n_rows` for table outputs, naming the constructors of the package that defines the class, as both of today's table displays bring `n_rows` ([R/tabular-display.R#L141-L175](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/tabular-display.R#L141-L175)), so that R collects them whichever renderer it picks. R picks one renderer for each output class and each board option, the first of the one a blockr option names for it, the front-end's and another package's, and otherwise the renderer of the package that defines the class, while a board option keeps the `ui` its definition gives ([Board objects](Rewrite-1.1.1#options)). For each output, R names in its JSON the renderer it picked for the most specific class in the output's class vector that has one, as S3 dispatch would, so that the outputs of a subclass that no package draws are drawn by their class's renderer, and the client mounts the renderer an output names, so neither class vectors nor dispatch reach it ([State in JS](Rewrite-1#principles)). Another package thus replaces a class's renderer through R's pick, extends the class with a subclass, or nests the class's outputs in its own ([Block classes in R](Rewrite-1.1.5#outputs)). Two renderers at one step are an error naming both, which the app settles with the blockr option. R sends the client the renderers it picked with the block registry's entries, and collects the board options they bring as it collects a block class's ([Defining a board in R](Rewrite-1.1.3#options)). So an app, a front-end or a UI kit changes how every table looks without touching a block class, as a JupyterLab extension replaces the renderer of a MIME type by registering its own ([registry.ts#L232-L258](https://github.com/jupyterlab/jupyterlab/blob/a877aee5ac6f490272a5ac18ac16b62b0deb1223/packages/rendermime/src/registry.ts#L232-L258)):

```r
# blockr.ui: a richer table for every block whose output is a table
register_renderer("table_preview", js_module("table-preview.js"),
                  class = "table_output", options = list(new_n_rows_option, new_page_size_option))

# an app that wants core's plain table anyway
options(blockr.renderers = c(table_output = "blockr.core-basic_table"))
```

A renderer gets an output host, or for a board option an option host ([UI modules in JS](Rewrite-1.1.7#the-contract)), through which it draws an output nested in its own, such as the table in blockr.dm's view of a dm, with the renderer R names in the nested output. A block's UI has no renderer, since it ships the schema of its block's state ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)), so a different UI makes a block class of its own, built from the fields of the block's ([Block classes in R](Rewrite-1.1.5#cores-classes-and-hooks)).

### What goes from R

The generics that draw or redraw UI from R go: `board_ui()`, `block_ui()`, `insert_block_ui()`, `remove_block_ui()`, `toolbar_ui()`, the stack UI generics, `blockr_app_ui()` and `blockr_app_server()`, and so do the `callbacks` through which a front-end hooks into `board_server()`, which goes with the board server ([Client-owned board state](Rewrite-1.1#today)). A front-end's R side shrinks to declaring its front-ends with their modules and the board options they require (above), its startup module ([UI modules in JS](Rewrite-1.1.7#startup-modules)), any renderers of its own (above), the constructors that app scripts call, such as the dock's `new_dock_board()` and `new_dock_stack()`, whose state R writes as the front-end's fields ([Board objects](Rewrite-1.1.1#extending-cores-objects)), and the blockr options its client reads ([Defining a board in R](Rewrite-1.1.3#blockr-options)).

## Open questions

None.
