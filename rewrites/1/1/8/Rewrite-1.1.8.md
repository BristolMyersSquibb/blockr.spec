# Drawing the board: `CoreApi`, the page, core's basic frontend and renderers
Status: settled on 2026-11-07. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): what core gives every plugin through `CoreApi`, how the page starts and opens a board, core's basic frontend, and renderers.
It builds on the [board objects proposal](Rewrite-1.1.1) and on the [board updates](Rewrite-1.1.2), evaluation ([Evaluation in the client](Rewrite-1.1.10)), UI modules ([UI modules in JS](Rewrite-1.1.7)) and plugins ([Plugins](Rewrite-1.1.12)) proposals, and shapes removing the generics that draw UI from R ([blockr.core#418](https://github.com/BristolMyersSquibb/blockr.core/issues/418)), the toolchain of core's client ([blockr.core#419](https://github.com/BristolMyersSquibb/blockr.core/issues/419)), what a package declares in R ([blockr.core#424](https://github.com/BristolMyersSquibb/blockr.core/issues/424)), renderers ([blockr.core#425](https://github.com/BristolMyersSquibb/blockr.core/issues/425)), the requests of the per-session evaluator ([blockr.core#430](https://github.com/BristolMyersSquibb/blockr.core/issues/430)), the UIs of core's built-in blocks ([blockr.core#438](https://github.com/BristolMyersSquibb/blockr.core/issues/438)), core's renderers and board options ([blockr.core#439](https://github.com/BristolMyersSquibb/blockr.core/issues/439)), `CoreApi` and starting the page ([blockr.core#440](https://github.com/BristolMyersSquibb/blockr.core/issues/440)), core's basic frontend ([blockr.core#441](https://github.com/BristolMyersSquibb/blockr.core/issues/441)), serving a board ([blockr.core#442](https://github.com/BristolMyersSquibb/blockr.core/issues/442)), what core exports for end-to-end tests ([blockr.core#443](https://github.com/BristolMyersSquibb/blockr.core/issues/443)), starting core again as a board opens ([blockr.core#497](https://github.com/BristolMyersSquibb/blockr.core/issues/497)), filling the block registry from the block classes that the app offers ([blockr.core#498](https://github.com/BristolMyersSquibb/blockr.core/issues/498)), a plugin's requests ([blockr.core#505](https://github.com/BristolMyersSquibb/blockr.core/issues/505)), making the frontend a plugin and running the board's plugins ([blockr.core#506](https://github.com/BristolMyersSquibb/blockr.core/issues/506)), saving, opening and placing plugins in core's basic frontend ([blockr.core#507](https://github.com/BristolMyersSquibb/blockr.core/issues/507)) and keeping the defaults of board options beside the board ([blockr.core#508](https://github.com/BristolMyersSquibb/blockr.core/issues/508)), each an item in the Work list of [Client-owned board state](Rewrite-1.1#work).
What a plugin is, the frontend and the storage plugin among them, and which plugins a board has are [Plugins](Rewrite-1.1.12)'s, and the places the dock offers plugins, such as its panels, are [Places the dock offers plugins](Rewrite-1.2.4)'s.
The plugin that adds, changes and removes blocks, links and stacks under every frontend is [The Edit board plugin](Rewrite-1.1.15)'s.

## What must hold

1. Core ships a basic frontend that draws any board, so a board serves without blockr.dock, and a frontend replaces it entirely, so that none of it runs underneath another, as core's stack generics run underneath the dock today.
2. A frontend draws everything around a block, its card, panel, menus and status, while core mounts the block's UI and output, so a block class works in every frontend.
3. A frontend and every other plugin work on the board only through core's JS API: the store, commands, demand, statuses and requests.
4. Nothing in R draws or redraws UI.
5. Any package can supply a renderer for an output class or a board option.
   An app replaces an output class's default renderer, or a board option's UI, with such a renderer through a blockr option, with no change to a block class.
6. Unless the load lock is on, the app's storage plugin can open another board in place of the opening board before anything is drawn or evaluated, as `rack_loader()` resolves the board a URL names before today's page is drawn.
7. Opening a board leaves the page as opening that board in a fresh app would, its frontend and its other plugins included, and with no reload ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).

## Today

Core's frontend is `board_ui.board()`: a toolbar of its plugins with a popover of board options, a bslib accordion of stacks and a bslib card per block, whose header and footer the `edit_block` plugin draws ([R/board-ui.R#L40-L140](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-ui.R#L40-L140)).
It computes a block's status without drawing it, and shows conditions as notifications ([R/plugin-notification.R#L76-L140](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-notification.R#L76-L140)).
It parks the blocks of collapsed stacks through `gate_stacks()`, the default `callbacks` of `board_server()`, so a stacked board is lazy under it ([R/board-server.R#L143-L158](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L143-L158)).
A frontend replaces it by implementing generics that dispatch on the board, `board_ui()`, `block_ui()`, `insert_block_ui()`, `remove_block_ui()` and more, and by passing `callbacks` of its own: blockr.dock implements those four and `blockr_app_ui()` and `blockr_app_server()`, through which it passes its callbacks ([blockr.dock R/utils-serve.R#L64-L86](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/utils-serve.R#L64-L86)), but none of the stack generics, which still fire underneath it ([R/stack-ui.R#L37-L255](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/stack-ui.R#L37-L255)).
The board's class also picks the page: `serve()` builds it with `blockr_app_ui()` for the board its loader returns at each request, and a restore stages the restored board and reloads the page, so a core board restored in a dock app brings core's UI along ([R/utils-serve.R#L227-L288](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L227-L288)).
The dock's extensions hook in through `new_dock_extension()` and `extension_block_callback()`, which the DAG uses to draw status badges ([R/ext-class.R#L52](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/ext-class.R#L52), [blockr.dag R/ext.R#L521-L583](https://github.com/BristolMyersSquibb/blockr.dag/blob/68869c56f83a0ec0c4987c75e9a1c07a46cf529b/R/ext.R#L521-L583)).
Insertions and removals reach the page through R, and the dock's removal currently misses: the selector it passes to `removeUI()` is built from the board's id instead of the block's and lacks the `#`, so it matches no element, as [blockr.dock#527](https://github.com/BristolMyersSquibb/blockr.dock/issues/527) reports ([R/block-ui.R#L104](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/block-ui.R#L104)).

## Proposal

### What core gives plugins

Core gives one `CoreApi` to the module of every plugin, a frontend's among them, as it calls the module's `render()`, to every plugin class's `start`, to the `storage.load()` of the app's storage plugin and to a board option's `default` that is a function, and a plugin works on the board through it alone ([Plugins](Rewrite-1.1.12#running-a-plugin), [UI modules in JS](Rewrite-1.1.7#modules-of-plugin-classes-and-board-options)):

```ts
interface CoreApi {
  store: Store;                    // board(), subscribe(), apply(), open(), from Board updates
  commands: Commands;              // run(), plan() and the command registry, for menus and shortcuts
  scheduler: Scheduler;            // demand(), evaluate(), invalidate(), status() and subscribe() alone, from Evaluation in the client
  blockRegistry(): BlockRegistry;  // the block registry's entries by registry id, for pickers, which change as another board opens
  options: Options;                // register(), the board options packages define, by id, value(), the board's value or else its default, and inUse(), those that something on the page requires or that the board holds a value for
  plugins: {                       // from Plugins
    register(def: PluginClass): () => void;        // a plugin class, as core registers each one that the reply names
    appPlugins(): Record<PluginClassId, Plugin>;   // the app's plugins whose classes are registered, each under its class's id with its name
    pluginClass(plugin: PluginClassId): PluginClass;   // the definition of the class of one of the app's plugins
    storage(): Storage | undefined;                // the app's storage plugin's, or undefined where the app holds none
  };
  lock: { board: boolean; load: boolean };   // whether the app sets the board lock and the load lock, from the reply to hello
  outputEvents: OutputEvents;      // what renderers report the user did, such as a selection, for plugins to act on
  notifications: { notify(plugin: PluginClassId, n: Raised): () => void; get(): readonly Notification[]; subscribe(fn: (all: readonly Notification[]) => void): () => void };   // every notification of the open board, which the frontend draws, from Notifications, logging and tracing
  log(pkg: string): Log;           // log lines that name the package, from Notifications, logging and tracing
  focus: { get(): BlockId | null; set(block: BlockId | null): void; subscribe(fn: (block: BlockId | null) => void): () => void };   // which block has focus, which the frontend sets
  request<T = Json>(plugin: PluginClassId, name: string, args?: Json, opts?: RequestOpts): Promise<T | Blob>;   // a plugin's request, by its class's id, as Plugins has it
  module<T = unknown>(id: string): Promise<T>;                // a module another package offers, by id
  blockrOption<T extends Json>(name: string, fallback: T): Promise<T>;   // a blockr option, asked of R once per page, or fallback where R has none
  mountBlock(el: HTMLElement, block: BlockId): () => void;    // the block's UI module
  mountOutput(el: HTMLElement, block: BlockId): () => void;   // its output, measured, fetched and drawn by the renderer R names in it
  mountOption(el: HTMLElement, option: OptionId): () => void; // a board option's UI, or the renderer the app names for it
  mountPlugin(el: HTMLElement, plugin: PluginClassId): () => void; // a plugin's UI module, where a frontend places the plugin
}

interface RequestOpts {
  reads?: BlockId[];                                         // the blocks it reads, which core has evaluated first
  signal?: AbortSignal;                                      // cancels it, as a cancel does on the wire
  file?: File;                                               // a file it sends, which R hands the function in its argument file
  progress?(note: { value?: number; message?: string }): void;   // each progress note R sends for it
}

interface OutputEvents {
  subscribe(fn: (event: { block: BlockId; name: string; payload: Json }) => void): () => void;   // each event a renderer emits ([UI modules in JS](Rewrite-1.1.7#the-contract))
}

```

A frontend decides where things go and core fills them: it gives `mountBlock()` the body of a card or a panel, and core mounts the block's UI module there, so the dock's card sections stay the dock's business while what is in them stays core's.
A frontend may mount a block's UI or output in several places at once, such as two panels of one view, and mount it again as its panels move or reopen, since everything a mount draws from is core's and none of it is lost when a mount ends ([UI modules in JS](Rewrite-1.1.7#the-contract)), rather than moving one element around, as the dock parks each card in its offcanvas today and carries it into a panel and back ([blockr.dock R/block-ui.R#L188-L295](https://github.com/BristolMyersSquibb/blockr.dock/blob/fd806ec45fd7158c32ae13b59cdca9386f34a985/R/block-ui.R#L188-L295)).
Two mounts of one output share its parameters, which core keeps per block, so both show the same page and sort.
Which of a block's sections a frontend shows is its own to keep in its state, as the dock keeps which sections of each card show ([Locked boards and the properties of blocks](Rewrite-1.1.11#what-a-plugin-keeps-about-a-block)), while on a locked board it mounts the UI only of a block that the board lock leaves open, as `store.locked()` says ([Board updates](Rewrite-1.1.2#the-store)).
The `mountOutput()` call measures its element for the output's `info`, asks R for the output unless core kept one asked with the same revision, board options, `info` and parameters ([UI modules in JS](Rewrite-1.1.7#the-contract)), draws it with the renderer R names in it (below), and redraws it when the block's revision, a board option that its renderer names, the `info` or the output's parameters change, while the block is `ready` ([Evaluation in the client](Rewrite-1.1.10#scheduling)).
A frontend draws a block's status, conditions and summary from `scheduler.status()`, and decides from the status what an output that is not current looks like, leaving it as it is, greying it out or hiding it, since core keeps drawing a block's last output whatever the block's status ([Evaluation in the client](Rewrite-1.1.10#statuses)).
It demands the blocks it shows, above the default evaluation priority ([Evaluation in the client](Rewrite-1.1.10#demand)), and follows the board through `store.subscribe()`, so a removed block's card goes away because the board changed, not because R said so.
It draws no control for what a lock fixes, as `lock` and `store.locked()` say ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)), and plugins reach R through `request()`, each through requests of its own, as code export and session management do ([Plugins](Rewrite-1.1.12#a-plugins-requests)).

A frontend places each plugin whose class has a `ui` as it places a block: it gives `mountPlugin()` an element of its choosing, and core mounts the plugin's module there ([Plugins](Rewrite-1.1.12#plugin-classes)).
Through `plugins` it reads which plugins run and what their classes give, and reaches the open board's storage, while plugins reach it through `notifications` and `focus` ([Plugins](Rewrite-1.1.12#what-a-frontend-offers-other-plugins)).

### Starting the page

Core starts the page once R replies to `hello`: it imports every module that the reply names and registers what each exports under its id ([UI modules in JS](Rewrite-1.1.7#modules-of-plugin-classes-and-board-options)), asks the app's storage plugin for a board to open in place of the one R sent (below), opens that board or R's, which runs the app's plugins ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)), and only then starts the scheduler and calls the frontend's `render()`, with what the reply to `hello` holds in `frontend` ([Plugins](Rewrite-1.1.12#the-frontend)), so nothing is evaluated or drawn before every plugin class and board option is registered ([blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)).
The scheduler sends nothing to R until `render()` has returned, or resolved where it is async, so a frontend demands what it first shows within `render()`, from the board, rather than from an effect that runs once it has drawn, as a React app's would, and those blocks are evaluated first ([Evaluation in the client](Rewrite-1.1.10#scheduling)).
Core then calls `start` for each of the app's plugins whose class has one, so that what the frontend first shows comes before what the plugins ask for as they start ([Plugins](Rewrite-1.1.12#running-a-plugin)).
A frontend's package lists its plugin class in R, whose module holds the class with its commands ([Plugins](Rewrite-1.1.12#a-plugin)), and subscribes to the store from its plugin's `start()` where it needs to follow the board, which runs once the board has opened ([Board updates](Rewrite-1.1.2#following-the-board)), while the frontend's `render()` only draws.
What the store dropped as the board opened reaches the frontend as a notification, which it reads as it draws ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)).

The app's storage plugin may resolve its class's `storage.load()` with the text of a JSON board, as session management's does with the board a URL names ([Session management as a storage plugin](Rewrite-1.6)), and core then opens that board instead of the one R sent ([blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)).
Core calls it once, as the page starts, after it has registered the app's plugin classes, and neither as a later board opens, nor for a block that `serve()` serves alone, nor under the load lock, which fixes the app to its opening board, where core keeps the board R sent ([Locked boards and the properties of blocks](Rewrite-1.1.11#the-load-lock)), so nothing of the script's board is drawn or evaluated, while the page shows that it is loading, as today's page waits for `rack_loader()` ([Defining a board in R](Rewrite-1.1.3#the-opening-board)).
Core keeps the board R sent for a block that `serve()` serves alone too, which no frontend draws, and names no package there ([Defining a board in R](Rewrite-1.1.3#data-passed-to-serve)).
Should two resolve with a board, core opens the one R sent and names both packages.

### Opening a board

Opening a board starts core again in place, as the page starts (above), with no reload ([Principles](Principles#opening-a-board-leaves-the-page-as-starting-it-with-that-board-would)).
A plugin, a frontend among them, opens a board through `store.open()` ([Board updates](Rewrite-1.1.2#opening-a-board)), and core first checks the board as the store on the page would open it, so that a board it refuses leaves the page as it was, with the reason.
Core then ends everything it runs for the board with one abort: the frontend and what it mounted, every plugin that runs, the store with its undo history, the command registry and the plugin classes, the board options, the scheduler with its demands, which block has focus, and what core keeps of outputs and answers.
A module releases what it holds as its signal aborts, as it does when core unmounts it ([UI modules in JS](Rewrite-1.1.7#the-contract)), and core drops the rest, so that no part of core has a reset of its own.
Core then starts as the page does: its `hello` starts R's session afresh, so that R drops every result and request of the board before ([Wire protocol](Rewrite-1.1.9#opening-a-board)), and core registers what the modules export again, opens the board in a new store, draws it with its frontend (below) and starts its plugins.

Only what is fixed for the page outlives an opening:

- The code and stylesheets that have loaded, since a module loads once per page.
- The page's element, and the transport with its session.
- The protocol's client, so that no id names two requests.
- The blockr options that core has read, and the load lock and the board lock.
- The revisions given so far, so that the next scheduler gives a block id a revision above any it had, and a revision never goes back within the page ([Evaluation in the client](Rewrite-1.1.10#revisions)).

Which plugins run comes from the app's plugins, which R's reply to every `hello` holds, never from the board it replaces or from the board that opens, and a plugin of the app whose state the board that opens does not hold starts with its class's default state ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)), so nothing outlives an opening that way either.
A new session after the server ended the last opens no board: core keeps the board it holds, and the scheduler has the new session evaluate it again ([Evaluation in the client](Rewrite-1.1.10#scheduling)).

Opening a board starts core again, its frontend included, so the page draws the board that opens with a frontend that starts again, so that nothing it kept of the board before outlives the opening (above).
Every board that the app opens runs the app's frontend, so the page draws each with that frontend and never switches to another while a board is open, since no change adds or removes a plugin ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)).
So a board made in a core app opens in a dock app with the dock's default layout, where today's restore brings core's UI along.

### Core's basic frontend

Core's basic frontend is a plugin, which `new_basic_frontend_plugin()` makes and an app runs unless another available package gives a frontend ([Plugins](Rewrite-1.1.12#the-frontend)).
It does what today's frontend does wherever core's commands and store do the work, so that it only draws: a toolbar for setting the board options that something on the page requires or that the board holds a value for, renaming the board, and the controls of the app's storage plugin, such as saving the board and opening another; a section for the UI of each plugin that has one, beside the board on a wide page and above it on a narrow one, where it mounts the plugin's module ([Plugins](Rewrite-1.1.12#plugin-classes)); stacks as groups; and a card per block with its name, a menu to rename or remove it or add a block before or after it, its UI, its output and its summary, as today's has, and its status and conditions, which today's computes but does not draw on the card, showing the severities that core's `show_conditions` board option names, with the output greyed out while the block is not `ready`, where today's clears it ([R/block-server.R#L63-L66](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L63-L66)).
Adding a block from the block registry's entries and editing links and stacks belong to the Edit board plugin, which the basic frontend shows in a section, as it shows any plugin, and which `serve()` gives an app by default ([The Edit board plugin](Rewrite-1.1.15#what-serve-gives-by-default)).
The user collapses or expands each plugin's section, which hides the plugin's UI but leaves it mounted, so that the UI keeps what it holds outside the plugin's state, and the toolbar needs no button for each plugin ([blockr.core#544](https://github.com/BristolMyersSquibb/blockr.core/pull/544)).
It requires two board options, which it names in its `options`: `show_conditions`, for the severities that its cards show, and `dark_mode`, for the theme it draws in ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)).
On a locked board, its toolbar keeps undo, redo, the board options and the storage plugin's controls, which leave out opening another board under the load lock themselves, since no lock fixes the rest ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks), [Plugins](Rewrite-1.1.12#storage)).
It draws the controls that `core.plugins.storage()` gives at the end of its toolbar, each kind with its own buttons and menus, so that core's storage plugin shows Save, which saves a download, and Open, which opens an upload, as today's `preserve_board` plugin does, while it draws none where the app holds no storage plugin ([Plugins](Rewrite-1.1.12#storage)).
It also binds undo and redo to their shortcuts, which today's lacks, since the store keeps the steps and a frontend binds the shortcuts ([Board updates](Rewrite-1.1.2#undo)), gives a block focus as the user clicks into its card or moves the keyboard's focus into it, but not as the pointer hovers over it ([blockr.core#544](https://github.com/BristolMyersSquibb/blockr.core/pull/544)), and shows every notification, among them what the store dropped when a board opened, which edit the store refused and what plugins notify, as [Notifications, logging and tracing](Rewrite-1.1.14#cores-basic-frontend) has it.
Code export is blockr.code's plugin, which the basic frontend places in a section as it places any other ([Code export as a plugin](Rewrite-1.5)), and the basic frontend reads no member of a plugin class beyond core's, so that a plugin needs only its `ui` to show under it ([Plugins](Rewrite-1.1.12#plugin-classes)).

It shows every block, so it demands every block, and a board that it draws evaluates every block ([Evaluation in the client](Rewrite-1.1.10#demand)), where today's parks the blocks of collapsed stacks.
The user collapses or expands each stack's group of cards too, which leaves the cards mounted, and the browser counts them out of view, so the frontend's demand gives their blocks a lower priority ([blockr.core#544](https://github.com/BristolMyersSquibb/blockr.core/pull/544)).
It is written in React, as TSX, as core's built-in block UIs and renderers are, on the one copy of React that core ships, and it mounts a block's UI and a plugin's as any frontend does, whatever the module is written in ([UI modules in JS](Rewrite-1.1.7#react)).
It builds on Tailwind CSS rather than on blockr.ui's design system, which the dock follows, since blockr.ui builds on blockr.core ([State in JS](Rewrite-1#what-must-hold)), and so do the UIs of core's built-in blocks and its renderers, which show under every frontend.
Their stylesheets keep Tailwind's utilities under core's prefix, outside any cascade layer, so that a page's other CSS, such as Bootstrap, does not win over them ([blockr.core#448](https://github.com/BristolMyersSquibb/blockr.core/pull/448)), and leave out its reset of the whole page, so that nothing core loads styles another package's elements, the dock's included once the page has switched to it ([UI modules in JS](Rewrite-1.1.7#modules-of-plugin-classes-and-board-options)), and they take their colours, fonts and radii from the variables in which Tailwind CSS 4 keeps its theme, which a frontend or a UI kit may set to restyle them, as blockr.ui may under the dock ([UI kit and design system for the client](Rewrite-1.7)).

### Renderers

A renderer is a module that draws the outputs of one output class ([Block classes in R](Rewrite-1.1.5#outputs)) or a board option's value.
A renderer of an output class is written against the class's contract, which the package that defines the class ships: a JSON Schema of its outputs, by which R writes them, with their TypeScript type, such as core's `TableOutput` for table outputs; the types of the parameters its coercion reads, such as `TableParams`, of the events its renderers emit, if they emit any, such as a chart's selection, and of the args and answers of its requests, if it has any, such as a download; the board options its coercion reads, such as `n_rows`, which every renderer of the class requires ([Board options and blockr options](Rewrite-1.1.13#board-option-values-in-r)); and fixtures of sample outputs it is tested on, so that whoever builds another table knows what to draw and what to ask for.
An output class's renderer is the one that its method of `output_renderer()` gives, an S3 method that the package that defines the class writes beside its methods for the class's JSON Schema, coercion and requests ([Block classes in R](Rewrite-1.1.5#outputs)), as core's method for table outputs gives its plain table, `blockr.core-table_output`, and a board option has the `ui` its definition gives ([Board options and blockr options](Rewrite-1.1.13#defining-a-board-option)).
A renderer is an object that `new_renderer()` makes, with its module, its own requests and its id, `{pkg}-{name}`, which its module's package and its name give, as blockr.ui's table preview is `blockr.ui-table_preview`, and one module may stand behind several renderers.
Any package may offer other renderers, each through a function that makes it, for an output class or for a board option.
An app replaces a class's renderer, or a board option's `ui`, only by naming another renderer for it in the `renderers` blockr option, under the class's name or the board option's id, which a class's method takes with `chosen_renderer()`, so that a package's renderer draws nothing until an app names it, and loading its package changes nothing.
S3 dispatch gives each output the renderer of the most specific class in its class vector that has a method, so that the outputs of a subclass without one of its own are drawn by their class's renderer until the subclass's package, or the app script, gives it one, and the client mounts the renderer an output carries, so neither class vectors nor dispatch reach it ([State in JS](Rewrite-1#principles)).
Another package thus supplies a renderer that an app names, or extends the class with a subclass ([Block classes in R](Rewrite-1.1.5#outputs)).
R sends each output with its renderer, the renderer's id and where R serves its module, so that the client loads a renderer that no registry entry names the first time an output names it, and needs no list of renderers when it connects, while R sends the renderers that the app names for board options with its reply to `hello`, since a board option's UI mounts without an output ([Wire protocol](Rewrite-1.1.9#handshake)).
R also names the renderer of a block class's outputs in the class's registry entry, so that core resolves that renderer's board options before it asks R for the block's first output ([Board options and blockr options](Rewrite-1.1.13#the-renderer-before-the-first-output)).
So an app changes how every table looks, with a UI kit's renderer or another's, without touching a block class, as a JupyterLab extension replaces the renderer of a MIME type by registering its own ([registry.ts#L232-L258](https://github.com/jupyterlab/jupyterlab/blob/a877aee5ac6f490272a5ac18ac16b62b0deb1223/packages/rendermime/src/registry.ts#L232-L258)):

```r
# blockr.core: its table outputs, drawn by its plain table, blockr.core-table_output, unless the app names another
output_renderer.table_output <- function(x, ...) {
  chosen_renderer("table_output", new_renderer("table_output", js_module("basic-table.js")))
}

# blockr.ui: a richer table, blockr.ui-table_preview, with a request of its own for the columns' labels
table_preview <- function() {
  new_renderer("table_preview", js_module("table-preview.js"),
               requests = list(labels = function(result) lapply(result, attr, "label", exact = TRUE)))
}

# an app that wants blockr.ui's table: an output class, and the renderer
options(blockr.renderers = list(table_output = blockr.ui::table_preview()))
```

A renderer gets an output host, or for a board option an `OptionHost` ([UI modules in JS](Rewrite-1.1.7#the-contract)), through which it calls the requests of its output class, such as a download of what it shows, and its own, such as the labels of a table's columns.
A block's UI has no renderer, since it ships the schema of its block's state ([Serialization](Rewrite-1.1.4#state-values-between-the-client-and-r)), so a different UI makes a block class of its own, built from the properties of the block's ([Block classes in R](Rewrite-1.1.5#cores-classes-and-hooks)).
A renderer's module names the board options it requires, as core's table renderer requires `n_rows` ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)).

### What a package declares in R

Besides its block classes, a package declares in R the rest of its client that R serves or answers for, each under a name that gives it the id `{pkg}-{name}`, as a registry id is: in the object it exports, `._BLOCKR_MODULES_`, its plugin classes and its board options, each with its module, and the modules it offers other packages' UIs, beside its block classes, which R reads for each available package, so that a package registers nothing as it loads but block classes that it does not list ([Block classes in R](Rewrite-1.1.5#registration)), and the rest through S3 methods.
With illustrative names:

```r
plugin_version.dag_plugin <- function(x, ...) 2L                  # in blockr.dag, once its plugin's state has changed shape, as an exported S3 method
output_schema.chart_output <- function(x, ...) read_json_schema("chart-output.schema.json")   # in blockr.viz, S3 methods for
output_coercion.chart_output <- function(x, ...) as_chart_output                               # its schema, its coercion,
output_renderer.chart_output <- function(x, ...) {                                             # its renderer
  chosen_renderer("chart_output", new_renderer("chart_output", js_module("chart.js")))
}
output_requests.chart_output <- function(x, ...) {                                             # and a download
  list(download = function(result, options, params, format, file) chart_pptx(result, file))
}
board_option_requests.data_dir_option <- function(x, ...) {       # in blockr.io, for its data directory
  list(list_dir = function(path = "") list_dir(path))
}
plugin_requests.code_plugin <- function(x, ...) {                 # in blockr.code, for its plugin class blockr.code-code_plugin
  list(script = function(reads) export_code(reads))
}
```

The object is an environment that the package's `.onLoad()` fills, reading its block classes from its `inst/registry/blocks.yml` with `read_blocks_yml()`, or a list that the package defines in its code ([blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)).
A plugin class and a board option each have one module ([UI modules in JS](Rewrite-1.1.7#modules-of-plugin-classes-and-board-options)), and a module that a package offers others, which its object lists in `modules`, is reached by its id through `host.module()` and `CoreApi.module()`, while a plugin class holds its `ui` and its `frontend` itself rather than naming a module by id.
A plugin class gives the version of its state through its method of `plugin_version()` ([Plugins](Rewrite-1.1.12#a-plugin)).
An output class gives, through S3 methods rather than declarations, the JSON Schema of its outputs, by which R writes them, its coercion, by which R names its renderer in a block class's registry entry, its renderer, `blockr.viz-chart_output` here, and its requests, which R runs with the result the output was made from, so that S3 dispatch gives a subclass what its class gives ([Block classes in R](Rewrite-1.1.5#outputs)).
A board option's requests come from its package's method of `board_option_requests()` for the board option's class, `{id}_option`, and a plugin's from its package's method of `plugin_requests()` for the plugin's class, which R finds by the type of each request, as [blockr.core#484](https://github.com/BristolMyersSquibb/blockr.core/pull/484) built requests ([Wire protocol](Rewrite-1.1.9#requests)).
R calls a board option's request with its args by name, and a plugin's with its args by name and, in `reads`, the blocks it reads by id, each a list of its `result` and the block expression `expr` R built for it.
A package declares none of the blockr options its client reads, which the client asks R for by name ([Board options and blockr options](Rewrite-1.1.13#blockr-options)).
A module's stylesheet and JSON Schema need no declaration, since they sit beside it ([UI modules in JS](Rewrite-1.1.7#packaging)).

### What goes from R

The generics that draw or redraw UI from R go: `board_ui()`, `block_ui()`, `insert_block_ui()`, `remove_block_ui()`, `toolbar_ui()`, the stack UI generics, `blockr_app_ui()` and `blockr_app_server()`, and so do the `callbacks` through which a frontend hooks into `board_server()`, which goes with the board server ([Client-owned board state](Rewrite-1.1#today)).
A frontend's R side shrinks to what its object lists, its plugin class with its module and the modules it offers, its plugin class's methods of `plugin_version()`, `plugin_requests()` and `frontend_args()`, its output classes' methods and the functions that make any renderers of its own (above), and the constructors that app scripts call, such as the dock's `new_dock_plugin()` and its `new_dock_board()`, which keeps working as a board that holds the dock's state ([Plugins](Rewrite-1.1.12#boards-and-app-scripts-from-today)).

### Testing

Core ships, beside the stubs of its hosts ([UI modules in JS](Rewrite-1.1.7#testing)), a `CoreApi` for tests whose store, commands and scheduler are core's own and whose replies from R come from fixtures, those the wire protocol's tests round-trip ([Wire protocol](Rewrite-1.1.9)), so that a plugin, a frontend among them, runs in a test runner on a board, needing neither R nor a browser, with the module of each plugin class or board option that the test gives it, by the id that a reply names it under, while the stubs bring core's basic frontend and its Edit board plugin ([Plugins](Rewrite-1.1.12#testing), [blockr.core#588](https://github.com/BristolMyersSquibb/blockr.core/pull/588)).

End-to-end tests run an app with R and a browser, through shinytest2 to start with, and core exports what they check.
R exports each block's latest result through `exportTestValues()`, as `blockr_test_exports()` does today ([R/utils-serve.R#L310-L331](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-serve.R#L310-L331)), which Shiny does only in the test mode shinytest2 starts an app in, and the client exposes the board and each block's status, read only, for `AppDriver$get_js()` to read, since they now live in the client.

## Open questions

None.
