# Saved boards and app scripts across the switch
Status: draft. Design for [Client-drawn dock](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock](Rewrite-1.2)): how what users made with today's blockr.dock crosses the switch.
It covers the boards that today's blockr.dock saved, which the conversion outside core turns into JSON boards for the `migrate` of the dock plugin's class in the client, and the app scripts that call its constructors.
It builds on [Serialization](Rewrite-1.1.4) and on [The dock's state: views, layouts and card sections](Rewrite-1.2.1), into which the migration writes.
Each of today's extensions becomes a plugin whose state the conversion takes from the extension's, as [Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today) has it.

## What must hold

Condition 5 of [Client-drawn dock](Rewrite-1.2#what-must-hold) rests on this page.

## Proposal

Not drafted yet.

## Open questions

- Whether `new_dock_stack()` stays, as a name for core's `new_stack()` that today's app scripts call, now that core keeps a stack's colour ([Board objects](Rewrite-1.1.1#stacks)), or goes, with a migration note.
- Whether `new_edit_board_extension()` stays, as a name for core's `new_edit_board_plugin()` that six of blockr.dock's examples, its README, its layouts vignette and twelve of its test files call, or goes, with a migration note ([The Edit board plugin](Rewrite-1.1.15#boards-and-app-scripts-from-today)).
