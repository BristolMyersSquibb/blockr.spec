# The dock board: views and layouts
Status: draft. Design for [Client-drawn dock and extensions](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock and extensions](Rewrite-1.2)): the properties that the dock board adds beside core's, which are its views and each view's grid.
It covers the commands that change them, the `update` that keeps them consistent with the board, the R functions that write them for an app script, and how the client turns a grid into dockview's layout and back.
It builds on the board classes of [Board updates](Rewrite-1.1.2#board-classes-and-attributes).
How boards saved today open is [Saved boards and app scripts across the switch](Rewrite-1.2.2)'s, and the state that extensions keep in the dock board's `extensions` is [Registering extensions with the dock](Rewrite-1.2.3)'s.

## What must hold

Conditions 1 and 2 of [Client-drawn dock and extensions](Rewrite-1.2#what-must-hold) rest on this page.

## Proposal

Not drafted yet.

## Open questions

- Whether a view keeps its members apart from its grid, as today, or the grid alone says which panels a view shows.
  Today a view's members decide which panels it shows, while its grid only arranges them, so a member that the grid omits gets a default place and a panel in the grid that is no longer a member is dropped ([R/dock-grid.R#L27-L32](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L27-L32)).
  It blocks the views' properties.
