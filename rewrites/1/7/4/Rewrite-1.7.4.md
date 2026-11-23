# Building on blockr.ui: the build preset, the bundle and the stylesheet on the page
Status: review. Design for [UI kit and design system for the client](Rewrite-1.7).

One of the designs for blockr.ui as the client's UI kit ([UI kit and design system for the client](Rewrite-1.7)): how a package builds its modules and its classes against blockr.ui through blockr.ui's build preset, which files blockr.ui's own build writes, and what of them R puts on the page.
It shapes the items of 1.7's Work list that start blockr.ui's client, declare the theme's list, and build core's stylesheet with the preset ([UI kit and design system for the client](Rewrite-1.7#work)).
Which variables the theme names, their defaults, and why those defaults sit in a cascade layer belong to [The theme's variables](Rewrite-1.7.2).
The components belong to [The components of blockr.ui](Rewrite-1.7.3).
Why a module gets React through its build rather than its host, and how a module's own stylesheet loads with it, belong to [UI modules in JS](Rewrite-1.1.7), and how R writes an app's theme into the page belongs to [An app's theme](Rewrite-1.1.17).

## What must hold

1. A package's build gets everything it needs of blockr.ui from the preset: its bundles hold no React and no React Aria, and its classes read blockr.ui's theme under the package's own prefix.
2. One copy each of React and of React Aria runs on the page, both from blockr.ui's files ([UI kit and design system for the client](Rewrite-1.7#what-must-hold)).
3. React loads in a file of its own, so that a page whose UIs draw with React, but with none of blockr.ui's components, loads no React Aria.
4. Only a major release of blockr.ui drops or renames a variable, a keyframe or a font of the theme's list, and no package's build reads one that the list lacks.
5. The stylesheet of blockr.ui is on the page from the first paint, under every frontend, and no stylesheet that a package builds styles another package's elements.
6. Nothing of blockr.ui's is a page global.

## Today

On `js-state`, at `79507c4`, core holds what this page gives blockr.ui:

- Core's build preset, `@blockr/core/build`, holds esbuild's options for a module.
  Its plugin leaves each import of React's entry points, of core's React SDK, binding and controls, and of OpenTelemetry's API an import, which the page's import map resolves.
  It fails a build that imports React Aria ([srcts/build/preset.ts#L38-L72](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/srcts/build/preset.ts#L38-L72)).
- Core's build bundles React, ReactDOM, two libraries of core's own and the parts of React Aria that core's components draw with into one file, `vendor-<hash>.js`.
  It writes each of React's entry points as an ES module of its own, such as `react.js`, which reads React from that file ([srcts/build/build.ts#L19-L37](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/srcts/build/build.ts#L19-L37)).
  So a module that imports React loads React Aria too, and React sits on no global.
- The page's import map names React's four entry points and core's own ([srcts/import-map/index.ts#L16-L29](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/srcts/import-map/index.ts#L16-L29)).
- Core's stylesheet imports Tailwind's theme under core's prefix, `bc`, and keys its dark variant on the attribute `data-bc-theme` ([srcts/runtime/index.css#L38-L41](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/srcts/runtime/index.css#L38-L41)).
  It holds core's theme, with the colours of statuses and categories in `@theme static` ([#L169-L183](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/srcts/runtime/index.css#L169-L183)).

## Proposal

### The build preset

The build preset is the set of build settings that blockr.ui ships for every package's build, as `@blockr/ui/build`, so that each package builds against blockr.ui in the same way.
It has a half for React and a half for Tailwind CSS.
For React, it holds esbuild's options for a module, which a package's build spreads into its own call, as `esbuild.build({ ...preset, entryPoints: ["srcts/head-block.tsx"], outdir: "inst/js" })`.
For Tailwind, it holds a stylesheet, which a package's stylesheet imports after Tailwind, and a check that the build runs on what Tailwind writes.

Core's preset, `@blockr/core/build`, extends blockr.ui's with core's own entry points.
So a package that builds on core spreads core's options alone into its esbuild call, and a package that builds on blockr.ui alone spreads blockr.ui's, while the stylesheet of either imports blockr.ui's preset stylesheet.
The general helpers of core's build move to blockr.ui's with the preset: `staticImports()`, which lists what each file imports up front, and the vendor check, which fails a build that puts a library into a file of the package's own code ([State in JS](Rewrite-1#conventions)).
The build of blockr.ui needs both, and it needs nothing of core's.

The React half:

1. It leaves each import of React's entry points, `react`, `react/jsx-runtime`, `react-dom` and `react-dom/client`, an import, and so each import of `@blockr/ui`.
   The page's import map resolves them to blockr.ui's files ([The bundle](#the-bundle)), so no package's bundle holds React or blockr.ui's components.
2. It fails a build that imports an entry point of React that the import map does not name, rather than bundle a second copy of React.
   The React Compiler's runtime is the exception: the preset resolves `react-compiler-runtime` and `react/compiler-runtime`, which a library that the compiler built imports, to a small module that reads the runtime from `react`, as core's preset does on `js-state` ([srcts/build/preset.ts#L43-L67](https://github.com/BristolMyersSquibb/blockr.core/blob/195d006ec31ec259cd70582a874dbc770f29bbb1/srcts/build/preset.ts#L43-L67)).
   So a package's bundle holds no copy of the runtime, and the import map names no entry for it.
3. It fails a build that imports React Aria, `react-aria-components`, `react-aria`, `react-stately` or a package under `@react-aria/` or `@react-stately/`, with an error that names `@blockr/ui`.
   A second copy would hold React contexts of its own, which blockr.ui's components do not read.
   An item of the second copy inside blockr.ui's `ComboBox` would then find no combo box.
   The packages under `@internationalized/`, such as `@internationalized/date`, hold no context, so a package bundles them itself.
   A type that a module imports with `import type` passes, since esbuild drops that import before it resolves anything.

The Tailwind half:

1. A package's stylesheet imports Tailwind's theme and utilities under the package's prefix, and then the preset's stylesheet, as core's would:

   ```css
   @layer theme;
   @import "tailwindcss/theme.css" layer(theme) prefix(bc);
   @import "tailwindcss/utilities.css" source(none);
   @import "@blockr/ui/preset.css";
   @source "../**/*.{ts,tsx}";
   ```

2. The preset's stylesheet maps every job of the theme onto blockr.ui's variable for it through `@theme inline`.
   So a package's classes compile to reads of blockr.ui's variables, whatever the package's prefix: core's `bc:bg-popover` writes `background-color: var(--bk-color-popover)`.
3. It drops Tailwind's palette, so that a class of the palette, such as `bc:bg-blue-600`, writes nothing.
   Tailwind skips a class that it does not know without a word, so the check fails a build whose code names a colour of the palette, under any prefix ([The theme's variables](Rewrite-1.7.2#colours)).
4. It keys the dark variant on `data-bk-mode="dark"` on the page's root, which core's board option `dark_mode` sets ([Board options and blockr options](Rewrite-1.1.13#where-the-two-meet)).
   Every job carries both modes, so the variant serves only what a package writes beyond the jobs.
5. It defines the classes `shadow-sm`, `shadow-md` and `shadow-lg` anew, each reading the variable of its name, as `--bk-shadow-md`.
   Tailwind writes a shadow's offsets and colours into each class that draws it, rather than reading a variable, so its own classes would not follow the theme ([The theme's variables](Rewrite-1.7.2#fonts-sizes-radii-shadows-and-spacing)).
6. It leaves out Tailwind's reset of the whole page, and keeps the utilities outside any cascade layer.
   So a page's other CSS, such as Bootstrap's, does not win over them, and nothing that one package loads styles another package's elements ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).
7. The check fails a build whose stylesheet reads a variable of blockr.ui's that the theme's list lacks, as in plain CSS or in an arbitrary value, and a build that runs another version of Tailwind than the one that the theme is written for ([The theme's list](#the-themes-list)).

### Prefixes

Tailwind writes CSS only for the classes that it finds in the files it scans.
So each package that writes classes builds them itself, under a prefix of its own.
The rest of Tailwind is blockr.ui's: the theme, the dark variant and the choices above, which hold for every package.

The theme's variables and the classes that blockr.ui writes take the prefix `bk`, for all of blockr rather than one package, as `--bk-color-popover` and `bk:flex`.
Every other package writes its classes under a prefix of its own, as core writes `bc:flex`, since stylesheets built apart that share a class override each other by load order ([UI modules in JS](Rewrite-1.1.7#packaging)).
The mode attribute takes the prefix too: `data-bk-mode`, which holds `light` or `dark`.
A package that writes no classes of its own, as the dock writes plain CSS today, runs no Tailwind, reads the theme's variables in its CSS, and runs the check on that CSS.

### The theme's list

Every package's stylesheet reads blockr.ui's variables.
Tailwind writes a variable of its theme only where a utility that it scans uses it.
So a change to blockr.ui that dropped a variable would break another package's look without a word.

So the theme's variables, its keyframes and fonts, and the mode attribute are a list that blockr.ui declares and exports, in JS for builds and in R for core's `new_theme()` ([An app's theme](Rewrite-1.1.17#a-theme-in-r)), and:

1. Its stylesheet holds the whole list through `@theme static`, whatever its own components use.
2. Its tests compare its compiled stylesheet with the list.
3. The preset's check fails a package's build whose stylesheet reads a variable of blockr.ui's that the list lacks ([The build preset](#the-build-preset)).
4. Adding to the list takes a minor release of blockr.ui, and removing or renaming takes a major.
5. Tailwind's version is part of the contract, pinned for each major of blockr.ui.
   The properties that Tailwind registers for its utilities, such as `--tw-blur`, carry no prefix, so every package's stylesheet registers them, and stylesheets built with two versions could register them differently.

The list holds the theme's own names alone, none of another package's.
So the colours of a block's statuses are the jobs that core maps them onto, and the colours of the categories of block classes are core's ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).

### The bundle

The build of blockr.ui writes three files into its `inst/js`:

1. React's file, `react-<hash>.js`, with React and ReactDOM, minified.
   Beside it, an ES module for each of React's entry points, such as `react.js`, reads React from that file, as core's build writes them on `js-state` (Today).
2. The file of blockr.ui's components, `blockr-ui.js`, with blockr.ui's own code, unminified, which imports React through React's entry points ([State in JS](Rewrite-1#conventions)).
3. React Aria's file, `react-aria-<hash>.js`, minified, with the parts of React Aria that the components draw with.
   Only the file of the components imports it.

The page's import map names React's entry points and `@blockr/ui`.
The build of blockr.ui writes their entries, as core's build writes its own into `inst/js/import-map.json`, and R puts both into the head of the page that it serves.
So a module that imports React loads React's file alone, and a module that imports `@blockr/ui` loads the components and React Aria too.
A page whose UIs draw with none of blockr.ui's components never loads React Aria (condition 3).
A module reads React through imports, so nothing of blockr.ui's is a page global (condition 6).
The `window.React` that reactR's dependency sets stays apart from the page's React ([R/dependencies.R#L35-L48](https://github.com/react-R/reactR/blob/808b21f4f2e5c374cb8ec910f8e2cc27f6b40e1b/R/dependencies.R#L35-L48)).

React Aria's file holds every part that the components draw with, dates, times and colours among them, since a file of their own for those two would save a page only 18 ms (notes).
It loads with the first module that draws with blockr.ui's components.
Under core's basic frontend or the dock, that is as the page opens, since their UIs draw with blockr.ui's components.

### The stylesheet on the page

R puts blockr.ui's stylesheet, with its theme and the font faces, on every page from the start, beside core's.
So everything that reads the theme finds it, core's loading note included, which R's page holds from the start.
R writes an app's theme into the page's head after it ([An app's theme](Rewrite-1.1.17#the-rules-that-r-writes)).
A part that loaded later would save a page nothing that it would notice, since core's compiled stylesheet takes 10.5 KB gzipped on `js-state`, and a font downloads only once something uses it.

The stylesheet sets the theme's defaults inside Tailwind's theme layer, `@layer theme`, where [The theme's variables](Rewrite-1.7.2#where-the-frontend-sets-the-values) has them sit.
So a frontend's values, which it sets outside any layer, win over the defaults whichever stylesheet loads first.

## Open questions

None.

<details><summary>Notes for implementers</summary>

- The files on `js-state` at `79507c4`: the preset is `srcts/build/preset.ts`, the vendor file and React's entry points are written in `srcts/build/build.ts`, the vendor check is `srcts/build/vendor-check.ts`, `staticImports()` is `srcts/build/preload.ts`, the import map is `srcts/import-map/index.ts`, and core's theme is `srcts/runtime/index.css`.
- React Aria took about 72 KB of the 146 KB gzipped of `vendor-<hash>.js` on `js-state` on 2026-11-18, and 96 KB of its 171 KB with [blockr.core#752](https://github.com/BristolMyersSquibb/blockr.core/pull/752), against 279 KB for the whole of React Aria.
  Over those parts, the form inputs added about 35 KB, the overlays and layout 10 KB, the table, the tree and the grid list 32 KB, dates and times 44 KB, and colours 29 KB, so that the file came to about 250 KB with the three groups that core's own UIs draw with.
  A file of their own for dates and colours could only ever have moved those two, whose 69 KB cost a page 18 ms to load, so core kept them in its vendor file ([150b001](https://github.com/BristolMyersSquibb/blockr.core/commit/150b001f14cb16dade6262b696eb8ecaea6c4a69), [ceda20a](https://github.com/BristolMyersSquibb/blockr.core/commit/ceda20a87c0e70cf391e1deb99430d31852cd2fb)).
  Each figure bundles `export { … } from "react-aria-components"` with esbuild, minified, with `process.env.NODE_ENV` set to `"production"` and React external, and gzips it at level 9.
  A package that bundled React Aria itself would hold 11 KB gzipped of it for a text field alone, and 72 KB for the parts of the select.
- On `js-state`, core's `setTheme()` in `srcts/options/options.ts` sets `data-bc-theme`, which becomes `data-bk-mode`.

</details>
