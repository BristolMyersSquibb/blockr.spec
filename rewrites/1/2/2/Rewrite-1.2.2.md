# Saved boards and app scripts across the switch
Status: draft. Design for [Client-drawn dock and extensions](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock and extensions](Rewrite-1.2)): how what users made with today's blockr.dock crosses the switch.
It covers the boards that today's blockr.dock saved, which the conversion outside core turns into JSON boards for the dock board class's `migrate` in the client, and the app scripts that call its constructors.
It builds on [Serialization](Rewrite-1.1.4) and on the properties of [The dock board](Rewrite-1.2.1), into which the migration writes.
How an extension's state migrates, inside the dock board's `extensions`, is [Registering extensions with the dock](Rewrite-1.2.3)'s.

## What must hold

Condition 5 of [Client-drawn dock and extensions](Rewrite-1.2#what-must-hold) rests on this page.

## Proposal

Not drafted yet.

## Open questions

- Whether `new_dock_stack()` stays, as a name for core's `new_stack()` that today's app scripts call, now that core keeps a stack's colour ([Board objects](Rewrite-1.1.1#stacks)), or goes, with a migration note.
- Whether `new_edit_board_extension()` stays, as a name for core's `new_edit_board_plugin()` that six of blockr.dock's examples, its README, its layouts vignette and twelve of its test files call, or goes, with a migration note ([The Edit board plugin](Rewrite-1.1.15#boards-and-app-scripts-from-today)).
