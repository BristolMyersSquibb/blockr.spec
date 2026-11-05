# The Edit board extension in React
Status: draft. Design for [Client-drawn dock and extensions](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock and extensions](Rewrite-1.2)): the Edit board extension, ported to React as a dock extension.
Its panel adds and removes blocks, and edits the board's links and stacks in tables, on a board that mounts no DAG.
It is the first extension built on the extension API, so it tests [Registering extensions with the dock](Rewrite-1.2.3) and the panels of [The dock's contribution points](Rewrite-1.2.4) before the DAG, the assistant, code export and session management are rebuilt on them.

## What must hold

1. Every edit that today's Edit board extension makes can be made through it: adding a block of any class in the block registry under an id the user picks, removing blocks, and adding, changing and removing links and stacks.
2. It works on the board through core's JS API, and on the screen through the dock's extension API alone, with nothing of the dock's internals.

## Today

The extension is `new_edit_board_extension()`, named "Edit board", whose docs call it "a simplistic example of an extension" that is "mainly relevant for testing purposes" ([R/ext-edit.R#L1-L25](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/ext-edit.R#L1-L25)).
Its panel adds a block from the block registry under an id the user picks, which it sends at once, and removes the blocks the user selects ([#L27-L79](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/ext-edit.R#L27-L79)).
Two DT tables list the links, each with its source, target and input, and the stacks, each with its name, colour and blocks, with rows to add and remove ([#L81-L144](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/ext-edit.R#L81-L144)).
Their edits are staged, and "Apply changes" first applies them to a copy of the board to show what fails, then sends one update of the links and one of the stacks ([#L832-L942](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/ext-edit.R#L832-L942)).
Six of blockr.dock's examples, its README, its layouts vignette and many of its tests use it.

## Proposal

Not drafted yet.

## Open questions

- Whether the extension still stages its edits and applies them with one button, as today, or applies each edit as the user makes it, now that every edit is a command that undo takes back ([Board updates](Rewrite-1.1.2#undo)).
  Staging is discussed on [blockr.dock#199](https://github.com/BristolMyersSquibb/blockr.dock/issues/199).
