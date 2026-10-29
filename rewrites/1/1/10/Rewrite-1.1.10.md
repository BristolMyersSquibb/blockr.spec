# Evaluation in the client: versions, demand and statuses
Status: draft. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): what the client tracks about evaluation, and the API front-ends and extensions use to ask for it. It builds on the [board objects proposal](Rewrite-1.1.1) and the [wire protocol proposal](Rewrite-1.1.9), and shapes the scheduler ([blockr.core#395](https://github.com/BristolMyersSquibb/blockr.core/issues/395)). It replaces what [blockr#489](https://github.com/orgs/BristolMyersSquibb/discussions/489) and [blockr#488](https://github.com/orgs/BristolMyersSquibb/discussions/488) rework within the R board, evaluation demand and statuses, and keeps their terms.

## What must hold

1. A board evaluates every block, as boards do today, unless its front-end is lazy and demands only the blocks it shows.
2. A board edit costs no R time beyond evaluating what is demanded and fetching outputs for what is on screen.
3. Any component can demand a block or invalidate one without knowing who else does, and without saying why.
4. A block's status, conditions and expression read the same whether or not it is demanded, as [blockr#488](https://github.com/orgs/BristolMyersSquibb/discussions/488) asks of the R board.
5. A block that must run with nothing on screen, such as a write block in auto mode, runs under a lazy front-end too, and a component that needs current results, such as the code export, gets them without putting a block on screen.

## Proposal

### Versions

Every block has a version, a number the client keeps for the session and never saves, since a reopened board meets an R process that holds nothing anyway. A block's version goes up when its state changes, when a link into it is added, removed or changed, when anything upstream of it goes up, and when something invalidates it. Renaming a block or moving it between stacks changes no version. A block is stale while its version is newer than the version of its latest reply.

### Demand

The scheduler evaluates every block something demands, and everything upstream of it, and nothing else. A demand has an owner, which alone replaces or releases it, and every owner demands the same way, so core never learns why a block is demanded, as [blockr#489](https://github.com/orgs/BristolMyersSquibb/discussions/489) has it for the R board:

- A demand is a set of blocks, which its owner replaces or releases, such as what the dock shows, or a rule, a function of the board that the scheduler reads again after every change, such as blockr.io's demand for every write block whose `auto_write` is on. A rule is how a block keeps evaluating with nothing on screen, by its own state or by any setting, so a block class declares nothing about it ([Block classes in R](Rewrite-1.1.5#the-block-class)), and a front-end or an extension can offer a pin on any block as a field it keeps and a rule that reads it ([Board updates](Rewrite-1.1.2#fields)).
- Core demands every block, unless the front-end is lazy, demanding only the blocks it shows, as its package declares in R with the front-end ([Front-ends and extension points](Rewrite-1.1.8#registering-a-front-end)). The dock is lazy, and core's basic front-end, which shows every block, is not. A blockr option keeps core's demand on every block under a lazy front-end too, for an app that wants every result current.
- A one-off evaluation evaluates what is stale among some blocks and their upstream once, and resolves with their statuses, such as a code export, which needs every block's current expression and names the blocks that end invalid or failed instead of giving code, or the assistant checking the descendants of a block it changed, hidden ones included, for new failures. A package request that names the blocks it reads evaluates them this way before it runs ([Wire protocol](Rewrite-1.1.9)).

```ts
const shown = scheduler.demand("blockr.dock", ["a", "b"]);    // a set: what the dock shows
shown.set(["a", "c"]);                                        // replaced as the view changes
shown.release();

scheduler.demand("blockr.io", board =>                        // a rule, read again after every change
  Object.keys(board.blocks).filter(id =>
    board.blocks[id].registry_id === "blockr.io-write_block" && board.blocks[id].state.auto_write === true));

const statuses = await scheduler.evaluate(["b", "c"]);        // a one-off evaluation, resolving with their statuses
```

### Invalidation

```ts
scheduler.invalidate("a");   // bumps a and everything downstream
```

Any component may invalidate a block, such as a read block's reload, the user from a block's menu, or an extension, so a block that reads something outside the board re-runs when asked to.

### Statuses

```ts
type Status = "unevaluated" | "stale" | "waiting" | "invalid" | "ready" | "failed";

interface BlockStatus {
  status: Status;
  version: number;             // the block's current version
  evaluated: number | null;    // the version its latest reply was for
  running: boolean;
  conditions: Condition[];     // from the latest reply, which replaces the ones before
  expr: string | null;         // the expression R built for that version
  summary: string | null;      // the result's summary from that reply, "<data.frame> [150 × 7]"
}

scheduler.status("b");                                         // the block's status now, read by whatever draws it
scheduler.subscribe(changed => { /* redraw these blocks */ });  // after statuses change, naming the blocks whose status changed
```

The names are those of [blockr#488](https://github.com/orgs/BristolMyersSquibb/discussions/488), with `invalid` in place of its `unset`, since a block class's `expr` says only whether a state can run, by signalling `invalid()` or using an arg the state leaves unset ([Block classes in R](Rewrite-1.1.5)). A reply of `ok` makes a block `ready`, `error` makes it `failed`, and `invalid` makes it `invalid`; it is `waiting` while an input is unlinked or an upstream block is `failed`, `invalid` or `waiting`, `stale` while a newer version exists than its latest reply was for, and `unevaluated` before its first reply. A cancelled evaluation leaves the block `stale`. The status of a block nothing demands keeps its latest reply, so a parked block that failed still reads `failed`.

### Scheduling

After every delta, the scheduler works out what is demanded and what feeds it, and sends the stale blocks among them to R in topological order, in one message, since R makes a request wait for an input still computing. When a block's version changes while R evaluates it, the scheduler cancels that evaluation where the capability allows and drops its reply in any case. Outputs are fetched by whatever draws them, once a block is `ready`. After the `hello` of a new session, which holds no results, every demanded block is evaluated again, with everything upstream, in one message, while front-ends keep drawing the last outputs core holds ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)).

There is no early cutoff: a recomputed R result is a new object, so an identity check would not fire, and hashing results costs time in proportion to their size. Cutoff can come later, opt-in per block class.

## Open questions

- Whether demands carry a priority, so the blocks the dock shows evaluate before what a code export evaluates in the background, and before the rest of a board whose front-end is not lazy.
- Whether the scheduler evaluates the blocks nothing demands while R is idle, as today's background construction builds blocks ahead of need.
