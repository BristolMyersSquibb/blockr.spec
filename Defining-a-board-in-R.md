Status: draft. Design for [Board state owned by the client](Board-state-owned-by-the-client).

One of the API proposals for the client-owned board ([Board state owned by the client](Board-state-owned-by-the-client)): the R code that defines and launches an app. It builds on the [document model](Board-document-model) and the [serialization proposal](Board-serialization), and shapes the store's opening document ([blockr.core#394](https://github.com/BristolMyersSquibb/blockr.core/issues/394)) and the loader ([blockr.core#402](https://github.com/BristolMyersSquibb/blockr.core/issues/402)). How a block type is written is the block types proposal ([Block types in R](Block-types-in-R)).

## What must hold

1. An app script keeps the shape it has today: `serve()` around a board constructor that takes blocks, links, stacks, options and, for the dock, extensions.
2. The board the script builds becomes the client's opening board, and R keeps nothing of it afterwards.
3. Serving a single block while developing it, and serving a saved file, work as today.

## Today

The `serve()` generic has methods for a block, a board and the path of a saved file ([R/utils-serve.R#L28-L120](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L28-L120)). For a board, `serve.board(x, id, plugins, options, loader, ...)` combines `blockr_app_ui()` and `blockr_app_server()` ([#L204-L218](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L204-L218)), and blockr.dock implements those for `dock_board`, adding its navbar ([blockr.dock R/utils-serve.R#L2-L86](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serve.R#L2-L86)). A dock app reads ([inst/examples/edit-board/app.R#L9-L20](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/inst/examples/edit-board/app.R#L9-L20)):

```r
serve(
  new_dock_board(
    blocks = c(a = new_dataset_block("iris"), b = new_head_block()),
    links = links(ab = new_link(from = "a", to = "b", input = "data")),
    stacks = stacks(grp = new_dock_stack(blocks = "a", name = "Group A")),
    extensions = new_edit_board_extension()
  ),
  "my_board"
)
```

## Proposal

### The script

That script stays as it is. The board constructors keep their arguments, `new_board(blocks, links, stacks, options, ..., ctor, pkg, class)` ([R/board-class.R#L38](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-class.R#L38)) and `new_dock_board()` with its extensions, views, grids and active view ([R/dock-board.R#L55](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/dock-board.R#L55)), and so do `new_link()`, `links()`, `new_stack()`, `stacks()` and the block constructors, whose args are their blocks' state. Of these, `new_board()` and `new_link()` gain a `name`, since every object has one ([Document model](Board-document-model)), and the board's name replaces core's `board_name` option. What changes is inside the objects they return: a block holds its state and name and refers to its block type ([Block types in R](Block-types-in-R)), with no Shiny server or UI function, and a board's plugins become commands and extensions.

### The opening board

When a session starts, R turns the board into the client's board ([Document model](Board-document-model)), as `blockr_ser()` does for a file, and sends it with the registry in its reply to the client's `hello`. From then on the client owns it, and R holds the session's results and nothing of the board. A `loader` can replace the script's board for a session, as `local_loader()` does today, so a session package can open a user's draft instead.

### The `serve()` generic

The `serve()` generic and its three methods stay. For a board, `serve.board(x, id, options, loader, ...)` starts a Shiny app whose page loads core's client and the front-end registered for the board's class, such as the dock for `dock_board`, and whose server carries the protocol and evaluates. The `blockr_app_ui()` and `blockr_app_server()` methods go, since a front-end now registers for a board class on the client. For a block, `serve.block(x, data = list(...))` serves a board holding the block and data blocks for its inputs, drawn by core's basic front-end, as today. For a path, `serve()` loads the file through R, with the migrations of [blockr.core#402](https://github.com/BristolMyersSquibb/blockr.core/issues/402). The new stack's `serve()` has no `plugins` argument, since core keeps no plugin or extension type of its own: a plugin's logic becomes commands and its UI a dock extension, and the notes of [Dock and extensions in the browser](Dock-and-extensions-in-the-browser) map each of today's nine plugins to its new home.

### Options

A board's options are declared as today, through `options = default_board_options()` and the `board_options()` methods of its block types, and collected as `blockr_app_options()` collects them ([R/utils-serve.R#L172](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L172)). What the board holds is their values ([Document model](Board-document-model)).

## Open questions

- Whether the opening board is built once per app, as a script's top level runs once, or once per session, for a loader that depends on who opens it.
