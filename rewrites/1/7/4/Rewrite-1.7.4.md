# Building on blockr.ui: the build preset, the bundle and the stylesheet on the page
Status: settled on 2026-11-24. Design for [UI kit and design system for the client](Rewrite-1.7).

One of the designs for blockr.ui as the client's UI kit ([UI kit and design system for the client](Rewrite-1.7)): how a package builds its modules and its classes against blockr.ui through blockr.ui's build preset, which files blockr.ui's own build writes, and what of them R puts on the page.
It shapes the issues of [UI kit and design system for the client](Rewrite-1.7#work) that start blockr.ui's client, [blockr.ui#108](https://github.com/BristolMyersSquibb/blockr.ui/issues/108), write the theme variables, [blockr.ui#109](https://github.com/BristolMyersSquibb/blockr.ui/issues/109), declare their list, [blockr.ui#110](https://github.com/BristolMyersSquibb/blockr.ui/issues/110), build core's stylesheet with the preset, [blockr.core#866](https://github.com/BristolMyersSquibb/blockr.core/issues/866), and split core's React SDK, [blockr.core#869](https://github.com/BristolMyersSquibb/blockr.core/issues/869).
The issues that drop today's code from blockr.ui, offer the icons, move the dock, the assistant and the DAG, draw their icons and write the design system's article rely on it too: [blockr.ui#107](https://github.com/BristolMyersSquibb/blockr.ui/issues/107), [blockr.ui#113](https://github.com/BristolMyersSquibb/blockr.ui/issues/113), [blockr.dock#673](https://github.com/BristolMyersSquibb/blockr.dock/issues/673), [blockr.assistant#319](https://github.com/BristolMyersSquibb/blockr.assistant/issues/319), [blockr.graph#12](https://github.com/BristolMyersSquibb/blockr.graph/issues/12), [blockr.dock#674](https://github.com/BristolMyersSquibb/blockr.dock/issues/674), [blockr.assistant#320](https://github.com/BristolMyersSquibb/blockr.assistant/issues/320) and [blockr.ui#116](https://github.com/BristolMyersSquibb/blockr.ui/issues/116).
Which theme variables there are, their defaults, and why those defaults sit in a cascade layer belong to [The theme variables](Rewrite-1.7.2).
The components belong to [The components of blockr.ui](Rewrite-1.7.3).
Why a module gets React through its build rather than its host, and how a module's own stylesheet loads with it, belong to [UI modules in JS](Rewrite-1.1.7), and how an app gives the page a theme of its own belongs to [An app's theme](Rewrite-1.7.5).

## What must hold

1. A package's build gets everything it needs of blockr.ui from the preset: its bundles hold no React and no React Aria, and its classes read the theme variables under the package's own prefix.
2. One copy each of React and of React Aria runs on the page, both from blockr.ui's files ([UI kit and design system for the client](Rewrite-1.7#what-must-hold)).
3. React loads in a file of its own, and core's hooks in one that imports nothing of blockr.ui, so that a page whose UIs draw with React, but neither with blockr.ui's components nor with React Aria's, loads no React Aria.
4. Only a major release of blockr.ui drops or renames what the list of theme variables holds, and no other package's build reads a variable of blockr.ui's that the list lacks, sets a variable under `--bk-` or writes a class under `bk:`.
5. The stylesheet of blockr.ui is on the page from the first paint, under every frontend, and no stylesheet that a package builds styles another package's elements.
6. Nothing of blockr.ui's is a page global.

## Today

On main, blockr.ui and the packages that draw with its widgets build no JS and no CSS.
Their scripts and stylesheets are written by hand, as blockr.ui's are in `inst/assets`.
Where a package has a `package.json`, its scripts only run the package's tests ([package.json](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/package.json)).
R puts them on a Shiny page as HTML dependencies: `theme_dep()` for the tokens and the theme, and `controls_dep()` for the widgets, which a package adds before its own, as blockr.dplyr does ([R/theme.R#L44-L67](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/R/theme.R#L44-L67), [R/controls.R#L58-L90](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/R/controls.R#L58-L90), [R/blockr-core-dep.R#L19-L30](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/58f232f5baebfab329e54255feca3ef9341d97e1/R/blockr-core-dep.R#L19-L30)).

| Today | Where it goes |
|---|---|
| Classic scripts, which put the widgets on the page global `window.Blockr` ([blockr-ui.js#L18](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/js/blockr-ui.js#L18)), each reading the widgets of the scripts before it, as `blockr-select.js` reads `Blockr.place` and `Blockr.layer` ([blockr-select.js#L39-L40](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/js/blockr-select.js#L39-L40)) | Modules that blockr.ui's build bundles, which a package imports as `@blockr/ui` through the page's import map, so that nothing of blockr.ui's is a page global ([The bundle](#the-bundle)) |
| Tokens under `--blockr-`, such as `--blockr-color-bg-surface`, whose dark values key on `data-bs-theme="dark"`, the attribute that bslib writes and core's board option `dark_mode` toggles ([blockr-tokens-dark.css#L1-L21](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens-dark.css#L1-L21)) | The theme variables under `--bk-` ([The theme variables](Rewrite-1.7.2)), whose dark values key on `data-bk-mode` ([Prefixes](#prefixes)) |
| Components that read the steps of the palette, such as `grey-900`, which the dark tokens restate by position ([blockr-tokens-dark.css#L10-L13](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens-dark.css#L10-L13)) | Classes that read jobs alone, since the preset drops the palette ([The build preset](#the-build-preset)) |
| Classes written by hand, such as `blockr-select__dropdown`, which other packages read and style, so that their names are part of what blockr.ui offers ([blockr-select.js#L34-L37](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/js/blockr-select.js#L34-L37)) | Classes under `bk:`, which the check fails another package's build for naming ([Prefixes](#prefixes)) |
| A theme stylesheet whose rules restyle the whole page, Bootstrap's included, as it sets `--bs-body-bg` under `:root:root` to win over the rules that bslib adds after it ([blockr-theme.css#L1-L25](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-theme.css#L1-L25)) | A stylesheet that styles blockr.ui's components alone ([The stylesheet on the page](#the-stylesheet-on-the-page)) |
| A base stylesheet for a page without Bootstrap, `base_dep()`, with a reset of the browser's defaults, the body's font and the look of Shiny's inputs ([R/theme.R#L69-L97](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/R/theme.R#L69-L97)) | Dropped, since the preset leaves out a reset, no Shiny input draws, and the frontend draws the page and its text with the theme variables ([The theme variables](Rewrite-1.7.2#colours)) |
| Bootstrap 5 on every page, through bslib, whose theme core's `serve()` and the dock's page fix ([R/utils-serve.R#L72-L73](https://github.com/BristolMyersSquibb/blockr.core/blob/5abaa52bc04bf202dab9c6e17772f2a170b10a38/R/utils-serve.R#L72-L73), [R/utils-serve.R#L30-L43](https://github.com/BristolMyersSquibb/blockr.dock/blob/d8b30e148a43612e580f8970ceaf85b89e7fb6d2/R/utils-serve.R#L30-L43)) | Dropped with the UI that R draws ([Drawing the board](Rewrite-1.1.8#what-goes-from-r)), while every package's utilities stay outside any cascade layer, so that a page's other CSS, such as Bootstrap's, does not win over them ([The build preset](#the-build-preset)) |

## Proposal

### The build preset

The build preset is the set of build settings that blockr.ui ships for every package's build, as `@blockr/ui/build`, so that each package builds against blockr.ui in the same way.
It has a half for React and a half for Tailwind CSS.
For React, it holds esbuild's options for a module, which a package's build spreads into its own call, as `esbuild.build({ ...preset, entryPoints: ["srcts/head-block.tsx"], outdir: "inst/js" })`.
For Tailwind, it holds a stylesheet, which a package's stylesheet imports after Tailwind, and a check that the build runs on the package's code and on the stylesheet that Tailwind writes from it.

Core's preset, `@blockr/core/build`, extends blockr.ui's with core's own entry points.
So a package that builds on core spreads core's options alone into its esbuild call, and a package that builds on blockr.ui alone spreads blockr.ui's, while the stylesheet of either imports blockr.ui's preset stylesheet.
The preset also holds two general helpers of a build: `staticImports()`, which lists what each file imports up front, and the vendor check, which fails a build that puts a library into a file of the package's own code ([State in JS](Rewrite-1#conventions)).
The build of blockr.ui needs both, and it needs nothing of core's.
A package imports both from `@blockr/ui/build`, whichever preset it spreads.

The React half:

1. It leaves each import of React's entry points, `react`, `react/jsx-runtime`, `react-dom` and `react-dom/client`, an import, and each import of `@blockr/ui` and of React Aria's three packages as well.
   Those are `react-aria-components`, with React Aria's components, `react-aria`, with the hooks that the components are built from, and `react-stately`, with the state that the hooks keep.
   The page's import map resolves them to blockr.ui's files ([The bundle](#the-bundle)), so no package's bundle holds React, React Aria or blockr.ui's components.
   The entry `@blockr/ui/icons` is the exception, which the preset bundles into the package's file of libraries, so that the file holds the icons that the package imports and no others ([The components of blockr.ui](Rewrite-1.7.3#the-icons)).
   A package imports React Aria's packages as any code written with React Aria does.
   Core's menu of board actions, for one, draws React Aria's `TextField`, `Input` and `Separator`, and the Edit board plugin reads its `TableStateContext`.
   React Aria's `Table` runs hooks in each of its cells.
   A table that draws thousands of cells without them would take its focus ring, its keyboard handling and its selection from `react-aria` and `react-stately`, whether blockr.ui or another package draws it.
   A package still draws with blockr.ui's component wherever blockr.ui has one ([State in JS](Rewrite-1#what-must-hold)).
2. It fails a build that imports an entry point of React that the import map does not name, rather than bundle a second copy of React.
   The React Compiler's runtime is the exception.
   A library that the compiler built imports `react-compiler-runtime` or `react/compiler-runtime`, as React Flow, which blockr.graph draws with, imports the first.
   The preset resolves both to a small module that reads the runtime from `react` (notes).
   So a package's bundle holds no copy of the runtime, and the import map names no entry for it.
3. It fails a build that imports a package under `@react-aria/` or `@react-stately/`, or an entry point inside one of React Aria's three packages, such as `react-aria-components/Table`, with an error that names the package to import instead.
   React Aria 1.22 gives each of its components such an entry point, and the packages under `@react-aria/` and `@react-stately/` now only pass on what those entry points hold (notes).
   Each would bundle a second copy of what blockr.ui's copy of React Aria holds inside itself: its React contexts, the focus modality and the stack of open overlays.
   An item of the second copy inside blockr.ui's `ComboBox` would then find no combo box.
   The packages under `@internationalized/`, such as `@internationalized/date`, hold no context, so a package bundles them itself.
   A type that a module imports with `import type` passes, since esbuild drops that import before it resolves anything.
4. It fails a build whose React Aria packages are at other versions than those in blockr.ui's files, so that a package builds against the React Aria that runs on the page.
   React Aria's major moves with blockr.ui's, as React's does ([UI modules in JS](Rewrite-1.1.7#react)).
5. It fails a build that imports one of Lucide's packages, such as `lucide` or `lucide-react`, with an error that names `@blockr/ui/icons` instead.
   So every package draws the icons of the Lucide that blockr.ui pins, and imports them through one entry, which keeps open serving each icon to a page once ([Backlog](Backlog#each-icon-once-on-the-page)).

The Tailwind half:

1. A package's stylesheet imports Tailwind's theme and utilities under the package's prefix, and then the preset's stylesheet, as core's would:

   ```css
   @layer theme;
   @import "tailwindcss/theme.css" layer(theme) prefix(bc);
   @import "tailwindcss/utilities.css" source(none);
   @import "@blockr/ui/preset.css";
   @source "../**/*.{ts,tsx}";
   ```

   The stylesheet of blockr.ui does the same under `bk`, so that one mapping serves every package, blockr.ui's own included.
2. The preset's stylesheet maps each name of Tailwind's theme that has a theme variable onto that variable, through `@theme inline reference`, as `--color-popover` onto `var(--bk-color-popover)`.
   So a package's classes compile to reads of blockr.ui's variables, whatever the package's prefix: core's `bc:bg-popover` writes `background-color: var(--bk-color-popover)`, and its `bc:shadow-md` writes `--tw-shadow: var(--bk-shadow-md)`.
   With `reference`, Tailwind writes none of these variables into the package's stylesheet, so blockr.ui's stylesheet alone sets them ([The list of theme variables](#the-list-of-theme-variables)).
3. It drops Tailwind's palette, so that a class of the palette, such as `bc:bg-blue-600`, writes nothing.
   Tailwind skips a class that it does not know without a word, so the check fails a build whose code names a colour of the palette, under any prefix ([The theme variables](Rewrite-1.7.2#colours)).
4. It keys the dark variant on `data-bk-mode="dark"` on the page's root, which core's board option `dark_mode` sets ([Board options and blockr options](Rewrite-1.1.13#where-the-two-meet)).
   Every job carries both modes, so the variant serves only what a package writes beyond the jobs.
5. It leaves out Tailwind's reset of the whole page, so that nothing that one package loads styles another package's elements.
   It keeps the utilities outside any cascade layer, so that a page's other CSS, such as Bootstrap's, does not win over them ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
6. The check fails a build whose stylesheet reads a variable of blockr.ui's that the list of theme variables lacks, as in plain CSS or in an arbitrary value ([The list of theme variables](#the-list-of-theme-variables)).
   It fails another package's build whose code names a class under `bk:`, which blockr.ui alone writes ([Prefixes](#prefixes)), and any build that runs another version of Tailwind than the one that blockr.ui is written for.
   It fails another package's build whose stylesheet sets a variable under `--bk-`, since blockr.ui's stylesheet alone sets the defaults, and R writes the values of the frontend and of the app from their themes ([The theme variables](Rewrite-1.7.2#where-the-values-are-set)).

### Prefixes

Tailwind writes CSS only for the classes that it finds in the files it scans.
So each package that writes classes builds them itself, under a prefix of its own.
The rest of Tailwind is blockr.ui's: the theme variables, the dark variant and the choices above, which hold for every package.

The theme variables and the classes that blockr.ui writes take the prefix `bk`, for all of blockr rather than one package, as `--bk-color-popover` and `bk:flex`.
Every other package writes its classes under a prefix of its own, as core writes `bc:flex`, since stylesheets built apart that share a class override each other by load order ([UI modules in JS](Rewrite-1.1.7#packaging)).
Tailwind writes a class under `bk:` only where a component of blockr.ui uses it, so those classes come and go with blockr.ui's components.
So no other package uses one, and the check fails another package's build whose code names one ([The build preset](#the-build-preset)).
The mode attribute takes the prefix too: `data-bk-mode`, which holds `light` or `dark`.
A package that writes no classes of its own, as the dock writes plain CSS today, runs no Tailwind, reads the theme variables in its CSS, and runs the check on that CSS and on its code.

### The list of theme variables

Every package's stylesheet reads blockr.ui's variables.
Tailwind leaves out of a stylesheet whatever the files that it scans do not use, such as a variable of its theme or a class.
If Tailwind wrote the theme variables, the stylesheet would drop a variable as soon as no component of blockr.ui used it, and another package that reads the variable would lose its look without a word.

So what blockr.ui's stylesheet provides other packages is a list that blockr.ui declares and exports, in JS for builds and in R for its own `new_blockr_theme()` ([An app's theme](Rewrite-1.7.5#a-theme-in-r)): the theme variables, its fonts and the mode attribute.
Its classes are not on the list, since no other package uses them ([Prefixes](#prefixes)).
The build of blockr.ui writes the list, which blockr.ui declares once in TypeScript, into a JSON file in its `inst/`.
The JS export comes from that declaration, and the R export reads the file, so the two never disagree.
The R export is `theme_variables()`, which returns the full names of the theme variables as a character vector, such as `"--bk-color-primary"`.
For the list:

1. The stylesheet of blockr.ui writes the whole list as plain CSS: the values of each variable as rules in `@layer theme`, and each font as a face.
   Tailwind copies plain CSS into what it writes as it stands, so nothing of the list depends on what blockr.ui's own components use.
2. Its tests compare its compiled stylesheet with the list.
3. The preset's check fails a build whose stylesheet reads a variable of blockr.ui's that the list lacks, and another package's build whose stylesheet sets a variable under `--bk-` or whose code names a class under `bk:` ([The build preset](#the-build-preset)).
4. Adding to the list takes a minor release of blockr.ui, and removing or renaming takes a major.
5. Tailwind's version is part of the contract: each major of blockr.ui names one version of Tailwind, which every package's build runs.
   The properties that Tailwind registers for its utilities, such as `--tw-blur`, carry no prefix, so every package's stylesheet registers them, and stylesheets built with two versions could register them differently.

The list holds blockr.ui's own names alone, none of another package's.
So the colours of a block's statuses are the jobs that core maps them onto, and the colours of the categories of block classes are core's ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).

### The bundle

The build of blockr.ui bundles its code and the libraries that it ships into these files in its `inst/js`:

1. React's file, `react-<hash>.js`, with React and ReactDOM, minified.
   Beside it, an ES module for each of React's entry points, such as `react.js`, reads React from that file.
2. The file of blockr.ui's components, `blockr-ui.js`, with blockr.ui's own code, unminified, which imports React through React's entry points ([State in JS](Rewrite-1#conventions)).
3. React Aria's files, minified, with the whole of React Aria's three packages.
   The build bundles each package as an entry of its own, and esbuild splits the code that the three share into files of their own.
   The file of the components imports `react-aria-components`, as does any module that draws with React Aria's components.
4. The vendor file of blockr.ui, `vendor-<hash>.js`, minified, with what its components draw with beside React and React Aria: functions of `@internationalized/date` and the icons of Lucide that they draw.
   The file of the components imports it by its name, so that it holds blockr.ui's own code alone, as the vendor check asks of every package ([blockr.ui#125](https://github.com/BristolMyersSquibb/blockr.ui/pull/125)).

The page's import map names React's entry points, `@blockr/ui` and React Aria's three packages.
It names no entry for `@blockr/ui/icons`, whose icons each package bundles ([The build preset](#the-build-preset)).
The build of blockr.ui writes their entries into its own `inst/js/import-map.json`, as core's build writes core's.
R puts the entries of both packages into the one import map in the head of the page that it serves.
So a module that imports React loads React's file alone.
A module that imports one of React Aria's packages loads the files of React Aria that the package needs too, and one that imports `@blockr/ui` loads the file of the components as well.
The build of blockr.ui also lists what each of its files imports up front in its `inst/js/preload.json`, as every package's build does ([State in JS](Rewrite-1#conventions)).
So R names React Aria's files in the page's head only where a module that it names there imports `@blockr/ui` or one of React Aria's packages, directly or through another file.

Every package reaches blockr.ui's components through the entry `@blockr/ui` alone.
Its build reads no variable of blockr.ui's beyond the list and names no class under `bk:` ([The list of theme variables](#the-list-of-theme-variables)).
So the design keeps open a later project of the [Backlog](Backlog#another-kit-in-place-of-blockruis-components): a package whose components have the same names and props as blockr.ui's but are styled with CSS of its own, such as in Bootstrap's look, and to whose files the import map resolves `@blockr/ui` in place of blockr.ui's.

Core's React SDK holds two entries, so that a page whose UIs use core's hooks loads no React Aria either:

- The entry `@blockr/core/react` holds what draws nothing: the hooks over the hosts, such as `useValue()`, and the helpers `reactModule()` and `outputRenderer()` ([UI modules in JS](Rewrite-1.1.7#react)).
  It imports React and nothing of blockr.ui.
- The entry `@blockr/core/components` holds what core draws with blockr.ui's components: the block's mark, the status dot and `NotificationList` ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).
  It imports `@blockr/ui`.

Core's runtime imports neither entry up front.
Each UI that core draws loads as core first draws it.
Its menu of board actions and its advanced actions are modules already ([Board actions](Rewrite-1.1.16#what-a-frontend-gives)), and the card of a block that `serve()` serves alone loads through a dynamic import.

The UI of a board option loads as it first renders too.
Core imports the module of every board option that an available package lists as the page starts, to register it, and that module holds the board option's UI ([UI modules in JS](Rewrite-1.1.7#modules-of-plugin-classes-and-board-options)).
So the UI's `render()` imports the rest of its code with `import()`, from a file of its own, which the contract allows, since `render()` may be async ([UI modules in JS](Rewrite-1.1.7#the-contract)).
Core's board options do so.
Otherwise every page would load React Aria as it starts, through the UIs of `n_rows` and `dark_mode` (notes), even where nothing draws them.

Core's tests read its `inst/js/preload.json` and fail where core's runtime, the entry `@blockr/core/react` or the module of one of core's board options imports `@blockr/ui` or one of React Aria's packages up front, directly or through another file.

A page whose UIs draw neither with blockr.ui's components nor with React Aria's thus never loads React Aria (condition 3).
A module reads React through imports, so nothing of blockr.ui's is a page global (condition 6).
The `window.React` that reactR's dependency sets stays apart from the page's React ([R/dependencies.R#L35-L48](https://github.com/react-R/reactR/blob/808b21f4f2e5c374cb8ec910f8e2cc27f6b40e1b/R/dependencies.R#L35-L48)).

React Aria's files hold the whole of its three packages, rather than the parts that the components draw with.
Those parts take 263 KB gzipped, and the whole of `react-aria-components` takes 279 KB (notes).
A file of the parts alone would save a page 16 KB, about 4 ms.
A package that needed another part would then wait for a release of blockr.ui.
The hooks and their state, in `react-aria` and `react-stately`, add only 3.4 KB to the whole, since React Aria's components are built from them and hold most of their code already.
A page loads those 3.4 KB only where a module imports `react-aria` or `react-stately` (notes).
The files load with the first module that imports `@blockr/ui` or one of React Aria's packages.
Under core's basic frontend or the dock, that is as the page opens, since their UIs draw with blockr.ui's components.

A file for each group of [the first set](Rewrite-1.7.3#the-first-set) was considered and not chosen.
Core's own UIs draw with six of the eight groups as the page opens, under core's basic frontend and under the dock, so only the dates and times and the colours could load later.
Their parts of React Aria take 68.6 KB gzipped, which added 18 ms to a cold load in [blockr.core#791](https://github.com/BristolMyersSquibb/blockr.core/pull/791) (notes).
A split would give blockr.ui an entry for each group, such as `@blockr/ui/dates`, which every package's imports would follow.

### The stylesheet on the page

R puts blockr.ui's stylesheet, with the theme variables, their defaults and the font faces, on every page from the start, ahead of core's.
So everything that reads the theme variables finds them, core's loading note included, which R's page holds from the start.
R writes the frontend's theme and then the app's into the page's head after it ([An app's theme](Rewrite-1.7.5#the-rules-that-r-writes)).
Loading the stylesheet later, with blockr.ui's JS, would save a page little: core's compiled stylesheet, which holds the classes of the components on `js-state`, takes 10.5 KB gzipped, and the browser downloads a font only once something uses it.

The stylesheet of blockr.ui comes first, since a package may pass classes of its own to one of blockr.ui's components.
A component writes those classes after its own, as core's basic frontend gives a toast `bc:border-l-4` beside the toast's own `border` (notes).
Both rules sit outside any layer and have the same specificity, so the rule of the later stylesheet wins.
Every package's stylesheet comes after blockr.ui's: core's follows it in the page's head, and a module's stylesheet loads with the module ([UI modules in JS](Rewrite-1.1.7#packaging)).

The stylesheet sets the defaults of the theme variables inside Tailwind's theme layer, `@layer theme`, where [The theme variables](Rewrite-1.7.2#where-the-values-are-set) has them sit.
So the values of the frontend's theme and of the app's, which R writes outside any layer, win over the defaults.

## Open questions

None.

<details><summary>Notes for implementers</summary>

- On `js-state`, at `79507c4`, core holds what this page gives blockr.ui:
  - Core's build preset, `@blockr/core/build`, holds esbuild's options for a module ([srcts/build/preset.ts#L38-L72](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/srcts/build/preset.ts#L38-L72)).
    Its plugin leaves each import of React's entry points, of core's React SDK, binding and controls, and of OpenTelemetry's API an import, which the page's import map resolves, and it fails a build that imports React Aria.
    At `195d006`, it resolves the React Compiler's runtime to a module that reads the runtime from `react` ([srcts/build/preset.ts#L43-L67](https://github.com/BristolMyersSquibb/blockr.core/blob/195d006ec31ec259cd70582a874dbc770f29bbb1/srcts/build/preset.ts#L43-L67)).
    Its general part moves to blockr.ui's preset, with `staticImports()`, from `srcts/build/preload.ts`, and the vendor check, from `srcts/build/vendor-check.ts`, while core's preset keeps core's entry points ([The build preset](#the-build-preset)).
  - Core's build bundles React, ReactDOM, the two libraries that core's code imports, `@preact/signals-core` and `@cfworker/json-schema`, and the parts of React Aria that core's components draw with into one file, `vendor-<hash>.js`.
    It writes each of React's entry points as an ES module of its own, such as `react.js`, which reads React from that file ([srcts/build/build.ts#L19-L37](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/srcts/build/build.ts#L19-L37)).
    So a module that imports React loads React Aria too, until React and React Aria move to files of blockr.ui's ([The bundle](#the-bundle)).
  - Core's runtime, `blockr-core.js`, imports `@blockr/core/react` up front ([inst/js/preload.json#L43-L51](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/inst/js/preload.json#L43-L51)).
    It needs the SDK for the dialogs of its board actions, the block picker among them, and for the card of a block that `serve()` serves alone, which it imports statically ([srcts/core/start.ts#L112](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/srcts/core/start.ts#L112), [srcts/page/page.ts#L25](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/srcts/page/page.ts#L25)).
    So every page loads the SDK's components, and React Aria with them.
  - The modules of core's board options `n_rows` and `dark_mode` import `@blockr/core/react` up front too, since each holds its UI, which draws with the SDK's `NumberField` or `ToggleButtonGroup` ([inst/js/preload.json#L56-L59](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/inst/js/preload.json#L56-L59), [#L91-L94](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/inst/js/preload.json#L91-L94)).
    Core imports both as every page starts, to register them, so they would load React Aria even without the runtime's import.
    The file `srcts/options/ui.tsx` builds both UIs with the SDK's `NumberField`, `ToggleButton` and `ToggleButtonGroup`, and `srcts/options/options.ts` holds each in its `Option`'s `ui`.
  - The page's import map, from `srcts/import-map/index.ts`, names React's four entry points, core's own and OpenTelemetry's API ([srcts/import-map/index.ts#L16-L29](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/srcts/import-map/index.ts#L16-L29)).
  - Core's stylesheet, `srcts/runtime/index.css`, imports Tailwind's theme under core's prefix, `bc`, and keys its dark variant on the attribute `data-bc-theme`, which core's `setTheme()` in `srcts/options/options.ts` sets ([srcts/runtime/index.css#L38-L41](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/srcts/runtime/index.css#L38-L41)).
    It holds core's theme, with the colours of statuses and categories in `@theme static` ([#L169-L183](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/srcts/runtime/index.css#L169-L183)).
    The theme moves to blockr.ui's stylesheet, and the attribute becomes `data-bk-mode`.
- On `js-state` at `ec30f737`, the 140 parts of React Aria that `srcts/aria/index.ts` names take 263 KB gzipped, and all of `react-aria-components` 1.22.1 takes 279 KB.
  The 16 KB between them would cost a page about 4 ms, at the rate that [blockr.core#791](https://github.com/BristolMyersSquibb/blockr.core/pull/791) measured.
  There, the 69 KB of the dates and the colours added 18 ms to loading core's vendor file in headless Chromium, 176 ms against 158 ms, the median of 9 cold loads.
  Each figure bundles `export { … } from "react-aria-components"` with esbuild, minified, with `process.env.NODE_ENV` set to `"production"` and React external, and gzips it at level 9.
  A package that bundled React Aria itself would hold 11 KB gzipped of it for a text field alone, and 72 KB for the parts of the select.
- On 2026-11-24, `react-aria-components` 1.22.1 resolved `react-aria` 3.53.1 and `react-stately` 3.51.0, as core's `package-lock.json` on `js-state` does.
  Bundled alone with esbuild 0.28.2, as above, `react-aria-components` took 284.4 KB gzipped, in KB of 1,000 bytes.
  Bundled as three entries with `splitting`, the files that a module importing `react-aria-components` loads took 284.2 KB, and the entries of `react-aria` and `react-stately` added 3.4 KB.
  Of the 160 names that `react-aria` exports, `react-aria-components` passes on 20, such as `useLocale`, and leaves out `useFocusRing`, `useKeyboard`, `FocusScope` and `mergeProps`.
  Of the 68 names that `react-stately` exports, `react-aria-components` leaves out 46, among them `useMultipleSelectionState` and `useTableColumnResizeState`.
- The packages under `@react-aria/` and `@react-stately/` only pass on what the entry points of `react-aria` and `react-stately` hold, as `@react-aria/table` 3.18.1 passes on `react-aria/useTable`.
- Split along the groups of the first set, the same way on 2026-11-24, React Aria took 41 files of 285.3 KB gzipped.
  Each group's entry exported the parts of React Aria that `srcts/aria/index.ts` names for its components, through React Aria's entry point for each component, such as `react-aria-components/DatePicker`, and esbuild split the rest.
  The six groups that core's UIs draw with as the page opens took 216.7 KB, and the dates and times and the colours added 68.6 KB.
  The code that one group alone needs takes 44.6 KB for the dates and times, 43.7 KB for the collections, 24.1 KB for the colours, 19.4 KB for the picks, 13.0 KB for the overlays, 9.6 KB for the fields, 6.0 KB for the layout and 1.7 KB for the buttons and files.
  Where each entry imported its parts from `react-aria-components` itself, every group loaded some 268 KB, so a split has to go through the entry point for each component.
- The build of blockr.ui bundles React and React Aria without the plugin of the React half, as core's build writes its vendor file without the preset's plugins on `js-state`.
- Tailwind 4.3.3, as of 2026-11-23, writes these from the mappings of the Tailwind half:
  - Under `prefix(bk)`, `@theme inline { --color-popover: var(--bk-color-popover) }` writes `--bk-color-popover: var(--bk-color-popover)` into the theme layer, a variable that refers to itself, while `@theme inline reference` writes no variable.
  - With `@theme static { --shadow-md: … }` under `prefix(bk)`, `bk:shadow-md` writes the shadow's literal offsets and colours.
    A class defined anew with `@utility shadow-md` comes after Tailwind's own, and a focus ring on the same element still reads the literal from Tailwind's `--tw-shadow`.
  - Through `@theme inline reference`, `bk:shadow-md` and `bc:shadow-md` both write `--tw-shadow: var(--bk-shadow-md)`, which a ring keeps, and a class of the dropped palette, such as `bk:bg-blue-600`, writes nothing.
- The entry `@blockr/core/components` joins core's other entries in core's import map and in the filter of core's preset, as `@blockr/core/controls` does, and takes `NotificationList` from `srcts/react/notifications.tsx`.
  On `js-state`, the card of a block that `serve()` serves alone imports `useNotified()` and `useStatus()` from the SDK, which stay in `@blockr/core/react`, and the footer, pills and banners of `srcts/card`.
- The esbuild 0.28.2 that core builds with writes the code that an `import()` names into a file of its own only where the build splits code, with `splitting`, or leaves that import an import of a file built apart, as the assistant's build does for the parts of pi that it loads on demand ([srcts/build/build.ts#L24-L31](https://github.com/BristolMyersSquibb/blockr.assistant/blob/4a3142df3016309a8ba38776b17f221e6d70de64/srcts/build/build.ts#L24-L31)).
  Otherwise esbuild puts that code into the board option's module, and the code's imports, such as `@blockr/ui`, become imports of the module, which load up front.
- On `js-state`, core's `Toast` in `srcts/overlays/toast.tsx` writes the classes that it is given after its own, `bc:border` among them, and the basic frontend's toasts in `srcts/modules/basic/board.tsx` give it `bc:border-l-4`.
  Once the toast is blockr.ui's, its `bk:border` and the frontend's `bc:border-l-4` sit in two stylesheets, and the stripe holds only while core's comes later.

</details>
