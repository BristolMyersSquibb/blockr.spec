# Front-ends and extension points for the client-owned board
Status: draft. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): core's basic front-end, how a front-end such as blockr.dock replaces it, and what front-ends and their extensions hook into. It builds on the [document model](Rewrite-1.1.1) and on the [board updates](Rewrite-1.1.2), evaluation ([Evaluation in the client](Rewrite-1.1.10)) and UI modules ([UI modules in JS](Rewrite-1.1.7)) proposals. The dock's own contribution API, its panels, navbar items and sidebar sections, is [Client-drawn dock and extensions](Rewrite-1.2)'s.

## What must hold

1. Core ships a basic front-end that draws any board, so a board serves without blockr.dock, and a front-end replaces it entirely, as the dock replaces core's UI today.
2. A front-end draws everything around a block, its card, panel, menus and status, while the block's UI and output come from core, so a block type works in every front-end.
3. A front-end and its extensions work on the board only through core's client API: the store, commands, demand, statuses and requests.
4. Nothing in R draws or redraws UI.

## Today

Core's front-end is `board_ui.board()`: a toolbar of its plugins with a popover of board options, a bslib accordion of stacks and a bslib card per block, whose header and footer the edit_block plugin draws ([R/board-ui.R#L40-L140](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-ui.R#L40-L140)). It computes a block's status without drawing it, and shows conditions as notifications ([R/plugin-notification.R#L76-L140](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-notification.R#L76-L140)). A front-end replaces it by implementing generics that dispatch on the board, `board_ui()`, `block_ui()`, `insert_block_ui()`, `remove_block_ui()` and more, and blockr.dock implements most of them, while core's stack generics still fire underneath it ([R/stack-ui.R#L37-L255](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/stack-ui.R#L37-L255)). Extensions hook in through `new_dock_extension()` and `extension_block_callback()`, which the DAG uses to draw status badges ([R/ext-class.R#L52](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/ext-class.R#L52), [blockr.dag R/ext.R#L521-L583](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/ext.R#L521-L583)). Insertions and removals reach the page through R, and the dock's removal currently misses: the selector it passes to `removeUI()` is built from the board's id instead of the block's and lacks the `#`, so it matches no element, as [blockr.dock#527](https://github.com/BristolMyersSquibb/blockr.dock/issues/527) reports ([R/block-ui.R#L104](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/block-ui.R#L104)).

## Proposal

### Registering a front-end

A front-end is a module registered for the registry id of the board type it draws, as the dock registers for `blockr.dock-dock_board` and core's basic front-end for `blockr.core-board` ([Document model](Rewrite-1.1.1#registry-ids)). The page loads the front-end of the app's board type, and a board of another type is converted or drawn by it when it is opened ([Board updates](Rewrite-1.1.2#opening-a-board)), so the front-end never changes while the page lives.

```ts
registerFrontEnd("blockr.dock-dock_board", {
  mount(el: HTMLElement, api: CoreApi): () => void { /* draw the board, return the cleanup */ }
});
```

### What core gives a front-end

```ts
interface CoreApi {
  store: Store;                    // board(), subscribe(), apply(), open(), register(), from Board updates
  commands: Commands;              // run(), plan() and the registry, for menus and shortcuts
  scheduler: Scheduler;            // demand(), evaluate(), invalidate(), status(), from Evaluation in the client
  registry: Registry;              // block types, options and commands, for pickers and settings
  mountBlock(el: HTMLElement, block: BlockId): () => void;    // the block's UI module
  mountOutput(el: HTMLElement, block: BlockId): () => void;   // its output, measured and fetched
  mountOption(el: HTMLElement, option: OptionId): () => void; // an option's UI
}
```

A front-end decides where things go and core fills them: it gives `mountBlock()` the body of a card or a panel, and core mounts the block's UI module there, so the dock's card sections stay the dock's business while what is in them stays core's. The `mountOutput()` call measures its element for the output's `info`, asks R for the output and redraws it when the block's version, an option or the size changes. A front-end draws a block's status and conditions from `scheduler.status()`, demands what it shows, and follows the board through `store.subscribe()`, so a removed block's card goes away because the board changed, not because R said so.

### Core's basic front-end

Core's own front-end draws what today's does: a toolbar with adding a block and the board's options, stacks as groups, and a card per block with its name, a menu to rename or remove it, its UI and its output. It also draws each block's status and conditions on its card, which today's computes but does not show. It demands nothing of its own, since a board evaluates every block unless its `evaluation` option is lazy ([Evaluation in the client](Rewrite-1.1.10)), so a board served without the dock evaluates eagerly, as today.

### Extensions

An extension is a module too, registered with the front-end it extends, and works on the board through the same `CoreApi`, so the DAG adds a link by running a command and draws its status badges from `scheduler.status()`, with no per-block callback. What it contributes to the screen, panels, navbar items and sidebar sections, goes through the front-end's own API, which for the dock is [Client-drawn dock and extensions](Rewrite-1.2)'s. Its state lives in fields it registers with the store, which other extensions and the assistant change as they change core's objects, and which stay consistent through the `expand` each field registers ([Board updates](Rewrite-1.1.2#fields)). A file names the extension's constructor next to its state, as today ([Serialization](Rewrite-1.1.4)), which the extension's package declares as a front-end declares the constructors of its classes (below).

### What goes from R

The generics that draw or redraw UI from R go: `board_ui()`, `block_ui()`, `insert_block_ui()`, `remove_block_ui()`, `toolbar_ui()`, the stack UI generics, `blockr_app_ui()` and `blockr_app_server()`, and the `callbacks` of `board_server()`. A front-end's R side shrinks to declaring its module, its board type and the constructors of the classes it adds, such as the dock's `new_dock_board()` and `new_dock_stack()`, which the registry export carries so that the client can name them in a file ([blockr.core#396](https://github.com/BristolMyersSquibb/blockr.core/issues/396), [Serialization](Rewrite-1.1.4)), and the `as_*()` method that upgrades a plain board to that class when one is opened ([Board updates](Rewrite-1.1.2)).

## Open questions

- Whether core's runtime ships React, so a block's React module also works under core's basic front-end, or whether the global stays the dock's to fill ([blockr.core#399](https://github.com/BristolMyersSquibb/blockr.core/issues/399)).
- What core's basic front-end offers beyond cards, stacks and options, such as editing links, exporting code, or downloading and uploading a board.
