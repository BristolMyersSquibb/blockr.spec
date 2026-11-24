# The Edit board plugin for blocks, links and stacks
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): the plugin in blockr.core that adds, changes and removes the board's blocks, links and stacks, which every frontend places as it places any plugin.
It replaces the toolbar's dialogs for adding a block and for links and stacks that [blockr.core#441](https://github.com/BristolMyersSquibb/blockr.core/issues/441) built into core's basic frontend, and the port of the dock's Edit board extension that [The Edit board extension in React](Rewrite-1.2.8) planned.
It shapes the plugin itself ([blockr.core#565](https://github.com/BristolMyersSquibb/blockr.core/issues/565)), an item in the Work list of the spec [blockr#503](https://github.com/orgs/BristolMyersSquibb/discussions/503), showing a refused edit close to the control that made it ([blockr.core#711](https://github.com/BristolMyersSquibb/blockr.core/issues/711)), the picker and the forms that it mounts as advanced actions ([blockr.core#745](https://github.com/BristolMyersSquibb/blockr.core/issues/745), [blockr.core#746](https://github.com/BristolMyersSquibb/blockr.core/issues/746)), the menus of its rows and of its selection ([blockr.core#783](https://github.com/BristolMyersSquibb/blockr.core/issues/783)), and the migration notes for app scripts ([blockr.core#445](https://github.com/BristolMyersSquibb/blockr.core/issues/445)).
What a plugin is and which plugins a board has are [Plugins](Rewrite-1.1.12)'s, the board actions that its rows and forms offer are [Board actions](Rewrite-1.1.16)'s, the commands that those run are [Board updates](Rewrite-1.1.2#commands)'s, and the rest of core's basic frontend, its card's menu among it, is [Drawing the board](Rewrite-1.1.8#cores-basic-frontend)'s.

## What must hold

1. It adds a block of any class in the block registry, under an id and a name that the user may give, renames and removes blocks, and adds, changes and removes links and stacks.
   That covers every edit that today's `manage_blocks`, `manage_links`, `manage_stacks` and `edit_stack` and the dock's Edit board extension make, but for giving a new link or stack an id, which core mints.
2. It works on the board through `CoreApi` alone, and every frontend places it as it places any plugin whose class has a `ui`, as condition 2 of [Plugins](Rewrite-1.1.12#what-must-hold) asks of every plugin.
3. Each edit is one batch of a board action, applied as the user makes it, so that undo takes back each one and the user learns at once, close to the control that made it, why the store refused one.
4. An app script that gives `serve()` no plugins gets this one, as it gets a plugin of each class that an available package lists, so that the user can add the first block to the board that `serve(new_board())` draws, and edit a board that `serve()` is given as a file, as today's `manage_blocks` lets them.
5. Under the board lock, it draws no control for what the lock fixes, as condition 3 of [Locked boards and the properties of blocks](Rewrite-1.1.11#what-must-hold) asks.
6. Each row offers the menu of its block, link or stack, so that the row offers every board action that applies to its object, a package's among them, as every other menu of the object does ([Board actions](Rewrite-1.1.16#what-must-hold)).

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
An issue, [blockr.dock#199](https://github.com/BristolMyersSquibb/blockr.dock/issues/199), asked to stage the block edits too, so that a block, a link to it and a stack that holds it go in one update, and closed once this page settled that each edit applies at once (below).
Six of blockr.dock's examples, its README, its layouts vignette and twelve of its test files use the extension.

On `js-state`, core's basic frontend makes these edits itself ([blockr.core#441](https://github.com/BristolMyersSquibb/blockr.core/issues/441)).
Its toolbar opens three dialogs, one that adds a block, one for links and one for stacks, about 520 lines in [`picker.tsx`, `links.tsx` and `stacks.tsx`](https://github.com/BristolMyersSquibb/blockr.core/tree/1776bf174cec20d8534965fccd514a8e600b20c1/srcts/modules/basic).
Each edit in them runs one of core's commands at once.
The links dialog adds and removes a link, but does not change one.
The card's menu renames or removes a block, and adds one before or after it with the same picker ([card.tsx#L111-L138](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/srcts/modules/basic/card.tsx#L111-L138)).
The group that draws a stack holds no control ([card.tsx#L173-L187](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/srcts/modules/basic/card.tsx#L173-L187)).
Since [blockr.core#569](https://github.com/BristolMyersSquibb/blockr.core/pull/569), the plugin is on `js-state`, and at `6805109` its rows rename and remove a block, and edit and remove a link or a stack, with buttons of their own that run core's commands ([blocks.tsx#L76-L124](https://github.com/BristolMyersSquibb/blockr.core/blob/6805109b4fa67e8899b956620e9b2faca6a12a99/srcts/modules/edit-board/blocks.tsx#L76-L124), [links.tsx#L107-L175](https://github.com/BristolMyersSquibb/blockr.core/blob/6805109b4fa67e8899b956620e9b2faca6a12a99/srcts/modules/edit-board/links.tsx#L107-L175), [stacks.tsx#L104-L169](https://github.com/BristolMyersSquibb/blockr.core/blob/6805109b4fa67e8899b956620e9b2faca6a12a99/srcts/modules/edit-board/stacks.tsx#L104-L169)).
So the plugin makes the edits of core's board actions a second way, and offers none of another package's.

## Proposal

### The plugin

In R, blockr.core exports the constructor, which makes a plugin of class `c("edit_board_plugin", "plugin")` with no state ([Plugins](Rewrite-1.1.12#a-plugin)):

```r
new_edit_board_plugin <- function() {
  new_plugin(list(), "edit_board_plugin")
}
```

Its class's id is `blockr.core-edit_board_plugin`.
Its name is "Edit board", which core lists for the class ([Plugins](Rewrite-1.1.12#a-plugin)).
Its class gives R no requests, since the plugin needs no R, and no method of `plugin_version()`, since the plugin keeps no state.

In JS, core registers the class from a module of its own, which core lists as any package lists a plugin class, before the store opens a board, as it registers its own board options and the classes of its basic frontend and its storage plugin ([Plugins](Rewrite-1.1.12#the-frontend), [blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)).
The class has a `ui` and nothing else, so the board holds nothing for its plugins, and the store has no `update` or `migrate` to call for it ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)):

```ts
core.plugins.register({ id: "blockr.core-edit_board_plugin", ui: "blockr.core-edit_board" });
```

### What it shows

Its UI shows three sections.
Each section lists what the board holds in a table that searches its rows and shows them ten to a page, so that it stays usable on a large board, below a form that adds one ([blockr.core#569](https://github.com/BristolMyersSquibb/blockr.core/pull/569)).
Each form is the advanced action of the board action that plays one of core's roles on the board, `add_block_role`, `add_link_role` or `add_stack_role`, which the plugin mounts through `mountAdvanced()` by the role's id, so that the plugin and the menus share it, and a board action that the app picks for the role shows its form here too ([Board actions](Rewrite-1.1.16#roles)):

- Blocks: the advanced action of Add block, the block picker, which searches the block registry's entries by their names, descriptions and keywords and groups them by category, with fields for the new block's id and name, and which adds nothing as the user picks a class, but only once the user submits it, so that the id and the name go in first ([blockr.core#569](https://github.com/BristolMyersSquibb/blockr.core/pull/569)).
  Where the user leaves a field empty, the picker mints the id, or takes the name from the block's class.
  Each row shows a block: its name, its id and its class.
- Links: the advanced action of Create link, a form that starts from no block, and offers as its target only a block that takes a link, and none that would close a cycle, as the dock's menus do today, and of that block the inputs that no link feeds, or for a variadic block an optional name for the link, as `b2` in `rbind(a, b2 = b)`, which no other link into the block gives ([Block classes in R](Rewrite-1.1.5#expressions), [blockr.core#569](https://github.com/BristolMyersSquibb/blockr.core/pull/569)).
  Each row shows a link: the block it comes from, the block it goes to and the input it feeds.
- Stacks: the advanced action of Create stack, a form that takes a new stack's name, its colour and its blocks first, and suggests a name and a colour that no other stack has, as the dock gives its stacks colours today ([blockr.core#569](https://github.com/BristolMyersSquibb/blockr.core/pull/569)).
  Each row shows a stack: its name, its colour and its blocks.

The plugin mounts a form only where `core.boardActions.on()` offers the form's board action on the board.
Every other edit is a board action that a row's menu offers.
Each row ends in a "…" button, which opens the menu of the row's block, link or stack through `core.boardActions.menu()`, as every menu of a board object opens ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).
So a row offers what every menu of its object offers, such as Rename and Remove block on a block, Edit link and Remove link on a link, and Rename, Edit stack and Remove stack on a stack, and the board actions of other packages too, such as blockr.md's Add to document on a block ([Board actions](Rewrite-1.1.16#a-board-action)).
A row shows the button only where `core.boardActions.on()` gives its object a board action.
An advanced action that a row's menu opens, such as the form of Edit link or of Edit stack, shows in the row, which turns into the form, as a row turns into its form today, and applies what the user changed in it through its Apply button ([Board actions](Rewrite-1.1.16#the-advanced-action)).
The plugin hands `menu()` an `advanced` that mounts the form in a cell across the row, and closes the form once `done()` ends the advanced action ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).

Each row also holds a checkbox, which adds the row's object to `core.selection` or takes it out.
The checkbox shows whether the selection holds the object, whatever set the selection, such as the DAG as the user selects nodes ([Board actions](Rewrite-1.1.16#the-advanced-action)).
While the selection holds a board object, a bar above the sections says how many it holds, with a "…" button that opens the menu of the selection, which offers Remove, Create stack and Add to stack among core's board actions, and a button that clears the selection.
An advanced action that the menu of the selection opens shows below the bar, as Create stack's form with the selected blocks given.

The forms for a link and for a stack ask for no id, and the board action mints one.
Today's tables take an id for a new link or stack, but nothing that the user reads shows either id.
A block's id differs: an exported script assigns the block's result to it, so the picker asks for it.

It draws nothing of a block's state, which the block's own UI sets, nor the board's name or its board options, which the frontend draws ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).

### Each edit at once

Each edit applies as the user makes it, by submitting a form, applying the form that a row turns into, or picking a row of a menu, while the tables of today's Edit board extension hold their edits until "Apply changes".
Each edit is one batch of a board action, so undo takes back each one, and the user learns at once why the store refused one ([Board updates](Rewrite-1.1.2#undo)), so that renaming a stack and then changing its blocks makes two steps, which undo takes back one at a time.
A block that the user adds is on the board at once, so the next edit can link it or put it in a stack.
The forms therefore read the board as it is.
Staging the block edits as well, as [blockr.dock#199](https://github.com/BristolMyersSquibb/blockr.dock/issues/199) asked, would have them read a staged copy of the board, in which a link can name a block that the board does not hold yet.
The plugin keeps nothing in its state, and nothing staged in its module.
That is this plugin's choice, not the API's: another plugin may stage edits and apply them later as one delta, which holds any number of blocks, links and stacks, through `core.store.apply()` or a command of its own, as one step that one undo takes back ([Board updates](Rewrite-1.1.2#applying-a-delta)).

Where the store or the command registry refuses one of its edits, the plugin shows why close to the control that made it, in a banner in the colour of an error, until the user's next edit there, and takes the notifications through a `notifier`, so that core raises none ([Notifications, logging and tracing](Rewrite-1.1.14#taking-a-calls-notifications)).
Close means near the control, not as near as can be.
A form shows why below its buttons, through the `notifier` of its `done()`, as every advanced action does ([Board actions](Rewrite-1.1.16#the-advanced-action)).
A table shows why below itself for a board action that the menu of one of its rows ran, through the `notifier` of `menu()`, and the bar of the selection shows why below itself for one that the menu of the selection ran.
A line below the row would break up the table, and the row's button sits in a column too narrow for a sentence.
Each reason starts with a sentence that names the edit, such as `Could not add the link.` or `Could not remove the stack "Input".`, which a table needs most, because the store names links and stacks by ids that the table does not show.
For a board action that a menu ran, the `notifier` of `menu()` hands the plugin the board action with the notifications, and the plugin names the edit by it: in its own words for core's board actions, as `Could not remove the stack "Input".`, and by its label for another package's, as `Add to document failed for the block "Filter".` ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).
The failures that the store or the command registry gives follow it, as a list where there are several, without the line that heads the error's message, which names the command or the delta rather than the edit.
At a form, the user's next edit is its next submit, also one that the form's own checks stop, since those checks then say what to change.
In a table or the bar, it is the next board action that one of its menus runs.
So the user reads why near where they made the edit, rather than in a toast that names no form, as every plugin with a UI shows what fails of what the user did in it ([Notifications, logging and tracing](Rewrite-1.1.14#where-a-notification-shows)).

### Where it shows

Every frontend places it as it places any plugin whose class has a `ui`, without knowing its class by id ([Plugins](Rewrite-1.1.12#plugin-classes)).
Core's basic frontend shows it in a section of its own beside the board, as it shows every plugin, and its toolbar draws no control for blocks, links or stacks ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
The card's menu offers the board actions on its block, renaming and removing it and appending or prepending a block among them, since those edits act on one card ([Board actions](Rewrite-1.1.16#cores-board-actions)).
The plugin's rows open the same menus, so that the card's menu and a block's row offer the same board actions, and its three forms are advanced actions that the menus open too (What it shows).
Under core's basic frontend, only the menu of a stack's row offers Rename and Remove stack for the stack, which today's `edit_stack` offers in the stack's own UI, since the group that draws a stack holds no control.
The DAG's menu of a stack offers both as well, as core's Rename and Remove stack ([Board actions](Rewrite-1.1.16#cores-board-actions)).
The dock shows the plugin in a panel wherever the app holds it, as it shows any plugin, so that a dock app without the DAG still edits its links and stacks ([Client-drawn dock](Rewrite-1.2#proposal)).

Under the board lock, the store refuses what every one of core's board actions but Copy block ID runs, so they fail their `offers` ([Board actions](Rewrite-1.1.16#cores-board-actions), [Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).
So the plugin mounts no form there, its rows and its bar show no "…" unless another package's board action applies, and it lists only the board's links and stacks.
A frontend draws the blocks on their cards, but the dock draws no link and no stack without the DAG ([Client-drawn dock](Rewrite-1.2#proposal)).
It reads the lock from `core.lock.board` ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).

### Its look

Its UI is written in React, as TSX, and draws with blockr.ui's components and with Tailwind CSS under core's prefix, built against the theme variables, as core's basic frontend and the UIs of core's built-in blocks do ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
So it takes its look from blockr.ui under every frontend, as other plugins do ([Plugins](Rewrite-1.1.12#plugin-classes), [UI kit and design system for the client](Rewrite-1.7)).

### What `serve()` gives by default

By default, an app runs the plugin, since core lists its class, and the `plugins` of `serve()` default to `available_plugins()`, a row for each plugin class that an available package lists, for a board and for a path alike ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has), [Defining a board in R](Rewrite-1.1.3#the-serve-generic)).
So an app script that gives `serve()` no plugins gets it, and the user can add the first block to the board that `serve(new_board())` draws, as today's `serve()` gives every core board `manage_blocks`.
A file that `serve()` is given gets it too, since a file gives only the state of its plugins ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)), as today's `serve()` gives the defaults to a core board that it reads from a file ([R/utils-serve.R#L297-L305](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L297-L305)).
Rows that a script passes hold the plugin where it wants it, and a locked app may leave it out.
A block that `serve()` serves alone gets no plugin, since no frontend places one for it ([Defining a board in R](Rewrite-1.1.3#the-serve-generic)).
A dock app runs it too, since the dock takes the place of core's basic frontend alone, where today's `new_dock_board()` adds no extension by default ([blockr.dock R/dock-board.R#L55-L56](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-board.R#L55-L56)).
A dock app whose rows hold neither this plugin nor the DAG offers no way to add the first block, as a dock board without either does today, since the dock itself only appends a block after another, from a card's menu ([Client-drawn dock](Rewrite-1.2#proposal)).

### Boards and app scripts from today

A core board that today's stack saved holds no plugin's state once converted, since today's `serve()` takes the plugins and the file holds none, and served by its path it runs this plugin from the default of `serve()` (above).
The dock's `new_edit_board_extension()` goes without an alias, and the scripts, examples and tests that call it drop it, since this plugin runs by default ([Saved boards and app scripts across the switch](Rewrite-1.2.2)).
An app that adds `manage_links()` or `manage_stacks()` through `serve(plugins = ...)` gets their edits from this plugin, since both go ([Plugins](Rewrite-1.1.12#what-goes)).
A script that today extends the defaults through `serve(plugins = custom_plugins(...))` keeps `manage_blocks` among them, since `custom_plugins()` keeps every default that it does not replace ([R/utils-serve.R#L147-L163](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L147-L163)).
The README of blockr.code does so for a core board ([blockr.code README.Rmd#L43-L56](https://github.com/BristolMyersSquibb/blockr.code/blob/72b20d6911496e4edc9ee64db758e70ebf3f50ca/README.Rmd#L43-L56)).
Such a script passes `serve()` no plugins instead, since `custom_plugins()` goes and the plugins it added run by default where their packages are available, this one among them ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

The dialogs to move, at `1776bf1`, are `picker.tsx`, `links.tsx` and `stacks.tsx` in `srcts/modules/basic/`, which `board.tsx` opens from `toolbar.tsx`.
They draw through the basic frontend's context, `useFrontEnd()` and `runCommand()`, which the plugin's module replaces with the `CoreApi` that its `render()` gets and with a notification of its own for a refused edit.
The card's menu keeps opening the picker in its `after` and `before` modes, so the picker stays a component that both share, while the plugin opens it in its `add` mode, with fields for the `id` and `name` that `blockr.core-add_block` takes.
Changing a link through `blockr.core-change_link` is new, since the dialog on `js-state` only adds and removes links.
On `js-state`, at `6805109`, the rows' own buttons are in `BlockRow`, `LinkRow` and `StackRow` in `srcts/modules/edit-board/`, and the form that a row turns into is `LinkForm` or `StackForm` in its editing mode.
Both go once the rows open menus, while the forms that add become advanced actions ([blockr.core#746](https://github.com/BristolMyersSquibb/blockr.core/issues/746)).
React Aria's `Table`, which [blockr.core#757](https://github.com/BristolMyersSquibb/blockr.core/issues/757) added to the React SDK and which moves to blockr.ui with the SDK's other components, draws a row's checkbox where its `selectionMode` is `"multiple"`, and the plugin binds its `selectedKeys` and `onSelectionChange` to `core.selection`.

Core registers the class in `srcts/core/start.ts`, beside its own board options, before the store opens a board.
In R, the constructor goes beside `new_plugin()` in `R/plugin-class.R`, and core lists the class beside those of its basic frontend and its storage plugin, so that `available_plugins()` gives it a row, while `new_board()` keeps `plugins = list()`, since a board holds only the state of its plugins.
The `serve.block()` method gives the app no plugin for its board of one block, which it builds with `new_board(x)` ([R/utils-serve.R#L102](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/R/utils-serve.R#L102)), since no frontend places a plugin for a block served alone.

Today's plugins are `R/plugin-blocks.R`, `R/plugin-links.R` and `R/plugin-stacks.R` at `da3fcb4`, of 218, 574 and 558 lines.
The dock's extension is `R/ext-edit.R` at `655e323`, which the examples `edit-add`, `edit-board`, `empty`, `rails`, `serdes` and `single-page` use.

</details>
