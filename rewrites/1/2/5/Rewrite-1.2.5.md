# The dock's navbar
Status: draft. Design for [Client-drawn dock and extensions](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock and extensions](Rewrite-1.2)): the bar across the top of the dock.
It covers the bar's items and their order, what fills the bar and what gives way when it is narrow, the dock's default items, and how extensions and apps add, drop and reorder items, which [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494) settled in R.
It builds on [Registering extensions with the dock](Rewrite-1.2.3) and [The dock's contribution points](Rewrite-1.2.4).

## What must hold

Condition 3 of [Client-drawn dock and extensions](Rewrite-1.2#what-must-hold) rests on this page for navbar items, with [Registering extensions with the dock](Rewrite-1.2.3), [The dock's contribution points](Rewrite-1.2.4) and [The dock's services](Rewrite-1.2.6).

## Proposal

Not drafted yet.

## Open questions

- How the navbar's items, their order and what gives way on a narrow bar become client API, which [blockr.dock#529](https://github.com/BristolMyersSquibb/blockr.dock/issues/529) settled in R for [blockr#494](https://github.com/orgs/BristolMyersSquibb/discussions/494), and whether an app script still adds, drops and reorders items, as `custom_navbar()` lets it today, or only packages do, from their startup modules.
