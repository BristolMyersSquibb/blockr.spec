# The Edit board plugin for blocks, links and stacks
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): the plugin in blockr.core that adds, changes and removes the board's blocks, links and stacks, which every frontend places as it places any plugin.
It replaces the toolbar's dialogs for adding a block and for links and stacks that [blockr.core#441](https://github.com/BristolMyersSquibb/blockr.core/issues/441) built into core's basic frontend, and the port of the dock's Edit board extension that [The Edit board extension in React](Rewrite-1.2.8) planned.
It shapes the migration notes for app scripts ([blockr.core#445](https://github.com/BristolMyersSquibb/blockr.core/issues/445)), and its own Work item joins the spec [blockr#503](https://github.com/orgs/BristolMyersSquibb/discussions/503) once this page settles.
What a plugin is and which plugins a board has are [Plugins](Rewrite-1.1.12)'s, the commands it runs are [Board updates](Rewrite-1.1.2#commands)'s, and the rest of core's basic frontend, its card's menu among it, is [Drawing the board](Rewrite-1.1.8#cores-basic-frontend)'s.

## What must hold

1. It adds a block of any class in the block registry, under an id and a name that the user may give, renames and removes blocks, and adds, changes and removes links and stacks.
   That covers every edit that today's `manage_blocks`, `manage_links`, `manage_stacks` and `edit_stack` and the dock's Edit board extension make, but for giving a new link or stack an id, which the commands mint.
2. It works on the board through `CoreApi` alone, and every frontend places it as it places any plugin whose class has a `ui`, as condition 2 of [Plugins](Rewrite-1.1.12#what-must-hold) asks of every plugin.
3. Each edit is one of core's commands, applied as the user makes it, so that undo takes back each one and the user learns at once why the store refused one.
4. An app script that gives `serve()` no plugins gets this one, so that the user can add the first block to the board that `serve(new_board())` draws, and edit a board that `serve()` is given as a file, as today's `manage_blocks` lets them.
5. Under the board lock, it draws no control, as condition 3 of [Locked boards and the properties of blocks](Rewrite-1.1.11#what-must-hold) asks for what a lock fixes.
6. The conversion of today's files turns a dock board's Edit board extension into this plugin.

## Today

Core edits blocks, links and stacks through three plugins, Shiny module pairs of 1,350 lines with their roxygen.
The `manage_blocks` plugin adds and removes blocks through modals, and is one of the plugins that `serve()` gives every core board by default ([R/plugin-blocks.R#L1-L12](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-blocks.R#L1-L12), [R/board-plugins.R#L322-L331](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-plugins.R#L322-L331)).
The `manage_links` and `manage_stacks` plugins edit links and stacks in DT tables inside a modal, and each table takes an id for a new link or stack.
An app adds them itself, since they are not among those defaults and need the suggested DT package ([R/plugin-links.R#L1-L11](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-links.R#L1-L11), [R/plugin-stacks.R#L1-L11](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-stacks.R#L1-L11)).
The `edit_stack` plugin, another of the defaults, renames and removes a stack from the stack's own UI ([R/plugin-stack.R#L1-L8](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-stack.R#L1-L8)).

The dock's Edit board extension, `new_edit_board_extension()`, makes the same edits in a panel, in 1,310 lines.
Its docs call it "a simplistic example of an extension" that is "mainly relevant for testing purposes" ([R/ext-edit.R#L1-L25](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/ext-edit.R#L1-L25)).
It adds a block under an id the user picks, and removes the blocks the user selects, each at once.
Its tables of links and stacks stage their edits until "Apply changes" sends one update of the links and one of the stacks ([#L832-L942](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/ext-edit.R#L832-L942)).
An open issue, [blockr.dock#199](https://github.com/BristolMyersSquibb/blockr.dock/issues/199), asks to stage the block edits too, so that a block, a link to it and a stack that holds it go in one update.
Six of blockr.dock's examples, its README, its layouts vignette and twelve of its test files use the extension.

On `js-state`, core's basic frontend makes these edits itself ([blockr.core#441](https://github.com/BristolMyersSquibb/blockr.core/issues/441)).
Its toolbar opens three dialogs, one that adds a block, one for links and one for stacks, about 520 lines in [`picker.tsx`, `links.tsx` and `stacks.tsx`](https://github.com/BristolMyersSquibb/blockr.core/tree/1776bf174cec20d8534965fccd514a8e600b20c1/srcts/modules/basic).
Each edit in them runs one of core's commands at once.
The links dialog adds and removes a link, but does not change one.
The card's menu renames or removes a block, and adds one before or after it with the same picker ([card.tsx#L111-L138](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/srcts/modules/basic/card.tsx#L111-L138)).
The group that draws a stack holds no control ([card.tsx#L173-L187](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/srcts/modules/basic/card.tsx#L173-L187)).

## Proposal

### The plugin

In R, blockr.core exports the constructor, which makes a plugin of class `c("edit_board_plugin", "plugin")` with no state ([Plugins](Rewrite-1.1.12#a-plugin)):

```r
new_edit_board_plugin <- function(plugin_name = "Edit board") {
  new_plugin(list(), plugin_name, "edit_board_plugin")
}
```

Its class's id is `blockr.core-edit_board_plugin`.
Its id is `edit_board` where the list of plugins gives it no name ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)).
Its class gives R no requests, since the plugin needs no R, and no method of `plugin_version()`, so its state stays at version 1.

In JS, core registers the class itself as it starts, before the store opens a board, as it registers its own board options.
That needs no startup module, which blockr.core does not have ([blockr.core#544](https://github.com/BristolMyersSquibb/blockr.core/pull/544)).
The class has a `ui` and nothing else, so each of its plugins holds an empty state, `{}`, and the store has no `update` or `migrate` to call for it:

```ts
core.plugins.register({ id: "blockr.core-edit_board_plugin", ui: "blockr.core-edit_board" });
```

### What it shows

Its UI shows three sections.
Each section lists what the board holds, with the controls that edit it, and each control runs one of core's commands as one of the user's steps ([Board updates](Rewrite-1.1.2#commands)):

- Blocks: a picker of the block registry's entries, which searches their names, descriptions and keywords and groups them by category, with fields for the new block's id and name.
  The command `blockr.core-add_block` adds the block.
  Where the user leaves a field empty, the command mints the id, or takes the name from the block's class.
  Below the picker, each of the board's blocks shows with its name, which `blockr.core-rename_block` changes, and a button that removes the block with `blockr.core-remove_block`.
- Links: each link with the block it comes from, the block it goes to and the input it feeds, which `blockr.core-change_link` changes and `blockr.core-remove_link` removes.
  A form adds a link with `blockr.core-add_link`, and offers the inputs of the target block that no link feeds.
- Stacks: each stack with its name, which `blockr.core-rename_stack` changes, with its colour and its blocks, which `blockr.core-change_stack` changes, and with a button for `blockr.core-remove_stack`, which leaves the stack's blocks on the board.
  A button adds an empty stack with `blockr.core-add_stack`.

The form for a link and the button for a stack ask for no id, and the command mints one.
Today's tables take an id for a new link or stack, but nothing that the user reads shows either id.
A block's id differs: an exported script assigns the block's result to it, so the picker asks for it.

It draws nothing of a block's state, which the block's own UI sets, nor the board's name or its board options, which the frontend draws ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).

### Each edit at once

Each edit applies as the user makes it, while the tables of today's Edit board extension hold their edits until "Apply changes".
Each edit is one command, so undo takes back each one, and the user learns at once why the store refused one ([Board updates](Rewrite-1.1.2#undo)).
A block that the user adds is on the board at once, so the next edit can link it or put it in a stack.
The forms therefore read the board as it is.
Staging the block edits as well, as [blockr.dock#199](https://github.com/BristolMyersSquibb/blockr.dock/issues/199) asks, would have them read a staged copy of the board, in which a link can name a block that the board does not hold yet.
The plugin keeps nothing in its state, and nothing staged in its module.

The plugin raises a notification for each of its edits that the store or the command registry refuses, as core's basic frontend does for its own edits ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)).
It is an error of the class `edit_refused` that concerns no block, with the plugin's id as its origin.

### Where it shows

Every frontend places it as it places any plugin whose class has a `ui`, without knowing its class by id ([Plugins](Rewrite-1.1.12#plugin-classes)).
Core's basic frontend shows it in a section of its own beside the board, as it shows every plugin, and its toolbar draws no control for blocks, links or stacks ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
The card's menu keeps renaming and removing a block and adding one before or after it, since those edits act on one card.
The menu and the plugin share the picker inside core.
Renaming and removing a stack, which today's `edit_stack` does from the stack's own UI, is the plugin's alone, since the group that draws a stack holds no control.
The dock shows the plugin in a panel wherever the app holds it, as it shows any plugin, so that a dock board without the DAG still edits its links and stacks ([Client-drawn dock and extensions](Rewrite-1.2#proposal)).

Under the board lock, the store refuses every edit that the plugin makes ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).
So the plugin draws no control there, and only lists the board's links and stacks.
A frontend draws the blocks on their cards, but the dock draws no link and no stack without the DAG ([Client-drawn dock and extensions](Rewrite-1.2#proposal)).
It reads the lock from `core.lock.board` ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).

### Its look

Its UI is written in React, as TSX, and builds on Tailwind CSS under core's prefix, as core's basic frontend and the UIs of core's built-in blocks do ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
Other plugins take their look from blockr.ui's design system ([Plugins](Rewrite-1.1.12#plugin-classes)).
Core's own plugin cannot, since blockr.ui builds on blockr.core.
It takes its colours, fonts and radii from Tailwind's theme variables, which the dock or blockr.ui may set to restyle it ([UI kit and design system for the client](Rewrite-1.7)).

### What `serve()` gives by default

By default, an app runs the plugin: the `plugins` of `serve()` default to `list(new_edit_board_plugin())`, for a board and for a path alike ([Defining a board in R](Rewrite-1.1.3#the-serve-generic)).
So an app script that gives `serve()` no plugins gets it, and the user can add the first block to the board that `serve(new_board())` draws, as today's `serve()` gives every core board `manage_blocks`.
A file that `serve()` is given gets it too, since a file gives only the state of its plugins ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)), as today's `serve()` gives the defaults to a core board that it reads from a file ([R/utils-serve.R#L297-L305](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L297-L305)).
A script that passes `plugins` lists the plugin where it wants it, and a locked app may leave it out.
A block that `serve()` serves alone gets no plugin, since no frontend places one for it ([Defining a board in R](Rewrite-1.1.3#the-serve-generic)).
Whether a dock app runs it, through what blockr.dock offers a script to pass to `serve()`, is an open question of [Client-drawn dock and extensions](Rewrite-1.2#open-questions).
Today's `new_dock_board()` adds no extension by default ([blockr.dock R/dock-board.R#L55-L56](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-board.R#L55-L56)).
A dock board with neither this plugin nor the DAG gets no first block, as today, since the dock itself only appends a block after another, from a card's menu ([Client-drawn dock and extensions](Rewrite-1.2#proposal)).

### Boards and app scripts from today

The conversion outside core turns a dock board's Edit board extension into this plugin, under the name that the board gave the extension, as it turns every extension into a plugin ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)).
The plugin's state is empty, since the extension keeps none.
A core board that today's stack saved holds no plugin once converted, since today's `serve()` takes the plugins and the file holds none, and served by its path it runs this plugin from the default of `serve()` (above).
Whether blockr.dock keeps `new_edit_board_extension()` as a name for `new_edit_board_plugin()`, for the scripts, examples and tests that call it, is [Saved boards and app scripts across the switch](Rewrite-1.2.2)'s to settle.
An app that adds `manage_links()` or `manage_stacks()` through `serve(plugins = ...)` gets their edits from this plugin, which the default of `serve()` holds, since both go ([Plugins](Rewrite-1.1.12#what-goes)).
A script that today extends the defaults through `serve(plugins = custom_plugins(...))` keeps `manage_blocks` among them, since `custom_plugins()` keeps every default that it does not replace ([R/utils-serve.R#L147-L163](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L147-L163)).
The README of blockr.code does so for a core board ([blockr.code README.Rmd#L43-L56](https://github.com/BristolMyersSquibb/blockr.code/blob/72b20d6911496e4edc9ee64db758e70ebf3f50ca/README.Rmd#L43-L56)).
Such a script passes `serve()` its plugins as a list instead, which `custom_plugins()` no longer builds ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)), and lists this plugin in it, since a list that a script passes replaces the default.

## Open questions

None.

<details><summary>Notes for implementers</summary>

The dialogs to move, at `1776bf1`, are `picker.tsx`, `links.tsx` and `stacks.tsx` in `srcts/modules/basic/`, which `board.tsx` opens from `toolbar.tsx`.
They draw through the basic frontend's context, `useFrontEnd()` and `runCommand()`, which the plugin's module replaces with the `CoreApi` that its `render()` gets and with a notification of its own for a refused edit.
The card's menu keeps opening the picker in its `after` and `before` modes, so the picker stays a component that both share, while the plugin opens it in its `add` mode, with fields for the `id` and `name` that `blockr.core-add_block` takes.
Changing a link through `blockr.core-change_link` is new, since the dialog on `js-state` only adds and removes links.

Core registers the class in `srcts/core/start.ts`, beside its own board options, before the store opens a board.
In R, the constructor goes beside `new_plugin()` in `R/plugin-class.R`, and `serve.board()` and `serve.character()` in `R/utils-serve.R` take it as the default of `plugins`, while `new_board()` keeps `plugins = list()`, since a board holds only the state of its plugins.
The `serve.block()` method gives the app no plugin for its board of one block, which it builds with `new_board(x)` ([R/utils-serve.R#L102](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/R/utils-serve.R#L102)), since no frontend places a plugin for a block served alone.
The conversion of today's files maps blockr.dock's class `edit_board_extension` to `blockr.core-edit_board_plugin`.

Today's plugins are `R/plugin-blocks.R`, `R/plugin-links.R` and `R/plugin-stacks.R` at `da3fcb4`, of 218, 574 and 558 lines.
The dock's extension is `R/ext-edit.R` at `655e323`, which the examples `edit-add`, `edit-board`, `empty`, `rails`, `serdes` and `single-page` use.

</details>
