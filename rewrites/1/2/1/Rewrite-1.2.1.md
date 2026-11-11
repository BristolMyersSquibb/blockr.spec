# The dock's state: views, layouts and card sections
Status: draft. Design for [Client-drawn dock](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock](Rewrite-1.2)): the dock plugin's state, which holds its views, each view's grid, which view is active and which sections of each block's card show.
It covers the commands that change that state, the `update` and the `migrate` of the dock plugin's class, the R functions that write the state for an app script, and how the client turns a grid into dockview's layout and back.
It builds on [Plugins](Rewrite-1.1.12#a-plugins-state) and [Board updates](Rewrite-1.1.2#plugins).
How boards saved today open is [Saved boards and app scripts across the switch](Rewrite-1.2.2)'s.

## What must hold

Conditions 1 and 2 of [Client-drawn dock](Rewrite-1.2#what-must-hold) rest on this page.

## Proposal

Not drafted yet.

## Open questions

- Whether a view keeps its members apart from its grid, as today, or the grid alone says which panels a view shows.
  Today a view's members decide which panels it shows, while its grid only arranges them, so a member that the grid omits gets a default place and a panel in the grid that is no longer a member is dropped ([R/dock-grid.R#L27-L32](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/dock-grid.R#L27-L32)).
  It blocks the views' properties.
