# UI kit and design system for the client
Status: review. Part of [State in JS](Rewrite-1).

This part covers blockr.ui as the client's UI kit: the one copy of React on the page, React Aria's components, which every UI of blockr's packages draws with, core's among them, and the Tailwind theme and build preset that give those UIs their look.
It needs nothing from [Client-owned board state](Rewrite-1.1), whose module contract every block's UI meets, since core builds on blockr.ui rather than the other way round ([UI modules in JS](Rewrite-1.1.7#react)).

## Problem

Block UIs reach blockr.ui through page globals and Shiny UI.
Its widgets sit on `window.Blockr`, where blockr.dplyr's JS names `Blockr.Select` 30 times, blockr.dm's 18 times and blockr.ggplot's 7 times, while under the module contract a block's UI gets what it shares with the page through its host ([UI modules in JS](Rewrite-1.1.7#the-contract)).
Its R helpers draw into Shiny UIs, and its table preview implements the Shiny methods of core's `tabular_display()` hook, both of which go, since nothing in R draws UI any more ([Drawing the board](Rewrite-1.1.8#what-goes-from-r)).

On `js-state`, core holds the kit instead: the copy of React, React Aria's components in its React SDK and the Tailwind theme that gives them their look ([UI modules in JS](Rewrite-1.1.7#react)).
That ties core to one UI kit, so that an app that uses core without core's blocks and plugins, and draws with a kit of its own, still loads core's, while blockr.ui, which builds on core today, can offer core nothing.
So the kit moves to blockr.ui, which needs nothing from core, and core, the dock, the assistant and the block packages draw with blockr.ui's components.

Today's blockr.ui is no base for that kit, since its tokens, its CSS and its widgets are written by hand and are still in progress, while Tailwind's theme and the conventions of the kits built on it are refined and widely used.
So the new blockr.ui takes its look from today's, roughly, and none of its code.

## What must hold

1. The kit needs nothing from core, in R or in JS, so that core, the dock, the assistant and every block package can build on it.
2. An app that uses core without core's blocks and plugins draws with whatever it likes, and loads no React Aria where nothing draws with blockr.ui ([Board actions](Rewrite-1.1.16#roles)).
3. One copy each of React and of React Aria runs on the page, both blockr.ui's ([UI modules in JS](Rewrite-1.1.7#react)).
4. Every UI of blockr's packages, core's among them, takes its look from blockr.ui's theme under every frontend, its overlays included, and a frontend or an app restyles it by setting the theme's variables alone.
5. What blockr.ui's stylesheet provides other packages is fixed and checked, so that no change to blockr.ui drops a variable, a keyframe or a font that another package reads.
6. Nothing of blockr.ui's is a page global, but for the copy of React, which sits on a global of blockr.ui's own ([UI modules in JS](Rewrite-1.1.7#react)).

## Today

| Today, at `9bd8312` | Lines | Where it goes |
|---|---|---|
| Design tokens, the theme and base CSS, fonts, icons and the design system article | 1,223 of CSS, 10 fonts, 19 icons | Taken as cues for the look of the new theme, which starts from Tailwind's own scales and from values of its palette, while the article is written anew for the new kit (Proposal) |
| Widgets on `window.Blockr`, such as `Blockr.Select`, `Blockr.textCommit` and `Blockr.gearTray`, with their types and CSS | 3,628 of JS, 2,194 of CSS | Replaced by blockr.ui's components, which block UIs draw with: the select by `ComboBox`, the text field that commits on Enter by `TextField`, the segmented control by `ToggleButtonGroup` and the gear tray, which opens in place under its gear, by `Disclosure` ([UI modules in JS](Rewrite-1.1.7#react)) |
| R helpers that draw them into Shiny UIs: the gear tray, action menu, dropdown, shortcut hints and block marks | 646 of R | Dropped, since nothing in R draws UI, while the block's mark comes to the client in a module of blockr.ui's (Work) |
| The table preview, a display for core's `tabular_display()` hook, with its render engine | 916 of R, 94 of JS, 322 of CSS | Dropped, so that core's plain table draws every table output until a package above core offers a richer renderer, which an app names in the blockr option `renderers` ([Drawing the board](Rewrite-1.1.8#renderers)) |
| Asset dependencies and the package's own files | 423 of R | Replaced by the stylesheet that R puts on every page and the bundle that loads with the first UI that draws with blockr.ui (Proposal) |
| Fixes to Shiny's behaviour: the recalculating fade, empty input batches, and the gear tray's input binding | 285 of JS | Dropped, unless the Shiny transport needs one, since no Shiny input or output draws the board |
| On `js-state`, at `46b8b56`, the components of core's React SDK, built after React Aria's Tailwind starter kit, with core's Tailwind theme and the parts of React Aria in core's vendor file | 6,472 of TypeScript | Moved to blockr.ui, onto the jobs of its theme in place of Tailwind's palette, while core keeps the hooks over the hosts (Proposal) |

## Proposal

### What blockr.ui holds

The kit holds the one copy of React on the page, React Aria's components, which it builds after React Aria's Tailwind starter kit, and the Tailwind theme with its build preset.
Core, the dock, the assistant and the block packages draw with its components, which they import as `@blockr/ui`, while core keeps its React SDK at `@blockr/core/react`: the hooks over the hosts, such as `useValue()` and `useOutput()`, and the helpers `reactModule()` and `outputRenderer()` ([UI modules in JS](Rewrite-1.1.7#react)).
An input of blockr.ui's takes `bound`, an interface that blockr.ui defines and core's `useValue()` returns, so that blockr.ui binds no value itself and core's binding keeps the contract's rules ([UI modules in JS](Rewrite-1.1.7#the-contract)).
The components of core's React SDK on `js-state` move to blockr.ui, and so do the parts of React Aria in core's vendor file and core's Tailwind theme (Today).

Everything that core draws stays a default that an app may swap: its renderers and the UIs of its board options through the blockr option `renderers` ([Drawing the board](Rewrite-1.1.8#renderers)), its frontend and plugins as any other ([Plugins](Rewrite-1.1.12#the-frontend)), its menu of board actions through `board_action_menu`, and the board actions that play its roles through `board_actions` ([Board actions](Rewrite-1.1.16#roles)).
So an app that draws with another kit draws everything with it, and core's UIs, which draw with blockr.ui's, never load.

### Designed against Tailwind

The new blockr.ui is designed against Tailwind CSS and the conventions of the kits built on it, with shadcn/ui as the reference, whose theme holds jobs, such as `primary` with `primary-foreground`, as variables on `:root` with a value for each mode, which reach Tailwind through `@theme inline` ([theming.mdx#L39-L64](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/content/docs/%28root%29/theming.mdx?plain=1#L39-L64), [#L118-L138](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/content/docs/%28root%29/theming.mdx?plain=1#L118-L138)).
Its look roughly keeps today's, tweaked where that is warranted, and its theme starts from Tailwind's own scales, of spacing, text, radii and shadows, and from values of Tailwind's palette.
Its components draw with the jobs of the theme alone, such as a raised background or a muted text, and never with a colour of Tailwind's palette, so that an app's theme reaches every component and each job carries both modes, with no `dark:` variant.
So the classes of the palette in React Aria's starter kit, such as its button's `bg-blue-600` ([Button.tsx#L21-L23](https://github.com/adobe/react-spectrum/blob/6be3466d87cc628ee69461230c1b5f4e3b64c6e3/starters/tailwind/src/Button.tsx#L21-L23)), are rewritten onto jobs as each component is copied in, while the jobs' defaults may take their values from the palette as fixed values, and the palette itself is no part of the theme.
Which variables the theme holds, what each is for and their defaults belong to [The theme's variables](Rewrite-1.7.2).

The theme holds a colour for each status of a block and for each category of block classes, under core's names, as GitHub's Primer, the design system of one product, holds that product's states, such as `open` and `done`, beside its accent and its danger ([bgColor.json5#L410](https://github.com/primer/primitives/blob/47736486bf67b2a14ba1ada61fa0f57af29bb875/src/tokens/functional/color/bgColor.json5#L410), [#L782](https://github.com/primer/primitives/blob/47736486bf67b2a14ba1ada61fa0f57af29bb875/src/tokens/functional/color/bgColor.json5#L782)).
That is a coupling, which a new status or suggested category meets with a release of blockr.ui first, with its colour and its dot, since blockr.ui draws the block's mark and the status dot too (Work).

### Prefixes

Tailwind writes CSS only for the classes that it finds in the files it scans, so each package that writes classes builds them itself, and blockr.ui owns the rest of Tailwind: the theme, the dark variant, the choices that hold for every package, such as leaving out Tailwind's reset of the whole page and keeping utilities outside cascade layers, and the build preset that runs Tailwind at the version that the theme is written for.
The theme's variables and the classes that blockr.ui writes take the prefix `bk`, for all of blockr rather than one package, as `--bk-…` and `bk:flex`.
Every other package writes its classes under a prefix of its own, as core writes `bc:flex`, since stylesheets built apart that share a class override each other by load order ([UI modules in JS](Rewrite-1.1.7#packaging)).
Through `@theme inline` in blockr.ui's preset, a package's classes compile to reads of blockr.ui's variables, whatever the package's prefix.
The dark variant keys off `data-bk-mode`, `light` or `dark`, on the page's root, which core's board option `dark_mode` sets ([Board options and blockr options](Rewrite-1.1.13#where-the-two-meet)).
A package that writes no classes of its own, as the dock writes plain CSS today, runs no Tailwind and reads the theme's variables in its CSS.

### What the theme provides

Every package's stylesheet reads blockr.ui's variables, so a change to blockr.ui that dropped one would break another package's look without a word, since Tailwind writes a variable of its theme only where a utility that it scans uses it.
So the theme's variables, its keyframes and fonts, and the mode attribute, are a list that blockr.ui declares and exports, and:

1. Its stylesheet holds the whole list, whatever its own components use, through `@theme static`, as core's stylesheet holds the colours of statuses and categories today ([index.css#L149-L168](https://github.com/BristolMyersSquibb/blockr.core/blob/15fa6c6c43de2e02e0b42074c7e2a8a41de28889/srcts/runtime/index.css#L149-L168)).
2. Its tests compare its compiled stylesheet with the list.
3. Its preset fails a package's build whose stylesheet reads a variable of blockr.ui's that the list lacks, such as one read in plain CSS or in an arbitrary value.
4. Adding to the list takes a minor release of blockr.ui, and removing or renaming takes a major.
5. Tailwind's version is part of the contract, pinned for each major of blockr.ui, since the properties that Tailwind registers for its utilities, such as `--tw-blur`, carry no prefix, so that every package's stylesheet registers them, and stylesheets built with two versions could register them differently.

### On the page

R puts blockr.ui's stylesheet, with its theme, the app's theme and the font faces, on every page from the start, beside core's, so that everything that reads the theme finds it, core's loading note included, which R's page holds from the start.
A part that loaded later would save a page nothing that it would notice, since core's compiled stylesheet takes 10.5 KB gzipped today and a font downloads only once something uses it.
How an app's theme sets its values over those of the frontend belongs to [An app's theme](Rewrite-1.1.17).
The JS of blockr.ui, its copy of React, React Aria and its components, loads with the first module that draws with blockr.ui, which under core's basic frontend or the dock is as the page opens, so that a page that draws with none loads no React Aria ([UI modules in JS](Rewrite-1.1.7#react)).

### Block UIs

Block UIs draw with blockr.ui's components in place of today's widgets, so that blockr.dplyr, blockr.dm and blockr.ggplot port their UIs onto them ([UI modules in JS](Rewrite-1.1.7#react)).
Input elements composed in R, which would draw with blockr.ui's components, are a later project of this part, still to be decided ([Input elements for block UIs written in R](Rewrite-1.7.1)).

## Open questions

None.

## Work

- Start blockr.ui's client: its build, its bundle with the one copy of React and the parts of React Aria that its components draw with, the page's import map entries for them, and its build preset, which maps React's entry points, `react-compiler-runtime` among them, as core's preset maps them until then ([Client-drawn DAG](Rewrite-1.3#work)), refuses an import of React Aria and runs Tailwind at the version that the theme is written for, in blockr.ui
- Write the theme under the prefix `bk`, as variables on `:root` with a value for each mode, which reach Tailwind through `@theme inline`, with the colours of statuses and categories under core's names and the dark variant on `data-bk-mode`, in blockr.ui
- Declare and export the theme's list, write all of it through `@theme static`, test the compiled stylesheet against it, and have the preset fail a build that reads a variable that the list lacks, in blockr.ui
- Move the components of core's React SDK to blockr.ui, onto the theme's jobs in place of Tailwind's palette, with `bound` as an interface of blockr.ui's, in blockr.ui and blockr.core
- Draw core's UIs with `@blockr/ui`, build `blockr-core.css` with blockr.ui's preset under `bc:`, drop core's Tailwind theme and React Aria from core's vendor file, have `dark_mode` set `data-bk-mode`, and have R put blockr.ui's stylesheet on every page from the start, in blockr.core
- Import blockr.ui's components in place of those of core's React SDK, in blockr.dock and blockr.assistant
- Write the design system's article anew for the new kit, in blockr.ui
- Bring the design system's locked mode in line with block locks: under the board lock a locked block shows no UI, its reader controls included, and an open block shows all of its UI, its gear included ([UI modules in JS](Rewrite-1.1.7#the-contract), [Block cards in the dock](Rewrite-1.2.7#the-blocks-lock)), in blockr.ui
- Add `ready`, a filled dot of the success colour, and `unevaluated`, a ring of the muted text, to the design system's spec of block status, which the dock's cards and the DAG's badges share ([Block cards in the dock](Rewrite-1.2.7#the-status-dot)), in blockr.ui
- Offer the block's mark and the status dot as one module, whose tooltips blockr.ui's `Tooltip` draws, and which the dock and the DAG import in place of the copies that each draws until then, in blockr.ui ([Block cards in the dock](Rewrite-1.2.7#the-status-dot), [Client-drawn DAG](Rewrite-1.3))
- Drop the widgets on `window.Blockr`, with their types and CSS, the R helpers that draw into Shiny UIs, and the table preview with its render engine, once no package draws with them, in blockr.ui

## Design pages

- [The theme's variables: their jobs, their defaults and a frontend's values](Rewrite-1.7.2): which variables blockr.ui's theme names, what each is for and their defaults, how a frontend sets values of its own and draws its own parts with them, light mode and dark mode, and which defaults a frontend keeps
- [Input elements for block UIs written in R](Rewrite-1.7.1): input elements composed in R, with data-dependent attributes as requests of the block class, drawn with blockr.ui's components, for the later project

<details><summary>Notes for implementers</summary>

The rows of Today by file, at `9bd8312`: the design system is `blockr-tokens.css`, `blockr-tokens-dark.css`, `blockr-theme.css` and `blockr-base.css`, with `inst/assets/fonts`, `inst/assets/icons` and `vignettes/articles/design-system.Rmd`; the widgets are `blockr-ui.js`, `blockr-select.js`, `blockr-input.js` and `types.d.ts`, with every other CSS file but `blockr-table-preview.css`; the R helpers are `action-menu.R`, `block-mark.R`, `dropdown.R`, `gear-tray.R` and `shortcut.R`; the table preview is `table-preview.R`, `table-preview-render.R`, `table-preview-engine.R`, `blockr-table-preview.js` and `blockr-table-preview.css`; the dependencies and package files are `theme.R`, `controls.R`, `icons.R`, `blockr.ui-package.R` and `utils-pkg.R`; and the fixes to Shiny are `blockr-shiny.js`, `shiny-has-perf.js` and `shiny-input-batch.js`.

The components of core's React SDK at `46b8b56` are in `srcts/aria`, `srcts/inputs`, `srcts/overlays`, `srcts/layout`, `srcts/dnd`, `srcts/gridlist`, `srcts/table` and `srcts/tree`, counted without their tests, while `srcts/react` holds the hooks and the helpers that stay in core.

The counts of `Blockr.Select` are its occurrences in each package's `inst/`, at blockr.dplyr `68e1b54`, blockr.dm `8b37981` and blockr.ggplot `289cb60`.
The packages that import blockr.ui are blockr.assistant, blockr.dag, blockr.dm, blockr.dock, blockr.dplyr, blockr.ggplot and blockr.session, and those of two internal apps, the clinical data explorer among them.

</details>
