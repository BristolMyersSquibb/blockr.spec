# Overview

### Goal of this document

To structure the discussion around blockly, block3, etc.

### Experiments

Please ask package authors if you lack access.

#### John's original draft

R6-based blocks

[https://github.com/devOpifex/blockly](https://github.com/devOpifex/blockly/blob/master/README.md)

#### Christoph's experiments

List-based blocks. Introduces 'stacks'. Stacks are working and can be demoed.

[https://github.com/cynkra/block3](https://github.com/cynkra/block3)

#### Nicolas's experiments

Distantly similar to Christoph's experiments, this sets up a more rigid S3 class structure. Introduces 'fields' that contain the user input state.

[https://github.com/nbenn/blockr](https://github.com/nbenn/blockr)

#### David's experiments

Similar to Christoph on the surface. Explores aspects of the user interface such as drag and drop containers, collapsible block. Explore an interface to let people extend/modify a block by their own server/ui functions. UI and server are tightly coupled in this concept.

[https://github.com/DivadNojnarg/abs](https://github.com/DivadNojnarg/abs)

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
