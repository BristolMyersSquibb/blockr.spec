# Evaluation in the client: versions, claims and statuses
Status: draft. Design for [Client-owned board state](Doc-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Doc-1.1)): what the client tracks about evaluation, and the API front-ends and extensions use to ask for it. It builds on the [document model](Doc-1.1.1) and the [wire protocol proposal](Doc-1.1.9), and shapes the scheduler ([blockr.core#395](https://github.com/BristolMyersSquibb/blockr.core/issues/395)). It replaces what [blockr#489](https://github.com/orgs/BristolMyersSquibb/discussions/489) and [blockr#488](https://github.com/orgs/BristolMyersSquibb/discussions/488) rework within the R board, evaluation demand and statuses, and keeps their terms.

## What must hold

1. A board evaluates every block, as boards do today, unless it opts into evaluating only what is demanded.
2. A board edit costs no R time beyond evaluating what is demanded and fetching outputs for what is on screen.
3. Any component can demand a block or invalidate one without knowing who else does, and without saying why.
4. A block's status, conditions and expression read the same whether or not it is demanded, as [blockr#488](https://github.com/orgs/BristolMyersSquibb/discussions/488) asks of the R board.

## Proposal

### Versions

Every block has a version, a number the client keeps for the session and never saves, since a reopened board meets an R process that holds nothing anyway. A block's version goes up when its state changes, when a link into it is added, removed or changed, when anything upstream of it goes up, and when something invalidates it. Renaming a block or moving it between stacks changes no version. A block is stale while its version is newer than the version of its latest reply.

### Demand

The scheduler evaluates what is demanded, and everything upstream of it. A board's `evaluation` option decides what that is: `"eager"`, the default, demands every block, and `"lazy"` demands only what the following ask for. The option configures the scheduler and never reaches a type's `interpolate`.

- A block of a type declared eager, such as one that writes a file, is always demanded, so it writes in a lazy board too. The type declares it through `new_block(..., eager = TRUE)`, or with a function of the block's state, so that a write block is demanded only while its auto mode is on ([Block types in R](Doc-1.1.5)), and the registry export carries it ([blockr.core#396](https://github.com/BristolMyersSquibb/blockr.core/issues/396)).
- A standing demand holds a set of blocks until its owner replaces or releases it, and all owners write the same owner-keyed set, as [blockr#489](https://github.com/orgs/BristolMyersSquibb/discussions/489) has it for the R board. The dock demands what it shows, and core does not know why.
- A one-off evaluation evaluates what is stale among some blocks and their upstream once, and resolves with their statuses, such as a code export that needs every block's current expression, or the assistant checking the descendants of a block it changed for new failures. A package request that names the blocks it reads evaluates them this way before it runs ([Wire protocol](Doc-1.1.9)).

```ts
const demand = scheduler.demand("blockr.dock", ["a", "b"]);   // what the dock shows
demand.set(["a", "c"]);                                       // replaced as the view changes
demand.release();

const statuses = await scheduler.evaluate(["b", "c"]);        // once, resolving with their statuses
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
}

scheduler.status("b");          // a signal, read by whatever draws the block
```

The names are those of [blockr#488](https://github.com/orgs/BristolMyersSquibb/discussions/488), with `invalid` in place of its `unset`, since a block type's `validate` says only whether a state can run ([Block types in R](Doc-1.1.5)). A reply of `ok` makes a block `ready`, `error` makes it `failed`, and `invalid` makes it `invalid`; it is `waiting` while an upstream block is `failed`, `invalid` or `waiting`, `stale` while a newer version exists than its latest reply was for, and `unevaluated` before its first reply. A cancelled evaluation leaves the block `stale`. The status of a block nothing demands keeps its latest reply, so a parked block that failed still reads `failed`.

### Scheduling

After every delta, the scheduler works out what is demanded and what feeds it, and sends the stale blocks among them to R in topological order, in one message, since R makes a request wait for an input still computing. When a block's version changes while R evaluates it, the scheduler cancels that evaluation where the capability allows and drops its reply in any case. Outputs are fetched by whatever draws them, once a block is `ready`. After R restarts, every demanded block is evaluated again, and R asks for the inputs it lacks.

There is no early cutoff: a recomputed R result is a new object, so an identity check would not fire, and hashing results costs time in proportion to their size. Cutoff can come later, opt-in per block type.

## Open questions

- Whether demands carry a priority, so the blocks the dock shows evaluate before what a code export evaluates in the background, and before the rest of an eager board.
- Whether a lazy board evaluates the blocks nothing demands while R is idle, as today's background construction builds blocks ahead of need.
