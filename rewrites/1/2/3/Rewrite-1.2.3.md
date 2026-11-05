# Registering extensions with the dock
Status: draft. Design for [Client-drawn dock and extensions](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock and extensions](Rewrite-1.2)): how an extension registers with the dock from its package's startup module, and which extensions a board has.
It covers the state an extension keeps in the dock board's `extensions`, with the commands that change it, the hook that keeps it consistent with the board and the way it migrates, the board options and requests an extension brings, the API majors it declares, and how it is tested.
It builds on [Front-ends and extension points](Rewrite-1.1.8#extensions) and [Board updates](Rewrite-1.1.2#board-classes-and-attributes).
Where an extension draws is [The dock's contribution points](Rewrite-1.2.4)'s and [The dock's navbar](Rewrite-1.2.5)'s, and what the dock offers it besides is [The dock's services](Rewrite-1.2.6)'s.

## What must hold

Condition 3 of [Client-drawn dock and extensions](Rewrite-1.2#what-must-hold) rests on this page, with [The dock's contribution points](Rewrite-1.2.4), [The dock's navbar](Rewrite-1.2.5) and [The dock's services](Rewrite-1.2.6).

## Proposal

Not drafted yet.

## Open questions

- Which extensions a board has: those whose state its `extensions` holds, as a script passes them to `new_dock_board()` today, which lets one board hold two of a class under different keys, or every extension that a loaded package registers.
  It blocks the extension API.
- How an extension's state migrates, since it lives in the dock board's `extensions`, while the dock board class's `migrate` gets every property beside core's and a block class's state migrates by its own version ([Board updates](Rewrite-1.1.2#board-classes-and-attributes)).
  It blocks opening boards whose extensions' state has changed shape.
