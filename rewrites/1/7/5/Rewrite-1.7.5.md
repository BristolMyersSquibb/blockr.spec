# An app's theme: `new_blockr_theme()`, the argument `theme` of `serve()` and the rules that R writes
Status: review. Design for [UI kit and design system for the client](Rewrite-1.7).

One of the designs for blockr.ui as the client's UI kit ([UI kit and design system for the client](Rewrite-1.7)): how an app gives the page a theme of its own, which blockr.ui's `new_blockr_theme()` makes in R and core's `serve()` takes, and how R writes the theme into the page.
It shapes the items of 1.7's Work list that export `new_blockr_theme()` from blockr.ui, make blockr.theme's theme with it, and have `serve()` take the theme and write it into the page ([UI kit and design system for the client](Rewrite-1.7#work)).
Which theme variables there are, what each is for, their defaults, how a frontend sets values of its own, which value wins on the page and which defaults a frontend keeps belong to [The theme variables](Rewrite-1.7.2), and how R puts blockr.ui's stylesheet on every page to [Building on blockr.ui](Rewrite-1.7.4#the-stylesheet-on-the-page).
How `serve()` takes its arguments belongs to [Defining a board in R](Rewrite-1.1.3#the-serve-generic), and how a blockr option is set to [Board options and blockr options](Rewrite-1.1.13#blockr-options).

## What must hold

1. An app restyles the whole page with a theme of its own, the frontend's own parts included, by setting theme variables alone, and a value that the app's theme sets wins over the frontend's and over blockr.ui's default, whichever stylesheet loads first.
   The colours of block categories are the exception, since core's blockr option `category_colors` sets them ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).
2. The page draws in the app's theme from the first paint, core's loading note included.
3. Each value of an app's theme holds in its own mode alone, so that a theme with values for light mode alone leaves dark mode to the frontend.
4. A name that is no theme variable stops the app as it starts, naming it.
5. An app's script sets the app's theme.
   A site-wide R profile can give one theme to every app that runs on its installation of R, and an app's script overrides it.
6. A package that makes themes, such as blockr.theme, needs blockr.ui alone to make one.

## Today

An app restyles blockr.ui's tokens today with blockr.theme, whose `use_theme()` returns a `<style>` that sets them on `:root` ([R/theme.R#L283-L357](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/R/theme.R#L283-L357), [#L597-L611](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/R/theme.R#L597-L611)).
Since `serve()` takes no theme, the app's script adds the `<style>` to the page by wrapping the dock's method of `blockr_app_ui()`, as blockr.theme's demo does ([dev/theme-demo.R#L51-L67](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/dev/theme-demo.R#L51-L67)).
There the `<style>` comes after blockr.ui's rule for dark mode, `[data-bs-theme="dark"]`, which has the same specificity, so each value that a theme sets holds in both modes.
Nothing checks a token's name, so a misspelt one does nothing ([#L304-L310](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/R/theme.R#L304-L310)).
The tokens of blockr.ui's accent refer to its palette, so a theme shifts the whole accent by setting two values, `blue-600` and `color-primary` ([#L43-L48](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/R/theme.R#L43-L48)).

A theme may set any of the 132 tokens that blockr.ui declares ([blockr-tokens.css](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/css/blockr-tokens.css)).
It reaches whatever reads them: blockr.ui's widgets, Bootstrap's elements through blockr.ui's theme stylesheet, and the stylesheets of the dock, the DAG and the block packages.
What a theme sets today goes as follows:

| What a theme sets today | Where it goes |
|---|---|
| The 33 steps of blockr.ui's palette, such as `blue-600`, which the colours by job refer to | Dropped, since an app's theme sets each job's colour itself ([What an app's theme sets](#what-an-apps-theme-sets)) |
| The 50 colours by job, such as `color-primary`, `color-primary-hover` and `color-bg-surface` | The 27 colours of the theme variables, such as `--bk-color-primary` and `--bk-color-card`, while a job's hover, subtle fill and subtle border, such as `color-primary-hover`, come from the job's colour in each component ([Colours](Rewrite-1.7.2#colours)) |
| The 9 colours of block categories | Core's blockr option `category_colors`, outside the theme ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)) |
| The sizes of text, the radii and the shadows, such as `font-size-xl`, `radius-md` and `shadow-dropdown` | Four sizes of text, from `--bk-text-xs` to `--bk-text-lg`, one radius from which every step derives, and three shadows ([Fonts, sizes, radii, shadows and spacing](Rewrite-1.7.2#fonts-sizes-radii-shadows-and-spacing)) |
| The focus ring | Its colour, `--bk-color-ring`, while its width and offset are the components' |
| The weights of the faces, the heights of controls, the block's mark, the transition and eight layers | The components', since no frontend needs its own, while the heights of controls follow the spacing and the size of their text, and every overlay stacks on `--bk-z-index-overlay` ([Fonts, sizes, radii, shadows and spacing](Rewrite-1.7.2#fonts-sizes-radii-shadows-and-spacing)) |
| The colour of the logo | The frontend's, which takes the logo through an argument or a blockr option of its own ([What an app's theme sets](#what-an-apps-theme-sets)) |
| The face, through `font_family`, and its file, through `webfont` | The theme variable `--bk-font-sans`, and the theme's `fonts` ([A theme in R](#a-theme-in-r)) |
| A selector that scopes the theme to a part of the page | Dropped, since a theme holds for the whole page ([What an app's theme sets](#what-an-apps-theme-sets)) |

The spacing, which sets the density of every UI, has no token today, and a theme sets it as `--bk-spacing`.

## Proposal

### What an app's theme sets

An app may give a theme of its own, whose values win over the frontend's and over blockr.ui's defaults, so that a company's design restyles the whole page, the frontend's own parts included ([The frontend's own parts](Rewrite-1.7.2#the-frontends-own-parts)).
It sets theme variables, as a frontend does, so that one theme fits every frontend, and it sets those whose values the app wants its own and leaves the rest to the frontend.
So blockr.theme makes such a theme from its values, where today it sets blockr.ui's tokens ([Today](#today)).

The theme variables name jobs rather than the steps of a palette ([The theme variables](Rewrite-1.7.2#colours)), and a frontend sets each job's value itself, so an app's theme sets every job whose look it changes.
A company's brand colour is thus `primary`, with `primary-foreground` for the text on it, `primary-text` for links and messages, and `ring` for the focus ring, each in both modes, where blockr.theme sets two of blockr.ui's tokens today, and no other job of a theme is derived from it behind its author's back.

A theme that starts from a few colours, such as a company's brand colour, gets the values of the rest as it is made, from whatever makes it, such as blockr.theme, which computes colours for its palettes of plots already ([R/palettes.R#L26-L40](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/R/palettes.R#L26-L40)), so that the theme holds every value that the page draws, where its author sees and checks it.
Nothing derives them as the page draws, since a derived colour can fall below a readable contrast for a colour that nobody tried, unseen, and a value that the frontend sets for a variable would win over one derived from the theme's colour.
That is how shadcn/ui's command line writes a theme's values from a base colour as it makes the theme, while it derives nothing but its radii as the page draws ([theming.mdx#L93-L150](https://github.com/shadcn-ui/ui/blob/bfa64ff4d1cb7317d2403ecb176df6826d4caffc/apps/v4/content/docs/%28root%29/theming.mdx?plain=1#L93-L150)).

A theme sets values, never parts, so a company's logo, an image, is the frontend's to take, through an argument or a blockr option of its own, where it draws one.
A theme holds for the whole page, since its rules set `:root`, from which every overlay inherits, while blockr.theme can scope its tokens to a part of the page today, so that two boards on one page look apart.
React Aria's `UNSAFE_PortalProvider`, which draws overlays into an element of one's choosing, leaves room for a theme of each board later.
What reads no theme variable keeps its colours under any theme, such as a block's UI that writes its colours as literals ([Colours](Rewrite-1.7.2#colours)).
An app sets the colours of block categories apart from its theme, through a blockr option of core's, `category_colors` ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).

### Where an app gives it

An app gives its theme to `serve()`, whose argument `theme` defaults to the blockr option `theme` ([Defining a board in R](Rewrite-1.1.3#the-serve-generic), [Board options and blockr options](Rewrite-1.1.13#blockr-options)).
An app's script sets the theme in either place: it passes the theme to `serve()`, or it sets the blockr option, as `options(blockr.theme = ...)` does.
The blockr option also lets a site-wide R profile, `Rprofile.site`, give one theme to every app that runs on its installation of R, and an app's script overrides it.
Where nothing sets the blockr option, it falls back on a theme with no values, as `new_blockr_theme()` makes with no arguments, so the page draws with its frontend's values and blockr.ui's defaults.
The blockr option holds what `new_blockr_theme()` returns, an R object, so only an R option sets it, as only one sets `renderers` ([A theme in R](#a-theme-in-r)).
Each method of `serve()` takes the argument, for a board, a path or a block, so that a block that `serve()` serves alone draws in the app's theme too.

#### A theme in R

A theme is values for theme variables, with the files of any fonts that it brings, which blockr.ui's `new_blockr_theme()` makes in R:

```r
new_blockr_theme(
  light = list("--bk-color-primary" = "#be2bbb", "--bk-font-sans" = "Inter, sans-serif"),
  dark = list("--bk-color-primary" = "#d66bd3", "--bk-font-sans" = "Inter, sans-serif"),
  fonts = list(
    list(family = "Inter", file = system.file("fonts", "inter-latin.woff2", package = "blockr.theme"), weight = "100 900")
  )
)
```

Its `light` and `dark` hold the values of each mode, each under its variable's full name, as [The theme variables](Rewrite-1.7.2) and the browser's tools show it, and each value holds in its own mode alone.
Each may hold any of the theme variables, which [The theme variables](Rewrite-1.7.2#which-theme-variables-blockrui-declares) lists in full: the colours by job, the two faces, the sizes of text, the radius, the shadows, the spacing and the layer of the overlays.
A value that holds in both modes, such as a face, goes into both lists.
A name that is no theme variable stops the app as it starts, since `new_blockr_theme()` refuses it, naming it, so that a misspelt name, or one that a later blockr.ui drops, never does nothing in silence.
The function checks each name against the list of theme variables, which `theme_variables()` returns ([Building on blockr.ui](Rewrite-1.7.4#the-list-of-theme-variables)).
A value is any CSS value, which R writes into the page as it is.
Its `fonts` hold a face for each file of a font, under the names that blockr.theme's `bundled_font()` gives them today: `family`, `file`, `weight` and `style` ([R/theme.R#L214-L234](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/R/theme.R#L214-L234)).
Here `file` is the path of the font's file, where `bundled_font()` takes the name of a file in a package's `inst/fonts`.
Its `weight` and `style` default to those of CSS's `@font-face`.
It takes nothing but values and fonts, so a theme sets values alone, as condition 1 has it.
Each method of `serve()` refuses a `theme` that is not what `new_blockr_theme()` returns, naming what it got, such as `NULL` or a string that an environment variable gave the blockr option.

So blockr.theme makes an app's theme with `new_blockr_theme()`, from its chrome under the names of the theme variables, its font's family and its bundled font, and an app passes that theme to `serve()` or sets it as the blockr option `theme`.
Its palettes for plots, its scale map and its templates stay its own, and so do the options that it sets for blockr.viz, such as the fills of a table's header ([R/theme.R#L359-L382](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/R/theme.R#L359-L382)).
They style data and documents rather than the page, and none of them passes through `serve()`.
Its scale map is a board option with a Shiny editor today, and the new stack runs no such editor.
How the scale map works in the new stack is for blockr.viz, which reads it, to work out.
So what `new_blockr_theme()` returns holds what R writes into the page and nothing else, and `serve()` is the only code that takes it.
The function is blockr.ui's, beside the variables that it sets and their list, so that a package that makes themes builds on blockr.ui alone (condition 6).
Core only takes the theme in `serve()` and writes it into the page.
A theme for the packages that draw data, such as the colours of a chart's series, is a later project.
It would serve every such package alike, with ggplot2's themes as a starting point for what it holds, or it is not built, since neither core nor blockr.ui holds settings for a single package.

### The rules that R writes

R writes the theme into the page that it serves, in the page's head, after blockr.ui's stylesheet, so that the theme holds from the first paint, with no request between, and every board that the app opens draws in it, since the page keeps it ([Building on blockr.ui](Rewrite-1.7.4#the-stylesheet-on-the-page)).
The theme never changes while the page runs, so nothing else carries it.
The rules come from blockr.ui's method of `format()` for the class `blockr_theme`, so that their selectors stay with those of blockr.ui's defaults, and core puts the text that it returns into the page's head.
For the theme above, it writes two rules:

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
As `dark_mode` switches the attribute `data-bk-mode`, the browser applies the rule of the new mode, with nothing for core to do ([Board options and blockr options](Rewrite-1.1.13#where-the-two-meet)).
Why each rule names `:root` twice and its mode, so that the app's values win over the frontend's and over blockr.ui's defaults, belongs to [The theme variables](Rewrite-1.7.2#where-the-values-are-set).

For each of the theme's fonts, core serves the file and writes a face with `@font-face`, at the URL at which it serves the file, and with `font-display: swap`, as blockr.theme writes its faces today ([R/theme.R#L240-L261](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/R/theme.R#L240-L261)).
R also names each file in the page's head as a preload link, as it names the files that the page imports as it starts ([State in JS](Rewrite-1#conventions)).
So the browser fetches the file as the page loads.
Where the file is still on its way, the text draws in the next face of the stack rather than not at all.

## Open questions

None.

<details><summary>Notes for implementers</summary>

- The function `new_blockr_theme()` returns an object of class `blockr_theme`, and blockr.ui exports `is_blockr_theme()` beside it, as core exports `is_plugin()` beside `new_plugin()`.
  Core's `serve()` tells a theme by `is_blockr_theme()`.
  The class is not `theme`, which ggplot2's themes carry, as ggplot2 4.0.3's `class(theme_grey())` begins with it, so that neither package's methods dispatch on the other's objects.
  The object that blockr.theme makes carries the class `blockr_theme` today, with the functions `blockr_theme()` and `is_blockr_theme()`, so blockr.theme gives them other names.
- The function `new_blockr_theme()` reads the list of theme variables through `theme_variables()`, which reads the file that blockr.ui's build writes from the list in TypeScript, so that the lists in R and in JS never disagree ([Building on blockr.ui](Rewrite-1.7.4#the-list-of-theme-variables)).
- R writes each value as it is, so `new_blockr_theme()` refuses a value that holds `}` or `<`, which would end the rule or the element that holds it.
  The check goes no further, so a value that is malformed in another way, such as one with an unclosed parenthesis, can break the theme, which is then its author's to fix.
- The function `blockr_option()` reads the blockr option `theme` from the R option `blockr.theme` or the environment variable `BLOCKR_THEME`.
  The R option bears the name of the package blockr.theme, so blockr.theme names its own R options otherwise, as it names `blockr.theme.current` today.
  The demo of blockr.theme picks a theme by `BLOCKR_THEME` today ([dev/theme-demo.R#L31](https://github.com/BristolMyersSquibb/blockr.theme/blob/6b7d00e89c53ef66d53d1ddf7c490e75c720c5f4/dev/theme-demo.R#L31)).
  So the demo reads another variable, since `blockr_option()` would return its string for the blockr option, which `serve()` refuses.
- For a theme with no values and no fonts, such as the blockr option's fallback, the method of `format()` returns an empty string, so the page of an app that sets no theme holds no rules of a theme.

</details>
