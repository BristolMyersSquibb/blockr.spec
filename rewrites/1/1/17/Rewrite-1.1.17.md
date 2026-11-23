# An app's theme: `new_blockr_theme()`, the argument `theme` of `serve()` and the rules that R writes
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how an app gives the page a theme of its own, which `new_blockr_theme()` makes in R and `serve()` takes, and how R writes the theme into the page, so that its values win over the frontend's and over blockr.ui's defaults from the moment core sets the page's mode.
Which variables a theme sets, what each is for, their defaults, how a frontend sets values of its own and which defaults a frontend keeps belong to [The theme's variables](Rewrite-1.7.2), and how R puts blockr.ui's stylesheet on every page to [Building on blockr.ui](Rewrite-1.7.4#the-stylesheet-on-the-page).
How `serve()` takes its arguments belongs to [Defining a board in R](Rewrite-1.1.3#the-serve-generic), and how a blockr option is set to [Board options and blockr options](Rewrite-1.1.13#blockr-options).

## What must hold

1. An app restyles the whole page with a theme of its own, the frontend's own parts included, by setting variables of blockr.ui's theme alone, and a value that the app's theme sets wins over the frontend's and over blockr.ui's default, whichever stylesheet loads first.
2. The page draws in the app's theme from the first paint after core sets the page's mode, and in blockr.ui's neutral greys before that, core's loading note included.
3. Each value of an app's theme holds in its own mode alone, so that a theme with values for light mode alone leaves dark mode to the frontend.
4. A name that blockr.ui's theme lacks stops the app as it starts, naming it.
5. A deployment sets one theme for all of its apps, and an app's script sets another where it wants its own.

## Today

An app restyles blockr.ui's tokens today with blockr.theme, whose `use_theme()` returns a `<style>` that sets them on `:root`, one value for each whatever the mode, and that the app puts into its UI after blockr's stylesheets ([R/theme.R#L283-L357](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/R/theme.R#L283-L357), [#L597-L611](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/R/theme.R#L597-L611)).
The tokens of blockr.ui's accent refer to its palette, so a theme shifts the whole accent by setting two values, `blue-600` and `color-primary` ([#L43-L48](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/R/theme.R#L43-L48)).

## Proposal

### What an app's theme sets

An app may give a theme of its own, whose values win over the frontend's and over blockr.ui's defaults, so that a company's design restyles the whole page, the frontend's own parts included ([The frontend's own parts](Rewrite-1.7.2#the-frontends-own-parts)).
It sets variables of blockr.ui's theme, as a frontend does, so that one theme fits every frontend, and it sets those whose values the app wants its own and leaves the rest to the frontend.
So blockr.theme makes such a theme from its values, where today it sets blockr.ui's tokens ([Today](#today)).

The theme names jobs rather than the steps of a palette ([The theme's variables](Rewrite-1.7.2#colours)), and a frontend sets each job's value itself, so an app's theme sets every job whose look it changes.
A company's brand colour is thus `primary`, with `primary-foreground` for the text on it, `primary-text` for links and messages, and `ring` for the focus ring, each in both modes, where blockr.theme sets two of blockr.ui's tokens today, and no other job of a theme is derived from it behind its author's back.

A theme that starts from a few colours, such as a company's brand colour, gets the values of the rest as it is made, from whatever makes it, such as blockr.theme, which computes colours for its palettes of plots already ([R/palettes.R#L26-L40](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/R/palettes.R#L26-L40)), so that the theme holds every value that the page draws, where its author sees and checks it.
Nothing derives them as the page draws, since a derived colour can fall below a readable contrast for a colour that nobody tried, unseen, and a value that the frontend sets for a variable would win over one derived from the theme's colour.
That is how shadcn/ui's command line writes a theme's values from a base colour as it makes the theme, while it derives nothing but its radii as the page draws ([theming.mdx#L93-L150](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/content/docs/%28root%29/theming.mdx?plain=1#L93-L150)).

A theme sets values, never parts, so a company's logo, an image, is the frontend's to take, through an argument or a blockr option of its own, where it draws one.
A theme holds for the whole page, since its rules set `:root`, from which every overlay inherits, while blockr.theme can scope its tokens to a part of the page today, so that two boards on one page look apart.
React Aria's `UNSAFE_PortalProvider`, which draws overlays into an element of one's choosing, leaves room for a theme of each board later.
What reads no variable of blockr.ui's theme keeps its colours under any theme, such as a block's UI that writes its colours as literals ([Colours](Rewrite-1.7.2#colours)).
An app sets the colours of block categories apart from its theme, through a blockr option of core's, `category_colors` ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).

### Where an app gives it

An app gives its theme to `serve()`, whose argument `theme` defaults to the blockr option `theme`, so that a deployment sets one theme for all of its apps, as `options(blockr.theme = ...)` in its R profile does, and an app's script passes another where it wants its own ([Defining a board in R](Rewrite-1.1.3#the-serve-generic), [Board options and blockr options](Rewrite-1.1.13#blockr-options)).
Where neither gives one, the blockr option falls back on `NULL`, no theme, so the page draws with its frontend as it is.
The blockr option holds what `new_blockr_theme()` returns, an R object, so only an R option sets it, as only one sets `renderers`, and a deployment sets it in its R profile rather than in an environment variable ([A theme in R](#a-theme-in-r)).
Each method of `serve()` takes the argument, for a board, a path or a block, so that a block that `serve()` serves alone draws in the app's theme too.

#### A theme in R

A theme is values for variables of blockr.ui's theme, with the files of any fonts that it brings, which core's `new_blockr_theme()` makes in R:

```r
new_blockr_theme(
  light = list("--bk-color-primary" = "#be2bbb", "--bk-font-sans" = "Inter, sans-serif"),
  dark = list("--bk-color-primary" = "#d66bd3", "--bk-font-sans" = "Inter, sans-serif"),
  fonts = list(
    list(family = "Inter", file = system.file("fonts", "inter-latin.woff2", package = "blockr.theme"), weight = "100 900")
  )
)
```

Its `light` and `dark` hold the values of each mode, each under its variable's full name, as [The theme's variables](Rewrite-1.7.2) and the browser's tools show it, and each value holds in its own mode alone.
A name that blockr.ui's theme lacks stops the app as it starts, since `new_blockr_theme()` refuses it, naming it, so that a misspelt name, or one that a later blockr.ui drops, never does nothing in silence.
The function checks each name against the list of the theme's variables that blockr.ui exports ([Building on blockr.ui](Rewrite-1.7.4#the-themes-list)).
A value is any CSS value, which R writes into the page as it is.
Its `fonts` hold a face for each file of a font, under the names that blockr.theme's `bundled_font()` gives them today: `family`, `file`, `weight` and `style` ([R/theme.R#L214-L234](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/R/theme.R#L214-L234)).
Here `file` is the path of the font's file, where `bundled_font()` takes the name of a file in a package's `inst/fonts`.
Its `weight` and `style` default to those of CSS's `@font-face`.
It takes nothing but values and fonts, so a theme sets values alone, as condition 1 has it.
Each method of `serve()` refuses a `theme` that is neither what `new_blockr_theme()` returns nor `NULL`, naming what it got, such as a string that an environment variable gave the blockr option.

So blockr.theme makes an app's theme with `new_blockr_theme()`, from its chrome under the names of blockr.ui's theme, its font's family and its bundled font, and an app passes that theme to `serve()` or sets it as the blockr option `theme`.
Its palettes for plots, its scale map and its templates stay its own, since they style data and documents rather than the page, and none of them passes through `serve()`.
Its scale map is a board option with a Shiny editor today, and the new stack runs no such editor.
How the scale map works in the new stack is for blockr.viz, which reads it, to work out.
So what `new_blockr_theme()` returns holds what R writes into the page and nothing else, and core is the only code that reads it.
A theme for the packages that draw data, such as the colours of a chart's series, is a later project.
It would serve every such package alike, with ggplot2's themes as a starting point for what it holds, or it is not built, since neither core nor blockr.ui holds settings for a single package.

### The rules that R writes

R writes the theme into the page that it serves, in the page's head, beside blockr.ui's stylesheet, so that the theme holds from the first paint after core sets the page's mode, with no request between, and every board that the app opens draws in it, since the page keeps it ([Building on blockr.ui](Rewrite-1.7.4#the-stylesheet-on-the-page)).
The theme never changes while the page runs, so nothing else carries it.
For the theme above, R writes two rules:

```css
:root:root[data-bk-mode="light"] {
  --bk-color-primary: #be2bbb;
  --bk-font-sans: Inter, sans-serif;
}

:root:root[data-bk-mode="dark"] {
  --bk-color-primary: #d66bd3;
  --bk-font-sans: Inter, sans-serif;
}
```

The rule of light mode holds in light mode and the rule of dark mode in dark mode, so each value holds in its own mode alone.
Before core first sets the page's mode, neither holds, so that the page draws in the neutral greys of blockr.ui's stylesheet until core knows the mode ([The theme's variables](Rewrite-1.7.2#light-mode-and-dark-mode)).
As `dark_mode` switches the attribute `data-bk-mode`, the browser applies the rule of the new mode, with nothing for core to do ([Board options and blockr options](Rewrite-1.1.13#where-the-two-meet)).
Each rule names `:root` twice beside the mode's attribute, which gives it a specificity of (0,3,0), while a frontend sets its values under `:root[data-bk-mode="light"]` and `:root[data-bk-mode="dark"]`, each of (0,2,0) ([Where the frontend sets the values](Rewrite-1.7.2#where-the-frontend-sets-the-values)).
So the app's values win over the frontend's whichever stylesheet loads first, although the frontend's loads with its module, after the page's head ([UI modules in JS](Rewrite-1.1.7#packaging)), and over blockr.ui's defaults, which sit in a cascade layer, over which every rule outside one wins.
The rule of light mode names the mode that it holds in, since a rule of `:root:root` alone would hold in dark mode too, where it would win over blockr.ui's defaults of dark mode, and before core sets the mode, where it would paint the app's light values over the greys.

For each of the theme's fonts, R writes a face with `@font-face`, at the URL at which R serves its file, and with `font-display: swap`, as blockr.theme writes its faces today ([R/theme.R#L240-L261](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/R/theme.R#L240-L261)).
R also names each file in the page's head as a preload link, as it names the files that the page imports as it starts ([State in JS](Rewrite-1#conventions)).
So the browser fetches the file as the page loads, while core waits for R's reply, and the face is there once core sets the page's mode.
Where the file is still on its way, the text draws in the next face of the stack rather than not at all.

## Open questions

None.

<details><summary>Notes for implementers</summary>

- The function `new_blockr_theme()` returns an object of class `blockr_theme`, and core exports `is_blockr_theme()` beside it, as it exports `is_plugin()` beside `new_plugin()`.
  The class is not `theme`, which ggplot2's themes carry, as ggplot2 4.0.3's `class(theme_grey())` begins with it, so that neither package's methods dispatch on the other's objects.
  The object that blockr.theme makes carries the class `blockr_theme` today, with the functions `blockr_theme()` and `is_blockr_theme()`, so blockr.theme gives them other names.
- The function `new_blockr_theme()` reads the theme's list from the installed blockr.ui in R, so blockr.ui exports the list in R as well as in JS.
- R writes each value as it is, so `new_blockr_theme()` refuses a value that holds `}` or `<`, which would end the rule or the element that holds it.
  The check goes no further, so a value that is malformed in another way, such as one with an unclosed parenthesis, can break the theme, which is then its author's to fix.
- A frontend that set a variable of the theme on an element below `:root` would win over the app's theme there by inheritance, whatever the selectors, which is why a frontend sets its values on `:root` alone ([Where the frontend sets the values](Rewrite-1.7.2#where-the-frontend-sets-the-values)).
- The blockr option `theme` is the R option `blockr.theme`, which bears the name of the package blockr.theme.
  So blockr.theme names its own R options otherwise, as it names `blockr.theme.current` today.

</details>
