# UI modules in JS: the host, React and packaging
Status: draft. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): the contract that the UI of every block, option and output meets, the React SDK on top of it, which blockr.ui ships with React, and how packages ship their UIs. It builds on the [board objects proposal](Rewrite-1.1.1) and shapes the module loading ([blockr.core#398](https://github.com/BristolMyersSquibb/blockr.core/issues/398)) and the React SDK ([blockr.core#399](https://github.com/BristolMyersSquibb/blockr.core/issues/399)). Ready-made components for form-like UIs are a later project of blockr.ui ([UI kit and design system for the client](Rewrite-1.7)).

## What must hold

1. A block type's UI is one ES module per type, shipped inside its R package and loaded the first time a block of that type appears.
2. A module gets everything it shares with the page through the host it receives, except React, which reaches it through its build.
3. The contract needs no framework, and React is the usual way to meet it, through a small SDK.
4. One copy each of React, core's runtime and every shared module runs on the page.
5. Core's runtime and every package's UIs ship inside their R packages, so installing a package pins the client code it runs.
6. Core ships no React, and a block type whose UI is written in React works under every front-end, core's basic one included.

## Proposal

### The contract

A module exports its JS API major and one `render()`, after anywidget's `render({ model, el })`, and returns its own cleanup:

```ts
export const api = 1;                                // the JS API major it was built against

export default {
  render({ el, host }: { el: HTMLElement; host: BlockHost }): () => void {
    const draw = () => { /* rebuild the UI from host.state() */ };
    draw();
    return host.on("state", draw);                   // unsubscribing is the cleanup
  }
};
```

Core refuses a module whose major does not match its own. The host is everything the module may use:

```ts
interface BlockHost {
  readonly block: BlockId;
  state(): State;                                    // the block's current state
  context(): BlockContext;                           // its name, status, and inputs as upstream ids and versions
  on(event: "state" | "context", fn: () => void): () => void;
  submit(change: Partial<State>): void;               // one edit, on a user's action only
  request(name: string, args?: Json): Promise<Json | Blob>;   // the block type's requests
  module(pkg: string, name: string): Promise<unknown>;        // a module another package offers
  commands: Commands;                                // run any command, such as setting another block's state
  board(): ReadonlyBoard;                            // a read of the board
}
```

A module takes state changes it did not make, since undo and other blocks make them, and calls `submit()` only when the user acts, never to fill in a value once data arrives. The context holds only what the client knows already, and anything that needs the data comes through the block type's requests, which the host caches by version. The shape is close to blockr.dplyr's [`Blockr.registerBlock()`](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/bdac6b38f7097425bfe96883032531cc919f6ee7/inst/js/blockr-core.js#L57) today, whose block classes implement `setState(state)` and call back on submit.

An option's module gets an option host, holding the option's value, `on("value")` and `submit()`, and an output's module gets an output host, holding the description `block_output()` returned, the output's `meta` and a way to change it, which asks R again.

### The React SDK

```tsx
import { blockModule, useBlockState, useBlockData } from "@blockr/react";

function HeadUI() {
  const [state, submit] = useBlockState();
  const max = useBlockData("n_max");                 // a block type request, cached by version
  return <input type="number" max={max} value={state.n} onChange={e => submit({ n: e.target.valueAsNumber })} />;
}

export const api = 1;
export default blockModule(HeadUI);
```

The hooks read like shinyreact's `useShinyInput()` and `useShinyOutputValue()` ([index.ts](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/pkg-js/src/shiny-react/index.ts)). React reaches the module through its build: blockr.ui ships the one copy of React with the SDK and puts it on a global before any module that uses it loads, and its build preset maps `react` to that copy, so a module's bundle contains no React ([blockr.core#399](https://github.com/BristolMyersSquibb/blockr.core/issues/399)). The copy is blockr.ui's rather than core's or the dock's, since core ships no React and a React block UI has to find React under every front-end: a block package that writes its UI in React imports blockr.ui, as blockr.dplyr, blockr.dm and blockr.ggplot do today, so React is on the page wherever its blocks are, and the dock and its extensions use the same copy, since the dock imports blockr.ui too. React's major then moves with blockr.ui's, not with core's.

### Packaging

A block type's UI is a module in its package, written against the types core ships inside blockr.core, and a UI in React is TSX, as an app's is a `ui.tsx` in shinyreact's pattern ([README.md#L18-L22](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/README.md#L18-L22)), written against the React SDK that blockr.ui ships inside its own R package, as shinyreact ships its runtime with React as one bundle inside its R package ([README.md#L46](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/README.md#L46)). Nothing is published to npm for now. In R, a block type names its UI in its `ui` field, and a package declares the modules it offers others, with their CSS beside them; R tells the client at startup where each is served ([blockr.core#396](https://github.com/BristolMyersSquibb/blockr.core/issues/396)), and the client imports each URL once and loads its CSS with it. A module of another package is reached through `host.module()`, along the R dependencies, as blockr.dm would reach blockr.dplyr's filter UI. A block type's module ships the JSON Schema of the block's state beside it, written once in TypeScript, such as with Zod, whose `z.infer` gives the module its type and `z.toJSONSchema()` the schema ([Zod](https://zod.dev/json-schema)), and R sends the schema with the type's entry in the block registry, so the client has it before the module loads, and writes the state of the blocks it builds by it ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)). A package ships the JSON Schema of each field it registers beside its module in the same way ([Board updates](Rewrite-1.1.2#fields)).

### Testing

Core's test helpers include a stub host, so a module mounts in a test runner with a state, requests answered from fixtures, and a record of what it submitted.

## Open questions

- How a block type's TSX becomes the module the client loads: built by its package with blockr.ui's preset, as shinyreact's bundler tier builds a `ui.tsx` with React externalized to its bundle's copy ([README.md#L42](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/README.md#L42)), or compiled by core as it loads the UI, so that a type defined outside a package needs no build step and the definition a file holds can carry its UI ([Board objects](Rewrite-1.1.1#block-types-outside-a-package)).
- Whether a custom element should be a second form of the contract, beside `render()`.
- Whether TanStack Query backs the host's cache of request answers ([blockr.core#398](https://github.com/BristolMyersSquibb/blockr.core/issues/398)).
