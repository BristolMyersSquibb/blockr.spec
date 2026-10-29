# Input elements for block UIs written in R
Status: draft. Design for [UI kit and design system for the client](Rewrite-1.7).

A design for a later project of [UI kit and design system for the client](Rewrite-1.7), still to be decided: the input elements a block class could compose its UI from in R, without writing TSX, which blockr.ui would build on core's module contract ([UI modules in JS](Rewrite-1.1.7)) once it ships ready-made components. Core ships none of it, and it shapes no issue yet. How a block class names its UI and its requests is the block classes proposal ([Block classes in R](Rewrite-1.1.5)).

## What must hold

1. A block class whose UI is a form of common inputs is written in R alone, as most block UIs are today.
2. Every element is bound to one state arg, or to an option's value, and an attribute that depends on the data is an R function whose arguments name what it reads.
3. The first set covers what core's built-in blocks and the block packages draw today.
4. R holds no reactive graph, since the client tracks what each attribute reads.

## Today

Core's twelve built-in blocks draw `selectInput()` four times, `textInput()` four times, and `numericInput()`, `bslib::input_switch()`, `checkboxGroupInput()`, `textAreaInput()`, `fileInput()`, `actionButton()` and `shinyFiles::shinyFilesButton()` once each, with no layout helpers. Three of them change an input from the data: the scatter plot's column choices, the merge's shared columns and the head block's maximum ([R/plot-scatter.R#L46-L52](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plot-scatter.R#L46-L52), [R/transform-merge.R#L67](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/transform-merge.R#L67), [R/transform-head.R#L45](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/transform-head.R#L45)). The block packages mostly draw blockr.ui's widgets from JS, as globals on `window.Blockr`: blockr.dplyr's fourteen blocks call its single and multiple select, checkbox, a text field that commits on Enter, the segmented control and the gear tray, and blockr.ggplot already builds its four blocks from a declarative field schema ([inst/js/gg-blocks.js#L85-L102](https://github.com/BristolMyersSquibb/blockr.ggplot/blob/289cb60f03d10caf13d143d06562f7eb663763d9/inst/js/gg-blocks.js#L85-L102)). In R, blockr.ui offers only the gear tray and its sections ([R/gear-tray.R#L52-L111](https://github.com/BristolMyersSquibb/blockr.ui/blob/9bd8312a3408bbcbabff2b57d1d3fd5681843c94/R/gear-tray.R#L52-L111)), and blockr.io draws Shiny inputs with a path picker of its own ([inst/assets/js/path-input.js#L111](https://github.com/BristolMyersSquibb/blockr.io/blob/acadbb26f1f7de9a649056d5bd44fbfe352ca477/inst/assets/js/path-input.js#L111)).

## Proposal

### Elements

An element is an R constructor named after the Shiny input it replaces, whose first argument names the state arg it binds:

```r
block_inputs(
  numeric_input("n", "Number of rows", min = 1L, max = \(data) nrow(data)),
  switch_input("direction", "Tail", on = "tail", off = "head")
)
```

The first set follows from today's call sites:

| Element | Replaces |
|---|---|
| `select_input()`, single or multiple, searchable | `selectInput()`, `checkboxGroupInput()`, `Blockr.Select` |
| `text_input()`, committing on Enter or blur | `textInput()`, `Blockr.textCommit` |
| `textarea_input()` | `textAreaInput()` |
| `numeric_input()` | `numericInput()` |
| `switch_input()`, `checkbox_input()` | `bslib::input_switch()`, `Blockr.checkbox` |
| `segmented_input()` | `Blockr.segmented` |
| `file_input()`, an upload through an action of its block class ([UI modules in JS](Rewrite-1.1.7#the-contract)) | `fileInput()` |

Layout comes from containers: `block_inputs()` stacks its elements, a row places them side by side, and a gear tray with sections holds what is used less, as blockr.ui's gear tray does. A package with an input of its own, such as blockr.io's path picker, ships it as a module that the host offers to others ([UI modules in JS](Rewrite-1.1.7)).

### Data-dependent attributes

An attribute is a value or an R function. A function's arguments name what it reads, an input slot or a state arg, and nothing else:

```r
select_input("x", "X axis", choices = \(data) colnames(data))
select_input("by", "Join by", multiple = TRUE, choices = \(x, y) intersect(colnames(x), colnames(y)))
select_input("column", "Column", choices = \(data, table) names(data[[table]]))
```

Each function is a request of its block class, registered under the element's id and attribute, such as `n.max`. The client asks R for it again when the revision of an input it names or the value of a state arg it names changes, caches the answers by those values, and tracks what each function reads with a JS signals library, so R just runs the function. An attribute that depends only on state, such as whether to show a field, goes through the same mechanism. A block class whose input slot and state arg share a name is rejected when `new_block_class()` defines it, since a function's argument would not say which it means ([Block classes in R](Rewrite-1.1.5)).

### Options

A board option's UI could be composed from the same elements, bound to the option's value instead of a state arg, as for `n_rows`:

```r
new_board_option("n_rows", 50L, ui = numeric_input("n_rows", "Preview rows", min = 1L))
```

### Inside modules

A module that draws most of its UI itself could still mount the elements, through `host.module()`, so a select looks and behaves the same in every block.

## Open questions

- Which containers the first set has besides rows and gear trays, such as tabs or collapsible sections.
- Whether a state-only attribute, such as showing a field, should be expressible without a round trip to R.
