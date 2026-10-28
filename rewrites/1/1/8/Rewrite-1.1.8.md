# Front-ends and extension points for the client-owned board
Status: draft. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): core's basic front-end, how a front-end such as blockr.dock replaces it, and what front-ends and their extensions hook into. It builds on the [board objects proposal](Rewrite-1.1.1) and on the [board updates](Rewrite-1.1.2), evaluation ([Evaluation in the client](Rewrite-1.1.10)) and UI modules ([UI modules in JS](Rewrite-1.1.7)) proposals. The dock's own contribution API, its panels, navbar items and sidebar sections, is [Client-drawn dock and extensions](Rewrite-1.2)'s.

## What must hold

1. Core ships a basic front-end that draws any board, so a board serves without blockr.dock, and a front-end replaces it entirely, as the dock replaces core's UI today.
2. A front-end draws everything around a block, its card, panel, menus and status, while the block's UI and output come from core, so a block type works in every front-end.
3. A front-end and its extensions work on the board only through core's client API: the store, commands, demand, statuses and requests.
4. Nothing in R draws or redraws UI.
5. A front-end or any other package can replace the renderer that draws a kind of output or a board option, and an app picks among them through a blockr option, with no change to a block type.

## Today

Core's front-end is `board_ui.board()`: a toolbar of its plugins with a popover of board options, a bslib accordion of stacks and a bslib card per block, whose header and footer the edit_block plugin draws ([R/board-ui.R#L40-L140](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-ui.R#L40-L140)). It computes a block's status without drawing it, and shows conditions as notifications ([R/plugin-notification.R#L76-L140](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-notification.R#L76-L140)). A front-end replaces it by implementing generics that dispatch on the board, `board_ui()`, `block_ui()`, `insert_block_ui()`, `remove_block_ui()` and more, and blockr.dock implements most of them, while core's stack generics still fire underneath it ([R/stack-ui.R#L37-L255](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/stack-ui.R#L37-L255)). Extensions hook in through `new_dock_extension()` and `extension_block_callback()`, which the DAG uses to draw status badges ([R/ext-class.R#L52](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/ext-class.R#L52), [blockr.dag R/ext.R#L521-L583](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/ext.R#L521-L583)). Insertions and removals reach the page through R, and the dock's removal currently misses: the selector it passes to `removeUI()` is built from the board's id instead of the block's and lacks the `#`, so it matches no element, as [blockr.dock#527](https://github.com/BristolMyersSquibb/blockr.dock/issues/527) reports ([R/block-ui.R#L104](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/block-ui.R#L104)).

## Proposal

### Registering a front-end

A front-end is a module that a package declares in R under a name, as a block type names its UI module, so that its id is `{pkg}-{name}`, as a registry id is, and a package can ship several: the dock declares `register_front_end("dock", js_module("dock.js"), lazy = TRUE)` and is `blockr.dock-dock`, lazy since it demands only the blocks it shows ([Evaluation in the client](Rewrite-1.1.10#demand)), and core's basic front-end is `blockr.core-basic`. A board names the front-end it is made for by that id in its `front_end`, which the board's constructor sets, as `new_dock_board()` sets `blockr.dock-dock` ([Board objects](Rewrite-1.1.1#the-board)). The page loads the module of the front-end the app's board is made for, and a board made for another is converted or drawn by it when it is opened ([Board updates](Rewrite-1.1.2#opening-a-board)), so the front-end never changes while the page lives.

The module meets the contract a block's UI module meets ([UI modules in JS](Rewrite-1.1.7#the-contract)): it exports the JS API major it was built against and a default whose `mount()` core calls, so it never names its own id.

```ts
export const api = 1;                                // the JS API major it was built against

export default {
  mount({ el, api }: { el: HTMLElement; api: CoreApi }): () => void { /* draw the board, return the cleanup */ }
};
```

### What core gives a front-end

```ts
interface CoreApi {
  store: Store;                    // board(), subscribe(), apply(), open(), register(), from Board updates
  commands: Commands;              // run(), plan() and the command registry, for menus and shortcuts
  scheduler: Scheduler;            // demand(), evaluate(), invalidate(), status(), from Evaluation in the client
  blockRegistry: BlockRegistry;    // block types by registry id, for pickers
  options: Record<OptionId, Option>; // the board options packages define, by id
  blockrOptions: BlockrOptions;    // the blockr options the client reads, by package, from the reply to hello
  mountBlock(el: HTMLElement, block: BlockId): () => void;    // the block's UI module
  mountOutput(el: HTMLElement, block: BlockId): () => void;   // its output, measured, fetched and drawn by its kind's renderer
  mountOption(el: HTMLElement, option: OptionId): () => void; // a board option's renderer
}
```

A front-end decides where things go and core fills them: it gives `mountBlock()` the body of a card or a panel, and core mounts the block's UI module there, so the dock's card sections stay the dock's business while what is in them stays core's. The `mountOutput()` call measures its element for the output's `info`, asks R for the output, draws it with the renderer R picked for its kind (below), and redraws it when the block's version, an option or the size changes. A front-end draws a block's status, conditions and summary from `scheduler.status()`, demands what it shows if it is lazy, and follows the board through `store.subscribe()`, so a removed block's card goes away because the board changed, not because R said so.

### Core's basic front-end

Core's own front-end draws what today's does: a toolbar with adding a block and the board's options, stacks as groups, and a card per block with its name, a menu to rename or remove it, its UI and its output. It also draws each block's status and conditions on its card, which today's computes but does not show. It is not lazy, since it shows every block, so core demands every block under it, and a board served without the dock evaluates every block, as today ([Evaluation in the client](Rewrite-1.1.10#demand)). It is written in plain TypeScript, as core's built-in block UIs are, since core ships no React, and it mounts a block UI written in React as the dock does, with the React that blockr.ui ships ([UI modules in JS](Rewrite-1.1.7#the-react-sdk)).

### Extensions

An extension is a module too, registered with the front-end it extends, and works on the board through the same `CoreApi`, so the DAG adds a link by running a command and draws its status badges from `scheduler.status()`, with no per-block callback. What it contributes to the screen, panels, navbar items and sidebar sections, goes through the front-end's own API, which for the dock is [Client-drawn dock and extensions](Rewrite-1.2)'s. Its state lives in fields it registers with the store, which other extensions and the assistant change as they change core's objects, and which stay consistent through the `expand` each field registers ([Board updates](Rewrite-1.1.2#fields)). A file holds those fields as the board does, with the version of the extension's package ([Serialization](Rewrite-1.1.4#files)), while a file from today's stack names the extension's constructor next to its state.

### Renderers

A renderer is a module that draws one kind of output ([Block types in R](Rewrite-1.1.5#outputs)) or a board option's value. A package declares its renderers in R, as it declares a front-end, each for the kinds or board options it draws: core declares a plain renderer for each kind it defines, blockr.ui declares its table preview for `blockr.core-table`, and a front-end may declare renderers of its own. R picks one renderer for each kind and each board option, the first of the one a blockr option names for it, the front-end's and another package's, and otherwise the renderer of the package that defines the kind, while a board option keeps the `ui` its definition gives ([Board objects](Rewrite-1.1.1#options)). Two renderers at one step are an error naming both, which the app settles with the blockr option. R sends the client the renderers it picked with the block registry's entries, and collects the board options they bring as it collects a block type's ([Defining a board in R](Rewrite-1.1.3#options)). So an app, a front-end or a UI kit changes how every table looks without touching a block type, as a JupyterLab extension replaces the renderer of a MIME type by registering its own ([registry.ts#L232-L258](https://github.com/jupyterlab/jupyterlab/blob/a877aee5ac6f490272a5ac18ac16b62b0deb1223/packages/rendermime/src/registry.ts#L232-L258)):

```r
# blockr.ui: a richer table for every block whose output is a table
register_renderer("table_preview", js_module("table-preview.js"),
                  kinds = "blockr.core-table", options = new_page_size_option)

# an app that wants core's plain table anyway
options(blockr.renderers = c("blockr.core-table" = "blockr.core-basic_table"))
```

A renderer gets an output host, or for a board option an option host ([UI modules in JS](Rewrite-1.1.7#the-contract)), through which it draws an output nested in its own, such as the table in blockr.dm's view of a dm, with the renderer R picked for that output's kind. A block's UI has no renderer, since it ships the schema of its block's state ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)), so a different UI makes a type derived from the block's ([Block types in R](Rewrite-1.1.5#cores-types-and-hooks)).

### What goes from R

The generics that draw or redraw UI from R go: `board_ui()`, `block_ui()`, `insert_block_ui()`, `remove_block_ui()`, `toolbar_ui()`, the stack UI generics, `blockr_app_ui()` and `blockr_app_server()`, and the `callbacks` of `board_server()`. A front-end's R side shrinks to declaring its front-ends by name with their modules, any renderers of its own (above), the constructors that app scripts call, such as the dock's `new_dock_board()` and `new_dock_stack()`, the blockr options its client reads ([Defining a board in R](Rewrite-1.1.3#blockr-options)), and the `as_*()` method that upgrades a plain board to that class when one is opened ([Board updates](Rewrite-1.1.2)).

## Open questions

- What core's basic front-end offers beyond cards, stacks and options, such as editing links, exporting code, or downloading and uploading a board.
- How an extension replaces the opening board before anything is drawn or evaluated, as session management must for the board a URL names, which arrives a few round trips after the `hello` has brought the script's board, where today's `rack_loader()` resolves it before the page is drawn ([Defining a board in R](Rewrite-1.1.3#the-opening-board)). It blocks adding front-end registration and `CoreApi`.
