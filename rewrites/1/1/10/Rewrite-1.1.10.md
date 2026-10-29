# Evaluation in the client: versions, demand and statuses
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): what the client tracks about evaluation, and the API front-ends and extensions use to ask for it. It builds on the [board objects](Rewrite-1.1.1), [board updates](Rewrite-1.1.2) and [wire protocol](Rewrite-1.1.9) proposals, and shapes building the client scheduler, an item in the Work list of [Client-owned board state](Rewrite-1.1#work). The messages that carry an evaluation are the wire protocol's, a front-end declares that it is lazy as [Front-ends and extension points](Rewrite-1.1.8#registering-a-front-end) has it, and core fetches and draws a block's output as [UI modules in JS](Rewrite-1.1.7#the-contract) has it. It moves into the client the demand and statuses that today's board server has from [blockr#489](https://github.com/orgs/BristolMyersSquibb/discussions/489) and [blockr#488](https://github.com/orgs/BristolMyersSquibb/discussions/488), and keeps the statuses' names.

## What must hold

1. A board evaluates every block, as boards do today, unless its front-end is lazy and demands only the blocks it shows.
2. A board edit costs no R time beyond evaluating what is demanded and fetching outputs for what is on screen, except what an app has R evaluate in the background, which starts only while R has nothing demanded to evaluate.
3. Any component can demand a block or invalidate one without knowing who else does, and without saying why.
4. A block's status, conditions, expression and summary read the same whether or not it is demanded, as they do on today's board ([blockr#488](https://github.com/orgs/BristolMyersSquibb/discussions/488)), so whatever reads neither `stale` nor `unevaluated` holds for the block's current version.
5. A block that must run with nothing on screen, such as a write block in auto mode, runs under a lazy front-end too, and a component that needs current results, such as the code export, gets them without putting a block on screen.
6. At startup, the blocks a lazy front-end shows and everything upstream of them are evaluated before any other block, so that first paint waits for no block off screen, as today's core builds their servers first ([blockr.core#243](https://github.com/BristolMyersSquibb/blockr.core/issues/243)).

## Today

Today's board server gives every block one of the statuses of [blockr#488](https://github.com/orgs/BristolMyersSquibb/discussions/488), `unevaluated`, `stale`, `waiting`, `unset`, `failed` or `ready`, and a block nothing needs keeps what its last check found, which reads `stale` once anything the check read has changed ([R/block-server.R#L20-L71](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L20-L71)). A block is needed while an owner holds it eager or it feeds one that is: a front-end makes the board lazy by returning `eager()` with the blocks it shows from the callback it registers, any other owner holds blocks through the `eager` component of a board update or brings them up to date once through its `evaluate` component, and the `gate_visibility` blockr option, set to `FALSE`, keeps every board eager ([R/block-server.R#L79-L105](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L79-L105), [R/board-server.R#L21-L78](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-server.R#L21-L78)). The servers of blocks nothing needs are built in the background once the front-end has painted what it holds eager, and evaluate nothing ([R/block-server.R#L113-L123](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L113-L123), [#L402-L404](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L402-L404)).

## Proposal

### Versions

Every block has a version, a number the client keeps for the page and never saves, since a board that opens meets an R process that holds no result of it. A block's version goes up whenever its recipe changes ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)): its state, the links into it, other than in their names, and the version of any block upstream of it, so a change reaches everything downstream. It also goes up when something invalidates the block (below). Nothing else changes a version: not renaming a block or a link, changing a block's attributes or moving it between stacks, nor changing a field or a board option, which never reaches `expr` and redraws outputs without evaluating ([Client-owned board state](Rewrite-1.1#proposal)). Within the page a block id's version only goes up, through a removal that undo takes back and through another board opening, so that a late reply never passes for a newer version. A block is stale while its version is newer than the version of its latest reply. The version is the scheduler's, apart from the edit version the store keeps for each block, which counts only the block's own edits ([Board updates](Rewrite-1.1.2#deltas)).

### Demand

The scheduler keeps every block that something demands evaluated, together with everything upstream of it, and evaluates nothing else, but for one-off evaluations and, where an app turns it on, evaluation in the background (below). A demand has an owner, and every owner demands the same way, so core never learns why a block is demanded, as [blockr#489](https://github.com/orgs/BristolMyersSquibb/discussions/489) has it for the R board:

- A demand is a set of blocks, such as what the dock shows, or a function of the board, which the scheduler calls again after every change to the board, such as blockr.io's demand for every write block whose `auto_write` is on. The handle that `demand()` returns replaces or releases it, so an owner may hold several and none replaces another's, while the owner's name says whose a demand is, so that core can name it, as when a function of the board throws (notes). A function of the board is how a block keeps evaluating with nothing on screen, by its own state or by any setting the board holds, so a block class declares nothing about it ([Block classes in R](Rewrite-1.1.5#the-block-class)), and a front-end or an extension can let the user keep any block evaluated through a field it keeps and a function that reads it ([Board updates](Rewrite-1.1.2#fields)).
- Core demands every block, unless the front-end is lazy, as its package declares in R with the front-end ([Front-ends and extension points](Rewrite-1.1.8#registering-a-front-end)), and the front-end then demands the blocks it shows. The dock is lazy, and core's basic front-end, which shows every block, is not. The `gate_visibility` blockr option, `TRUE` by default as today, keeps core's demand on every block under a lazy front-end too when set to `FALSE`, for an app that wants every result current.
- A one-off evaluation brings some blocks and their upstream up to date without keeping them so: it evaluates those that read `stale` or `unevaluated`, and resolves with their statuses once none of them does, at whatever version each has by then, so that an edit made while it waits delays it, rather than leaving it waiting for a version whose reply the scheduler drops. It leaves out a block that leaves the board meanwhile, and rejects when another board opens, as a host's `submit()` does ([UI modules in JS](Rewrite-1.1.7#the-contract)). The code export and the assistant run one ([Code export as a client extension](Rewrite-1.5), [Assistant as a client extension](Rewrite-1.4)), and a request that reads blocks, a block class's or a package's, has them evaluated this way before it runs ([UI modules in JS](Rewrite-1.1.7#the-contract), [Wire protocol](Rewrite-1.1.9#requests)).
- A one-off evaluation can carry parameters, which R passes to the `block_eval()` method of each block it names, and then evaluates those blocks whether they are stale or not, as a write block's save button does ([UI modules in JS](Rewrite-1.1.7#the-contract), [Block classes in R](Rewrite-1.1.5#evaluation)). Since such a method may write, the evaluation runs once per call, as an action does: the scheduler sends it for the versions the blocks have when it is called, never cancels it, and resolves it with its own replies, which set a block's status only where their version is still the block's.

Every demand and one-off evaluation has a priority, a number that defaults to 0, and a block takes the highest priority of anything that needs it, itself or a block downstream of it, so that what a view shows and everything upstream of it go first. A lazy front-end demands what it shows above the default, as today's core re-prioritizes construction toward the view that navigation brings on screen ([blockr.core#275](https://github.com/BristolMyersSquibb/blockr.core/issues/275)), and a front-end that is not lazy may demand what is on screen in the same way, beside core's demand on every block. A priority only orders evaluations, so it says how soon an owner needs its blocks and never why. Both `demand()` and `evaluate()` take it as an option, after a demand's blocks and a one-off evaluation's parameters, and a request has the blocks it reads evaluated at the default, after what a lazy front-end shows.

An app can also have R evaluate in the background the stale and unevaluated blocks nothing demands, with the `background_evaluation_delay` blockr option: once R has had nothing demanded to evaluate for that many seconds, the scheduler evaluates them at priority -1, one at a time, until something demanded arrives, as the blockx prototype at cynkra evaluates the rest of the board after the view on screen ([blockr.core#395](https://github.com/BristolMyersSquibb/blockr.core/issues/395)). Its default, `Inf`, evaluates nothing in the background, as today's background pass builds block servers but evaluates none, and the option takes the place of today's `background_construction_delay`, which goes with the block servers. Sending one at a time keeps what a demanded evaluation can wait behind to the one background evaluation R has started, for as long as it runs, or for 5 s where R can stop it (below).

```ts
const shown = scheduler.demand("blockr.dock", ["a", "b"], { priority: 1 });   // a set: what the dock shows, ahead of the default
shown.set(["a", "c"]);                                                         // replaced as the view changes
shown.release();

scheduler.demand("blockr.io", board =>                                         // a function of the board, called after every change
  Object.keys(board.blocks).filter(id =>
    board.blocks[id].registry_id === "blockr.io-write_block" && board.blocks[id].state.auto_write === true));

const statuses = await scheduler.evaluate(["b", "c"]);                         // a one-off evaluation, resolving with their statuses
await scheduler.evaluate(["w"], { save: true });                               // with parameters, which run w even where it is not stale
```

### Invalidation

```ts
scheduler.invalidate("a");   // bumps a and everything downstream
```

Any component may invalidate a block, such as the user from a block's menu, which a front-end draws and which invalidates through `CoreApi`, or an extension, so a block that reads something outside the board, such as a file that changed on disk, runs again when asked to ([UI modules in JS](Rewrite-1.1.7#the-contract)). Invalidating changes no state, so it is no delta, which nothing undoes or saves, and a block nothing demands only turns `stale`.

### Statuses

```ts
type Status = "unevaluated" | "stale" | "waiting" | "invalid" | "ready" | "failed";

interface BlockStatus {
  status: Status;
  version: number;                                 // the block's current version
  evaluated: number | null;                        // the version its latest reply was for
  running: boolean;                                // whether an evaluation of it is sent and not yet answered
  conditions: Condition[];                         // from the latest reply, which replaces the ones before
  omitted: { warning: number; message: number };   // the conditions that reply counted rather than kept
  stdout: string;                                  // its standard output and error, bounded
  stderr: string;
  expr: string | null;                             // the expression R built for that version
  summary: string | null;                          // the result's summary from that reply, "<data.frame> [150 × 7]"
}

scheduler.status("b");                                         // the block's status now, read by whatever draws it
scheduler.subscribe(changed => { /* redraw these blocks */ });  // after statuses change, naming the blocks whose status changed
```

The names are today's ([R/block-server.R#L20-L71](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L20-L71)), with `invalid` in place of `unset`, since a block class says only whether a state can run, by signalling `invalid()` in its `expr` or its `block_eval()` method or using an arg the state leaves unset ([Block classes in R](Rewrite-1.1.5#expressions)), and the conditions are those a reply carries ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)). A block's status is the first of these that holds:

1. It is `waiting` while an input without a default is unlinked, a variadic block has no link, or a block upstream reads `failed`, `invalid` or `waiting`, which the client sees from the block registry and the board without asking R ([Block classes in R](Rewrite-1.1.5#the-block-class)).
2. It is `unevaluated` before its first reply.
3. It is `stale` while its version is newer than its latest reply's, whether anything demands it or not.
4. It is what that reply says: `ready` for `ok`, `failed` for `error` and `invalid` for `invalid`.

A reply of `cancelled` or `missing` counts as none, since the scheduler sends again what it still needs. A block nothing demands reads the same way, so one that failed and has not changed since still reads `failed`, and a `stale` block keeps its latest reply's conditions, so one that failed before it went stale shows why. The conditions of an `invalid` reply hold the message of its `invalid()` or name the unset arg, and while a block is `waiting`, the scheduler adds a condition that names the unlinked input or the upstream block that keeps it waiting, as today's board server records a note for `waiting` and `unset` ([R/block-server.R#L66-L71](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L66-L71)).

### Scheduling

After every change to the board, to a demand or to a version, and after every reply, the scheduler works out what is demanded and what feeds it, and queues the blocks among them that read `stale` or `unevaluated`, highest priority first and in topological order within a priority. It holds what is still to send itself and sends R only a few evaluations ahead of the one R runs, which R runs one at a time in the order they arrive, making a request wait for an input still computing ([Wire protocol](Rewrite-1.1.9#one-request-at-a-time)), so that a new priority or version takes effect at the next send, nothing superseded waits in R beyond those few, and the protocol needs no message to reorder what R holds, as the `prio` message of the blockx prototype at cynkra does ([blockr.core#393](https://github.com/BristolMyersSquibb/blockr.core/issues/393)). When a block's version changes while R holds its evaluation, the scheduler cancels the evaluation where the capability allows, unless it carries parameters (above), and never lets its reply set the block's status, as it ignores the reply for a block that reads `waiting` by the time it arrives, such as one whose upstream failed meanwhile. Where R can stop an evaluation it has started ([Wire protocol](Rewrite-1.1.9#cancelling)), the scheduler also cancels one whose priority is below 0 once an evaluation of a higher priority has waited 5 s behind it, and queues it again, so that background evaluation, for now the only one below 0, never holds up for long what someone asked for. It cancels nothing at 0 or above for priority, since a demanded evaluation that gave way to every edit on screen, such as a write block's in auto mode, might never finish.

At startup the scheduler sends nothing until the front-end's `render()` has returned, so that a lazy front-end, which demands what it first shows there, from the board, has those blocks and everything upstream of them evaluated first ([Front-ends and extension points](Rewrite-1.1.8#starting-the-page)), as today's core seeds the front-end's opening demand before the first flush ([R/block-server.R#L79-L95](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L79-L95)). Outputs are fetched by whatever draws them, once a block is `ready`, and core keeps drawing a block's last output whatever its status, so that the front-end decides from the status what an output that is not current looks like ([Front-ends and extension points](Rewrite-1.1.8#what-core-gives-a-front-end)). After the `hello` of a new session, which holds no results, the scheduler queues every demanded block again, with everything upstream, while front-ends keep drawing the last outputs core holds ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)).

There is no early cutoff: a recomputed R result is a new object, so an identity check would not fire, and hashing results costs time in proportion to their size. Cutoff can come later, opt-in per block class.

## Open questions

- How many evaluations the scheduler keeps R ahead of the one it runs, which only measuring settles, in the scheduler's issue: the fewest with which R does not wait between evaluations on the CEDX board over a link with a 40 ms round trip, the link the blockx prototype was measured on ([blockr.core#395](https://github.com/BristolMyersSquibb/blockr.core/issues/395)).

<details><summary>Notes for implementers</summary>

A set may name blocks that are no longer on the board, which the scheduler passes over, so a block that undo brings back is demanded again by any set that still names it. A function of the board that throws demands nothing until it next returns, and the scheduler names its owner in an error, as core names a startup module that throws ([UI modules in JS](Rewrite-1.1.7#startup-modules)).

The precedents, Excel's recalculation of every dependent of changed data, the version counter Observable's runtime keeps per variable and Incremental's bringing up to date only what leads to an observed node, are on [blockr.core#395](https://github.com/BristolMyersSquibb/blockr.core/issues/395), whose comment gives what the blockx prototype at cynkra measured when it sent rows only for the blocks on screen.

</details>
