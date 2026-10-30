# Later additions
Revised on 2026-10-30.

This page lists additions to blockr that are small or medium, go beyond what [State in JS](Rewrite-1) needs for parity, and are not ready for a spec. Each item says what the addition would let us remove, what it would cost, and what would settle whether to build it, and an item leaves the list once it becomes a spec or an issue, or once it is dropped, with the reason. The large projects after State in JS are on the [roadmap](Roadmap#after-state-in-js).

## Control links

A control link would be a second kind of edge on the board, beside links, saying that a selection on one block's output sets another block's state, such as a click on "SEX = F" in a chart setting a cohort filter's condition. Today blockr.viz carries such a claim outside the DAG, from block code over a channel of its own, to a target that a block's setting names or that it finds by class ([R/ctrl-send.R#L1-L27](https://github.com/BristolMyersSquibb/blockr.viz/blob/332ce573ffafa86f5a41dc400b0f85e6800128f7/R/ctrl-send.R#L1-L27)). In State in JS a renderer reports a selection through `emit()` and an extension turns it into a command, keeping which block's selections go where in a field of its own ([UI modules in JS](Rewrite-1.1.7#the-contract), [Client-drawn dock and extensions](Rewrite-1.2#open-questions)).

What it would remove: an extension's own record of where each block's selections go, and drill-down's need for an extension at all, since core would route a selection to the state it sets. Every such dependency would show on the board and in the DAG, as a link does. A control link could point upstream, as a drill into a cohort filter does, since it carries an edit rather than data, so it closes no cycle, and it would add nothing to evaluation, so lazy evaluation never drags the sending block's upstream into its target, which is why blockr.viz kept such claims off links.

What it would cost: a new object in the board ([Board objects](Rewrite-1.1.1)), with commands to add, change and remove it and checks in the store ([Board updates](Rewrite-1.1.2)), a place in the saved file ([Serialization](Rewrite-1.1.4)), a second kind of edge for the DAG to draw and edit and for front-ends to offer ([Client-drawn dock and extensions](Rewrite-1.2), [Client-drawn DAG extension](Rewrite-1.3)), and a rule for how a target turns a selection into its state, which for blockr.dm's drill filter needs the dm to say which table a column belongs to.

What would settle it: whether, once drill-down runs as an extension in State in JS, other packages route selections between blocks too, or blockr.viz's drill stays the only one.
