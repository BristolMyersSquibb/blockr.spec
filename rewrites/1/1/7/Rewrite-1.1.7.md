# UI modules in JS: the host, React and packaging
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): the contract that the UI of every block, board option and output meets, how core loads these modules and the startup modules packages declare, and how packages ship them. It builds on the [board objects](Rewrite-1.1.1) and [board updates](Rewrite-1.1.2) proposals, and shapes loading and mounting a block type's UI module, an item in the Work list of [Client-owned board state](Rewrite-1.1#work). How R names a type's UI and its requests is [Block types in R](Rewrite-1.1.5)'s, and how a front-end has core mount these modules is [Front-ends and extension points](Rewrite-1.1.8)'s. Core ships no React, and this page covers only what core does so that a package can ship the one copy block UIs use: which package does, with any SDK on top of it, lies outside it, as do ready-made components for form-like UIs.

## What must hold

1. A block type's UI is one ES module, shipped inside its R package, or carried by its definition for a type defined outside a package, and loaded the first time core mounts a block of that type.
2. A module gets everything it shares with the page through the host it receives, except a library it imports as it loads, such as React, which reaches it through its build.
3. The contract needs no framework, so a UI in plain TypeScript and one in React meet it alike.
4. One copy each of React, core's runtime and every shared module runs on the page.
5. Core's runtime and every package's UIs ship inside their R packages, so installing a package pins the client code it runs.
6. Core ships no React, and a block type whose UI is written in React works under every front-end, core's basic one included.
7. What a package registers in the client, its board options, fields and commands, is registered before the store opens a board, however late R loads the package.

## Proposal

### The contract

A module exports the JS API major it was built against and a default with one `render()`, after the `render({ model, el, signal, host })` of anywidget's front-end module ([AFM](https://anywidget.dev/en/afm/)). Core calls it whenever it mounts the module, with the element to draw in, the host, and a signal that it aborts when it unmounts the module, and `render()` may be async and may return its cleanup, which core runs when it aborts the signal:

```ts
export const api = 1;                                // the JS API major it was built against

export default {
  render({ el, host, signal }: { el: HTMLElement; host: BlockHost; signal: AbortSignal }): () => void {
    const draw = () => { /* rebuild the UI from host.state() */ };
    draw();
    return host.on("state", draw);                   // unsubscribing is the cleanup
  }
};
```

Core refuses a module whose major does not match its own. A module that fails to load, declares another major or throws in `render()` leaves an error in its element that names the module and its package, as AFM has a failing hook fail visibly, and the rest of the page, the block's evaluation included, carries on. A custom element meets the contract through `render()`, which puts one in `el` and hands it the host, so the contract has no second form for it, since that would tie the contract to the page's element registry, where a name is defined once and never removed. The host is everything the module may use:

```ts
interface BlockHost<S extends State = State> {
  readonly block: BlockId;
  state(): S;                                        // the block's current state
  context(): BlockContext;                           // what the client knows of the block besides its state
  on(event: "state" | "context", fn: () => void): () => void;
  submit(change: Partial<S>): Promise<void>;         // one edit, on a user's action only, rejecting with what refused it
  request<T = Json>(name: string, args?: Partial<S> & Record<string, Json>): Promise<T | Blob>;   // a request of the block type, with state args and parameters
  upload(file: File): Promise<string>;               // sends a file to the R session, resolving with the path R stored it at
  invalidate(): void;                                // has the block evaluated again, as a read block's reload does
  module<T = unknown>(id: string): Promise<T>;       // a module another package offers, by id, such as "blockr.dplyr-filter"
}

interface BlockContext {
  name: string;                                      // "Head"
  status: BlockStatus;                               // its status, version, conditions and expression, as the scheduler has them
  inputs: { slot: string; block: BlockId; version: number }[];   // in slot order, as an evaluation request names them
  fixed: string[];                                   // the state args the board's lock fixes
}
```

Core's public interfaces, the hosts and `CoreApi` alike, follow changes through a getter and a subscription, as `state()` and `on()` do here, while core derives its values with signals inside, as [State in JS](Rewrite-1#principles) has Shiny's reactives become signals. React's `useSyncExternalStore` takes such a pair as it is, and any other framework, or none, can use it, so no module depends on which signals library core uses.

A block's UI touches only its own block, as a block's module does today, which core's block server hands only its data inputs ([R/block-server.R#L638](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L638)). Data reaches it through links, and edits across blocks come from extensions, which get `CoreApi` ([Front-ends and extension points](Rewrite-1.1.8#extensions)), so the host gives it neither the board nor the command registry, which it can gain later without a new major once a block type needs them.

Core makes a host each time it mounts a module and drops it when the module unmounts, and a host keeps nothing of its own: the state is the store's, the status the scheduler's, and request answers, each block's last output and an output's `meta` are core's, so a module mounted again draws from them without asking R. A module stays mounted until the front-end calls the cleanup that mounting it returned, so the front-end decides how long a mount lasts. Dockview destroys a panel only when it is closed, which removes the panel and not its block, and a panel hidden behind another only has its element leave the page or stay in it hidden ([rendering.mdx#L15-L50](https://github.com/mathuo/dockview/blob/27a42c314a06ebc37f288d6d181d01b6cb84cd7a/packages/docs/docs/core/panels/rendering.mdx#L15-L50)), so a front-end that mounts a block's UI with its panel keeps it mounted through every switch between panels.

A block with no mounted UI, such as one whose panel is closed, loses nothing: its state stays in the board, its status in the scheduler and its result in R, it evaluates whenever something demands it ([Evaluation in the client](Rewrite-1.1.10#demand)), and anything can invalidate it through `CoreApi` ([Evaluation in the client](Rewrite-1.1.10#invalidation)), where `host.invalidate()` is only its own UI's way to do so. What goes with a module is its own screen state, such as a scroll position or text not yet submitted, so a module submits an edit still pending when core unmounts it.

A module takes state changes it did not make, since undo, the assistant and extensions make them, and calls `submit()` only when the user acts, never to fill in a value once data arrives. An input that changes with every keystroke or pointer move submits once the user pauses or lets go, so that a burst of typing is one edit and one undo step ([Board updates](Rewrite-1.1.2#undo)), and a `submit()` runs the command that sets the block's state ([Board updates](Rewrite-1.1.2#commands)). The module draws no control for an arg that `fixed` names, since the store refuses every edit of one ([Wire protocol](Rewrite-1.1.9#locked-boards)), and reads the block's status as front-ends do ([Evaluation in the client](Rewrite-1.1.10#statuses)). The shape is close to blockr.dplyr's [`Blockr.registerBlock()`](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/bdac6b38f7097425bfe96883032531cc919f6ee7/inst/js/blockr-core.js#L57) today, whose block classes implement `setState(state)` and call back on submit.

The context holds only what the client knows already, and anything that needs the data comes through the block type's requests. The host sends a request with the inputs at the versions the context names and with the state args its function names, from `args` or else from the block's state, and with the parameters `args` gives, such as the column whose values a dropdown lists ([Block types in R](Rewrite-1.1.5#requests), [Wire protocol](Rewrite-1.1.9#requests)). Core keeps the answers, shared by every block of the type, by registry id, name, args and the versions read: it merges a request with an identical one in flight, keeps a block's last answer while the next loads, and drops an answer once the versions it read are superseded. An answer is a snapshot that never goes stale for its key, so nothing refetches it, while the answer of a request its type marks volatile, such as a directory listing, is never kept, and core needs no query library such as TanStack Query, which refetches data that changes behind the client's back. A file the user picks reaches R through `upload()`, which sends it to the session as Shiny's `fileInput()` does. R stores it in the session's temporary directory for as long as the session lives, and the module submits the path `upload()` resolves with into the block's state, from which the type's `expr` builds the expression, as core's upload block builds it today from `input$upload$datapath` ([R/file-upload.R#L21-L44](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/file-upload.R#L21-L44)). Storing a file is a write, so an upload is no request of the block type, whose answers core caches.

A board option's UI, or the renderer that replaces it, gets an option host, and the renderer of an output's family ([Front-ends and extension points](Rewrite-1.1.8#renderers)) gets an output host:

```ts
interface OptionHost<V extends Json = Json> {
  readonly option: OptionId;
  value(): V;                                        // the option's value in the board
  on(event: "value", fn: () => void): () => void;
  submit(value: V): Promise<void>;                   // runs core's command that sets a board option
}

interface OutputHost {
  readonly block: BlockId;
  output(): Json;                                    // what the block type's output returned for the block's result
  body(): Blob | null;                               // the binary body it came with, if any, such as a plot's PNG
  meta(): Json;                                      // what the output keeps of its own, such as a table's page and sort
  on(event: "output", fn: () => void): () => void;
  setMeta(meta: Json): void;                         // asks R for the output again
  draw(el: HTMLElement, output: Json): () => void;   // draws an output nested in this one, with the renderer for its families
}
```

What a block type's `output` returns lists its output families in its `family`, most specific first, as `{ "family": ["blockr.core-table"], ... }` does, and the renderer R picked for the first of them that has one draws it ([Front-ends and extension points](Rewrite-1.1.8#renderers)), so that a front-end or a UI kit changes how every table looks without touching a block type. Core asks R for an output and draws it again when the block's version, a board option, the element's size or the output's `meta` changes ([Front-ends and extension points](Rewrite-1.1.8#what-core-gives-a-front-end)). It keeps each block's last output with the version, board options, size and `meta` it was asked with, so that an output mounted again under the same ones, as when a panel reopens, draws without asking R. An output's `meta` has the shape its output family documents, as its description does, since R's `output` reads it and any renderer of the family sets it, so that a UI kit's table and core's plain table page and sort through the same `meta`. Core keeps it per block for the page, beside the block's status, so that a panel mounted again keeps its page and sort, while the board holds none of it, so that nothing of it is saved or undone, as blockr.dm's table output keeps its table, page and sort in the Shiny session today ([R/dm-block.R#L504-L560](https://github.com/BristolMyersSquibb/blockr.dm/blob/4e2191a9a99bafd0a60f8b8ee301c9f9c3e7b8ee/R/dm-block.R#L504-L560)).

Only what core mounts inside a front-end's layout, written by another package, gets a host narrowed to one thing: a block's UI, a board option's UI or renderer, and an output's renderer. A front-end, which draws the whole board, its stacks and links included, gets `CoreApi`, as a startup module does, so core makes no host for a stack or for the board. A front-end that mounts other packages' UI itself, such as on its stacks, narrows `CoreApi` for it in the same way, and keeps what that UI should save in a field it registers, keyed by stack id ([Board updates](Rewrite-1.1.2#fields)), as in this host for a note on each stack:

```ts
// in the front-end's package, which registers the field "myfe-stack_notes" in its startup module
const stackHost = (core: CoreApi, id: StackId) => ({
  stack: () => core.store.board().stacks[id],
  note: () => core.store.board().fields["myfe-stack_notes"]?.[id],
  on: (fn: () => void) => core.store.subscribe(fn),
  // and a way to write the note, through core's command for a field's entries, as one undo step
});
```

### Startup modules

A package may declare in R one startup module, for what has to run before anything mounts: registering the board options it ships ([Board objects](Rewrite-1.1.1#options)), its fields and its commands ([Board updates](Rewrite-1.1.2#fields)), putting on the page what it shares with other packages' modules, such as React (below) or a UI kit's stylesheet, and naming a board to open in place of the one R sent, such as the board a URL names for session management ([Front-ends and extension points](Rewrite-1.1.8#starting-the-page)). The module exports the JS API major and a default with `initialize()`, after AFM's, which runs once before any view renders, and core calls it with `CoreApi`, as it calls a front-end's `render()` ([Front-ends and extension points](Rewrite-1.1.8#what-core-gives-a-front-end)):

```ts
export const api = 1;                                // the JS API major it was built against

export default {
  initialize({ core, signal }: { core: CoreApi; signal: AbortSignal }): void | Promise<string | void> {
    core.options.register(dataDir);                  // a board option it ships, such as blockr.io's data directory
    core.store.register(positions);                  // a field, such as the DAG's positions
    core.commands.register(relayout);                // a command, such as the DAG's relayout
    // it may also resolve with a saved file's text, which core opens in place of the board R sent
  }
};
```

R sends the startup modules of the packages it has loaded with the block registry's entries, in its reply to `hello` and to every opening of a board, since opening one loads the packages it names ([Board updates](Rewrite-1.1.2#opening-a-board)), and orders them so that each package's comes after those of the packages it depends on in R. Core imports and initializes them one at a time in that order, awaiting each `initialize()`, since a module's imports run as it loads, so that what a package sets up is in place before the module of a package that depends on it loads. It does so before the front-end mounts and before the store opens the board R sent, so that the store finds every field and board option registered.

Core initializes each package's startup module once per page and skips it when a later reply names the package again. A reply that names a package at another version than the one loaded, as after R restarts with the package reinstalled, makes core ask for the page to be reloaded rather than load a second copy. A startup module that fails to load or throws in `initialize()` is named in an error, and core carries on with the rest, so the board opens without what that package registers, which the store names as it names any field no package registered ([Board updates](Rewrite-1.1.2#fields)).

A package relies on the order only for the packages it imports in R, which is what a module needs as it loads, such as a library on another package's global. Between any other two packages the order is unspecified, and core keeps what they share independent of it:

- A startup module registers and subscribes in `initialize()`, and looks up what other packages registered when it uses it, as a field's `expand` runs per delta and a command's `run()` per command. It reads no board there, since none is open at startup, and when an opening brings the package, the board R sent replaces the old one only after `initialize()`.
- Ids carry their package, and a board option id, which does not, fails when another package has registered it, naming both, as a taken attribute name does ([Board updates](Rewrite-1.1.2#fields)).
- A startup module that an opening brings runs just before the store announces the board ([Board updates](Rewrite-1.1.2#following-the-board)), so a front-end that lists registrations, such as the board options in its settings, reads them again then. Only a startup module that runs as the page starts may name a board to open, and core ignores a board named by one that an opening brings, since that opening is under way.
- A stylesheet loads with its module, so a UI kit's, beside its startup module, is in place before those of the packages that import the kit, which use its classes and refine them in their own CSS, loaded later. A stylesheet styles only classes under a prefix of its package's own, so packages that don't know each other never style the same element, and a theme restyles every package through the kit's custom properties.

### React

A module written in React imports `react` as any React code does, and its build maps `react`, `react-dom` and entry points such as `react/jsx-runtime` to one copy that a package puts on the page, so the module's bundle holds no React, as WordPress's build plugin maps `react` to the global `React` ([README](https://github.com/WordPress/gutenberg/blob/debb46ec9c901b95e31f8c420ef93dd61054f497/packages/dependency-extraction-webpack-plugin/README.md)) and Grafana builds plugins with `react`, `react/jsx-runtime` and `react-dom` as [externals](https://github.com/grafana/plugin-tools/blob/2115b27767554a555640300c7b4dc9c9e1842909/packages/create-plugin/templates/common/.config/bundler/externals.ts#L19-L22). React reaches the module through its build rather than through the host, since React libraries import `react` themselves, often as they load, as TanStack Query calls `createContext()` at the top of a module ([QueryClientProvider.tsx#L9](https://github.com/TanStack/query/blob/9e4253766f8015d1372bcd515f50103fd067a42d/packages/react-query/src/QueryClientProvider.tsx#L9)), while the host arrives only once the module renders. The package that ships the copy puts it on a global of its own in its startup module, and a package whose modules import React depends on that package in R, so that the copy is in place before any of them loads. The global is the package's rather than `window.React`, which may be taken already: reactR's dependency loads React's UMD build, which sets it ([R/dependencies.R#L35-L48](https://github.com/react-R/reactR/blob/808b21f4f2e5c374cb8ec910f8e2cc27f6b40e1b/R/dependencies.R#L35-L48)).

Core ships no React, since its basic front-end and built-in blocks are written in plain TypeScript, so core's JS API major says nothing of React's, which moves with the package that ships the copy. An SDK of hooks over the host, which could read like shinyreact's `useShinyInput()` and `useShinyOutputValue()` ([index.ts](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/pkg-js/src/shiny-react/index.ts)), can ship with that copy and needs nothing of core beyond the host.

### Packaging

A block type's UI is an ES module in its package's `inst/`, written against the types core ships inside blockr.core. Core loads JS only and compiles nothing, so a package either writes its modules in JS, as blockr.dplyr and blockr.ggplot write theirs today with no build step, type-checked through `// @ts-check` ([tsconfig.json](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/bdac6b38f7097425bfe96883032531cc919f6ee7/tsconfig.json)), or builds them from TypeScript or TSX and commits what it builds, since R CMD check and CRAN run no Node, as shinyreact keeps the bundle it builds in its R package ([README.md#L63](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/README.md#L63)) and its apps write a `ui.tsx` ([README.md#L18-L22](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/README.md#L18-L22)). Core's runtime ships inside blockr.core as one bundle, as shinyreact ships its runtime inside its R package ([README.md#L46](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/README.md#L46)), and nothing is published to npm for now, so a package builds against the types of the installed blockr.core.

In R, a block type names its UI in its `ui` field ([Block types in R](Rewrite-1.1.5#the-block-type)), and a package declares the modules it offers others and its renderers ([Front-ends and extension points](Rewrite-1.1.8#renderers)), each under a name that gives it an id, `{pkg}-{name}`, as a registry id is. R tells the client where each module is served, with the block registry's entries, when the client connects and whenever a board opens ([Block types in R](Rewrite-1.1.5#registration)), and the client imports each URL once and loads the CSS beside a module with it. A module of another package is reached through `host.module()` by its id, along the R dependencies, as blockr.dm reuses blockr.dplyr's filter UI today through its HTML dependency ([R/dm-filter-block.R#L173-L191](https://github.com/BristolMyersSquibb/blockr.dm/blob/4e2191a9a99bafd0a60f8b8ee301c9f9c3e7b8ee/R/dm-filter-block.R#L173-L191)).

A block type defined outside a package names a plain JS module, whose text its definition carries ([Board objects](Rewrite-1.1.1#block-types-outside-a-package)), so that a saved file brings the type's UI along, and core imports it once R has registered the type. R registers such a type from a file only where the `load_definitions` option allows it, so the JS a file carries runs under the same opt-in as its R.

A block type's module ships the JSON Schema of the block's state beside it, which a package that builds from TypeScript can write once, such as with Zod, whose `z.infer` gives the module its type and `z.toJSONSchema()` the schema ([Zod](https://zod.dev/json-schema)). R reads the schema when it registers the type, writes the state of the blocks it builds by it ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)), and sends it with the type's entry in the block registry, so the client has it before the module loads. A package ships the JSON Schema of each field it registers beside the startup module that registers it, in the same way ([Board updates](Rewrite-1.1.2#fields)).

### Testing

Core ships a stub of each host inside blockr.core, beside its types, so a module mounts in a test runner with a state, requests answered from fixtures, and a record of what it submitted, needing neither R nor a browser, as blockr.dplyr tests its JS today with `node --test` and happy-dom ([package.json](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/bdac6b38f7097425bfe96883032531cc919f6ee7/package.json)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

An element that has left the page measures 0 by 0, as dockview warns of a hidden panel under its default renderer ([rendering.mdx#L18-L21](https://github.com/mathuo/dockview/blob/27a42c314a06ebc37f288d6d181d01b6cb84cd7a/packages/docs/docs/core/panels/rendering.mdx#L18-L21)), so `mountOutput()` asks R for no output while its element measures nothing, and asks again once it measures a size.

Only running the startup modules and their `initialize()` follows the order, so core can fetch every one at once, such as with `<link rel="modulepreload">`. R orders them by the `Depends` and `Imports` of each package's DESCRIPTION, since the namespaces R has loaded come in no order of their own.

The module of a type defined outside a package is written into its definition as the file's text, read when `block_type()` is called, rather than as the path the script gave, which does not exist where the file is opened. R can serve that text at a URL of its own, as it serves a package's modules, so that the client imports every module alike, and a page whose content security policy forbids `blob:` scripts loads it too.

An import map, which would let a module import `react` with no build step, was weighed for shinyreact and not chosen: injecting one is fragile with the order in which htmltools assembles the page head, and Vite's dev server does not resolve bare specifiers against a page's import map ([js-distribution decision](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/decisions/2026-08-17-js-distribution.md)).

</details>
