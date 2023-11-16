
# What is a block?

![](https://t4730439.p.clickup-attachments.com/t4730439/75fd767a-fcbd-493b-bdd3-d6f0c91d9d47/image.png)

### S3-based object (Nicolas)

*   A block is a set of fields (user inputs) + instructions on how to produce a result given an input and the block state (values for block fields)
*   Using generic function OOP we can associate methods with a block, e.g.
    *   `generate_ui()/generate_server()`:
        *   instructions on how to render the UI of a given block
        *   a default can be provided which generates shiny input fields for the block fields
        *   the shiny dependency comes in only via these generics and is not part of the core block definition
    *   auxiliary methods (defaults will most likely suffice for any type of block, but let's stick to generics here this for extensibility purposes)
        *   `serialize_block()` create a JSON representation of the block (and its state)
        *   `serve_block()` create a standalone shiny app for testing/dev purposes
*   blocks can be created and manipulated programmatically (useful for testing and most likely for other things down the line: presets/templates?)
*   blocks keep track of their state; makes serialization easy as copy/pasting etc.

# What is a stack?

![](https://t4730439.p.clickup-attachments.com/t4730439/99c226c9-4c8a-47d5-bd41-3302f3528725/image.png)

*   Combine blocks
*   Pass data input from one block to another
*   Generate integrated UI and Server functionality for the stack

Open Questions (Nicolas)

*   does a stack manage cache (invalidation) or do we rely entirely on shiny for this (using reactivity)
*   which per-block UI components are provided by the stack? for me, currently all "card" related things

# UI-Abstraction

## Problem

It should be possible for Junior R-Programmers or intermediate R-Users to write blocks. For simple blocks, we would like to keep the requirements for shiny knowledge as minimal as possible.

## Potential Solutions

### Specs Layer

Add another layer to give automated layers for standard data types (numeric, factor, Date, …).

Examples, see block3

**Pros:** No knowledge of shiny needed

**Cons**: Specs layer needs to be learned as well. Contrary to standard shiny, there is no external help available (coworkers, Stack Overflow, ChatGPT). Also, the knowledge cannot be re-used outside the project, which may reduce the willingness to learn it.

### Shiny UI

Write the UI as standard Shiny code. Have a standard server logic that makes all input IDs available in a list.

**Pros**

*   See cons of 'Specs Layer'
*   Helper functions may still give us some benefits of 'Specs Layer'

### Standardized Field Types (Nicolas)

*   the core "block" package comes with a set of "field types" like "string", "range", "enum/factor", etc. and when sticking to this, a default UI can be generated easily
*   the standard UI can of course be overridden by providing a (class-specific) implementation of the "generate UI" generic

# Code Generation

## Problem

Blocks should contain their functional logic, and should be able to provide a way to generate reproducible code from it.

## Nicolas:

*   For experimentation purposes, stick to base R functionality for quoting and manipulating R language objects; might have to resort to rlang infrastructure at some point; maybe keep base R stuff as a fallback due to its simplicity?
*   Example "filter block":

```r
quote(
  dplyr::filter(.(column) == .(value))
)
```

*   base R alternative `substitute()` is less "safe" as there is no control over what is substituted (symbols are matched by name only)

```r
substitute(foo <- foo, list(foo = "bar"))
#> "bar" <- "bar"
```

*   why not strings (this is wip)
    ```r
    string <- glue::glue(
      filter({column} == {value})
    )
    eval(parse(text = strings))
    ```
    *   security: "injection" type attacks
    *   quoting issues: e.g. non-syntactic column names have to be handled; maybe also issues with literals?
    *   `eval(parse(...))` often times simply is a short-cut (lack of "NSE" proficiency)
    *   no "source-time" syntax checks (applies to quoted expressions too probably)
    *   performance (TBD whether relevant)
    *   not a super argument in itself, but anyway: base R provides utilities for "computing on the language", rlang then was developed to increase these capabilities; surely there are good reasons for this (even if I cannot list them right now)
    *   (as above:) the arrow/dplyr backend experimented with strings at some point but over time moved away from this approach

## General remarks

*   trade-off: readability vs familiarity for block implementers vs robustness
*   ordering (Nicolas): robustness > familiarity > readability; maybe look at a function-based approach one more time?
*   "name-spacing" issues in non-function contexts

# APIs

## Inter-block communication

*   handled by the stack class
*   currently pretty straight forward: pass results from one block to the next
*   becomes more involved when actions in one block should trigger things in another that are not mediated via the intermediate result (we might not need this)
*   we could start to think about formalizing types of changes
    *   i.e. "schema" changes are different from "data" changes and require other "update" actions in subsequent blocks
    *   for Nicolas this is handled by a `update_fields()` generic (this area needs more work in order to not have to duplicate logic)

## Intra-bock communication

*   the approach of Christoph takes the "freestyle" route here: per-block server function that calls functions like `shiny::update*Input()`
*   Nicolas tried to formalize this a bit (in turn providing a default behavior) that can handle block type agnostic "field updates"; needs more thought though

### Misc

*   look into how to model dependencies between fields and (data) input
    *   current handling of data -> fields dependencies too ad-hoc
    *   could prove limiting if we cannot capture inter-field deps
    *   otoh maybe a fiel type for cols already gets us quite far?
*   how do we do „default“ values? not at all? an abstraction that helps out with both init and updates?
*   introduction of ptypes for input maybe output too?) data
*   recursion in field definitions?

# UI for creating "expressions"

We're currently constrained by the "input fields" offered by shiny. Medium term, it will be hard to benefit from the expressiveness of R/dplyr/ggplot with such inputs only. This is building on what John showed towards the end of our last meeting with using more complex JS input "forms" instead of building this in pure shiny.

## The competition

I had a quick look at Tableau, Spotfire and PowerBI. A common theme is that they offer composing "Excel-type" expressions embedded in a "mini IDE".![](https://t4730439.p.clickup-attachments.com/t4730439/470a4c62-a7a0-4ab9-ad8c-f68e9b5d9827/Screenshot%202023-10-05%20at%2010.56.00.png)

## Possible building blocks

*   [blockly](https://developers.google.com/blockly/): not pretty, very "visual" and expressive[![](https://t4730439.p.clickup-attachments.com/t4730439/54fe278e-3be9-4f02-a0b3-58b8bb7436f4/Screenshot%202023-10-05%20at%2016.57.04.png)](https://querybuilder.js.org)
*   [QueryBuilder](https://querybuilder.js.org): limited to "querying" i.e. could be helpful for a filter block, not much else (close to John suggestion from last week I believe)[![](https://t4730439.p.clickup-attachments.com/t4730439/be91fff7-8f1e-49fc-af8a-6ce4cb487a3f/Screenshot%202023-10-05%20at%2016.57.49.png)](https://exp.js.org/demo.html)
*   [ExpressionBuilder](https://exp.js.org/demo.html): more "text-focused" with help in the form of a drop down; lacking visual component of blockly[![](https://t4730439.p.clickup-attachments.com/t4730439/38558c37-efc1-47f4-9af5-2e4fea47a62f/Screenshot%202023-10-05%20at%2016.59.22.png)](https://ui-predicate.fgribreau.com/ui-predicate-vue/1.0.0/getting-started/)
*   [ui-predicate](https://ui-predicate.fgribreau.com/ui-predicate-vue/1.0.0/getting-started/): similar limitations to QueryBuilder, less pretty out of the box?![](https://t4730439.p.clickup-attachments.com/t4730439/a7414401-aa9f-4cd0-a5c3-89bddb9d3e93/Screenshot%202023-10-05%20at%2017.15.47.png)

For pursuing any such direction, I'd could use some help to get started. In order to do general purpose data-wrangling, we probably need to introduce UI input components beyond what shin offers. Are there things like this out there already?