# Roadmap
Revised on 2026-10-29.

This page says when the parts of [State in JS](Rewrite-1) are specced and implemented, when the block packages port to block classes, and what comes after the switch. The rewrite's pages hold its design and this page only its schedule, so a date that moves here changes no page there.

## State in JS

In its spec week a part settles with its design pages, and its spec and issues are opened. In its implementation week the issues are fixed on the `js-state` branches. Each part is specced after the parts it builds on. Weeks are ISO weeks.

| Weeks | From | Work | Page |
|---|---|---|---|
| 44 | 2026-10-26 | Spec blockr.core | [Client-owned board state](Rewrite-1.1) |
| 45 | 2026-11-02 | Implement blockr.core, and add the TypeScript gates to blockr.ci's workflows | [Client-owned board state](Rewrite-1.1) |
| 46 | 2026-11-09 | Spec blockr.dock and blockr.ui | [Client-drawn dock and extensions](Rewrite-1.2), [UI kit and design system for the client](Rewrite-1.7) |
| 47 | 2026-11-16 | Implement blockr.ui, its React first since the dock is built on it, and blockr.dock | [Client-drawn dock and extensions](Rewrite-1.2), [UI kit and design system for the client](Rewrite-1.7) |
| 48–49 | 2026-11-23 | Spec and implement blockr.assistant | [Assistant as a client extension](Rewrite-1.4) |
| 50–51 | 2026-12-07 | Spec and implement blockr.session | [Session management as a client extension](Rewrite-1.6) |
| 52–53 | 2026-12-21 | Holidays | |
| 1 | 2027-01-04 | Spec and implement blockr.dag | [Client-drawn DAG extension](Rewrite-1.3) |
| 2 | 2027-01-11 | Spec and implement blockr.code | [Code export as a client extension](Rewrite-1.5) |
| 3 | 2027-01-18 | Rebuild blockr.md's document as a dock extension | None yet |
| 4 | 2027-01-25 | Run the blockr.uat board on `js-state` | [blockr.uat](https://github.com/BristolMyersSquibb/blockr.uat) |
| 5–8 | 2027-02-01 | The switch: merge `js-state` into main repo by repo, take out the pins and release the 0.2 versions | [Migration](Rewrite-1#migration) |

Every part is implemented by 2027-01-15 and the blockr.uat board runs on `js-state` by 2027-01-29, with weeks 52 and 53 off. The plan holds no slack, so each week that slips moves both dates by a week. The switch waits for CRAN as well as for the code: eight of the packages are on CRAN and blockr.ui is not, while blockr.dock, blockr.dplyr, blockr.ggplot, blockr.dag and blockr.session import it on main already, so blockr.ui's first submission comes before their releases.

## Block packages

The block packages port to block classes beside the parts from week 46, once core's block classes, outputs and UI modules are implemented and its guide for porting a block from `new_block()` is written, and their UIs written in React from week 47, once blockr.ui ships React. Each ports after the packages it builds on. The first are blockr.dplyr, blockr.io and blockr.ggplot, by week 4, since the `blockr` package imports them and the blockr.uat board installs it. The rest follow for the CEDX board, which lives in blockr.sandbox ([blockr#493](https://github.com/orgs/BristolMyersSquibb/discussions/493)) and needs all of them but blockr.ggplot. Beside them, blockr.ops, which reads and writes boards, follows the new format ([Serialization of the client-owned board](Rewrite-1.1.4)).

| Package | Builds on, besides blockr.core | Exported block constructors |
|---|---|---|
| blockr.dplyr | blockr.ui | 14 |
| blockr.io | | 3 |
| blockr.ggplot | blockr.ui | 5 |
| blockr.theme | | 0, board-level theming through a board option |
| blockr.ai | | 0, AI controls for blocks |
| blockr.stats | blockr.ui | 6 |
| blockr.viz | blockr.ui | 8 |
| blockr.extra | blockr.dplyr, blockr.ui | 10 |
| blockr.dm | blockr.ai, blockr.dplyr, blockr.io, blockr.ui | 17 |
| blockr.pharma | blockr.dm, blockr.dplyr, blockr.theme, blockr.ui, blockr.viz | 7 |

## After State in JS

None of this is specced or scheduled yet. Each becomes a rewrite or a spec of its own after the switch.

### Leaving Shiny

Shiny stays host and transport through State in JS, since on Connect it gives each session its own process, and one bridge module carries the protocol ([State in JS](Rewrite-1#proposal)). Leaving Shiny replaces that module with a transport of our own, and needs another way to give each session its own process.

### Python

Look into a Python process in R's place: one that evaluates what the client sends over the wire protocol ([Wire protocol between the client and R](Rewrite-1.1.9)), starts an app as `serve()` does in R, and runs blocks written in Python. What a block class looks like in Python comes first, and with it whether one board can mix R and Python blocks, which moves results between processes.

### A server of our own

A server-side component of our own would sit between the client and the processes that evaluate, shaped as a proxy in Go or as a scheduler in Node, which is still open. Above all it would let a board use several R and Python processes, and backends other than a process, such as a database, where data locality decides where a block is evaluated, so that data moves as little as possible. It would also open the way to collaboration, whose relay State in JS keeps open ([State in JS](Rewrite-1#proposal)), to an MCP endpoint, and to what the client cannot do alone, such as holding the provider credentials of the assistant's proxy ([Assistant as a client extension](Rewrite-1.4)) and making the calls on an app's own Connect key ([Session management as a client extension](Rewrite-1.6)).

<details><summary>Sources</summary>

The block constructors are the `export(new_*_block)` lines in each package's `NAMESPACE` on main on 2026-10-29, at blockr.dplyr `68e1b54`, blockr.io `acadbb2`, blockr.ggplot `289cb60`, blockr.dm `8b37981`, blockr.viz `332ce57`, blockr.stats `268259d`, blockr.extra `c99bce6` and blockr.pharma `22c6c03`, and what a package builds on is its `Imports`. On CRAN on 2026-10-29: blockr 0.1.0, blockr.core 0.1.3, blockr.dag 0.1.5, blockr.dock 0.1.2, blockr.dplyr 0.1.0, blockr.ggplot 0.1.0, blockr.io 0.1.0 and blockr.session 0.1.0. The reusable `ci.yaml` of blockr.ci runs no Node step.

</details>
