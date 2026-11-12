# Places the dock offers plugins
Status: review. Design for [Client-drawn dock](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock](Rewrite-1.2)): the places where the dock puts plugins.
It covers the panel in which the dock mounts each plugin's `ui` with `mountPlugin()`, how a plugin shows a panel in the active view, and where a plugin's settings show.
It also says why the panel is the only place that the dock offers plugins, so the dock declares no member of its own on core's `PluginClass` ([Plugins](Rewrite-1.1.12#plugin-classes)).
It builds on [Plugins](Rewrite-1.1.12) and [Drawing the board](Rewrite-1.1.8#what-core-gives-plugins).
It shapes two items of the Work list of [Client-drawn dock](Rewrite-1.2#work): placing every plugin, and writing how a plugin uses the places that the dock offers.
The navbar is [The dock's navbar](Rewrite-1.2.5)'s, the card's own design is [Block cards in the dock](Rewrite-1.2.7)'s, and the commands that change the dock's views are [The dock's state](Rewrite-1.2.1)'s.

## What must hold

Condition 3 of [Client-drawn dock](Rewrite-1.2#what-must-hold) rests on this page.

1. The dock can show every plugin whose class has a `ui` in a panel, with the plugin's name on the panel's tab, a plugin of a package that the dock does not know included.
2. A plugin draws only in the elements that the dock gives it and in the browser's top layer, and nothing it draws depends on the dock's markup, so that it draws the same under any frontend.
3. A plugin can show its own panel or a block's in the active view, and change which views hold which panels, as today's extensions can.
4. The dock asks nothing of a plugin beyond what core's `PluginClass` holds, so that every plugin works under the dock as under any other frontend.
5. What today's extensions take from the dock carries over where a package still needs it, as condition 4 of [Client-drawn dock](Rewrite-1.2#what-must-hold) asks, and Today names what goes, with the reason.

## Today

An extension reaches the dock through its server function, which `new_dock_extension()` takes.
The dock calls that function with the board, `update()`, the views and their grids as the browser last reported them, the dock's actions and the state of every other extension ([R/ext-class.R#L6-L13](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/ext-class.R#L6-L13)).
The dock builds the extension's UI once and moves it into the extension's panel.
What the extensions of today's packages take from the dock, at `655e323`:

| Today | Used by | Where it goes |
|---|---|---|
| A panel for each extension, titled with the extension's name. A board's default view puts every extension's panel on its left rail ([R/dock-grid.R#L994-L1008](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L994-L1008), [R/dock-rail.R#L339-L349](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-rail.R#L339-L349)), and the panel picker offers the extensions under "Extensions", each with a gear ([R/panel-menu.R#L72-L121](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/panel-menu.R#L72-L121)) | Every extension with a UI | Carried over for every plugin whose class has a `ui` ([A plugin's panel](#a-plugins-panel)). A view without a grid of its own shows the plugins' panels in one tab group, beside the blocks' panels in another ([The dock's state](Rewrite-1.2.1#grids)) |
| The dock's markup around an extension's UI: a wrapper with no height of its own ([R/ext-class.R#L164-L178](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/ext-class.R#L164-L178)) and dockview's classes. A collapsed rail squeezes its panel to about 30 px | The DAG sizes its canvas through the markup. The assistant sets the wrapper's height through `:has(> .asst-panel)` and blanks itself at 140 px or narrower. Both, and blockr.md's fix of its editor after the move into its panel, are in the notes of [Client-drawn dock](Rewrite-1.2) | Replaced by an element that fills the panel, and by a collapsed rail that hides its panels ([A plugin's panel](#a-plugins-panel)) |
| Deltas of `views$mod`, which show a block's panel or an extension's in the active view, and change which views hold which panels | The DAG and the slides of blockr.outline show a block. The outline shows an extension's panel and edits which views hold which panels ([R/outline-ext.R#L478-L614](https://github.com/cynkra/blockr.outline/blob/d3499f4623f956f6691235f90fa84b46b925852c/R/outline-ext.R#L478-L614)) | Replaced by the dock's commands, which any plugin runs ([Showing a panel](#showing-a-panel)) |
| The views and their grids as the browser last reported them, which the dock hands each extension's server as `view_data` | The assistant reads the active view's focus from it, and lists the blocks of the active view first in its `@` menu ([R/focus.R#L150-L176](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/focus.R#L150-L176)) | Replaced by `CoreApi.focus` ([Plugins](Rewrite-1.1.12#what-a-frontend-offers-other-plugins)), and by the dock's state, which every plugin reads through `core.store.board()` ([Plugins](Rewrite-1.1.12#a-plugins-state)) |
| The dock's twelve actions, which an extension fires by id. Nine of them open the "+" menu at a point, or an editor of links, inputs or stacks in the dock's sidebar. The function `sidebar_owned_by()` tells whether the editor that an action opened is still on screen | The DAG's context menu, toolbar and canvas fire all twelve, and retarget a pinned editor to the next selection ([R/ext.R#L118-L419](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ext.R#L118-L419), [R/srv.R#L444-L474](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/srv.R#L444-L474)) | The edits are core's commands ([Client-drawn dock](Rewrite-1.2#proposal)). The DAG gathers their args in its own UI, so `sidebar_owned_by()` goes ([Places besides the panel](#places-besides-the-panel)) |
| An extension's own actions, through its method of `board_actions()` ([R/action-class.R#L90-L93](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/action-class.R#L90-L93)) | The DAG draws a link, and removes, copies, cuts and pastes, through actions of its own ([R/action.R#L202-L212](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/action.R#L202-L212)) | Replaced by commands that the plugin's package registers ([Board updates](Rewrite-1.1.2#commands)) |
| A callback for each block, `extension_block_callback()`, which every card's server runs with the block's status and conditions ([R/plugin-block.R#L402-L422](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L402-L422)) | The DAG and blockr.outline's minidag draw their status badges through it ([R/outline-ext.R#L787-L844](https://github.com/cynkra/blockr.outline/blob/d3499f4623f956f6691235f90fa84b46b925852c/R/outline-ext.R#L787-L844)) | Dropped, since a plugin reads every block's status through `scheduler.status()` and `scheduler.subscribe()` ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)) |
| The card's section `ctrl`, which the dock fills with the UI of core's `ctrl_block` plugin. A button in the card's header shows or hides it, with that plugin's label and icon ([R/plugin-block.R#L128-L174](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L128-L174), [R/plugin-block.R#L258-L288](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L258-L288)) | The chat on every block of blockr.ai's `ai_ctrl_block()`, which CEDX's `run_cedx_view()` serves ([R/cedx_view_board.R#L107-L120](https://github.com/BristolMyersSquibb/blockr.cdex/blob/7792b7e0fd9eda417995dd7e460f086f671df73c/R/cedx_view_board.R#L107-L120)) | Dropped with that chat, which the assistant replaces ([Plugins](Rewrite-1.1.12#today)), and the card offers plugins no other place in its stead ([Places besides the panel](#places-besides-the-panel)) |
| The board options that an extension brings in the `options` of `new_dock_extension()`. The options sidebar shows each on the page of its category ([R/board-options.R#L253-L339](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/board-options.R#L253-L339)) | The assistant brings `llm_model`, `chat_compact` and `chat_keep` ([R/ext-server.R#L147-L162](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/ext-server.R#L147-L162)) | Carried over through core: the board options that a plugin's class requires, which the dock's options sidebar shows ([Settings](#settings)) |
| Navbar items, which only an app adds, through `serve()` ([blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494)) | The avatar of blockr.session | Dropped, since neither an app nor a plugin adds to the dock's navbar, and the avatar becomes a status among the storage controls of blockr.session's storage plugin ([The dock's navbar](Rewrite-1.2.5)) |

No extension adds to the card's "…" menu.
The dock fixes its items: Controls, Rename, Append block, Copy block ID and Remove block ([R/plugin-block.R#L191-L247](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L191-L247)).

The DAG offers places of its own.
Every extension may add entries to the DAG's context menu and toolbar through methods of the S3 generics `context_menu_items()` and `toolbar_items()`, but only the DAG's own extension has such methods ([R/ctx.R#L230-L253](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/ctx.R#L230-L253), [R/tool.R#L187-L217](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/tool.R#L187-L217)).
Carrying those places over is [Client-drawn DAG extension](Rewrite-1.3)'s.

## Proposal

### A plugin's panel

The dock offers each plugin whose class has a `ui` one panel, in which it mounts the plugin's module with `core.mountPlugin(el, plugin)` ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
A view's grid names the panel by the plugin's class id, as `{ "plugin": "blockr.md-md_plugin" }`, and a view has at most one panel for each plugin, as for each block ([The dock's state](Rewrite-1.2.1#grids)).
The panel's tab shows the plugin's name, which `core.plugins.running()` gives ([Plugins](Rewrite-1.1.12#a-plugin)).
The panel picker lists, after the blocks and under "Plugins", each plugin with a `ui` that the active view does not show, by its name.
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

A plugin that needs more room than its panel, as for a menu or a form, opens it in the browser's top layer, as a `<dialog>` that `showModal()` opens or as a popover.
An element there "cannot be clipped by anything in the document" ([CSS Positioned Layout 4](https://drafts.csswg.org/css-position-4/#top-layer)).
It still sits inside the plugin's element in the DOM, as the contract asks of a module ([UI modules in JS](Rewrite-1.1.7#the-contract)).
So the dock offers no place for dialogs.

A board that holds no state for the dock opens on one view, which shows the panel of every plugin of the app that has a `ui`, in one tab group beside the blocks' panels ([The dock's state](Rewrite-1.2.1#starting-on-a-board)).
A plugin that no view of a board holds, such as one that the app added since the board was saved, shows in no panel until the user picks it from the panel picker or a command shows it, as an extension that no view holds today.
The dock adds a view of its own as it starts only where its state holds none, so it never changes the views of a saved board as the board opens.

### Showing a panel

A plugin shows a block's panel or a plugin's in the active view with the dock's command `blockr.dock-show_panel`, which takes the panel as a grid names it, such as `{ "plugin": "blockr.md-md_plugin" }` ([The dock's state](Rewrite-1.2.1#commands)).
The command has the panel's tab group show it where the view holds it, and adds it at the default place where the view does not.
Today the DAG and the slides of blockr.outline show a block, and the outline shows an extension's panel, through deltas of `views$mod` of their own.
A plugin changes which views hold which panels with the dock's commands `blockr.dock-add_panel` and `blockr.dock-remove_panel`, as the outline's menu of views does today.
Any plugin runs these commands, as any package runs another's ([Board updates](Rewrite-1.1.2#commands)).
A plugin reads which views there are, and which panels each holds, from the dock's state, which is open to every plugin ([Plugins](Rewrite-1.1.12#a-plugins-state)).
The outline reads the dock board's views in the same way today.

A plugin draws a control for one of the dock's commands only where `core.commands.registered()` holds that command.
Another frontend registers none of the dock's commands, so there the plugin draws no such control and works on.
A locked dock adds no panel, so there `blockr.dock-show_panel` only brings to the front a panel that the view holds already ([The dock's state](Rewrite-1.2.1#on-a-locked-board)).

### Settings

What a user sets for a plugin while the app runs is a board option, unless the plugin keeps it in its state.
The plugin's class names the board option in `options`, and its package registers it ([Board options and blockr options](Rewrite-1.1.13#defining-a-board-option)), as the assistant will do with `llm_model` ([Assistant as a client extension](Rewrite-1.4#proposal)).
The dock's options sidebar shows every board option that `core.options.inUse()` lists, on the page of its `category`, and mounts each with `mountOption()`.
Today's sidebar shows the board options that an extension brings in the same way ([Client-drawn dock](Rewrite-1.2#today)).
So settings need no member of the dock's.
A plugin's board options show under every frontend, as core's basic frontend shows them in its toolbar ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
On a locked board the sidebar shows them too, since the board lock leaves board options open ([Locked boards and the properties of blocks](Rewrite-1.1.11#board-options-on-a-locked-board)).
Today's sidebar shows only the code export on a locked board ([R/board-options.R#L268-L273](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/board-options.R#L268-L273)).

### Places besides the panel

The panel is the only place that the dock offers plugins.
No plugin adds to the dock's navbar, where the storage plugin's controls are the only ones of another plugin that the dock draws ([The dock's navbar](Rewrite-1.2.5)), and the dock's menus and cards offer plugins nothing, as below.
So the dock declares no member of its own on core's `PluginClass`, and reads no member of a plugin's class beyond core's, as core's basic frontend reads none ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
A place that the dock comes to offer later is a member of its own, which TypeScript's module augmentation declares ([TypeScript](https://www.typescriptlang.org/docs/handbook/declaration-merging.html#module-augmentation)), and which changes nothing for the plugins that do not set it.

The dock takes no part in what a plugin draws, and offers plugins none of its own pickers, editors or sidebars.
A plugin draws the UI that gathers the args of the commands it runs, in its panel or in the top layer, and runs core's commands with what the user picks.
So the DAG draws its own block picker and its own editors of links, inputs and stacks for its menus ([Client-drawn DAG extension](Rewrite-1.3)), where today it opens the dock's through the dock's actions.
It edits in the same way under every frontend, and keeps a pinned editor on the selection by itself, without `sidebar_owned_by()`.
The dock keeps its "+" menu for the "Append block" of a card's menu, and its sidebar for its options ([Client-drawn dock](Rewrite-1.2#proposal)).

The dock's block cards offer plugins no place: no section on every card, no button in a card's header, no entry in a card's menu and no panel for each block.
No package needs one, since the `ctrl` section goes with blockr.ai's chat on every block, and no extension adds to a card's menu today ([Today](#today)).
A grid names a panel by an object, which leaves room for a panel for each block later ([The dock's state](Rewrite-1.2.1#grids)).
Entries that plugins add to a block's menu would rather come from core, so that every menu of a block draws them, the dock's cards and the DAG's nodes alike ([Backlog](Backlog#entries-of-a-blocks-menu-in-core)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's code, at `655e323`: the panel picker is `suggest_panels_to_add()` and `add_panel_menu_items()` in `R/panel-menu.R`; the wrapper of an extension's UI is the `div` that `extension_ui()` adds in `R/ext-class.R`; the card's `ctrl` section and its button are `block_card_toggles()` and `block_card_content()` in `R/plugin-block.R`, which `R/block-ui.R` fills from the served `ctrl_block` plugin; the callbacks for each block run in `edit_block_server()` in `R/plugin-block.R`, which `R/board-plugins.R` hands every extension's `extension_block_callback()`; and the options sidebar is `settings_body()` and `options_sidebar_ui()` in `R/board-options.R`.

A test that drives the dock's panels registers a plugin class of its own through `core.plugins.register()`, as [Plugins](Rewrite-1.1.12#testing) has it, and mounts the dock's frontend module on core's `CoreApi` for tests ([Drawing the board](Rewrite-1.1.8#testing)).

</details>
