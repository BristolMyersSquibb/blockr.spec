# The dock's services
Status: dropped on 2026-11-11, because core gives every plugin notifications and focus through `CoreApi`, and storage is core's storage plugin ([Plugins for the client-owned board](Rewrite-1.1.12#what-a-frontend-offers-other-plugins)). Design for [Client-drawn dock](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock](Rewrite-1.2)): what the dock offers extensions besides places to draw in.
It covers notifications, and storage, which saves and opens boards, with a download and an upload by default, and which session management replaces ([Session management as a client extension](Rewrite-1.6)).
It also covers what the dock tells extensions about the screen, such as which panel has focus.
It builds on [Registering extensions with the dock](Rewrite-1.2.3).

## What must hold

Condition 3 of [Client-drawn dock](Rewrite-1.2#what-must-hold) rests on this page, with [Registering extensions with the dock](Rewrite-1.2.3), [Places the dock offers plugins](Rewrite-1.2.4) and [The dock's navbar](Rewrite-1.2.5).

## Proposal

Not drafted yet.

## Open questions

- Whether storage is among the dock's services, which depends on the open question of [Session management as a client extension](Rewrite-1.6#open-questions) on whether where boards are saved and opened becomes an interface of core.
