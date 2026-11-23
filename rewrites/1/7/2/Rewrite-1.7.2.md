# The theme's variables: their jobs, their defaults and a frontend's values
Status: review. Design for [UI kit and design system for the client](Rewrite-1.7).

One of the designs for blockr.ui as the client's UI kit ([UI kit and design system for the client](Rewrite-1.7)): which variables blockr.ui's theme names, what each is for, the defaults that blockr.ui gives them in both modes, how a frontend sets values of its own and where, and draws its own parts with them, and which defaults a frontend keeps.
It takes the place of the fix that [blockr.core#789](https://github.com/BristolMyersSquibb/blockr.core/issues/789) asks for.
The prefix, the mode's attribute, what the theme's list promises other packages and how the build preset writes the theme belong to [Building on blockr.ui](Rewrite-1.7.4), how an app's theme sets values over the frontend's to [An app's theme](Rewrite-1.1.17), what a frontend is to [Plugins](Rewrite-1.1.12#the-frontend), and how a stylesheet loads with its module and where overlays sit to [UI modules in JS](Rewrite-1.1.7).

## What must hold

1. The stylesheet of blockr.ui gives every variable of its theme a default, for light mode and for dark mode, so that every page draws whole, whatever its frontend sets, a block that `serve()` serves alone included.
2. A frontend restyles the page by setting variables of blockr.ui's theme alone, and a value that it sets wins over blockr.ui's default, whichever stylesheet loads first.
3. Every colour that blockr.ui's components, core's UIs and the frontend's own parts draw comes from a variable of blockr.ui's theme, so that a frontend restyles them by setting those variables, and an app's theme restyles all of them.
   The colours of block categories are the exception, since they are core's ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).
4. The defaults take no colour from what surrounds an element: they are fixed values for each mode, and blockr.ui measures nothing and mixes no colour of the page into another.
5. In dark mode, the default of `popover` is lighter than that of `card` by at least 1.10:1, so that a menu that opens from a block's card stands out from it, as today's pair, `#1e242e` over `#161b23`, does at 1.109:1.
6. A frontend's tests tell, for each mode, which variables of blockr.ui's theme the frontend leaves at blockr.ui's defaults, so that a frontend keeps a default only by choice.

## Today

On `js-state`, core's runtime stylesheet, which loads on every page, holds the values of core's theme, which moves to blockr.ui ([srcts/runtime/index.css#L86-L180](https://github.com/BristolMyersSquibb/blockr.core/blob/e59b17104009684c9d15fb56c0f38ad53d523fa7/srcts/runtime/index.css#L86-L180), [UI kit and design system for the client](Rewrite-1.7#what-blockrui-holds)).
Those values are the basic frontend's look: the page is the browser's `Canvas`, a card is `bg-subtle`, 5% of the text over the page, and a menu or a dialog is `bg-raised`, the page's colour mixed with 10% of the text in dark mode.
The basic frontend has no stylesheet of its own.
Core's UIs also draw 32 colours of Tailwind's palette under core's prefix, in 8 files, most of them with a variant for dark mode, as a popover's `bc:text-gray-900` and `bc:dark:text-gray-100` in place of `text-default` ([srcts/overlays/popover.tsx#L20](https://github.com/BristolMyersSquibb/blockr.core/blob/e59b17104009684c9d15fb56c0f38ad53d523fa7/srcts/overlays/popover.tsx#L20)), and the tints of a card's messages, `bc:bg-red-500/10`, `bc:bg-amber-500/10` and `bc:bg-blue-500/10`, in place of `bg-danger`, `bg-warning` and `bg-accent-subtle` ([srcts/card/footer.tsx#L211-L225](https://github.com/BristolMyersSquibb/blockr.core/blob/e59b17104009684c9d15fb56c0f38ad53d523fa7/srcts/card/footer.tsx#L211-L225)).

The dock draws its panels and cards from copies of blockr.ui's tokens, such as `--blockr-dock-bg-surface: var(--blockr-color-bg-surface, #ffffff)`, and sets none of core's variables ([srcts/modules/dock/index.css#L88-L186](https://github.com/BristolMyersSquibb/blockr.dock/blob/5d9a4764709d0e3a391117855c0434cf06034bfb/srcts/modules/dock/index.css#L88-L186)).
So core's menus, select lists, dialogs and fields inside the dock wear the basic frontend's colours.
In dark mode they show as neutral grey panels over the dock's blue-grey cards, as [blockr.core#789](https://github.com/BristolMyersSquibb/blockr.core/issues/789) measured.

A first fix, [blockr.core#795](https://github.com/BristolMyersSquibb/blockr.core/pull/795), closed unmerged, gave core's defaults blockr.ui's values, which fitted the dock but turned the basic frontend's menus blue-grey over its neutral grey cards.
It then derived core's colours from what surrounds an element: a border mixed the text's colour, and a raised surface lightened the colour that core measured behind what opened it.
That worked around the misplaced values rather than moving them.

The tokens of today's blockr.ui hold the look that the dock wears, such as a surface of `#161b23` and a raised background of `#1e242e` in dark mode ([inst/assets/css/blockr-tokens-dark.css#L40-L42](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens-dark.css#L40-L42)).

## Proposal

### What the theme names

A theme is the values of a set of variables, and blockr.ui's theme is the set through which any frontend gives the page the look it likes, and an app's theme gives the whole page the app's: blockr.ui's components, core's UIs, the frontend's own parts and the UIs of blocks and plugins all draw with it.
The set is as big as that needs and as small as it can be, so it holds the colours, fonts, sizes of text, radii, shadows and spacing that a frontend may want its own, and leaves the rest of how components look to blockr.ui.
Each is a variable that Tailwind CSS 4 keeps its theme in, under the prefix `bk`, as `--bk-color-popover` and `--bk-spacing`, which every package's classes read through `@theme inline`, as core's `bc:bg-popover` and `bc:px-2` do ([Building on blockr.ui](Rewrite-1.7.4#prefixes)).
The stylesheet of blockr.ui declares the variables and gives each a default for both modes, its documentation says what each is for, and it exports their list ([Building on blockr.ui](Rewrite-1.7.4#the-themes-list)).
A frontend sets the variables whose values it wants its own, and keeps blockr.ui's defaults for the rest ([The defaults](#the-defaults)), and an app's theme sets those whose values the app wants its own, over the frontend's ([An app's theme](Rewrite-1.1.17)).

#### Colours

The colours take the names that shadcn/ui gives their jobs, under the prefix `bk`, so that the set gets the thought that went into one that many projects draw with, and its names are those that authors of UIs on Tailwind know ([theming.mdx#L62-L84](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/content/docs/%28root%29/theming.mdx?plain=1#L62-L84)).
React Aria's components draw with them already in JollyUI, whose button reads `bg-primary`, `text-primary-foreground`, `border-input` and `ring-ring` ([button.tsx#L19-L33](https://github.com/jolbol1/jolly-ui/blob/e2272fbc1acceef0f59c0e166467962ac5b16a71/src/registry/new-york/ui/button.tsx#L19-L33)).
Today's blockr.ui leads each name with its property, as `--blockr-color-text-muted`, after GitHub's Primer and Shopify's Polaris, and calls its brand colour `accent`, since its body text was `text-primary` ([naming.md#L36-L41](https://github.com/BristolMyersSquibb/blockr.ui/blob/caf3f835146ff6cb916aef775cf283876c58b8a9/dev/design-system/naming.md#L36-L41), [#L174-L176](https://github.com/BristolMyersSquibb/blockr.ui/blob/caf3f835146ff6cb916aef775cf283876c58b8a9/dev/design-system/naming.md#L174-L176)).
Under shadcn/ui's names the body text is `foreground`, so the brand colour is `primary`, and `accent` is the fill of a hover.
A UI reads the colour whose use it shares:

| Variable | What reads it |
|---|---|
| `--bk-color-background`, `--bk-color-foreground` | The page, which the frontend draws behind its panels and cards, as the dock does behind dockview's panels, and the text of every UI, its overlays included |
| `--bk-color-card`, `--bk-color-card-foreground` | A card or a node that a plugin draws on the page or in a panel, such as the DAG's nodes, the dock's cards and the basic frontend's cards, and its text. The card is opaque, since a node covers the links below it |
| `--bk-color-popover`, `--bk-color-popover-foreground` | Every overlay, such as a menu, a select's list, a popover, a dialog, a sheet, a tooltip or a toast, and a slider's thumb, and its text. The popover is opaque, since an overlay covers the page |
| `--bk-color-primary`, `--bk-color-primary-foreground` | The brand colour: what is picked or checked, such as a checked checkbox or a picked day, the primary button, a link, the check of a picked option and the edge of what is selected or current, and the text and icons on it, while its tints mark a message's banner, pill and toast |
| `--bk-color-secondary`, `--bk-color-secondary-foreground` | A filled control of lower emphasis, such as a secondary button, and its text |
| `--bk-color-muted`, `--bk-color-muted-foreground` | A quiet fill inside a surface, such as a tag or a block of code, and secondary text, such as a hint, a placeholder, a count or a block's summary |
| `--bk-color-accent`, `--bk-color-accent-foreground` | A row or a button that is hovered, pressed or focused from the keyboard, and its text |
| `--bk-color-destructive` | An error and what removes: the text and the mark of an error, the edge of an invalid field, the row of a menu that removes and the destructive button, while its tints mark an error's banner, pill and toast |
| `--bk-color-warning` | A warning: its text and its mark, while its tints mark its banner, pill and toast |
| `--bk-color-success` | The mark of a success, such as the status dot of a block that is `ready` ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)) |
| `--bk-color-border` | Outlines and dividers: the edge of a card or an overlay, the rules of a table, a menu's divider and a slider's track |
| `--bk-color-input` | The edge of a field, such as a text, number, search or token field, a select, a combo box, a date field or picker, or a colour field, and the outline of a checkbox, a radio button, a switch or a drop zone |
| `--bk-color-ring` | The focus ring |

An error, a warning and a success each have a colour, as the building blocks of every page that tells the user how things stand: `destructive`, which shadcn/ui names, and `warning` and `success`, which the theme adds beside it, while a message takes the tints of `primary`.
The page draws all three: a block raises warnings as well as errors, which its card tints apart, and the status dot draws `waiting` and `invalid` in the colour of a warning and `ready` in that of a success ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).
The set of shadcn/ui stops at `destructive` only because its own components draw no warning or success: its alert comes in `default` and `destructive` alone, and its toasts mark a success or a warning with an icon, in the popover's colours ([alert.tsx#L8-L16](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/registry/new-york-v4/ui/alert.tsx#L8-L16), [sonner.tsx#L21-L31](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/registry/new-york-v4/ui/sonner.tsx#L21-L31)).
So the theme adds the two as shadcn/ui's documentation adds a colour, under `:root` and for dark mode, through `@theme inline`, which takes a warning as its example ([theming.mdx#L118-L138](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/content/docs/%28root%29/theming.mdx?plain=1#L118-L138)).
Each is one colour without a `-foreground`, as shadcn/ui's own `destructive` is, since nothing draws text on either, so that the three colours of a state work alike.
The theme names no `danger` beside `destructive`, since `destructive` marks an error as well as what removes, as shadcn/ui's form draws an error's message in `text-destructive` ([form.tsx#L150](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/registry/new-york-v4/ui/form.tsx#L150)).
A second name for that job would have every theme set it twice, and the two could drift apart.
Each of `destructive`, `warning` and `success` does every job of its kind, its text, its mark and its edge, and the tints of its banner and toast come from it through the opacity modifier, as `bg-warning/10`, where today's blockr.ui names a fill, a text and a border for each.
The set leaves out shadcn/ui's colours of charts, since the colours of data come from blockr.theme's palettes or the board's scale map, and those of its sidebar, since a frontend's sidebar draws with the colours above.

A field's edge stands out more than an outline or a divider does, since it alone marks a field, and the outline of a checkbox, a radio button, a switch or a drop zone alone marks one that is unchecked, off or empty.
So `input` is stronger than `border`.
Its default is Tailwind's gray-400, and gray-600 in dark mode, about 2.3:1 to 2.6:1 against what it sits on.
That lies between the soft border of today's blockr.ui, about 1.2:1, and the 3:1 that [WCAG 2.2's success criterion 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) asks of what marks a control, at which a full frame looked too heavy.

The theme names a colour for the page, `background`, so that an app's theme reaches the page under every frontend, which draws it behind its panels and cards ([The frontend's own parts](#the-frontends-own-parts)).
A plugin's UI leaves its own background transparent, so that it shows the page or the panel that the frontend puts it in.
The theme names no fill for a field, since the fields that move from core's React SDK have none.
The hover, `accent`, has a name of its own, apart from `muted`, since the two differ once their values are solid colours, as blockr.ui's defaults are: the subtle fill of today's blockr.ui, `#f9fafb`, differs from a white menu by 1.05:1, which nobody sees, while its hover, `#f3f4f6`, reaches 1.10:1.

Two things draw in black and white of their own, since each must stand out on any colour: the backdrop behind a modal, black at 40%, which dims whatever page lies below it, and the rings of a colour field's thumbs and swatches, which show on any colour that the user picks.

The theme holds no other colour, since Tailwind's palette, whose colours follow neither a theme nor the mode, is no part of it ([UI kit and design system for the client](Rewrite-1.7#designed-against-tailwind)).
So every UI that draws with classes built by blockr.ui's preset, blockr.ui's components, core's UIs and those of plugins and blocks, takes its colours from the variables above.
The build preset fails a build whose code names a colour of Tailwind's palette, under any prefix ([Building on blockr.ui](Rewrite-1.7.4#the-build-preset)).
A UI that needs a shade between two variables derives it from them in its own stylesheet, as `color-mix(in oklab, var(--bk-color-primary) 15%, var(--bk-color-card))`, or tints one with Tailwind's opacity modifier, as `bc:bg-primary/20`, and both follow the theme and the mode.
A colour that must stay fixed it writes on purpose, as `bc:bg-[#0072b2]`, and the colours of data, such as a chart's series, come from blockr.theme's palettes or the board's scale map rather than from the theme.
Where several packages need a colour that no variable gives, the theme takes it in a later version of blockr.ui, with defaults ([Which defaults a frontend keeps](#which-defaults-a-frontend-keeps)), so that the set grows by what its users show they need, as it grows by `warning` and `success` beside shadcn/ui's.

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
The build preset defines the classes of shadows anew, so that they read these variables ([Building on blockr.ui](Rewrite-1.7.4#the-build-preset)).

### Where the frontend sets the values

The frontend sets the values in the stylesheet beside its module, which core loads with the module and waits for, so that the values are on the page before the frontend draws ([UI modules in JS](Rewrite-1.1.7#packaging)):

1. The stylesheet sets each variable whose value it gives under `:root[data-bk-mode="light"]`, on the page's root element, with its value in light mode.
2. It sets each of them again under `:root[data-bk-mode="dark"]`, with its value in dark mode, which is the same value where the two modes share one.
3. Every element inherits the values from `:root`, so that an overlay takes them wherever it sits, React Aria's portal at the end of the page's body included ([UI modules in JS](Rewrite-1.1.7#react)).

For two of the variables, a frontend's stylesheet would hold:

```css
:root[data-bk-mode="light"] {
  --bk-color-popover: #fafafa;
  --bk-spacing: 0.25rem;
}

:root[data-bk-mode="dark"] {
  --bk-color-popover: #262626;
  --bk-spacing: 0.25rem;
}
```

Only the frontend's stylesheet and an app's theme set variables of blockr.ui's theme, and nothing else of a package's styles `:root`, beside blockr.ui's own stylesheet, which sets there its defaults and the browser's `color-scheme` for each mode.
A frontend sets them on `:root` alone and under those two selectors alone, since the rules of an app's theme win over them by specificity, a value set on an element below `:root` would win there over the app's by inheritance ([The rules that R writes](Rewrite-1.1.17#the-rules-that-r-writes)), and a value on `:root` that names no mode would paint before core sets the mode.
The stylesheet of blockr.ui sets its defaults inside a cascade layer, and the frontend's sets its values outside one, so that the frontend's win whichever stylesheet loads first, while the rules of an app's theme win over both.
The values outlive the opening of another board, since the page keeps the stylesheets that it loaded and never switches to another frontend ([Drawing the board](Rewrite-1.1.8#opening-a-board)).
Today the dock sets its own variables on its own elements, and on the block's menu through that menu's class, so that an overlay without that class, such as a select's list in a block's UI, gets none of them, while a value on `:root` reaches every overlay.

### The frontend's own parts

A frontend draws its own parts with blockr.ui's theme too, such as the dock's cards, its navbar and the frame that dockview draws around its panels, so that an app's theme restyles them with every other UI ([An app's theme](Rewrite-1.1.17)).
So the frontend's stylesheet takes every colour, face, size, radius and shadow of those parts from a variable of the theme, and holds no colour of its own outside the values that it sets.
Where a part needs a value that the theme does not name, such as a grey between two of its own or the larger radius of the dock's panels, the frontend takes the variable whose job comes closest, or derives the value from variables of the theme in its own stylesheet, which an app's theme then reaches only through the values it derives from.

The dock defines 26 colours for itself today ([srcts/modules/dock/index.css#L93-L185](https://github.com/BristolMyersSquibb/blockr.dock/blob/5d9a4764709d0e3a391117855c0434cf06034bfb/srcts/modules/dock/index.css#L93-L185)).
Eighteen of them do jobs that the theme names, and its selected fill is a tint of `primary`.
It uses each of the other seven once to three times: a secondary and a disabled text, a stronger accent text, a field's fill, a strong border, a subtle accent border and the colour of its logo.
So the dock may draw two greys of text where it draws four today.
Only the colour of the page, behind dockview's panels, is a colour of its own rather than a step of another, so the theme names it, `background` ([Colours](#colours)).
The dock gives dockview's variables their values from the theme as well, as it gives them blockr.ui's tokens today ([#L596-L651](https://github.com/BristolMyersSquibb/blockr.dock/blob/5d9a4764709d0e3a391117855c0434cf06034bfb/srcts/modules/dock/index.css#L596-L651)).

### Light mode and dark mode

A theme has two modes, light mode and dark mode, and gives each variable that it sets a value for both, whether it is blockr.ui's defaults, a frontend's values or an app's theme.
Core's board option `dark_mode` switches the page between the two, through the attribute `data-bk-mode` on the page's root, as the user picks one or as the user's system prefers ([Building on blockr.ui](Rewrite-1.7.4#prefixes), [Board options and blockr options](Rewrite-1.1.13#where-the-two-meet)).
So no theme is light or dark alone.
In VS Code and JupyterLab a colour theme is one or the other, and the user picks one theme among many, since a theme is a plugin of its own there.
Here a theme comes with the page's one frontend, or with the app, so it holds both modes, and `dark_mode` stays the only switch.
A theme with one mode would also clash with what switches beside it: blockr.ui's defaults differ by mode, and the browser draws its scrollbars and form controls in the mode that core switches the page to.
A frontend sets each of its values under the attribute of its mode, so that no value of its light mode, such as a white menu, shows in its dark mode, and no value of either shows before core sets the mode.

Core sets the mode only as the board opens, once it has read `dark_mode`, so the page draws before it knows the mode, with core's loading note alone.
A page could paint the wrong mode first, as a saved board or a blockr option may fix the mode that the user's system does not prefer.
So until core sets the mode, the page's root holds no `data-bk-mode`, and blockr.ui's stylesheet draws the page in neutral greys, which suit either mode:

1. The page draws with `background` in Tailwind's gray-500, `#6b7280`, midway in lightness between a white page and a near-black one, and with `foreground` and `muted-foreground` in its gray-50, `#f9fafb`, which reads on it at 4.6:1.
2. Core opens the board, reads `dark_mode`, and sets `data-bk-mode` to `light` or `dark`.
3. The page draws in that mode.

The rules of light mode, a frontend's as an app's theme's, hold under `data-bk-mode="light"` alone, so that the greys hold until core sets the mode under every frontend ([Where the frontend sets the values](#where-the-frontend-sets-the-values), [The rules that R writes](Rewrite-1.1.17#the-rules-that-r-writes)).
So the page never paints the wrong mode, while every page starts grey.
A later version may have R write the mode on the page wherever R knows it, from the blockr option `dark_mode` or from the value that the opening board holds where no storage plugin can open another board first, so that those pages skip the greys.

### The defaults

The defaults are fixed values, one for light mode and one for dark mode, since blockr.ui takes no colour from what surrounds an element.
For the look, each colour's default is the value that the token of today's blockr.ui with the same job takes in that mode, as `popover` is `#ffffff` in light mode and `#1e242e` in dark mode, and `card` is `#ffffff` and `#161b23` ([inst/assets/css/blockr-tokens.css#L94-L98](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css#L94-L98), [blockr-tokens-dark.css#L40-L42](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens-dark.css#L40-L42)), so that the look roughly keeps today's ([UI kit and design system for the client](Rewrite-1.7#designed-against-tailwind)).
A token that mixes others, as today's hover in dark mode lays 6% of the text over what lies below ([blockr-tokens-dark.css#L46](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens-dark.css#L46)), gives `accent` the fixed value that its mix comes to, and a job that no token does takes a value of Tailwind's palette, as `input` and `secondary` do ([Colours](#colours)).
Where the set gives one colour to jobs that today's tokens split, the default is the value of the token that serves them all: `destructive` takes today's red border, `#dc2626`, which reads as text on white at 4.8:1, and `warning` takes today's amber text, `#b45309`, at 5.0:1, since the amber border, `#d97706`, reaches 3.2:1 alone ([blockr-tokens.css#L84-L85](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css#L84-L85), [#L119-L120](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css#L119-L120)).
The fonts, the sizes of text, the radii, the shadows and the spacing take Tailwind's own scales, from which blockr.ui's look starts, and today's values where that look departs from them, as today's blockr.ui draws its small text at `0.8125rem`, 13 pixels, where Tailwind's is 14 ([blockr-tokens.css#L152-L156](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css#L152-L156)).
So the page keeps the look of today's blockr.ui wherever its frontend sets nothing, and a variable that a later version of blockr.ui adds draws at once under every frontend that does not know it yet, as VS Code registers a default for each of its colours, for light and for dark themes, and takes the default wherever a theme leaves a colour out ([colorUtils.ts#L70-L75](https://github.com/microsoft/vscode/blob/817607ae52b88ef6021bb456e5995b6367e1b481/src/vs/platform/theme/common/colorUtils.ts#L70-L75), [#L222-L223](https://github.com/microsoft/vscode/blob/817607ae52b88ef6021bb456e5995b6367e1b481/src/vs/platform/theme/common/colorUtils.ts#L222-L223)).

Core's basic frontend and the dock keep every one of blockr.ui's defaults, since their look is blockr.ui's, so that the values of that look have one home.
The basic frontend draws its page in `background` and its cards in `card`, so it needs no stylesheet of its own, as today.
A block that `serve()` serves alone draws in blockr.ui's defaults, since its page has no frontend ([Defining a board in R](Rewrite-1.1.3#data-passed-to-serve)), or in the app's theme where the app gives one ([An app's theme](Rewrite-1.1.17)).

The layer of the overlays takes this default:

| Variable | What reads it | Default |
|---|---|---|
| `--bk-z-index-overlay` | Every overlay, which stacks above everything else on the page ([UI modules in JS](Rewrite-1.1.7#react)) | 1100 |

The theme holds no colour for a block's status or for a category of block classes, since both are core's.
Core maps each status onto a job of the theme, as `ready` onto `success`, and holds the colours of the categories itself, outside every theme ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).

### Which defaults a frontend keeps

Beside the theme's list, blockr.ui exports for tests a function that takes the text of a frontend's stylesheet and returns, for light mode and for dark mode, the variables of the theme that the stylesheet leaves at blockr.ui's defaults.
It returns as well each rule that sets a variable of the theme under another selector than the two that a frontend uses ([Where the frontend sets the values](#where-the-frontend-sets-the-values)).
A frontend's tests check that it returns exactly what the frontend keeps on purpose, and no such rule, as the tests of core's basic frontend and of the dock list every variable, since both keep every default.
So a default that a frontend keeps is a choice that its tests write down, and a colour that it sets for light mode alone shows up in its list for dark mode.
When blockr.ui adds a variable, in a minor release ([Building on blockr.ui](Rewrite-1.7.4#the-themes-list)):

1. Every page draws the new variable in blockr.ui's default, so nothing breaks for users.
2. The next time a frontend's tests run against that blockr.ui, they fail and name the new variable.
3. The frontend's author sets the variable, or adds it to the defaults that the frontend keeps.

Nothing warns of a kept default while the page runs, since a deployed app would then warn on every page, for the defaults that a frontend keeps on purpose too.

## Open questions

None.

<details><summary>Notes for implementers</summary>

- The theme of blockr.ui drops Tailwind's palette with `--color-*: initial` and declares `--color-black` and `--color-white` again, for the backdrop and the colour field's rings, while `bg-transparent` and `bg-current` need no variable.
- The DAG and core's Edit board plugin take their colours from the theme already ([Drawing the DAG](Rewrite-1.3.2#its-look), [The Edit board plugin](Rewrite-1.1.15#its-look)), so an app's theme reaches them with no change but the names under `bk` and the move off Tailwind's palette.
- Core loads a frontend's stylesheet, and waits for it, before it opens the board, so a frontend's rules paint as soon as the mode they name is set, and not before.
- The CSS of shadcn/ui sets its variables without a prefix, as `--card`, and maps them through `@theme inline` onto `--color-card`, while blockr.ui's carry the prefix, as `--bk-color-card`, so a theme made for shadcn/ui maps onto blockr.ui's name by name ([Building on blockr.ui](Rewrite-1.7.4#prefixes)).

</details>
