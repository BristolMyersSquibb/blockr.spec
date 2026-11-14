# The assistant's tools
Status: settled on 2026-11-14. Design for [Assistant as a plugin](Rewrite-1.4).

One of the design pages of the assistant ([Assistant as a plugin](Rewrite-1.4)): the tools that the model calls, what each reads, changes and returns, and the requests that some of them send to R.
It shapes the Work items that build the tools, that compare the edit tool with other versions and that write blockr.assistant's migration notes, and the one in blockr.core that lets the command registry run and plan a list of commands.
Where the calls to a model go is [Model access](Rewrite-1.4.1)'s, the threads that hold the tools' calls and results are [The assistant's state](Rewrite-1.4.3)'s, how the chat shows those calls is [The assistant's chat](Rewrite-1.4.4)'s, and what the model is told before each call is [The system prompt](Rewrite-1.4.5)'s.

## What must hold

1. The model edits the board only through the commands of core's command registry, and takes an edit back only through `undo_edit` ([Assistant as a plugin](Rewrite-1.4#what-must-hold)).
   Each call of a tool that runs commands applies them as one step of the assistant, all or none.
   That step is an undo step of the assistant, unless every command of it has `undo: false` or it sets only board options ([Board updates](Rewrite-1.1.2#undo)).
2. The edit tool returns only once the blocks it changed, and those downstream of them, are current, unless the user stops the turn.
   Its review covers those blocks and the blocks that feed the changed ones.
   It gives each block's status, and what today's review of a commit gives: what `describe_result()` writes about each result, the conditions that appeared since the edit began, and the state of each block that the edit added.
3. The tools read the board, the block registry, the registered commands and each block's status in the browser, and send R a request only for what needs R: a block's result, the model's own R code, or the skills on the server.
4. Each tool bounds what it returns as the tool it follows does today, through today's blockr options.
5. Every read and every edit that today's 39 tools and its typed tools make carries over, through the tools below or the commands that the edit tool runs, but for what Today drops with its reason, here or on [Assistant as a plugin](Rewrite-1.4#today).
6. On a locked board, the model reads as on any board, but runs no R code of its own, and learns from the tool's result why the lock refuses an edit or its R code.

## Today

Today's assistant registers 39 tools as its chat is built, and the typed tools on top, each an `ellmer::tool()` that reads the board server's reactives, stages a change, or sets a board option at once, as `set_board_option` does ([R/ext-server.R#L485-L509](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L485-L509)).
It also registers the tools that the blockr option `assistant_tools` gives, which [Assistant as a plugin](Rewrite-1.4#today) drops, since the loop in the browser cannot call an R function.
Each of the 39 and the typed tools goes as follows:

| Today, at `fcbdb27` | Where it goes |
|---|---|
| `list_blocks`, `describe_block`, `get_block_state` and `get_block_conditions` ([R/tools-read.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-read.R)) | Kept, reading the board through `store.board()` and each block's status and conditions through `scheduler.status()`, while the generic `describe_block()`, which writes the text in R today, goes ([Assistant as a plugin](Rewrite-1.4#today)) |
| `list_links`, `list_stacks` and `describe_stack` | Kept, reading `store.board()`, while the generic `describe_stack()` goes, as `describe_block()` does |
| `list_block_types` and `describe_block_type`, which build a block of each class to read its data inputs. Today's `describe_block_type` also gives the worked examples that a class registers, each a complete state of its block | Kept, reading the block registry's entries, which give each class's data inputs, its arg specs and the JSON Schema of its state without building a block. The worked examples go, since core's merge block is the only class of core, blockr.dplyr, blockr.ggplot and blockr.io that registers any. The tool still gives each arg's example from the arg specs, and the guidance in full. The guidance is where blockr.dplyr writes its worked examples (notes). Whether whole examples help the model is for the benchmark to measure ([The assistant's benchmark](Rewrite-1.8.1#the-decisions-it-compares)) |
| `get_block_result`, which gives what `describe_result()` writes about a block's result | Kept, sending a request that R answers through `describe_result()` |
| `inspect_results`, which evaluates the model's R code with the result of each block that has one bound to the block's id | Kept, sending a request that reads only the blocks that the model names, since core has every block that a request reads evaluated first, while R refuses the request on a locked board |
| `list_views` and `validate_layout` ([R/tools-view.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-view.R)) | `get_plugin_state` on the dock's class id in place of `list_views`, while `validate_layout` goes, since the dock's commands check what they are given |
| The view tools that stage a change: `add_view`, `remove_view`, `rename_view`, `set_active_view`, `add_panel_to_view`, `remove_panel_from_view`, `move_panel`, `resize_panel` and `focus_panel` | The dock's commands, which the edit tool runs, in the same order: `blockr.dock-add_view`, `blockr.dock-remove_view`, `blockr.dock-rename_view`, `blockr.dock-activate_view`, `blockr.dock-add_panel`, `blockr.dock-remove_panel`, `blockr.dock-move_panel`, `blockr.dock-resize_panel` and `blockr.dock-activate_panel`, the last after `blockr.dock-activate_view` where the panel's view is not the active one, as `focus_panel` switches to it ([The dock's state](Rewrite-1.2.1#commands)). Today's `add_view` keeps the active view unless it is given `active`, while `blockr.dock-add_view` makes the new view active, so the model follows it with `blockr.dock-activate_view` where it keeps the view that was active. The `size` that `add_panel_to_view` takes goes, as [The dock's state](Rewrite-1.2.1) drops it, since nothing reads it |
| The mutation tools: `add_block`, `remove_block`, `modify_block`, `add_link`, `remove_link`, `modify_link`, `add_stack`, `remove_stack` and `modify_stack` ([R/tools-mutation.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-mutation.R)) | Core's commands, which the edit tool runs ([Board updates](Rewrite-1.1.2#commands)) |
| `list_extensions` and `describe_extension` ([R/tools-extension.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-extension.R)) | `list_plugins` and `get_plugin_state`, which read the app's plugins and each one's state, with the schema that describes it and the skills that name its class |
| `modify_extension` | Core's `blockr.core-set_plugin_state` and each plugin class's own commands, which the edit tool runs ([Plugins](Rewrite-1.1.12#a-plugins-state)) |
| `commit` and `discard` ([R/tools-commit.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-commit.R)) | The edit tool, which applies what it is given at once, so that nothing is staged to commit or discard |
| `list_board_options` and `set_board_option` ([R/tools-options.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-options.R)). Today's `list_board_options` gives each board option's value in the session and, as its `default`, the value that the board object holds | `list_board_options`, reading `core.options`, and core's `blockr.core-set_option`, which the edit tool runs. The `default` goes, since the board holds the value of every board option that something on the page requires, its default included, so that nothing tells a value that someone chose from a default ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)) |
| `read_skill` ([R/skills-invoke.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-invoke.R)) | Kept, sending a request that R answers |
| The typed tools `add_<type>` and `modify_<type>`, twenty of each at a time, whose args take each class's arg types ([R/tools-typed.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-typed.R)) | Dropped from the first version, since `describe_block_type` gives the JSON Schema of a class's state, and core's commands refuse a state that the schema refuses, naming each failure (notes). The benchmark compares that version with tools like these for each block class (The edit tool) |

## Proposal

### The tools

Each tool runs in the browser, and those that need R send a request of the assistant's plugin ([Plugins](Rewrite-1.1.12#a-plugins-requests)):

| Tool | What it returns or does | What it reads |
|---|---|---|
| `list_blocks` | Each block's id, name, registry id and status | `store.board()`, `scheduler.status()` |
| `describe_block` | One block's class, state, data inputs with the links into them, status, why it is `invalid` or `waiting` where it is, conditions, and the one-line summary of its result that `scheduler.status()` gives, and the skills that name its class | `store.board()`, `blockRegistry()`, `scheduler.status()`, the reply to `list_skills` |
| `get_block_state` | One block's state, within `assistant_state_max_chars` | `store.board()` |
| `get_block_conditions` | One block's conditions, by severity and phase | `scheduler.status()` |
| `list_links`, `list_stacks` and `describe_stack` | The links, the stacks, and one stack with its blocks | `store.board()` |
| `list_block_types` and `describe_block_type` | Each block class's id, name, category, data inputs and description, and one class's name, category, description and guidance in full, its data inputs, its arg specs, the JSON Schema of its state and the skills that name it | `blockRegistry()`, the reply to `list_skills` |
| `list_commands` and `describe_command` | Each registered command's id and description, and one command's description in full, its args as their JSON Schema has them, with a description of each arg, and whether it has `undo: false` | `commands.registered()` |
| `list_plugins` and `get_plugin_state` | Each of the app's plugins by its class's id and name, with the description that the schema of its class's state gives, and one plugin's state, with that schema, whose `description` keywords describe it, and the skills that name its class | `plugins.appPlugins()`, `plugins.pluginClass()`, `store.board()`, the reply to `list_skills` |
| `list_board_options` | Each board option that a loaded package defines, with its id, label, category and the JSON Schema of its value, and the value of each one that the board holds | `options.registered()`, `options.value()` |
| `get_block_result` | What `describe_result()` writes about one block's result | The request `describe_result` |
| `inspect_results` | What the model's R code prints, and up to four of the plots it draws, given the code, the ids of the blocks whose results it reads, and the width and height of its plots | The request `inspect_results` |
| `read_skill` | The text of a skill that the model may read, or a file that the skill holds | The request `read_skill` |
| `edit` | Runs a list of commands as one step of the assistant, and returns a review of the blocks it changed, those that feed them and those downstream (below) | `commands.run()`, `store.subscribe()`, `scheduler.evaluate()`, `scheduler.status()`, the request `describe_result` |
| `undo_edit` | Takes back the assistant's last undo step, past any step of the user's after it ([The assistant's chat](Rewrite-1.4.4#undoing-the-assistants-edits)), and returns as `edit` does (below) | `store.canUndo("assistant")`, `store.undo("assistant")`, and what `edit` reads |

The read tools that carry over keep today's names.
Of the two pairs that are new, `list_commands` and `describe_command` follow today's `list_block_types` and `describe_block_type`.
The pair `list_plugins` and `get_plugin_state` takes the place of `list_extensions`, `describe_extension` and `list_views` (Today), and follows `list_blocks` and `get_block_state` in its names and caps.
Every other read tool carries over one for one, as parity has it, and whether fewer tools serve the model better is for the benchmark to show ([The assistant's benchmark](Rewrite-1.8.1#the-decisions-it-compares)).
A tool that sends no request reads the board as it is now, and says of a block that reads `stale` or `unevaluated` that it does, without evaluating it.
A tool that sends a request has the blocks that the request reads evaluated first, as every request does ([Evaluation in the client](Rewrite-1.1.10#demand)).
The tools `list_plugins` and `get_plugin_state` leave out the assistant's own plugin, since its state holds the threads, and the model has its own thread already.
The tool `read_skill` is offered in every app, even where no skill is listed, so that the tools' definitions change only with a release of blockr.assistant ([The system prompt](Rewrite-1.4.5#what-a-call-sends-and-in-which-order)).
The tool `list_board_options` lists every board option that a loaded package defines, so that the model can set one that nothing on the page uses yet, such as `n_rows` before any table is drawn.
It gives the value of each board option that the board holds, and no value for the others, since core puts a default on the board only once something on the page requires the board option ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)).
The edit tool sets any of them through core's `blockr.core-set_option`, on a locked board too, since a lock leaves board options open ([Board options and blockr options](Rewrite-1.1.13#locked-boards)).
Unlike today's `set_board_option`, it refuses none of them, since `llm_model` goes and each thread keeps its own pick of the model ([Assistant as a plugin](Rewrite-1.4#proposal)).

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
2. Where a command refuses, the tool returns the command's index in the list, its id and each failure that the command registry names, such as a state that the schema of the block's class refuses, and the board stays as it was.
   The store then tells no subscriber of a change, so the scheduler sends R no block to evaluate, and nothing needs undoing (notes).
   Where the command is not enabled on the board as it is, as `blockr.core-add_link` refuses a block that the board lacks, the tool adds a hint that says what to check, so that the model can correct its args and edit again (notes).
   On a locked board, the hint says that the lock may be why, since core's `blockr.core-set_plugin_state` is not enabled there, and a plugin's own commands are not enabled for what the plugin locks ([Locked boards and the properties of blocks](Rewrite-1.1.11#plugins-on-a-locked-board)).
3. From the changes that the store announces for the step, one for each of its deltas, the tool takes the blocks that the step added or whose state or links it changed, every block downstream of them, and the blocks that feed the changed blocks directly ([Board updates](Rewrite-1.1.2#applying-a-delta)).
4. It brings those blocks up to date with one one-time evaluation, `core.scheduler.evaluate(blocks, undefined, { signal })`, given the signal of the turn, so that stopping the turn stops the wait ([Evaluation in the client](Rewrite-1.1.10#demand)).
   It passes no parameters, since a one-time evaluation with parameters has R run every block again, whether the block is current or not.
5. It picks the blocks that its review covers: at most `assistant_review_max_blocks` of them, 50 by default, the blocks it changed first, then those that feed them, then those downstream.
6. It sends one request, `describe_result`, which reads each of those blocks that reads `ready`, with the signal of the turn, and R answers with the text that `describe_result()` writes about each block's result (The requests in R).
7. It returns, for each of those blocks, its status and, where it is `invalid` or `waiting`, why, as `scheduler.status()` gives it, the conditions that appeared since the edit began, the text that `describe_result()` wrote and, for a block that the step added, its state, within the caps of today's review (notes).
   As today's review does, it marks as unverified a block that it changed and that has no result but has not failed, and it says how many blocks it left out.
   It names, by their ids, the blocks, links and stacks that the step added or removed, and says whether the step took an undo step (What must hold).

A block that the user edits meanwhile reports its status at its newer revision.
An edit that the user makes meanwhile delays the one-time evaluation and the request of step 6, rather than failing them ([Evaluation in the client](Rewrite-1.1.10#demand)).
A block that leaves the board meanwhile is named as removed, rather than left out as the one-time evaluation leaves it, so that the model does not report it as built ([The assistant's chat](Rewrite-1.4.4#while-a-turn-runs)).
Where every block of step 4 leaves the board meanwhile, the one-time evaluation rejects, and the tool names each of them as removed.
Where another board opens meanwhile, the one-time evaluation rejects too, and the tool returns that its commands applied to a board that is no longer open.
Where core rejects the request of step 6, as when the user changes one of its blocks so that it no longer reads `ready`, the tool sends the request once more without the blocks that the rejection names.
Where that fails too, the review gives the one-line summary of `scheduler.status()`, such as `<data.frame> [306 × 49]`, in place of each text.
Where R loses the request to a new session, the tool goes back to step 4 once, since every block reads `stale` in a new session (notes).

Some lists leave no block to evaluate, such as one that changes only the dock's views.
The tool then evaluates nothing and returns at once, since a one-time evaluation of no block rejects.
A stop while the tool waits leaves its commands applied.
So the tool still returns that they applied, with as much of the review as it has, and that the user stopped the turn, so that the model does not run them again ([The assistant's chat](Rewrite-1.4.4#stopping-a-turn)).
A stop while a command of the list waits in its `prepare()`, as the DAG's relayout waits for elkjs, does not stop `commands.run()`, which takes no signal ([Board updates](Rewrite-1.1.2#commands)).
The tool then waits for the call to settle, and returns whether the commands applied, with no review.

```json
{ "applied": true, "undo_step": true, "added": { "blocks": ["adults"], "links": ["<the id that add_link minted>"] }, "blocks": {
  "adults": { "status": "ready", "conditions": [], "result": "<what describe_result() writes, up to 2,000 characters>", "state": { "conditions": ["AGE >= 18"] } },
  "adsl": { "status": "ready", "conditions": [], "result": "<what describe_result() writes>" }
} }
{ "applied": false, "index": 1, "command": "blockr.core-add_link", "failures": ["It is not enabled on the board as it is, with the args {\"from\":\"adsl\",\"to\":\"adlts\"}."],
  "hint": "Check that each block, link, stack and plugin that the args name is on the board, and each board option is defined, with list_blocks, list_links, list_stacks, list_plugins or list_board_options, and that a block that a new link goes to has a free data input, with describe_block." }
```

The model learns which commands it can run from `list_commands`, which gives each command's `description`: what the command does and when to use it, as its package writes it for the model ([Board updates](Rewrite-1.1.2#commands)).
It learns what a command's args take from `describe_command`, which gives the command's description in full and the JSON Schema of its args, with a `description` of each arg.
Guidance on using several commands together, such as how to arrange the dock's views, goes first in a skill of the package, as the dock's `layout` skill does, and the benchmark compares that with the same guidance in the commands' descriptions ([The system prompt](Rewrite-1.4.5#what-a-package-adds)).
So a package that registers a command opens it to the assistant with no code of the assistant's, as today's `new_ext_meta()` opens an extension ([Board updates](Rewrite-1.1.2#what-must-hold)).
After `js-state` has merged into main, a pull request that changes a command's description shows the benchmark's comparison, in whichever package registers the command ([The assistant's benchmark](Rewrite-1.8.1#where-it-lives)).
The edit tool refuses a list that holds a command of the assistant's own, or core's `blockr.core-set_plugin_state` for the assistant's plugin, and `list_commands` leaves out the assistant's own commands, since only the assistant's chat and loop change its threads and each thread's pick of the model, as today's `set_board_option` refuses `llm_model`, which "drives the assistant's own chat client" ([R/tools-options.R#L93-L101](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-options.R#L93-L101)).

The tool `undo_edit` takes back the assistant's last undo step with `core.store.undo("assistant")`, which applies the undo as a new edit, and then returns as the edit tool does from step 3, so that the model learns what the undo changed.
That step may be another thread's, since the edits of every thread are steps of the one origin `assistant` ([The assistant's chat](Rewrite-1.4.4#undoing-the-assistants-edits)).
It passes over an edit that took no undo step, and leaves the board options as they are, as every undo does ([Board updates](Rewrite-1.1.2#undo)).
Where `core.store.canUndo("assistant")` is false, it changes nothing and returns that the assistant has no edit left to take back.
Where the store refuses the undo, as a lock or a check of the board refuses it, it returns why, as step 2 returns a refusal, and the board stays as it was.

The edit tool and `undo_edit` set pi's `executionMode` to `"sequential"`.
So where one response of the model calls either of them, pi runs every call of that response one after the other, in the model's order (notes).
By default, pi runs a response's calls at once, so a read that the model put after an edit could read the board from before the edit, and two edits could each take the other's changes into their review.

The edit tool is the first version of how the model edits the board.
The benchmark compares it with two others ([The assistant's benchmark](Rewrite-1.8.1#the-decisions-it-compares)):

- A tool per command, whose args are the command's `args`, so that the model reads them in the tool's definition rather than through `describe_command`.
- Beside the edit tool, two tools for each block class: one adds a block of the class, and one sets a block's state.
  Their args follow the JSON Schema of the class's state, as the args of today's `add_<type>` and `modify_<type>` follow the class's arg types.

Each tool of these versions runs the steps above on a list of one command, such as `blockr.core-add_block` or `blockr.core-set_block`.
So an edit through them takes one call for each command, and each call is a step of its own.
Their tools' definitions hold the schemas of the app's commands or classes, which a provider may refuse in part (notes).
How many tools for block classes the model is offered at once, as today's typed tools come twenty at a time, is for the issue that runs the comparison to settle.
The assistant keeps the version that passes the comparison ([The assistant's benchmark](Rewrite-1.8.1#what-a-comparison-reports)).

### The requests in R

The assistant's class gives R five requests through its method of `plugin_requests()`: the three that the tools send, and `list_skills` and `read_template`, which the plugin sends once a board opens.
The chat sends `read_skill` too, for a skill that the user calls with `/name` ([The assistant's chat](Rewrite-1.4.4#slash-commands)).
R calls each with the blocks that it reads in `reads`, each by its id with its result ([Plugins](Rewrite-1.1.12#a-plugins-requests)):

```r
plugin_requests.assistant_plugin <- function(x, ...) {                  # in blockr.assistant
  list(
    describe_result = function(reads) {                                  # the block that get_block_result names, or those of an edit's review
      lapply(reads, function(read) summarise_result(read$result))        # by block id: describe_result(), its errors caught, cut at assistant_summary_max_chars
    },
    inspect_results = function(code, reads, width = NULL, height = NULL) {
      if (isTRUE(as.logical(blockr_option("locked", FALSE)))) {          # an environment variable gives a string
        stop("The board is locked, so the assistant runs no R code of its own.")
      }
      env <- list2env(lapply(reads, `[[`, "result"), parent = baseenv())  # each block's result under its id
      run_inspection(parse(text = code), env, width, height)             # what it prints, and its plots as base64 PNGs
    },
    list_skills = function() skill_catalogue(),                          # the skills of the packages whose classes the app uses, then those of the directory that assistant_skills names
    read_template = function() template_text(),                          # the text of the file that assistant_template names, or NULL where it names none
    read_skill = function(name, path = NULL) skill_text(name, path)      # a skill's text, or a file that it bundles, named by path, since R binds file to a request's body
  )
}
```

```ts
const answer = await core.request("blockr.assistant-assistant_plugin", "inspect_results",
  { code: "table(adsl$ARM)" }, { reads: ["adsl"], signal });              // reads: the blocks that the model names
```

Core evaluates the blocks that a request reads first, even off screen, and sends the request only where each reads `ready`, rejecting it otherwise with their statuses ([Evaluation in the client](Rewrite-1.1.10#demand)).
The tool then hands the model those statuses, as it hands it a request that R loses to a new session (notes).

A stop cancels the request of `inspect_results` while it waits in R's queue.
Once R has started it, the model's code runs to its end, unless the app runs its requests in a worker that can stop one ([Wire protocol](Rewrite-1.1.9#cancelling)).
Until then, every request sent after it waits, the evaluations of the user's next edit among them.

The generic `describe_result()` stays blockr.assistant's in R, which writes what `get_block_result` and the edit's review give, and a package that teaches the model about a class of results gives a method of it, as the clinical data explorer does for its summary tables for clinical study reports.
The assistant's package gives a method for each class of results that the new stack brings, such as the `captured_plot` that a base plot's block returns, as today's gives one for `recordedplot` ([R/describe-result.R#L48-L91](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/describe-result.R#L48-L91), [Block classes in R](Rewrite-1.1.5#outputs)).
The description of `inspect_results` then says how to draw such a result again, in place of today's `evaluate::replay()` of a plot block's recordings ([R/tools-read.R#L655-L658](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-read.R#L655-L658)).

The reply to `list_skills` gives each skill's name and description, the classes that its frontmatter names, and today's two flags: `user-invocable`, whether the user may call the skill, and `disable-model-invocation`, whether the model may not read it.
A skill names block classes by registry id in `blocks:`, such as `blockr.dplyr-filter_block` in place of today's `filter_block`, and plugin classes by their ids in `plugins:`, such as `blockr.dock-dock_plugin`, in place of today's `extensions:`.
The tools `describe_block` and `describe_block_type` list the skills that name the block's class, and `get_plugin_state` those that name the plugin's class, as today's `describe_block`, `describe_block_type` and `describe_extension` list theirs ([R/skills-render.R#L14-L32](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-render.R#L14-L32)).
The system prompt lists only the skills that name no class ([The system prompt](Rewrite-1.4.5#the-sections)).
As today, these lists and the tool `read_skill` take only the skills that the model may read, while the chat's `/name` takes those that the user may call (notes).
What a skill written for today's stack changes at the switch is in the notes of [The conversion and the migration notes](Rewrite-1.9).

The reply to `read_template` gives the text of the file that the blockr option `assistant_template` names, or none where the option names no file, and the plugin puts in blockr.assistant's sections where the file names them ([The system prompt](Rewrite-1.4.5#what-a-deployment-adds)).

### On a locked board

The read tools and `read_skill` work on a locked board as on any other.
The store refuses an edit or an undo that a lock fixes, and the edit tool and `undo_edit` return why, as they return any refusal ([Locked boards and the properties of blocks](Rewrite-1.1.11#plugins-on-a-locked-board)).
Where a lock leaves a command not enabled, the edit tool's hint names the lock (The edit tool).
R refuses the request `inspect_results` on a locked board, since it evaluates what the client sends.
The tool refuses first, where `core.lock.board` is on, so that core evaluates none of the blocks that the request reads, and the model learns of the lock rather than of a block's status ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).

### How failures reach the model

A failure reaches the model as the result of the tool that met it, marked as an error, as today's tools return one ([R/tools-util.R#L1-L11](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-util.R#L1-L11)).
An edit that applied is never marked as an error, even where its review holds a `failed` block, or where the user stopped the turn while it waited.
Its text names what failed, why, and where the model can read more, as today's tools answer a block id that the board lacks with the hint "Call list_blocks first" ([R/tools-read.R#L86-L87](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-read.R#L86-L87)):

| What fails | What the model gets |
|---|---|
| A tool's args that its schema refuses | The schema's failures, from the library's check, so that the model calls the tool again with args that fit (notes) |
| A call to a tool that the plugin does not offer, such as a tool that a later release drops, which the model calls again in a thread that a board saved before | That no such tool is offered, as the library answers it (notes) |
| A block, a command, a plugin or a skill that a tool names and the board or the app lacks | That it is not there, with the tool that lists those that are, such as `list_blocks` |
| A command of an edit that refuses | The command's index and id, and each failure that the command registry names, with a hint where the command is not enabled on the board as it is, while the board stays as it was (The edit tool) |
| A block that an edit changed, or one downstream of it, that reads `failed`, `invalid` or `waiting` once evaluated | Its status, why it stopped and the conditions that appeared since the edit began, in the edit's review: the error of a `failed` block, the unset arg or the message of `blockr_invalid()` of an `invalid` one, and what a `waiting` one waits for ([Evaluation in the client](Rewrite-1.1.10#statuses)) |
| A request whose blocks do not read `ready` | The statuses of those blocks, with which core rejects it (The requests in R) |
| A request that R loses to a new session | That it was lost, since core sends it no more (notes) |
| An error in the model's own R code | The error's message, as R gives it |
| What a lock refuses | Why the lock refuses it, as the store, the edit tool's hint, the tool `inspect_results` or R says (On a locked board) |
| A value past its cap | What today's tools give for it: a value left out and marked, with the tool that reads it in full, as today's `describe_block` marks an arg too long to show ([R/describe-block.R#L126-L141](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/describe-block.R#L126-L141)), or a text cut and marked, as today's caps cut what `describe_result()` writes |
| A tool call that the user stops | A result saying that the user stopped the turn, which the plugin writes for each call left without one, since a provider takes a tool call in a thread only with its result ([The assistant's chat](Rewrite-1.4.4#stopping-a-turn)). An edit stopped while it waits says too that its commands applied (The edit tool) |

How each of these reads is a decision that [The assistant's benchmark](Rewrite-1.8.1#the-decisions-it-compares) compares, where its questions have turns that meet it.
None of these reaches the user as a notification, since the model tells the user of them in its reply.
R's failure to list the skills does, since the chat then goes on without them ([The assistant's chat](Rewrite-1.4.4#what-fails)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

The 40 tool definitions at `fcbdb27`, as at `fd58655`, by file: `tools-read.R` 11, `tools-view.R` 11, `tools-mutation.R` 9, `tools-extension.R` 3, `tools-commit.R` 2, `tools-options.R` 2, `skills-invoke.R` 1, `tools-typed.R` 1, the factory of the typed tools.

The schemas that the tools give the model come from the `args` of the registered commands, the schemas of plugin classes' state and the schemas that block classes' UIs ship, which the arg specs describe ([Board updates](Rewrite-1.1.2#commands)), and the arg specs are a JSON Schema subset that blockr.ai already binds through `ellmer::type_from_schema()`.
The loop's library, pi, takes such a schema as it is, since a tool's `parameters` is a plain JSON Schema object, as a run in a browser confirmed ([Assistant as a plugin](Rewrite-1.4)).
It checks each call's args against that schema before it runs the tool, and answers a call whose args fail, or a call to a tool that it does not offer, with an error as the tool's result (`prepareToolCall()` in `dist/agent-loop.js` of `@earendil-works/pi-agent-core` 1.5.2, with `validateToolArguments()` of `@earendil-works/pi-ai` 1.5.2).
It runs the calls of one response one after the other where any of them calls a tool whose `executionMode` is `"sequential"`, and at once otherwise, which is its default (`executeToolCalls()` in the same file).
The edit tool's own schema is fixed, and the schemas of commands and classes reach the model as text in a tool's result, so no provider checks them.
The two other versions put those schemas into tools' definitions, where a provider may refuse a keyword, as Gemini refuses the `additionalProperties` that OpenAI's strict mode requires ([R/tools-typed.R#L27-L33](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-typed.R#L27-L33)), so the issue that runs the comparison checks them on each provider.
On `js-state`, core's `blockr.core-add_block` and `blockr.core-set_block` check the state they set against the schema of the block's class, which the block's entry in the block registry carries, and refuse with each failure ([srcts/commands/core.ts#L101-L118](https://github.com/BristolMyersSquibb/blockr.core/blob/69770d0aa9ba04954775e7827944b92d66cc2630/srcts/commands/core.ts#L101-L118), [#L213-L221](https://github.com/BristolMyersSquibb/blockr.core/blob/69770d0aa9ba04954775e7827944b92d66cc2630/srcts/commands/core.ts#L213-L221)), which is what the typed tools give the model today through ellmer's types.

Today's `describe_block_type` gives the worked examples that a class passes to `register_block()` as `examples`, and none for a class that passes none ([R/tools-read.R#L349](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-read.R#L349)).
Core's merge block passes two, a left join and a full join ([inst/registry/blocks.yml#L240-L246](https://github.com/BristolMyersSquibb/blockr.core/blob/4064d835476c45967ac6bc282de37b739737c928/inst/registry/blocks.yml#L240-L246)).
The mutate and summarize blocks of blockr.dplyr give theirs in the guidance instead ([R/registry.R#L153-L170](https://github.com/BristolMyersSquibb/blockr.dplyr/blob/bdac6b38f7097425bfe96883032531cc919f6ee7/R/registry.R#L153-L170)).

The command registry refuses a command whose `enabled()` returns false with "It is not enabled on the board as it is, with the args …" ([srcts/commands/commands.ts#L170-L177](https://github.com/BristolMyersSquibb/blockr.core/blob/319f81c355383cdea9443be48d7e1d316c485a1c/srcts/commands/commands.ts#L170-L177)), since `enabled()` returns only true or false.
Nearly every `enabled()` of core's commands checks that an id in the args names a block, link, stack or plugin on the board, or a board option that a loaded package defines, while `blockr.core-add_link` and `blockr.core-prepend_block` also need a free data input on the block that the link goes to ([srcts/commands/core.ts](https://github.com/BristolMyersSquibb/blockr.core/blob/319f81c355383cdea9443be48d7e1d316c485a1c/srcts/commands/core.ts)).
So the hint says what to check, and the model finds the wrong id in its args, against the ids that the Board section of each call holds, or through `list_blocks` where that section's list is cut ([The system prompt](Rewrite-1.4.5#the-sections)).
Core's `blockr.core-set_plugin_state` is not enabled on a locked board ([srcts/commands/core.ts#L571](https://github.com/BristolMyersSquibb/blockr.core/blob/4507d893e8cd9e656fcebf75ee15dff34bb0768e/srcts/commands/core.ts#L571)), so there the hint names the lock.
A `CommandError` holds a message and its failures, but neither the index of the command that refused nor whether its `enabled()` refused it ([srcts/commands/commands.ts#L88-L105](https://github.com/BristolMyersSquibb/blockr.core/blob/4507d893e8cd9e656fcebf75ee15dff34bb0768e/srcts/commands/commands.ts#L88-L105)).
The Work item in blockr.core has the command registry give both where it refuses a list, so that the edit tool returns the index and adds its hint only for a command that is not enabled.

Each command of an edit is planned on the board that the commands before it leave, since a command checks its args against the board it gets, as `blockr.core-add_link` is enabled only where both of its blocks are on the board ([srcts/commands/core.ts#L337-L358](https://github.com/BristolMyersSquibb/blockr.core/blob/69770d0aa9ba04954775e7827944b92d66cc2630/srcts/commands/core.ts#L337-L358)), while `commands.plan()` gives each command the current board ([srcts/commands/commands.ts#L191-L194](https://github.com/BristolMyersSquibb/blockr.core/blob/69770d0aa9ba04954775e7827944b92d66cc2630/srcts/commands/commands.ts#L191-L194)).
The store's `run()` works out the board after each delta of a step before it commits any ([srcts/store/store.ts#L248-L293](https://github.com/BristolMyersSquibb/blockr.core/blob/69770d0aa9ba04954775e7827944b92d66cc2630/srcts/store/store.ts#L248-L293)), which gives the command registry the board for each command after the first.

The edit tool subscribes to the store before it calls `commands.run()`, and ends the subscription once the call settles.
It takes the changes of the origin `assistant` that it hears meanwhile, since the user and other plugins edit with origins of their own ([Board updates](Rewrite-1.1.2#the-store)).
An undo through the frontend's Undo carries the origin `user`, even where it takes back a step of the assistant's, so the edit tool does not take it for one of its own changes ([Board updates](Rewrite-1.1.2#undo)).
The tool `undo_edit` hears the changes of its undo within its call of `store.undo()`, which applies at once.
A step took an undo step unless every command of its list has `undo: false` in `commands.registered()`, or the changes that the tool heard set only board options ([Board updates](Rewrite-1.1.2#undo)).

Applying a delta in the browser costs little.
Evaluating a block in R costs more.
The store sets the board and announces a step only once every delta of the step has passed its checks ([srcts/store/store.ts#L348-L377](https://github.com/BristolMyersSquibb/blockr.core/blob/4507d893e8cd9e656fcebf75ee15dff34bb0768e/srcts/store/store.ts#L348-L377)).
The scheduler hears of a change only through `store.subscribe()` ([srcts/scheduler/scheduler.ts#L639-L642](https://github.com/BristolMyersSquibb/blockr.core/blob/4507d893e8cd9e656fcebf75ee15dff34bb0768e/srcts/scheduler/scheduler.ts#L639-L642)).
So a refused list starts no evaluation in R.
The edit tool therefore does not plan a list before it runs it, since `commands.plan()` would only repeat the checks of `commands.run()`.
Only a failure that R finds costs an evaluation, such as a filter on a column that the data lacks.
The edit then stays applied, and its review gives the error.

Today's `inspect_results` evaluates the code in an environment whose parent is `baseenv()`, with the result of each block that has one bound to its block's id, and a PNG device open that writes a file per page ([R/tools-read.R#L514-L690](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/tools-read.R#L514-L690), [R/utils-plot.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/utils-plot.R)).
A reply carries at most one binary body ([Wire protocol](Rewrite-1.1.9#outputs)), so the request returns its plots as base64 PNGs in its JSON value, within the blockr option `max_message_size`, 4 MiB by default ([Wire protocol](Rewrite-1.1.9#the-shiny-transport)).
A request that R loses to a new session is rejected rather than sent again ([Wire protocol](Rewrite-1.1.9#evaluating-a-block)), so the tool hands the failure to the model.
For the request of a review, the edit tool and `undo_edit` go back to step 4 once instead, since a new session holds no result, and every block reads `stale` until it is evaluated again ([Evaluation in the client](Rewrite-1.1.10#scheduling)).
The edit tool sends the request of step 6 after it awaits the evaluation of step 4, and so does `undo_edit`.
So each captures the active context before its first `await`, and sends the request inside `context.with()` of that context, which makes the tool's span active again while `core.request()` starts the request's span.
That keeps the request's span under the tool's, as [Assistant as a plugin](Rewrite-1.4#proposal) has it, and as a check with the `StackContextManager` of `@opentelemetry/sdk-trace` 3.1.1 showed, where the same request sent without `context.with()` started a trace of its own.
The library, pi, sends the plots of `inspect_results` on each of the three APIs: in the tool's result on Anthropic's Messages API and OpenAI's Responses API, and in a user message after the results on the Chat Completions API, which takes no image in a tool's result (`dist/api/anthropic-messages.js`, `dist/api/openai-responses-shared.js` and `dist/api/openai-completions.js` of `@earendil-works/pi-ai` 1.5.2).
For a model whose `input` lacks `"image"`, pi replaces each image of a tool's result with "(tool image omitted: model does not support images)" before any API's conversion (`downgradeUnsupportedImages()` in `dist/api/transform-messages.js` of the same package).
R reads only a file that the skill bundles, and refuses any other with the list of those that it bundles, as today's `read_skill` does ([R/skills-invoke.R#L35-L45](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-invoke.R#L35-L45)).
The tool `read_skill` refuses a skill whose frontmatter sets `disable-model-invocation`, as today's refuses it ([R/skills-invoke.R#L16-L29](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-invoke.R#L16-L29)).
The request still reads such a skill for the chat's `/name`, where the skill's frontmatter sets `user-invocable`.
R lists the skills once a board opens, while today's catalogue is read again whenever a `SKILL.md` changes ([R/skills-scan.R#L8-L16](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-scan.R#L8-L16)).
So an edit to a skill reaches the model with the next board that opens, which serves skills that change with a deployment's releases.

The caps carry over as today's blockr options, at `fcbdb27`: `assistant_summary_max_chars` 2000, `assistant_state_max_chars` 20000, `assistant_state_value_max_chars` 128, `assistant_eval_max_chars` 16000, `assistant_board_section_max_chars` 1500, `assistant_description_max_chars` 1000, `assistant_skill_description_max_chars` 1024, `assistant_skill_catalogue_max_chars` 4000, past which R only logs a warning, `assistant_plot_render_px` 768, `assistant_plot_render_range` 200 to 2000 and `assistant_plot_render_max` 4 ([R/utils-bounds.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/utils-bounds.R)), and `assistant_review_max_blocks` 50 ([R/stage-review.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/stage-review.R)).
Today's review of a commit, `collect_touched_results()`, covers the changed blocks and those one link away on either side, the changed first ([R/stage-review.R#L167-L197](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/stage-review.R#L167-L197), [#L265-L288](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/stage-review.R#L265-L288)).
It gives each block's text from `summarise_result()`, and the state of each block that the commit added, with each value over `assistant_state_value_max_chars` left out and the whole cut at `assistant_summary_max_chars` ([#L235-L257](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/stage-review.R#L235-L257)).
It gives too the conditions that appeared since the commit began, of any block, against those that the board held as the commit started ([R/ext-server.R#L891-L901](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L891-L901), [#L972](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L972)).
It marks as unverified a block that the commit changed and that has no result but has not failed ([R/stage-review.R#L212-L233](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/stage-review.R#L212-L233)).
The edit's review keeps those caps, and covers every block downstream rather than those one link away, since the one-time evaluation brings them all up to date.
The edit tool reads the conditions of the blocks on the board before step 1, and its review gives, of the blocks that it covers, only the conditions that the tool did not read then.
A cap in the browser is read through `CoreApi.blockrOption()`, and one in a request through `blockr_option()`.
The new tools take the caps of the tools they follow.
The tools `list_commands` and `list_plugins` cut each description at `assistant_description_max_chars`, as `list_block_types` does, and point at `describe_command` and `get_plugin_state` for the rest.
The tool `describe_command` cuts nothing, as `describe_block_type` cuts nothing, and `get_plugin_state` cuts a state at `assistant_state_max_chars`, as `get_block_state` does.

</details>
