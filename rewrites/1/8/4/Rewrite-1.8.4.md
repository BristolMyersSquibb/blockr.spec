# The speed benchmark: boards, measurements and runs
Status: review. Design for [Wrap-up](Rewrite-1.8).

One of the design pages of [Wrap-up](Rewrite-1.8): how fast the new stack runs against today's stack on the same boards, where the new stack spends its time, and how a pull request learns that it made the new stack slower.
It shapes the Work items of its section of that part's Work list.
How well the assistant does what users ask is [The assistant's benchmark](Rewrite-1.8.1)'s, and whether the packages work together is [The `blockr` meta-package](Rewrite-1.8.5)'s.

## What must hold

1. The speed benchmark takes named measurements on named boards, on the new stack and on today's stack, in one job on one machine.
   It reports each time with its spread over repeated runs.
2. A comparison with today's stack says, for each measurement and board, whether the new stack meets the bar that [Wrap-up](Rewrite-1.8#problem) sets: faster than today's stack, rather than no slower.
3. Each run reports exact counts beside its times, such as the messages between the page and R and their bytes.
   A change in what the stack does then shows even where its times vary.
4. The boards grow up to the size of the largest real board and beyond, so that the report shows how each time grows with the number of blocks.
5. A profiling run says where the new stack spends its time in each measurement, by span and by function, in the client and in R.
6. A pull request of a package that the speed benchmark covers gets a comparison of its head with its base, as one comment that each run rewrites.
   The comparison blocks no merge.
7. A run names the ref of each package, the versions of R and Chrome, and the machine, so that each number can be traced to what produced it.

## Today

No benchmark measures either stack.
Each measurement so far was taken once, with a script of its own:

- On today's dock, a board of two blocks takes about 5.8 s and 13 busy periods to settle after it mounts.
  The time came from Shiny's busy and idle events on the page ([blockr.dock#397](https://github.com/BristolMyersSquibb/blockr.dock/issues/397)).
- On one R process, a classic Shiny app answered none of one user's updates within 120 s once four other sessions streamed.
  The same updates, sent as data, took a few milliseconds ([blockr#493](https://github.com/BristolMyersSquibb/blockr/discussions/493#discussioncomment-18775537)).
- React Flow drew the clinical data explorer's board, with 99 blocks and 108 links, in a third of the time that G6 took ([Client-drawn DAG](Rewrite-1.3)).
- Loading the 14 blockr packages installed in the workspace took 2.30 s in one R process.
  Of that, 1.86 s went to the meta-package blockr and the six packages that it imports ([Block classes in R](Rewrite-1.1.5)).

On `js-state`, core records OpenTelemetry spans on both sides, once a deployment sends them to a collector ([Tracing](Rewrite-1.1.14#tracing)).
In the client, core records a span for each command, for each evaluation, output and request, and for each step of starting the page and opening a board.
In R, core records a span for each message that R handles, and inside it a span for each phase of an evaluation.
So one trace runs from an edit through R to the reply.
Today's blockr packages record no spans.

Core's page gives end-to-end tests the board, each block's status, the blocks on screen and the notifications, through `blockrTest` in Shiny's test mode ([srcts/modules/blockr-test/index.ts](https://github.com/BristolMyersSquibb/blockr.core/blob/f139384947271f29917687bb90dbf8736e0868eb/srcts/modules/blockr-test/index.ts)).
Core's browser tests drive Chrome through chromote, with the app in another R process ([tests/testthat/helper-browser.R](https://github.com/BristolMyersSquibb/blockr.core/blob/f139384947271f29917687bb90dbf8736e0868eb/tests/testthat/helper-browser.R)).

## Proposal

### The measurements

Each measurement is the time that one step of using an app takes.
The harness takes each step as a user would, clicking and typing on the page through Chrome's input events, and times it:

1. **Starting an app:** from starting R's process until it serves the page.
   On Connect, a session pays this wherever one process serves one session ([State in JS](Rewrite-1#proposal)).
2. **Opening a board:** from loading the page until every output on screen is drawn and no message between the page and R is in flight.
   The time of the first paint is reported beside it.
3. **Switching views:** from clicking the tab of another view of the dock until every output in that view is drawn.
4. **Editing a block:** from changing a value in a block's UI, such as a head block's `n`, until the outputs on screen of that block and of the blocks downstream of it are drawn again.
5. **Adding a block:** from picking a block class in the block picker until the new block's output is drawn.
6. **Sharing an R process:** the time of an edit as in measurement 4, in one session, while k other sessions on the same R process each repeat edits.
   It is taken for k of 0, 1, 2, 4 and 8, as [blockr#493](https://github.com/BristolMyersSquibb/blockr/discussions/493#discussioncomment-18775537) took it.

The harness has a script for each measurement on each stack, since the two stacks draw different pages.
Both scripts do the same thing, as a user sees it.
On the new stack, a measurement ends once no block on screen reads `unevaluated` or `stale` in `blockrTest`, and the output of each block on screen is on the page.
On today's stack, it ends once Shiny is idle and the outputs on screen are drawn, as [blockr.dock#397](https://github.com/BristolMyersSquibb/blockr.dock/issues/397) timed it.
A measurement that passes its cap, two minutes unless it names another, is reported as stopped rather than timed, as the classic Shiny app of [blockr#493](https://github.com/BristolMyersSquibb/blockr/discussions/493#discussioncomment-18775537) was at 120 s.

### The boards

The generated boards hold 10, 30, 100 and 300 blocks.
Their blocks are of core's block classes that both stacks have, such as the dataset, head, subset, merge and scatter plot blocks.
They hold chains and stacks of blocks, spread over several views of the dock.
The harness builds each of them for both stacks from one description of its blocks, links, stacks and views, with each stack's constructors.

The largest real board is the clinical data explorer's, with 99 blocks and 108 links.
It joins once its packages have been ported.
The new stack opens it as the conversion of the file that today's packages save from its script ([The conversion and the migration notes](Rewrite-1.8.3)), so that both stacks open the same board.

### What a run records

Each measurement is taken several times on each version, five times unless the run names another number.
The runs alternate between the versions in one job, so that both versions meet the same load of the machine.
The report gives each time's median and its spread, the range of the middle half of the runs.

Beside the times, each run reports exact counts: the messages between the page and R in each direction, and their bytes, which Chrome's network events give for both stacks alike.
On the new stack, the kind of each message also gives the number of evaluations, outputs and requests that the page sends ([Wire protocol](Rewrite-1.1.9#messages)).
A count that differs between two versions means that one of them does something that the other does not, whatever the load of the machine.

Each run also reports the CPU time that R's process takes during a measurement, the memory of R's process at the end, and the size of the page's JS heap at the end.

### Where the time goes

A profiling run takes each measurement once more, apart from the timed runs, since recording slows down what it records.
It keeps three records:

- Core's spans from both sides, which the harness collects through an OpenTelemetry collector of its own, as a deployment collects them ([Where the records go](Rewrite-1.1.14#where-the-records-go)).
- The page's CPU profile, from Chrome's profiler.
- R's profile of the app's process, from `Rprof()`.

For each measurement, the report adds up the time of each span by its name, and the time of each function.
It lists those that take the most time, each with the package that it belongs to.
A package's own code stays unminified in what it builds ([State in JS](Rewrite-1#conventions)).
So the page's profile names the functions of the blockr packages, while the libraries that they bundle show up by file.

The spans of an edit also show whether R spends time on anything other than evaluating what is demanded and fetching data for what is on screen.
Condition 3 of [State in JS](Rewrite-1#what-must-hold) limits R to that.

Where a function or a span takes a large share of a measurement, and a change could cut it, whoever reads the report files an issue in its package, labeled `js-state`, with the profile that shows it.
The run keeps the profiles, which Chrome's DevTools and profvis open.
Today's stack gets a profiling run as well, whose profiles show what the new stack no longer does.

### Comparing with today's stack

A comparison takes every measurement on every board on both stacks, with today's stack at the refs of main.
For each measurement and board, it says whether the new stack meets the bar (condition 2).
It runs on demand in blockr.bench, for the first time once the new stack opens the generated boards.
Its report stays with the run.

### What a pull request gets

The speed benchmark covers each package whose code runs in its measurements.
At first those are blockr.core, blockr.ui, blockr.dock, blockr.graph and blockr.assistant.
A package of block classes joins once its classes are on the boards.
A pull request to `js-state` of such a package starts a run on each push.
The run takes every measurement on the generated boards of up to 100 blocks, on the pull request's head and on its base.

The comparison only informs.
It reaches the pull request the way the release gate of blockr.ci reaches a release's pull request: through blockr.ci's `sticky-comment` action.
That action keeps one comment and rewrites it on each push, so that the comment always describes the head commit.
The comment gives each time's median on both versions, with their spreads.
It marks each time whose median on the head lies outside its spread on the base, and each count that changed.
A reviewer reads the comment and decides whether a slowdown is acceptable, and no check fails on one.
The comparison can later become a required check, once runs show how much its numbers vary.

### Where it lives

The speed benchmark lives in blockr.bench, beside the assistant's benchmark ([Wrap-up](Rewrite-1.8#benchmarks)).
It shares with the assistant's benchmark the harness that installs the packages at the refs that a run names, serves a board with `serve()` and drives its page.
The harness drives Chrome through chromote, as core's browser tests do.
It starts the app's R process from R anyway, and chromote reaches every part of Chrome's DevTools protocol that a run needs: input events, network events, the profiler and the heap.
Each package that the benchmark covers starts a run from its pull requests, through a reusable workflow that blockr.bench offers.
The run then posts its comment on that pull request.

## Open questions

None.

<details><summary>Notes for implementers</summary>

The protocol's domains that a run needs: `Input` for the user's clicks and typing, `Network` for the WebSocket frames (`Network.webSocketFrameSent` and `Network.webSocketFrameReceived`), `Profiler` for the CPU profile, and `Performance.getMetrics()` for `JSHeapUsedSize`.
A run that wants a slower client throttles the page through `Emulation.setCPUThrottlingRate`.
The new stack's frames carry the wire protocol's messages, whose `kind` sorts them, while today's carry Shiny's inputs, values and custom messages.

The harness starts the app's process with `callr::r_bg()` on a port from `httpuv::randomPort()`, as core's `start_transport_app()` does, and reads the process's CPU time and memory with `ps::ps_cpu_times()` and `ps::ps_memory_info()`.
R exports its spans through otelsdk to the address in `OTEL_EXPORTER_OTLP_ENDPOINT`, and the page to the address in the blockr option `otel_client_endpoint`, so that both reach the harness's collector, such as the OpenTelemetry Collector with its `file` exporter.

To time today's stack, [blockr.dock#397](https://github.com/BristolMyersSquibb/blockr.dock/issues/397) launched the app with `wait = FALSE` and attached listeners to `shiny:busy`, `shiny:idle`, `shiny:value` and `shiny:inputchanged` as early as possible.

The comment goes through blockr.ci's `sticky-comment` action ([action.yaml](https://github.com/BristolMyersSquibb/blockr.ci/blob/51647f31367c4f5e3187141d1a2b3204e08a5216/.github/actions/sticky-comment/action.yaml)), with a marker of its own, such as `<!-- speed-benchmark -->`, as the release gate's comment does ([release-gate.yaml](https://github.com/BristolMyersSquibb/blockr.ci/blob/51647f31367c4f5e3187141d1a2b3204e08a5216/.github/workflows/release-gate.yaml)).
A concurrency group per pull request lets a new push cancel the run of the push before it.

</details>
