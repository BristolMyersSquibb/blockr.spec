# Places the dock offers plugins
Status: settled on 2026-11-12. Design for [Client-drawn dock](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock](Rewrite-1.2)): the places where the dock puts plugins.
The dock draws what a plugin's class gives every frontend: it mounts a `ui` in a panel and draws in its navbar the controls that a storage plugin's `storage` gives, while the dock is itself the plugin whose `frontend` draws the page ([Plugins](Rewrite-1.1.12#plugin-classes)).
This page covers the panel, how the dock carries out core's `show()`, where a plugin's settings show and where the dock draws board actions, and says why the dock offers plugins no other place, so that it declares no member of its own on core's `PluginClass`.
It builds on [Plugins](Rewrite-1.1.12) and [Drawing the board](Rewrite-1.1.8#what-core-gives-plugins).
It shapes placing every plugin that has a UI in a panel ([blockr.dock#584](https://github.com/BristolMyersSquibb/blockr.dock/issues/584)), the options sidebar ([blockr.dock#583](https://github.com/BristolMyersSquibb/blockr.dock/issues/583)), the vignette on how a plugin uses the dock's panels ([blockr.dock#586](https://github.com/BristolMyersSquibb/blockr.dock/issues/586)) carrying out core's `show()` ([blockr.dock#599](https://github.com/BristolMyersSquibb/blockr.dock/issues/599)), and the dot on a panel's tab and the toast that shows the panel ([blockr.dock#637](https://github.com/BristolMyersSquibb/blockr.dock/issues/637)).
It shapes drawing the dock's overlays with core's React SDK too: the card's menu, the dock's buttons and its options sidebar ([blockr.dock#645](https://github.com/BristolMyersSquibb/blockr.dock/issues/645)), its tooltips, the bar's menus and its folds ([blockr.dock#646](https://github.com/BristolMyersSquibb/blockr.dock/issues/646)), and its views menu and manage mode as a tree ([blockr.dock#647](https://github.com/BristolMyersSquibb/blockr.dock/issues/647)).
The navbar is [The dock's navbar](Rewrite-1.2.5)'s, the card's own design is [Block cards in the dock](Rewrite-1.2.7)'s, and the commands that change the dock's views are [The dock's state](Rewrite-1.2.1)'s.

## What must hold

Condition 3 of [Client-drawn dock](Rewrite-1.2#what-must-hold) rests on this page.

1. The dock can show every plugin whose class has a `ui` in a panel, with the plugin's name on the panel's tab, and draws the controls of the app's storage plugin in its navbar ([The dock's navbar](Rewrite-1.2.5#what-must-hold)), for a plugin of a package that the dock does not know too.
2. A plugin draws only in the elements that the dock gives it and in the overlays of core's React SDK, and nothing it draws depends on the dock's markup, so that it draws the same under any frontend.
3. A plugin can show its own panel or a block's in the active view, and change which views hold which panels, as today's extensions can.
4. The dock asks nothing of a plugin beyond what core's `PluginClass` holds, so that every plugin works under the dock as under any other frontend.
5. What today's extensions take from the dock carries over where a package still needs it, as condition 4 of [Client-drawn dock](Rewrite-1.2#what-must-hold) asks, and Today names what goes, with the reason.
6. A warning or an error about a plugin shows on its panel's tab wherever the tab shows, and one about a plugin whose panel the active view does not hold reaches the user as a toast, from which the user reaches the panel.

## Today

An extension reaches the dock through its server function, which `new_dock_extension()` takes.
The dock calls that function with the board, `update()`, the views and their grids as the browser last reported them, the dock's actions and the state of every other extension ([R/ext-class.R#L6-L13](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/ext-class.R#L6-L13)).
The dock builds the extension's UI once and moves it into the extension's panel.
What the extensions of today's packages take from the dock, at `655e323`:

| Today | Used by | Where it goes |
|---|---|---|
| A panel for each extension, titled with the extension's name. A board's default view puts every extension's panel on its left rail ([R/dock-grid.R#L994-L1008](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L994-L1008), [R/dock-rail.R#L339-L349](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-rail.R#L339-L349)), and the panel picker offers the extensions under "Extensions", each with a gear ([R/panel-menu.R#L72-L121](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/panel-menu.R#L72-L121)) | Every extension with a UI | Carried over for every plugin whose class has a `ui` ([A plugin's panel](#a-plugins-panel)), with the plugins' panels on the left rail of a board's default view ([The dock's state](Rewrite-1.2.1#starting-on-a-board)), while a view without a grid of its own shows them in one tab group, beside the blocks' panels in another, as today ([The dock's state](Rewrite-1.2.1#grids)) |
| The dock's markup around an extension's UI: a wrapper with no height of its own ([R/ext-class.R#L164-L178](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/ext-class.R#L164-L178)) and dockview's classes. A collapsed rail squeezes its panel to about 30 px | The DAG sizes its canvas through the markup. The assistant sets the wrapper's height through `:has(> .asst-panel)` and blanks itself at 140 px or narrower. Both, and blockr.md's fix of its editor after the move into its panel, are in the notes of [Client-drawn dock](Rewrite-1.2) | Replaced by an element that fills the panel, and by a collapsed rail that hides its panels ([A plugin's panel](#a-plugins-panel)) |
| Deltas of `views$mod`, which show a block's panel or an extension's in the active view, and change which views hold which panels | The DAG and the slides of blockr.outline show a block. The outline shows an extension's panel and edits which views hold which panels ([R/outline-ext.R#L478-L614](https://github.com/cynkra/blockr.outline/blob/d3499f4623f956f6691235f90fa84b46b925852c/R/outline-ext.R#L478-L614)) | Replaced by core's `show()`, which the dock carries out in the active view, and by the dock's commands for which views hold which panels, which any plugin runs ([Showing a panel](#showing-a-panel)) |
| The views and their grids as the browser last reported them, which the dock hands each extension's server as `view_data` | The assistant reads the active view's focus from it, and lists the blocks of the active view first in its `@` menu ([R/focus.R#L150-L176](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/focus.R#L150-L176)) | Replaced by `CoreApi.focus` and `CoreApi.onScreen` ([Plugins](Rewrite-1.1.12#what-a-frontend-offers-other-plugins)), and by the dock's state, which every plugin reads through `core.store.board()` ([Plugins](Rewrite-1.1.12#a-plugins-state)) |
| The dock's twelve actions, which an extension fires by id. Nine of them open the "+" menu at a point, or an editor of links, inputs or stacks in the dock's sidebar. The function `sidebar_owned_by()` tells whether the editor that an action opened is still on screen | The DAG's context menu, toolbar and canvas fire all twelve, and retarget a pinned editor to the next selection ([R/ext.R#L118-L419](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L118-L419), [R/srv.R#L444-L474](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/srv.R#L444-L474)) | Replaced by core's board actions, which any plugin triggers by id, and whose advanced actions the dock shows in its sidebar, where a pinned one follows the DAG's selection, so that `sidebar_owned_by()` goes ([Board actions](Rewrite-1.1.16), [Places besides the panel](#places-besides-the-panel)) |
| An extension's own actions, through its method of `board_actions()` ([R/action-class.R#L90-L93](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/action-class.R#L90-L93)) | The DAG draws a link, and removes, copies, cuts and pastes, through actions of its own ([R/action.R#L202-L212](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/action.R#L202-L212)) | Replaced by the board actions that a plugin's class lists, which run its commands ([Board actions](Rewrite-1.1.16#a-board-action)) |
| A callback for each block, `extension_block_callback()`, which every card's server runs with the block's status and conditions ([R/plugin-block.R#L402-L422](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L402-L422)) | The DAG and blockr.outline's minidag draw their status badges through it ([R/outline-ext.R#L787-L844](https://github.com/cynkra/blockr.outline/blob/d3499f4623f956f6691235f90fa84b46b925852c/R/outline-ext.R#L787-L844)) | Dropped, since a plugin reads every block's status through `scheduler.status()` and `scheduler.subscribe()` ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)) |
| The card's section `ctrl`, which the dock fills with the UI of core's `ctrl_block` plugin. A button in the card's header shows or hides it, with that plugin's label and icon ([R/plugin-block.R#L128-L174](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L128-L174), [R/plugin-block.R#L258-L288](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L258-L288)) | The chat on every block of blockr.ai's `ai_ctrl_block()`, which the clinical data explorer's script of one view serves | Dropped with that chat, which the assistant replaces ([Plugins](Rewrite-1.1.12#today)), and no plugin's section takes its place on the card ([Places besides the panel](#places-besides-the-panel)) |
| The board options that an extension brings in the `options` of `new_dock_extension()`. The options sidebar shows each on the page of its category ([R/board-options.R#L253-L339](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/board-options.R#L253-L339)) | The assistant brings `llm_model`, `chat_compact_tokens` and `chat_compact_keep` ([R/ext-server.R#L147-L162](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/ext-server.R#L147-L162)) | Carried over through core for board options that set how the board is shown, which a plugin's class requires and the dock's options sidebar shows, while a plugin keeps a setting of its own in its state first ([Settings](#settings)) |
| Navbar items, which only an app adds, through `serve()` ([blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494)) | The avatar of blockr.session | Carried over for an app, which gives its navbar items to `serve()` in `navbar`, while no plugin adds to the bar, and the avatar becomes a status among the storage controls of blockr.session's storage plugin, which an app's `navbar` places apart ([The dock's navbar](Rewrite-1.2.5#what-the-bar-holds)) |

Today no extension adds to the card's "…" menu, whose items the dock fixes: Controls, Rename, Append block, Copy block ID and Remove block ([R/plugin-block.R#L191-L247](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L191-L247)).

The DAG offers places of its own.
Every extension may add entries to the DAG's context menu and toolbar through methods of the S3 generics `context_menu_items()` and `toolbar_items()`, but only the DAG's own extension has such methods ([R/ctx.R#L230-L253](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ctx.R#L230-L253), [R/tool.R#L187-L217](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/tool.R#L187-L217)).
The DAG's menus offer board actions in their place, as every menu of a board object does ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).

## Proposal

### A plugin's panel

The dock offers each plugin whose class has a `ui` one panel, in which it mounts the plugin's module with `core.mountPlugin(el, plugin)` ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
A view's grid names the panel by the plugin's class id, as `{ "plugin": "blockr.md-md_plugin" }`, and a view has at most one panel for each plugin, as for each block ([The dock's state](Rewrite-1.2.1#grids)).
The panel's tab shows the plugin's name, which `core.plugins.appPlugins()` gives ([Plugins](Rewrite-1.1.12#a-plugin)).
The panel picker lists, after the blocks and under "Plugins", each plugin with a `ui` that the active view does not show, by its name.
A view that shows no panel says "Start by adding a panel", with a button that opens the panel picker, or "This view is empty" under the board lock, as today ([R/utils-ui.R#L179-L201](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/utils-ui.R#L179-L201)).
Core's Edit board plugin is the first plugin that the dock places in a panel, since core builds it before the dock ([Client-drawn dock](Rewrite-1.2#proposal)).

The dock mounts a plugin's UI when it draws the plugin's panel.
It runs the cleanup that `mountPlugin()` returned once the panel goes, as when the user closes the panel or another board opens.
A panel behind another tab or on a collapsed rail stays mounted, as dockview keeps a panel until it is closed ([UI modules in JS](Rewrite-1.1.7#the-contract)).
So the UI keeps what it holds outside the plugin's state, such as a scroll position or a message not yet sent.
The dock may mount the UI again, as when it redraws a view.
So a plugin keeps in its state what others should see, and runs from its class's `start` what has to outlive its panel, as [Plugins](Rewrite-1.1.12#running-a-plugin) has it.

The element that the dock gives `mountPlugin()` fills the panel's body, at the panel's width and height.
So a plugin sizes itself from its own element, with `height: 100%`, a container query or a `ResizeObserver`.
Today the DAG sizes its canvas through dockview's markup instead, and the assistant sets the height of the dock's wrapper.
A collapsed rail shows its tabs alone ([The dock's state](Rewrite-1.2.1#grids)), and the dock hides the content of its panels rather than squeeze it.
So no plugin has to tell a collapsed rail from a narrow panel by its width, as the assistant does today when it blanks itself at 140 px.
The panel's frame, tab and close button are the dock's, in blockr.ui's design system.
What is inside the panel is the plugin's, in a root of its own ([Plugins](Rewrite-1.1.12#plugin-classes)).

A plugin that needs more room than its panel, as for a menu or a form, opens it in an overlay of core's React SDK, such as its `Modal` or its `Popover`, which React Aria draws in a portal at the end of the page's body, where no panel clips it ([UI modules in JS](Rewrite-1.1.7#react)).
It opens nothing in the browser's top layer, such as a `<dialog>` that `showModal()` opens or a popover, since an overlay of the SDK opened inside it would show beneath it.
So the dock offers no place for dialogs.

A board that holds no state for the dock opens on one view, which shows the panel of every plugin of the app that has a `ui` on its left rail, beside the blocks' panels, as today ([The dock's state](Rewrite-1.2.1#starting-on-a-board)).
A plugin that no view of a board holds, such as one that the app added since the board was saved, shows in no panel until the user picks it from the panel picker or a command shows it, as an extension that no view holds today.
The dock adds a view of its own as it starts only where its state holds none, so it never changes the views of a saved board as the board opens.

### Showing a panel

A plugin shows a block or a plugin through core's `show()`, as under every frontend ([Plugins](Rewrite-1.1.12#showing-a-block-or-a-plugin)).
The dock's `show` runs its command `blockr.dock-show_panel` with the board object that `show()` was given, which names the panel as a grid names it, such as `{ "plugin": "blockr.md-md_plugin" }` ([The dock's state](Rewrite-1.2.1#commands)).
The command has the panel's tab group or rail show it where the active view holds it, opening the rail where it is collapsed, and adds it at the default place where the view does not.
It takes no undo step, adding included, since showing takes none under any frontend.
Today the DAG and the slides of blockr.outline show a block, and the outline shows an extension's panel, through deltas of `views$mod` of their own.
A plugin changes which views hold which panels with the dock's commands `blockr.dock-add_panel` and `blockr.dock-remove_panel`, as the outline's menu of views does today.
Any plugin runs these commands, as any package runs another's ([Board updates](Rewrite-1.1.2#commands)).
A plugin reads which views there are, and which panels each holds, from the dock's state, which is open to every plugin ([Plugins](Rewrite-1.1.12#a-plugins-state)).
The outline reads the dock board's views in the same way today.

A plugin draws a control for one of the dock's commands only where `core.commands.registered()` holds that command.
Another frontend registers none of the dock's commands, so there the plugin draws no such control and works on.
A locked dock adds no panel, so there `blockr.dock-show_panel` only brings to the front a panel that the view holds already ([The dock's state](Rewrite-1.2.1#on-a-locked-board)).

### Settings

A plugin keeps a setting of its own in its state first, so that the setting saves and migrates with the plugin, and the plugin's UI shows it and changes it through the plugin's commands, in its panel or in an overlay ([Plugins](Rewrite-1.1.12#a-plugins-state)).
A board option is no substitute for that state, since it is meant for how the board is shown, such as the dock's `view_tabs` ([Board options and blockr options](Rewrite-1.1.13#the-two-kinds)).
A plugin's class names the board options of that kind that it requires in `options`, and its package registers those it ships ([Board options and blockr options](Rewrite-1.1.13#defining-a-board-option)).
The dock's options sidebar shows each board option that the board holds, which include every one that something on the page requires, on the page of its `category`, and mounts each with `mountOption()`.
Today's sidebar shows the board options that an extension brings in the same way ([Client-drawn dock](Rewrite-1.2#today)).
So settings need no member of the dock's.
A plugin's board options show under every frontend, as core's basic frontend shows them in its toolbar ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
On a locked board the sidebar shows them too, since the board lock leaves board options open ([Locked boards and the properties of blocks](Rewrite-1.1.11#board-options-on-a-locked-board)).
Today's sidebar shows only the code export on a locked board ([R/board-options.R#L268-L273](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/board-options.R#L268-L273)).

### Places besides the panel

Besides the panel, the dock gives plugins what every frontend gives them: it draws the notifications of `CoreApi` ([Notifications, logging and tracing](Rewrite-1.1.14#where-a-notification-shows)), and the controls of the app's storage plugin in its navbar ([The dock's navbar](Rewrite-1.2.5#the-storage-plugins-controls)).
It shows the advanced actions of board actions in its sidebar, which the user may pin, through the `advanced` member that core's `FrontendModule` offers every frontend, while core draws their menus and quick actions in the design system's look, which blockr.ui gives core's theme ([Board actions](Rewrite-1.1.16#what-a-frontend-gives)).
What those controls cannot hold, the storage plugin draws in a dialog of its own, an overlay of core's React SDK, which the dock does not place, as it places no plugin's dialog ([A plugin's panel](#a-plugins-panel)).
The dock offers plugins no other place, so it declares no member of its own on core's `PluginClass`, and reads no member of a plugin's class beyond core's, as core's basic frontend reads none ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
A place that the dock comes to offer later is a member of its own, which TypeScript's module augmentation declares ([TypeScript](https://www.typescriptlang.org/docs/handbook/declaration-merging.html#module-augmentation)), and which changes nothing for the plugins that do not set it.

A plugin shows the notifications about itself in its panel, as every plugin with a `ui` does, and the dock tells the user that a warning or an error about the plugin holds with a dot on the panel's tab, in the design system's danger colour for an error and its amber set for a warning, whichever panel the tab group or rail shows, so that a collapsed rail, which shows its tabs alone, shows the dot too ([Notifications, logging and tracing](Rewrite-1.1.14#where-a-notification-shows)).
A tab has no room for a badge that counts them, as core's basic frontend draws on a plugin's section.
The tab's tooltip holds their messages, so that the user can read one that the plugin does not show, such as why its UI cannot draw.
Where the active view holds no panel of the plugin, the dock shows each notification about the plugin as a toast, which names the plugin, with a link that shows the panel: it makes the first view of the navigation that holds the panel the active one and shows the panel there, or, where no view holds it, adds it to the active view at the default place, as `blockr.dock-show_panel` does ([Showing a panel](#showing-a-panel)).
Such a toast goes once the active view holds the panel, since the dot then shows on its tab.
A plugin without a `ui`, such as the storage plugin, has no panel, so the dock shows its notifications as toasts, as it shows those about the board, a link, a stack or a board option ([Block cards in the dock](Rewrite-1.2.7#notifications)).

The dock draws no picker or editor of its own for a plugin, since a plugin triggers board actions, whose UI the package that registers each one writes ([Board actions](Rewrite-1.1.16#a-board-action)).
So the DAG's menus offer core's board actions, with the block picker and the editors of links, inputs and stacks, where today the DAG opens the dock's through the dock's actions ([Client-drawn DAG](Rewrite-1.3)).
The DAG shows their advanced actions in a panel beside the object that it opened them on, and leaves them to the dock's sidebar where that panel does not hold up ([Drawing the DAG](Rewrite-1.3.2#its-advanced-actions)).
Where the user pins the sidebar, it stays open once `done()` ends its advanced action, and the dock mounts the advanced action again through the `mount()` that core hands its `advanced` ([Board actions](Rewrite-1.1.16#what-a-frontend-gives)):

1. Once `done()` has run a batch, the dock mounts the advanced action on the one board object that the batch added of a kind that the board action's `on` names, so that a pinned Append block moves on to the block that it appended, and otherwise on the same target, so that a pinned Add block stays on the board.
2. As `core.selection` comes to hold one board object for which `core.boardActions.on()` offers the board action, the dock mounts the advanced action on that object, so that a pinned Edit inputs, opened from a card's menu, follows the blocks that the user selects in the DAG.
3. Otherwise a selection changes nothing, so that a selection never swaps one board action's advanced action for another's, which only opening a board action or closing the sidebar does.

So the sidebar follows the DAG's selection without `sidebar_owned_by()`, and the rules are the dock's alone, since core keeps none.
The dock's sidebar holds its options as well ([Client-drawn dock](Rewrite-1.2#proposal)).

The dock's block cards offer plugins no section on every card, no button in a card's header and no panel for each block, which no package needs once the `ctrl` section goes with blockr.ai's chat on every block ([Today](#today)).
A grid names a panel by an object, which leaves room for a panel for each block later ([The dock's state](Rewrite-1.2.1#grids)).
A card's "…" menu offers the board actions on its block, which any plugin registers, so that the dock's cards and the DAG's nodes offer the same ones ([Board actions](Rewrite-1.1.16#the-menus-of-board-objects)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's code, at `655e323`: the panel picker is `suggest_panels_to_add()` and `add_panel_menu_items()` in `R/panel-menu.R`; the wrapper of an extension's UI is the `div` that `extension_ui()` adds in `R/ext-class.R`; the card's `ctrl` section and its button are `block_card_toggles()` and `block_card_content()` in `R/plugin-block.R`, which `R/block-ui.R` fills from the served `ctrl_block` plugin; the callbacks for each block run in `edit_block_server()` in `R/plugin-block.R`, which `R/board-plugins.R` hands every extension's `extension_block_callback()`; and the options sidebar is `settings_body()` and `options_sidebar_ui()` in `R/board-options.R`.

A test that drives the dock's panels registers a plugin class of its own through `core.plugins.register()`, as [Plugins](Rewrite-1.1.12#testing) has it, and mounts the dock's frontend module on core's `CoreApi` for tests ([Drawing the board](Rewrite-1.1.8#testing)).

</details>
