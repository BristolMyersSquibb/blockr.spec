# Notifications, logging and tracing: what the user is told and what is recorded where
Status: settled on 2026-11-10. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how the user learns of a message, warning or error, and what R and the client log and trace.
Every message, warning and error that the user should see reaches the frontend through one member of `CoreApi`, whether R raised it as a condition, core failed at something, or a package's module raised it.
Each shows by what it concerns, such as on a block's card or in a plugin's panel, and only one for which the frontend draws no such place shows for the whole board, as a toast.
Log lines go to the console by default, and log lines and spans go to an OpenTelemetry collector wherever the deployment names one, from R and from the browser alike.
It shapes the notifications of `CoreApi` ([blockr.core#539](https://github.com/BristolMyersSquibb/blockr.core/issues/539)) and the `notifier` of the calls that raise them ([blockr.core#709](https://github.com/BristolMyersSquibb/blockr.core/issues/709)), how core's basic frontend shows them, as toasts ([blockr.core#549](https://github.com/BristolMyersSquibb/blockr.core/issues/549)) and by a plugin's section ([blockr.core#710](https://github.com/BristolMyersSquibb/blockr.core/issues/710)), logging in R ([blockr.core#550](https://github.com/BristolMyersSquibb/blockr.core/issues/550)) and in the client ([blockr.core#551](https://github.com/BristolMyersSquibb/blockr.core/issues/551)), tracing ([blockr.core#552](https://github.com/BristolMyersSquibb/blockr.core/issues/552)) and the guide for deployments ([blockr.core#553](https://github.com/BristolMyersSquibb/blockr.core/issues/553)), and the dock's notifications build on it ([Client-drawn dock](Rewrite-1.2), [blockr.dock#637](https://github.com/BristolMyersSquibb/blockr.dock/issues/637)), as do the Edit board plugin's ([blockr.core#711](https://github.com/BristolMyersSquibb/blockr.core/issues/711)) and the assistant's ([blockr.assistant#283](https://github.com/BristolMyersSquibb/blockr.assistant/issues/283), [blockr.assistant#284](https://github.com/BristolMyersSquibb/blockr.assistant/issues/284)).
How a reply carries a block's conditions is [Wire protocol](Rewrite-1.1.9#evaluating-a-block)'s, how a block's status holds them [Evaluation in the client](Rewrite-1.1.10#statuses)'s, and how a frontend draws the board [Drawing the board](Rewrite-1.1.8)'s.

## What must hold

1. Every message, warning and error that the user should see reaches the frontend through one member of `CoreApi`, whoever raised it: R, core or a package's module.
   So a frontend draws them all from one place, where today's `board$conditions` holds only those of blocks.
2. Each holds what a frontend needs to choose how and where to show it without reading its message: its severity, who raised it, and the board object that it concerns or the board, each apart from the other.
   So a frontend places a notification by either, such as on the card of the block that it concerns or next to the plugin that raised it.
3. Core withdraws each notification once its cause has gone, so that a frontend can take down one that has gone stale.
   A block's conditions go when the block's next reply replaces them, those of R's reply to an ask of its output when the next such reply does, the conditions of R's reply to a request when R next replies to a request of the same name, unless the request's caller takes them itself, and the rest when whoever raised them withdraws them, and every one as the block, link or stack that it concerns leaves the board or the next board opens.
4. A frontend reads those that hold as it draws, and hears each one that comes or goes.
   So one raised before it draws, such as the failure of a module that the reply names, still reaches the user.
5. A frontend shows each notification where it draws what the notification concerns, such as on the card of the block or by the section or the panel of the plugin, and in a place for the whole board, such as a toast, only one for which it draws no such place, since the user cannot always tell from a toast where a failure lies.
   Where that place is collapsed or hidden, the frontend still tells the user that a warning or an error holds there, such as with a badge.
   Each frontend decides how far it can follow this, and how each notification shows and for how long, such as until core withdraws it, until the user dismisses it, or as a toast that fades after a few seconds, since core offers each notification with what it concerns and cannot check where it shows.
   Core draws only what no frontend can: the error of a page that cannot start or whose frontend cannot draw.
   It leaves the element of a module that cannot draw empty, so that the frontend says where the failure shows ([UI modules in JS](Rewrite-1.1.7#the-contract)).
6. A plugin whose class has a `ui` shows the notifications about itself in its UI, and what fails of what the user did there beside where the user did it, such as why the store refused the edit of one of its forms.
   A storage plugin, whose controls the frontend draws, leaves its own to the frontend, as the frontend draws every notification.
7. Core raises a notification for what fails of a call, a request or an edit, unless the call's caller takes it, which every such call lets its caller do in the same way, so that a caller that shows the failure itself, or hands it on as the assistant hands its tools' failures to the model, shows it once.
8. Core holds them outside the board, as it holds which block has focus, so that no file saves them and no undo brings one back ([Board objects](Rewrite-1.1.1#what-lives-where)).
9. What fails in the client's code is logged with its stack, and what fails in R's own machinery is logged in R, whether or not the user is also told, so that whoever can fix it finds it.
10. R logs every condition that it sends the client, as main logs every condition that a block raises.
11. Packages write log lines through one API on each side, `write_log()` in R and `log` in the client.
    A deployment swaps the logger that writes the lines out, from the console's to OpenTelemetry's, without changing a package.
12. R does none of the client's logging or tracing: the browser sends its own records to the collector, so that telemetry never delays an evaluation.
13. A deployment can follow an edit as one trace, from the command in the client, through each evaluation that it causes in R, to the reply.
14. Nothing leaves the page or the R process as telemetry unless the deployment sets where it goes.

## Today

On main, `board_server()` gathers the conditions of every block into one reactive data frame, `board$conditions`, with a row per active condition and the columns `block`, `phase`, `severity`, `message` and `id`, the last a digest of the message ([R/board-server.R#L11-L19](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L11-L19)).
The `notify_user` plugin shows a toast for each row whose severity `show_conditions` names, warnings and errors unless a board option or a blockr option names others.
A toast stays until the user closes it or its condition goes.
Toasts are keyed by block, severity and `id`, so a toast that the user closed stays closed while the same condition holds, and a condition that a block raises twice shows once ([R/plugin-notification.R#L76-L141](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-notification.R#L76-L141)).
Everything else that core tells the user passes it by: 27 calls of `notify()`, core's wrapper of Shiny's `showNotification()`, show a board update that fails ([R/board-server.R#L403](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L403)) and what `manage_blocks`, `manage_links`, `manage_stacks`, `edit_block` and `ctrl_block` refuse or fail at.
Shiny stacks every toast in the page's bottom right corner.
A toast of `notify()` fades after five seconds, its default, while the editors of links and stacks keep theirs until the user closes them ([R/plugin-links.R#L531-L545](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-links.R#L531-L545), [R/plugin-stacks.R#L504-L518](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-stacks.R#L504-L518)).
The issue [blockr.core#93](https://github.com/BristolMyersSquibb/blockr.core/issues/93) puts this as "Board notifications are not centrally organized."
Each call of `notify()` also logs its message, at the level of its severity, unless it passes `log = FALSE` ([R/utils-shiny.R#L40-L71](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-shiny.R#L40-L71)).

R logs through core's own `write_log()` and its wrappers, `log_fatal()` to `log_trace()`, as the blockr options `log_level`, `logger`, `log_time` and `log_mem` set, at info and above unless `log_level` names another level ([R/utils-logging.R#L25-L104](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/utils-logging.R#L25-L104)).
The function `write_log()` hands the logger that the blockr option `logger` picks one finished line, with the level, time and package written into the text and the text wrapped to the console's width ([#L68-L103](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/utils-logging.R#L68-L103)).
Its default logger, `cat_logger()`, writes errors to standard error and the rest to standard output, which Connect keeps in the content's log ([#L200-L252](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/utils-logging.R#L200-L252)).
On main, the handlers that catch a block's conditions log each one, a message at info, a warning at warn and an error at error ([R/utils-cnd.R#L157-L200](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-cnd.R#L157-L200)), so main's log holds every condition that a block raises.
Main's `blockr_deser()` logs what it drops and tells the user nothing ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)).
On `js-state`, the evaluator and the Shiny transport log what they ignore, at debug or warn, and what they fail at, at error, such as a reply they cannot send ([R/evaluator-class.R#L200-L255](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/evaluator-class.R#L200-L255), [#L440-L490](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/evaluator-class.R#L440-L490), [R/shiny-transport.R#L140-L160](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/shiny-transport.R#L140-L160)).
But R logs none of the conditions that it sends in a reply, so a block that fails leaves no line in R's log.

In the client, `report()` throws what it is given from a microtask, so that it reaches the console as an uncaught error ([srcts/util/util.ts#L26-L33](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/srcts/util/util.ts#L26-L33)).
Core calls it at 33 places, alike for what the user should hear of and for what only a developer should, and has no other log.
The `notifications` member of `CoreApi` hands each `Note`, a message with a severity, to its subscribers and keeps none, so that a note sent before the frontend subscribes reaches nobody ([srcts/core/core.ts#L198-L227](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/srcts/core/core.ts#L198-L227)).
As a board opens, core sends a note of its own that names what the store dropped, if it dropped anything, once the frontend has drawn the board ([srcts/core/start.ts#L442-L444](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/srcts/core/start.ts#L442-L444)).
Core's basic frontend lists above the board, each until the user dismisses it, every note and every edit that the store or the command registry refused ([srcts/modules/basic/board.tsx#L114-L144](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/srcts/modules/basic/board.tsx#L114-L144)), and draws a block's conditions on its card, from the block's status ([srcts/modules/basic/card.tsx#L219-L233](https://github.com/BristolMyersSquibb/blockr.core/blob/1776bf174cec20d8534965fccd514a8e600b20c1/srcts/modules/basic/card.tsx#L219-L233)).

Shiny imports otel, the OpenTelemetry API for R.
Since 1.12.0, Shiny records spans of sessions, reactive updates, reactives, observers and outputs, and logs of fatal and unhandled errors, wherever `otel::is_tracing_enabled()` holds, as it does once otelsdk is configured to export ([NEWS.md#L1-L56](https://github.com/rstudio/shiny/blob/b5da7868fa0c2924bcb6febad4b78d33da1fdb86/NEWS.md#L1-L56)).
It sanitizes the errors it logs unless `shiny.otel.sanitize.errors` is `FALSE`.
It names the session in each span and record by `session.id`, its session token, as OpenTelemetry's [conventions for sessions](https://opentelemetry.io/docs/specs/semconv/general/session/) have it ([R/otel-session.R#L81-L93](https://github.com/rstudio/shiny/blob/b5da7868fa0c2924bcb6febad4b78d33da1fdb86/R/otel-session.R#L81-L93)).
Core records no telemetry of its own, in R or in the client.

Connect has OpenTelemetry built in since 2026.02.0: an administrator points it at a collector, to which it exports its own traces, metrics and logs ([OpenTelemetry](https://docs.posit.co/connect/admin/opentelemetry/)).
Since 2026.09.0, it also sets up otelsdk for each R content item that opts in, so that the item's process exports traces ([Content telemetry](https://docs.posit.co/connect/admin/opentelemetry/content-telemetry.html)).
Its documentation describes no address to which a browser, or content, can send records of its own.

## Proposal

### Notifications

A notification is a message, warning or error that the user should see, whoever raised it.
R raises one as a condition while it evaluates a block, makes its output or answers a request, core where it fails at something that the user asked for or that the board needs, and a package's module: a plugin, the frontend among them, through `CoreApi`, and a module that core mounts through its host.
The term names what reaches the user rather than how it arose.
R raises conditions and the client throws exceptions, and only some of either reach the user, so "condition" keeps R's sense ([Glossary](Glossary)).
A notification's `source` says who raised it, and its `about` names the board object that it concerns ([Board objects](Rewrite-1.1.1)), apart, so that a frontend places a notification by either.

The `notifications` member of `CoreApi` holds every notification of the open board.
A frontend follows them as it follows focus, through a getter and a subscription ([UI modules in JS](Rewrite-1.1.7#the-contract)):

```ts
interface Notification {
  id: string;                        // the same while it holds, so that a frontend knows which it has shown
  severity: "message" | "warning" | "error";
  message: string;
  source: RSource | CoreSource | ModuleSource;  // who raised it
  about?: BoardObject;               // the board object that it concerns, none for the board
}

interface SourceModule {             // the package's module behind a notification, in one form whoever raised it
  object: { plugin: PluginClassId } | { block: BlockId } | { option: OptionId };  // the board object whose module it is
  renderer?: string;                 // the renderer, by its id, where the module is the renderer of a block's output or the one that draws a board option
  package?: string;                  // the module's package, where core knows it
}

type BoardObject =                   // a board object by its id, a plugin by its class's
  | { block: BlockId } | { link: LinkId } | { stack: StackId } | { option: OptionId } | { plugin: PluginClassId };

interface RSource {                  // R, in a condition of its reply to what core asked of it for `about`
  kind: "r";
  class: string[];                   // the condition's class vector, as ["simpleWarning", "warning", "condition"]
  request:
    | { type: "evaluate"; phase?: "expr" | "inputs" | "block_eval" | "result_summary" }
    | { type: "output" }
    | { type: "block_class" | "output_class" | "renderer" | "option" | "plugin"; name: string };
  module?: SourceModule;             // the module that made the request, none for an evaluation or an output, which core asks for
}

interface CoreSource {               // core, where it fails at something
  kind: "core";
  code: string;                      // what it is of: a code of the table below, "evaluation_unsent" or "output_unanswered"
  module?: SourceModule;             // the module whose code failed, where one did
}

interface ModuleSource {             // a package's module in the client
  kind: "module";
  module: SourceModule;              // the module that raised it
  code: string;                      // the package's own, such as "render_failed"
}

interface Raised {                   // what a package's module gives notify()
  severity: "message" | "warning" | "error";
  message: string;
  code: string;
  about?: BoardObject | null;        // the board object whose module raises it unless given, null for the board
}

notifications: {
  notify(plugin: PluginClassId, n: Raised): () => void;              // raises a plugin's, and returns what withdraws it
  get(): readonly Notification[];                                    // those that hold, the same array until one comes or goes
  subscribe(fn: (all: readonly Notification[]) => void): () => void;
};
```

A frontend reads `get()` as it draws and follows `subscribe()` from then on, the pair that React's `useSyncExternalStore` takes.
The type takes the term's name, `Notification`.
The browser has a global of that name too, for desktop notifications, and it stays usable: core's type hides only the browser's type, and only in a module that imports core's, where the browser's constructor still works.
A plugin names itself as the first argument of `notify()`, as it does for `request()`, since `CoreApi` is one object for every plugin and cannot tell who calls it, and core makes the source from it, with the package from the class's id.
A module that core mounts raises one through its host's `notify()`, which takes what a plugin gives and fills in the module: the block or the board option that it belongs to, the renderer where it is one, and its package ([UI modules in JS](Rewrite-1.1.7#the-contract)).
A board option's `onChange()` raises one through the `notify` that it gets beside the value ([Board options and blockr options](Rewrite-1.1.13#defining-a-board-option)).
A notification of a module concerns the module's own board object unless it names another, or the board with `null`.
What a mounted module raises holds until its mount ends at the latest, and what an `onChange()` raises until its next call returns.
The code lets a frontend choose how to draw a notification, such as a button that reloads the page for core's `page_reload_needed`, while a class vector stays R's, on R's conditions alone.
The source lets a frontend say who raised one, and lets a plugin find its own.
Each source names the module behind a notification in `module`, in the one form of `SourceModule`, so that a frontend reads which module a notification is of in one way, whoever raised it: the module that made R's request, the module whose code core found failing, or the module that raised it ([blockr.core#615](https://github.com/BristolMyersSquibb/blockr.core/pull/615)).
A block has two modules, its class's UI module and the renderer of its output, and so has a board option, its own module and the renderer that the app may name to draw its value in place of its UI, so a module names the renderer, by its id, where it is one.
A module without a renderer is the block's UI module, the board option's own module or the plugin class's module.

Core makes a block's notifications from the conditions of its status, one for each, and derives them from the scheduler rather than copying them.
So `scheduler.status()` keeps a block's conditions for the frontends and hosts that read them ([UI modules in JS](Rewrite-1.1.7#the-contract)), and the two never differ.
Their source is R's, with the evaluation and the phase that raised each condition.
The scheduler writes one condition itself, the error of an evaluation that the transport could not send, and that is core's, of the code `evaluation_unsent` ([Evaluation in the client](Rewrite-1.1.10#statuses)).
Why a block is invalid or waiting is no condition but the reason that its status holds beside its summary, and raises no notification.
A block's notification takes its id from the block, the severity, the source and the message.
So the same condition in the block's next reply keeps its id, and a frontend can tell that it has shown it already, as a toast that the user closed stays closed today while its condition holds.
Two conditions of one reply that share all four are one notification, as today's toasts show such a condition once.
Where R replies to an ask of a block's output, ok or error, core raises a notification for each condition of the reply, R's, of the request `output`, which concerns the block, in place of those of the reply before, so that a warning of an output that R made reaches the user as the error of one that it could not make does ([blockr.core#607](https://github.com/BristolMyersSquibb/blockr.core/pull/607), [blockr.core#614](https://github.com/BristolMyersSquibb/blockr.core/pull/614)).
Where an ask fails without an error from R, as where it gets no reply or where R's error reply holds no condition of the severity `error`, core raises one of its own beside them, of the code `output_unanswered`, with the failure that the output's host gives through `error()` ([UI modules in JS](Rewrite-1.1.7#the-contract)).
Where R replies to a request, ok or error, core raises a notification for each condition of the reply, R's, with the request's type and name and the module that made it, which concerns what the request was made for: the block of a block class's, an output class's or a renderer's request, the board option, or the plugin.
It holds until R next replies to a request of the same name for that board object, so that a request that fails again keeps its notifications, and one that succeeds with no condition withdraws them.
A request that fails still rejects to its caller with the conditions.
A caller that shows the conditions itself, or hands them on, as the assistant hands them to the model ([The assistant's tools](Rewrite-1.4.2#how-failures-reach-the-model)), takes their notifications through the request's `notifier` instead, a plugin and a module that core mounts alike, since a frontend cannot tell the assistant's requests from another plugin's ([Taking a call's notifications](#taking-a-calls-notifications)).

Core raises its own notifications where it fails at something that the user asked for or that the board needs.
Each names what failed and what needed it, and its source is core's, with the code that the table gives:

| What | Severity and code | Concerns | Withdrawn when |
|---|---|---|---|
| A module that cannot draw: a block's UI, a renderer, a board option's UI or a plugin's UI ([UI modules in JS](Rewrite-1.1.7#the-contract)) | Error, `module_failed` | The block, board option or plugin, naming the module | The next board opens, or the block leaves the board |
| A board option that does not go onto the board, since no available package defines it or its default fails or does not fit its schema ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)) | Error, `board_option_failed` | The board option, naming its own module where an available package defines it | The next board opens |
| An `onChange` that throws ([Board options and blockr options](Rewrite-1.1.13#defining-a-board-option)) | Error, `on_change_failed` | The board option, naming its own module | Its next call returns |
| A module that the reply names for a plugin class or a board option, and that fails to load ([UI modules in JS](Rewrite-1.1.7#modules-of-plugin-classes-and-board-options)) | Error, `module_failed` | The plugin class or the board option, naming the module | The next board opens |
| A plugin's `start` that throws ([Plugins](Rewrite-1.1.12#running-a-plugin)) | Error, `plugin_start_failed` | The plugin, naming its class's module | The next board opens |
| A board that core could not open: one that the app's storage plugin named but that holds no JSON or fails to open, one that the store's check refuses as `store.open()` is called, so that the board on the page stays open, or one that fails to open after core's check, so that core opens the board before again ([Drawing the board](Rewrite-1.1.8#opening-a-board)) | Error, `board_open_failed` | The storage plugin that named it, naming its module, or else the board | The next board opens |
| An edit that the store or the command registry refuses, which a plugin made through `CoreApi` or a module through its host's `submit()`, and whose caller takes no notifications ([Taking a call's notifications](#taking-a-calls-notifications)) | Error, `board_edit_failed` | The board for a plugin's edit, whatever block the edit names, since core cannot tell which plugin made it, and the block or the board option for a module's | The same refusal again, which raises it anew, or the next board opens |
| A later reply to `hello` that names a package at another version than the page loaded, for which core asks the user to reload the page ([UI modules in JS](Rewrite-1.1.7#modules-of-plugin-classes-and-board-options)) | Warning, `page_reload_needed` | The board, naming the packages | A later reply to `hello` that names the versions that the page loaded, or one that names other versions again, which raises it anew with them, and the next board opens, which raises it again while the versions differ |
| What the store dropped as the board opened ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)) | Warning, `board_objects_dropped` | The board, naming each object with its package | The next board opens |

So what the store dropped as the board opened reaches every frontend with no code of its own, where each frontend's package would otherwise subscribe to the store before the board opens to learn of it.
One notification covers the whole opening, so that a board that loses twenty blocks shows one message.
The store still announces what it dropped with the opening, for code that acts on it ([Board updates](Rewrite-1.1.2#following-the-board)).
Where `serve()` serves a block alone, core keeps the board R sent, since it runs no plugin there, and so no storage plugin that could name another, and no frontend draws that page ([Drawing the board](Rewrite-1.1.8#starting-the-page)).

Core logs every failure that it raises a notification for as well, with its stack, which a notification does not carry ([Logging](#logging)).
Core draws nothing in the element of a module that cannot draw, which it leaves empty, so that the frontend alone says where the failure shows, as on the card of the block whose module it is.
A renderer that the React SDK's `outputRenderer()` makes draws nothing in place of a component that throws either, and raises why through its host's `notify()`, of the code `render_failed`, until the component draws another output ([UI modules in JS](Rewrite-1.1.7#react)).
Where a board option that a block's UI module, a renderer or a plugin's UI requires does not go onto the board, core also raises that the module cannot draw, of the code `module_failed`, about the block or the plugin, since the notification about the board option says nothing of what it stops.
The frontend's own module is the exception: where it cannot draw, no frontend runs to draw a notification, so core shows the error in the page's element alone, as it does for a page that cannot start.

A failure that a call returns goes to the caller as well: the store throws what refuses an edit, a command and `store.open()` reject with it, and a request that fails rejects with the reply's conditions ([UI modules in JS](Rewrite-1.1.7#the-contract)).
Core raises a notification for a refused edit besides, of the code `board_edit_failed`, and for a board that the store's check refuses, of the code `board_open_failed`, unless the caller takes it ([Taking a call's notifications](#taking-a-calls-notifications)).
So a caller that shows nothing of the failure itself, such as core's basic frontend for its own edits, raises nothing of its own, where the basic frontend keeps a list of refused edits above the board today (Today).
Core raises the same refusal anew each time, so that a frontend that has shown it shows it again, and logs the reason at debug alone, since the call hands it to its caller.
A board that fails to open after core's check is an exception.
Its `store.open()` rejects, but the opening has ended the code that called it, so core raises the notification itself, whatever the caller passed.
A failure inside core's own machinery, such as a subscriber that throws or a demand whose function throws, reaches no user, since no user can act on it, and is only logged.

Core withdraws every notification as the next board opens, since an opening ends everything core runs for the board ([Drawing the board](Rewrite-1.1.8#opening-a-board)).
It withdraws every notification that concerns a block, a link or a stack as that leaves the board, with those of a block's modules, and a module's own as the module withdraws it.
A notification raised about a block, a link or a stack that the board no longer holds holds nothing, whoever raised it, since the work that raises one, such as a plugin's request, can outlive what it concerns, and core logs it at debug ([Logging](#logging)).
Core logs one about a board object that the board has never held, and one from a plugin that the app does not run, at error, since only a mistake in the module names one, and `notify()` refuses one whose members are of the wrong kind, as a module in plain JS may give.
Core's own notifications and those of R's replies to requests take their ids from what they hold, so that a failure raised twice, as by two mounts of one module, is one notification, which holds until each raise of it is withdrawn, while those of modules take a count within the opening.

### Taking a call's notifications

A call through which core raises notifications for its caller takes a `notifier`, a function to which core hands those notifications in place of raising them:

```ts
notifier?(notifications: readonly Notification[]): void;   // the notifications that the call would raise, none of which core then raises
```

It is a request option of `request()`, on `CoreApi` and on every host.
The other such calls take it in an object as their last argument, as the store's `apply()` takes `undo` there: `commands.run()`, the store's `apply()`, `undo()`, `redo()` and `open()`, as `CoreApi` hands the store out, and a host's `submit()` ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins), [UI modules in JS](Rewrite-1.1.7#the-contract)).
Core hands it the notifications of a request once for each reply, ok or error, an empty list for a reply with no condition, and the notification of a refused edit or board once, before the call rejects or throws, which it still does, with the reply's conditions or the reason.
So a caller that shows the user a failure itself, or hands it on, takes the call's notifications, while one that does neither leaves them to core, which raises them for the frontend to show.
The assistant takes those of its tools' requests and edits, which it hands to the model, since the model tells the user of them in its reply ([The assistant's tools](Rewrite-1.4.2#how-failures-reach-the-model)).
Core's inputs take those of their block's `submit()`, whose reason they show below themselves ([UI modules in JS](Rewrite-1.1.7#react)), and the Edit board plugin those of its edits, whose reason it shows beside the form or the button that made each ([The Edit board plugin](Rewrite-1.1.15#each-edit-at-once)).

A call with a notifier withdraws none of the notifications that earlier calls raised, such as those of an earlier reply to a request of the same name, since core cannot tell which caller raised them, and a withdrawal could take back what another caller's call raised.
A plugin passes a notifier only for a call of its own, which core cannot check, since `CoreApi` is one object for every plugin.
One function serves every such call, so that a caller keeps a failure from showing twice in one way, where `js-state` has a request option of its own for a plugin's requests, raises nothing for an edit of an origin other than `user` or for a host's `submit()`, and lets no module keep the conditions of its host's requests from raising (notes).

### Where a notification shows

A notification shows best where the user looks for it, by what it concerns, since the user cannot always tell from a toast where a failure lies.
Core offers each notification with what it concerns and cannot check where it shows, so frontends and plugins follow this as guidance, each as far as it can:

- A plugin whose class has a `ui` shows the notifications about itself that hold in its UI, those that core and R raise about it included, such as the conditions of its requests, which it reads from `notifications.get()`, or through the React SDK's `useNotified()` given the plugin ([UI modules in JS](Rewrite-1.1.7#react)).
  It shows what fails of something that the user did in its UI beside where the user did it, such as why the store refused an edit of one of its forms, and takes that call's notifications, so that core raises none (Taking a call's notifications).
  How it shows them is its own.
- A frontend shows the notifications about a block on the block's card, and those about a plugin by the plugin's section or panel, where it tells the user that a warning or an error holds while the section is collapsed or the panel is behind another tab, such as with a badge on the section's title or a dot on the panel's tab.
- A frontend shows a notification in a place for the whole board, such as a toast, only where it draws no place for what the notification concerns: the board, a link, a stack or a board option where it draws none for them, a plugin without a `ui`, such as a storage plugin, or a plugin whose section or panel it does not draw, such as a panel that the dock's active view does not hold.

A storage plugin and the frontend are exceptions to the first, since a storage plugin has no UI but the controls that the frontend draws, and the frontend draws every notification ([Plugins](Rewrite-1.1.12#storage)).
A frontend that cannot follow the others, as for want of room for a badge, shows the notification as it can, such as a toast.
Core's basic frontend follows them as below, and the dock as [Client-drawn dock](Rewrite-1.2) has it.
A frontend may one day also show some as desktop notifications, such as an error while the page's tab is hidden, which needs nothing from core.

### Core's basic frontend

Core's basic frontend shows each notification once, on a block's card, by a plugin's section or as a toast:

- A block's card shows the notifications about the block, whoever raised them, of the severities that core's `show_conditions` board option names, which are warnings and errors unless a script, a file or the user sets others.
  Those are the conditions of the block's status and of R's replies to an ask of its output or to its requests, a module of the block that cannot draw, an output that core could not get, and what the block's modules and plugins raise about it, since core draws none of them in an element of the card.
- A plugin's section shows the notifications about the plugin, of the same severities, as pills on its title beside the plugin's name, whether the section is open or collapsed, as a card's pills count a block's: the pill of the errors reads "error", and those of the warnings and the messages count them, as "2 warnings" ([Defining a board in R](Rewrite-1.1.3#data-passed-to-serve)).
  Each pill opens the messages of its notifications below the title, as a card's pill opens its banners, but closed at first, since the plugin shows them in its UI, so that the user can still read one that the plugin does not show, such as why its UI cannot draw.
  Those are what the plugin raises about itself, the conditions of its requests, and what core raises about it, such as its module that cannot draw or its `start` that throws.
- Every other notification shows as a toast, whatever its severity: those about the board, a link, a stack, a board option, or a plugin without a section, such as a storage plugin.

So `show_conditions` filters what a card and a section show, as it filters blocks' conditions today, and keeps its name, since the block's conditions are most of what a card shows.

The toasts stack in the page's bottom right corner, as Shiny's do on main (Today), and each names what it concerns, such as the block, the board option, the plugin or the package.
A message's toast fades after five seconds, as a toast of `notify()` does by default, though not while the pointer rests on it.
A warning's or an error's stays until the user closes it, as the toasts of a block's conditions do on main, since one that fades is easy to miss, such as the failure of a module while the page still loads.
A toast goes as soon as core withdraws its notification, and one that faded or that the user closed does not come back while its notification holds, since the basic frontend keeps the ids of those it has shown, for the opening.
The toasts take the place of the list above the board, which moves the board each time an item comes or goes.

### Logging

Every log line, in R and in the client, has a level, a message and the package that wrote it.
Packages write log lines through one API on each side: `write_log()` and its wrappers in R, as today, and `log` in the client.
A logger writes the lines out, and the blockr option `logger` names it on both sides, by a string that R and the client both read, since a function tells the client nothing and R cannot send one to it ([blockr.core#612](https://github.com/BristolMyersSquibb/blockr.core/pull/612)):

- With `"console"`, R writes an error to standard error and any other line to standard output, and the client writes each line to the browser's console.
- With `"otel"`, each side writes each line as a record through OpenTelemetry: R through `otel::log()`, and the client to the collector that the blockr option `otel_client_endpoint` names ([Where the records go](#where-the-records-go)).
- With `"condition"`, R signals an error or a warning as a warning and any other line as a message, which a test catches as such, and the client writes to the console, since the browser has no conditions.

Where `logger` is not set, each side writes through OpenTelemetry where it has somewhere to send, R where OpenTelemetry has set up an exporter of logs and the client where `otel_client_endpoint` names a collector, and to the console otherwise.
So a deployment swaps the logger without changing a package, and one that sends its records to a collector sets nothing more.
Where `logger` is `"otel"`, each side stops where it has nowhere to send: R fails to write a line where OpenTelemetry has set up no exporter, and `serve()` stops before the app's first session where `otel_client_endpoint` names no collector, so that a deployment learns of it before a page starts, while the client checks again as the page starts.
Any other value of `logger`, a function among them, is an error.
The blockr option `log_level` sets the lowest level written, on both sides, and is info unless it names another.

In R, OpenTelemetry's logger writes each line through `otel::log()`, with its level as the record's severity, and with its package, the session whose message R handles as it writes the line, and the line's attributes as the record's attributes.
Since it records the level and the package as fields of their own, `write_log()` hands its logger the message as written, its level and its package, where today it hands over one finished line (Today).
So the console's logger, and the one of `"condition"`, add the prefix of level, time and package themselves, as the blockr options `log_time` and `log_mem` set, and wrap the text.
Core works the logger out as it first needs one and keeps it for the process, and `serve()` works it out afresh as it starts an app, so a test that changes the blockr option calls `reset_logging()` for core to work it out again.
With otelsdk's exporter over HTTP, the records leave R from a background thread, so that R's own thread only queues each one.
The evaluator and the transport log what they fail at, at error, naming the request where there is one, and what they ignore, at warn or debug.
R also logs every condition that it sends in a reply, of an evaluation, an output or a request, at the level of its severity: a message at info, a warning at warn and an error at error.
Each line names the block and its revision, so that R logs every condition that a block raises, as main does (Today).

In the client, plugins write log lines through `CoreApi`, and every other module through its host, whose `log` names the module's package already ([UI modules in JS](Rewrite-1.1.7#the-contract)):

```ts
log(pkg: string): Log;               // in CoreApi: log lines that name the package, as core.log("blockr.dock").warn("...")
readonly log: Log;                   // in every host: log lines that name the package of the module's block class, renderer or board option

interface Log {
  error(message: string | Error, attributes?: Record<string, Json>): void;   // an Error is logged with its stack
  warn(message: string, attributes?: Record<string, Json>): void;
  info(message: string, attributes?: Record<string, Json>): void;
  debug(message: string, attributes?: Record<string, Json>): void;
  trace(message: string, attributes?: Record<string, Json>): void;
}
```

The levels are R's but for fatal, which stops R and has nothing to stop in the client.
Core logs every failure that it catches at error, with its stack, through its own `log`, where `report()` throws it from a microtask today, and so it logs every failure that it raises a notification for too.
Core reads `log_level`, `logger` and `otel_client_endpoint` with the blockr options that it reads as the page starts ([Drawing the board](Rewrite-1.1.8#starting-the-page)), and drops a line below that level before any logger sees it.
A value that the client does not take stops the page, as a bad value of the scheduler's options does: a `log_level` that names no level, a `logger` that names none of the three, and an `otel_client_endpoint` that is no URL over HTTP or HTTPS, while the client takes a level by the start of its name, as R's `as_log_level()` does.
Core holds every line logged before it has set the logger up, which includes the time that the OpenTelemetry module takes to load, and then writes those that reach the level, each with the time when it was logged, so that what fails as the page starts reaches the logger too.
Where the page fails before core sets up any logger, core writes what it holds to the console, at info, and where the OpenTelemetry module fails to load, it writes to the console and logs why there.
The console's logger writes each line with `console.error()`, `console.warn()`, `console.info()` or `console.debug()`, puts its package's name in front of it, and leaves out the attributes, as R's console logger does.
OpenTelemetry's logger sends each line as a log record from the browser to the collector's path `v1/logs`, in batches, and sends what it holds as the page is hidden.
It logs an `Error` with the stack of each of its causes after its own, each after `Caused by: `, since core wraps most errors that it catches, and the stack of the wrapper points at core's own catch.
R does none of that work.
Tests replace the logger with one that holds the lines, and a test fails where it logs an error that it does not capture, as an error that `report()` threw failed it today, while the stub of `CoreApi` holds each line that a plugin logs, so that a package's test checks what its plugin logged ([UI modules in JS](Rewrite-1.1.7#testing)).

### Tracing

Core records spans through OpenTelemetry on both sides: through otel in R, which Shiny already imports, and through `@opentelemetry/api` in the client.
Core ships one copy of `@opentelemetry/api` on the page and maps it in the page's import map, as it does React ([UI modules in JS](Rewrite-1.1.7#react)), so that a package records spans of its own into the same traces, such as the assistant's calls to its model.
Neither side records a span until the deployment sends its records to a collector ([Where the records go](#where-the-records-go)).
Spans carry ids and revisions, never a block's state or data.

In the client, core records a span for:

1. Each command, from `run()` until the store commits its delta, with the command's id and the delta's origin ([Board updates](Rewrite-1.1.2#commands)).
2. Each evaluation, output and request, from sending it to its reply, with the block's id, registry id and revision.
   An evaluation's span links to the span of the command whose delta changed the block's recipe, where one did, so that a trace leads from an edit to every evaluation that it caused.
3. Starting the page and each opening of a board, with a span for each step inside it: `hello`, importing the modules that the reply names, the storage plugin's `storage.load()`, the store's `open()` and the frontend's `render()` ([Drawing the board](Rewrite-1.1.8#starting-the-page)).

Core puts the span of a command, and of a request, under the span that is active as `run()` or `request()` is called, as OpenTelemetry does by default, so that a plugin that calls them inside a span of its own holds them in its trace, as the assistant's tools do ([Assistant as a plugin](Rewrite-1.4#proposal)).

In R, core records a span for each `evaluate`, `request` and `output` message that it handles, with the block's id, registry id and revision, and a span inside it for each phase of an evaluation: `expr`, `inputs`, `block_eval` and `result_summary` ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)).
Each request carries the context of the client's span in `traceparent`, in the format that W3C's [Trace Context](https://www.w3.org/TR/trace-context/) gives its header of that name ([Wire protocol](Rewrite-1.1.9#messages)).
So R's span is a child of the client's, and one trace runs from the edit, through R, to the reply.
The client sends `traceparent` only while it records spans, and R ignores it while it records none.
Both sides name the session in every record and span by `session.id`, Shiny's session token, as Shiny's own telemetry does (Today), so that a collector joins a session's records from R and from the browser.
R hands the client the token in the message that starts a session, as `token` beside `body_url`, which the Shiny transport gives core through an optional `sessionId()` of its `Transport` ([Wire protocol](Rewrite-1.1.9#the-shiny-transport)).

### Where the records go

A deployment sends the records of both sides to one OpenTelemetry collector, which passes them on wherever it is set to.
R exports through otelsdk, which OpenTelemetry's environment variables set, or, for traces, Connect's own setup for content that opts in (Today).
The browser exports to the collector whose base URL the blockr option `otel_client_endpoint` gives, at its path `v1/logs`, as an SDK sends to `OTEL_EXPORTER_OTLP_ENDPOINT`, so that traces can go to `v1/traces` of the same collector, and a relative URL is read against the page.
Every user's browser must reach that URL.
A record from the client holds what R's log lines hold, so the collector needs the care that wherever R's logs go needs.

On Connect, that address is best a collector run beside Connect under Connect's host name, such as `https://connect.example.com/otlp/`.
The page then sends to its own origin and needs no CORS, and Connect's own export can point at the same collector, so that Connect's, R's and the browser's records meet in one place.
Connect itself offers no such address (Today), and running a collector as content on Connect is undocumented.
A hosted service that takes records from browsers works too, but its key then sits in every user's page.

## Open questions

None.

<details><summary>Notes for implementers</summary>

Core's calls of `report()` on `js-state`, at `1776bf1`, sorted by this page.
Those that become notifications: `srcts/core/start.ts` at lines 399, 485, 499, 503 and 513, the startup modules and the boards they name, and at 599, the request to reload the page; `srcts/core/plugins.ts` at 227 and 270, a plugin's `start` and its UI; `srcts/mount/block.ts` at 142 and 346, board options and a block's UI; `srcts/mount/option.ts` at 204, a board option's UI; `srcts/mount/output.ts` at 483 and 533, a renderer; `srcts/core/core.ts` at 187, an `onChange`; and `srcts/react/module.tsx` at 123, the error boundary of a renderer written with the React SDK, through the renderer's host.
Those that core shows in the page's element: `srcts/core/frontends.ts` at 96 and 129, the frontend's module, and `srcts/page/page.ts` at 57, a page that cannot start.
Those for the log alone: `srcts/core/start.ts` at 189, 246, 411 and 475; `srcts/core/plugins.ts` at 203, a plugin left out for a board option whose failure is reported already; `srcts/protocol/client.ts` at 297 and 453; `srcts/scheduler/scheduler.ts` at 582 and 630; `srcts/mount/answers.ts` at 135; `srcts/mount/shared.ts` at 54; `srcts/mount/load.ts` at 103, a stylesheet; `srcts/mount/block.ts` at 461; `srcts/core/core.ts` at 106; and `srcts/store/store.ts` at 226.
Board options' failures are reported once per board and message already (`srcts/mount/block.ts` at 142), and a renderer's `ModuleError` once per object (`srcts/mount/output.ts` at 483).
The one condition that the scheduler writes itself is the error of `unsent()` in `srcts/scheduler/status.ts`, which has no phase, and which `isUnsentError()` tells from R's.
Tests capture what core reports with `reports()` from `srcts/testing/reports.ts`, which holds what `report()` queues.

A module that imports core's `Notification` and also shows desktop notifications still calls the browser's constructor as `new Notification()`, since core's type has no value, as TypeScript 5.9 compiles it.
But its type errors would then name two types `Notification`, so such a module imports core's type under another name.
Core keeps the type a module export and never declares it global, since TypeScript would then merge it into the browser's interface.
The type replaces `Note` in `CoreApi`, and the toasts replace the basic frontend's `Notice` and the list of them that `srcts/modules/basic/notices.ts` keeps.

The basic frontend's dialogs are React Aria's `Modal`, which makes the rest of the page inert while a dialog is open ([blockr.core#752](https://github.com/BristolMyersSquibb/blockr.core/pull/752)).
So the toasts show inside an open dialog, through a portal into an element at the dialog's end, so that they come after its content in the order of the keyboard's focus while they stay fixed to the window's corner, above the backdrop, since the toast of an edit that the dialog made would otherwise wait behind it, as the list above the board does today ([blockr.core#610](https://github.com/BristolMyersSquibb/blockr.core/pull/610)).
A message's toast is a status and a warning's or an error's an alert, which a screen reader reads out at once, as the items of that list are (`srcts/modules/basic/board.tsx` at 126).

The notifier replaces three rules of `js-state` at `6ad402a`: the request option `conditions` of `RequestOpts`, which `srcts/core/requests.ts` hands each reply's conditions; the check of the origin in `refused()`, inside `refusing()` in `srcts/core/core.ts`, which raises `board_edit_failed` only for the origin `user`; and a host's `submit()`, which runs its command past that wrapper, so that core raises nothing for it, as `srcts/types/hosts.ts` says.
A host's request options become `Omit<RequestOpts, "reads">`, which keeps `notifier`.
Core checks that a notifier is a function, as it checks `conditions` today, since a module in plain JS may pass another value.
The React SDK's `useNotified()` in `srcts/react/hooks.ts` takes a block, or null for every notification, and takes a board object instead, so that a plugin's UI and the basic frontend's sections read those about a plugin as a card reads those about its block.
A section's pills reuse what draws a card's, `Pills` and `Banners` in `srcts/card/footer.tsx`, in `srcts/modules/basic/plugins.tsx`, which draws each section as a `<details>` whose `<summary>` holds the plugin's name.

Each of R's loggers is a function inside core of the message, its level and its package, which also gets `asis`, whether to keep the message's line breaks rather than wrap it, and the blockr option `logger` names one by its string.
The one logger in the workspace that core does not set, in the tests of blockr.assistant (`tests/testthat/helper-skills.R`), names `"condition"`.
Whether otel logs at all is `otel::is_logging_enabled()`, which is false until otelsdk is configured, as through `OTEL_LOGS_EXPORTER=otlp` and `OTEL_EXPORTER_OTLP_ENDPOINT`.
The OTLP/HTTP exporters of otelsdk 0.3.0 export from a worker thread of opentelemetry-cpp's batch processors, and drop a record when their queue of 2,048 is full, while its file and console exporters write on R's thread, which a deployment avoids for that reason ([src/stdstream.cc](https://github.com/r-lib/otelsdk/blob/main/src/stdstream.cc)).

The client's OpenTelemetry logger and its tracing are a module of core's that core imports only where `otel_client_endpoint` is set, so that a page without telemetry loads none of it.
The page hands core that import, as `otel` of `StartOptions`, which `startPage()` gives as an import of `@blockr/core/otel`, since the stubs run core without a page and their bundle splits nothing, so that an import inside core would put the SDK into `@blockr/core/stubs`.
It builds on `@opentelemetry/sdk-logs`, stable since the JS SDK's 3.0.0, and on `@opentelemetry/exporter-logs-otlp-http`, still marked experimental, which send OTLP's JSON encoding, stable for logs and traces, by `fetch`: the parts that core uses, `@opentelemetry/api` among them, ship minified in `opentelemetry-<hash>.js`, at 43 kB, or 14 kB gzipped, which R serves gzipped as httpuv serves every file, while core's own code stays readable in `blockr-core-otel.js`, at 2 kB ([blockr.core#612](https://github.com/BristolMyersSquibb/blockr.core/pull/612)), and on the 3.x trace SDK, `@opentelemetry/sdk-trace` with its `StackContextManager`, and its OTLP/HTTP exporter ([JS SDK 3.0.0](https://github.com/open-telemetry/opentelemetry-js/releases/tag/v3.0.0)).
The browser's batch processor sends what it holds on `visibilitychange` to hidden, with `fetch`'s `keepalive`.
The Logs API is part of `@opentelemetry/api` from 1.10.0, which replaced `@opentelemetry/api-logs`.
A collector at another origin than the page lists the page's origin in its OTLP/HTTP receiver's `cors.allowed_origins`, and never `*`, since its responses allow credentials.
In R, Shiny's own spans would show mostly the observer through which the transport takes each message, and `SHINY_OTEL_COLLECT=session` keeps them to sessions.
The guide for deployments first tries the setup on a Connect server of 2026.09.0 or later: which of OpenTelemetry's environment variables Connect sets for content that opts in, whether R's log records reach the collector beside Connect while it does, and whether a page reaches that collector under Connect's host name.

</details>
