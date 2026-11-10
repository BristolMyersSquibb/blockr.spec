# Notifications and logging: what the user is told and what is logged where
Status: draft. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how the user learns of a message, warning or error, and what R and the client log.
Every message, warning and error that the user should see reaches the frontend through one member of `CoreApi`, whether R raised it as a condition, core failed at something, or a plugin sent it.
It shapes sending core's own failures to the frontend ([blockr.core#539](https://github.com/BristolMyersSquibb/blockr.core/issues/539)) and what core's basic frontend shows ([blockr.core#507](https://github.com/BristolMyersSquibb/blockr.core/issues/507)), and the notifications of [The dock's services](Rewrite-1.2.6) build on it.
Once settled, it takes over what [Drawing the board](Rewrite-1.1.8#what-core-gives-plugins) and [Plugins](Rewrite-1.1.12#what-a-frontend-offers-other-plugins) say of `notifications`.
How a reply carries a block's conditions stays [Wire protocol](Rewrite-1.1.9#evaluating-a-block)'s, how a block's status holds them [Evaluation in the client](Rewrite-1.1.10#statuses)'s, and how a frontend draws the board [Drawing the board](Rewrite-1.1.8)'s.

## What must hold

1. Every message, warning and error that the user should see reaches the frontend through one member of `CoreApi`, whoever raised it: R, core or a plugin.
   So a frontend draws them all from one place, where today's `board$conditions` holds only those of blocks.
2. Each holds what a frontend needs to choose how to show it without reading its message: its severity, its class, who raised it, and what it concerns, a block, a board option, a plugin, a package or the board.
3. Each lasts as long as its cause.
   A block's conditions last until the block's next reply replaces them or the block leaves the board, and the rest until whoever raised them withdraws them or the next board opens.
4. A frontend reads those that hold as it draws, and hears each one that comes or goes.
   So one raised before it draws, such as a startup module's failure, still reaches the user.
5. The frontend alone decides how each shows.
   Core draws only what no frontend can: the error in the element of a module that cannot draw ([UI modules in JS](Rewrite-1.1.7#the-contract)), and the error of a page that cannot start or whose frontend cannot draw.
6. Core holds them outside the board, as it holds which block has focus, so that no file saves them and no undo brings one back ([Board objects](Rewrite-1.1.1#what-lives-where)).
7. What fails in the client's code is logged in the console with its stack, and what fails in R's own machinery in R's log, whether or not the user is also told, so that whoever can fix it finds it.
8. R's log holds every condition that R sends the client, as main's log holds every condition that a block raises.
9. Nothing leaves the page or the R process as telemetry unless the deployment sets where it goes.

## Today

On main, `board_server()` gathers the conditions of every block into one reactive data frame, `board$conditions`, with a row per active condition and the columns `block`, `phase`, `severity`, `message` and `id`, the last a digest of the message ([R/board-server.R#L11-L19](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L11-L19)).
The `notify_user` plugin shows a toast for each row whose severity `show_conditions` names, warnings and errors unless a board option or a blockr option names others.
A toast stays until the user closes it or its condition goes.
Toasts are keyed by block, severity and `id`, so a toast that the user closed stays closed while the same condition holds, and a condition that a block raises twice shows once ([R/plugin-notification.R#L76-L141](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-notification.R#L76-L141)).
Everything else that core tells the user passes it by: 27 calls of `notify()`, core's wrapper of Shiny's `showNotification()`, show a board update that fails ([R/board-server.R#L403](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L403)) and what `manage_blocks`, `manage_links`, `manage_stacks`, `edit_block` and `ctrl_block` refuse or fail at.
The issue [blockr.core#93](https://github.com/BristolMyersSquibb/blockr.core/issues/93) puts this as "Board notifications are not centrally organized."
Each call of `notify()` also logs its message, at the level of its severity, unless it passes `log = FALSE` ([R/utils-shiny.R#L40-L71](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-shiny.R#L40-L71)).

R logs through core's own `write_log()` and its wrappers, `log_fatal()` to `log_trace()`, as the blockr options `log_level`, `logger`, `log_time` and `log_mem` set, at info and above unless `log_level` names another level ([R/utils-logging.R#L25-L104](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/utils-logging.R#L25-L104)).
Its default logger, `cat_logger()`, writes errors to standard error and the rest to standard output, which Connect keeps in the content's log ([#L200-L252](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/utils-logging.R#L200-L252)).
On main, the handlers that catch a block's conditions log each one, a message at info, a warning at warn and an error at error ([R/utils-cnd.R#L157-L200](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-cnd.R#L157-L200)), so main's log holds every condition that a block raises.
Main's `blockr_deser()` logs what it drops and tells the user nothing ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)).
On `js-state`, the evaluator and the Shiny transport log what they ignore, at debug or warn, and what they fail at, at error, such as a reply they cannot send ([R/evaluator-class.R#L200-L255](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/evaluator-class.R#L200-L255), [#L440-L490](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/evaluator-class.R#L440-L490), [R/shiny-transport.R#L140-L160](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/shiny-transport.R#L140-L160)).
But R logs none of the conditions that it sends in a reply, so a block that fails leaves no line in R's log.

In the client, `report()` throws what it is given from a microtask, so that it reaches the console as an uncaught error ([srcts/util/util.ts#L26-L33](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/srcts/util/util.ts#L26-L33)).
Core calls it at 33 places, alike for what the user should hear of and for what only a developer should.
The `notifications` member of `CoreApi` hands each `Note`, a message with a severity, to its subscribers and keeps none, so that a note sent before the frontend subscribes reaches nobody ([srcts/core/core.ts#L192-L223](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/srcts/core/core.ts#L192-L223)).
Core's basic frontend lists above the board only the edits that the store refused ([srcts/modules/basic/notices.ts#L1-L20](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/srcts/modules/basic/notices.ts#L1-L20)), and draws a block's conditions on its card, from the block's status ([srcts/modules/basic/card.tsx#L214-L228](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/srcts/modules/basic/card.tsx#L214-L228)).

Shiny imports otel, the OpenTelemetry API for R.
Since 1.12.0, Shiny records spans of sessions, reactive updates, reactives, observers and outputs, and logs of fatal and unhandled errors, wherever `otel::is_tracing_enabled()` holds, as it does once otelsdk is configured to export ([NEWS.md#L1-L56](https://github.com/rstudio/shiny/blob/b5da7868fa0c2924bcb6febad4b78d33da1fdb86/NEWS.md#L1-L56)).
It sanitizes the errors it logs unless `shiny.otel.sanitize.errors` is `FALSE`.
Core records no telemetry of its own, in R or in the client.

## Proposal

### Notifications

A notification is a message, warning or error that the user should see, whoever raised it.
R raises one as a condition while it evaluates a block or makes its output, core where it fails at something that the user asked for or that the board needs, and a plugin through `CoreApi`, the frontend among them.
The term names what reaches the user rather than how it arose.
R raises conditions and the client throws exceptions, and only some of either reach the user, so "condition" keeps R's sense ([Glossary](Glossary)).
A notification's `origin` names who raised it, as a delta's origin names who made it ([Board updates](Rewrite-1.1.2#the-store)).

The `notifications` member of `CoreApi` holds every notification of the open board.
A frontend follows them as it follows focus, through a getter and a subscription ([UI modules in JS](Rewrite-1.1.7#the-contract)):

```ts
interface Notification {             // its name is to settle (Open questions)
  id: string;                        // the same while it holds, so that a frontend keeps what the user dismissed
  severity: "message" | "warning" | "error";
  class: string[];                   // a condition's class, or core's own, such as ["module_failed", "blockr_error", "error", "condition"]
  message: string;
  origin: Origin;                    // who raised it: "r", "core" or a plugin's id
  phase?: Phase;                     // what raised a block's condition, as on the protocol's Condition
  block?: BlockId;                   // what it concerns, none of these for the board
  option?: OptionId;
  plugin?: PluginId;
  package?: string;                  // the package whose code failed, such as a module's or a startup module's
}

notifications: {
  notify(n: Omit<Notification, "id">): () => void;                   // raises one, and returns what withdraws it
  get(): readonly Notification[];                                    // those that hold, the same array until one comes or goes
  subscribe(fn: (all: readonly Notification[]) => void): () => void;
};
```

A frontend reads `get()` as it draws and follows `subscribe()` from then on, the pair that React's `useSyncExternalStore` takes.
Whoever raises a notification gives its origin and its class, since `CoreApi` is one object for every plugin and cannot tell who calls it.
The class lets a frontend choose how to draw a notification, such as a button that reloads the page for `page_reload_needed`.
The origin lets a frontend say who raised one, and lets a plugin find its own.

Core makes a block's notifications from the conditions of its status, one for each, and derives them from the scheduler rather than copying them.
So `scheduler.status()` keeps a block's conditions for the frontends and hosts that read them ([UI modules in JS](Rewrite-1.1.7#the-contract)), and the two never differ.
Their origin is `"r"`, since R raised them.
The scheduler writes two conditions itself, the message of a block that waits and the error of an evaluation that the transport could not send, and those have the origin `"core"` ([Evaluation in the client](Rewrite-1.1.10#statuses)).
A block's notification takes its id from the block, the severity, the class and the message.
So the same condition in the block's next reply keeps its id, and one that the user dismissed stays dismissed, as a toast that the user closed stays closed today.
Two conditions of one reply that share all four are one notification, as today's toasts show such a condition once.
Where R cannot make a block's output, core raises a notification with the condition that the output's host gives through `error()`, concerning the block, until the block's next output arrives ([UI modules in JS](Rewrite-1.1.7#the-contract)).

Core raises its own notifications where it fails at something that the user asked for or that the board needs.
Each names what failed and what needed it, and its class starts with the class that the table gives, followed by `blockr_error`, `error` and `condition` for an error, or by `blockr_warning`, `warning` and `condition` for a warning, as R's classes run:

| What | Severity and class | Concerns | Goes when |
|---|---|---|---|
| A module that cannot draw: a block's UI, a renderer, a board option's UI or a plugin's UI ([UI modules in JS](Rewrite-1.1.7#the-contract)) | Error, `module_failed` | The block, board option or plugin, with the module's package | The next board opens, or the block leaves the board |
| A board option that does not go onto the board, since no loaded package defines it or its default fails or does not fit its schema ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)) | Error, `board_option_failed` | The board option | The next board opens |
| An `onChange` that throws ([Board options and blockr options](Rewrite-1.1.13#defining-a-board-option)) | Error, `on_change_failed` | The board option, with its package | Its next call returns |
| A startup module that fails to load or throws in `initialize()` ([UI modules in JS](Rewrite-1.1.7#startup-modules)) | Error, `startup_module_failed` | Its package | The next board opens |
| A plugin's `start` that throws ([Plugins](Rewrite-1.1.12#running-a-plugin)) | Error, `plugin_start_failed` | The plugin, with its class's package | The next board opens |
| A board that a startup module named, which the load lock keeps core from opening ([Drawing the board](Rewrite-1.1.8#starting-the-page)) | Warning, `board_open_locked` | The package that named it | The next board opens |
| A board that core could not open: one that a startup module named but that holds no JSON or fails to open, the boards that two startup modules named, or one that fails to open after core's check, so that core opens the board before again ([Drawing the board](Rewrite-1.1.8#opening-a-board)) | Error, `board_open_failed` | The package that named it, or else the board | The next board opens |
| A later reply to `hello` that names a package at another version than the page loaded, for which core asks the user to reload the page ([UI modules in JS](Rewrite-1.1.7#startup-modules)) | Warning, `page_reload_needed` | The board, naming the packages | The next board opens, which raises it again while the versions differ |
| What the store dropped as the board opened ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)) | Warning, `board_objects_dropped` | The board, naming each object with its package | The next board opens |

Core logs every failure that it raises a notification for as well, with its stack, which a notification does not carry ([Logging](#logging)).
A module that cannot draw also shows its error in its element, so that the user sees which spot failed.
The frontend's own module is the exception: where it cannot draw, no frontend runs to draw a notification, so core shows the error in the page's element alone, as it does for a page that cannot start.

A failure that a call returns goes to the caller, which tells the user where it should.
The store throws what refuses an edit, a command rejects with it, and a request that fails rejects with the reply's conditions ([UI modules in JS](Rewrite-1.1.7#the-contract)).
So core's basic frontend raises a notification of its own for each of its edits that the store or the command registry refuses, in place of the list it keeps today.
It is an error of the class `edit_refused`, with the origin `"core"`, and concerns the block that the edit names, if any.
A board that fails to open after core's check is an exception.
Its `store.open()` rejects, but the opening has ended the code that called it, so core raises the notification itself.
A failure inside core's own machinery, such as a subscriber that throws or a demand whose function throws, reaches no user, since no user can act on it, and is only logged.

Core withdraws every notification as the next board opens, since an opening ends everything core runs for the board ([Drawing the board](Rewrite-1.1.8#opening-a-board)).
It withdraws every notification that concerns a block as the block leaves the board, and a plugin's own as the plugin withdraws it.

### Core's basic frontend

A frontend draws notifications as it chooses, by their class, origin and what they concern, and the dock draws them as [The dock's services](Rewrite-1.2.6) will have it.
Core's basic frontend shows each notification once, next to what it concerns:

- A block's card lists the notifications that concern the block, of the severities that core's `show_conditions` board option names, which are warnings and errors unless a script, a file or the user sets others.
  It leaves out what core or the renderer already shows in an element of the card: a module that cannot draw, and an output that R could not make.
- Above the board, it lists every other notification, whatever its severity, each until the user dismisses it, rather than as a toast that fades, since an error that vanishes after a few seconds is easy to miss.

So `show_conditions` filters what a card lists, as it filters blocks' conditions today, and keeps its name, since a card lists mostly the block's conditions.
The basic frontend keeps the ids of the notifications that the user dismissed, for the opening.

### Logging

R logs through `write_log()`, as today, and so to the R process's standard output and standard error, which Connect keeps in the content's log.
An app that wants the lines elsewhere sets the blockr option `logger` to a function of its own, as today.
The evaluator and the transport log what they fail at, at error, naming the request where there is one, and what they ignore, at warn or debug.
R also logs every condition that it sends in a reply, of an evaluation, an output or a request, at the level of its severity: a message at info, a warning at warn and an error at error.
Each line names the block and its revision, so that R's log holds every condition that a block raises, as main's log does (Today).

The client logs to the console.
Core reports each failure that nobody waits on through `report()`, which throws it from a microtask with its stack, as now, whether or not core also raises a notification for it.
Core's client keeps no logger and no levels of its own: core logs only what fails, and packages log to the console as any JS does, whose levels the browser's developer tools filter.
A logger can join `CoreApi` later as a new member, without a new major, once a package needs one ([UI modules in JS](Rewrite-1.1.7#the-contract)).
Whether the client's failures also reach R's log is open ([Open questions](#open-questions)).

### Telemetry

Core would record telemetry through OpenTelemetry's APIs: otel in R, which Shiny already imports, and `@opentelemetry/api` in the client.
Both record nothing until the deployment configures an SDK and where it exports, which keeps to condition 9.
The spans worth having are an edit in the client, through the evaluations it causes, to their replies, and in R each evaluation and request, with the block's id, registry id and revision as attributes.
A context that each evaluation request carries would join them into one trace, as the `traceparent` of [Trace Context](https://www.w3.org/TR/trace-context/) does in HTTP.
That context would be a property of the protocol's messages, which a later minor version of [Wire protocol](Rewrite-1.1.9#versions) can add, since both sides ignore properties they do not know.
Whether to record telemetry now is open ([Open questions](#open-questions)).

## Open questions

- The name of the type, since a type named `Notification` shadows the DOM's global of that name in each module that imports it.
  It blocks the code of [blockr.core#539](https://github.com/BristolMyersSquibb/blockr.core/issues/539), and a name that the user agrees settles it.
- Whether core raises the notification for what the store dropped as a board opened, in place of each frontend's package subscribing to the store to learn of it.
  It would change [Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt), [Drawing the board](Rewrite-1.1.8#starting-the-page) and [blockr.core#507](https://github.com/BristolMyersSquibb/blockr.core/issues/507), and the user's choice settles it.
- Whether the client's failures reach R's log, through a message kind of the protocol that the client sends at a bounded rate, so that an operator on Connect sees what failed in a user's browser.
  It costs a message kind ([Wire protocol](Rewrite-1.1.9#messages)), and the user's choice settles it.
- Whether to record telemetry now, in R first, where otel brings no dependency that Shiny does not, or in the client too, where `@opentelemetry/api` and a context in the protocol's messages would.
  The user's choice settles it, and a spike that traces one evaluation from an edit to its reply would settle how.

<details><summary>Notes for implementers</summary>

Core's calls of `report()` on `js-state`, at `87263e4`, sorted by this page.
Those that become notifications: `srcts/core/start.ts` at lines 376, 451, 465, 469 and 479, the startup modules and the boards they name, and at 565, the request to reload the page; `srcts/core/plugins.ts` at 222 and 265, a plugin's `start` and its UI; `srcts/mount/block.ts` at 142 and 346, board options and a block's UI; `srcts/mount/option.ts` at 204, a board option's UI; `srcts/mount/output.ts` at 483 and 533, a renderer; and `srcts/core/core.ts` at 183, an `onChange`.
Those that core shows in the page's element: `srcts/core/frontends.ts` at 96 and 129, the frontend's module, and `srcts/core/page.ts` at 46, a page that cannot start.
Those for the console alone: `srcts/core/start.ts` at 167, 224, 388 and 441; `srcts/core/plugins.ts` at 198, a plugin left out for a board option whose failure is reported already; `srcts/protocol/client.ts` at 297 and 453; `srcts/scheduler/scheduler.ts` at 582 and 630; `srcts/mount/answers.ts` at 135; `srcts/mount/shared.ts` at 54; `srcts/mount/load.ts` at 103, a stylesheet; `srcts/mount/block.ts` at 461; `srcts/core/core.ts` at 103; `srcts/store/store.ts` at 226; and `srcts/react/module.tsx` at 123, the error boundary of a renderer written with the React SDK, which shows what it caught in the renderer's element.
Board options' failures are reported once per board and message already (`srcts/mount/block.ts` at 142), and a renderer's `ModuleError` once per object (`srcts/mount/output.ts` at 483).
The two conditions that the scheduler writes itself are in `srcts/scheduler/status.ts`: `waitingFor()`, of the phase `status`, and `unsent()`, which has no phase.
Tests capture what core reports with `reports()` from `srcts/testing/reports.ts`, which holds what `report()` queues.

</details>
