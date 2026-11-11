# The dock's navbar
Status: draft. Design for [Client-drawn dock](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock](Rewrite-1.2)): the bar across the top of the dock.
It covers the items on the bar and their order, what gives way on a narrow bar, the dock's own items, and the items that plugins add through the dock's member `dockNavbar` ([Plugins](Rewrite-1.1.12#plugin-classes)), as blockr.session adds its avatar.
It also covers what becomes of the navbar's functions in R, which [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) settled.
It shapes two items of the Work of [Client-drawn dock](Rewrite-1.2#work): offering plugins the dock's places, and writing the migration notes for dock app scripts.
It builds on [Plugins](Rewrite-1.1.12#plugin-classes), whose contract for a plugin's module every item meets, and on [Drawing the board](Rewrite-1.1.8#what-core-gives-plugins), whose `CoreApi` every item works through.
What the dock's places share is [Places the dock offers plugins](Rewrite-1.2.4)'s, and the views that the views item lists, with the commands that change them, are [The dock's state](Rewrite-1.2.1)'s.

## What must hold

Condition 3 of [Client-drawn dock](Rewrite-1.2#what-must-hold) rests on this page for navbar items, with [Places the dock offers plugins](Rewrite-1.2.4), and condition 4 for what today's navbar does.

1. Every item on the bar comes from the `dockNavbar` of a plugin that runs, and the dock's own items come from the dock plugin's class.
   So a plugin adds an item through its class alone, and the item works through `CoreApi` alone, with no R code and no markup of the dock's.
2. The dock's own items are today's, in today's order: the logo as busy indicator, the save and open controls in place of the `preserve_board` plugin's piece, the views item with its tab line, the read-only pill and the options button.
3. Every other plugin's item goes after the dock's own items, at the end of the bar that the item names, and the free space falls between the two ends.
4. On a narrow bar, the items that may shrink give way first, and the rest keep their width and stay on one line, as condition 4 of [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) asks.
5. An item whose module draws nothing takes no room, so blockr.session's avatar leaves no gap for a visitor who is not signed in.
6. The bar draws no control for what a lock fixes ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).
   Under the board lock, the views item only switches views, and the read-only pill shows.
   Under the load lock, the bar has no open control.

## Today

At `655e323`, blockr.dock draws the navbar from a list of navbar items, each made by `navbar_item(id, ui, server, fill, shrink)` ([R/dock-navbar.R#L67-L74](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-navbar.R#L67-L74)).
It draws them in one row, 48px high, in the order of the list.
An item with `fill` takes the free space, an item with `shrink` gives way first on a narrow bar, and the others keep their width ([inst/assets/css/blockr-dock.css#L538-L567](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L538-L567)).
An item whose `ui` returns `NULL` is left out, and an item whose only output renders nothing takes no room.

The default items of `default_navbar_items()` are, in order ([R/dock-navbar.R#L264-L283](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-navbar.R#L264-L283)):

1. The logo, which is the busy indicator ([blockr.dock#530](https://github.com/BristolMyersSquibb/blockr.dock/issues/530)).
2. The piece of the `preserve_board` plugin, which shrinks.
   It is the dock's Import and Export, one row of quiet 30px buttons ([R/plugin-serdes.R#L9-L28](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-serdes.R#L9-L28)), or blockr.session's workflow name, save status and save menu ([blockr.session R/ui.R#L6-L184](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/ui.R#L6-L184)).
3. A spacer, which fills.
4. The views menu, with a short rule after it, which draws the views as a line of tabs under the bar while the `view_tabs` board option is on ([blockr.dock#555](https://github.com/BristolMyersSquibb/blockr.dock/issues/555)).
5. The read-only pill, only on a locked board.
6. The options button, which opens the options sidebar.

An app changes the bar through `serve(navbar = f)`, where `f` is a function of the board and its plugins that returns the items.
The function that `custom_navbar(items)` returns appends `items` to the default items, and drops each default item that shares an id with one of them ([R/dock-navbar.R#L298-L308](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-navbar.R#L298-L308)).
An app's own function can also reorder or drop items by id with `[`.
Two packages add items, and both append them.
The avatar of blockr.session, `avatar_navbar_item()`, shows the initials of `session$user`, and draws nothing for a visitor who is not signed in ([R/avatar.R#L23-L53](https://github.com/BristolMyersSquibb/blockr.session/blob/66d950549a905066a2860c1d39da1cf6cf320bc8/R/avatar.R#L23-L53)).
The help menu of blockr.sandbox comes from blockr.bms through `use_help_nav()` ([R/navbar-help.R#L18-L22](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/d4df2e479564d463d267776563929f27cd4bf9a4/R/navbar-help.R#L18-L22)), and its links come from the blockr options `docs_url` and `issues_url` ([dev/cedx/_boot.R#L147-L155](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/d4df2e479564d463d267776563929f27cd4bf9a4/dev/cedx/_boot.R#L147-L155)).
No code in blockr.session or blockr.sandbox, and no example of blockr.dock, drops or reorders a default item.
The code of blockr.bms is not in blockr.sandbox's repo, so it was not checked.

| Today | Where it goes |
|---|---|
| The logo | The dock's item `logo` (Proposal) |
| The dock's Import and Export | The dock's save and open controls, Open and Save, which call the app's storage plugin, whichever it is |
| The workflow name, save status and save menu of blockr.session | Its Save, and its switch to another workflow, through the dock's save and open controls, which call its storage plugin, and the rest through the items and the UI of its plugin, as [Session management as a client extension](Rewrite-1.6) settles |
| The spacer and `fill` | Dropped, since the free space falls between the bar's two ends |
| The views menu, with its rule and its tab line | The dock's item `views` |
| The read-only pill | The dock's item `read_only` |
| The options button | The dock's item `options` |
| An item's `shrink` | Carried over as an item's `shrink` |
| An item whose output renders nothing takes no room | Carried over for an item whose module draws nothing |
| An item's `server`, which runs once per session | Dropped, since an item's module runs in the browser and reaches R through its plugin's requests ([Plugins](Rewrite-1.1.12#a-plugins-requests)) |
| The avatar of blockr.session | An item of blockr.session's plugin class |
| The help menu of blockr.bms | An item of a plugin class of blockr.bms |
| The functions `navbar_item()`, `default_navbar_items()`, `blockr_app_navbar()`, `custom_navbar()` and `plugin_navbar_item()`, the `navbar_items` collection and the `navbar` of `serve()` | Dropped (Proposal) |

## Proposal

### Items

A plugin class gives the items of its plugin through `dockNavbar`, a member that blockr.dock declares on core's `PluginClass` and that only the dock reads ([Plugins](Rewrite-1.1.12#plugin-classes)):

```ts
declare module "@blockr/core" {                    // in blockr.dock's types
  interface PluginClass {
    dockNavbar?(plugin: PluginClassId): NavbarItem[];   // the items of the class's plugin, in order
  }
}

interface NavbarItem {
  id: string;                                      // unique among the items of its plugin, such as "avatar"
  module: ModuleId;                                // the module that draws it, which its package offers, such as "blockr.session-avatar"
  side: "left" | "right";                          // the end of the bar that it goes to
  shrink?: boolean;                                // whether it gives way first on a narrow bar, false where left out
}
```

The dock reads `dockNavbar` from the class of each plugin that runs, as it draws the bar for the open board.
So the items follow the plugins that run, and nothing registers an item as a plugin starts.
An item's module meets the contract of a plugin's module: its `render()` gets an element, `CoreApi`, the id of the plugin whose class gives the item, and a signal ([Plugins](Rewrite-1.1.12#plugin-classes)).
The dock loads the module with `core.module()`, gives it an element of its own on the bar, and calls `render()`.
An item stays mounted until the next board opens.
As that board opens, the dock stops, and it aborts the signal of every item and runs its cleanup ([Plugins](Rewrite-1.1.12#running-a-plugin)).
An item renders in a root of its own, as a plugin's `ui` does, and follows blockr.ui's design system for the bar: 30px controls, tokens only, no field labels, and menus from blockr.ui, as [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) settled.

The dock gives its own items through the dock plugin's class, as any plugin gives its items.
So the bar has one list and one set of rules, and a plugin can add what the dock adds ([Client-drawn dock](Rewrite-1.2#proposal)):

```ts
core.plugins.register({                            // blockr.dock's, from its startup module
  id: "blockr.dock-dock_plugin",
  frontend: "blockr.dock-dock",
  dockNavbar: () => [
    { id: "logo", module: "blockr.dock-logo", side: "left" },
    { id: "storage", module: "blockr.dock-storage", side: "left", shrink: true },
    { id: "views", module: "blockr.dock-views", side: "right" },
    { id: "read_only", module: "blockr.dock-read_only", side: "right" },
    { id: "options", module: "blockr.dock-options", side: "right" },
  ],
  // its state, update and migrate, as The dock's state has them
});
```

An item decides for itself whether it shows.
Its module draws nothing where it has nothing to show, and the dock hides the item's element while it is empty, so the item takes no room (condition 5).
The read-only pill is an example:

```ts
export const api = 1;                                // the module blockr.dock-read_only

export default {
  render({ el, core }: { el: HTMLElement; core: CoreApi; plugin: PluginClassId; signal: AbortSignal }) {
    if (core.lock.board) el.append(readOnlyPill());  // nothing without the board lock, so it takes no room
    return () => el.replaceChildren();
  }
};
```

### The order

The bar has two ends, and the free space falls between them.
So no item fills the bar, and today's spacer goes.
The dock builds each end in two steps:

1. It places the dock's own items that name that end, in the order of the dock's `dockNavbar`.
2. It places the items of every other plugin that name that end, plugin by plugin in the order that `core.plugins.running()` lists the plugins, and each plugin's items in the order of its `dockNavbar`.

So blockr.session's avatar goes after the options button, where `custom_navbar()` puts it today.
Whether that order of plugins is the order of the rows that `serve()` takes, and whether an app may drop or reorder items besides, is open (below).
No item goes between two of the dock's own items, since no plugin needs that today.
A later member of `NavbarItem`, such as a rank within its end, could place an item there, and an item that sets no rank would keep its place.

### A narrow bar

An item with `shrink` gives way first on a narrow bar, and the others keep their width, so the bar stays on one line, as today.
Of the dock's own items, only the save and open controls shrink, and they cut their names short, as Import and Export do today.
A plugin sets `shrink` on an item that can cut its text short, such as a name that shows in full in its tooltip, as blockr.session's workflow name does today ([blockr.session#136](https://github.com/BristolMyersSquibb/blockr.session/issues/136)).

### The dock's own items

The logo leads the bar and is the busy indicator, as today.
It is busy while a block that the dock demands reads `stale` or `unevaluated`.
It reads those statuses from `scheduler.status()`, and reads them again whenever `scheduler.subscribe()` names blocks whose status changed ([Evaluation in the client](Rewrite-1.1.10#statuses)).
So it turns while R evaluates what the user looks at, as today's logo turns while an output on screen recalculates.
It starts to turn only after the delay that the blockr option `spinner_delay_ms` gives, 200 ms by default, so a short evaluation never shows.
It reads that blockr option with `core.blockrOption()`.
Its squares fade and fill in the order in which they draw the letter R, more slowly under reduced motion, and its tooltip says "Computing" while it turns, as today.
Whether it also turns while R makes the output of a block that reads `ready` is open (below).

The save and open controls are the dock's own, in place of the `preserve_board` plugin's piece.
They are two quiet 30px buttons, Open and Save, as core's basic frontend names them, since they call whichever storage plugin the app holds ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
Save hands the JSON board that the store writes to the `save()` of `core.plugins.storage()`.
Open passes the text that `open()` resolves with to `store.open()` ([Plugins](Rewrite-1.1.12#storage)).
So with core's storage plugin they save a download and open an upload, as Import and Export do today, and with blockr.session's they save to Connect and open its picker.
The item draws neither control where the app holds no storage plugin, and no Open under the load lock.
Save stays on a locked board, since no lock fixes saving ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).

The views item lists the views and switches between them.
On a board without the board lock, it also adds, renames, reorders and removes views, as today's views menu does ([R/dock-view.R#L602-L675](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-view.R#L602-L675)).
A short rule sets it apart from the items after it.
While the `view_tabs` board option is on, the item draws the views as a line of tabs under the bar, followed by the menu as a chevron alone, as today.

The read-only pill shows while `core.lock.board` says that the board lock is on.
It keeps today's label, "Read-only", and today's tooltip, "Editing is disabled by this deployment." ([R/dock-navbar.R#L463-L480](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-navbar.R#L463-L480)).

The options button opens the dock's options sidebar, as today.
The sidebar mounts the UI of each board option with `mountOption()` ([Client-drawn dock](Rewrite-1.2#today)).

### Items of other plugins

The avatar of blockr.session is an item of its plugin class at the right end, as [Plugins](Rewrite-1.1.12#plugin-classes) sketches it.
Its module draws nothing for a visitor who is not signed in, so the item takes no room then.
The piece that blockr.session draws today splits in two.
Its Save, and its switch to another workflow, go through the dock's save and open controls, which call its storage plugin.
Where its workflow name, its save status and the rest of its save menu go, among the items and the UI of its plugin, is [Session management as a client extension](Rewrite-1.6)'s to settle.

The help menu that blockr.sandbox draws through blockr.bms becomes an item of a plugin class of blockr.bms, at the right end.
Its module reads its links from the blockr options `docs_url` and `issues_url` with `core.blockrOption()`, as today's menu reads them in R.

Any plugin can add an item, so the place that [blockr.dock#128](https://github.com/BristolMyersSquibb/blockr.dock/issues/128) asks for a plugin of class `manage_stacks` needs nothing more.

### App scripts from today

The navbar's functions go from blockr.dock: `navbar_item()`, `is_navbar_item()`, the `navbar_items` collection with `is_navbar_items()` and its methods for `c()`, `[`, `[[` and `names()`, `default_navbar_items()`, `blockr_app_navbar()`, `custom_navbar()` and `plugin_navbar_item()`.
Nothing in R draws UI any more ([Drawing the board](Rewrite-1.1.8#what-goes-from-r)), and `serve()` refuses `navbar` with an error that says where it went ([Defining a board in R](Rewrite-1.1.3#the-serve-generic)).
The function `avatar_navbar_item()` goes from blockr.session too.

The migration notes of blockr.dock and blockr.session list what a script changes ([Saved boards and app scripts across the switch](Rewrite-1.2.2#app-scripts)):

- A script that passes `navbar = custom_navbar(avatar_navbar_item())` drops the argument, since the avatar shows wherever blockr.session's plugin runs, and that plugin runs by default wherever blockr.session is installed.
- A script that passes items of its own moves each of them into a package, as an item of a plugin class there, since an app script defines no plugin class ([Plugins](Rewrite-1.1.12#a-plugin)).

### Testing

The dock's tests draw the bar on the `CoreApi` for tests, which needs neither R nor a browser ([Plugins](Rewrite-1.1.12#testing)).
A test registers plugin classes that give items through `core.plugins.register()`.
It checks the order of the items at each end, what shrinks, that an item whose module draws nothing takes no room, and what each of the dock's own items shows under each lock and without a storage plugin.

## Open questions

- How an app changes the bar, now that `serve()` takes no `navbar` ([Defining a board in R](Rewrite-1.1.3#the-serve-generic)).
  One answer is that an app changes the bar only through the rows that `serve()` takes in `plugins`.
  Which plugins run would decide which items show, and the order of the rows would decide the order of their items at each end.
  Then `core.plugins.running()` would have to keep that order.
  Another is a blockr option that lists the items to show, in order, as `custom_navbar()` and `[` let a script drop and reorder items today.
  It blocks the order of the items of plugins and the migration notes for a script that drops or reorders items.
- Whether the logo also turns while R makes the output of a block that reads `ready`, such as a plot drawn again at a new size, as today's logo turns for every output on screen that recalculates.
  Core asks R for an output inside `mountOutput()` and tells no frontend while it waits, so this needs a member of `CoreApi` that says when R is making an output.
  That member would change [Drawing the board](Rewrite-1.1.8#what-core-gives-plugins).
  Without it, a renderer shows that wait itself, through the `loading()` of its host ([UI modules in JS](Rewrite-1.1.7#the-contract)).
  It blocks the logo's rule.
- Whether the bar gets Undo and Redo buttons, as the toolbar of core's basic frontend has ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
  Today's dock has no undo, and the store gives the dock undo for every edit, arrangement included ([Board updates](Rewrite-1.1.2#undo)).
  It blocks the list of the dock's own items.
- Where a dock user renames the board, now that the board's name takes the place of core's `board_name` board option ([Defining a board in R](Rewrite-1.1.3#the-script)).
  Today's dock shows that board option in its options sidebar ([R/dock-board.R#L233-L245](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-board.R#L233-L245)).
  It may be an item on the bar, as the toolbar of core's basic frontend renames the board, or a row of the dock's own in the options sidebar.
  It blocks the list of the dock's own items.

<details><summary>Notes for implementers</summary>

Today's code, at `655e323`: the items and the collection are in `R/dock-navbar.R`, tested in `tests/testthat/test-dock-navbar.R` and `tests/testthat/test-board-ui.R`.
The bar's styles are the navbar section of `inst/assets/css/blockr-dock.css` ([#L525-L647](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L525-L647)), with the tab line's ([#L940-L1022](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L940-L1022)) and the logo's ([#L1213-L1297](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L1213-L1297)).
The busy logo's script is `inst/assets/js/navbar-logo.js`, the views menu is `view_nav_ui()` and `view_tabs_ui()` in `R/dock-view.R`, Import and Export are `ser_deser_ui()` in `R/plugin-serdes.R`, and the example `inst/examples/navbar/app.R` goes with `custom_navbar()`.

Today's CSS takes an empty item out of flow rather than hiding it, since Shiny suspends an output that has no box and then never renders what would show the item ([inst/assets/css/blockr-dock.css#L557-L567](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L557-L567)).
No Shiny output is left on the bar, so the dock can hide an item's element with `display: none` while it is `:empty`.

The logo's animation carries over from today's CSS, driven by a class that the logo's module sets from the statuses rather than from Shiny's busy and output events.
Today's script sets a class on the logo rather than have a `:has()` selector read the page, which restyled a page of 21,000 elements on every output update ([blockr.dock#565](https://github.com/BristolMyersSquibb/blockr.dock/issues/565)).
The module likewise sets the class on its own element.
Today's `spinner_delay_ms()` takes 200 ms where the blockr option is not a whole number of at least 0 ([R/board-ui.R#L113-L118](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/board-ui.R#L113-L118)), and the module does the same.

The modules of the dock's own items are blockr.dock's, so they share state with the dock's frontend module.
That is how the logo reads which blocks the dock demands, and how the options button opens the dock's options sidebar, neither of which a plugin's item can reach.
A plugin's item opens a menu of its own instead, as blockr.session's menus do today.

The dock keys an item by the class id of its plugin and its own id.
Where two items of one plugin share an id, the dock keeps the first and logs the second through `core.log()`.
Where an item's module fails to load, declares another major of core's API or throws in `render()`, the dock draws a warning icon in the item's place, whose tooltip names the module and its package, and logs the error, so that the rest of the bar works, as core leaves an error in the element of a module that fails ([UI modules in JS](Rewrite-1.1.7#the-contract)).

Two issues of [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) are still open: spacing the avatar 4px from the options button ([blockr.session#141](https://github.com/BristolMyersSquibb/blockr.session/issues/141)), and the design spec's navbar section, which still draws blockr.session's pieces as the navbar's own ([blockr.ui#91](https://github.com/BristolMyersSquibb/blockr.ui/issues/91)).

</details>
