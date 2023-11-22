# Overview

### Goal of this document

To document developer discussions and features around blockr


### User Documentation

Is stored as vignette and rendered as a pkgdown website:

https://blockr-org.github.io/blockr/articles/developer-guide.html#adding-new-fields

### Definitions

*   Block: element with input/output ports (data/data, data/plot) with a specific task such as data selection, wrangling, visualization, …
*   Stack: a group of connected blocks.

### Other tools

*   tidyblocks (JS).
*   teal (R, Roche).

### Open questions

*   What makes our tool different from the others (teal, ...)? Aren't we reinventing the wheel?
*   How to generate code from a given block/stack?
*   What are the responsibilities of a block?
*   How to extend a block?
*   Same questions for the stack (blocks group)
*   Should all blocks be able to run standalone (without shiny)?
*   How do we connect 2 stacks together?
*   How do we include/connect an isolate block to a stack?
*   What is the easiest way for developers to develop custom blocks on top of the predefined ones (by us)? We will develop the concept but people will have very specific needs in terms of visualizations so we can't handle all situations. We must provide a flexible way for developers to add their own blocks.
