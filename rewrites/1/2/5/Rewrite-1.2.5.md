# The dock's navbar
Status: draft. Design for [Client-drawn dock](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock](Rewrite-1.2)): the bar across the top of the dock.
It covers the bar's items and their order, what fills the bar and what gives way when it is narrow, the dock's default items, the items that plugins add through the dock's member `dockNavbar` ([Plugins](Rewrite-1.1.12#plugin-classes)), as blockr.session adds its avatar, and how an app drops and reorders items, which [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) settled in R.
It builds on [Places the dock offers plugins](Rewrite-1.2.4).

## What must hold

Condition 3 of [Client-drawn dock](Rewrite-1.2#what-must-hold) rests on this page for navbar items, with [Places the dock offers plugins](Rewrite-1.2.4).

## Proposal

Not drafted yet.

## Open questions

- How the navbar's items, their order and what gives way on a narrow bar become `dockNavbar` and the dock's own items, which [blockr.dock#529](https://github.com/BristolMyersSquibb/blockr.dock/issues/529) settled in R for [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494), and whether an app script still drops and reorders items, as `custom_navbar()` lets it today, beside choosing the plugins that add them through `serve()` ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)).
