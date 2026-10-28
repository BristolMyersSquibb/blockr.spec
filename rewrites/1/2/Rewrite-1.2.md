# Client-drawn dock and extensions
Status: draft. Part of [State in JS](Rewrite-1).

This part covers blockr.dock, which becomes a React app on core's JS API, and the client extension API that the DAG, the assistant, code export and session management are rebuilt on. It builds on [Client-owned board state](Rewrite-1.1).

## Problem

The dock draws the board from R with DOM operations: `insertUI()` parks cards, `move-element` messages carry them into dockViewR panels, proxy calls add and move panels, sidebars arrive as `renderTags()` HTML and menus as `menu:sync` diffs. Of 100 defects in the shell's history, 37 are this protocol failing ([blockr#493](https://github.com/orgs/BristolMyersSquibb/discussions/493)).

The dock's model lives in R too: views, grids, the `views$mod` grammar and the action registry (`new_action()`, `register_actions()`), so every view switch and arrangement change is sent to the session's R process. Extensions are Shiny module pairs (`new_dock_extension(server, ui, ...)`), and other surfaces have no API at all, the navbar among them ([blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494)).

Once board state moves to the client ([Client-owned board state](Rewrite-1.1)), the dock's model is board state too. The POC of [blockr#493](https://github.com/orgs/BristolMyersSquibb/discussions/493) keeps it in R, so it settles the drawing but not the ownership.

## What must hold

1. The browser draws the dock with dockview directly, without dockViewR.
2. Views, layouts and arrangement are the dock's fields in the board, and no arrangement change reaches R.
3. An extension contributes panels and navbar items through the dock's client API, and works on the board through core's JS API, which is enough to rebuild the DAG, the assistant, the code extension and session management on.
4. Boards saved by today's blockr.dock open with their views and layouts.
5. On the CEDX board, first paint and a view switch take no longer than with blockr.dock today.

## Proposal

- The dock is a React app on core's JS API, with the layout drawn by `dockview-react`, since React has the largest pool of components and of extension authors, AI tools write it best, and the POC already runs on it. React draws only the chrome, while the board and commands stay in core's store. The dock's model (views, grids, the `views$mod` grammar, its actions) moves to TypeScript as the dock's fields in the board ([Document model](Rewrite-1.1.1)), since with the client as sole owner the model is board state. A view's layout is stored as dockview's own `toJSON()`, and the conversion from today's compact grid, `grid_to_tree()` and its inverse in R, moves to the client to load saved boards.
- The dock's fields in the board hold only what everyone who opens a board shares, the views and their layouts, and keep one person's screen apart: which view is active, the selection, which panel has focus. The tldraw store makes the same split, between session records, "local to one editor instance, like which page you're viewing", and document records, "saved to storage and synced across instances" ([tldraw store](https://tldraw.dev/sdk-features/store)). Nothing syncs now, but if a relay for collaboration comes later as an add-on, mixed fields would move every collaborator's screen with one person's clicks, and separating the two then would mean migrating saved boards.
- The dock's actions become commands in core's registry, and everything the dock changes goes through core's deltas, so undo and save cover arrangement too, and nothing the client does to its own layout reaches R.
- Extensions are ES modules that register with the dock, the one extension mechanism, since core has none ([Client-owned board state](Rewrite-1.1)). An extension's logic works against core's JS API (the board, commands, requests to R), and its UI goes through the dock's contribution points as React components: panels, one per board or per block, navbar items (the API [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) asks for, here on the client), sidebar sections, menus on the board, a block, a stack and the DAG's canvas, and settings. The dock also offers services, such as notifications and storage, where one extension can replace the dock's default.
- The dock builds its own features, such as adding blocks or showing notifications, on the same contribution points, as JupyterLab's own main menu and file browser are extensions ([extension guide](https://jupyterlab.readthedocs.io/en/latest/extension/extension_dev.html)), so an extension can do whatever the dock does.
- Extensions are few and integrate with the dock's chrome, so unlike block UIs, which keep the framework-free contract of [Client-owned board state](Rewrite-1.1), they use React directly. Their components render inside the dock's React tree, where hooks fail on a second copy ([React](https://react.dev/warnings/invalid-hook-call-warning)), so they are built with the same preset as block UIs, which maps `react` to the one copy blockr.ui ships, the copy the dock itself uses ([UI modules in JS](Rewrite-1.1.7#the-react-sdk)). An extension with state of its own, such as the DAG's layout settings, keeps it in fields it registers with core's store, which other extensions and the assistant change as they change core's objects ([Board updates](Rewrite-1.1.2#fields)), and declares the majors of the core and dock APIs it was built against.
- The DAG ([Client-drawn DAG extension](Rewrite-1.3)), the assistant ([Assistant extension](Rewrite-1.4)), the code extension ([Code export extension](Rewrite-1.5)) and session management ([Session management extension](Rewrite-1.6)) have parts of their own and are rebuilt after the dock. This part settles only the API they build on, and leaves libraries, agent design and their R requests to them.
- The dock draws block cards, with the header of [blockr#492](https://github.com/orgs/BristolMyersSquibb/discussions/492) and status from core, and mounts each block's UI component from core's block registry. During the migration, classic R-authored block UIs are parked and adopted as in [blockr#493](https://github.com/orgs/BristolMyersSquibb/discussions/493).
- From [blockr#493](https://github.com/orgs/BristolMyersSquibb/discussions/493), the hosting of classic block UIs and the CEDX measurement carry over. Its bridge, shinyreact, and its criterion of reusing the dock's model in R do not.

## Open questions

- Panel kinds: one per board, like the assistant's, or one per block, and whether commands can open panels.
- How the navbar order and narrow-window behavior of [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) become client API.

## Work

- Write the dock board's fields for views and layouts, with loading of boards saved by today's blockr.dock, in blockr.dock
- Draw the dock with dockview from the client's board, in blockr.dock
- Add the client extension API for panels, navbar items and sidebar sections, in blockr.dock
- Measure first paint and view switch on the CEDX board against blockr.dock, in blockr.dock

<details><summary>Notes for implementers</summary>

Prototype findings of [blockr#493](https://github.com/orgs/BristolMyersSquibb/discussions/493) that carry over: dockview reuses the panel object when a panel moves between groups (`moveGroupOrPanel()`), so mounted content stays mounted; a `fromJSON()` disposes and recreates panels; a restore through `clear()` and `fromJSON()` fires `onDidRemovePanel()` for every panel, which must not count as user closes; with `defaultRenderer = "always"`, back tabs stay in the DOM. The POC bundle was 622 KB minified and 162 KB gzipped.

Today's code: [`grid_to_tree()`](https://github.com/BristolMyersSquibb/blockr.dock/blob/1304d4df86309b03a7f4c4b96279e3d695a28cc6/R/dock-layout.R#L276) expands the compact grid into dockview's tree, inverse of `tree_to_grid()`; [`new_action()`, `board_actions()` and `register_actions()`](https://github.com/BristolMyersSquibb/blockr.dock/blob/1304d4df86309b03a7f4c4b96279e3d695a28cc6/R/action-class.R#L43-L126); [`new_dock_extension()`](https://github.com/BristolMyersSquibb/blockr.dock/blob/1304d4df86309b03a7f4c4b96279e3d695a28cc6/R/ext-class.R#L52).

Today's core plugins ([`known_plugins()`](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-plugins.R#L72-L75)) map onto the mechanism: `preserve_board` becomes session management's extension on the command that replaces the board ([Session management extension](Rewrite-1.6)); `generate_code` the code extension ([Code export extension](Rewrite-1.5)); `manage_blocks`, `manage_links` and `manage_stacks` core commands under the dock's menus and the DAG's gestures; `edit_block` and `edit_stack` the dock's block card and stack chrome, with a block menu for extensions; `notify_user` the dock's notification service; and `ctrl_block` nothing, since any command can set any block's state ([blockr.core#398](https://github.com/BristolMyersSquibb/blockr.core/issues/398)).

Coupling to expect, from [blockr#493](https://github.com/orgs/BristolMyersSquibb/discussions/493): blockr.dag asks `sidebar_owned_by()`, fires dock actions by id, and its tests set `board-actions_sidebar` directly; the assistant styles the extension wrapper through `:has(> .asst-panel)` and assumes a collapsed panel is about 30 px wide; blockr.session's navbar button uses `.blockr-navbar-icon-btn`.

Versions on npm on 2026-10-21: `dockview` 8.6.1, with `dockview-core`, `dockview-react`, `dockview-vue` and `dockview-angular` at the same version, while the `dockview-svelte` and `dockview-solid` packages are at 1.0.2 and 4.2.7.

</details>
