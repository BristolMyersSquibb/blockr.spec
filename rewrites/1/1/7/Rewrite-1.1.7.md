# UI modules in JS: the host, React and packaging
Status: settled on 2026-10-30. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): the contract that the UI of every block, board option and output meets, how core loads these modules and the startup modules packages declare, and how packages ship them.
It builds on the [board objects](Rewrite-1.1.1) and [board updates](Rewrite-1.1.2) proposals, and shapes blockr.ci's TypeScript gates ([blockr.ci#93](https://github.com/BristolMyersSquibb/blockr.ci/issues/93)), the toolchain of core's client ([blockr.core#419](https://github.com/BristolMyersSquibb/blockr.core/issues/419)), what packages declare in R ([blockr.core#424](https://github.com/BristolMyersSquibb/blockr.core/issues/424)), exporting the block registry ([blockr.core#426](https://github.com/BristolMyersSquibb/blockr.core/issues/426)), loading and mounting a block class's UI module ([blockr.core#437](https://github.com/BristolMyersSquibb/blockr.core/issues/437)), the UIs of core's built-in blocks ([blockr.core#438](https://github.com/BristolMyersSquibb/blockr.core/issues/438)), core's renderers and board options ([blockr.core#439](https://github.com/BristolMyersSquibb/blockr.core/issues/439)), `CoreApi` and starting the page ([blockr.core#440](https://github.com/BristolMyersSquibb/blockr.core/issues/440)), the guide for block class authors ([blockr.core#444](https://github.com/BristolMyersSquibb/blockr.core/issues/444)), starting core again as a board opens ([blockr.core#497](https://github.com/BristolMyersSquibb/blockr.core/issues/497)) and filling the block registry from the packages that the app names ([blockr.core#498](https://github.com/BristolMyersSquibb/blockr.core/issues/498)), each an item in the Work list of [Client-owned board state](Rewrite-1.1#work).
How R names a class's UI and its requests is [Block classes in R](Rewrite-1.1.5)'s, and how a front-end has core mount these modules is [Drawing the board](Rewrite-1.1.8)'s.
Core ships the one copy of React that block UIs use, with the React SDK, while richer ready-made components for form-like UIs lie outside this page ([UI kit and design system for the client](Rewrite-1.7)).

## What must hold

1. A block class's UI is one ES module, shipped inside its R package, or in a file the script names for a class defined outside a package, and loaded the first time core mounts a block of that class.
2. A module gets everything it shares with the page through the host it receives, except a library it imports as it loads, such as React, which reaches it through its build.
3. The contract needs no framework, so a UI in plain TypeScript and one in React meet it alike.
4. One copy each of React, core's runtime and every shared module runs on the page.
5. Core's runtime and every package's UIs ship inside their R packages, so installing a package pins the client code it runs.
6. Core ships the one copy of React, so that a block class whose UI is written in React works under every front-end, core's basic one included, whichever other packages are loaded.
7. What a package registers in the client, its board options, its board classes, the migrations of its block classes' states and its commands, is registered before the store opens a board.

## Proposal

### The contract

A module exports the JS API major it was built against and a default with one `render()`, after the `render({ model, el, signal, host })` of anywidget's front-end module ([AFM](https://anywidget.dev/en/afm/)).
Core calls it whenever it mounts the module, with the element to draw in, the host, and a signal that it aborts when it unmounts the module, and `render()` may be async and may return its cleanup, which core runs when it aborts the signal:

```ts
export const api = 1;                                // the JS API major it was built against

export default {
  render({ el, host, signal }: { el: HTMLElement; host: BlockHost; signal: AbortSignal }): () => void {
    const draw = () => { /* set each input from host.state() in place, but the one the user is editing */ };
    draw();
    return host.on("state", draw);                   // unsubscribing is the cleanup
  }
};
```

Core refuses a module whose major does not match its own.
Beside `render()`, the default may hold `options`, the ids of the board options the module requires, which core adds to the board before it calls `render()`, and for a renderer before it first asks R for an output that the renderer draws ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)).
Those include every board option that a request of the module's class reads, as the block registry entry names them, and core refuses a module that leaves one out, naming the board option and the request.
A module that fails to load, declares another major, leaves out such a board option or throws in `render()` leaves an error in its element that names the module and its package, as AFM has a failing hook fail visibly, and the rest of the page, the block's evaluation included, carries on.
A custom element meets the contract through `render()`, which puts one in `el` and hands it the host, so the contract has no second form for it, since that would tie the contract to the page's element registry, where a name is defined once and never removed.
The host is everything the module may use:

```ts
interface BlockHost<S extends State = State> {
  readonly block: BlockId;
  readonly class: RegistryId;                        // its block class, since one module may serve several
  state(): S;                                        // the block's current state
  context(): BlockContext;                           // what the client knows of the block besides its state
  on(event: "state" | "context", fn: () => void): () => void;
  submit(change: Partial<S>): Promise<void>;         // one edit, on a user's action only, rejecting with what refused it
  request<T = Json>(name: string, args?: Partial<S> & Record<string, Json>, opts?: HostRequestOpts): Promise<T | Blob>;   // a request of the block class, with state args and parameters
  evaluate(params: Record<string, Json>): Promise<BlockStatus>;   // a one-time evaluation of the block with parameters, which its block_eval() method reads
  module<T = unknown>(id: string): Promise<T>;       // a module another package offers, by id, such as "blockr.dplyr-filter"
}

interface BlockContext {
  name: string;                                      // "Head"
  status: BlockStatus;                               // its status, revision, conditions and summary, as the scheduler has them
  inputs: { input: string; revision: number }[];     // its linked inputs, in the order of its class's inputs, whose revisions say when the data changed
  options: Record<OptionId, Json>;                   // the values of the board options its module names
}

interface HostRequestOpts extends Omit<RequestOpts, "reads"> {   // CoreApi's, whose reads the host fills in, from the block's inputs or the output it holds
  file?: File;                                       // a file it sends, such as an upload or the bitmap of a chart
}
```

Core's public interfaces, the hosts and `CoreApi` alike, follow changes through a getter and a subscription, as `state()` and `on()` do here, while core derives its values with signals inside, as [State in JS](Rewrite-1#principles) has Shiny's reactives become signals.
React's `useSyncExternalStore` takes such a pair as it is, and any other framework, or none, can use it, so no module depends on which signals library core uses.
A getter returns the same object until the event that announces a change fires, since `useSyncExternalStore` compares what it returns by identity and draws again, without end, if every call returns a new one.

A block's UI touches only its own block, as a block's module does today, which core's block server hands only its data inputs ([R/block-server.R#L638](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L638)).
Data reaches it through links, and edits across blocks come from extensions, which get `CoreApi` ([Plugins](Rewrite-1.1.12#a-plugin)), so the host gives it neither the board nor the command registry, nor a way to invalidate its block, which no block's UI has today and a block's menu does through `CoreApi` ([Evaluation in the client](Rewrite-1.1.10#invalidation)).
It can gain any of them later without a new major once a block class needs it.
What it does give is a one-time evaluation of its own block with parameters, as a write block's save button needs (below), which without parameters would only repeat what demand does for a block whose UI shows, and the block's class, since blockr.ggplot draws its four block classes with one module, which tells them apart today by an attribute their R UIs set ([inst/js/gg-blocks.js#L405-L406](https://github.com/BristolMyersSquibb/blockr.ggplot/blob/a44620faec412232d62e03629ef0584e48bae447/inst/js/gg-blocks.js#L405-L406)).

Core makes a host each time it mounts a module and drops it when the module unmounts, and a host keeps nothing of its own: the state is the store's, the status the scheduler's, and request answers, each block's last output and an output's parameters are core's, which it keeps for one opening of the board ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)), so a module mounted again draws from them without asking R.
A module stays mounted until the front-end calls the cleanup that mounting it returned, so the front-end decides how long a mount lasts, except that a host is bound to the board it was made on and to its block: once another board opens or the block leaves the board, core aborts the module's signal, and `submit()` and `evaluate()` reject, so that an edit still pending when a module unmounts never lands on a board opened in the meantime.
A cleanup that `render()` resolves with after core aborted the signal runs at once.
Dockview destroys a panel only when it is closed, which removes the panel and not its block, and a panel hidden behind another only has its element leave the page or stay in it hidden ([rendering.mdx#L15-L50](https://github.com/mathuo/dockview/blob/27a42c314a06ebc37f288d6d181d01b6cb84cd7a/packages/docs/docs/core/panels/rendering.mdx#L15-L50)), so a front-end that mounts a block's UI with its panel keeps it mounted through every switch between panels.

A block with no mounted UI, such as one whose panel is closed, loses nothing: its state stays in the board, its status in the scheduler and its result in R, it evaluates whenever something demands it ([Evaluation in the client](Rewrite-1.1.10#demand)), and anything can invalidate it through `CoreApi` ([Evaluation in the client](Rewrite-1.1.10#invalidation)).
What goes with a module is its own screen state, such as a scroll position or text not yet submitted, so a module submits an edit still pending when core unmounts it.
A module draws only inside its element and keeps nothing document-wide, such as an element id, so that core can mount one block's UI or output in several places at once, each mount with a host of its own, where a Shiny input binds to one element only, which is why today's dock moves a card's element from place to place.

A module takes state changes it did not make, since undo, the assistant and extensions make them, and calls `submit()` only when the user acts, never to fill in a value once data arrives.
An input that changes with every keystroke or pointer move submits once the user pauses or lets go, so that a burst of typing is one edit and one undo step ([Board updates](Rewrite-1.1.2#undo)), and a `submit()` runs the command that sets the block's state ([Board updates](Rewrite-1.1.2#commands)).
The store commits a submit at once, and the host announces it as it does any other change, before the user's next keystroke, so the echo of a module's own edit comes before anything the user types next rather than late from R, which is why today's blocks skip it with a flag ([R/read.R#L372-L392](https://github.com/BristolMyersSquibb/blockr.io/blob/9d8a10142777ae86bbde400c91ce6e4c20f515b7/R/read.R#L372-L392)).
A module updates its inputs in place, leaving the one the user is editing, since building them again would take its focus and caret, and builds each submit from `host.state()` when it submits, so that an edit made in the meantime, such as a condition the assistant added to a filter, is kept.
A submit builds on the current state, as every command does, so of two edits to one arg the later wins ([Board updates](Rewrite-1.1.2#deltas)).
On a locked board a front-end mounts the UI only of a block that the board lock leaves open, as `store.locked()` says, since it draws no control for what a lock fixes, so a module needs no flag for the lock ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins), [Locked boards and the properties of blocks](Rewrite-1.1.11#block-locks)).
It reads the block's status as front-ends do ([Evaluation in the client](Rewrite-1.1.10#statuses)).
The shape is close to blockr.dplyr's [`Blockr.registerBlock()`](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/bdac6b38f7097425bfe96883032531cc919f6ee7/inst/js/blockr-core.js#L57) today, whose block classes implement `setState(state)` and call back on submit.

The context holds only what the client knows already, and anything that needs the data comes through the block class's requests.
The host sends a request once core has had the inputs it reads evaluated, even where nothing demands them, as core does for a plugin's request, so that it reads them at revisions that may be newer than those the context named when the module asked ([Evaluation in the client](Rewrite-1.1.10#demand)).
It sends the request through the scheduler's `request()`.
Where R replies `missing`, the host has the inputs evaluated again and asks again at their current revisions.
With them go the state args its function names, from `args` or else from the block's state, the parameters `args` gives, such as the column whose values a dropdown lists, and exactly the values of the board options it reads, by id, which its `new_block_request()` names, so that a board option it does not read changes none of its answers ([Block classes in R](Rewrite-1.1.5#requests), [Wire protocol](Rewrite-1.1.9#requests)).
Those values are in the context too, which changes when one does, so that a module asks again and shows what depends on them, as blockr.io's path field shows the data directory as its prefix today ([R/path-input.R#L195-L205](https://github.com/BristolMyersSquibb/blockr.io/blob/9d8a10142777ae86bbde400c91ce6e4c20f515b7/R/path-input.R#L195-L205)).
A module gives a request up through its `signal`, and core sends R a `cancel` once no caller merged with it still waits, so that a search the user has typed on does not hold up what R runs after it, as R runs one request at a time ([Wire protocol](Rewrite-1.1.9#cancelling)).
A request resolves with its answer as R writes it, every vector as an array, a length-one vector included, so that a module reads a single value as `answer[0]` ([Block classes in R](Rewrite-1.1.5#requests)).
A request that fails rejects with the reply's status and conditions, or with the statuses of the inputs that could not be evaluated, and one that R reports progress for calls `progress`, as a plugin's does ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
A download is a request whose answer is a file, which resolves with a `File` carrying the name the reply gives, for the module to hand the browser, as blockr.io's download block builds its file and its timestamped name in R on each click today ([R/download.R#L80-L92](https://github.com/BristolMyersSquibb/blockr.io/blob/9d8a10142777ae86bbde400c91ce6e4c20f515b7/R/download.R#L80-L92)), and a renderer offers one through a request of its output class (below).
Core keeps the answers for one opening of the board, shared by every block of the class, by registry id, name, args, the board option values sent and the revisions read: it merges a request with an identical one in flight and drops an answer once the revisions it read are superseded.
Core keeps no superseded answer, since no host method hands one out, and a module keeps the last answer it got on screen while it asks again.
An answer is a snapshot that never goes stale for its key, so nothing refetches it, while the answer of a request its class marks volatile, such as a directory listing, is never kept, and core needs no query library such as TanStack Query, which refetches data that changes behind the client's back.
A request that its class makes with `new_block_request(action = TRUE)` acts rather than reads: R runs it once per call and it may write, so core never keeps or merges its answer, and on a locked board R runs it only for a block that the board lock leaves open ([Block classes in R](Rewrite-1.1.5#requests), [Wire protocol](Rewrite-1.1.9#locked-boards)).
A write block's manual save is its button's one-time evaluation with a parameter, `evaluate({ save: true })`: the write block's `block_eval()` method runs the block expression, which holds the write, only in auto mode or with `save`, and signals `invalid()` otherwise, so that no later upstream change rewrites the file, as today's write block writes only per click ([R/write.R#L266-L307](https://github.com/BristolMyersSquibb/blockr.io/blob/9d8a10142777ae86bbde400c91ce6e4c20f515b7/R/write.R#L266-L307)), while an exported script, which runs the block expression, writes it ([Block classes in R](Rewrite-1.1.5#evaluation)).
An upload is an action that receives the file the user picked, keeps it where its package decides and returns the path that the module submits into the block's state, as blockr.io's read block keeps uploads under `blockr_option("upload_path")` today ([R/read.R#L332-L371](https://github.com/BristolMyersSquibb/blockr.io/blob/9d8a10142777ae86bbde400c91ce6e4c20f515b7/R/read.R#L332-L371)).

A board option's UI, or the renderer that replaces it, gets an `OptionHost`, which reaches R through the board option's own requests, which the package that ships it registers in R under the board option's id, as blockr.io's data directory board option checks and lists the server's directories today ([R/data-dir.R#L50-L124](https://github.com/BristolMyersSquibb/blockr.io/blob/9d8a10142777ae86bbde400c91ce6e4c20f515b7/R/data-dir.R#L50-L124)), and an output's renderer ([Drawing the board](Rewrite-1.1.8#renderers)) gets an output host:

```ts
interface OptionHost<V extends Json = Json> {
  readonly option: OptionId;
  value(): V;                                        // the board option's value in the board, or else its default, which core resolves before render()
  on(event: "value", fn: () => void): () => void;
  submit(value: V): Promise<void>;                   // runs core's command that sets a board option
  request<T = Json>(name: string, args?: Record<string, Json>, opts?: HostRequestOpts): Promise<T | Blob>;   // a request of the board option, never cached
}

interface OutputHost {
  readonly block: BlockId;
  output(): Json;                                    // the output it holds, which its block class's coercion made from the block's result
  body(): Blob | null;                               // the binary body it came with, if any, such as a plot's PNG
  params(): Json;                                    // the parameters the output it holds was made with, such as a table's page and sort
  options(): Record<OptionId, Json>;                 // the values of the board options its module names, which the output it holds was asked with
  loading(): boolean;                                // whether core is asking R for a newer output
  error(): Condition | null;                         // why the latest ask failed, while output() keeps what it held
  on(event: "output", fn: () => void): () => void;
  setParams(params: Json): void;                     // asks R for an output made with these, which params() returns once it arrives
  request<T = Json>(name: string, args?: Record<string, Json>, opts?: HostRequestOpts & { scope?: "class" | "renderer" }): Promise<T | Blob>;   // a request of its output class, or with scope "renderer" of the renderer, run with the result the output was made from
  emit(name: string, payload: Json): void;           // reports what the user did on the output, such as a selection, for an extension to act on
  draw(el: HTMLElement, key: string, output: Json, body?: Blob): Nested;   // draws an output nested in this one, with the renderer R names in it
}

interface Nested {
  update(output: Json, body?: Blob): void;           // hands the nested renderer a new output without mounting it again
  remove(): void;
}
```

An output carries in its `renderer` the renderer that draws it, with its id and where R serves its module, as `{ "renderer": { "id": "blockr.core-table_output", "module": "blockr.core/js/basic-table.js?v=b7e2a915" }, ... }` does, and core loads that module before it asks R for a block's first output where the block registry entry names the renderer, and otherwise the first time an output names it, and draws the output with it ([Drawing the board](Rewrite-1.1.8#renderers)), so that an app changes how every table looks, as with a UI kit's renderer, without touching a block class.
Core mounts a renderer once it has an output for it, keeps the last output drawn while the next loads, with `loading()` true, and hands the renderer an output that failed in R through `error()`, keeping it mounted with the output it holds, so that a renderer only ever draws an output it has and can ask again, as one whose parameters asked for a page that no longer exists must.
Core shows the error in the element itself only where no output came before it.
It keeps the last output drawn whatever the block's status, which the front-end reads to decide what an output that is not current looks like ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
Core asks R for an output and draws it again when the block's revision, a board option that its renderer names, the output's `info` or its parameters change, while the block is `ready`, and otherwise keeps the last output as drawn until it is ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins), [Evaluation in the client](Rewrite-1.1.10#scheduling)).
The `info` is what core measures for the output's element, its size, pixel ratio, colours and font, so that a plot is drawn again at a new size or on a display of another density, and a switch between light and dark redraws every plot on screen ([Block classes in R](Rewrite-1.1.5#outputs)).
It keeps each block's last output with the revision, board options, `info` and parameters it was asked with, so that an output mounted again under the same ones, as when a panel reopens, draws without asking R.
An output's parameters have the shape its output class's contract gives, as its fields do ([Block classes in R](Rewrite-1.1.5#outputs)), since the class's coercion in R reads them and any renderer of the class sets them, so that a UI kit's table and core's plain table page and sort through the same parameters.
A nested output comes within its parent's, made by the parent's coercion, so it is fetched, sized and kept with its parent and unmounts with it, and a nested renderer's parameters are the entry under its key in its parent's, which its `setParams()` replaces and `remove()` drops, as the table in blockr.dm's view of a dm keeps its page and sort beside the dm's selected table.
Core keeps them per block for one opening of the board, beside the block's status, so that a panel mounted again keeps its page and sort, while the board holds none of them, so that nothing of them is saved or undone, as blockr.dm's table output keeps its table, page and sort in the Shiny session today ([R/dm-block.R#L504-L560](https://github.com/BristolMyersSquibb/blockr.dm/blob/4e2191a9a99bafd0a60f8b8ee301c9f9c3e7b8ee/R/dm-block.R#L504-L560)).

A renderer reports what the user does on an output, such as selecting a bar of a chart, through `emit()`, in the shape its output class's contract gives, and changes nothing itself, so that an extension may hear it through `CoreApi` and edit the board with commands ([Plugins](Rewrite-1.1.12#running-a-plugin)).
Drill-down is built that way: a selection sets the clicked block's state, so that it shapes the block's result and reaches what is linked downstream, or another block's, such as a cohort filter upstream, which is external control rather than a link, since a link there would close a cycle, as blockr.viz sends such a claim over a channel of its own today ([R/ctrl-send.R#L1-L27](https://github.com/BristolMyersSquibb/blockr.viz/blob/332ce573ffafa86f5a41dc400b0f85e6800128f7/R/ctrl-send.R#L1-L27)).
[Client-drawn dock and extensions](Rewrite-1.2) takes the extension up, and a link of its own for such edits is in the [Backlog](Backlog#control-links).

A renderer asks R for what its output does not hold through the requests of its output class, which the package that defines the class registers in R ([Block classes in R](Rewrite-1.1.5#outputs)), such as a download of what it shows, as blockr.viz's tables offer the frame on screen as xlsx, HTML and pptx today ([R/table-download.R#L3-L11](https://github.com/BristolMyersSquibb/blockr.viz/blob/332ce573ffafa86f5a41dc400b0f85e6800128f7/R/table-download.R#L3-L11)).
A renderer that a package declares beside a class's default may also bring requests of its own, which its package declares with it, for what it alone offers, such as the labels of a table's columns, which core's table output does not carry.
It calls those through `request()` with `{ scope: "renderer" }`, where the default, `"class"`, calls a request of the output class, so that the request names the renderer and R finds the function among that renderer's requests alone ([Wire protocol](Rewrite-1.1.9#requests)).
The host sends such a request with the block and revision of the output it holds and the board options and parameters that output was asked with, so that R runs it with the result the output was made from, as it runs the coercion ([Wire protocol](Rewrite-1.1.9#requests)), and with a file where the renderer sends one, such as the bitmap the browser drew of a chart, for R to write into a PowerPoint file, as blockr.viz's chart block posts it to R today ([R/chart-block.R#L1883-L1887](https://github.com/BristolMyersSquibb/blockr.viz/blob/332ce573ffafa86f5a41dc400b0f85e6800128f7/R/chart-block.R#L1883-L1887)).
While the block reads `stale` or `unevaluated`, the host holds such a request.
Once core holds the output of the block's current revision, the host sends the request for that output, so a download clicked on a greyed-out table is of the result being computed.
Where the block reads `failed`, `invalid` or `waiting`, no result is in sight, and the host rejects the request at once with the block's status.
Core keeps an answer as it keeps the output, unless the class marks the request volatile, which a renderer's own request never is, and no such request writes, so a renderer still changes nothing itself.

Only what core mounts inside a front-end's layout, written by another package, gets a host narrowed to one thing: a block's UI, a board option's UI or renderer, and an output's renderer.
A front-end, which draws the whole board, its stacks and links included, gets `CoreApi`, as a startup module does, so core makes no host for a stack or for the board.
A front-end that mounts other packages' UI itself, such as on its stacks, narrows `CoreApi` for it in the same way, and keeps what that UI should save in a property of its board class, keyed by stack id ([Board updates](Rewrite-1.1.2#board-classes)), as in this host for a note on each stack:

```ts
// in the front-end's package, whose board class adds the property stack_notes
const stackHost = (core: CoreApi, id: StackId) => ({
  stack: () => core.store.board().stacks[id],
  note: () => core.store.board().stack_notes?.[id],
  on: (fn: () => void) => core.store.subscribe(fn),
  // and a way to write the note, through the command its package registers for it, as one undo step
});
```

### Startup modules

A package may declare in R one startup module ([Drawing the board](Rewrite-1.1.8#what-a-package-declares-in-r)), for what has to run before anything mounts: registering the board options it ships ([Board options and blockr options](Rewrite-1.1.13#defining-a-board-option)), defining its board classes, and registering the migrations of its block classes' states and its commands ([Board updates](Rewrite-1.1.2#board-classes)), putting on the page what it shares with other packages' modules, such as a UI kit's stylesheet, and naming a board to open in place of the one R sent, such as the board a URL names for session management ([Drawing the board](Rewrite-1.1.8#starting-the-page)).
The module exports the JS API major and a default with `initialize()`, after AFM's, which runs once before any view renders, and core calls it with `CoreApi`, as it calls a front-end's `render()` ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)):

```ts
export const api = 1;                                // the JS API major it was built against

export default {
  initialize({ core, signal }: { core: CoreApi; signal: AbortSignal }): void | Promise<string | void> {
    core.options.register(dataDir);                  // a board option it ships, such as blockr.io's data directory
    core.store.register(dockBoard);                  // a board class, with the properties it adds, such as the dock's
    core.store.registerMigration("blockr.dplyr-filter_block", migrateFilter);   // a block class's migration of its state
    core.commands.register(relayout);                // a command, such as the DAG's relayout
    // it may also resolve with a JSON board's text, which core opens in place of the board R sent
  }
};
```

R sends the startup modules of the packages that the app names with the block registry's entries, in its reply to `hello` ([Block classes in R](Rewrite-1.1.5#registration)), and keeps them in the order of the packages' dependencies, which their DESCRIPTION files give, so that each package's comes after those of the packages it imports, and in the order the app names them otherwise.
Core imports and initializes them one at a time in that order, awaiting each `initialize()`, since a module's imports run as it loads, so that what a package sets up is in place before the module of a package that depends on it loads.
It does so before the front-end mounts and before the store opens the board R sent, so that the store finds every board class defined and every board option registered.

Core initializes each package's startup module as each board opens, since opening a board starts core again ([Drawing the board](Rewrite-1.1.8#opening-a-board)), with a new `CoreApi` and a signal that aborts as the next board opens, and skips it when a later reply of the same opening names the package again.
A reply that names a package at another version than the one loaded, as after R restarts with the package reinstalled, makes core ask for the page to be reloaded rather than load a second copy.
A startup module that fails to load or throws in `initialize()` is named in an error, and core carries on with the rest, so the board opens without what that package registers, as without the properties of a board class that no loaded package defines ([Board updates](Rewrite-1.1.2#board-classes)).

A package relies on the order only for the packages it imports, which is what a module needs as it loads, such as a library on another package's global.
Between any other two packages the order is unspecified, and core keeps what they share independent of it:

- A startup module registers and subscribes in `initialize()`, and looks up what other packages registered when it uses it, as a key's `expand` runs per delta and a command's `run()` per command.
  It reads no board there, since none is open at startup.
  It keeps nothing of a board at module scope, since its module loads once per page while core initializes it again with each board, and keeps what it needs for a board within `initialize()`, which ends with its signal ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).
- Ids carry their package, and a board option id, which does not, fails when another package has registered it, naming both ([Board options and blockr options](Rewrite-1.1.13#defining-a-board-option)).
- Every startup module runs once R has replied and before the store migrates or drops anything, since the store awaits what core runs then through the `loaded` it is created with ([Board updates](Rewrite-1.1.2#the-store)), and so before the store announces the board ([Board updates](Rewrite-1.1.2#following-the-board)) and before the front-end reads what packages registered, such as the commands in its menus.
  Only a startup module that runs as the page starts may name a board to open, and core ignores a board that one names as a later board opens, since that opening names its own.
- A stylesheet loads with its module, so a UI kit's, beside its startup module, is in place before those of the packages that import the kit, which use its classes and refine them in their own CSS, loaded later.
  A stylesheet styles only classes under a prefix of its package's own, so packages that don't know each other never style the same element, and a theme restyles every package through the kit's custom properties, and core's through the variables of its Tailwind theme ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).

### React

A module written in React imports `react` as any React code does, and its build maps `react`, `react-dom` and entry points such as `react/jsx-runtime` to the one copy that core puts on the page, so the module's bundle holds no React, as WordPress's build plugin maps `react` to the global `React` ([README](https://github.com/WordPress/gutenberg/blob/debb46ec9c901b95e31f8c420ef93dd61054f497/packages/dependency-extraction-webpack-plugin/README.md)) and Grafana builds plugins with `react`, `react/jsx-runtime` and `react-dom` as [externals](https://github.com/grafana/plugin-tools/blob/2115b27767554a555640300c7b4dc9c9e1842909/packages/create-plugin/templates/common/.config/bundler/externals.ts#L19-L22).
React reaches the module through its build rather than through the host, since React libraries import `react` themselves, often as they load, as TanStack Query calls `createContext()` at the top of a module ([QueryClientProvider.tsx#L9](https://github.com/TanStack/query/blob/9e4253766f8015d1372bcd515f50103fd067a42d/packages/react-query/src/QueryClientProvider.tsx#L9)), while the host arrives only once the module renders.
Core's runtime puts the copy on a global of its own as it loads, before core imports any startup module or other module, so that the copy is in place before any module that imports React loads, and a package needs no import of its own to find it.
The global is core's rather than `window.React`, which may be taken already: reactR's dependency loads React's UMD build, which sets it ([R/dependencies.R#L35-L48](https://github.com/react-R/reactR/blob/808b21f4f2e5c374cb8ec910f8e2cc27f6b40e1b/R/dependencies.R#L35-L48)).
Core ships the mapping as a build preset, which a package's build uses as core's own does.

Core draws its own UIs with React, written as TSX: those of its built-in blocks, its renderers, its board options and its basic front-end, so that they are written as the dock, its extensions and the UIs of packages are ([Client-drawn dock and extensions](Rewrite-1.2)).
React's major moves with core: core takes a new major of React only with a new major of its JS API, so that it refuses a module built against the old one rather than let it fail as it renders.
Core ships the React SDK beside the copy: hooks over the hosts, which read like shinyreact's `useShinyInput()` and `useShinyOutputValue()` ([index.ts](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/pkg-js/src/shiny-react/index.ts)), such as `useOutput()` for what an output's host holds, and the inputs that core's own UIs draw with, which the UI of a package may use too.
The hooks and the inputs keep the contract's rules for a value that a control shows and submits ([The contract](#the-contract)), which core also offers without React, for a module in plain TypeScript, so that a UI meets the contract alike whatever it is written in.

### Packaging

A block class's UI is an ES module in its package's `inst/`, written against the types core ships inside blockr.core.
Core loads JS only and compiles nothing, so a package either writes its modules in JS, as blockr.dplyr and blockr.ggplot write theirs today with no build step, type-checked through `// @ts-check` ([tsconfig.json](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/bdac6b38f7097425bfe96883032531cc919f6ee7/tsconfig.json)), or builds them from TypeScript or TSX and commits what it builds, since R CMD check and CRAN run no Node, as shinyreact keeps the bundle it builds in its R package ([README.md#L63](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/README.md#L63)) and its apps write a `ui.tsx` ([README.md#L18-L22](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/README.md#L18-L22)).
Core's runtime ships inside blockr.core as one bundle, with the one copy of React, as shinyreact ships its runtime inside its R package ([README.md#L46](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/README.md#L46)), and nothing is published to npm for now, so a package builds against the types of the installed blockr.core, which its build resolves as `@blockr/core`, whose `Board` interface a board class extends to type its properties ([Board objects](Rewrite-1.1.1#extending-cores-objects)).

In R, a block class names its UI in its `ui` field with `js_module()`, which keeps the module's path in its package's `inst/` and the package, for R to resolve when it serves the module ([Block classes in R](Rewrite-1.1.5#the-block-class)), and a package declares the modules it offers others and its renderers ([Drawing the board](Rewrite-1.1.8#what-a-package-declares-in-r)), each under a name that gives it an id, `{pkg}-{name}`, as a registry id is.
R tells the client where each module is served, with the block registry's entries, when the client connects and whenever a board opens ([Block classes in R](Rewrite-1.1.5#registration)), and the client imports each URL once and loads the CSS beside a module with it.
R serves each module and stylesheet at a URL that holds a hash of its content, so that a changed file is never read from a browser's cache, as blockr.io bumps its path field's asset version by hand today so that users do not keep running the old file ([R/path-input.R#L387-L396](https://github.com/BristolMyersSquibb/blockr.io/blob/9d8a10142777ae86bbde400c91ce6e4c20f515b7/R/path-input.R#L387-L396)).
A module of another package is reached through `host.module()` by its id, along the R dependencies, as blockr.dm reuses blockr.dplyr's filter UI today through its HTML dependency ([R/dm-filter-block.R#L173-L191](https://github.com/BristolMyersSquibb/blockr.dm/blob/4e2191a9a99bafd0a60f8b8ee301c9f9c3e7b8ee/R/dm-filter-block.R#L173-L191)).

A block class defined outside a package names a plain JS module by its path, which `js_module()` resolves against the working directory there and R serves once the script has registered the class, as it serves a package's modules, while a file holds none of it ([Board objects](Rewrite-1.1.1#block-classes-outside-a-package)).

What a module ships beside it sits in its folder under its name, so that `head-block.js` has its stylesheet in `head-block.css` and its JSON Schema in `head-block.schema.json`, which R serves or reads with it, and R names every module to the client with the URL of its stylesheet where it has one.
A block class's module ships the JSON Schema of the block's state beside it, which a package that builds from TypeScript can write once, such as with Zod, whose `z.infer` gives the module its type and `z.toJSONSchema()` the schema ([Zod](https://zod.dev/json-schema)).
R reads the schema when it registers the class, writes the state of the blocks it builds by it ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)), and sends it with the class's entry in the block registry, so the client has it before the module loads.
A package ships the JSON Schemas of the properties its board classes add and of the board options that it registers beside the startup module that defines and registers them, in the same way, each property's by its class and name and each board option's by its id, by which R writes their values ([Board updates](Rewrite-1.1.2#board-classes), [Board options and blockr options](Rewrite-1.1.13#defining-a-board-option)).

### Testing

Core ships a stub of each host inside blockr.core, beside its types, so a module mounts in a test runner with a state, requests answered from fixtures, and a record of what it submitted, needing neither R nor a browser, as blockr.dplyr tests its JS today with `node --test` and happy-dom ([package.json](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/bdac6b38f7097425bfe96883032531cc919f6ee7/package.json)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

An element that has left the page measures 0 by 0, as dockview warns of a hidden panel under its default renderer ([rendering.mdx#L18-L21](https://github.com/mathuo/dockview/blob/27a42c314a06ebc37f288d6d181d01b6cb84cd7a/packages/docs/docs/core/panels/rendering.mdx#L18-L21)), so `mountOutput()` asks R for no output while its element measures nothing, and asks again once it measures a size.

Only running the startup modules and their `initialize()` follows the order, so core can fetch every one at once, such as with `<link rel="modulepreload">`.
R orders them by the dependencies that the installed DESCRIPTION files of the packages the app names give, which it reads without loading a package, and by the order the app names them where those leave two packages unordered.

R serves the module of a class defined outside a package at a URL of its own, read from the path the script gave, as it serves a package's modules, so that the client imports every module alike, and a page whose content security policy forbids `blob:` scripts loads it too.

An import map, which would let a module import `react` with no build step, was weighed for shinyreact and not chosen: injecting one is fragile with the order in which htmltools assembles the page head, and Vite's dev server does not resolve bare specifiers against a page's import map ([js-distribution decision](https://github.com/posit-dev/shinyreact/blob/e8812353d5f076f6e98a27a7e210d0a3e177ea1d/decisions/2026-08-17-js-distribution.md)).

</details>
