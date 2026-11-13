# The dock's navbar
Status: settled on 2026-11-12. Design for [Client-drawn dock](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock](Rewrite-1.2)): the bar across the top of the dock.
It covers the navbar items that the bar holds and their order, which an app script gives `serve()`, what gives way on a narrow bar, the dock's own parts of the bar, a module on the bar, and how the dock draws the controls of the app's storage plugin.
It also covers what becomes of the navbar's functions in R, which [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) settled.
The bar is the dock's, and the app script composes it: by default it holds the dock's own parts and the controls of the app's storage plugin, and a script adds links, menus and modules that packages offer, while no plugin puts anything there by itself.
It shapes taking the bar's navbar items in R ([blockr.dock#576](https://github.com/BristolMyersSquibb/blockr.dock/issues/576)), drawing the bar ([blockr.dock#581](https://github.com/BristolMyersSquibb/blockr.dock/issues/581)) and its views menu ([blockr.dock#582](https://github.com/BristolMyersSquibb/blockr.dock/issues/582)), and the migration notes for dock app scripts ([blockr.dock#585](https://github.com/BristolMyersSquibb/blockr.dock/issues/585)).
It builds on [Plugins](Rewrite-1.1.12#the-frontend), whose `frontend_args()` hands the dock what a script gives `serve()` and whose storage controls the bar draws, and on [Drawing the board](Rewrite-1.1.8#what-core-gives-plugins), whose `CoreApi` the bar works through.
The views and folders that the views menu lists, with the commands that change them, are [The dock's state](Rewrite-1.2.1)'s, and which controls blockr.session's storage plugin gives is [Session management as a storage plugin](Rewrite-1.6)'s.

## What must hold

Condition 4 of [Client-drawn dock](Rewrite-1.2#what-must-hold) rests on this page for what today's navbar does, and condition 10 of [Plugins](Rewrite-1.1.12#what-must-hold) for the dock's part in drawing the storage plugin's controls.

1. The bar holds the navbar items that the app script gives `serve()` in `navbar`, in their order, and no board or file holds them, so every board that the app opens shows the same bar.
   No plugin puts anything on it by itself.
2. By default it holds what today's default bar holds, in today's order: the logo as busy indicator, the controls of the app's storage plugin where the `preserve_board` plugin's piece is, the views menu with its tab line, the read-only pill and the options button.
   Two parts join them, the board's name after the logo and Undo and Redo after the storage plugin's controls.
3. A script does with `navbar` what it does with today's navbar items: it adds items of its own, drops or reorders the dock's own parts by their ids, and places one of the storage plugin's controls apart, as blockr.session's avatar goes after the options button.
4. The dock draws every kind of control that a storage plugin gives, in its own look, so that the controls of core's storage plugin, of blockr.session's and of one from a package the dock does not know all look like the rest of the bar.
5. On a narrow bar, the board's name and the storage plugin's controls give way first, and the other navbar items keep their width and stay on one line, as condition 4 of [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) asks.
6. A navbar item with nothing to show takes no room, as the read-only pill on a board without the board lock, or the storage plugin's controls in an app without one.
7. The dock's own parts draw no control for what a lock fixes ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).
   Under the board lock, the board's name only shows, the views menu only switches views, the read-only pill shows, and Undo and Redo stay, since what that lock leaves open still takes undo steps.
   The storage plugin's controls leave out what a lock fixes themselves, such as opening another board under the load lock ([Plugins](Rewrite-1.1.12#storage)).
8. A navbar item that the dock cannot draw, such as a part whose id it does not know or a module that no available package offers, fails as the app starts, naming the item, and a module that fails in the page leaves the rest of the bar working.

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
The help menu of the clinical data explorer comes from blockr.bms, an internal package, through `use_help_nav()`, and its links come from the blockr options `docs_url` and `issues_url`.
Today's dock has no undo.
No code in blockr.session or blockr.sandbox, and no example of blockr.dock, drops or reorders a default item.
The code of blockr.bms is not in blockr.sandbox's repo, so it was not checked.

| Today | Where it goes |
|---|---|
| The logo | The dock's logo, which turns while R evaluates a block that the dock demands, and no longer while R makes the output of a block that reads `ready`, whose renderer shows that wait on its card (Proposal) |
| The dock's Import and Export | The controls of core's storage plugin, Save and Open, which the dock draws in their place ([Plugins](Rewrite-1.1.12#storage)) |
| The workflow name, save status and save menu of blockr.session | The controls of blockr.session's storage plugin, which the dock draws in the same place ([Session management as a storage plugin](Rewrite-1.6)) |
| The spacer and `fill` | The spacer, a navbar item that takes the free space, while `fill` goes, since only the spacer fills |
| The views menu, with its rule and its tab line | The dock's views menu, which lists the folders of [The dock's state](Rewrite-1.2.1) too |
| The read-only pill | The dock's read-only pill |
| The options button | The dock's options button |
| The field for the `board_name` board option in the options sidebar ([R/dock-board.R#L233-L245](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-board.R#L233-L245)) | The board's name on the bar, after the logo, which a click renames where the app keeps the `name` item, since the board's name takes the place of that board option ([Defining a board in R](Rewrite-1.1.3#the-script)) |
| An item's `shrink` | Dropped as a setting, since the storage plugin's controls give way first, as the `preserve_board` plugin's piece does today |
| An item whose output renders nothing takes no room | Carried over for every navbar item |
| An item's `server`, which runs once per session | Dropped, since nothing on the bar runs in R, while a module that needs R calls the requests of a plugin class of its package (Proposal) |
| The avatar of blockr.session | A status among the controls of blockr.session's storage plugin, with the visitor's initials, which the plugin gives only for a visitor who is signed in, and which `avatar_navbar_item()` places after the options button where a script appends that item, as today ([Session management as a storage plugin](Rewrite-1.6)) |
| The help menu of blockr.bms | A menu of links among the script's navbar items, which blockr.bms can give, with its links from the blockr options `docs_url` and `issues_url` |
| The functions `navbar_item()`, `default_navbar_items()`, `blockr_app_navbar()`, `custom_navbar()` and `plugin_navbar_item()`, the `navbar_items` collection and the `navbar` of `serve()` | The collection, `navbar_item()` with a module in place of `ui` and `server`, `custom_navbar()`, which gains `drop`, and the `navbar` of `serve()`, which `serve()` hands the dock, while `default_navbar()` takes the place of `default_navbar_items()`, and `blockr_app_navbar()` and `plugin_navbar_item()` go (Proposal) |

## Proposal

### What the bar holds

The bar is a component of the dock's frontend module, which draws in one row the navbar items that the app script gives `serve()` in `navbar`, in their order.
The `serve()` generic hands `navbar` to the dock's method of `frontend_args()`, which checks every item as the app starts and returns the items as JSON, and the reply to `hello` carries them to the dock outside the board ([Plugins](Rewrite-1.1.12#the-frontend)).
So no board or file holds the bar, and every board that the app opens shows the same one, as today's `navbar` is the app's and not the board's.

By default, `navbar` holds `default_navbar()`, which gives the dock's own parts and the storage plugin's controls, from left to right, each under its id:

1. The logo, `logo`.
2. The board's name, `name`.
3. The controls of the app's storage plugin, `storage`.
4. Undo and Redo, `undo_redo`.
5. The spacer, `spacer`, which takes the free space, so that what follows sits at the right end.
6. The views menu, `views`, followed by a short rule.
7. The read-only pill, `read_only`.
8. The options button, `options`.

Besides the dock's own parts, a navbar item is one of these, each made by a function of blockr.dock and each with an id of its own:

```r
navbar_link(id, label, href)      # a link, which opens in a new tab
navbar_menu(id, label, ...)       # a menu of links and further menus
navbar_storage(id)                # one of the storage plugin's controls, by its id, apart from the rest
navbar_item(id, module)           # a module that a package offers, by its id, which draws the item where today's takes ui and server
```

The dock draws links and menus with its own components, as it draws its own parts, so that they look like the rest of the bar.
The `storage` item draws every control of the storage plugin that no `navbar_storage()` item places elsewhere.
Items combine with `c()`, `[` reorders or drops them by id and `[[` extracts one, as today, and `custom_navbar(items, drop)` gives `default_navbar()` without the items whose ids `drop` names, with `items` appended, dropping each default item that shares an id with one of them too, as today's does with `items` ([R/dock-navbar.R#L298-L308](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-navbar.R#L298-L308)).
So a script for a Connect deployment with a help menu, whose storage plugin names the workflow, passes:

```r
serve(
  new_dock_board(...),
  navbar = custom_navbar(
    c(
      navbar_menu("help", "Help", navbar_link("issues", "Report an issue", "https://github.com/BristolMyersSquibb/blockr/issues/new")),
      avatar_navbar_item()        # navbar_storage("avatar"), from blockr.session
    ),
    drop = "name"                 # the workflows menu names the workflow
  )
)
```

The dock's `frontend_args()` refuses an item that the dock cannot draw as the app starts, naming it: one whose id another item shares, a part or a kind that the dock does not know, or a module that no available package offers (condition 8).
A navbar item with nothing to show draws nothing and takes no room, as the read-only pill does without the board lock, `storage` in an app without a storage plugin, and `navbar_storage("avatar")` for a visitor who is not signed in (condition 6).

The slide-deck builder of blockr.topline, a private package, for which [blockr.dock#128](https://github.com/BristolMyersSquibb/blockr.dock/issues/128) asks a slot on the navbar, gets one as a module that blockr.topline offers and that an app's `navbar` places, so that no other plugin has to draw it.
A plugin's `ui` never goes on the bar, since the dock places it in a panel ([Places the dock offers plugins](Rewrite-1.2.4)).

### A module on the bar

A `navbar_item()` names its module by the id of a module that a package offers, such as `"blockr.topline-deck_button"`, which the dock loads with `core.module()` ([Drawing the board](Rewrite-1.1.8#what-a-package-declares-in-r)).
So every module on the bar comes from a package, which R serves as it serves every package's modules, and an app script that wants a widget of its own on the bar gives it a package.

The module meets the contract of a UI module, with `CoreApi` in place of a host: the dock calls its `render()` with the item's element, `CoreApi` and a signal that it aborts when it takes the bar down, and runs the cleanup that `render()` returns ([UI modules in JS](Rewrite-1.1.7#the-contract)).
Where the module fails to load, declares another `api` major or throws in `render()`, the dock leaves a warning icon in the item's place, whose tooltip names the module, as core leaves an error in the element of a module that fails, and the rest of the bar works (condition 8).
A module may be written in TSX, which its package's build compiles ([UI modules in JS](Rewrite-1.1.7#packaging)).
A module draws itself, so it looks like the rest of the bar only where its author builds it from blockr.ui's components or its tokens, as a plugin's `ui` does in a panel.
It keeps its width on a narrow bar, as the dock's own parts other than the board's name do.
Nothing on the bar runs in R, so a module that needs R calls the requests of a plugin class of its package with `core.request()`, as a button that files an issue through R would ([Plugins](Rewrite-1.1.12#a-plugins-requests)).

### The storage plugin's controls

The dock draws the controls that `core.plugins.storage()` gives where the `storage` item is, right after the board's name by default, in the storage plugin's order, with its own components ([Plugins](Rewrite-1.1.12#storage)).
It draws a control that a `navbar_storage()` item names in that item's place instead.
Such an item names a control at the top of the storage plugin's list, since one inside a menu opens with its menu, and it draws nothing where the plugin gives no control of that id.
Each kind looks as follows:

- A button is a quiet 30px button with its label, greyed out while it is `disabled`, with its tooltip where it has one.
- A menu is a quiet 30px button with its label and blockr.ui's chevron, which opens a menu of blockr.ui that holds its items, and a menu among those opens beside it.
- A status is text in the muted color, with its tooltip where it has one.

They follow blockr.ui's design system for the bar, as the dock's own parts do: 30px controls, tokens only, no field labels, and menus from blockr.ui, as [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) settled.
The dock calls `controls()` as it draws the bar, and again whenever the storage plugin's `subscribe()` calls back.
It binds the `shortcut` of every button among the controls, those in menus included.
Where a `run()` rejects, the dock shows the error as a toast, as it shows every notification that is not a block's ([Client-drawn dock](Rewrite-1.2#proposal)).
The dock draws the controls the same way under every lock, since the storage plugin leaves out what a lock fixes itself (condition 7).

So core's storage plugin shows two buttons, Save and Open, where Import and Export are today.
Save saves a download and Open opens an upload, as Export and Import do, and Save stays on a locked board, as Export does today ([R/board-plugins.R#L10-L15](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/board-plugins.R#L10-L15)).
The storage plugin of blockr.session shows its menu named after the workflow, its save status and its Save menu in the same place, as [Session management as a storage plugin](Rewrite-1.6) has them.
For a visitor who is signed in, it gives a status with the visitor's initials, which `avatar_navbar_item()` places after the options button, where today's avatar sits, and which shows among its other controls where an app's `navbar` places it nowhere apart.
What a storage plugin draws in a dialog of its own, such as blockr.session's sharing settings, the dock does not place.

### A narrow bar

On a narrow bar, the board's name and the storage plugin's controls give way first, and the other navbar items keep their width, so the bar stays on one line, as today.
They give way by cutting their labels short, the board's name among them.
A label cut short shows in full as the control's tooltip where the control has no tooltip of its own, as blockr.session's workflow name does today ([blockr.session#136](https://github.com/BristolMyersSquibb/blockr.session/issues/136)).
So no navbar item has a `shrink` of its own.

### The dock's own parts

The logo leads the default bar and is the busy indicator, as today.
It is busy while a block that the dock demands reads `stale` or `unevaluated`.
It reads those statuses from `scheduler.status()`, and reads them again whenever `scheduler.subscribe()` names blocks whose status changed ([Evaluation in the client](Rewrite-1.1.10#statuses)).
So it turns while R evaluates what the user looks at, as today's logo turns while an output on screen recalculates.
It starts to turn only after the delay that the blockr option `spinner_delay_ms` gives, 200 ms by default, so a short evaluation never shows.
It reads that blockr option with `core.blockrOption()`.
Its squares fade and fill in the order in which they draw the letter R, more slowly under reduced motion, and its tooltip says "Computing" while it turns, as today.
It does not turn while R makes the output of a block that reads `ready`, such as a plot drawn again at a new size.
The renderer shows that wait on the block's card through the `loading()` of its host, since core keeps the last output drawn while the next one loads ([UI modules in JS](Rewrite-1.1.7#the-contract)).
Whether the logo should turn for outputs too is left to how the bar feels in use, and a member of `CoreApi` that says which outputs R is making would let it, which nothing here rules out ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).

The board's name follows the logo in the default bar, as core's basic frontend shows it at the head of its toolbar ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
A click on it turns it into a field, which runs core's command `blockr.core-rename_board` with the name the user gives, as that toolbar's Rename does ([Board updates](Rewrite-1.1.2#commands)).
Under the board lock it shows the name alone, as core's basic frontend leaves out Rename under that lock ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).
The board's name takes the place of the `board_name` board option, so the options sidebar holds no field for it any more ([Defining a board in R](Rewrite-1.1.3#the-script)).
Whether the name matters depends on the storage plugin, since none keys its records on the name, which a rename changes at any time ([Plugins](Rewrite-1.1.12#storage)).
With core's storage plugin, it is the one name that a board has on the bar, while blockr.session's storage plugin names a workflow by a key of its own, which its workflows menu shows ([Session management as a storage plugin](Rewrite-1.6)).
So the name is a navbar item that an app keeps or leaves out, and an app with blockr.session's storage plugin passes `drop = "name"` to `custom_navbar()`, so that its bar shows one name, the workflow's.

Undo and Redo are two quiet icon buttons, right after the storage plugin's controls in the default bar, which run `core.store.undo()` and `core.store.redo()`, as the toolbar of core's basic frontend does ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
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

Of the navbar's functions in blockr.dock, `navbar_item()` stays, with a module in place of its `ui` and `server` and without `fill` and `shrink`, and so do `is_navbar_item()`, the `navbar_items` collection with `is_navbar_items()` and its methods for `c()`, `[`, `[[` and `names()`, and `custom_navbar()`, which returns the items rather than a function of the board and its plugins, and which takes in `drop` the ids of default items to leave out.
The function `default_navbar()` takes the place of `default_navbar_items()`, which took the board and its plugins, since the default depends on neither, while `blockr_app_navbar()` and `plugin_navbar_item()` go, since no board class picks the bar and no plugin's `ui` goes on it.
The `serve()` generic hands its `navbar` to the dock ([Defining a board in R](Rewrite-1.1.3#the-serve-generic)), which takes the items themselves, since nothing in R draws UI any more ([Drawing the board](Rewrite-1.1.8#what-goes-from-r)).
The function `avatar_navbar_item()` of blockr.session stays, and returns `navbar_storage("avatar")`.

The migration notes of blockr.dock and blockr.session list what a script changes ([Saved boards and app scripts across the switch](Rewrite-1.2.2#app-scripts)):

- A script that passes `navbar = custom_navbar(avatar_navbar_item())` keeps it, adding `drop = "name"` so that the bar shows the workflow's name alone, while one that leaves `navbar` out shows the avatar among the other controls of blockr.session's storage plugin, beside the board's name.
- A script that passes items of its own gives each a link or a menu where the item showed links, and otherwise a module that a package offers, in place of its `ui` and `server`.
  Where the item needs R, that package gives a plugin class whose requests the module calls, since an app script defines no plugin class ([Plugins](Rewrite-1.1.12#a-plugin)).
- A script that passes a function of its own as `navbar` passes the items that the function returns, since `navbar` takes items, with `default_navbar()` in place of `default_navbar_items(board, plugins)`.
- A script that calls `use_help_nav()` of blockr.sandbox passes the help menu among its navbar items instead, as a menu of links that blockr.bms gives.

### Testing

The dock's tests draw the bar on the `CoreApi` for tests, which needs neither R nor a browser ([Plugins](Rewrite-1.1.12#testing)), from the items that its `frontend_args()` returns.
A test registers a storage plugin class whose controls hold every kind, a menu inside a menu among them, through `core.plugins.register()`.
It checks how the dock draws each kind, that a `navbar_storage()` item places its control apart while `storage` draws the rest, that it draws them again as `subscribe()` calls back, that it binds each `shortcut`, that a `run()` that rejects shows as a toast, and that the controls give way first on a narrow bar.
It checks too that the dock draws links and menus, mounts a module and takes it down through its signal, and leaves a warning in the place of a module that fails to load, declares another major or throws, while the rest of the bar works.
It also checks that a click on the board's name renames the board but not under the board lock, that Undo and Redo follow the store's history and run on their shortcuts but not in a text field, and what each of the dock's own parts shows under each lock and without a storage plugin.
The R tests check that `serve()` hands `navbar` to the dock's `frontend_args()`, which gives `default_navbar()` where a script passes none, that `custom_navbar()` drops what `drop` names, and that the method refuses an item that the dock cannot draw, naming it, a module that no available package offers among them.

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's code, at `655e323`: the items and the collection are in `R/dock-navbar.R`, tested in `tests/testthat/test-dock-navbar.R` and `tests/testthat/test-board-ui.R`.
The bar's styles are the navbar section of `inst/assets/css/blockr-dock.css` ([#L525-L647](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L525-L647)), with the tab line's ([#L940-L1022](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L940-L1022)) and the logo's ([#L1213-L1297](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L1213-L1297)).
The busy logo's script is `inst/assets/js/navbar-logo.js`, the views menu is `view_nav_ui()` and `view_tabs_ui()` in `R/dock-view.R`, Import and Export are `ser_deser_ui()` in `R/plugin-serdes.R`, and the example `inst/examples/navbar/app.R` shows `custom_navbar()`, as it goes on doing with items of the new kinds.

Today's CSS takes an empty item out of flow rather than hiding it, since Shiny suspends an output that has no box and then never renders what would show the item ([inst/assets/css/blockr-dock.css#L557-L567](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L557-L567)).
No Shiny output is left on the bar, so a part with nothing to show renders nothing, and no rule is needed for an empty box.

The logo's animation carries over from today's CSS, driven by a class that the logo sets from the statuses rather than from Shiny's busy and output events.
Today's script sets a class on the logo rather than have a `:has()` selector read the page, which restyled a page of 21,000 elements on every output update ([blockr.dock#565](https://github.com/BristolMyersSquibb/blockr.dock/issues/565)).
The logo likewise sets the class on its own element.
Today's `spinner_delay_ms()` takes 200 ms where the blockr option is not a whole number of at least 0 ([R/board-ui.R#L113-L118](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/board-ui.R#L113-L118)), and the logo does the same.

Today's checks of an item and of the collection, `validate_navbar_item()` and `validate_navbar_items()`, carry over into the dock's `frontend_args()`, with a module's checks in place of those of `ui` and `server` ([R/dock-navbar.R#L85-L166](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-navbar.R#L85-L166)).

The bar's parts are components of the dock's frontend module, so the logo reads which blocks the dock demands, and the options button opens the dock's options sidebar, from the dock's own state.

The dock keys a control by its `id` within its list.
Where two controls of one list share an id, the dock keeps the first and logs the second through `core.log()`.
Where `controls()` throws, the dock draws a warning icon in the storage plugin's place, whose tooltip names the plugin's package, and logs the error, so that the rest of the bar works, as core leaves an error in the element of a module that fails ([UI modules in JS](Rewrite-1.1.7#the-contract)).

Two issues of [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) are still open: spacing the avatar 4px from the options button ([blockr.session#141](https://github.com/BristolMyersSquibb/blockr.session/issues/141)), and the design spec's navbar section, which still draws blockr.session's pieces as the navbar's own ([blockr.ui#91](https://github.com/BristolMyersSquibb/blockr.ui/issues/91)).

</details>
