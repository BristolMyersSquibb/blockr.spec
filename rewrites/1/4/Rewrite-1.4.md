# Assistant as a client extension
Status: draft. Part of [State in JS](Rewrite-1).

This part covers blockr.assistant, whose agent loop moves to the browser as a dock extension. It builds on [Client-drawn dock and extensions](Rewrite-1.2) and on core's commands and scheduler ([Client-owned board state](Rewrite-1.1)).

## Problem

Today's assistant runs its agent loop in the session's R process through ellmer, with 40 tools (`ellmer::tool()` definitions at `fd58655`) that change a running Shiny board. Its mutation tools stage a delta ([`commit_pending()`](https://github.com/BristolMyersSquibb/blockr.assistant/blob/a429c3061348a354834eeb2a5c173f8ff27f7c0b/R/stage-pending.R#L88)), and its `commit` tool applies it through the board's `update()` ([`flush_pending()`](https://github.com/BristolMyersSquibb/blockr.assistant/blob/a429c3061348a354834eeb2a5c173f8ff27f7c0b/R/stage-pending.R#L682)) and waits for the touched blocks to re-evaluate, up to `assistant_commit_timeout_secs`, 30 s by default; a commit can also stop partway, with "the board may be partly updated" ([`tools-commit.R`](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/tools-commit.R#L84-L116)). With the board held by the client ([Client-owned board state](Rewrite-1.1)), there is no R board to stage into, and the assistant's edits and the user's meet in one board.

## What must hold

1. The assistant is a dock extension ([Client-drawn dock and extensions](Rewrite-1.2)) whose edits are deltas through core's commands, applied all or none and marked as its own, so undo keeps its steps apart from the user's ([blockr.core#432](https://github.com/BristolMyersSquibb/blockr.core/issues/432)).
2. An edit reports done only once the blocks it changed, and those downstream of them, are current, with each block's status and conditions.
3. No visitor can read a credential that is not their own.

## Proposal

- The agent loop runs in the browser, where the board it edits is, through the Vercel AI SDK (`ai`) or a provider's SDK, with the commands that core and the extensions register, and requests to R, as its tools, so that it changes what an extension adds, such as blockr.md's document or the DAG's layout, as it changes core's objects ([Board updates](Rewrite-1.1.2#the-front-ends-state-and-attributes)).
- The assistant ships the `llm_model` board option, which core defines today ([R/board-option.R#L666-L751](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L666-L751)) and only the assistant reads, and defines it in the client as every package defines the board options it ships ([Board objects](Rewrite-1.1.1#board-options)).
- One edit tool takes a whole delta and applies it as one undoable step, rather than one tool per command, as Anthropic's guidance argues: "More tools don't always lead to better outcomes" ([Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)).
- The edit tool evaluates the blocks it changed and everything downstream of them, those no panel shows included, in a one-time evaluation ([Evaluation in the client](Rewrite-1.1.10#demand)), and returns once they are current, with each block's status and conditions, so that it sees every failure it caused, and a block the user edits meanwhile at its newer revision.
- A visitor's own credential, such as a viewer OAuth token, may go to the browser, since "OAuth refresh tokens are never returned by Connect" and access tokens are "usually expiring within 24 hours" ([Connect](https://docs.posit.co/connect/user/oauth-integrations/)). A shared key, such as a company LLM key, stays in R behind a stateless proxy, where its calls wait behind evaluation in the session's one process ([blockr.core#430](https://github.com/BristolMyersSquibb/blockr.core/issues/430)), a trade-off to revisit.

## Open questions

- Whether an answer that needs a number adds a block, so that every number the assistant reports is in the exported code, or the assistant may run R outside blocks.
- Whether the proxy runs in the session's R process, or the browser reaches a gateway with the user's SSO token, if it allows cross-origin requests.

## Work

- Rebuild the assistant as a client extension with its agent loop in the browser, in blockr.assistant
- Add the stateless proxy for the provider's shared credentials, in blockr.assistant

<details><summary>Notes for implementers</summary>

The 40 tool definitions at `fd58655`, by file: `tools-read.R` 11, `tools-view.R` 11, `tools-mutation.R` 9, `tools-extension.R` 3, `tools-commit.R` 2, `tools-options.R` 2, `skills-invoke.R` 1, `tools-typed.R` 1.

Tool schemas can come from the registered commands, the schemas of the front-end's state and the block arg specs, a JSON Schema subset that blockr.ai already binds through `ellmer::type_from_schema()`. Both official SDKs refuse to run in a browser without `dangerouslyAllowBrowser: true`, a key there being readable by every visitor. A proxy in R cannot stream over HTTP, since httpuv takes a response body only whole, as "A string (or raw vector)", so streamed tokens would travel over the websocket and pause while R evaluates.

Versions on npm on 2026-10-21: `ai` 7.0.148, `@anthropic-ai/sdk` 0.137.0, `openai` 7.39.0, `@assistant-ui/react` 0.15.30.

</details>
