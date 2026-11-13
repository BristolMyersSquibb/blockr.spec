# Notifications, logging and tracing: what the user is told and what is recorded where
Status: settled on 2026-11-10. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how the user learns of a message, warning or error, and what R and the client log and trace.
Every message, warning and error that the user should see reaches the frontend through one member of `CoreApi`, whether R raised it as a condition, core failed at something, or a package's module raised it.
Log lines go to the console by default, and log lines and spans go to an OpenTelemetry collector wherever the deployment names one, from R and from the browser alike.
It shapes the notifications of `CoreApi` ([blockr.core#539](https://github.com/BristolMyersSquibb/blockr.core/issues/539)) and their toasts in core's basic frontend ([blockr.core#549](https://github.com/BristolMyersSquibb/blockr.core/issues/549)), logging in R ([blockr.core#550](https://github.com/BristolMyersSquibb/blockr.core/issues/550)) and in the client ([blockr.core#551](https://github.com/BristolMyersSquibb/blockr.core/issues/551)), tracing ([blockr.core#552](https://github.com/BristolMyersSquibb/blockr.core/issues/552)) and the guide for deployments ([blockr.core#553](https://github.com/BristolMyersSquibb/blockr.core/issues/553)), and the dock's notifications build on it ([Client-drawn dock](Rewrite-1.2)).
How a reply carries a block's conditions is [Wire protocol](Rewrite-1.1.9#evaluating-a-block)'s, how a block's status holds them [Evaluation in the client](Rewrite-1.1.10#statuses)'s, and how a frontend draws the board [Drawing the board](Rewrite-1.1.8)'s.

## What must hold

1. Every message, warning and error that the user should see reaches the frontend through one member of `CoreApi`, whoever raised it: R, core or a package's module.
   So a frontend draws them all from one place, where today's `board$conditions` holds only those of blocks.
2. Each holds what a frontend needs to choose how and where to show it without reading its message: its severity, who raised it, and the board object that it concerns or the board, each apart from the other.
   So a frontend places a notification by either, such as on the card of the block that it concerns or next to the plugin that raised it.
3. Core withdraws each notification once its cause has gone, so that a frontend can take down one that has gone stale.
   A block's conditions go when the block's next reply replaces them, the conditions of R's reply to a request when R next replies to a request of the same name, and the rest when whoever raised them withdraws them, and every one as the block, link or stack that it concerns leaves the board or the next board opens.
4. A frontend reads those that hold as it draws, and hears each one that comes or goes.
   So one raised before it draws, such as the failure of a module that the reply names, still reaches the user.
5. The frontend alone decides how each shows and for how long, such as until core withdraws it, until the user dismisses it, or as a toast that fades after a few seconds.
   Core draws only what no frontend can: the error in the element of a module that cannot draw ([UI modules in JS](Rewrite-1.1.7#the-contract)), and the error of a page that cannot start or whose frontend cannot draw.
6. Core holds them outside the board, as it holds which block has focus, so that no file saves them and no undo brings one back ([Board objects](Rewrite-1.1.1#what-lives-where)).
7. What fails in the client's code is logged with its stack, and what fails in R's own machinery is logged in R, whether or not the user is also told, so that whoever can fix it finds it.
8. R logs every condition that it sends the client, as main logs every condition that a block raises.
9. Packages write log lines through one API on each side, `write_log()` in R and `log` in the client.
   A deployment swaps the logger that writes the lines out, from the console's to OpenTelemetry's, without changing a package.
10. R does none of the client's logging or tracing: the browser sends its own records to the collector, so that telemetry never delays an evaluation.
11. A deployment can follow an edit as one trace, from the command in the client, through each evaluation that it causes in R, to the reply.
12. Nothing leaves the page or the R process as telemetry unless the deployment sets where it goes.

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

type BoardObject =                   // a board object by its id, a plugin by its class's
  | { block: BlockId } | { link: LinkId } | { stack: StackId } | { option: OptionId } | { plugin: PluginClassId };

interface RSource {                  // R, in a condition of its reply to what core asked of it for `about`
  kind: "r";
  class: string[];                   // the condition's class vector, as ["simpleWarning", "warning", "condition"]
  request:
    | { type: "evaluate"; phase?: "expr" | "inputs" | "block_eval" | "result_summary" }
    | { type: "output" }
    | { type: "block_class" | "output_class" | "option" | "plugin"; name: string }
    | { type: "renderer"; renderer: string; name: string };
}

interface CoreSource {               // core, where it fails at something
  kind: "core";
  code: string;                      // what it is of: a code of the table below, "block_waiting", "evaluation_unsent" or "output_unanswered"
  package?: string;                  // the package whose module failed, where core knows it
}

interface ModuleSource {             // a package's module in the client
  kind: "module";
  object: { plugin: PluginClassId } | { block: BlockId } | { option: OptionId };  // the board object whose module raised it
  code: string;                      // the package's own, such as "edit_refused"
  package?: string;                  // the package whose module raised it, where core knows it
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
A module that core mounts raises one through its host's `notify()`, which takes what a plugin gives and fills in the block or the board option that the module belongs to, with the module's package ([UI modules in JS](Rewrite-1.1.7#the-contract)).
A board option's `onChange()` raises one through the `notify` that it gets beside the value ([Board options and blockr options](Rewrite-1.1.13#defining-a-board-option)).
A notification of a module concerns the module's own board object unless it names another, or the board with `null`.
What a mounted module raises holds until its mount ends at the latest, and what an `onChange()` raises until its next call returns.
The code lets a frontend choose how to draw a notification, such as a button that reloads the page for core's `page_reload_needed`, while a class vector stays R's, on R's conditions alone.
The source lets a frontend say who raised one, and lets a plugin find its own.

Core makes a block's notifications from the conditions of its status, one for each, and derives them from the scheduler rather than copying them.
So `scheduler.status()` keeps a block's conditions for the frontends and hosts that read them ([UI modules in JS](Rewrite-1.1.7#the-contract)), and the two never differ.
Their source is R's, with the evaluation and the phase that raised each condition.
The scheduler writes two conditions itself, the message of a block that waits and the error of an evaluation that the transport could not send, and those are core's, of the codes `block_waiting` and `evaluation_unsent` ([Evaluation in the client](Rewrite-1.1.10#statuses)).
A block's notification takes its id from the block, the severity, the source and the message.
So the same condition in the block's next reply keeps its id, and a frontend can tell that it has shown it already, as a toast that the user closed stays closed today while its condition holds.
Two conditions of one reply that share all four are one notification, as today's toasts show such a condition once.
Where R cannot make a block's output, core raises a notification with the condition that the output's host gives through `error()`, concerning the block, until the block's next output arrives ([UI modules in JS](Rewrite-1.1.7#the-contract)).
It is R's, of the request `output`, or core's, of the code `output_unanswered`, where the ask got no reply or R's error held no condition.
Where R replies error to a request, core raises a notification for each condition of the reply, R's, with the request's type and name, which concerns what the request was made for: the block of a block class's, an output class's or a renderer's request, the board option, or the plugin.
It holds until R next replies to a request of the same name for that board object, so that a request that fails again keeps its notifications, and one that succeeds withdraws them.
The request still rejects to its caller with the conditions, and a frontend leaves out, by the request's type, what the caller shows already.

Core raises its own notifications where it fails at something that the user asked for or that the board needs.
Each names what failed and what needed it, and its source is core's, with the code that the table gives:

| What | Severity and code | Concerns | Withdrawn when |
|---|---|---|---|
| A module that cannot draw: a block's UI, a renderer, a board option's UI or a plugin's UI ([UI modules in JS](Rewrite-1.1.7#the-contract)) | Error, `module_failed` | The block, board option or plugin, with the module's package | The next board opens, or the block leaves the board |
| A board option that does not go onto the board, since no loaded package defines it or its default fails or does not fit its schema ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)) | Error, `board_option_failed` | The board option | The next board opens |
| An `onChange` that throws ([Board options and blockr options](Rewrite-1.1.13#defining-a-board-option)) | Error, `on_change_failed` | The board option, with its package | Its next call returns |
| A module that the reply names for a plugin class or a board option, and that fails to load ([UI modules in JS](Rewrite-1.1.7#modules-of-plugin-classes-and-board-options)) | Error, `module_failed` | The plugin class or the board option, with the module's package | The next board opens |
| A plugin's `start` that throws ([Plugins](Rewrite-1.1.12#running-a-plugin)) | Error, `plugin_start_failed` | The plugin, with its class's package | The next board opens |
| A board that core could not open: one that the app's storage plugin named but that holds no JSON or fails to open, or one that fails to open after core's check, so that core opens the board before again ([Drawing the board](Rewrite-1.1.8#opening-a-board)) | Error, `board_open_failed` | The storage plugin that named it, with its package, or else the board | The next board opens |
| A later reply to `hello` that names a package at another version than the page loaded, for which core asks the user to reload the page ([UI modules in JS](Rewrite-1.1.7#modules-of-plugin-classes-and-board-options)) | Warning, `page_reload_needed` | The board, naming the packages | A later reply to `hello` that names the versions that the page loaded, or one that names other versions again, which raises it anew with them, and the next board opens, which raises it again while the versions differ |
| What the store dropped as the board opened ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)) | Warning, `board_objects_dropped` | The board, naming each object with its package | The next board opens |

So what the store dropped as the board opened reaches every frontend with no code of its own, where each frontend's package would otherwise subscribe to the store before the board opens to learn of it.
One notification covers the whole opening, so that a board that loses twenty blocks shows one message.
The store still announces what it dropped with the opening, for code that acts on it ([Board updates](Rewrite-1.1.2#following-the-board)).
Where `serve()` serves a block alone, core keeps the board R sent, since it runs no plugin there, and so no storage plugin that could name another, and no frontend draws that page ([Drawing the board](Rewrite-1.1.8#starting-the-page)).

Core logs every failure that it raises a notification for as well, with its stack, which a notification does not carry ([Logging](#logging)).
A module that cannot draw also shows its error in its element, so that the user sees which spot failed.
The frontend's own module is the exception: where it cannot draw, no frontend runs to draw a notification, so core shows the error in the page's element alone, as it does for a page that cannot start.

A failure that a call returns goes to the caller, which tells the user where it should.
The store throws what refuses an edit, a command rejects with it, and a request that fails rejects with the reply's conditions besides its notifications ([UI modules in JS](Rewrite-1.1.7#the-contract)).
So core's basic frontend raises a notification of its own for each of its edits that the store or the command registry refuses, in place of the list it keeps today, and so does the Edit board plugin for its own edits ([The Edit board plugin](Rewrite-1.1.15)).
It is an error of the code `edit_refused`, which concerns the plugin that made the edit, whatever block the edit names, so that it shows as a toast rather than on a card, which the dialog that made the edit may cover ([Core's basic frontend](#cores-basic-frontend)).
A board that fails to open after core's check is an exception.
Its `store.open()` rejects, but the opening has ended the code that called it, so core raises the notification itself.
A failure inside core's own machinery, such as a subscriber that throws or a demand whose function throws, reaches no user, since no user can act on it, and is only logged.

Core withdraws every notification as the next board opens, since an opening ends everything core runs for the board ([Drawing the board](Rewrite-1.1.8#opening-a-board)).
It withdraws every notification that concerns a block, a link or a stack as that leaves the board, with those of a block's modules, and a module's own as the module withdraws it.
A notification raised about a block, a link or a stack that the board no longer holds holds nothing, since the work that raises one, such as a plugin's request, can outlive what it concerns, and core logs it at debug ([Logging](#logging)).
Core logs one about a board object that the board has never held, and one from a plugin that the app does not run, at error, since only a mistake in the module names one, and `notify()` refuses one whose members are of the wrong kind, as a module in plain JS may give.
Core's own notifications and those of R's replies to requests take their ids from what they hold, so that a failure raised twice, as by two mounts of one module, is one notification, which holds until each raise of it is withdrawn, while those of modules take a count within the opening.

### Core's basic frontend

A frontend draws notifications as it chooses, by their source and the board object that they concern, and the dock draws them as [Client-drawn dock](Rewrite-1.2) has it.
A frontend may one day also show some as desktop notifications, such as an error while the page's tab is hidden, which needs nothing from core.
Core's basic frontend shows each notification once, on a block's card or as a toast:

- A block's card shows the notifications that R and core raise about the block, of the severities that core's `show_conditions` board option names, which are warnings and errors unless a script, a file or the user sets others.
  It leaves out what core, the renderer or a module already shows in an element of the card: a module that cannot draw, an output that R could not make, and a request that failed, whose module shows why.
- Every other notification shows as a toast, whatever its severity: those that concern no block, and those that the modules of packages raise.

So `show_conditions` filters what a card shows, as it filters blocks' conditions today, and keeps its name, since a card shows the block's conditions.

The toasts stack in the page's bottom right corner, as Shiny's do on main (Today), and each names what it concerns, such as the block, the board option, the plugin or the package.
A message's toast fades after five seconds, as a toast of `notify()` does by default, though not while the pointer rests on it.
A warning's or an error's stays until the user closes it, as the toasts of a block's conditions do on main, since one that fades is easy to miss, such as the failure of a module while the page still loads.
A toast goes as soon as core withdraws its notification, and one that faded or that the user closed does not come back while its notification holds, since the basic frontend keeps the ids of those it has shown, for the opening.
The toasts take the place of the list above the board, which moves the board each time an item comes or goes.

### Logging

Every log line, in R and in the client, has a level, a message and the package that wrote it.
Packages write log lines through one API on each side: `write_log()` and its wrappers in R, as today, and `log` in the client.
A logger writes the lines out, the console's by default, and a deployment swaps it for OpenTelemetry's without changing a package ([Where the records go](#where-the-records-go)).
In R it sets the blockr option `logger` to `otel_logger()` in place of `cat_logger()`, and in the client it sets the blockr option `otel_client_endpoint`.
The blockr option `log_level` sets the lowest level written, on both sides, and is info unless it names another.

In R, the blockr option `logger` picks the logger, as today, and core adds `otel_logger()`, which writes each line through `otel::log()`, with its level as the record's severity and its package as an attribute.
Where no SDK exports logs, `otel_logger()` writes as `cat_logger()` does, so that no line is lost.
Since `otel_logger()` records the level and the package as fields of their own, `write_log()` hands its logger the message as written, its level and its package, where today it hands over one finished line (Today).
So `cat_logger()` itself adds the prefix of level, time and package, as the blockr options `log_time` and `log_mem` set, and wraps the text.
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
Core reads `log_level` with the blockr options that it reads as the page starts ([Drawing the board](Rewrite-1.1.8#starting-the-page)), and drops a line below that level before any logger sees it.
The console's logger writes each line with `console.error()`, `console.warn()`, `console.info()` or `console.debug()`, and puts its package's name in front of it.
OpenTelemetry's logger, which core uses once the blockr option `otel_client_endpoint` names a collector, sends each line as a log record from the browser to that collector, in batches, and sends what it holds as the page is hidden.
R does none of that work.
Tests replace the logger with one that holds the lines, as `reports()` holds what `report()` queues today.

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

### Where the records go

A deployment sends the records of both sides to one OpenTelemetry collector, which passes them on wherever it is set to.
R exports through otelsdk, which OpenTelemetry's environment variables set, or, for traces, Connect's own setup for content that opts in (Today).
The browser exports to the address that the blockr option `otel_client_endpoint` gives, which every user's browser must reach.
A record from the client holds what R's log lines hold, so the collector needs the care that wherever R's logs go needs.

On Connect, that address is best a collector run beside Connect under Connect's host name, such as `https://connect.example.com/otlp/`.
The page then sends to its own origin and needs no CORS, and Connect's own export can point at the same collector, so that Connect's, R's and the browser's records meet in one place.
Connect itself offers no such address (Today), and running a collector as content on Connect is undocumented.
A hosted service that takes records from browsers works too, but its key then sits in every user's page.

## Open questions

None.

<details><summary>Notes for implementers</summary>

Core's calls of `report()` on `js-state`, at `1776bf1`, sorted by this page.
Those that become notifications: `srcts/core/start.ts` at lines 399, 485, 499, 503 and 513, the startup modules and the boards they name, and at 599, the request to reload the page; `srcts/core/plugins.ts` at 227 and 270, a plugin's `start` and its UI; `srcts/mount/block.ts` at 142 and 346, board options and a block's UI; `srcts/mount/option.ts` at 204, a board option's UI; `srcts/mount/output.ts` at 483 and 533, a renderer; and `srcts/core/core.ts` at 187, an `onChange`.
Those that core shows in the page's element: `srcts/core/frontends.ts` at 96 and 129, the frontend's module, and `srcts/page/page.ts` at 57, a page that cannot start.
Those for the log alone: `srcts/core/start.ts` at 189, 246, 411 and 475; `srcts/core/plugins.ts` at 203, a plugin left out for a board option whose failure is reported already; `srcts/protocol/client.ts` at 297 and 453; `srcts/scheduler/scheduler.ts` at 582 and 630; `srcts/mount/answers.ts` at 135; `srcts/mount/shared.ts` at 54; `srcts/mount/load.ts` at 103, a stylesheet; `srcts/mount/block.ts` at 461; `srcts/core/core.ts` at 106; `srcts/store/store.ts` at 226; and `srcts/react/module.tsx` at 123, the error boundary of a renderer written with the React SDK, which shows what it caught in the renderer's element.
Board options' failures are reported once per board and message already (`srcts/mount/block.ts` at 142), and a renderer's `ModuleError` once per object (`srcts/mount/output.ts` at 483).
The two conditions that the scheduler writes itself are in `srcts/scheduler/status.ts`: `waitingFor()`, of the phase `status`, and `unsent()`, which has no phase, and each marks its condition with the code of core's notification of it.
Tests capture what core reports with `reports()` from `srcts/testing/reports.ts`, which holds what `report()` queues.

A module that imports core's `Notification` and also shows desktop notifications still calls the browser's constructor as `new Notification()`, since core's type has no value, as TypeScript 5.9 compiles it.
But its type errors would then name two types `Notification`, so such a module imports core's type under another name.
Core keeps the type a module export and never declares it global, since TypeScript would then merge it into the browser's interface.
The type replaces `Note` in `CoreApi`, and the toasts replace the basic frontend's `Notice` and the list of them that `srcts/modules/basic/notices.ts` keeps.

The basic frontend's dialogs are modal: `showModal()` puts each in the top layer, above any `z-index`, and makes the rest of the page inert (`srcts/modules/basic/ui.tsx` at 47).
So the toasts show inside an open dialog, such as through a portal into it, since the toast of an edit that the dialog made would otherwise wait behind it, as the list above the board does today.
A message's toast is a status and a warning's or an error's an alert, which a screen reader reads out at once, as the items of that list are (`srcts/modules/basic/board.tsx` at 126).

A logger in R becomes a function of the message, its level and its package, which also gets `asis`, whether to keep the message's line breaks rather than wrap it.
The one logger in the workspace outside core, `blockr.logger = function(msg, level)` in the tests of blockr.assistant (`tests/testthat/helper-skills.R`), takes the new arguments.
Whether otel logs at all is `otel::is_logging_enabled()`, which is false until otelsdk is configured, as through `OTEL_LOGS_EXPORTER=otlp` and `OTEL_EXPORTER_OTLP_ENDPOINT`.
The OTLP/HTTP exporters of otelsdk 0.3.0 export from a worker thread of opentelemetry-cpp's batch processors, and drop a record when their queue of 2,048 is full, while its file and console exporters write on R's thread, which a deployment avoids for that reason ([src/stdstream.cc](https://github.com/r-lib/otelsdk/blob/main/src/stdstream.cc)).

The client's OpenTelemetry logger and its tracing are a module of core's that core imports only where `otel_client_endpoint` is set, so that a page without telemetry loads none of it.
It builds on `@opentelemetry/sdk-logs`, stable since the JS SDK's 3.0.0, and on `@opentelemetry/exporter-logs-otlp-http`, still marked experimental, which send OTLP's JSON encoding, stable for logs and traces, by `fetch`, about 15 to 20 kB gzipped for logs, and on the 3.x trace SDK, `@opentelemetry/sdk-trace` with its `StackContextManager`, and its OTLP/HTTP exporter ([JS SDK 3.0.0](https://github.com/open-telemetry/opentelemetry-js/releases/tag/v3.0.0)).
The browser's batch processor sends what it holds on `visibilitychange` to hidden, with `fetch`'s `keepalive`.
The Logs API is part of `@opentelemetry/api` from 1.10.0, which replaced `@opentelemetry/api-logs`.
A collector at another origin than the page lists the page's origin in its OTLP/HTTP receiver's `cors.allowed_origins`, and never `*`, since its responses allow credentials.
In R, Shiny's own spans would show mostly the observer through which the transport takes each message, and `SHINY_OTEL_COLLECT=session` keeps them to sessions.
The guide for deployments first tries the setup on a Connect server of 2026.09.0 or later: which of OpenTelemetry's environment variables Connect sets for content that opts in, whether R's log records reach the collector beside Connect while it does, and whether a page reaches that collector under Connect's host name.

</details>
