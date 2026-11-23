# UI kit and design system for the client
Status: review. Part of [State in JS](Rewrite-1).

This part covers blockr.ui as the client's UI kit: the one copy of React on the page, React Aria's components, which every UI of blockr's packages draws with, core's among them, and the Tailwind theme and build preset that give those UIs their look.
It builds on no other blockr package, since core builds on blockr.ui rather than the other way round ([UI modules in JS](Rewrite-1.1.7#react)).
How an app gives the page a theme of its own is core's ([An app's theme](Rewrite-1.1.17)).

## Problem

Block UIs reach blockr.ui through page globals and Shiny UI.
Its widgets sit on `window.Blockr`, where blockr.dplyr's JS names `Blockr.Select` 30 times, blockr.dm's 18 times and blockr.ggplot's 7 times, while under the module contract a block's UI gets what it shares with the page through its host ([UI modules in JS](Rewrite-1.1.7#the-contract)).
Its R helpers draw into Shiny UIs, and its table preview implements the Shiny methods of core's `tabular_display()` hook, both of which go, since nothing in R draws UI any more ([Drawing the board](Rewrite-1.1.8#what-goes-from-r)).

On `js-state`, core holds the kit instead: the copy of React, React Aria's components in its React SDK and the Tailwind theme that gives them their look ([UI modules in JS](Rewrite-1.1.7#react)).
That ties core to one UI kit, so that an app that uses core without core's blocks and plugins, and draws with a kit of its own, still loads core's, while blockr.ui, which builds on core today, can offer core nothing.
So the kit moves to blockr.ui, which depends on no other blockr package, and core, the dock, the assistant and the block packages draw with blockr.ui's components.

Today's blockr.ui is no base for that kit, since its tokens, its CSS and its widgets are written by hand and are still in progress, while Tailwind's theme and the conventions of the kits built on it are refined and widely used.
So the new blockr.ui takes its look from today's, roughly, and none of its code.

## What must hold

1. The kit depends on no other blockr package, in R or in JS, and holds nothing tied to theirs, such as the statuses of a block or the categories of block classes.
   It provides general-purpose components, their theme and CSS, and the build preset, so that core, the dock, the assistant and every block package can build on it.
2. An app that uses core without core's blocks and plugins draws with whatever it likes, and loads no React Aria where nothing draws with blockr.ui's components, even where it draws with React ([Board actions](Rewrite-1.1.16#roles)).
3. One copy each of React and of React Aria runs on the page, both blockr.ui's ([UI modules in JS](Rewrite-1.1.7#react)).
4. Every UI of blockr's packages, core's among them, takes its look from blockr.ui's theme under every frontend, its overlays included, and a frontend or an app restyles it by setting the theme's variables alone.
   The colours of the categories of block classes are the exception, since they are core's ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).
5. What blockr.ui's stylesheet provides other packages is fixed and checked, so that no change to blockr.ui drops a variable, a keyframe or a font that another package reads.
6. Nothing of blockr.ui's is a page global.

## Today

| Today, at `9bd8312` | Lines | Where it goes |
|---|---|---|
| Design tokens, the theme and base CSS, fonts, icons and the design system article | 1,223 of CSS, 10 fonts, 19 icons | Taken as cues for the look of the new theme, which starts from Tailwind's own scales and from values of its palette, while the colours of the categories become core's defaults ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)) and the article is written anew for the new kit (Proposal) |
| Widgets on `window.Blockr`, such as `Blockr.Select`, `Blockr.textCommit` and `Blockr.gearTray`, with their types and CSS | 3,628 of JS, 2,194 of CSS | Replaced by blockr.ui's components, which block UIs draw with: the select by `ComboBox`, the text field that commits on Enter by `TextField`, the segmented control by `ToggleButtonGroup` and the gear tray, which opens in place under its gear, by `Disclosure` ([UI modules in JS](Rewrite-1.1.7#react)) |
| R helpers that draw them into Shiny UIs: the gear tray, action menu, dropdown, shortcut hints and block marks | 646 of R | Dropped, since nothing in R draws UI, while the block's mark comes to the client in core's React SDK ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)) |
| The table preview, a display for core's `tabular_display()` hook, with its render engine | 916 of R, 94 of JS, 322 of CSS | Dropped, so that core's plain table draws every table output until a package above core offers a richer renderer, which an app names in the blockr option `renderers` ([Drawing the board](Rewrite-1.1.8#renderers)) |
| Asset dependencies and the package's own files | 423 of R | Replaced by the stylesheet that R puts on every page and the files of blockr.ui's bundle, which load with the first UI that draws with blockr.ui ([Building on blockr.ui](Rewrite-1.7.4)) |
| Fixes to Shiny's behaviour: the recalculating fade, empty input batches, and the gear tray's input binding | 285 of JS | Dropped, unless the Shiny transport needs one, since no Shiny input or output draws the board |
| On `js-state`, at `79507c4`, the components of core's React SDK, built after React Aria's Tailwind starter kit, with core's Tailwind theme and the parts of React Aria in core's vendor file | 6,473 of TypeScript | Moved to blockr.ui, onto the jobs of its theme in place of Tailwind's palette, while core keeps the hooks over the hosts ([The components of blockr.ui](Rewrite-1.7.3)) |

## Proposal

### What blockr.ui holds

The kit holds the one copy of React on the page, React Aria's components, which it builds after React Aria's Tailwind starter kit, and the Tailwind theme with its build preset.
Core, the dock, the assistant and the block packages draw with its components, which they import as `@blockr/ui` ([The components of blockr.ui](Rewrite-1.7.3)).
Core keeps its React SDK at `@blockr/core/react`: the hooks over the hosts, such as `useValue()` and `useOutput()`, the helpers `reactModule()` and `outputRenderer()`, and what reads core's own types, such as the block's mark and status dot ([UI modules in JS](Rewrite-1.1.7#react), [Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).
An input of blockr.ui's takes `bound`, an interface that blockr.ui defines and core's `useValue()` returns, so that blockr.ui binds no value itself and core's binding keeps the contract's rules ([The components of blockr.ui](Rewrite-1.7.3#the-interface-bound)).
The components of core's React SDK on `js-state` move to blockr.ui, and so do the parts of React Aria in core's vendor file and core's Tailwind theme (Today).

Everything that the kit holds is general-purpose, so that any page could draw with it: a component knows no block, and a variable of the theme names no status.
What blockr's packages share beyond the kit, such as the block's mark, is core's.

Everything that core draws stays a default that an app may swap: its renderers and the UIs of its board options through the blockr option `renderers` ([Drawing the board](Rewrite-1.1.8#renderers)), its frontend and plugins as any other ([Plugins](Rewrite-1.1.12#the-frontend)), its menu of board actions through `board_action_menu`, and the board actions that play its roles through `board_actions` ([Board actions](Rewrite-1.1.16#roles)).
So an app that draws with another kit draws everything with it, and core's UIs, which draw with blockr.ui's, never load.

### Designed against Tailwind

The new blockr.ui is designed against Tailwind CSS and the conventions of the kits built on it, with shadcn/ui as the reference, whose theme holds jobs, such as `primary` with `primary-foreground`, as variables on `:root` with a value for each mode, which reach Tailwind through `@theme inline` ([theming.mdx#L39-L64](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/content/docs/%28root%29/theming.mdx?plain=1#L39-L64), [#L118-L138](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/content/docs/%28root%29/theming.mdx?plain=1#L118-L138)).
Its look roughly keeps today's, tweaked where that is warranted, and its theme starts from Tailwind's own scales, of spacing, text, radii and shadows, and from values of Tailwind's palette.
Its components draw with the jobs of the theme alone, such as a raised background or a muted text, and never with a colour of Tailwind's palette, so that an app's theme reaches every component and each job carries both modes, with no `dark:` variant.
So the classes of the palette in React Aria's starter kit, such as its button's `bg-blue-600` ([Button.tsx#L21-L23](https://github.com/adobe/react-spectrum/blob/6be3466d87cc628ee69461230c1b5f4e3b64c6e3/starters/tailwind/src/Button.tsx#L21-L23)), are rewritten onto jobs as each component is copied in, while the jobs' defaults may take their values from the palette as fixed values, and the palette itself is no part of the theme.
Which variables the theme holds, what each is for and their defaults belong to [The theme's variables](Rewrite-1.7.2).

The theme's jobs are general, such as danger and success, and none is named after something of core's.
Core maps each status of a block onto a job, as `failed` onto the danger border, and holds the colours of the categories of block classes itself, outside every theme, which an app sets through a blockr option ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).
So a new status or category is a change to core alone.

### Building on blockr.ui

The theme's variables and the classes that blockr.ui writes take the prefix `bk`, and every other package writes its classes under a prefix of its own, as core writes `bc:flex`.
Through `@theme inline` in blockr.ui's build preset, a package's classes compile to reads of blockr.ui's variables ([Building on blockr.ui](Rewrite-1.7.4#prefixes)).
What the theme provides other packages is a list that blockr.ui declares and exports, which its stylesheet holds whole and against which the preset checks every package's build ([Building on blockr.ui](Rewrite-1.7.4#the-themes-list)).
R puts blockr.ui's stylesheet on every page from the start, while its JS loads with the first module that draws with blockr.ui, with React in a file of its own, so that a page that draws with React but with none of blockr.ui's components loads no React Aria ([Building on blockr.ui](Rewrite-1.7.4#the-bundle)).
How an app's theme sets its values over those of the frontend belongs to [An app's theme](Rewrite-1.1.17).

### Block UIs

Block UIs draw with blockr.ui's components in place of today's widgets, so that blockr.dplyr, blockr.dm and blockr.ggplot port their UIs onto them ([UI modules in JS](Rewrite-1.1.7#react)).
Composing a block's UI in R from blockr.ui's components is a later project, not decided, which the [Backlog](Backlog#block-uis-composed-in-r) holds with a way to build it that keeps blockr.ui free of blocks.

## Open questions

None.

## Work

- Start blockr.ui's client, in blockr.ui ([Building on blockr.ui](Rewrite-1.7.4)): its build, with its preset as `@blockr/ui/build`, which maps React's entry points and resolves the React Compiler's runtime to React's, as core's preset does until then ([Client-drawn DAG](Rewrite-1.3#work)), refuses an import of React Aria and runs Tailwind at the version that the theme is written for; its bundle, with React in a file of its own, the components in another and the parts of React Aria that they draw with in a third; and the entries of the page's import map for them
- Write the theme under the prefix `bk`, as variables on `:root` with a value for each mode, which reach Tailwind through `@theme inline`, with the dark variant on `data-bk-mode`, in blockr.ui ([The theme's variables](Rewrite-1.7.2))
- Declare and export the theme's list, write all of it through `@theme static`, test the compiled stylesheet against it, and have the preset fail a build that reads a variable that the list lacks or names a colour of Tailwind's palette, in blockr.ui ([Building on blockr.ui](Rewrite-1.7.4#the-themes-list))
- Move the components of core's React SDK to blockr.ui, onto the theme's jobs in place of Tailwind's palette, with `Bound` as an interface of blockr.ui's and a stub of it for tests, and `Stack` renamed `FormLayout`, in blockr.ui and blockr.core ([The components of blockr.ui](Rewrite-1.7.3))
- Draw core's UIs with `@blockr/ui`, build `blockr-core.css` with blockr.ui's preset under `bc:`, have core's preset extend blockr.ui's, drop core's Tailwind theme and React Aria from core's vendor file, have `dark_mode` set `data-bk-mode`, and have R put blockr.ui's stylesheet on every page from the start, in blockr.core ([Building on blockr.ui](Rewrite-1.7.4))
- Offer the block's mark and the status dot in core's React SDK, drawn with blockr.ui's components, with each status on the theme's job for it and the colours of the categories from the blockr option `category_colors`, which R writes into the page's head, in blockr.core ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot))
- Import blockr.ui's components in place of those of core's React SDK, in blockr.dock and blockr.assistant
- Draw core's mark and status dot on the dock's cards and on the DAG's nodes, in place of the copies that each draws until then, in blockr.dock and blockr.graph ([Block cards in the dock](Rewrite-1.2.7#the-status-dot), [Drawing the DAG](Rewrite-1.3.2#nodes))
- Write the design system's article anew for the new kit, in blockr.ui
- Drop the widgets on `window.Blockr`, with their types and CSS, the R helpers that draw into Shiny UIs, and the table preview with its render engine, once no package draws with them, in blockr.ui

## Design pages

- [Building on blockr.ui: the build preset, the bundle and the stylesheet on the page](Rewrite-1.7.4): how a package builds against blockr.ui through its build preset, with its React half and its Tailwind half, the prefixes, the theme's list as a contract, the bundle with React in a file of its own, and the stylesheet on the page
- [The theme's variables: their jobs, their defaults and a frontend's values](Rewrite-1.7.2): which variables blockr.ui's theme names, what each is for and their defaults, how a frontend sets values of its own and draws its own parts with them, light mode and dark mode, and which defaults a frontend keeps
- [The components of blockr.ui: the first set, `bound` and their tests](Rewrite-1.7.3): the components that blockr.ui offers after React Aria's starter kit, the first set from core's React SDK, the interface `Bound` through which an input takes its value, and their tests

<details><summary>Notes for implementers</summary>

The rows of Today by file, at `9bd8312`: the design system is `blockr-tokens.css`, `blockr-tokens-dark.css`, `blockr-theme.css` and `blockr-base.css`, with `inst/assets/fonts`, `inst/assets/icons` and `vignettes/articles/design-system.Rmd`; the widgets are `blockr-ui.js`, `blockr-select.js`, `blockr-input.js` and `types.d.ts`, with every other CSS file but `blockr-table-preview.css`; the R helpers are `action-menu.R`, `block-mark.R`, `dropdown.R`, `gear-tray.R` and `shortcut.R`; the table preview is `table-preview.R`, `table-preview-render.R`, `table-preview-engine.R`, `blockr-table-preview.js` and `blockr-table-preview.css`; the dependencies and package files are `theme.R`, `controls.R`, `icons.R`, `blockr.ui-package.R` and `utils-pkg.R`; and the fixes to Shiny are `blockr-shiny.js`, `shiny-has-perf.js` and `shiny-input-batch.js`.

The components of core's React SDK at `79507c4` are in `srcts/aria`, `srcts/inputs`, `srcts/overlays`, `srcts/layout`, `srcts/dnd`, `srcts/gridlist`, `srcts/table` and `srcts/tree`, counted without their tests, while `srcts/react` holds the hooks and the helpers that stay in core.

The counts of `Blockr.Select` are its occurrences in each package's `inst/`, at blockr.dplyr `68e1b54`, blockr.dm `8b37981` and blockr.ggplot `289cb60`.
The packages that import blockr.ui are blockr.assistant, blockr.dag, blockr.dm, blockr.dock, blockr.dplyr, blockr.ggplot and blockr.session, and those of two internal apps, the clinical data explorer among them.

</details>
