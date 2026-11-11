# The dock's navbar
Status: review. Design for [Client-drawn dock](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock](Rewrite-1.2)): the bar across the top of the dock.
It covers what the bar holds and in what order, what gives way on a narrow bar, the dock's own parts of it, and how the dock draws the controls of the app's storage plugin.
It also covers what becomes of the navbar's functions in R, which [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) settled.
The bar is the dock's alone: no plugin adds to it, and the storage plugin is the only other plugin whose controls it draws ([Plugins](Rewrite-1.1.12#storage)).
It shapes two items of the Work of [Client-drawn dock](Rewrite-1.2#work): drawing the dock from the client's board, the bar among it, and writing the migration notes for dock app scripts.
It builds on [Plugins](Rewrite-1.1.12#storage), whose storage controls the bar draws, and on [Drawing the board](Rewrite-1.1.8#what-core-gives-plugins), whose `CoreApi` the bar works through.
The views and folders that the views menu lists, with the commands that change them, are [The dock's state](Rewrite-1.2.1)'s, and which controls blockr.session's storage plugin gives is [Session management as a client extension](Rewrite-1.6)'s.

## What must hold

Condition 4 of [Client-drawn dock](Rewrite-1.2#what-must-hold) rests on this page for what today's navbar does, and condition 10 of [Plugins](Rewrite-1.1.12#what-must-hold) for the dock's part in drawing the storage plugin's controls.

1. The bar holds the dock's own parts and the controls of the app's storage plugin, and nothing else.
   No plugin adds to it, so an app changes it only through the storage plugin it runs.
2. It holds what today's default bar holds, in today's order: the logo as busy indicator, the controls of the app's storage plugin where the `preserve_board` plugin's piece is, the views menu with its tab line, the read-only pill and the options button.
   Two parts join them, the board's name after the logo and Undo and Redo after the storage plugin's controls, and the controls that ask for the end of the bar go after the options button, where blockr.session's avatar sits today.
3. The dock draws every kind of control that a storage plugin gives, in its own look, and honors the hint `placement: "end"`, so that the controls of core's storage plugin, of blockr.session's and of one from a package the dock does not know all look like the rest of the bar.
4. On a narrow bar, the board's name and the storage plugin's controls give way first, and the dock's other parts keep their width and stay on one line, as condition 4 of [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) asks.
5. A part with nothing to show takes no room, as the read-only pill on a board without the board lock, or the storage plugin's place in an app without one.
6. The dock's own parts draw no control for what a lock fixes ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).
   Under the board lock, the board's name only shows, the views menu only switches views, the read-only pill shows, and Undo and Redo stay, since what that lock leaves open still takes undo steps.
   The storage plugin's controls leave out what a lock fixes themselves, such as opening another board under the load lock ([Plugins](Rewrite-1.1.12#storage)).

## Today

At `655e323`, blockr.dock draws the navbar from a list of navbar items, each made by `navbar_item(id, ui, server, fill, shrink)` ([R/dock-navbar.R#L67-L74](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-navbar.R#L67-L74)).
It draws them in one row, 48px high, in the order of the list.
An item with `fill` takes the free space, an item with `shrink` gives way first on a narrow bar, and the others keep their width ([inst/assets/css/blockr-dock.css#L538-L567](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L538-L567)).
An item whose `ui` returns `NULL` is left out, and an item whose only output renders nothing takes no room.

The default items of `default_navbar_items()` are, in order ([R/dock-navbar.R#L244-L283](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-navbar.R#L244-L283)):

1. The logo, which is the busy indicator ([blockr.dock#530](https://github.com/BristolMyersSquibb/blockr.dock/issues/530)).
2. The piece of the `preserve_board` plugin, which shrinks.
   For core's storage plugin, the dock gives that plugin a UI of its own, Import and Export, one row of quiet 30px buttons that keep the input ids that core's server reads ([R/board-plugins.R#L10-L15](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/board-plugins.R#L10-L15), [R/plugin-serdes.R#L9-L28](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-serdes.R#L9-L28)).
   The `manage_project()` plugin of blockr.session brings its own UI for the piece: the workflow's name with a menu of workflows and drafts, the save status, and a Save menu with Save, Save as, Download, versions and Share ([blockr.session R/ui.R#L6-L184](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/ui.R#L6-L184)).
3. A spacer, which fills.
4. The views menu, with a short rule after it, which draws the views as a line of tabs under the bar while the `view_tabs` board option is on ([blockr.dock#555](https://github.com/BristolMyersSquibb/blockr.dock/issues/555)).
5. The read-only pill, only on a locked board.
6. The options button, which opens the options sidebar.

Core's own board places the same piece of the `preserve_board` plugin in its toolbar ([blockr.core R/board-ui.R#L215-L257](https://github.com/BristolMyersSquibb/blockr.core/blob/5abaa52bc04bf202dab9c6e17772f2a170b10a38/R/board-ui.R#L215-L257)).

An app changes the bar through `serve(navbar = f)`, where `f` is a function of the board and its plugins that returns the items.
The function that `custom_navbar(items)` returns appends `items` to the default items, and drops each default item that shares an id with one of them ([R/dock-navbar.R#L298-L308](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-navbar.R#L298-L308)).
An app's own function can also reorder or drop items by id with `[`.
Two packages add items, and both append them.
The avatar of blockr.session, `avatar_navbar_item()`, shows the initials of `session$user`, and draws nothing for a visitor who is not signed in ([R/avatar.R#L23-L53](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/avatar.R#L23-L53)).
The help menu of blockr.sandbox comes from blockr.bms through `use_help_nav()` ([R/navbar-help.R#L18-L22](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/d4df2e479564d463d267776563929f27cd4bf9a4/R/navbar-help.R#L18-L22)), and its links come from the blockr options `docs_url` and `issues_url` ([dev/cedx/_boot.R#L147-L155](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/d4df2e479564d463d267776563929f27cd4bf9a4/dev/cedx/_boot.R#L147-L155)).
Today's dock has no undo.
No code in blockr.session or blockr.sandbox, and no example of blockr.dock, drops or reorders a default item.
The code of blockr.bms is not in blockr.sandbox's repo, so it was not checked.

| Today | Where it goes |
|---|---|
| The logo | The dock's logo, which turns while R evaluates a block that the dock demands, and no longer while R makes the output of a block that reads `ready`, whose renderer shows that wait on its card (Proposal) |
| The dock's Import and Export | The controls of core's storage plugin, Save and Open, which the dock draws in their place ([Plugins](Rewrite-1.1.12#storage)) |
| The workflow name, save status and save menu of blockr.session | The controls of blockr.session's storage plugin, which the dock draws in the same place ([Session management as a client extension](Rewrite-1.6)) |
| The spacer and `fill` | Dropped, since the free space falls between the bar's two ends |
| The views menu, with its rule and its tab line | The dock's views menu, which lists the folders of [The dock's state](Rewrite-1.2.1) too |
| The read-only pill | The dock's read-only pill |
| The options button | The dock's options button |
| The field for the `board_name` board option in the options sidebar ([R/dock-board.R#L233-L245](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-board.R#L233-L245)) | The board's name on the bar, after the logo, which a click renames, since the board's name takes the place of that board option ([Defining a board in R](Rewrite-1.1.3#the-script)) |
| An item's `shrink` | Dropped as a setting, since the storage plugin's controls give way first, as the `preserve_board` plugin's piece does today |
| An item whose output renders nothing takes no room | Carried over for every part of the bar |
| An item's `server`, which runs once per session | Dropped, since nothing on the bar runs in R |
| The avatar of blockr.session | A status among the controls of blockr.session's storage plugin, with the visitor's initials, which the plugin gives only for a visitor who is signed in, and which asks for the end of the bar, so that it keeps its place after the options button ([Session management as a client extension](Rewrite-1.6)) |
| The help menu of blockr.bms | Dropped for now, since no plugin adds to the bar, while a help menu of the dock's own is on the [Backlog](Backlog#a-help-menu-in-the-docks-navbar) |
| The functions `navbar_item()`, `default_navbar_items()`, `blockr_app_navbar()`, `custom_navbar()` and `plugin_navbar_item()`, the `navbar_items` collection and the `navbar` of `serve()` | Dropped (Proposal) |

## Proposal

### What the bar holds

The bar is a component of the dock's frontend module, and no plugin adds to it.
It holds, from left to right:

1. The logo.
2. The board's name.
3. The controls of the app's storage plugin.
4. Undo and Redo.
5. The views menu, followed by a short rule.
6. The read-only pill.
7. The options button.
8. The controls of the storage plugin that ask for the end of the bar.

The first four sit at the left end and the rest at the right end, with the free space between them, so today's spacer goes.
An app changes the bar only through the storage plugin it runs, since `serve()` takes no `navbar` ([Defining a board in R](Rewrite-1.1.3#the-serve-generic)) and no plugin adds to the bar.
So the bar of an app without a storage plugin holds the dock's own parts alone.
A help menu of the dock's own, from the blockr options `docs_url` and `issues_url`, may join them later, and nothing here rules it out ([Backlog](Backlog#a-help-menu-in-the-docks-navbar)).
A part with nothing to show draws nothing and takes no room, as the read-only pill does without the board lock and the storage plugin's place does in an app without one (condition 5).

A plugin that needs a place on the screen gets a panel, as every plugin with a `ui` does ([Plugins](Rewrite-1.1.12#plugin-classes)).
So does the deck composer of blockr.topline, for which [blockr.dock#128](https://github.com/BristolMyersSquibb/blockr.dock/issues/128) asks a slot on the navbar.

### The storage plugin's controls

The dock draws the controls that `core.plugins.storage()` gives right after the board's name, in the storage plugin's order, with its own components ([Plugins](Rewrite-1.1.12#storage)).
It draws those that ask for the end of the bar with `placement: "end"` after the options button instead, in the same order.
It ignores hints inside a menu, and draws a control with a hint it does not know as if the control had none.
Each kind looks as follows:

- A button is a quiet 30px button with its label, greyed out while it is `disabled`, with its tooltip where it has one.
- A menu is a quiet 30px button with its label and blockr.ui's chevron, which opens a menu of blockr.ui that holds its items, and a menu among those opens beside it.
- A status is text in the muted color, with its tooltip where it has one.

They follow blockr.ui's design system for the bar, as the dock's own parts do: 30px controls, tokens only, no field labels, and menus from blockr.ui, as [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) settled.
The dock calls `controls()` as it draws the bar, and again whenever the storage plugin's `subscribe()` calls back.
It binds the `shortcut` of every button among the controls, those in menus included.
Where a `run()` rejects, the dock shows the error as a toast, as it shows every notification that is not a block's ([Client-drawn dock](Rewrite-1.2#proposal)).
The dock draws the controls the same way under every lock, since the storage plugin leaves out what a lock fixes itself (condition 6).

So core's storage plugin shows two buttons, Save and Open, where Import and Export are today.
Save saves a download and Open opens an upload, as Export and Import do, and Save stays on a locked board, as Export does today ([R/board-plugins.R#L10-L15](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/board-plugins.R#L10-L15)).
The storage plugin of blockr.session shows its menu named after the workflow, its save status and its Save menu in the same place, as [Session management as a client extension](Rewrite-1.6) has them.
For a visitor who is signed in, it shows a status with the visitor's initials after the options button, which it asks for with `placement: "end"`, where today's avatar sits.
What a storage plugin draws in a dialog of its own, such as blockr.session's sharing settings, the dock does not place.

### A narrow bar

On a narrow bar, the board's name and the storage plugin's controls give way first, and the dock's other parts keep their width, so the bar stays on one line, as today.
They give way by cutting their labels short, the board's name among them.
A label cut short shows in full as the control's tooltip where the control has no tooltip of its own, as blockr.session's workflow name does today ([blockr.session#136](https://github.com/BristolMyersSquibb/blockr.session/issues/136)).
So no part of the bar has a `shrink` of its own.

### The dock's own parts

The logo leads the bar and is the busy indicator, as today.
It is busy while a block that the dock demands reads `stale` or `unevaluated`.
It reads those statuses from `scheduler.status()`, and reads them again whenever `scheduler.subscribe()` names blocks whose status changed ([Evaluation in the client](Rewrite-1.1.10#statuses)).
So it turns while R evaluates what the user looks at, as today's logo turns while an output on screen recalculates.
It starts to turn only after the delay that the blockr option `spinner_delay_ms` gives, 200 ms by default, so a short evaluation never shows.
It reads that blockr option with `core.blockrOption()`.
Its squares fade and fill in the order in which they draw the letter R, more slowly under reduced motion, and its tooltip says "Computing" while it turns, as today.
It does not turn while R makes the output of a block that reads `ready`, such as a plot drawn again at a new size.
The renderer shows that wait on the block's card through the `loading()` of its host, since core keeps the last output drawn while the next one loads ([UI modules in JS](Rewrite-1.1.7#the-contract)).
Whether the logo should turn for outputs too is left to how the bar feels in use, and a member of `CoreApi` that says which outputs R is making would let it, which nothing here rules out ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).

The board's name follows the logo, as core's basic frontend shows it at the head of its toolbar ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
A click on it turns it into a field, which runs core's command `blockr.core-rename_board` with the name the user gives, as that toolbar's Rename does ([Board updates](Rewrite-1.1.2#commands)).
Under the board lock it shows the name alone, as core's basic frontend leaves out Rename under that lock ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).
The board's name takes the place of the `board_name` board option, so the options sidebar holds no field for it any more ([Defining a board in R](Rewrite-1.1.3#the-script)).
With blockr.session's storage plugin, the bar shows the board's name beside the workflows menu, which names the record that is open, and how the two fit together is [Session management as a client extension](Rewrite-1.6#open-questions)'s to settle.

Undo and Redo are two quiet icon buttons right after the storage plugin's controls, which run `core.store.undo()` and `core.store.redo()`, as the toolbar of core's basic frontend does ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
Each is greyed out while `canUndo()` or `canRedo()` of the store says there is nothing to take back, and its tooltip names its shortcut ([Board updates](Rewrite-1.1.2#undo)).
The dock binds the shortcuts as core's basic frontend binds them: Mod+Z undoes, and Mod+Shift+Z or Mod+Y redoes, with Mod either Ctrl or Cmd, while in a text field the shortcuts stay the field's own.
Switching views or tabs takes no undo step, so Undo takes back the last edit rather than a switch ([The dock's state](Rewrite-1.2.1#commands)).
Both stay under the board lock, since what that lock leaves open, such as a block's state, still takes undo steps ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).
Where the store refuses a step, the dock shows the error as a toast, as it shows every notification that is not a block's.

The views menu lists the views and folders of the navigation, each in the order that its `index` gives within its folder ([The dock's state](Rewrite-1.2.1#views-and-folders)).
A folder opens and closes in the menu, and which folders are open stays on the screen, as that page has it.
Choosing a view runs `blockr.dock-activate_view`, under every lock.
On a board without the board lock, the menu also adds, renames, moves and removes views and folders, through the dock's commands for them ([The dock's state](Rewrite-1.2.1#commands)), as today's views menu adds, renames, reorders and removes views ([R/dock-view.R#L602-L675](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-view.R#L602-L675)).
A short rule sets it apart from the parts after it.
While the `view_tabs` board option is on, the views menu draws a line of tabs under the bar, followed by the menu as a chevron alone, as today.
The line holds a tab for each view and folder at the top of the navigation, and a folder's tab opens a menu of what the folder holds, so that the line stays one row however deep the folders go.

The read-only pill shows while `core.lock.board` says that the board lock is on.
It keeps today's label, "Read-only", and today's tooltip, "Editing is disabled by this deployment." ([R/dock-navbar.R#L463-L480](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-navbar.R#L463-L480)).

The options button opens the dock's options sidebar, as today.
The sidebar mounts the UI of each board option with `mountOption()` ([Client-drawn dock](Rewrite-1.2#today)).

### App scripts from today

The navbar's functions go from blockr.dock: `navbar_item()`, `is_navbar_item()`, the `navbar_items` collection with `is_navbar_items()` and its methods for `c()`, `[`, `[[` and `names()`, `default_navbar_items()`, `blockr_app_navbar()`, `custom_navbar()` and `plugin_navbar_item()`.
Nothing in R draws UI any more ([Drawing the board](Rewrite-1.1.8#what-goes-from-r)), and `serve()` refuses `navbar` with an error that says where it went ([Defining a board in R](Rewrite-1.1.3#the-serve-generic)).
The function `avatar_navbar_item()` goes from blockr.session too.

The migration notes of blockr.dock and blockr.session list what a script changes ([Saved boards and app scripts across the switch](Rewrite-1.2.2#app-scripts)):

- A script that passes `navbar = custom_navbar(avatar_navbar_item())` drops the argument, since the avatar is one of the controls of blockr.session's storage plugin, which runs by default wherever blockr.session is installed ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)).
- A script that passes items of its own drops them, since nothing adds to the bar.
  What such an item showed moves into the `ui` of a plugin class in a package, which the dock places in a panel, since an app script defines no plugin class ([Plugins](Rewrite-1.1.12#a-plugin)).
- A script that calls `use_help_nav()` of blockr.sandbox drops the call, and its deployment has no help menu on the bar until the dock gets one of its own ([Backlog](Backlog#a-help-menu-in-the-docks-navbar)).

### Testing

The dock's tests draw the bar on the `CoreApi` for tests, which needs neither R nor a browser ([Plugins](Rewrite-1.1.12#testing)).
A test registers a storage plugin class whose controls hold every kind, a menu inside a menu among them, through `core.plugins.register()`.
It checks how the dock draws each kind, that a control that asks for the end of the bar goes after the options button, that a hint inside a menu changes nothing, that it draws them again as `subscribe()` calls back, that it binds each `shortcut`, that a `run()` that rejects shows as a toast, and that the controls give way first on a narrow bar.
It also checks that a click on the board's name renames the board but not under the board lock, that Undo and Redo follow the store's history and run on their shortcuts but not in a text field, and what each of the dock's own parts shows under each lock and without a storage plugin.

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's code, at `655e323`: the items and the collection are in `R/dock-navbar.R`, tested in `tests/testthat/test-dock-navbar.R` and `tests/testthat/test-board-ui.R`.
The bar's styles are the navbar section of `inst/assets/css/blockr-dock.css` ([#L525-L647](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L525-L647)), with the tab line's ([#L940-L1022](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L940-L1022)) and the logo's ([#L1213-L1297](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L1213-L1297)).
The busy logo's script is `inst/assets/js/navbar-logo.js`, the views menu is `view_nav_ui()` and `view_tabs_ui()` in `R/dock-view.R`, Import and Export are `ser_deser_ui()` in `R/plugin-serdes.R`, and the example `inst/examples/navbar/app.R` goes with `custom_navbar()`.

Today's CSS takes an empty item out of flow rather than hiding it, since Shiny suspends an output that has no box and then never renders what would show the item ([inst/assets/css/blockr-dock.css#L557-L567](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L557-L567)).
No Shiny output is left on the bar, so a part with nothing to show renders nothing, and no rule is needed for an empty box.

The logo's animation carries over from today's CSS, driven by a class that the logo sets from the statuses rather than from Shiny's busy and output events.
Today's script sets a class on the logo rather than have a `:has()` selector read the page, which restyled a page of 21,000 elements on every output update ([blockr.dock#565](https://github.com/BristolMyersSquibb/blockr.dock/issues/565)).
The logo likewise sets the class on its own element.
Today's `spinner_delay_ms()` takes 200 ms where the blockr option is not a whole number of at least 0 ([R/board-ui.R#L113-L118](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/board-ui.R#L113-L118)), and the logo does the same.

The bar's parts are components of the dock's frontend module, so the logo reads which blocks the dock demands, and the options button opens the dock's options sidebar, from the dock's own state.

The dock keys a control by its `id` within its list.
Where two controls of one list share an id, the dock keeps the first and logs the second through `core.log()`.
Where `controls()` throws, the dock draws a warning icon in the storage plugin's place, whose tooltip names the plugin's package, and logs the error, so that the rest of the bar works, as core leaves an error in the element of a module that fails ([UI modules in JS](Rewrite-1.1.7#the-contract)).

Two issues of [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) are still open: spacing the avatar 4px from the options button ([blockr.session#141](https://github.com/BristolMyersSquibb/blockr.session/issues/141)), and the design spec's navbar section, which still draws blockr.session's pieces as the navbar's own ([blockr.ui#91](https://github.com/BristolMyersSquibb/blockr.ui/issues/91)).

</details>
