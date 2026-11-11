# Places the dock offers plugins
Status: draft. Design for [Client-drawn dock](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock](Rewrite-1.2)): the places where the dock puts plugins, which the dock uses for its own features too.
They are the panel in which the dock mounts each plugin's `ui` with `mountPlugin()`, and the places it offers besides through members of its own on core's `PluginClass`, as `dockNavbar` adds navbar items ([Plugins](Rewrite-1.1.12#plugin-classes)): menus on the board, a block and a stack, settings, and the block card.
It builds on [Plugins](Rewrite-1.1.12) and [Drawing the board](Rewrite-1.1.8#what-core-gives-plugins).
The navbar is [The dock's navbar](Rewrite-1.2.5)'s, and the card's own design is [Block cards in the dock](Rewrite-1.2.7)'s.

## What must hold

Condition 3 of [Client-drawn dock](Rewrite-1.2#what-must-hold) rests on this page, with [The dock's navbar](Rewrite-1.2.5).

## Proposal

Not drafted yet.

## Open questions

- Whether a plugin has more places on the screen than its one panel, such as a panel per block, while `blockr.dock-show_panel` opens a plugin's panel in the active view as it opens a block's ([The dock's state](Rewrite-1.2.1#commands)).
- Whether a plugin names the major of the dock's members it was built against, as a module names the major of core's JS API ([UI modules in JS](Rewrite-1.1.7#the-contract)), so that the dock skips the members of a plugin built against another major.
- Whether the dock's block card takes contributions from plugins, a section in its body and actions in its header, each a module the dock mounts per block with the block's id, through a member of the dock's on `PluginClass`, to keep what today's `edit_block` callbacks and `ctrl` section let a package add to every block.
  Core needs nothing new for it: the component works through `CoreApi`, a plugin's request reads the block's result in R ([Plugins](Rewrite-1.1.12#a-plugins-requests)), and whether a section shows can live in the dock's `visible`, by block id, which core carries without reading ([Locked boards and the properties of blocks](Rewrite-1.1.11#what-a-plugin-keeps-about-a-block)).
  It blocks nothing yet, since the assistant replaces the per-block chat that blockr.ai puts in the `ctrl` section today, and a package that needs such UI would settle it.
