# Choosing the libraries: the agent loop, the chat and the spike
Status: draft. Design for [Assistant as a plugin](Rewrite-1.4).

One of the design pages of the assistant ([Assistant as a plugin](Rewrite-1.4)): the libraries that the agent loop and the chat build on, the candidates with why each that the spike does not try is ruled out, the criteria, and the spike that chooses by them.
The spike runs before the part's other design pages settle, since each of them builds on what it chooses, and each follows its result before it settles.
It shapes the spike's issue, and through its result the Work items that run the loop, draw the chat and port compaction.
The criteria come from the conditions of the part and of its other design pages, and the questions that the spike runs on each library from [The assistant's benchmark](Rewrite-1.8.1).

## What must hold

1. The spike chooses the loop's library and the chat's by the criteria that this page writes down before it runs, and its result names the criterion that decided.
2. Every candidate that this page names is either tried by the spike or ruled out here, with its reason and a source.
3. The spike runs before the part's other design pages settle, and each of them follows its result before it settles.
4. The spike tries each library with the same tools, prompt and model, so that only the libraries differ.
5. The spike's measurements are written down with the versions and the machine that they were taken with.

## Today

Today's assistant builds on two R packages: ellmer runs its agent loop in the session's R process, and shinychat draws its chat ([Assistant as a plugin](Rewrite-1.4#today)).
Neither runs in a browser, so both go.
Two libraries have been found that run an agent loop in a page, the AI SDK and pi, whose bundles were measured on 2026-10-31 (notes).

## Proposal

### What needs a library

- The agent loop calls the model from the page, through the places and the ways to authenticate of [Model access](Rewrite-1.4.1), streams the reply, runs the tools of [The assistant's tools](Rewrite-1.4.2), calls the model again until the turn ends, and stops when the turn's signal aborts ([The assistant's chat](Rewrite-1.4.4#stopping-a-turn)).
- The chat draws the transcript, the composer, the rows of tool calls, branches, attachments, the stop button and the drawer of threads, over the assistant's state ([The assistant's chat](Rewrite-1.4.4)).

What stays the plugin's own, whichever library it builds on: the state's shape ([The assistant's state](Rewrite-1.4.3#the-state)), compaction, which neither library does ([The assistant's state](Rewrite-1.4.3#compaction)), and what the model is told ([The system prompt](Rewrite-1.4.5)).

### The candidates

| Candidate | For | What the spike does with it |
|---|---|---|
| The AI SDK, `ai` with `@ai-sdk/openai` and `@ai-sdk/anthropic` | The loop | Tries it |
| pi, `@earendil-works/pi-agent-core` with `@earendil-works/pi-ai` | The loop | Tries it |
| The providers' own SDKs, `openai` and `@anthropic-ai/sdk` | The loop | Rules it out, since each leaves the loop to the plugin, and the plugin would hold one of them per API of [Model access](Rewrite-1.4.1#the-blockr-options) |
| assistant-ui, `@assistant-ui/react`, over its `ExternalStoreRuntime` | The chat | Tries it ([The assistant's chat](Rewrite-1.4.4#the-panel)) |
| Components of the plugin's own, on blockr.ui's design system | The chat | Tries it, as the measure for assistant-ui |

### The criteria

The loop's library is kept only where it meets each of these:

1. It meets What must hold 1 to 4 of [Assistant as a plugin](Rewrite-1.4#what-must-hold).
2. It reaches each API that [Model access](Rewrite-1.4.1#the-blockr-options) names, OpenAI's Responses and Chat Completions APIs and Anthropic's Messages API, at any base URL, with the credential that the plugin hands it for each call.
3. It streams a turn, and stops it when the turn's signal aborts, with the edit tool's wait and a request to R ([The assistant's chat](Rewrite-1.4.4#stopping-a-turn)).
4. It takes the JSON Schemas that core and other packages register as tool schemas, unchanged ([The assistant's tools](Rewrite-1.4.2#the-tools)).
5. Its messages turn into the state's and back without loss, so that a thread goes on once its board is saved and opened again ([The assistant's state](Rewrite-1.4.3#the-state)).
6. It lets the plugin add the board and the focus after the last message of each call ([The system prompt](Rewrite-1.4.5#what-a-call-sends-and-in-which-order)), and compact before a call.
7. It runs under Vitest on happy-dom with the model faked.
8. Its license lets blockr.assistant ship it in the plugin's bundle.

The chat's library is kept only where it meets each of these:

1. It draws only in the element that the frontend gives it and in the top layer, at any size down to a rail's ([The assistant's chat](Rewrite-1.4.4#what-must-hold)).
2. It shows the assistant's state as it is, branches and attachments included, whatever command changed it last.
3. It runs on the copy of React that core ships ([UI modules in JS](Rewrite-1.1.7#react)), in blockr.ui's design system ([UI kit and design system for the client](Rewrite-1.7)).
4. Its license lets blockr.assistant ship it in the plugin's bundle.

Between libraries that meet them all, the spike keeps the one that needs less code of the plugin's own, and a smaller bundle breaks a tie.
The result records each library's majors of the last year beside them, since a major can break what the plugin builds on, while the plugin's own state keeps it from saved boards ([The assistant's state](Rewrite-1.4.3#the-state)).

### What the spike builds

The spike builds, on each library for the loop, in a branch of blockr.assistant:

1. The edit tool, running a list of commands as one step through core's command registry ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).
2. A read tool, and `inspect_results`, a request to R that stopping the turn cancels.
3. Compaction, before a call, and the board and the focus after the last message.
4. A thread that is saved with its board and opened again.
5. The credential through one function, with each of the three APIs, through OpenAI's provider and Anthropic's.

On the chat, it draws the transcript with its branches, the composer and the stop button, on assistant-ui and on components of the plugin's own, over the same state.

### What the spike measures

- Each criterion, whether the library meets it, and how.
- The bundle that the first turn loads, minified and gzipped, as the measurements of 2026-10-31 took it (notes).
- The lines of TypeScript of the plugin's own that each library needs for what the spike builds.
- The rule for when compaction runs, which the spike sets from the context windows of the models that it tries and the tokens that the questions' calls take ([The assistant's state](Rewrite-1.4.3#compaction)).
- Three of the benchmark's questions, run by hand five times on each library with the same model, prompt and tools, on a board of blocks that have moved to the new stack, since the benchmark's harness comes later ([The assistant's benchmark](Rewrite-1.8.1)).

### When it runs, and where its result goes

The spike is an issue of blockr.assistant, opened once this page settles, ahead of the part's spec, and its branch is never merged.
It writes its result into this page: the libraries chosen, the criterion that decided, and the measurements, with the versions and the machine.
The part's other design pages then follow the result before they settle, as [The assistant's chat](Rewrite-1.4.4#the-panel) does with the chat's library, and [The system prompt](Rewrite-1.4.5) and [The assistant's state](Rewrite-1.4.3#compaction) with the loop's hooks.

## Open questions

None.

<details><summary>Notes for implementers</summary>

The pi project moved from `badlogic/pi-mono` to [earendil-works/pi](https://github.com/earendil-works/pi) in spring 2026, and its npm packages from the now deprecated `@mariozechner/*` to `@earendil-works/*`.
Its `pi-ai` "supports browser environments", except for Amazon Bedrock and the OAuth login flows ([README](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/README.md#browser-usage)), and reaches a proxy that speaks a provider's API as a provider made with `createProvider()`, whose models name the proxy as their `baseUrl` ([README](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/README.md#createprovider)).
Its `pi-agent-core` adds the loop, with steering and follow-up queues, `beforeToolCall` and `afterToolCall`, `transformContext` "for pruning, compaction" and a replaceable `streamFn`, for which `streamProxy()` serves "browser apps that proxy through a backend" ([README](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/agent/README.md#proxy-usage)), posting to a server of pi's own at `/api/stream` that answers in pi's events ([proxy.ts#L146-L150](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/agent/src/proxy.ts#L146-L150)), which a proxy that passes a provider's API through is not ([Model access](Rewrite-1.4.1)).
Sitegeist, a Chrome side-panel agent by pi's author, was built on both and on `pi-web-ui` ([badlogic/sitegeist](https://github.com/badlogic/sitegeist)), whose web components left the repo after 0.75.3 in May 2026, so pi brings no UI.
The AI SDK runs a `ToolLoopAgent` in the page behind `useChat` through `DirectChatTransport` ([reference](https://ai-sdk.dev/docs/reference/ai-sdk-ui/direct-chat-transport)), and its providers take `baseURL`, `headers` and `fetch` ([Anthropic provider](https://ai-sdk.dev/providers/ai-sdk-providers/anthropic)), while a model named by a bare id goes to Vercel's AI Gateway, since "By default, the global provider is set to the Vercel AI Gateway" ([provider management](https://ai-sdk.dev/docs/ai-sdk-core/provider-management)).
The chat UI of `@assistant-ui/react` runs on either loop through its custom runtimes ([LocalRuntime](https://www.assistant-ui.com/docs/runtimes/custom/local-runtime)).

Measured on 2026-10-31, a minimal agent with one tool and the Anthropic provider, bundled with esbuild 0.25.12 as minified ESM for the browser and gzipped at level 9, weighs 205 KB with the AI SDK (912 KB minified, of which zod 4.6.7 takes 443 KB and the unused AI Gateway client 71 KB) and 116 KB with pi (435 KB minified, of which `@anthropic-ai/sdk` takes 181 KB and TypeBox 142 KB).
The Anthropic SDK alone weighs 76 KB, and a client that ships zod anyway shares it with the AI SDK.
Nothing has measured either library with OpenAI's provider yet, which the spike does.

Versions on npm on 2026-10-31: `ai` 7.0.159 with `@ai-sdk/anthropic` 4.0.94, `@earendil-works/pi-agent-core` and `@earendil-works/pi-ai` 1.4.0, `@anthropic-ai/sdk` 1.3.0, `openai` 7.47.0, `@assistant-ui/react` 0.15.32.
The AI SDK released 5.0, 6.0 and 7.0 on 2025-07-31, 2025-12-22 and 2026-06-25, and pi-agent-core 1.0 on 2026-10-01.

</details>
