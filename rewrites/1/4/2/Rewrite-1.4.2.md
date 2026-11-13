# The assistant's tools
Status: review. Design for [Assistant as a plugin](Rewrite-1.4).

One of the design pages of the assistant ([Assistant as a plugin](Rewrite-1.4)): the tools that the model calls, what each reads, changes and returns, the requests that some of them send to R, and what the model is told before each call.
It shapes the Work items that build the tools and the loop, and the one in blockr.core that lets the command registry plan a list of commands.
Where the calls to a model go is [Model access](Rewrite-1.4.1)'s, and the threads that hold the tools' calls and results are [The assistant's state](Rewrite-1.4.3)'s.

## What must hold

1. The model edits the board through one tool alone, the edit tool, whose commands apply as one undo step of the assistant, all or none, through core's command registry, and takes such an edit back through `undo_edit` alone ([Assistant as a plugin](Rewrite-1.4#what-must-hold)).
2. The edit tool returns only once the blocks it changed, and those downstream of them, are current, with each block's status, conditions and summary.
3. The tools read the board, the block registry, the registered commands and each block's status in the browser, and send R a request only for what needs R: a block's result, the model's own R code, or the skills on the server.
4. What each tool returns is bounded by today's blockr options, so that no call fills the model's context.
5. Every read and every edit that today's 40 tools make carries over, through the tools below or the commands that the edit tool runs, but for what Today drops with its reason.
6. On a locked board, the model reads as on any board, and learns from the edit tool why the lock refuses an edit.

## Today

Today's assistant registers 39 tools as its chat is built, and the typed tools on top, each an `ellmer::tool()` that reads the board server's reactives or stages a change ([R/ext-server.R#L485-L509](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L485-L509)).
Each goes as follows:

| Today, at `fcbdb27` | Where it goes |
|---|---|
| `list_blocks`, `describe_block`, `get_block_state` and `get_block_conditions` ([R/tools-read.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-read.R)) | Kept, reading the board through `store.board()` and each block's status and conditions through `scheduler.status()` |
| `list_links`, `list_stacks` and `describe_stack` | Kept, reading `store.board()` |
| `list_block_types` and `describe_block_type`, which build a block of each class to read its inputs | Kept, reading the block registry's entries, which give each class's inputs, its arg specs and the JSON Schema of its state without building a block |
| `get_block_result`, which summarizes a block's result through `describe_result()` | Kept, sending a request that R answers through `describe_result()` |
| `inspect_results`, which evaluates the model's R code with every result bound to its block's id | Kept, sending a request that reads only the blocks the model names, and which R refuses on a locked board |
| `list_views` and `validate_layout` ([R/tools-view.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-view.R)) | `get_plugin_state` on the dock's class id in place of `list_views`, while `validate_layout` goes, since the dock's commands check what they are given |
| The view tools that stage a change: `add_view`, `remove_view`, `rename_view`, `set_active_view`, `add_panel_to_view`, `remove_panel_from_view`, `move_panel`, `resize_panel` and `focus_panel` | The dock's commands, from `blockr.dock-add_view` to `blockr.dock-resize_panel`, which the edit tool runs ([The dock's state](Rewrite-1.2.1#commands)) |
| The mutation tools: `add_block`, `remove_block`, `modify_block`, `add_link`, `remove_link`, `modify_link`, `add_stack`, `remove_stack` and `modify_stack` ([R/tools-mutation.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-mutation.R)) | Core's commands, which the edit tool runs ([Board updates](Rewrite-1.1.2#commands)) |
| `list_extensions` and `describe_extension` ([R/tools-extension.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-extension.R)) | `list_plugins` and `get_plugin_state`, which read the app's plugins and each one's state, with the schema that describes it |
| `modify_extension` | Core's `blockr.core-set_plugin_state` and each plugin class's own commands, which the edit tool runs ([Plugins](Rewrite-1.1.12#a-plugins-state)) |
| `commit` and `discard` ([R/tools-commit.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-commit.R)) | The edit tool, which applies what it is given at once, so that nothing is staged to commit or discard |
| `list_board_options` and `set_board_option` ([R/tools-options.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-options.R)) | `list_board_options`, reading `core.options`, and core's `blockr.core-set_option`, which the edit tool runs |
| `read_skill` ([R/skills-invoke.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-invoke.R)) | Kept, sending a request that R answers |
| The typed tools `add_<type>` and `modify_<type>`, twenty of each at a time, whose args take each class's arg types ([R/tools-typed.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-typed.R)) | Dropped, since `describe_block_type` gives the JSON Schema of a class's state, and core's commands refuse a state that the schema refuses, naming each failure (notes) |

## Proposal

### The tools

Each tool runs in the browser, and the three that need R send a request of the assistant's plugin ([Plugins](Rewrite-1.1.12#a-plugins-requests)):

| Tool | What it returns or does | What it reads |
|---|---|---|
| `list_blocks` | Each block's id, name, registry id and status | `store.board()`, `scheduler.status()` |
| `describe_block` | One block's class, state, inputs with the links into them, status, conditions and summary | `store.board()`, `blockRegistry()`, `scheduler.status()` |
| `get_block_state` | One block's state in full | `store.board()` |
| `get_block_conditions` | One block's conditions, by severity and phase | `scheduler.status()` |
| `list_links`, `list_stacks` and `describe_stack` | The links, the stacks, and one stack with its blocks | `store.board()` |
| `list_block_types` and `describe_block_type` | Each block class's id, name and description, and one class's inputs, arg specs and the JSON Schema of its state | `blockRegistry()` |
| `list_commands` and `describe_command` | Each registered command's id and description, and one command's args, as their JSON Schema has them | `commands.registered()` |
| `list_plugins` and `get_plugin_state` | Each of the app's plugins by its class's id and name, and one plugin's state, with the descriptions of its class's schema | `plugins.appPlugins()`, `store.board()` |
| `list_board_options` | Each board option in use, with its value and its description | `options.inUse()`, `options.value()` |
| `get_block_result` | The summary of one block's result, as `describe_result()` writes it | The request `describe_result` |
| `inspect_results` | What the model's R code prints, and up to four of the plots it draws | The request `inspect_results` |
| `read_skill` | A skill's text, or a file that the skill holds | The request `read_skill` |
| `edit` | Runs a list of commands as one step of the assistant, and returns the status of each block it changed and of those downstream (below) | `commands.run()`, `scheduler.evaluate()` |
| `undo_edit` | Takes back the assistant's last edit, as the chat's Undo does ([The assistant's chat](Rewrite-1.4.4#undoing-the-assistants-edits)) | `store.undo("assistant")` |

The read tools keep today's names, and the two pairs that are new follow today's `list_block_types` and `describe_block_type`.
They carry over one for one, as parity has it, and whether fewer tools serve the model better is for the benchmarks to show ([Benchmarks of the new stack](Rewrite-1.8)).
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

1. The edit tool runs the list with `core.commands.run(list, "assistant")`.
   The command registry plans each command on the board that the commands before it leave, and the store applies them all as one step of the origin `assistant`, or applies none ([Board updates](Rewrite-1.1.2#commands)).
2. Where a command refuses, the tool returns the command's id and each failure that the command registry names, such as a state that the schema of the block's class refuses, and the board stays as it was.
3. From the change that the store announces, the tool takes the blocks that the step added or whose state or links it changed, and every block downstream of them ([Board updates](Rewrite-1.1.2#following-the-board)).
4. It brings those blocks up to date with one one-time evaluation, `core.scheduler.evaluate(blocks, { signal })`, given the signal of the turn, so that stopping the turn stops the wait ([Evaluation in the client](Rewrite-1.1.10#demand)).
5. It returns each block's status, conditions and summary, as `scheduler.status()` gives them, for at most `assistant_review_max_blocks` blocks, 50 by default.

A block that the user edits meanwhile reports its newer revision, and a block that leaves the board meanwhile is left out, as a one-time evaluation leaves it out.
A list that changes only the state of plugins, such as the dock's views, evaluates nothing, and the tool returns at once.

```json
{ "applied": true, "blocks": { "adults": { "status": "ready", "summary": "<data.frame> [306 × 49]", "conditions": [] } } }
{ "applied": false, "command": "blockr.core-add_link", "failures": ["It is not enabled on the board as it is, with the args {\"from\":\"adsl\",\"to\":\"adlts\"}."] }
```

The model learns which commands it can run, and what their args take, from `list_commands` and `describe_command`.
So a package that registers a command opens it to the assistant with no code of the assistant's, as today's `new_ext_meta()` opens an extension ([Board updates](Rewrite-1.1.2#what-must-hold)).
The edit tool refuses a list that holds a command of the assistant's own, or core's `blockr.core-set_plugin_state` for the assistant's plugin, and `list_commands` leaves them out, since only the assistant's chat and loop change its threads and its pick of the model, as today's `set_board_option` refuses `llm_model`, which "drives the assistant's own chat client" ([R/tools-options.R#L93-L100](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-options.R#L93-L100)).

### The requests in R

The assistant's class gives R four requests through its method of `plugin_requests()`: the three that the tools send, and `list_skills`, which the plugin sends once a board opens.
R calls each with the blocks that it reads in `reads`, each by its id with its result ([Plugins](Rewrite-1.1.12#a-plugins-requests)):

```r
plugin_requests.assistant_plugin <- function(x, ...) {                  # in blockr.assistant
  list(
    describe_result = function(reads) {                                  # the one block that get_block_result names
      summarise_result(reads[[1L]]$result)                                # describe_result(), its errors caught, cut at assistant_summary_max_chars
    },
    inspect_results = function(code, reads, width = NULL, height = NULL) {
      if (isTRUE(blockr_option("locked", FALSE))) {
        stop("The board is locked, so the assistant runs no R code of its own.")
      }
      env <- list2env(lapply(reads, `[[`, "result"), parent = baseenv())  # each block's result under its id
      run_inspection(parse(text = code), env, width, height)             # what it prints, and its plots as base64 PNGs
    },
    list_skills = function() skill_catalogue(),                          # the package's skills and those of the directory that assistant_skills names
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
So `describe_result()` stays a generic of blockr.assistant's in R, and a package that teaches the model about a class of results gives a method of it, as blockr.sandbox does for its composer tables.

### What the model is told before each call

The plugin builds the system prompt as `default_system_prompt()` builds it today ([R/system-prompt.R#L57-L103](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/system-prompt.R#L57-L103)), from the template in its bundle and three sections:

- The skills that no block or plugin scopes, from the reply to `list_skills`.
- The board: each block with its status and conditions, the links, the stacks and the app's plugins, each section cut at `assistant_board_section_max_chars`.
- The focus: the block that has focus in `CoreApi.focus`, the blocks that the user added with @, and, where the dock is the frontend, the blocks in its active view.

It builds the prompt again before each call to the model, from the board, the statuses and the focus as they are then, rather than on every change to them, as today's server does.
The template keeps today's rules, with the edit tool in place of staging and committing.

### On a locked board

The read tools and `read_skill` work on a locked board as on any other.
The store refuses an edit that a lock fixes, and the edit tool returns why, as it returns any refusal ([Locked boards and the properties of blocks](Rewrite-1.1.11#plugins-on-a-locked-board)).
R refuses `inspect_results`, since it evaluates what the client sends.

## Open questions

None.

<details><summary>Notes for implementers</summary>

The 40 tool definitions at `fcbdb27`, as at `fd58655`, by file: `tools-read.R` 11, `tools-view.R` 11, `tools-mutation.R` 9, `tools-extension.R` 3, `tools-commit.R` 2, `tools-options.R` 2, `skills-invoke.R` 1, `tools-typed.R` 1, the factory of the typed tools.

Tool schemas come from the `args` of the registered commands, the schemas of plugin classes' state and the schemas that block classes' UIs ship, which the arg specs describe ([Board updates](Rewrite-1.1.2#commands)), and the arg specs are a JSON Schema subset that blockr.ai already binds through `ellmer::type_from_schema()`.
The AI SDK's `jsonSchema()` takes such a schema as it is, while pi types its tools with TypeBox, so the spike checks that such a schema passes pi's validation unchanged.
On `js-state`, core's `blockr.core-add_block` and `blockr.core-set_block` check the state they set against the schema of the block's class, which the block's entry in the block registry carries, and refuse with each failure ([srcts/commands/core.ts#L101-L118](https://github.com/BristolMyersSquibb/blockr.core/blob/69770d0aa9ba04954775e7827944b92d66cc2630/srcts/commands/core.ts#L101-L118)), which is what the typed tools give the model today through ellmer's types.

Each command of an edit is planned on the board that the commands before it leave, since a command checks its args against the board it gets, as `blockr.core-add_link` is enabled only where both of its blocks are on the board ([srcts/commands/core.ts#L337-L358](https://github.com/BristolMyersSquibb/blockr.core/blob/69770d0aa9ba04954775e7827944b92d66cc2630/srcts/commands/core.ts#L337-L358)), while `commands.plan()` gives each command the current board ([srcts/commands/commands.ts#L191-L194](https://github.com/BristolMyersSquibb/blockr.core/blob/69770d0aa9ba04954775e7827944b92d66cc2630/srcts/commands/commands.ts#L191-L194)).
The store's `run()` works out the board after each delta of a step before it commits any ([srcts/store/store.ts#L248-L293](https://github.com/BristolMyersSquibb/blockr.core/blob/69770d0aa9ba04954775e7827944b92d66cc2630/srcts/store/store.ts#L248-L293)), which gives the command registry the board for each command after the first.

Today's `inspect_results` evaluates the code in an environment whose parent is `baseenv()`, with every result that R holds bound to its block's id and a PNG device open that writes a file per page ([R/tools-read.R#L514-L690](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-read.R#L514-L690)).
A reply carries at most one binary body ([Wire protocol](Rewrite-1.1.9#outputs)), so the request returns its plots as base64 PNGs in its JSON value, within the blockr option `max_message_size`, 4 MiB by default ([Wire protocol](Rewrite-1.1.9#the-shiny-transport)).
A request that R loses to a new session is rejected rather than sent again ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)), so the tool hands the failure to the model.

The caps carry over as today's blockr options, at `fcbdb27`: `assistant_summary_max_chars` 2000, `assistant_state_max_chars` 20000, `assistant_state_value_max_chars` 128, `assistant_eval_max_chars` 16000, `assistant_board_section_max_chars` 1500, `assistant_description_max_chars` 1000, `assistant_skill_description_max_chars` 1024, `assistant_skill_catalogue_max_chars` 4000, `assistant_plot_render_px` 768, `assistant_plot_render_range` 200 to 2000 and `assistant_plot_render_max` 4 ([R/utils-bounds.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/utils-bounds.R)), and `assistant_review_max_blocks` 50 ([R/stage-review.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/stage-review.R)).
A cap in the browser is read through `CoreApi.blockrOption()`, and one in a request through `blockr_option()`.

A prompt that changes with every call defeats a provider's prompt cache, which keys on the start of a prompt, so moving the board and the focus to the end of each request, out of the system prompt, is a change for the benchmarks to weigh.

</details>
