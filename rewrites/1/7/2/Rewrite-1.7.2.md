# The theme variables: their jobs, their defaults and a frontend's values
Status: settled on 2026-11-24. Design for [UI kit and design system for the client](Rewrite-1.7).

One of the designs for blockr.ui as the client's UI kit ([UI kit and design system for the client](Rewrite-1.7)): which theme variables blockr.ui declares, what each is for, the defaults that blockr.ui gives them in both modes, how a frontend gives values of its own, as a theme, and draws its own parts with them, which value wins on the page, blockr.ui's default, the frontend's or the app's, and which defaults a frontend keeps.
It shapes the issues of [UI kit and design system for the client](Rewrite-1.7#work) that write the theme variables, [blockr.ui#109](https://github.com/BristolMyersSquibb/blockr.ui/issues/109), export `unset_variables()`, which tells which defaults a frontend keeps, [blockr.ui#111](https://github.com/BristolMyersSquibb/blockr.ui/issues/111), give a frontend's theme through `frontend_theme()` and write it into the page, [blockr.core#866](https://github.com/BristolMyersSquibb/blockr.core/issues/866) and [blockr.core#868](https://github.com/BristolMyersSquibb/blockr.core/issues/868), and move the dock onto the theme variables, [blockr.dock#673](https://github.com/BristolMyersSquibb/blockr.dock/issues/673).
The issues that drop today's code from blockr.ui, declare the list of theme variables, make an app's theme in blockr.ui and in blockr.theme, move the components, keep `dark_mode` with the user, move the assistant and the DAG, offer core's mark and status dot and write the design system's article rely on it too: [blockr.ui#107](https://github.com/BristolMyersSquibb/blockr.ui/issues/107), [blockr.ui#110](https://github.com/BristolMyersSquibb/blockr.ui/issues/110), [blockr.ui#112](https://github.com/BristolMyersSquibb/blockr.ui/issues/112), [blockr.theme#10](https://github.com/BristolMyersSquibb/blockr.theme/issues/10), [blockr.ui#114](https://github.com/BristolMyersSquibb/blockr.ui/issues/114), [blockr.core#867](https://github.com/BristolMyersSquibb/blockr.core/issues/867), [blockr.assistant#319](https://github.com/BristolMyersSquibb/blockr.assistant/issues/319), [blockr.graph#12](https://github.com/BristolMyersSquibb/blockr.graph/issues/12), [blockr.core#870](https://github.com/BristolMyersSquibb/blockr.core/issues/870) and [blockr.ui#116](https://github.com/BristolMyersSquibb/blockr.ui/issues/116).
It takes the place of the fix that [blockr.core#789](https://github.com/BristolMyersSquibb/blockr.core/issues/789) asks for.
The prefix, the mode's attribute, what the list of theme variables promises other packages and how the build preset writes the theme variables belong to [Building on blockr.ui](Rewrite-1.7.4), how an app gives its theme to [An app's theme](Rewrite-1.7.5), what a frontend is to [Plugins](Rewrite-1.1.12#the-frontend), and how a stylesheet loads with its module and where overlays sit to [UI modules in JS](Rewrite-1.1.7).

## What must hold

1. The stylesheet of blockr.ui gives every theme variable a default, for light mode and for dark mode, so that every page draws whole, whatever its frontend sets, a block that `serve()` serves alone included.
2. A frontend restyles the page by setting theme variables alone, in a theme of its own, and a value that it sets wins over blockr.ui's default.
3. Every colour that blockr.ui's components, core's UIs and the frontend's own parts draw comes from a theme variable, so that a frontend restyles them by setting those variables, and an app's theme restyles all of them.
   The colours of block categories are one exception, since they are core's ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).
   The black of a modal's backdrop and the black and white rings of a colour field are the other, since they must stand out on any colour ([Colours](#colours)).
4. The defaults take no colour from what surrounds an element: they are fixed values for each mode, and blockr.ui measures nothing and mixes no colour of the page into another.
5. A frontend's tests tell, for each mode, which theme variables the frontend leaves at blockr.ui's defaults, so that a frontend keeps a default only by choice.
6. Every page paints in its mode from the first paint, and never in one mode first and then in the other.

## Today

On main, blockr.ui's design tokens give the page its look, as variables such as `--blockr-color-bg-surface`.
Its `blockr-tokens.css` gives their values on `:root`, and its `blockr-tokens-dark.css` gives them again under `[data-bs-theme="dark"]`, Bootstrap's attribute for dark mode ([R/theme.R#L1-L67](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/R/theme.R#L1-L67)).
In dark mode, they give a surface of `#161b23` and a raised background of `#1e242e` ([inst/assets/css/blockr-tokens-dark.css#L40-L42](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens-dark.css#L40-L42)).
Its `theme_dep()` puts the tokens on the page together with a theme layer, which restyles Bootstrap's type, fields, buttons, tooltips and popovers from the tokens across the whole page.
The dock puts both on its board page, and its own stylesheet reads the tokens ([R/board-ui.R#L19-L21](https://github.com/BristolMyersSquibb/blockr.dock/blob/d8b30e148a43612e580f8970ceaf85b89e7fb6d2/R/board-ui.R#L19-L21)).
An app restyles the tokens with blockr.theme ([An app's theme](Rewrite-1.7.5#today)).

Core's board option `dark_mode` switches the page between the two modes through that attribute ([R/board-option.R#L539-L632](https://github.com/BristolMyersSquibb/blockr.core/blob/5abaa52bc04bf202dab9c6e17772f2a170b10a38/R/board-option.R#L539-L632)).
A board holds its value, which the board's script or the blockr option `dark_mode` gives.
Where neither gives one, the page follows the mode that the user's system prefers.
R knows the opening board as it serves the page.
So the board option's UI puts a line into the page's head that sets the attribute before the first paint.

On `js-state`, core's runtime stylesheet, which loads on every page, holds core's Tailwind theme, its variables with their values, which move to blockr.ui ([srcts/runtime/index.css#L86-L180](https://github.com/BristolMyersSquibb/blockr.core/blob/e59b17104009684c9d15fb56c0f38ad53d523fa7/srcts/runtime/index.css#L86-L180), [UI kit and design system for the client](Rewrite-1.7#what-blockrui-holds)).
Those values are the basic frontend's look: the page is the browser's `Canvas`, a card is `bg-subtle`, 5% of the text over the page, and a menu or a dialog is `bg-raised`, the page's colour mixed with 10% of the text in dark mode.
The basic frontend has no stylesheet of its own.
Core's UIs also name 10 colours of Tailwind's palette under core's prefix, 32 times in 8 files, most of them with a variant for dark mode, as a popover's `bc:text-gray-900` and `bc:dark:text-gray-100` in place of `text-default` ([srcts/overlays/popover.tsx#L20](https://github.com/BristolMyersSquibb/blockr.core/blob/e59b17104009684c9d15fb56c0f38ad53d523fa7/srcts/overlays/popover.tsx#L20)).
So do the tints of a card's notifications, `bc:bg-red-500/10`, `bc:bg-amber-500/10` and `bc:bg-blue-500/10`, although core's Tailwind theme gives `bg-danger` and `bg-warning` for the first two ([srcts/card/footer.tsx#L211-L225](https://github.com/BristolMyersSquibb/blockr.core/blob/e59b17104009684c9d15fb56c0f38ad53d523fa7/srcts/card/footer.tsx#L211-L225)).

On `js-state`, the dock draws its panels and cards from copies of blockr.ui's tokens, such as `--blockr-dock-bg-surface: var(--blockr-color-bg-surface, #ffffff)`, and sets none of core's variables ([srcts/modules/dock/index.css#L88-L186](https://github.com/BristolMyersSquibb/blockr.dock/blob/5d9a4764709d0e3a391117855c0434cf06034bfb/srcts/modules/dock/index.css#L88-L186)).
So core's menus, select lists, dialogs and fields inside the dock wear the basic frontend's colours.
In dark mode they show as neutral grey panels over the dock's blue-grey cards, as [blockr.core#789](https://github.com/BristolMyersSquibb/blockr.core/issues/789) measured.

A first fix, [blockr.core#795](https://github.com/BristolMyersSquibb/blockr.core/pull/795), closed unmerged, gave core's defaults blockr.ui's values, which fitted the dock but turned the basic frontend's menus blue-grey over its neutral grey cards.
It then derived core's colours from what surrounds an element: a border mixed the text's colour, and a raised surface lightened the colour that core measured behind what opened it.
That worked around the misplaced values rather than moving them.

## Proposal

### Which theme variables blockr.ui declares

The theme variables are the CSS variables through which any frontend gives the page the look it likes, and through which an app's theme gives the whole page the app's look.
A theme is values for some of them, in light mode and in dark mode.
Every UI draws with them: blockr.ui's components, core's UIs, the frontend's own parts, and the UIs of blocks and plugins.
The set is as big as that needs and as small as it can be, so it holds the colours, fonts, sizes of text, radii, shadows and spacing that a frontend may want its own, and leaves the rest of how components look to blockr.ui.
Each is a variable that Tailwind CSS 4 keeps its theme in, under the prefix `bk`, as `--bk-color-popover` and `--bk-spacing`, which every package's classes read through `@theme inline`, as core's `bc:bg-popover` and `bc:px-2` do ([Building on blockr.ui](Rewrite-1.7.4#prefixes)).
The stylesheet of blockr.ui declares the variables and gives each a default for both modes, its documentation says what each is for, and it exports their list ([Building on blockr.ui](Rewrite-1.7.4#the-list-of-theme-variables)).
A frontend sets the variables whose values it wants its own, in its theme, and keeps blockr.ui's defaults for the rest ([Where the values are set](#where-the-values-are-set), [The defaults](#the-defaults)), and an app's theme sets those whose values the app wants its own, over the frontend's ([An app's theme](Rewrite-1.7.5)).
Beside them, the theme variable `--bk-z-index-overlay` gives the layer that every overlay stacks on, whose default [The defaults](#the-defaults) gives.

#### Colours

The colours take the names that shadcn/ui gives their jobs, under the prefix `bk`, so that the set gets the thought that went into one that many projects draw with, and its names are those that authors of UIs on Tailwind know ([theming.mdx#L62-L84](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/content/docs/%28root%29/theming.mdx?plain=1#L62-L84)).
React Aria's components draw with them already in JollyUI, whose button reads `bg-primary`, `text-primary-foreground`, `border-input` and `ring-ring` ([button.tsx#L19-L33](https://github.com/jolbol1/jolly-ui/blob/e2272fbc1acceef0f59c0e166467962ac5b16a71/src/registry/new-york/ui/button.tsx#L19-L33)).
Today's blockr.ui leads each name with its property, as `--blockr-color-text-muted`, after GitHub's Primer and Shopify's Polaris, and calls its brand colour `accent`, since its body text was `text-primary` ([naming.md#L36-L41](https://github.com/BristolMyersSquibb/blockr.ui/blob/caf3f835146ff6cb916aef775cf283876c58b8a9/dev/design-system/naming.md#L36-L41), [#L174-L176](https://github.com/BristolMyersSquibb/blockr.ui/blob/caf3f835146ff6cb916aef775cf283876c58b8a9/dev/design-system/naming.md#L174-L176)).
Under shadcn/ui's names the body text is `foreground`, so the brand colour is `primary`, and `accent` is the fill of a hover.
A UI reads the colour whose use it shares:

| Variable | What reads it |
|---|---|
| `--bk-color-background`, `--bk-color-foreground` | The page, which the frontend draws behind its panels and cards, as the dock does behind dockview's panels, and the text on it |
| `--bk-color-card`, `--bk-color-card-foreground` | A card or a node that a plugin draws on the page or in a panel, such as the DAG's nodes, the dock's cards and the basic frontend's cards, and its text. The card is opaque, since a node covers the links below it |
| `--bk-color-popover`, `--bk-color-popover-foreground` | Every overlay, such as a menu, a select's list, a popover, a dialog, a sheet, a tooltip or a toast, and a slider's thumb, and its text. The popover is opaque, since an overlay covers the page |
| `--bk-color-primary`, `--bk-color-primary-foreground`, `--bk-color-primary-text` | The brand colour: what is picked or checked, such as a checked checkbox or a picked day, the primary button, the check of a picked option, the edge of what is selected or current, and the tints of a message's banner, pill and toast; the text and icons on it; and the text of a link and of a message |
| `--bk-color-secondary`, `--bk-color-secondary-foreground` | A filled control of lower emphasis, and its text |
| `--bk-color-muted`, `--bk-color-muted-foreground` | A quiet fill inside a surface, such as a tag or a block of code, and secondary text, such as a hint, a placeholder, a count or a block's summary |
| `--bk-color-accent`, `--bk-color-accent-foreground` | A row or a button that is hovered, pressed or focused from the keyboard, and its text |
| `--bk-color-destructive`, `--bk-color-destructive-foreground`, `--bk-color-destructive-text` | An error and what removes: the mark of an error, the edge of an invalid field, the destructive button, and the tints of an error's banner, pill and toast and of the row of a menu that removes; the text on the destructive button; and the text of an error and of that row |
| `--bk-color-warning`, `--bk-color-warning-foreground`, `--bk-color-warning-text` | A warning: its mark and the tints of its banner, pill and toast; the text on a fill of it; and its text |
| `--bk-color-success`, `--bk-color-success-foreground`, `--bk-color-success-text` | A success: its mark, such as the status dot of a block that is `ready` ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)), and its tints; the text on a fill of it; and its text |
| `--bk-color-border` | Outlines and dividers: the edge of a card or an overlay, the rules of a table, a menu's divider and a slider's track |
| `--bk-color-input` | The edge of a field, such as a text, number, search or token field, a select, a combo box, a date field or picker, or a colour field, and the outline of a checkbox, a radio button, a switch or a drop zone |
| `--bk-color-ring` | The focus ring |

An error, a warning and a success each have a colour, as the building blocks of every page that tells the user how things stand: `destructive`, which shadcn/ui names, and `warning` and `success`, which the theme variables add beside it, while a message takes the colours of `primary`.
The page draws all three: a block raises warnings as well as errors, which its card tints apart, and the status dot draws `waiting` and `invalid` in the colour of a warning and `ready` in that of a success ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).
The set of shadcn/ui stops at `destructive` only because its own components draw no warning or success: its alert comes in `default` and `destructive` alone, and its toasts mark a success or a warning with an icon, in the popover's colours ([alert.tsx#L8-L16](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/registry/new-york-v4/ui/alert.tsx#L8-L16), [sonner.tsx#L21-L31](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/registry/new-york-v4/ui/sonner.tsx#L21-L31)).
So blockr.ui adds the two as shadcn/ui's documentation adds a colour, with its `-foreground`, under `:root` and for dark mode, through `@theme inline`, which takes a warning as its example ([theming.mdx#L118-L138](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/content/docs/%28root%29/theming.mdx?plain=1#L118-L138)).

The colours `primary`, `destructive`, `warning` and `success` do the same jobs, so each comes with the same three variables:

1. The colour itself gives the mark, the edge and the fill, and the tints of a banner, a pill and a toast, which come from it through the opacity modifier, as `bg-warning/10`.
2. Its `-foreground` gives the text on a fill of the colour, as on the destructive button.
3. Its `-text` gives text in the colour, on any surface and on the colour's own tints, as an error's message does.

One colour cannot do all three in both modes.
White text on the red of the destructive button reaches 4.8:1 in light mode, but 2.8:1 on the red of dark mode, `#f87171`.
In light mode, the shade of a mark is too light for text on its own tint, and so are some of today's texts: red-600 reaches 4.0:1 there, and today's amber text, amber-700, 4.3:1.
Today's blockr.ui names a text apart from a fill and a border for each state for the same reason ([blockr-tokens.css#L14-L15](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css#L14-L15)).
A state that nothing of blockr's fills yet, such as a warning, still has its `-foreground`, so that a block's UI can draw every state in each of the three ways.

The theme variables hold no `danger` beside `destructive`, since `destructive` marks an error as well as what removes, as shadcn/ui's form draws an error's message in `text-destructive` ([form.tsx#L150](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/registry/new-york-v4/ui/form.tsx#L150)).
A second name for that job would have every theme set it twice, and the two could drift apart.
The set leaves out shadcn/ui's colours of charts, since the colours of data come from blockr.theme's palettes or its scale map, and those of its sidebar, since a frontend's sidebar draws with the colours above.

A field's edge stands out more than an outline or a divider does, since it alone marks a field, and the outline of a checkbox, a radio button, a switch or a drop zone alone marks one that is unchecked, off or empty.
So `input` is stronger than `border`.
Its default is Tailwind's gray-400, and gray-600 in dark mode, about 2.1:1 to 2.6:1 against what it sits on, the least on a dialog in dark mode.
That lies between the soft border of today's blockr.ui, about 1.2:1, and the 3:1 that [WCAG 2.2's success criterion 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) asks of what marks a control, at which a full frame looked too heavy.

The theme variables hold a colour for the page, `background`, so that an app's theme reaches the page under every frontend, which draws it behind its panels and cards ([The frontend's own parts](#the-frontends-own-parts)).
A plugin's UI leaves its own background transparent, so that it shows the page or the panel that the frontend puts it in.
The theme variables hold no fill for a field, since the fields that move from core's React SDK have none.
The hover, `accent`, has a name of its own, apart from `muted`, since the two differ once their values are solid colours, as blockr.ui's defaults are: the subtle fill of today's blockr.ui, `#f9fafb`, differs from a white menu by 1.05:1, which nobody sees, while its hover, `#f3f4f6`, reaches 1.10:1.

The secondary button keeps its frame, as today's design system and core's SDK on `js-state` draw it, so it reads `border`, and `accent` under the pointer ([design-system.Rmd#L851](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/vignettes/articles/design-system.Rmd#L851)).
No component of blockr.ui fills with `secondary` yet.
The theme variables keep it, with its `-foreground`, for a UI that draws a filled control of lower emphasis, as one written after shadcn/ui does.

Two things draw in black and white of their own, since each must stand out on any colour: the backdrop behind a modal, black at 40%, which dims whatever page lies below it, and the rings of a colour field's thumbs and swatches, which show on any colour that the user picks.

The theme variables hold no other colour, since Tailwind's palette, whose colours follow neither a theme nor the mode, is no part of them ([UI kit and design system for the client](Rewrite-1.7#designed-against-tailwind)).
So every UI that draws with classes built by blockr.ui's preset, blockr.ui's components, core's UIs and those of plugins and blocks, takes its colours from the variables above.
The build preset fails a build whose code names a colour of Tailwind's palette, under any prefix ([Building on blockr.ui](Rewrite-1.7.4#the-build-preset)).
A UI that needs a shade between two variables derives it from them in its own stylesheet, as `color-mix(in oklab, var(--bk-color-primary) 15%, var(--bk-color-card))`, or tints one with Tailwind's opacity modifier, as `bc:bg-primary/20`, and both follow the theme and the mode.
A colour that must stay fixed it writes on purpose, as `bc:bg-[#0072b2]`, and the colours of data, such as a chart's series, come from blockr.theme's palettes or its scale map rather than from the theme variables.
Where several packages need a colour that no variable gives, the theme variables take it in a later version of blockr.ui, with defaults ([Which defaults a frontend keeps](#which-defaults-a-frontend-keeps)), so that the set grows by what its users show they need, as it grows by `warning` and `success` beside shadcn/ui's.

#### Fonts, sizes, radii, shadows and spacing

The rest of the set takes the names that Tailwind's theme gives these variables, under the prefix `bk`, each with a default that a frontend may set, as it may set the colours:

| Variable | What reads it |
|---|---|
| `--bk-font-sans`, `--bk-font-mono` | The face of every UI's text, and of its code |
| `--bk-text-xs`, `--bk-text-sm`, `--bk-text-base`, `--bk-text-lg` | The sizes of text, from a pill's or a hint's up to a dialog's title, each of whose line heights follows its size |
| `--bk-radius` | The base of every corner, from which each step of the radius scale derives, from a checkbox's or a tag's up to a dialog's or a card's |
| `--bk-shadow-sm`, `--bk-shadow-md`, `--bk-shadow-lg` | The shadow of a slider's or a switch's thumb, of menus, lists, popovers, tooltips and toasts, and of dialogs and sheets |
| `--bk-spacing` | The unit of which every padding, margin, gap and size of a component is a multiple, as `bc:px-2` pads by twice it |

The radii derive from `--bk-radius`, as shadcn/ui's derive from `--radius`: `radius-lg` is the base, and every other step is a multiple of it, from 0.6 of it for `radius-sm` to 2.6 of it for `radius-4xl`, which the build preset writes through `@theme inline` ([theming.mdx#L93-L117](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/content/docs/%28root%29/theming.mdx?plain=1#L93-L117)).
So a theme sets one value and every corner follows, and a theme made for shadcn/ui carries its `--radius` over as `--bk-radius`.
A component that draws a step that the scale lacks, as the colour picker draws `rounded-xs`, draws the smallest step instead, `rounded-sm`.
The shadows come in three steps, as those of today's blockr.ui do, so a component that draws another step, as the sheet draws `shadow-2xl`, draws the nearest of the three.
A pill stays round under every theme, so `rounded-full` derives from no variable.

The weights of the faces, the line heights and letter spacing that the classes name, and the timing of transitions are not in the set, since no frontend needs its own to fit its look, and blockr.ui keeps Tailwind's values for them as part of its components.

A frontend thus sets the type and the density of every UI, as today's blockr.ui draws its text at 13 pixels where core's fields on `js-state` draw 14.
So blockr.ui's components take every size from the set: the few fixed sizes that they hold on `js-state`, such as a field's height of 30 pixels, become multiples of the spacing or follow the line height of their text, so that a frontend's spacing and sizes of text reach them too.
The build preset maps the classes of shadows onto these variables, as it maps the rest of the set, so that they read them ([Building on blockr.ui](Rewrite-1.7.4#the-build-preset)).

### Where the values are set

Three sources set the theme variables, each over the one before:

1. The stylesheet of blockr.ui gives every variable its default.
2. The frontend's theme sets the values that the frontend wants its own.
3. An app's theme sets the values that the app wants its own ([An app's theme](Rewrite-1.7.5)).

A frontend gives its values as an app gives its own: as a theme, which blockr.ui's `new_blockr_theme()` makes in R ([A theme in R](Rewrite-1.7.5#a-theme-in-r)).
Core defines the generic `frontend_theme()`, whose method returns the frontend's theme ([Plugins](Rewrite-1.1.12#the-frontend)).
R calls `frontend_theme()` on the app's frontend as `serve()` builds the app, as it calls `frontend_args()`.
Core's method for `frontend_plugin` returns a theme with no values, so a frontend that keeps every default needs no method of its own.

No other stylesheet of a package styles `:root`.
No stylesheet of a package but blockr.ui's sets a theme variable either, for two reasons:

1. A value that a stylesheet sets on an element below `:root` wins there over both themes, since the element no longer inherits the variable.
2. A value in a stylesheet escapes the frontend's theme, which the frontend's tests read ([Which defaults a frontend keeps](#which-defaults-a-frontend-keeps)).

So the check of the build preset fails another package's build whose stylesheet sets a variable under `--bk-` ([The build preset](Rewrite-1.7.4#the-build-preset)).

The stylesheet of blockr.ui sets its defaults inside a cascade layer, under three selectors:

1. Under `:root`, it sets the defaults that are the same in both modes, such as the fonts, the sizes of text, the radius, the spacing and the layer of the overlays.
2. Under `:root[data-bk-mode="light"]`, it sets the colours and the shadows of light mode, and the browser's `color-scheme`, `light`.
3. Under `:root[data-bk-mode="dark"]`, it sets those of dark mode, and `color-scheme: dark`.

R writes the frontend's theme and then the app's into the page's head, after blockr.ui's stylesheet, each through blockr.ui's method of `format()` ([The rules that R writes](Rewrite-1.7.5#the-rules-that-r-writes)).
For two of the variables, a frontend's method of `frontend_theme()` would return:

```r
new_blockr_theme(
  light = list("--bk-color-popover" = "#fafafa", "--bk-spacing" = "0.25rem"),
  dark = list("--bk-color-popover" = "#262626", "--bk-spacing" = "0.25rem")
)
```

R writes that theme as two rules:

```css
:root:root[data-bk-mode="light"] {
  --bk-color-popover: #fafafa;
  --bk-spacing: 0.25rem;
}

:root:root[data-bk-mode="dark"] {
  --bk-color-popover: #262626;
  --bk-spacing: 0.25rem;
}
```

Every element inherits the values from `:root`, so that an overlay takes them wherever it sits, React Aria's portal at the end of the page's body included ([UI modules in JS](Rewrite-1.1.7#react)).

Which value wins follows from where each source sets it:

1. R writes both themes outside any layer, so their values win over blockr.ui's defaults, which sit in one.
2. The rules of the two themes have the same selectors, so the later rule wins: the app's, which R writes after the frontend's.
3. Each rule names `:root` twice beside the mode's attribute, which gives it a specificity of (0,3,0).
   A stylesheet that the check does not reach may still set a theme variable under `:root[data-bk-mode="light"]`, at (0,2,0).
   Both themes win over such a value, whichever loads first.

The rule of light mode names its mode as well.
A rule of `:root:root` alone would hold in dark mode too, where it would win over blockr.ui's defaults of dark mode.

The values hold from the first paint, core's loading note included, since R writes both themes into the page's head.
They outlive the opening of another board, since the page keeps its head and never switches to another frontend ([Drawing the board](Rewrite-1.1.8#opening-a-board)).
On `js-state`, the dock sets its own variables on its own elements, and on the block's menu through that menu's class, so that an overlay without that class, such as a select's list in a block's UI, gets none of them, while a value on `:root` reaches every overlay.

### The frontend's own parts

A frontend draws its own parts with the theme variables too, such as the dock's cards, its navbar and the frame that dockview draws around its panels, so that an app's theme restyles them with every other UI ([An app's theme](Rewrite-1.7.5)).
So the frontend's stylesheet takes every colour, face, size, radius and shadow of those parts from a theme variable, and holds no colour of its own, since the values that the frontend sets are in its theme.
Where a part needs a value that no theme variable gives, such as a grey between two of its own or the larger radius of the dock's panels, the frontend takes the variable whose job comes closest, or derives the value from theme variables in its own stylesheet, which an app's theme then reaches only through the values it derives from.

On `js-state`, the dock defines 26 colours for itself ([srcts/modules/dock/index.css#L93-L185](https://github.com/BristolMyersSquibb/blockr.dock/blob/5d9a4764709d0e3a391117855c0434cf06034bfb/srcts/modules/dock/index.css#L93-L185)).
Eighteen of them do the jobs of theme variables, and its selected fill is a tint of `primary`.
It uses each of the other seven once to three times: a secondary and a disabled text, a stronger accent text, a field's fill, a strong border, a subtle accent border and the colour of its logo.
So the dock may draw two greys of text where it draws four on `js-state`.
Only the colour of the page, behind dockview's panels, is a colour of its own rather than a step of another, so the theme variables hold it, as `background` ([Colours](#colours)).
The dock gives dockview's variables their values from the theme variables as well, as it gives them blockr.ui's tokens on `js-state` ([#L596-L651](https://github.com/BristolMyersSquibb/blockr.dock/blob/5d9a4764709d0e3a391117855c0434cf06034bfb/srcts/modules/dock/index.css#L596-L651)).

### Light mode and dark mode

A theme has two modes, light mode and dark mode, and gives each variable that it sets a value for both, whether it is blockr.ui's defaults, a frontend's theme or an app's theme.
Core's board option `dark_mode` switches the page between the two, through the attribute `data-bk-mode` on the page's root, as the user picks one or as the user's system prefers ([Building on blockr.ui](Rewrite-1.7.4#prefixes), [Board options and blockr options](Rewrite-1.1.13#where-the-two-meet)).
Its value stays with the user, in the browser, rather than with the board ([Board options and blockr options](Rewrite-1.1.13#board-options-that-stay-with-the-user)).
So no theme is light or dark alone.
In VS Code and JupyterLab a colour theme is one or the other, and the user picks one theme among many, since a theme is a plugin of its own there.
Here a theme comes with the page's one frontend, or with the app, so it holds both modes, and `dark_mode` stays the only switch.
A theme with one mode would also clash with what switches beside it: blockr.ui's defaults differ by mode, and the browser draws its scrollbars and form controls in the mode that core switches the page to.
A frontend's theme holds each of its values in `light` or in `dark`, and R writes each under the attribute of its mode, so that no value of its light mode, such as a white menu, shows in its dark mode.

The page knows its mode before it first paints, since the value of `dark_mode` stays with the user rather than with the board, which opens later:

1. R writes into the page's head a line that sets the mode, with the value of the blockr option `dark_mode` where the app or its deployment sets one.
2. As the page loads, the line reads the user's pick of `dark_mode` from the browser's storage.
   Where the user has picked nothing, it takes the blockr option's value, and where that is not set either, the mode that the user's system prefers.
3. The line sets `data-bk-mode` to `light` or `dark` before the page first paints, so that core's loading note draws in that mode too.
4. Once the board opens, core's `dark_mode` reads the same three, so that the board option and the page agree, and core switches the attribute whenever the user picks the other mode.

So every page paints in its mode from the start, as main's line has it paint today from the board's value (Today), and never in one mode first and then in the other.
The page's `color-scheme` tag takes `light dark`, while blockr.ui's stylesheet sets `color-scheme` under the attribute of each mode ([Where the values are set](#where-the-values-are-set)).

### The defaults

The defaults are fixed values, one for light mode and one for dark mode, since blockr.ui takes no colour from what surrounds an element.
For the look, each colour's default is the value that the token of today's blockr.ui with the same job takes in that mode, as `popover` is `#ffffff` in light mode and `#1e242e` in dark mode, and `card` is `#ffffff` and `#161b23` ([inst/assets/css/blockr-tokens.css#L94-L98](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css#L94-L98), [blockr-tokens-dark.css#L40-L42](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens-dark.css#L40-L42)), so that the look roughly keeps today's ([UI kit and design system for the client](Rewrite-1.7#designed-against-tailwind)).
In dark mode, `popover` is lighter than `card`, as today's raised background is lighter than its surface, so that a menu stands apart from the card that it opens from.
In light mode, both are white, and a menu stands apart by its border and its shadow.
A token that mixes others gives its job the fixed value that its mix comes to.
Today's hover in dark mode lays 6% of the text over what lies below ([blockr-tokens-dark.css#L46](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens-dark.css#L46)), so `accent` takes that mix over `popover`, `#2b303a`, the lighter of the two surfaces that a hover sits on.
It stands out from a menu at 1.18:1 and from a card at 1.31:1, while the mix over `card`, `#232830`, would differ from a menu by 1.05:1.
A job that no token does takes a value of Tailwind's palette, as `input` does ([Colours](#colours)).
The colours `secondary` and `secondary-foreground` take the defaults of `accent` and `accent-foreground`, as shadcn/ui gives the two pairs one value in each mode ([theming.mdx#L214-L219](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/content/docs/%28root%29/theming.mdx?plain=1#L214-L219), [#L248-L253](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/content/docs/%28root%29/theming.mdx?plain=1#L248-L253)).
The colours of the states take today's borders: `destructive` takes `#dc2626`, `warning` takes `#d97706`, and `success` takes `#16a34a`, which the status dot of a `ready` block draws today ([blockr-tokens.css#L119-L121](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css#L119-L121)).
The colour `primary` takes today's accent fill, `#2563eb` ([#L108](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css#L108)).
Each `-text` takes the lightest of Tailwind's shades of its hue that reaches 4.5:1 on every surface of light mode, and on the colour's own tint over it:

| Variable | Default in light mode | On the tint, at least |
|---|---|---|
| `--bk-color-destructive-text` | Red-700, `#b91c1c`, today's red text | 5.3:1 |
| `--bk-color-warning-text` | Amber-800, `#92400e` | 6.1:1 |
| `--bk-color-success-text` | Green-800, `#166534` | 6.1:1 |
| `--bk-color-primary-text` | Blue-700, `#1d4ed8` | 5.6:1 |

Today's amber and green texts, the 700 shades, reach 4.3:1 on the tint, so the two take the 800 shades, as core's stylesheet on `js-state` takes amber-800 for its warnings ([blockr-tokens.css#L84-L86](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css#L84-L86), [srcts/runtime/index.css#L89-L90](https://github.com/BristolMyersSquibb/blockr.core/blob/e59b17104009684c9d15fb56c0f38ad53d523fa7/srcts/runtime/index.css#L89-L90)).
In dark mode, each `-text` takes today's text of its state, which reads at 4.9:1 or more on every dark surface and tint, as `primary-text` takes `#60a5fa` where `primary` is `#3b82f6` ([blockr-tokens-dark.css#L50-L55](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens-dark.css#L50-L55)).
Each `-foreground` takes white where white reaches 4.5:1 on the colour, as on `destructive` at 4.8:1 and on `primary` at 5.2:1.
On `warning` and `success`, where white reaches only 3.2:1 and 3.3:1, it takes today's dark text, `#111827`.
In dark mode, every `-foreground` takes `#0e1219`, as today's text on the accent fill does ([blockr-tokens-dark.css#L49](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens-dark.css#L49)).
The fonts, the sizes of text, the radii, the shadows and the spacing take Tailwind's own scales, from which blockr.ui's look starts, and today's values where that look departs from them, as today's blockr.ui draws its small text at `0.8125rem`, 13 pixels, where Tailwind's is 14 ([blockr-tokens.css#L152-L156](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css#L152-L156)).
So the page keeps the look of today's blockr.ui wherever its frontend sets nothing, and a variable that a later version of blockr.ui adds draws at once under every frontend that does not know it yet, as VS Code registers a default for each of its colours, for light and for dark themes, and takes the default wherever a theme leaves a colour out ([colorUtils.ts#L70-L75](https://github.com/microsoft/vscode/blob/817607ae52b88ef6021bb456e5995b6367e1b481/src/vs/platform/theme/common/colorUtils.ts#L70-L75), [#L222-L223](https://github.com/microsoft/vscode/blob/817607ae52b88ef6021bb456e5995b6367e1b481/src/vs/platform/theme/common/colorUtils.ts#L222-L223)).

Core's basic frontend and the dock keep every one of blockr.ui's defaults, since their look is blockr.ui's, so that the values of that look have one home.
So neither has a method of `frontend_theme()`, and both take core's, which returns a theme with no values ([Where the values are set](#where-the-values-are-set)).
The basic frontend draws its page in `background` and its cards in `card`, so it needs no stylesheet of its own, as on `js-state`.
A block that `serve()` serves alone draws in blockr.ui's defaults, since its page has no frontend ([Defining a board in R](Rewrite-1.1.3#data-passed-to-serve)), or in the app's theme where the app gives one ([An app's theme](Rewrite-1.7.5)).

The layer of the overlays takes this default:

| Variable | What reads it | Default |
|---|---|---|
| `--bk-z-index-overlay` | Every overlay, which stacks above everything else on the page ([UI modules in JS](Rewrite-1.1.7#react)) | 1100 |

The theme variables hold no colour for a block's status or for a category of block classes, since both are core's.
Core maps each status onto a theme variable, as `ready` onto `success`, and holds the colours of the categories itself, outside every theme ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).

### Which defaults a frontend keeps

Beside the list of theme variables, blockr.ui exports for tests `unset_variables()`.
It takes a theme, as `new_blockr_theme()` makes it, and returns, for light mode and for dark mode, the theme variables that the theme sets no value for, in the order of `theme_variables()`.
For a frontend's theme, those are the defaults of blockr.ui that the frontend keeps.
A frontend's tests check that `unset_variables()` returns exactly what the frontend keeps on purpose, for the theme that `frontend_theme()` returns for the frontend.
The tests of core's basic frontend and of the dock list every variable, since both keep every default:

```r
expect_identical(
  unset_variables(frontend_theme(new_dock_plugin())),
  list(
    light = c("--bk-color-background", "--bk-color-foreground", ...),
    dark = c("--bk-color-background", "--bk-color-foreground", ...)
  )
)
```

So a default that a frontend keeps is a choice that its tests write down, and a colour that it sets for light mode alone shows up in its list for dark mode.
No value of a frontend's escapes its theme, since the check of the build preset fails a build whose stylesheet sets a variable under `--bk-` ([Where the values are set](#where-the-values-are-set)).
When blockr.ui adds a variable, in a minor release ([Building on blockr.ui](Rewrite-1.7.4#the-list-of-theme-variables)):

1. Every page draws the new variable in blockr.ui's default, so nothing breaks for users.
2. The next time a frontend's tests run against that blockr.ui, they fail and name the new variable.
3. The frontend's author sets the variable in the frontend's theme, or adds it to the defaults that the frontend keeps.

Nothing warns of a kept default while the page runs, since a deployed app would then warn on every page, for the defaults that a frontend keeps on purpose too.

## Open questions

None.

<details><summary>Notes for implementers</summary>

- The build preset of blockr.ui drops Tailwind's palette with `--color-*: initial` and declares `--color-black` and `--color-white` again, for the backdrop and the colour field's rings, while `bg-transparent` and `bg-current` need no variable.
- The DAG and core's Edit board plugin take their colours from the theme variables already ([Drawing the DAG](Rewrite-1.3.2#its-look), [The Edit board plugin](Rewrite-1.1.15#its-look)), so an app's theme reaches them with no change but the names under `bk` and the move off Tailwind's palette.
- Core loads a frontend's stylesheet, and waits for it, before it opens the board, so that the frontend's own parts are styled from the board's first paint.
  The frontend's values need no such wait, since R writes the frontend's theme into the page's head.
- The CSS of shadcn/ui sets its variables without a prefix, as `--card`, and maps them through `@theme inline` onto `--color-card`, while blockr.ui's carry the prefix, as `--bk-color-card`, so a theme made for shadcn/ui maps onto blockr.ui's name by name ([Building on blockr.ui](Rewrite-1.7.4#prefixes)).

The defaults that [The defaults](#the-defaults) gives, from the tokens of today's blockr.ui at `e14e831`, with each variable named without `--bk-` and, for a colour, without `color-`, as `background` for `--bk-color-background`:

| Variables | Light mode | Dark mode | From |
|---|---|---|---|
| `background`, `foreground` | `#f9fafb`, `#111827` | `#0e1219`, `#f0f3f7` | Today's page and text |
| `card`, `card-foreground` | `#ffffff`, `#111827` | `#161b23`, `#f0f3f7` | Today's surface and text |
| `popover`, `popover-foreground` | `#ffffff`, `#111827` | `#1e242e`, `#f0f3f7` | Today's raised background and text |
| `primary`, `primary-foreground`, `primary-text` | `#2563eb`, `#ffffff`, `#1d4ed8` | `#3b82f6`, `#0e1219`, `#60a5fa` | Today's accent fill, the text on it, and its strong accent text, in dark mode its accent text |
| `secondary`, `secondary-foreground` | `#f3f4f6`, `#111827` | `#2b303a`, `#f0f3f7` | Those of `accent` |
| `muted`, `muted-foreground` | `#f9fafb`, `#6b7280` | `#14181f`, `#8a94a3` | Today's subtle fill and muted text |
| `accent`, `accent-foreground` | `#f3f4f6`, `#111827` | `#2b303a`, `#f0f3f7` | Today's hover and text, in dark mode 6% of the text over `popover` |
| `destructive`, `destructive-foreground`, `destructive-text` | `#dc2626`, `#ffffff`, `#b91c1c` | `#f87171`, `#0e1219`, `#f87171` | Today's red border and red text |
| `warning`, `warning-foreground`, `warning-text` | `#d97706`, `#111827`, `#92400e` | `#fbbf24`, `#0e1219`, `#fbbf24` | Today's amber border, and amber-800 for text |
| `success`, `success-foreground`, `success-text` | `#16a34a`, `#111827`, `#166534` | `#4ade80`, `#0e1219`, `#4ade80` | Today's green border, and green-800 for text |
| `border` | `#e5e7eb` | `#232932` | Today's border |
| `input` | `#99a1af` | `#4a5565` | Tailwind's gray-400, `oklch(70.7% 0.022 261.325)`, and gray-600, `oklch(44.6% 0.03 256.802)` |
| `ring` | `#2563eb` | `#3b82f6` | Today's accent border, which draws the focus outline |
| `font-sans` | `"Open Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` | The same | Today's body face, whose files blockr.ui ships ([blockr-base.css#L35-L36](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-base.css#L35-L36)) |
| `font-mono` | `'SF Mono', 'Fira Code', 'Consolas', 'Monaco', monospace` | The same | Today's ([blockr-tokens.css#L162](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css#L162)) |
| `text-xs`, `text-sm`, `text-base`, `text-lg` | `0.75rem`, `0.8125rem`, `0.875rem`, `1rem` | The same | Today's sizes ([#L152-L155](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css#L152-L155)) |
| `radius` | `0.5rem` | The same | Today's large radius, 8 pixels ([#L174](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css#L174)) |
| `shadow-sm`, `shadow-md`, `shadow-lg` | Today's three, at 10% to 25% black | Today's three of dark mode, at 50% to 70% black | Today's ([blockr-tokens.css#L184-L186](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css#L184-L186), [blockr-tokens-dark.css#L67-L69](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens-dark.css#L67-L69)) |
| `spacing` | `0.25rem` | The same | Tailwind's |
| `z-index-overlay` | `1100` | The same | Core's on `js-state` |

From `0.5rem`, the radius scale gives corners of 4.8, 6.4, 8 and 11.2 pixels, where today's are 4, 6, 8 and 12.

Muted text reaches 4.4:1 on `accent` in light mode and 4.3:1 in dark mode, below the 4.5:1 that text needs.
So a hovered row draws its muted text in `accent-foreground`, as today's design system keeps muted text off a hover ([blockr-tokens.css#L72-L75](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css#L72-L75)).

On `js-state`, R's `page_color_scheme()` writes into the page's `color-scheme` tag the mode that it works out from the opening board's `dark_mode` or else from the blockr option, and `light dark` only where it knows neither ([R/utils-serve.R#L600-L637](https://github.com/BristolMyersSquibb/blockr.core/blob/35971d0b134948285d8ea8c6157f1a2a01aacc6f/R/utils-serve.R#L600-L637)).
It writes `light dark` on every page instead ([Light mode and dark mode](#light-mode-and-dark-mode)).

</details>
