# UI kit and design system for the client
Status: implementing in [blockr#514](https://github.com/orgs/BristolMyersSquibb/discussions/514). Part of [State in JS](Rewrite-1).

This part covers blockr.ui as the client's UI kit: the one copy each of React and of React Aria on the page, React Aria's components and Lucide's icons, which every UI of blockr's packages draws with, core's among them, the theme variables that give those UIs their look, and the build preset through which every package builds against them.
It builds on no other blockr package, since core builds on blockr.ui rather than the other way round ([UI modules in JS](Rewrite-1.1.7#react)).
It covers an app's theme too, which sets values of the theme variables for one app, and which core's `serve()` takes ([An app's theme](Rewrite-1.7.5)).

## Problem

Block UIs reach blockr.ui through page globals and Shiny UI.
Its widgets sit on `window.Blockr`, where blockr.dplyr's JS names `Blockr.Select` 30 times, blockr.dm's 22 times and blockr.ggplot's 7 times.
In the new stack, a block's UI is a module, which imports what it shares with the page, such as React, through the page's import map ([UI modules in JS](Rewrite-1.1.7#react)).
Its R helpers draw into Shiny UIs, and its table preview implements the Shiny methods of core's `tabular_display()` hook, both of which go, since nothing in R draws UI any more ([Drawing the board](Rewrite-1.1.8#what-goes-from-r)).

On `js-state`, core holds the kit instead: the copy of React, React Aria's components in its React SDK, and its own Tailwind theme, which gives them their look ([The components of blockr.ui](Rewrite-1.7.3#today)).
That ties core to one UI kit, so that an app that uses core without core's blocks and plugins, and draws with a kit of its own, still loads core's, while blockr.ui, which builds on core today, can offer core nothing.
So the kit moves to blockr.ui, which depends on no other blockr package, and core, the dock, the assistant and the block packages draw with blockr.ui's components.

Today's blockr.ui is no base for that kit, since its tokens, its CSS and its widgets are written by hand and are still in progress, while Tailwind's theme and the conventions of the kits built on it are refined and widely used.
So the new blockr.ui takes its look from today's, roughly, and none of its code.

## What must hold

1. The kit depends on no other blockr package, in R or in JS, and holds nothing tied to theirs, such as the statuses of a block or the categories of block classes.
   It provides general-purpose components, their theme variables and CSS, and the build preset, so that core, the dock, the assistant and every block package can build on it.
2. An app that uses core without core's blocks and plugins draws with whatever it likes, and loads no React Aria where nothing draws with blockr.ui's components or with React Aria's, even where it draws with React ([Board actions](Rewrite-1.1.16#roles)).
3. One copy each of React and of React Aria runs on the page, both blockr.ui's ([UI modules in JS](Rewrite-1.1.7#react)).
4. Every UI of blockr's packages, core's among them, takes its look from the theme variables under every frontend, its overlays included, and a frontend or an app restyles it by setting those variables alone.
   The colours of the categories of block classes are the exception, since they are core's ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)), and so are the black and white that must stand out on any colour, such as a modal's backdrop ([The theme variables](Rewrite-1.7.2#what-must-hold)).
5. What blockr.ui's stylesheet provides other packages is a list that blockr.ui declares and checks, so that only a major release of blockr.ui drops or renames a variable or a font that another package reads ([Building on blockr.ui](Rewrite-1.7.4#what-must-hold)).
6. Nothing of blockr.ui's is a page global.

## Today

| Today, at `e14e831` | Lines | Where it goes |
|---|---|---|
| Design tokens, and the theme and base CSS | 1,223 of CSS | Their values become the defaults of the theme variables: each colour takes the value of today's token with the same job, and the sizes of text, the radii and the shadows take today's values where today's look departs from Tailwind's scales ([The theme variables](Rewrite-1.7.2#the-defaults)). The colours of the categories become core's defaults ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)), and the rules that restyle Bootstrap's elements and Shiny's inputs go ([Building on blockr.ui](Rewrite-1.7.4#today)) |
| Open Sans, in 8 files for its scripts and styles, with its licence and its faces | 10 files | Carried over, as the default of `--bk-font-sans`, whose faces blockr.ui's stylesheet writes ([The theme variables](Rewrite-1.7.2#the-defaults), [Building on blockr.ui](Rewrite-1.7.4#the-list-of-theme-variables)) |
| Small icons, such as `plus`, `trash` and `gear`, which `small_icon()` draws in R and `Blockr.icons` offers in JS | 19 icons | Replaced by Lucide's icons, whose stroked lines with round caps are the style of 14 of the 19, and which blockr.ui offers through `@blockr/ui/icons`, from which each package's build bundles the icons that it imports ([The components of blockr.ui](Rewrite-1.7.3#the-icons)) |
| The design system's article | 1,693 of R Markdown | Written anew for the new kit (Work) |
| Widgets on `window.Blockr`, such as `Blockr.Select`, `Blockr.textCommit` and `Blockr.gearTray`, with their types and CSS | 4,123 of JS, 2,243 of CSS | Replaced by blockr.ui's components, which block UIs draw with: the select by `ComboBox`, the text field that commits on Enter by `TextField`, the segmented control by `ToggleButtonGroup` and the gear tray, which opens in place under its gear, by `Disclosure` ([UI modules in JS](Rewrite-1.1.7#react)) |
| R helpers that draw them into Shiny UIs: the gear tray, action menu, dropdown, shortcut hints and block marks | 646 of R | Dropped, since nothing in R draws UI, while the block's mark comes to the client in core's React SDK ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)) |
| The table preview, a display for core's `tabular_display()` hook, with its render engine | 916 of R, 94 of JS, 322 of CSS | Dropped, so that core's plain table draws every table output until a package above core offers a richer renderer, which an app names in the blockr option `renderers` ([Drawing the board](Rewrite-1.1.8#renderers)) |
| Asset dependencies and the package's own files | 423 of R | Replaced by the stylesheet that R puts on every page and the files of blockr.ui's bundle, which load with the first UI that draws with blockr.ui ([Building on blockr.ui](Rewrite-1.7.4)) |
| Fixes to Shiny's behaviour: the recalculating fade, empty input batches, and the gear tray's input binding | 285 of JS | Dropped, unless the Shiny transport needs one, since no Shiny input or output draws the board |
| On `js-state`, at `79507c4`, the components of core's React SDK, built after React Aria's Tailwind starter kit, with core's Tailwind theme and the parts of React Aria in core's vendor file | 6,473 of TypeScript | Moved to blockr.ui, onto the theme variables in place of Tailwind's palette, while core keeps the hooks over the hosts ([The components of blockr.ui](Rewrite-1.7.3)) |

## Proposal

### What blockr.ui holds

The kit holds the one copy of React on the page, React Aria's components, which it builds after React Aria's Tailwind starter kit, the theme variables with their defaults, and its build preset.
It holds what makes a theme as well: its `new_blockr_theme()` makes one in R, for an app or for a frontend, and core's `serve()` writes both into the page's head, so that a package that makes themes builds on blockr.ui alone ([An app's theme](Rewrite-1.7.5), [The theme variables](Rewrite-1.7.2#where-the-values-are-set)).
It holds the one copy of React Aria too, the whole of it: its components, the hooks that they are built from and the state that the hooks keep.
A UI imports React Aria's own parts from it, as `react-aria-components`, `react-aria` and `react-stately`, for what no component of blockr.ui does, such as a table that draws thousands of cells without hooks in each ([Building on blockr.ui](Rewrite-1.7.4#the-build-preset)).
Core, the dock, the assistant and the block packages draw with its components, which they import as `@blockr/ui` ([The components of blockr.ui](Rewrite-1.7.3)).
They draw their icons from Lucide's set, which blockr.ui offers through an entry of its own, `@blockr/ui/icons`, and from which each package's build bundles the icons that it imports ([The components of blockr.ui](Rewrite-1.7.3#the-icons)).
So a package draws any of Lucide's icons without a change to blockr.ui, and a page loads only those that its packages draw.
Core keeps its React SDK in two entries, so that a UI that binds its values with core's hooks loads no React Aria ([Building on blockr.ui](Rewrite-1.7.4#the-bundle)).
The entry `@blockr/core/react` holds the hooks over the hosts, such as `useValue()` and `useOutput()`, and the helpers `reactModule()` and `outputRenderer()` ([UI modules in JS](Rewrite-1.1.7#react)).
The entry `@blockr/core/components` holds what reads core's own types and draws with blockr.ui's components, such as the block's mark and status dot ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).
An input of blockr.ui's takes `bound`, an interface that blockr.ui defines and core's `useValue()` returns, so that blockr.ui binds no value itself and core's binding keeps the contract's rules ([The components of blockr.ui](Rewrite-1.7.3#the-interface-bound)).
The components of core's React SDK on `js-state` move to blockr.ui, and so do the parts of React Aria in core's vendor file and core's Tailwind theme (Today).

Everything that the kit holds is general-purpose, so that any page could draw with it: a component knows no block, and no theme variable names a status.
What blockr's packages share beyond the kit, such as the block's mark, is core's.

Everything that core draws but the UIs of its board options stays a default that an app may swap: its renderers through the blockr option `renderers` ([Drawing the board](Rewrite-1.1.8#renderers)), its frontend and plugins as any other ([Plugins](Rewrite-1.1.12#the-frontend)), its menu of board actions through `board_action_menu`, and the board actions that play its roles through `board_actions` ([Board actions](Rewrite-1.1.16#roles)).
So an app that swaps all of them for UIs drawn with another kit, and shows no other package's UI, never loads core's UIs, which draw with blockr.ui's components ([Building on blockr.ui](Rewrite-1.7.4#the-bundle)).

### Designed against Tailwind

The new blockr.ui is designed against Tailwind CSS and the conventions of the kits built on it, with shadcn/ui as the reference, whose theme holds jobs, such as `primary` with `primary-foreground`, as variables on `:root` with a value for each mode, which reach Tailwind through `@theme inline` ([theming.mdx#L39-L64](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/content/docs/%28root%29/theming.mdx?plain=1#L39-L64), [#L118-L138](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/content/docs/%28root%29/theming.mdx?plain=1#L118-L138)).
Its look roughly keeps today's, tweaked where that is warranted.
So the default of each colour is the value of today's token with the same job, and the sizes of text, the radii, the shadows and the spacing take Tailwind's own scales, with today's values where today's look departs from them ([The theme variables](Rewrite-1.7.2#the-defaults)).
Its components draw with the theme variables alone, such as a raised background or a muted text, and never with a colour of Tailwind's palette, so that an app's theme reaches every component and each job carries both modes, with no `dark:` variant.
So the classes of the palette in React Aria's starter kit, such as its button's `bg-blue-600` ([Button.tsx#L21-L23](https://github.com/adobe/react-spectrum/blob/6be3466d87cc628ee69461230c1b5f4e3b64c6e3/starters/tailwind/src/Button.tsx#L21-L23)), are rewritten onto jobs as each component is copied in, while the jobs' defaults may take their values from the palette as fixed values, and the palette itself is no part of the theme variables.
Which theme variables there are, what each is for and their defaults belong to [The theme variables](Rewrite-1.7.2).

The theme variables do general jobs, such as `destructive` and `success`, and none is named after something of core's.
Core maps each status of a block onto a job, as `failed` onto `destructive`, and holds the colours of the categories of block classes itself, outside every theme, which an app sets through a blockr option ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).
So a new status or category is a change to core alone.

### Building on blockr.ui

The theme variables and the classes that blockr.ui writes take the prefix `bk`, and every other package writes its classes under a prefix of its own, as core writes `bc:flex`.
Through `@theme inline reference` in blockr.ui's build preset, a package's classes compile to reads of blockr.ui's variables, blockr.ui's own included ([Building on blockr.ui](Rewrite-1.7.4#prefixes)).
The theme variables that blockr.ui provides other packages are a list that it declares and exports, which its stylesheet holds whole and against which the preset checks every package's build ([Building on blockr.ui](Rewrite-1.7.4#the-list-of-theme-variables)).
R puts blockr.ui's stylesheet on every page from the start, while its JS loads with the first module that draws with blockr.ui, with React in a file of its own, so that a page that draws with React, but neither with blockr.ui's components nor with React Aria's, loads no React Aria ([Building on blockr.ui](Rewrite-1.7.4#the-bundle)).
Which value wins on the page, blockr.ui's default, the frontend's or the app's, belongs to [The theme variables](Rewrite-1.7.2#where-the-values-are-set).

Core's board option `dark_mode` switches the page between light mode and dark mode, through the attribute `data-bk-mode` on the page's root.
Its value stays with the user, in the browser, so a line that R writes into the page's head sets the mode before the first paint ([The theme variables](Rewrite-1.7.2#light-mode-and-dark-mode)).

### Block UIs

Block UIs draw with blockr.ui's components in place of today's widgets, so that blockr.dplyr, blockr.dm and blockr.ggplot port their UIs onto them ([UI modules in JS](Rewrite-1.1.7#react)).
Composing a block's UI in R from blockr.ui's components is a later project, not decided, which the [Backlog](Backlog#block-uis-composed-in-r) holds with a way to build it that keeps blockr.ui free of blocks.

## Open questions

None.

## Work

The spec [blockr#514](https://github.com/orgs/BristolMyersSquibb/discussions/514) holds the Work list from here, each item with its issue.

## Design pages

- [Building on blockr.ui: the build preset, the bundle and the stylesheet on the page](Rewrite-1.7.4): how a package builds against blockr.ui through its build preset, with its React half and its Tailwind half, the prefixes, the list of theme variables as a contract, the bundle with React in a file of its own, and the stylesheet on the page
- [The theme variables: their jobs, their defaults and a frontend's values](Rewrite-1.7.2): which theme variables blockr.ui declares, what each is for and their defaults, how a frontend gives values of its own, as a theme, and draws its own parts with them, which value wins on the page, light mode and dark mode, and which defaults a frontend keeps
- [An app's theme: `new_blockr_theme()`, the argument `theme` of `serve()` and the rules that R writes](Rewrite-1.7.5): how an app gives the page a theme of its own, which blockr.ui's `new_blockr_theme()` makes and core's `serve()` takes, and the rules that R writes into the page
- [The components of blockr.ui: the first set, the icons, `bound` and their tests](Rewrite-1.7.3): the components that blockr.ui offers after React Aria's starter kit, the first set from core's React SDK, the icons from Lucide's set, the interface `Bound` through which an input takes its value, and their tests

<details><summary>Notes for implementers</summary>

The rows of Today by file, at `e14e831`: the design tokens and the theme and base CSS are `blockr-tokens.css`, `blockr-tokens-dark.css`, `blockr-theme.css` and `blockr-base.css`; Open Sans is in `inst/assets/fonts`, the icons are in `inst/assets/icons`, and the article is `vignettes/articles/design-system.Rmd`; the widgets are `blockr-ui.js`, `blockr-select.js`, `blockr-input.js` and `types.d.ts`, with every other CSS file but `blockr-table-preview.css`; the R helpers are `action-menu.R`, `block-mark.R`, `dropdown.R`, `gear-tray.R` and `shortcut.R`; the table preview is `table-preview.R`, `table-preview-render.R`, `table-preview-engine.R`, `blockr-table-preview.js` and `blockr-table-preview.css`; the dependencies and package files are `theme.R`, `controls.R`, `icons.R`, `blockr.ui-package.R` and `utils-pkg.R`; and the fixes to Shiny are `blockr-shiny.js`, `shiny-has-perf.js` and `shiny-input-batch.js`.

The components of core's React SDK at `79507c4` are in `srcts/aria`, `srcts/inputs`, `srcts/overlays`, `srcts/layout`, `srcts/dnd`, `srcts/gridlist`, `srcts/table` and `srcts/tree`, counted without their tests, while `srcts/react` holds the hooks and the helpers that stay in core.

The counts of `Blockr.Select` are its occurrences in each package's `inst/`, at blockr.dplyr `58f232f`, blockr.dm `dbe8502` and blockr.ggplot `262a263`.
On main, the packages that import blockr.ui are blockr.assistant, blockr.dag, blockr.dm, blockr.dock, blockr.dplyr, blockr.ggplot and blockr.session, and those of two internal apps, the clinical data explorer among them.
Scripts in blockr.dm, blockr.dplyr, blockr.io and blockr.ui, and in the clinical data explorer's repos, pick the table preview with `options(blockr.tabular_display = blockr.ui::html_table_display)`.

On main, blockr.ui imports blockr.core, for `pkg_name()` and for the methods of `tabular_display()` that the table preview implements, and pins it in `Remotes:` ([DESCRIPTION](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/DESCRIPTION)).
Core's `js-state` has no `tabular_display()`, and no package's `js-state` imports blockr.ui, so the first item of Work drops what needs core, and nothing on `js-state` loses a widget.
The table preview's page size is core's board option, which `new_page_size_option()` makes ([R/table-preview-render.R#L156-L158](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/R/table-preview-render.R#L156-L158)), so no file of today's stack holds anything of blockr.ui's, and blockr.convert holds no method for it.

On `js-state`, core's documentation of `renderers` and its error for an invalid value of that blockr option name `blockr.ui::table_preview()` as an example, which no package will offer ([R/output-renderer.R#L62-L66](https://github.com/BristolMyersSquibb/blockr.core/blob/8b817996fa17b8cd11b258c50a31e513625b2182/R/output-renderer.R#L62-L66), [#L170-L178](https://github.com/BristolMyersSquibb/blockr.core/blob/8b817996fa17b8cd11b258c50a31e513625b2182/R/output-renderer.R#L170-L178)).

On `js-state`, the dock, the assistant and blockr.graph import `staticImports()` and `vendorCheck()` from `@blockr/core/build`, and [blockr.core#721](https://github.com/BristolMyersSquibb/blockr.core/issues/721) adds a function to the vendor check, which moves to blockr.ui's preset with it.
The assistant's stylesheet reads core's theme, as `--bc-color-text-default`, and keys the colour of its links in dark mode on `data-bc-theme` ([index.css#L46-L73](https://github.com/BristolMyersSquibb/blockr.assistant/blob/4a3142df3016309a8ba38776b17f221e6d70de64/srcts/modules/assistant_plugin/index.css#L46-L73)).
The DAG builds against core's theme and core's React SDK until blockr.ui has a `js-state` ([blockr.graph#4](https://github.com/BristolMyersSquibb/blockr.graph/issues/4)).

On `js-state`, core, the dock and the assistant draw their icons as SVG of their own.
Core draws two chevrons, a tick, a dash, a cross and a magnifier in `srcts/inputs/icons.tsx`, a grip in `srcts/dnd/dnd.tsx` and the plus of its board actions in `srcts/actions/icons.ts`.
The dock draws a chevron, a warning, a padlock, a check, a grip, a plus, a cross, the sliders and a pin in `srcts/modules/dock/icons.tsx`, and the sliders, the eye, the padlocks and the dots of its card in `srcts/modules/dock/card/icons.tsx` ([icons.tsx#L1-L6](https://github.com/BristolMyersSquibb/blockr.dock/blob/5d9a4764709d0e3a391117855c0434cf06034bfb/srcts/modules/dock/icons.tsx#L1-L6)).
The assistant draws its icons inline, in the files of `srcts/chat`.
In Lucide, core's and the dock's are `ChevronDown`, `ChevronRight`, `Check`, `Minus`, `X`, `Search`, `GripVertical`, `Plus`, `TriangleExclamationPoint`, `Lock`, `LockOpen`, `SlidersHorizontal`, `Pin`, `Eye` and `Ellipsis`.

</details>
