# Benchmarks of the new stack
Status: draft. Part of [State in JS](Rewrite-1).

This part covers benchmarks of the new stack, run once a proof of concept of it is ready.
It measures the speed of the client and R against today's stack, and how well the assistant does what users ask, so that two versions of its tools, or of how it frames its context, can be compared.
It builds on the parts it measures, and comes last among them.

## Problem

Nothing measures the new stack yet, though the case for it is speed: today the session's one R thread runs the board's state and every block's UI logic, and evaluation waits behind them ([State in JS](Rewrite-1#problem)).
On today's dock, a board of two blocks takes about 5.8 s and 13 busy periods to settle after it mounts ([blockr.dock#397](https://github.com/BristolMyersSquibb/blockr.dock/issues/397)).
On one R process, a classic Shiny app answered none of one user's updates within 120 s once four other sessions streamed, where the same updates sent as data took a few milliseconds ([blockr#493](https://github.com/BristolMyersSquibb/blockr/discussions/493#discussioncomment-18775537)).
The bar is a new stack that is faster than today's, rather than no slower, which takes measurements on boards of the size users run, such as the CEDX board.

The assistant is rebuilt too ([Assistant as a plugin](Rewrite-1.4)).
Today five clinical questions with answer keys computed from the data, which someone runs by hand on the CEDX board, are all that check its answers ([dev/cedx/assistant-intent](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/0e3e074647a257c1e828e49b92c81ea9d4669570/dev/cedx/assistant-intent/README.md)).
Nothing compares two versions of its tools, or of how it frames its context, by how well it does what users ask.

## What must hold

To agree once the proof of concept runs.

## Proposal

Not drafted yet.

## Open questions

- Which kinds of benchmark come first: the speed of first paint, a view switch and an edit's round trip, several sessions sharing one R process, or the assistant's work on a set of user requests.
- Which boards they run on: the CEDX board once its packages have ported, and boards of its size before then.
- Whether the benchmarks run in CI, so that a regression shows on the pull request that causes it, and on what machine.
- Which repo they live in.
- What the assistant's work is judged against: answer keys computed from the data, as the CEDX questions have, the board a user would have built, or a model's judgement.

## Work

Not drafted yet.
