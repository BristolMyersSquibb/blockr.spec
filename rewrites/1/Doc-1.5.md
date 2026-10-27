# Code export as a client extension
Status: draft. Part of [State in JS](Doc-1).

This part covers blockr.code, whose code export becomes a dock extension with generation as a request to R. It builds on [Client-drawn dock and extensions](Doc-1.2) and on core's requests ([Client-owned board state](Doc-1.1)).

## Problem

The code export shows a board's code in a modal: `generate_flat_code_server()` has every block server constructed, waits until each block's state is ready and no block has an error, and joins the `expr` reactives of the block servers into a script with `export_wrapped_code()` ([`plugin.R#L44-L82`](https://github.com/BristolMyersSquibb/blockr.code/blob/72b20d6911496e4edc9ee64db758e70ebf3f50ca/R/plugin.R#L44-L82)). The issue [blockr.code#8](https://github.com/BristolMyersSquibb/blockr.code/issues/8) moves it from a core plugin to a dock extension on today's stack. With the board a client document ([Client-owned board state](Doc-1.1)), there are no block servers to read expressions from.

## What must hold

1. The code extension is a dock extension ([Client-drawn dock and extensions](Doc-1.2)) that shows the code of the board in the document.
2. R generates it from the document's recipes with each block's `expr_fn`, so the code shown is the code that runs ([Client-owned board state](Doc-1.1)).
3. A block that cannot give code yet, with an unset arg, an error or inputs still unevaluated, is named in the answer instead of the script, as `code_export_state()` reports `"blocked"` today.

## Proposal

- Generation is a request that blockr.code registers ([blockr.core#393](https://github.com/BristolMyersSquibb/blockr.core/issues/393)): it carries the recipes, R calls each block's `expr_fn`, and `export_wrapped_code()` joins the expressions, formatted and highlighted in R as today.
- The request claims the blocks it needs evaluated ([blockr.core#395](https://github.com/BristolMyersSquibb/blockr.core/issues/395)), since a block whose `expr_fn` reads its inputs has code only once they exist.

## Open questions

- How the request knows which blocks need their inputs: a flag in the registry export ([blockr.core#396](https://github.com/BristolMyersSquibb/blockr.core/issues/396)), or by claiming every block upstream of the code it shows.

## Work

- Rebuild the code extension on the dock's client API, with generation as a request to R, in blockr.code

<details><summary>Notes for implementers</summary>

The generator in `R/code.R` stays, `export_wrapped_code(expressions, board)` ([`code.R#L1-L16`](https://github.com/BristolMyersSquibb/blockr.code/blob/72b20d6911496e4edc9ee64db758e70ebf3f50ca/R/code.R#L1-L16)), with styler, xml2 and downlit for formatting and highlighting. The "Evaluate blocks" button of today's modal, which sends `evaluate` for every block, becomes the claim.

</details>
