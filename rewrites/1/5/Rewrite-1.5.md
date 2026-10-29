# Code export as a client extension
Status: draft. Part of [State in JS](Rewrite-1).

This part covers blockr.code, whose code export becomes a dock extension with generation as a request to R. It builds on [Client-drawn dock and extensions](Rewrite-1.2) and on core's requests ([Client-owned board state](Rewrite-1.1)).

## Problem

The code export shows a board's code in a modal: `generate_flat_code_server()` has every block server constructed, waits until each block's state is ready and no block has an error, and joins the `expr` reactives of the block servers into a script with `export_wrapped_code()` ([`plugin.R#L44-L82`](https://github.com/BristolMyersSquibb/blockr.code/blob/72b20d6911496e4edc9ee64db758e70ebf3f50ca/R/plugin.R#L44-L82)). The issue [blockr.code#8](https://github.com/BristolMyersSquibb/blockr.code/issues/8) moves it from a core plugin to a dock extension on today's stack. With the board held by the client ([Client-owned board state](Rewrite-1.1)), there are no block servers to read expressions from.

## What must hold

1. The code extension is a dock extension ([Client-drawn dock and extensions](Rewrite-1.2)) that shows the code of the board.
2. R generates it from the board's recipes with each block class's `expr`, so the code shown is the code that runs ([Client-owned board state](Rewrite-1.1)).
3. A block that cannot give code yet, with an unset arg or an error, is named in the answer instead of the script, as `code_export_state()` reports `"blocked"` today.

## Proposal

- Generation is a request that blockr.code registers ([blockr.core#393](https://github.com/BristolMyersSquibb/blockr.core/issues/393)): it carries the recipes, R builds each block's expression from its class's `expr`, and `export_wrapped_code()` joins the expressions, formatted and highlighted in R as today.
- The request has the blocks it needs evaluated first, in a one-off evaluation ([Evaluation in the client](Rewrite-1.1.10#demand)), since only an evaluation tells whether a stale block's state still runs, while building the expression itself needs no data, as a class's `expr` builds it from the state alone ([Block classes in R](Rewrite-1.1.5#evaluation)).

## Open questions

None.

## Work

- Rebuild the code extension on the dock's client API, with generation as a request to R, in blockr.code

<details><summary>Notes for implementers</summary>

The generator in `R/code.R` stays, `export_wrapped_code(expressions, board)` ([`code.R#L1-L16`](https://github.com/BristolMyersSquibb/blockr.code/blob/72b20d6911496e4edc9ee64db758e70ebf3f50ca/R/code.R#L1-L16)), with styler, xml2 and downlit for formatting and highlighting. The "Evaluate blocks" button of today's modal, which sends `evaluate` for every block, becomes the claim.

</details>
