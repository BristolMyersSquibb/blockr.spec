# The assistant's tools
Status: review. Design for [Assistant as a plugin](Rewrite-1.4).

One of the design pages of the assistant ([Assistant as a plugin](Rewrite-1.4)): the tools that the model calls, what each reads, changes and returns, and the requests that some of them send to R.
It shapes the Work items that build the tools and the loop and that compare the edit tool with other versions, and the one in blockr.core that lets the command registry plan a list of commands.
Where the calls to a model go is [Model access](Rewrite-1.4.1)'s, the threads that hold the tools' calls and results are [The assistant's state](Rewrite-1.4.3)'s, and what the model is told before each call is [The system prompt](Rewrite-1.4.5)'s.

## What must hold

1. The model edits the board only through the commands of core's command registry ([Assistant as a plugin](Rewrite-1.4#what-must-hold)).
   Each call of a tool that edits applies its commands as one undo step of the assistant, all or none, and the model takes such a step back through `undo_edit` alone.
2. The edit tool returns only once the blocks it changed, and those downstream of them, are current.
   Its review covers those blocks and the blocks that feed the changed ones, and gives what today's review of a commit gives: each block's status and conditions, what `describe_result()` writes about its result, and the state of each block that the edit added.
3. The tools read the board, the block registry, the registered commands and each block's status in the browser, and send R a request only for what needs R: a block's result, the model's own R code, or the skills on the server.
4. What each tool returns is bounded by today's blockr options, so that no call fills the model's context.
5. Every read and every edit that today's 40 tools make carries over, through the tools below or the commands that the edit tool runs, but for what Today drops with its reason.
6. On a locked board, the model reads as on any board, but runs no R code of its own, and learns from the tool's result why the lock refuses an edit or its R code.

## Today

Today's assistant registers 39 tools as its chat is built, and the typed tools on top, each an `ellmer::tool()` that reads the board server's reactives or stages a change ([R/ext-server.R#L485-L509](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L485-L509)).
Each goes as follows:

| Today, at `fcbdb27` | Where it goes |
|---|---|
| `list_blocks`, `describe_block`, `get_block_state` and `get_block_conditions` ([R/tools-read.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-read.R)) | Kept, reading the board through `store.board()` and each block's status and conditions through `scheduler.status()` |
| `list_links`, `list_stacks` and `describe_stack` | Kept, reading `store.board()` |
| `list_block_types` and `describe_block_type`, which build a block of each class to read its inputs | Kept, reading the block registry's entries, which give each class's inputs, its arg specs and the JSON Schema of its state without building a block |
| `get_block_result`, which summarizes a block's result through `describe_result()` | Kept, sending a request that R answers through `describe_result()` |
| `inspect_results`, which evaluates the model's R code with every result bound to its block's id | Kept, sending a request that reads only the blocks that the model names, since core has every block that a request reads evaluated first, while R refuses the request on a locked board |
| `list_views` and `validate_layout` ([R/tools-view.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-view.R)) | `get_plugin_state` on the dock's class id in place of `list_views`, while `validate_layout` goes, since the dock's commands check what they are given |
| The view tools that stage a change: `add_view`, `remove_view`, `rename_view`, `set_active_view`, `add_panel_to_view`, `remove_panel_from_view`, `move_panel`, `resize_panel` and `focus_panel` | The dock's commands, which the edit tool runs, in the same order: `blockr.dock-add_view`, `blockr.dock-remove_view`, `blockr.dock-rename_view`, `blockr.dock-activate_view`, `blockr.dock-add_panel`, `blockr.dock-remove_panel`, `blockr.dock-move_panel`, `blockr.dock-resize_panel` and `blockr.dock-activate_panel`, the last after `blockr.dock-activate_view` where the panel's view is not the active one, as `focus_panel` switches to it ([The dock's state](Rewrite-1.2.1#commands)) |
| The mutation tools: `add_block`, `remove_block`, `modify_block`, `add_link`, `remove_link`, `modify_link`, `add_stack`, `remove_stack` and `modify_stack` ([R/tools-mutation.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-mutation.R)) | Core's commands, which the edit tool runs ([Board updates](Rewrite-1.1.2#commands)) |
| `list_extensions` and `describe_extension` ([R/tools-extension.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-extension.R)) | `list_plugins` and `get_plugin_state`, which read the app's plugins and each one's state, with the schema that describes it and the skills that name its class |
| `modify_extension` | Core's `blockr.core-set_plugin_state` and each plugin class's own commands, which the edit tool runs ([Plugins](Rewrite-1.1.12#a-plugins-state)) |
| `commit` and `discard` ([R/tools-commit.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-commit.R)) | The edit tool, which applies what it is given at once, so that nothing is staged to commit or discard |
| `list_board_options` and `set_board_option` ([R/tools-options.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-options.R)) | `list_board_options`, reading `core.options`, and core's `blockr.core-set_option`, which the edit tool runs |
| `read_skill` ([R/skills-invoke.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-invoke.R)) | Kept, sending a request that R answers |
| The typed tools `add_<type>` and `modify_<type>`, twenty of each at a time, whose args take each class's arg types ([R/tools-typed.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-typed.R)) | Dropped from the first version, since `describe_block_type` gives the JSON Schema of a class's state, and core's commands refuse a state that the schema refuses, naming each failure (notes). The benchmark compares that version with tools like these for each block class (The edit tool) |

## Proposal

### The tools

Each tool runs in the browser, and those that need R send a request of the assistant's plugin ([Plugins](Rewrite-1.1.12#a-plugins-requests)):

| Tool | What it returns or does | What it reads |
|---|---|---|
| `list_blocks` | Each block's id, name, registry id and status | `store.board()`, `scheduler.status()` |
| `describe_block` | One block's class, state, inputs with the links into them, status, conditions and summary, and the skills scoped to its class | `store.board()`, `blockRegistry()`, `scheduler.status()`, the reply to `list_skills` |
| `get_block_state` | One block's state in full | `store.board()` |
| `get_block_conditions` | One block's conditions, by severity and phase | `scheduler.status()` |
| `list_links`, `list_stacks` and `describe_stack` | The links, the stacks, and one stack with its blocks | `store.board()` |
| `list_block_types` and `describe_block_type` | Each block class's id, name and description, and one class's inputs, arg specs, the JSON Schema of its state and the skills scoped to it | `blockRegistry()`, the reply to `list_skills` |
| `list_commands` and `describe_command` | Each registered command's id and description, and one command's args, as their JSON Schema has them | `commands.registered()` |
| `list_plugins` and `get_plugin_state` | Each of the app's plugins by its class's id and name, and one plugin's state, with the JSON Schema of its class's state, whose `description` keywords describe it, and the skills scoped to its class | `plugins.appPlugins()`, `plugins.pluginClass()`, `store.board()`, the reply to `list_skills` |
| `list_board_options` | Each board option in use, with its id, label, category and value, and the JSON Schema of its value | `options.inUse()`, `options.registered()`, `options.value()` |
| `get_block_result` | The summary of one block's result, as `describe_result()` writes it | The request `describe_result` |
| `inspect_results` | What the model's R code prints, and up to four of the plots it draws | The request `inspect_results` |
| `read_skill` | A skill's text, or a file that the skill holds | The request `read_skill` |
| `edit` | Runs a list of commands as one step of the assistant, and returns a review of the blocks it changed, those that feed them and those downstream (below) | `commands.run()`, `store.subscribe()`, `scheduler.evaluate()`, `scheduler.status()`, the request `describe_result` |
| `undo_edit` | Takes back the assistant's last edit, as the chat's Undo does ([The assistant's chat](Rewrite-1.4.4#undoing-the-assistants-edits)), and returns as `edit` does (below) | `store.canUndo("assistant")`, `store.undo("assistant")`, and what `edit` reads |

The read tools keep today's names.
Of the two pairs that are new, `list_commands` and `describe_command` follow today's `list_block_types` and `describe_block_type`, and `list_plugins` and `get_plugin_state` follow `list_blocks` and `get_block_state`.
They carry over one for one, as parity has it, and whether fewer tools serve the model better is for the benchmark to show ([The assistant's benchmark](Rewrite-1.8.1#the-decisions-it-compares)).
A read tool reads the board as it is now, and says of a block that reads `stale` or `unevaluated` that it does, without evaluating it.
Only a request evaluates the blocks it reads, as every request does ([Evaluation in the client](Rewrite-1.1.10#demand)).

### The edit tool

The edit tool takes a list of commands, each by its id with its args, here with an illustrative state:

```json
{ "commands": [
  { "command": "blockr.core-add_block", "args": { "registry_id": "blockr.dplyr-filter_block", "id": "adults", "state": { "conditions": ["AGE >= 18"] } } },
  { "command": "blockr.core-add_link", "args": { "from": "adsl", "to": "adults" } },
  { "command": "blockr.dock-show_panel", "args": { "panel": { "block": "adults" } } }
] }
```

It applies them in these steps:

1. The edit tool runs the commands with `core.commands.run(list, "assistant")`, passing each command's `command` as its `id`.
   The command registry plans each command on the board that the commands before it leave, and the store applies them all as one step of the origin `assistant`, or applies none ([Board updates](Rewrite-1.1.2#commands)).
2. Where a command refuses, the tool returns the command's id and each failure that the command registry names, such as a state that the schema of the block's class refuses, and the board stays as it was.
   Where the command refuses its args on the board as it is, as `blockr.core-add_link` refuses a block that the board lacks, the tool adds a hint that says what to check, so that the model can correct its args and edit again (notes).
3. From the changes that the store announces for the step, one for each of its deltas, the tool takes the blocks that the step added or whose state or links it changed, every block downstream of them, and the blocks that feed the changed blocks directly ([Board updates](Rewrite-1.1.2#following-the-board)).
4. It brings those blocks up to date with one one-time evaluation, `core.scheduler.evaluate(blocks, undefined, { signal })`, given the signal of the turn, so that stopping the turn stops the wait ([Evaluation in the client](Rewrite-1.1.10#demand)).
   It passes no parameters, since a one-time evaluation with parameters has R run every block again, whether the block is current or not.
5. It picks the blocks that its review covers: at most `assistant_review_max_blocks` of them, 50 by default, the blocks it changed first, then those that feed them, then those downstream.
6. It sends one request, `describe_result`, which reads each of those blocks that reads `ready`, with the signal of the turn, and R answers with the text that `describe_result()` writes about each block's result (The requests in R).
7. It returns, for each of those blocks, its status and conditions, as `scheduler.status()` gives them, the text that `describe_result()` wrote and, for a block that the step added, its state, within the caps of today's review (notes).
   It says how many blocks it left out, as today's review does.

A block that the user edits meanwhile reports its status at its newer revision.
A block that leaves the board meanwhile is named as removed, rather than left out as the one-time evaluation leaves it, so that the model does not report it as built ([The assistant's chat](Rewrite-1.4.4#while-a-turn-runs)).
Where core rejects the request of step 6, as when the user changes one of its blocks meanwhile, the review gives the one-line summary of `scheduler.status()`, such as `<data.frame> [306 × 49]`, in place of that text.
Some lists leave no block to evaluate, such as one that changes only the dock's views.
The tool then evaluates nothing and returns at once, since a one-time evaluation of no block rejects.
A stop while the tool waits leaves its commands applied.
So the tool still returns that they applied, with as much of the review as it has, and that the user stopped the turn, so that the model does not run them again ([The assistant's chat](Rewrite-1.4.4#stopping-a-turn)).

```json
{ "applied": true, "blocks": {
  "adults": { "status": "ready", "conditions": [], "result": "<what describe_result() writes, up to 2,000 characters>", "state": { "conditions": ["AGE >= 18"] } },
  "adsl": { "status": "ready", "conditions": [], "result": "<what describe_result() writes>" }
} }
{ "applied": false, "command": "blockr.core-add_link", "failures": ["It is not enabled on the board as it is, with the args {\"from\":\"adsl\",\"to\":\"adlts\"}."],
  "hint": "Check that each block, link, stack, board option and plugin that the args name is on the board, with list_blocks, list_links, list_stacks, list_board_options or list_plugins, and that a block that a new link goes to has a free input, with describe_block." }
```

The model learns which commands it can run, and what their args take, from `list_commands` and `describe_command`.
So a package that registers a command opens it to the assistant with no code of the assistant's, as today's `new_ext_meta()` opens an extension ([Board updates](Rewrite-1.1.2#what-must-hold)).
The edit tool refuses a list that holds a command of the assistant's own, or core's `blockr.core-set_plugin_state` for the assistant's plugin, and `list_commands` leaves them out, since only the assistant's chat and loop change its threads and each thread's pick of the model, as today's `set_board_option` refuses `llm_model`, which "drives the assistant's own chat client" ([R/tools-options.R#L93-L100](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-options.R#L93-L100)).

The tool `undo_edit` takes back the assistant's last step with `core.store.undo("assistant")`, which applies the undo as a new edit, and then returns as the edit tool does from step 3, so that the model learns what the undo changed.
Where `core.store.canUndo("assistant")` is false, it changes nothing and returns that the assistant has no edit left to take back.

The edit tool is the first version of how the model edits the board.
The benchmark compares it with two others ([The assistant's benchmark](Rewrite-1.8.1#the-decisions-it-compares)):

- A tool per command, whose args are the command's `args`, so that the model reads them in the tool's definition rather than through `describe_command`.
- Beside the edit tool, two tools for each block class: one adds a block of the class, and one sets a block's state.
  Their args follow the JSON Schema of the class's state, as the args of today's `add_<type>` and `modify_<type>` follow the class's arg types.

Each tool of these versions runs the steps above on a list of one command, such as `blockr.core-add_block` or `blockr.core-set_block`.
So an edit through them takes one call for each command, and each call is an undo step of its own.
The assistant keeps the version that passes the comparison ([The assistant's benchmark](Rewrite-1.8.1#what-a-comparison-reports)).

### The requests in R

The assistant's class gives R four requests through its method of `plugin_requests()`: the three that the tools send, and `list_skills`, which the plugin sends once a board opens.
R calls each with the blocks that it reads in `reads`, each by its id with its result ([Plugins](Rewrite-1.1.12#a-plugins-requests)):

```r
plugin_requests.assistant_plugin <- function(x, ...) {                  # in blockr.assistant
  list(
    describe_result = function(reads) {                                  # the block that get_block_result names, or those of an edit's review
      lapply(reads, function(read) summarise_result(read$result))        # by block id: describe_result(), its errors caught, cut at assistant_summary_max_chars
    },
    inspect_results = function(code, reads, width = NULL, height = NULL) {
      if (isTRUE(blockr_option("locked", FALSE))) {
        stop("The board is locked, so the assistant runs no R code of its own.")
      }
      env <- list2env(lapply(reads, `[[`, "result"), parent = baseenv())  # each block's result under its id
      run_inspection(parse(text = code), env, width, height)             # what it prints, and its plots as base64 PNGs
    },
    list_skills = function() skill_catalogue(),                          # the skills of the app's packages, then those of the directory that assistant_skills names
    read_skill = function(name, file = NULL) read_skill_file(name, file)  # a skill's text, or a file that it holds
  )
}
```

```ts
const answer = await core.request("blockr.assistant-assistant_plugin", "inspect_results",
  { code: "table(adsl$ARM)" }, { reads: ["adsl"], signal });              // reads: the blocks that the model names
```

Core evaluates the blocks that a request reads first, even off screen, and sends the request only where each reads `ready`, rejecting it otherwise with their statuses ([Evaluation in the client](Rewrite-1.1.10#demand)).
The tool then hands the model those statuses, as it hands it a request that R loses to a new session (notes).
So `describe_result()` stays a generic of blockr.assistant's in R, which writes what `get_block_result` and the edit's review give, and a package that teaches the model about a class of results gives a method of it, as the clinical data explorer does for its summary tables for clinical study reports.

The reply to `list_skills` gives each skill's name and description, and the classes that its frontmatter names.
A skill names block classes by registry id in `blocks:`, such as `blockr.dplyr-filter_block`, and plugin classes by their ids in `plugins:`, such as `blockr.dock-dock_plugin`, in place of today's `extensions:`.
The tools `describe_block` and `describe_block_type` list the skills that name the block's class, and `get_plugin_state` those that name the plugin's class, as today's `describe_block`, `describe_block_type` and `describe_extension` list theirs ([R/skills-render.R#L14-L32](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-render.R#L14-L32)).
The system prompt lists only the skills that name no class ([The system prompt](Rewrite-1.4.5#the-sections)).
What a skill written for today's stack changes at the switch is in [The conversion and the migration notes](Rewrite-1.9#the-migration-notes).

### On a locked board

The read tools and `read_skill` work on a locked board as on any other.
The store refuses an edit that a lock fixes, and the edit tool returns why, as it returns any refusal ([Locked boards and the properties of blocks](Rewrite-1.1.11#plugins-on-a-locked-board)).
R refuses `inspect_results`, since it evaluates what the client sends.

### How failures reach the model

A failure reaches the model as the result of the tool that met it, marked as an error, as today's tools return one ([R/tools-util.R#L1-L10](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-util.R#L1-L10)).
Its text names what failed, why, and where the model can read more, as today's tools answer a block id that the board lacks with the hint "Call list_blocks first" ([R/tools-read.R#L86-L87](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-read.R#L86-L87)):

| What fails | What the model gets |
|---|---|
| A tool's args that its schema refuses | The schema's failures, from the library's check, so that the model calls the tool again with args that fit |
| A block, a command, a plugin or a skill that a tool names and the board or the app lacks | That it is not there, with the tool that lists those that are, such as `list_blocks` |
| A command of an edit that refuses | The command's id and each failure that the command registry names, with a hint where the command refuses its args on the board as it is, while the board stays as it was (The edit tool) |
| A block that an edit changed, or one downstream of it, that reads `failed`, `invalid` or `waiting` once evaluated | Its status and conditions in the edit's review: the error of a `failed` block, the unset arg or the message of `blockr_invalid()` of an `invalid` one, and what a `waiting` one waits for ([Evaluation in the client](Rewrite-1.1.10#statuses)) |
| A request whose blocks do not read `ready` | The statuses of those blocks, with which core rejects it (The requests in R) |
| A request that R loses to a new session | That it was lost, since core sends it no more (notes) |
| An error in the model's own R code | The error's message, as R gives it |
| What a lock refuses | Why the lock refuses it, as the store or R says (On a locked board) |
| A value past its cap | That it is left out, as today's `describe_block` marks an arg too long to show ([R/describe-block.R#L126-L141](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/describe-block.R#L126-L141)), with the tool that reads it in full, such as `get_block_state` |
| A tool call that the user stops | A result saying that the user stopped the turn, which the plugin writes for each call left without one, since a provider takes a tool call in a thread only with its result ([The assistant's chat](Rewrite-1.4.4#stopping-a-turn)). An edit stopped while it waits says too that its commands applied (The edit tool) |

How each of these reads is a decision that [The assistant's benchmark](Rewrite-1.8.1#the-decisions-it-compares) compares, with questions whose turns meet it.
A failure that the user should know of reaches them as a notification as well, as a call to the model that fails does ([The assistant's chat](Rewrite-1.4.4#what-fails)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

The 40 tool definitions at `fcbdb27`, as at `fd58655`, by file: `tools-read.R` 11, `tools-view.R` 11, `tools-mutation.R` 9, `tools-extension.R` 3, `tools-commit.R` 2, `tools-options.R` 2, `skills-invoke.R` 1, `tools-typed.R` 1, the factory of the typed tools.

The schemas that the tools give the model come from the `args` of the registered commands, the schemas of plugin classes' state and the schemas that block classes' UIs ship, which the arg specs describe ([Board updates](Rewrite-1.1.2#commands)), and the arg specs are a JSON Schema subset that blockr.ai already binds through `ellmer::type_from_schema()`.
The loop's library, pi, takes such a schema as it is, since a tool's `parameters` is a plain JSON Schema object, as a run in a browser confirmed ([Assistant as a plugin](Rewrite-1.4)).
On `js-state`, core's `blockr.core-add_block` and `blockr.core-set_block` check the state they set against the schema of the block's class, which the block's entry in the block registry carries, and refuse with each failure ([srcts/commands/core.ts#L101-L118](https://github.com/BristolMyersSquibb/blockr.core/blob/69770d0aa9ba04954775e7827944b92d66cc2630/srcts/commands/core.ts#L101-L118)), which is what the typed tools give the model today through ellmer's types.

The command registry refuses a command whose `enabled()` returns false with "It is not enabled on the board as it is, with the args …" ([srcts/commands/commands.ts#L170-L177](https://github.com/BristolMyersSquibb/blockr.core/blob/319f81c355383cdea9443be48d7e1d316c485a1c/srcts/commands/commands.ts#L170-L177)), since `enabled()` returns only true or false.
Nearly every `enabled()` of core's commands checks that an id in the args names a block, link, stack, board option or plugin on the board, while `blockr.core-add_link` and `blockr.core-prepend_block` also need a free input on the block that the link goes to ([srcts/commands/core.ts](https://github.com/BristolMyersSquibb/blockr.core/blob/319f81c355383cdea9443be48d7e1d316c485a1c/srcts/commands/core.ts)).
So the hint says what to check, and the model finds the wrong id in its args, against the ids of every block that the Board section of each call holds ([The system prompt](Rewrite-1.4.5#the-sections)).

Each command of an edit is planned on the board that the commands before it leave, since a command checks its args against the board it gets, as `blockr.core-add_link` is enabled only where both of its blocks are on the board ([srcts/commands/core.ts#L337-L358](https://github.com/BristolMyersSquibb/blockr.core/blob/69770d0aa9ba04954775e7827944b92d66cc2630/srcts/commands/core.ts#L337-L358)), while `commands.plan()` gives each command the current board ([srcts/commands/commands.ts#L191-L194](https://github.com/BristolMyersSquibb/blockr.core/blob/69770d0aa9ba04954775e7827944b92d66cc2630/srcts/commands/commands.ts#L191-L194)).
The store's `run()` works out the board after each delta of a step before it commits any ([srcts/store/store.ts#L248-L293](https://github.com/BristolMyersSquibb/blockr.core/blob/69770d0aa9ba04954775e7827944b92d66cc2630/srcts/store/store.ts#L248-L293)), which gives the command registry the board for each command after the first.

Today's `inspect_results` evaluates the code in an environment whose parent is `baseenv()`, with every result that R holds bound to its block's id and a PNG device open that writes a file per page ([R/tools-read.R#L514-L690](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-read.R#L514-L690)).
A reply carries at most one binary body ([Wire protocol](Rewrite-1.1.9#outputs)), so the request returns its plots as base64 PNGs in its JSON value, within the blockr option `max_message_size`, 4 MiB by default ([Wire protocol](Rewrite-1.1.9#the-shiny-transport)).
A request that R loses to a new session is rejected rather than sent again ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)), so the tool hands the failure to the model.
The edit tool sends the request of step 6 after it awaits the evaluation of step 4, and so does `undo_edit`.
So each captures the active context before its first `await`, and sends the request inside `context.with()` of that context, which makes the tool's span active again while `core.request()` starts the request's span.
That keeps the request's span under the tool's, as [Assistant as a plugin](Rewrite-1.4#proposal) has it, and as a check with the `StackContextManager` of `@opentelemetry/sdk-trace` 3.1.1 showed, where the same request sent without `context.with()` started a trace of its own.
The library, pi, sends the plots of `inspect_results` on each of the three APIs: in the tool's result on Anthropic's Messages API and OpenAI's Responses API, and in a user message after the results on the Chat Completions API, which takes no image in a tool's result, while a model that takes no images gets "(see attached image)" in their place (`dist/api/anthropic-messages.js`, `dist/api/openai-responses-shared.js` and `dist/api/openai-completions.js` of `@earendil-works/pi-ai` 1.5.2).
R reads only a file that the skill bundles, and refuses any other with the list of those that it bundles, as today's `read_skill` does ([R/skills-invoke.R#L35-L45](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-invoke.R#L35-L45)).

The caps carry over as today's blockr options, at `fcbdb27`: `assistant_summary_max_chars` 2000, `assistant_state_max_chars` 20000, `assistant_state_value_max_chars` 128, `assistant_eval_max_chars` 16000, `assistant_board_section_max_chars` 1500, `assistant_description_max_chars` 1000, `assistant_skill_description_max_chars` 1024, `assistant_skill_catalogue_max_chars` 4000, `assistant_plot_render_px` 768, `assistant_plot_render_range` 200 to 2000 and `assistant_plot_render_max` 4 ([R/utils-bounds.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/utils-bounds.R)), and `assistant_review_max_blocks` 50 ([R/stage-review.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/stage-review.R)).
Today's review of a commit, `collect_touched_results()`, covers the changed blocks and those one link away on either side, the changed first ([R/stage-review.R#L167-L197](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/stage-review.R#L167-L197), [#L265-L288](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/stage-review.R#L265-L288)).
It gives each block's text from `summarise_result()`, and the state of each block that the commit added, with each value over `assistant_state_value_max_chars` left out and the whole cut at `assistant_summary_max_chars` ([#L235-L257](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/stage-review.R#L235-L257)).
The edit's review keeps those caps, and covers every block downstream rather than those one link away, since the one-time evaluation brings them all up to date.
A cap in the browser is read through `CoreApi.blockrOption()`, and one in a request through `blockr_option()`.
The new tools take the caps of the tools they follow: `list_commands`, `describe_command` and `list_plugins` cut each description at `assistant_description_max_chars`, as `list_block_types` does, and `get_plugin_state` cuts a state at `assistant_state_max_chars`, as `get_block_state` does.

</details>
