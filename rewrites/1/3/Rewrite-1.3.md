# Client-drawn DAG extension
Status: draft. Part of [State in JS](Rewrite-1).

This part covers blockr.dag, which becomes a dock extension drawn in the browser. It builds on [Client-drawn dock and extensions](Rewrite-1.2).

## Problem

The DAG is an htmlwidget driven from R: blockr.dag configures G6's behaviors and plugins through g6R ([`g6r.R#L284-L460`](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/g6r.R#L284-L460)) and keeps block positions and layout settings as state of a Shiny-module extension, `new_dag_extension(positions, layout)` ([`ext.R#L37-L45`](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/ext.R#L37-L45)). With the board held by the client ([Client-owned board state](Rewrite-1.1)) and the dock drawn in the browser ([Client-drawn dock and extensions](Rewrite-1.2)), there is no R board left for it to read or update.

## What must hold

1. The DAG draws the board's blocks, links and stacks in the browser, without g6R, and follows every delta.
2. Its gestures, such as drawing a link, moving a block into a stack or removing one, run core's commands, so undo and save cover them.
3. Positions and layout settings are the DAG's fields in the board ([Board updates](Rewrite-1.1.2#fields)), and boards saved today open with theirs.
4. What blockr.dag offers today carries over: zoom and pan, dragging blocks, click and brush selection, drawing a link by dragging, highlighting on hover, the context menu, the toolbar, tooltips, and stacks that collapse and expand.

## Proposal

- The DAG is a dock extension drawn with React Flow (`@xyflow/react`): it is React, so a node is a component in the dock's own tree that reads core's store through hooks; Langflow, Flowise and Dify are built on it; and it is 59 KB gzipped against 390 KB for G6.
- React Flow has no layout engine ("We have not implemented our own layouting solution yet"), and of the libraries it suggests only elkjs lays out groups reliably, since a dagre issue "prevents it from laying out sub-flows correctly" when a node inside a group links to one outside it ([layouting](https://reactflow.dev/learn/layouting/layouting)), which stack members do all the time. Stacks become group nodes with a `parentId` ([sub flows](https://reactflow.dev/learn/layouting/sub-flows)), and collapsing one is the extension's own code.
- A test decides the library before the rebuild: the stacks of a real board laid out with elkjs and collapsed in React Flow. If that fails, the DAG uses G6, whose combos "can contain nodes and sub-combos" and collapse on a double click ([combos](https://g6.antv.antgroup.com/en/manual/element/combo/overview)).

## Open questions

- When layout runs: on every change, or on request with the positions a user placed kept, as `positions` and `layout` coexist today.

## Work

- Lay out and collapse the stacks of a real board with React Flow and elkjs, to decide between React Flow and G6, in blockr.dag
- Rebuild the DAG as a client extension on the dock's extension API, in blockr.dag

<details><summary>Notes for implementers</summary>

Today's behaviors in g6R are `zoom_canvas()`, `drag_canvas()`, `drag_element()`, `click_select(multiple = TRUE)`, `brush_select()`, `collapse_expand()`, `hover_activate()` and `create_edge()`, and its plugins a context menu, a toolbar, tooltips and a background ([`g6r.R#L284-L460`](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/g6r.R#L284-L460)). Stacks are combos laid out with dagre, which does not know a combo's padding, so the spacing presets are tuned around it ([`layout.R#L66-L76`](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/layout.R#L66-L76)).

The dock coupling to replace is listed in [Client-drawn dock and extensions](Rewrite-1.2).

Versions on npm on 2026-10-24: `@xyflow/react` 12.12.0 (MIT), `elkjs` 0.12.0 (EPL-2.0 or GPL-3.0-or-later, so blockr.dag, GPL (>= 3), can bundle it under the GPL), `@antv/g6` 5.1.1 (MIT). Weekly downloads for 2026-10-16 to 22: `@xyflow/react` 9.0 million, `@antv/g6` 137,000. Gzipped sizes from bundlephobia: 59 KB and 390 KB.

</details>
