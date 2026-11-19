# UI kit and design system for the client
Status: draft. Part of [State in JS](Rewrite-1).

This part covers blockr.ui: the design system from which the dock and the plugins take their look, the widgets that block packages draw with today, and the table preview that it adds as a renderer of core's table outputs.
It builds on [Client-owned board state](Rewrite-1.1), whose module contract every block's UI meets, and on the one copy of React and the React SDK that core ships, whose components every UI on the page draws with in place of blockr.ui's widgets ([UI modules in JS](Rewrite-1.1.7#react)).

## Problem

Block UIs reach blockr.ui through page globals and Shiny UI.
Its widgets sit on `window.Blockr`, where blockr.dplyr's JS names `Blockr.Select` 30 times, blockr.dm's 18 times and blockr.ggplot's 7 times, while under the module contract a block's UI gets what it shares with the page through its host ([UI modules in JS](Rewrite-1.1.7#the-contract)).
Its R helpers draw into Shiny UIs, and its table preview implements the Shiny methods of core's `tabular_display()` hook, both of which go, since nothing in R draws UI any more ([Drawing the board](Rewrite-1.1.8#what-goes-from-r)).

## What must hold

1. The dock and the other plugins take their look from the design system documented in blockr.ui, and depart from it, with a reason, wherever React Aria's components do better, as condition 6 of [State in JS](Rewrite-1#what-must-hold) has it.
2. Under the dock, the components of core's React SDK and core's own UIs take the design system's colours, fonts and radii, their overlays included.
3. What blockr.ui draws with React uses the one copy of React that core ships, as the dock does ([UI modules in JS](Rewrite-1.1.7#react)).
4. Nothing of blockr.ui's is a page global.

## Today

| Today, at `9bd8312` | Lines | Where it goes |
|---|---|---|
| Design tokens, the theme and base CSS, fonts, icons and the design system article | 1,223 of CSS, 10 fonts, 19 icons | Carried over, as the design system from which the dock and the plugins take their look, with the article following the components of core's React SDK where they depart from it (Proposal) |
| Widgets on `window.Blockr`, such as `Blockr.Select`, `Blockr.textCommit` and `Blockr.gearTray`, with their types and CSS | 3,628 of JS, 2,194 of CSS | Replaced by the components of core's React SDK, which block UIs draw with: the select by `ComboBox`, the text field that commits on Enter by `TextField`, the segmented control by `ToggleButtonGroup` and the gear tray, which opens in place under its gear, by `Disclosure` ([UI modules in JS](Rewrite-1.1.7#react)) |
| R helpers that draw them into Shiny UIs: the gear tray, action menu, dropdown, shortcut hints and block marks | 646 of R | Dropped, since nothing in R draws UI, while the block's mark comes to the client in a module of blockr.ui's (Work) |
| The table preview, a display for core's `tabular_display()` hook, with its render engine | 916 of R, 94 of JS, 322 of CSS | Carried over as a renderer of the output class `table_output`, which takes the place of core's plain table where an app names it in the blockr option `renderers` ([Drawing the board](Rewrite-1.1.8#renderers)) |
| Asset dependencies and the package's own files | 423 of R | Replaced by however the client loads blockr.ui's assets (below) |
| Fixes to Shiny's behaviour: the recalculating fade, empty input batches, and the gear tray's input binding | 285 of JS | Dropped, unless the Shiny transport needs one, since no Shiny input or output draws the board |

## Proposal

- The design system stays blockr.ui's, with its tokens, fonts and icons, and the dock and the other plugins take their look from it, while core's client builds on Tailwind CSS ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
- Under the dock, blockr.ui restyles the components of core's React SDK and core's own UIs by setting the variables of core's Tailwind theme from its tokens on `:root`, the page's root, where the SDK's overlays read them too, as [Drawing the board](Rewrite-1.1.8#cores-basic-frontend) has a frontend or a UI kit restyle core's UIs.
- Block UIs draw with the components of core's React SDK in place of blockr.ui's widgets, so that blockr.ui offers block UIs no components of its own, and blockr.dplyr, blockr.dm and blockr.ggplot port their UIs onto the SDK's ([UI modules in JS](Rewrite-1.1.7#react)).
- The design system is a source of the look rather than a rule: where React Aria's components do better, the SDK's depart from it, with a reason, as the select of several shows its picks as chips where the design system lists them under "Selected" ([blockr.core#686](https://github.com/BristolMyersSquibb/blockr.core/pull/686)), and the design system's article follows the SDK there.
- Like the dock and the other plugins, blockr.ui draws with the one copy of React that core ships, with core's React SDK and its build preset, and ships no React of its own ([UI modules in JS](Rewrite-1.1.7#react)).
- Input elements composed in R, which would draw with the SDK's components, are a later project of this part, still to be decided ([Input elements for block UIs written in R](Rewrite-1.7.1)).

## Open questions

- How the client loads the design tokens, now that they no longer arrive as HTML dependencies of Shiny UI.

## Work

- Port the table preview to a renderer of the output class `table_output`, paging and sorting through the output's parameters, in blockr.ui
- Set the variables of core's Tailwind theme from the design system's tokens on `:root` wherever the dock draws the page, its colours for statuses and categories included, so that the components of core's React SDK and core's own UIs take the design system's look there, their overlays included, in blockr.ui ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend))
- Revise the design system's article where the components of core's React SDK depart from it, such as the select of several, which shows its picks as chips, in blockr.ui
- Bring the design system's locked mode in line with block locks: under the board lock a locked block shows no UI, its reader controls included, and an open block shows all of its UI, its gear included ([UI modules in JS](Rewrite-1.1.7#the-contract), [Block cards in the dock](Rewrite-1.2.7#the-blocks-lock)), in blockr.ui
- Add `ready`, a dot of `border-success`, and `unevaluated`, a ring of `text-muted`, to the design system's spec of block status, which the dock's cards and the DAG's badges share ([Block cards in the dock](Rewrite-1.2.7#the-status-dot)), in blockr.ui
- Offer the block's mark and the status dot as one module, whose tooltips the `Tooltip` of core's React SDK draws, and which the dock and the DAG import in place of the copies that each draws until then, in blockr.ui ([Block cards in the dock](Rewrite-1.2.7#the-status-dot), [Client-drawn DAG](Rewrite-1.3))
- Drop the widgets on `window.Blockr`, with their types and CSS, and the R helpers that draw into Shiny UIs, once no package draws with them, in blockr.ui

## Design pages

- [Input elements for block UIs written in R](Rewrite-1.7.1): input elements composed in R, with data-dependent attributes as requests of the block class, drawn with the SDK's components, for the later project

<details><summary>Notes for implementers</summary>

The rows of Today by file, at `9bd8312`: the design system is `blockr-tokens.css`, `blockr-tokens-dark.css`, `blockr-theme.css` and `blockr-base.css`, with `inst/assets/fonts`, `inst/assets/icons` and `vignettes/articles/design-system.Rmd`; the widgets are `blockr-ui.js`, `blockr-select.js`, `blockr-input.js` and `types.d.ts`, with every other CSS file but `blockr-table-preview.css`; the R helpers are `action-menu.R`, `block-mark.R`, `dropdown.R`, `gear-tray.R` and `shortcut.R`; the table preview is `table-preview.R`, `table-preview-render.R`, `table-preview-engine.R`, `blockr-table-preview.js` and `blockr-table-preview.css`; the dependencies and package files are `theme.R`, `controls.R`, `icons.R`, `blockr.ui-package.R` and `utils-pkg.R`; and the fixes to Shiny are `blockr-shiny.js`, `shiny-has-perf.js` and `shiny-input-batch.js`.

The counts of `Blockr.Select` are its occurrences in each package's `inst/`, at blockr.dplyr `68e1b54`, blockr.dm `8b37981` and blockr.ggplot `289cb60`.
The packages that import blockr.ui are blockr.assistant, blockr.cdex, blockr.dag, blockr.dm, blockr.dock, blockr.dplyr, blockr.ggplot, blockr.sandbox and blockr.session.

</details>
