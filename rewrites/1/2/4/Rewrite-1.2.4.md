# The dock's contribution points
Status: draft. Design for [Client-drawn dock and extensions](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock and extensions](Rewrite-1.2)): the places in the dock's UI where an extension contributes React components, which the dock uses for its own features too.
They are panels, sidebar sections, menus on the board, a block, a stack and the DAG's canvas, settings, and the block card.
It builds on [Registering extensions with the dock](Rewrite-1.2.3).
The navbar is [The dock's navbar](Rewrite-1.2.5)'s, and the card's own design is [Block cards in the dock](Rewrite-1.2.7)'s.

## What must hold

Condition 3 of [Client-drawn dock and extensions](Rewrite-1.2#what-must-hold) rests on this page, with [Registering extensions with the dock](Rewrite-1.2.3), [The dock's navbar](Rewrite-1.2.5) and [The dock's services](Rewrite-1.2.6).

## Proposal

Not drafted yet.

## Open questions

- Panel kinds: one per board, like the assistant's, or one per block, and whether commands can open panels.
- Whether the dock's block card takes contributions from extensions, a section in its body and actions in its header, each a component the dock renders per block with the block's id, to keep what today's `edit_block` callbacks and `ctrl` section let a package add to every block.
  Core needs nothing new for it: the component works through `CoreApi`, a plugin's request reads the block's result in R ([Plugins](Rewrite-1.1.12#a-plugins-requests)), and whether a section shows can live in the dock board's `visible`, by block id, which core carries without reading ([Locked boards and the properties of blocks](Rewrite-1.1.11#what-a-plugin-keeps-about-a-block)).
  It blocks nothing yet, since the assistant replaces the per-block chat that blockr.ai puts in the `ctrl` section today, and a package that needs such UI would settle it.
