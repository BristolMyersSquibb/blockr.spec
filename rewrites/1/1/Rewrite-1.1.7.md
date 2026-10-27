# UI modules in JS: the host, React and packaging
Status: draft. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): the contract a JS module meets when a block, an option or an output needs more than core's input elements, the React SDK on top of it, and how packages ship their JS. It builds on the [document model](Rewrite-1.1.1) and shapes the module loading ([blockr.core#398](https://github.com/BristolMyersSquibb/blockr.core/issues/398)) and the React SDK ([blockr.core#399](https://github.com/BristolMyersSquibb/blockr.core/issues/399)); the input elements composed in R are the UI-in-R proposal ([Input elements](Rewrite-1.1.6)).

## What must hold

1. A UI that needs more than the input elements is one ES module per type, built from TypeScript into its R package's `inst/`, loaded the first time a block of that type appears.
2. A module gets everything it shares with the page through the host it receives, except React, which reaches it through its build.
3. The contract needs no framework, and React is the usual way to meet it, through a small SDK.
4. One copy each of React, core's runtime and every shared module runs on the page.

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
  elements: Elements;                                // core's input elements, usable inside a module
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
  const max = useBlockData("n.max");                 // a block type request, cached by version
  return <input type="number" max={max} value={state.n} onChange={e => submit({ n: e.target.valueAsNumber })} />;
}

export const api = 1;
export default blockModule(HeadUI);
```

The hooks read like shinyreact's `useShinyInput()` and `useShinyOutputValue()` ([index.ts](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/pkg-js/src/shiny-react/index.ts)). React reaches the module through its build, from a global the dock fills before any module loads, through a preset core publishes, so the bundle contains no React ([blockr.core#399](https://github.com/BristolMyersSquibb/blockr.core/issues/399)).

### Packaging

A package builds its modules with any bundler and core's preset into `inst/js/`, against the types core publishes on npm. In R, a block type names its module where it would name its UI, and a package declares the modules it offers others, with their CSS beside them; R tells the client at startup where each is served ([blockr.core#396](https://github.com/BristolMyersSquibb/blockr.core/issues/396)), and the client imports each URL once and loads its CSS with it. A module of another package is reached through `host.module()`, along the R dependencies, as blockr.dm would reach blockr.dplyr's filter UI.

### Testing

Core's test helpers include a stub host, so a module mounts in a test runner with a state, requests answered from fixtures, and a record of what it submitted.

## Open questions

- Whether a custom element should be a second form of the contract, beside `render()`.
- Whether TanStack Query backs the host's cache of request answers ([blockr.core#398](https://github.com/BristolMyersSquibb/blockr.core/issues/398)).
