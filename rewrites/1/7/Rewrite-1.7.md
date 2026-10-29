# UI kit and design system for the client
Status: draft. Part of [State in JS](Rewrite-1).

This part covers blockr.ui: the design system that core's client, the dock and the extensions follow, the widgets block packages draw with today, the table preview it adds as a renderer of the output family `blockr.core-table`, and the one copy of React on the page, with the React SDK that block UIs are written with. It builds on [Client-owned board state](Rewrite-1.1), whose module contract every block's UI meets ([UI modules in JS](Rewrite-1.1.7)), and holds the later project of ready-made components for form-like block UIs, which is still to be decided.

## Problem

Block UIs reach blockr.ui through page globals and Shiny UI. Its widgets sit on `window.Blockr`, where blockr.dplyr's JS names `Blockr.Select` 30 times, blockr.dm's 18 times and blockr.ggplot's 7 times, while under the module contract a block's UI gets what it shares with the page through its host ([UI modules in JS](Rewrite-1.1.7#the-contract)). Its R helpers draw into Shiny UIs, and its table preview implements the Shiny methods of core's `tabular_display()` hook, both of which go, since nothing in R draws UI any more ([Front-ends and extension points](Rewrite-1.1.8#what-goes-from-r)).

## What must hold

1. The design system documented in blockr.ui stays valid, and core's client, the dock and the extensions follow it, as condition 6 of [State in JS](Rewrite-1#what-must-hold) has it.
2. A block UI written in React gets React and the React SDK from blockr.ui through its build, under every front-end, core's basic one included, and the dock uses the same copy ([UI modules in JS](Rewrite-1.1.7#react)).
3. Whatever else blockr.ui offers block UIs reaches them through the host, as any package's module does, and none of it is a page global.

## Today

| Today, at `9bd8312` | Lines | Where it goes |
|---|---|---|
| Design tokens, the theme and base CSS, fonts, icons and the design system article | 1,223 of CSS, 10 fonts, 19 icons | Carried over, as the design system the client follows |
| Widgets on `window.Blockr`, such as `Blockr.Select`, `Blockr.textCommit` and `Blockr.gearTray`, with their types and CSS | 3,628 of JS, 2,194 of CSS | Open (below), since they reach block UIs as page globals |
| R helpers that draw them into Shiny UIs: the gear tray, action menu, dropdown, shortcut hints and block marks | 646 of R | Open (below), since nothing in R draws UI |
| The table preview, a display for core's `tabular_display()` hook, with its render engine | 916 of R, 94 of JS, 322 of CSS | Carried over as a renderer of the output family `blockr.core-table`, which takes the place of core's plain table wherever blockr.ui is loaded ([Front-ends and extension points](Rewrite-1.1.8#renderers)) |
| Asset dependencies and the package's own files | 423 of R | Replaced by however the client loads blockr.ui's assets (below) |
| Fixes to Shiny's behaviour: the recalculating fade, empty input batches, and the gear tray's input binding | 285 of JS | Dropped, unless the bridge needs one, since no Shiny input or output draws the board |

## Proposal

- As the UI kit, blockr.ui keeps the design system that core's client, the dock and the extensions follow.
- Block UIs are modules written against core's contract ([UI modules in JS](Rewrite-1.1.7)), so blockr.ui's widgets stop being page globals, and whatever else blockr.ui offers block UIs from then on reaches them through the host.
- The one copy of React on the page ships with blockr.ui, with the React SDK and the build preset that maps `react` to it, so that core ships no React while a block UI written in React still finds it under every front-end, since its package imports blockr.ui. The dock and its extensions use the same copy ([UI modules in JS](Rewrite-1.1.7#react)).
- Ready-made components for form-like block UIs are a later project of this part, still to be decided, and so are input elements composed in R on top of them ([Input elements for block UIs written in R](Rewrite-1.7.1)).

## Open questions

- What else blockr.ui offers block UIs in place of its widgets, and when: ready-made components, the input elements of [Input elements for block UIs written in R](Rewrite-1.7.1) on top of them, or nothing until the block packages have ported. It decides whether blockr.dplyr, blockr.dm and blockr.ggplot port their UIs onto blockr.ui's components or write their own.
- Where the design tokens live, since core's client follows them while blockr.ui builds on blockr.core, and how the client loads them, now that they no longer arrive as HTML dependencies of Shiny UI.
- What becomes of the R helpers, which draw into Shiny UIs today.

## Work

- Ship React, one copy for the page, with the React SDK that block UIs are written with and the build preset that maps `react` to it, inside the R package, in blockr.ui
- Port the table preview to a renderer of the output family `blockr.core-table`, paging and sorting through the output's `meta`, in blockr.ui

## Design pages

- [Input elements for block UIs written in R](Rewrite-1.7.1): input elements composed in R, with data-dependent attributes as requests of the block class, for the later project

<details><summary>Notes for implementers</summary>

The rows of Today by file, at `9bd8312`: the design system is `blockr-tokens.css`, `blockr-tokens-dark.css`, `blockr-theme.css` and `blockr-base.css`, with `inst/assets/fonts`, `inst/assets/icons` and `vignettes/articles/design-system.Rmd`; the widgets are `blockr-ui.js`, `blockr-select.js`, `blockr-input.js` and `types.d.ts`, with every other CSS file but `blockr-table-preview.css`; the R helpers are `action-menu.R`, `block-mark.R`, `dropdown.R`, `gear-tray.R` and `shortcut.R`; the table preview is `table-preview.R`, `table-preview-render.R`, `table-preview-engine.R`, `blockr-table-preview.js` and `blockr-table-preview.css`; the dependencies and package files are `theme.R`, `controls.R`, `icons.R`, `blockr.ui-package.R` and `utils-pkg.R`; and the fixes to Shiny are `blockr-shiny.js`, `shiny-has-perf.js` and `shiny-input-batch.js`.

The counts of `Blockr.Select` are its occurrences in each package's `inst/`, at blockr.dplyr `68e1b54`, blockr.dm `8b37981` and blockr.ggplot `289cb60`. The packages that import blockr.ui are blockr.assistant, blockr.cdex, blockr.dag, blockr.dm, blockr.dock, blockr.dplyr, blockr.ggplot, blockr.sandbox and blockr.session.

</details>
