# Notifications and logging: what the user is told and what is logged where
Status: draft. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): how the user learns of a message, warning or error, whether R raised it as a condition or the client threw it as an exception, through one member of `CoreApi`, and what is logged where, in R and in the client, with the telemetry that either may record.
It shapes sending core's own failures to the frontend ([blockr.core#539](https://github.com/BristolMyersSquibb/blockr.core/issues/539)) and what core's basic frontend shows ([blockr.core#507](https://github.com/BristolMyersSquibb/blockr.core/issues/507)), and the notifications of [The dock's services](Rewrite-1.2.6) build on it.
Once settled, it takes over what [Drawing the board](Rewrite-1.1.8#what-core-gives-plugins) and [Plugins](Rewrite-1.1.12#what-a-frontend-offers-other-plugins) say of `notifications`, while how a reply carries a block's conditions stays [Wire protocol](Rewrite-1.1.9#evaluating-a-block)'s, how a block's status holds them [Evaluation in the client](Rewrite-1.1.10#statuses)'s, and how a frontend draws [Drawing the board](Rewrite-1.1.8)'s.
It is a seed, written from the discussion of [blockr.core#539](https://github.com/BristolMyersSquibb/blockr.core/issues/539), and nothing on it is agreed yet, its term included ([Open questions](#open-questions)).

## What must hold

1. Every message, warning and error that the user should see reaches the frontend through one member of `CoreApi`, whether R raised it or the client did, core or a plugin, so that a frontend draws them all from one place, where today's `board$conditions` holds only those of blocks.
2. Each holds what a frontend needs to choose how to show it without reading its message: its severity, its class, who raised it, and what it concerns, a block, a board option, a plugin, a package or the board.
3. Each lasts as long as its cause: a block's conditions until the block's next reply replaces them or the block leaves the board, and the rest until whoever raised them withdraws them or the next board opens.
4. A frontend reads those that hold as it draws, and hears each one that comes or goes, so that one raised before it draws, such as a startup module's failure, still reaches the user.
5. The frontend alone decides how each shows, while core draws only what no frontend can: the error in the element of a module that cannot draw ([UI modules in JS](Rewrite-1.1.7#the-contract)), and a page that cannot start.
6. Core holds them outside the board, as it holds which block has focus, so that no file saves them and no undo brings one back ([Board objects](Rewrite-1.1.1#what-lives-where)).
7. What fails in the client's code is logged in the console with its stack, and what fails in R's own machinery in R's log, whether or not the user is also told, so that whoever can fix it finds it.
8. Nothing leaves the page or the R process as telemetry unless the deployment sets where it goes.

## Today

On main, `board_server()` gathers the conditions of every block into one reactive data frame, `board$conditions`, with a row per active condition and the columns `block`, `phase`, `severity`, `message` and `id`, the last a digest of the message ([R/board-server.R#L11-L19](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L11-L19)).
The `notify_user` plugin shows a toast for each row whose severity `show_conditions` names, keyed by block, severity and id, and removes it once its condition goes ([R/plugin-notification.R#L76-L140](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-notification.R#L76-L140)).
Everything else that core tells the user passes it by: 27 calls of `notify()`, core's wrapper of Shiny's `showNotification()`, show a board update that fails ([R/board-server.R#L403](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L403)) and what `manage_blocks`, `manage_links`, `manage_stacks`, `edit_block` and `ctrl_block` refuse or fail at, which [blockr.core#93](https://github.com/BristolMyersSquibb/blockr.core/issues/93) puts as "Board notifications are not centrally organized."
Each call also logs its message, at the level of its severity, unless it passes `log = FALSE` ([R/utils-shiny.R#L40-L71](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/utils-shiny.R#L40-L71)).

R logs through core's own `write_log()` and its wrappers, `log_fatal()` to `log_trace()`, as the blockr options `log_level`, `logger`, `log_time` and `log_mem` set, and its default logger, `cat_logger()`, writes errors to standard error and the rest to standard output, which Connect keeps in the content's log ([R/utils-logging.R#L25-L104](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/utils-logging.R#L25-L104), [#L200-L252](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/utils-logging.R#L200-L252)).
Main's `blockr_deser()` logs what it drops and tells the user nothing ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)).
On `js-state`, the evaluator and the Shiny transport log what they ignore, at debug or warn, and what they fail at, at error, such as a reply they cannot send ([R/evaluator-class.R#L200-L255](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/evaluator-class.R#L200-L255), [#L440-L490](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/evaluator-class.R#L440-L490), [R/shiny-transport.R#L140-L160](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/R/shiny-transport.R#L140-L160)), while R logs none of the conditions it sends in a reply.

In the client, `report()` throws what it is given from a microtask, so that it reaches the console as an uncaught error, and core calls it at 33 places, for what the user should hear of and for what only a developer should alike ([srcts/util/util.ts#L26-L33](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/srcts/util/util.ts#L26-L33)).
The `notifications` member of `CoreApi` hands each `Note`, a message with a severity, to its subscribers and keeps none, so that one sent before the frontend subscribes reaches nobody ([srcts/core/core.ts#L192-L223](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/srcts/core/core.ts#L192-L223)).
Core's basic frontend lists above the board only the edits that the store refused ([srcts/modules/basic/notices.ts#L1-L20](https://github.com/BristolMyersSquibb/blockr.core/blob/87263e40e313e7c5fed5021f66d9966420c18bb4/srcts/modules/basic/notices.ts#L1-L20)).

Shiny imports otel, the OpenTelemetry API for R, and since 1.12.0 records spans of sessions, reactive updates, reactives, observers and outputs wherever `otel::is_tracing_enabled()` holds, as it does once otelsdk is configured to export, and logs of fatal and unhandled errors, sanitized unless `shiny.otel.sanitize.errors` is `FALSE` ([NEWS.md#L1-L56](https://github.com/rstudio/shiny/blob/b5da7868fa0c2924bcb6febad4b78d33da1fdb86/NEWS.md#L1-L56)).
Core records no telemetry of its own, in R or in the client.

## Proposal

### Notifications

A notification is a message, warning or error that the user should see, whoever raised it: R, as a condition while it evaluates a block or makes its output, core, where it fails at something that the user asked for or that the board needs, or a plugin, the frontend among them.
The `notifications` member of `CoreApi` holds every notification of the open board, which a frontend follows as it follows focus, through a getter and a subscription ([State in JS](Rewrite-1#principles)):

```ts
interface Notification {             // its name is to settle, since the DOM has a global Notification
  id: string;                        // the same while it holds, so that a frontend keeps what the user dismissed
  severity: "message" | "warning" | "error";
  class: string[];                   // R's class for one that R raised, and core's own, such as ["blockr_module_error", "blockr_error", "error"]
  message: string;
  origin: Origin;                    // who raised it, "r", "core" or a plugin's id, as a delta names its origin
  phase?: Phase;                     // for one that R raised, what raised it, as on the protocol's Condition
  block?: BlockId;                   // what it concerns, none of these for the board
  option?: OptionId;
  plugin?: PluginId;
  package?: string;                  // the package of what it concerns, or of a startup module
}

notifications: {
  notify(n: Omit<Notification, "id">): () => void;                   // raises one, and returns what withdraws it
  get(): readonly Notification[];                                    // those that hold, the same array until one comes or goes
  subscribe(fn: (all: readonly Notification[]) => void): () => void;
};
```

A frontend reads `get()` as it draws and follows `subscribe()` from then on, the pair that React's `useSyncExternalStore` takes.
Core makes a block's notifications from the conditions of its status, deriving them from the scheduler rather than copying them, so that `scheduler.status()` keeps a block's conditions for the hosts that read them ([UI modules in JS](Rewrite-1.1.7#the-contract)) and the two never differ.
Core raises its own where it fails at something that the user asked for or that the board needs, each naming what failed and what needed it:

| What | Concerns | Goes when |
|---|---|---|
| A block's conditions, from its status | The block | Its next reply replaces them, or it leaves the board |
| An output that R could not make | The block | Its next output arrives |
| A module that cannot draw: a block's UI, a renderer, a board option's UI, a plugin's UI or the frontend | The block, board option or plugin, with the module's package | The next board opens |
| A board option that no loaded package defines, or whose default fails or does not fit its schema ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)) | The board option | The next board opens |
| An `onChange` that throws | The board option | Its next call returns |
| A startup module that fails to load or throws in `initialize()` ([UI modules in JS](Rewrite-1.1.7#startup-modules)) | Its package | The next board opens |
| A board that a startup module named, which core did not open, under the load lock or where two named one ([Drawing the board](Rewrite-1.1.8#starting-the-page)) | The packages | The next board opens |
| A plugin's `start` that throws ([Plugins](Rewrite-1.1.12#running-a-plugin)) | The plugin | The next board opens |
| A board that fails to open after core's check, so that core opens the one before again | The board | The next board opens |
| What the store dropped as the board opened ([Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt)) | The block, plugin or board option, with its package | The next board opens |
| A plugin's own, through `notify()` | What the plugin names | The plugin withdraws it, or the next board opens |

A failure that rejects a call goes to the caller, which tells the user where it should: the store refuses an edit by rejecting the command, and a request that fails rejects with the reply's conditions ([UI modules in JS](Rewrite-1.1.7#the-contract)), so core's basic frontend raises a notification for each of its own edits that the store refuses, in place of the list it keeps today.
A failure inside core's own machinery, such as a subscriber that throws or a demand whose function throws, reaches no user, since no user can act on it, and is logged ([Logging](#logging)).
Core logs every failure that it raises a notification for as well, with its stack, which a notification does not carry.

Core withdraws every notification as the next board opens, since an opening ends everything core runs for the board ([Drawing the board](Rewrite-1.1.8#opening-a-board)), and a block's as the block leaves the board.
The frontend draws them as it chooses, by their class, origin and what they concern: core's basic frontend draws a block's on its card and the rest above the board, each until the user dismisses it, showing the severities that `show_conditions` names, while the dock draws them as [The dock's services](Rewrite-1.2.6) will have it.

### Logging

R logs through `write_log()`, as today: its evaluator and transport log what they fail at, at error, naming the request where there is one, and what they ignore, at warn or debug, all of which goes to the R process's standard output and error, and so to the content's log on Connect.
The client logs to the console: `report()` throws each failure that core catches from a microtask, with its stack, as now, whether or not core also raises a notification for it.
Which tools log, at which levels, and whether the client's failures reach R's log are open ([Open questions](#open-questions)).

### Telemetry

Core would record telemetry through OpenTelemetry's APIs, otel in R, which Shiny already imports, and `@opentelemetry/api` in the client, both of which record nothing until the deployment configures an SDK and where it exports, which keeps to condition 8.
The spans worth having are an edit in the client, through the evaluations it causes, to their replies, and in R each evaluation and request, with the block's id, registry id and revision as attributes, joined into one trace by a context that each evaluation request carries, as the `traceparent` of [Trace Context](https://www.w3.org/TR/trace-context/) does in HTTP.
That context is a property of the protocol's messages, which [Wire protocol](Rewrite-1.1.9) would gain.

## Open questions

- The term: this page proposes "notification" for every message, warning and error that the user should see, with a row in the [Glossary](Glossary), since R raises conditions and the client throws exceptions, of which some reach the user and others are only logged, so the word for what reaches the user names neither, and since the pages use it in that sense already ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend), [Plugins](Rewrite-1.1.12#what-a-frontend-offers-other-plugins), [Client-drawn dock and extensions](Rewrite-1.2)).
  It blocks every use of the word here, and the user's agreement settles it, with the name of the type, which the DOM's `Notification` makes awkward, and of `origin`, which takes the sense that a delta gives it ([Board updates](Rewrite-1.1.2#the-store)).
- The classes of core's own notifications, such as one for a module that cannot draw, which a frontend matches to choose how to draw them, block [blockr.core#539](https://github.com/BristolMyersSquibb/blockr.core/issues/539), and listing them here settles them.
- Whether a condition that a block's next reply raises again is the same notification, by a digest of its class and message, as today's `id` is a digest of the message, so that one the user dismissed stays dismissed, blocks `id`, and the user's choice settles it.
- Whether core raises a notification for each object that the store dropped, in place of each frontend's package subscribing to the store to learn of them, would change [Board objects](Rewrite-1.1.1#objects-that-cannot-be-rebuilt), [Drawing the board](Rewrite-1.1.8#starting-the-page) and [blockr.core#507](https://github.com/BristolMyersSquibb/blockr.core/issues/507), and the user's choice settles it.
- Whether `show_conditions` filters every notification by severity, or only those that R raised, as it filters only blocks' conditions today, and whether its name still fits, blocks what core's basic frontend shows.
- Whether an output that R could not make is a notification, or stays its renderer's alone, through the host's `error()`, which keeps the output it held ([UI modules in JS](Rewrite-1.1.7#the-contract)), blocks that row of the table.
- Whether a block's UI and a renderer raise notifications through their hosts, concerning their block, as a plugin does through `CoreApi`, so that a renderer written with the React SDK shows what its error boundary catches, which reaches only the console today, blocks the hosts' types.
- Whether the client's failures reach R's log, through a message kind of the protocol that the client sends at a bounded rate, so that an operator on Connect sees what failed in a user's browser, costs a message kind ([Wire protocol](Rewrite-1.1.9#what-must-hold)), and the user's choice settles it.
- Whether the client logs at levels, such as the protocol's messages at debug, as `options(shiny.trace = TRUE)` logs Shiny's, and whether the blockr option `log_level`, which R reads, sets them through `blockrOption()`.
- Whether `CoreApi` gives packages a logger that names the package, as `write_log()` does in R, so that the client has one toolkit for logging as R does ([State in JS](Rewrite-1#principles)).
- Whether R logs the conditions it sends, at debug, so that R's log shows why a block failed, as main's `notify()` logs what it shows.
- Which tools log: whether R keeps `write_log()`, moves to a package such as logger or lgr, or writes through otel's logs, which also reach a collector where one is configured, and whether the client has the console alone.
- Whether to record telemetry now, in R first, where otel brings no dependency that Shiny does not, or in the client too, where `@opentelemetry/api` and a context in the protocol's messages would, which a spike that traces one evaluation from an edit to its reply settles.

<details><summary>Notes for implementers</summary>

Core's calls of `report()` on `js-state`, at `87263e4`, sorted by this page.
For the user: `srcts/core/start.ts` at lines 376, 451, 465, 469 and 479, the startup modules and the board they name; `srcts/core/frontends.ts` at 96 and 129, the frontend's module; `srcts/core/plugins.ts` at 222 and 265, a plugin's `start` and its UI; `srcts/mount/block.ts` at 142 and 346, board options and a block's UI; `srcts/mount/option.ts` at 204, a board option's UI; `srcts/mount/output.ts` at 483 and 533, a renderer; and `srcts/core/core.ts` at 183, an `onChange`.
For the console alone: `srcts/core/start.ts` at 167, 224, 388, 441 and 565; `srcts/core/plugins.ts` at 198, a plugin left out for a board option whose failure is reported already; `srcts/core/page.ts` at 46, a page that cannot start, which shows in its element too; `srcts/protocol/client.ts` at 297 and 453; `srcts/scheduler/scheduler.ts` at 582 and 630; `srcts/mount/answers.ts` at 135; `srcts/mount/shared.ts` at 54; `srcts/mount/load.ts` at 103, a stylesheet; `srcts/mount/block.ts` at 461; `srcts/core/core.ts` at 103; `srcts/store/store.ts` at 226; and `srcts/react/module.tsx` at 123, the error boundary of a renderer written with the React SDK.
Board options' failures are reported once per board and message already (`srcts/mount/block.ts` at 142), and a renderer's `ModuleError` once per object (`srcts/mount/output.ts` at 483).

</details>
