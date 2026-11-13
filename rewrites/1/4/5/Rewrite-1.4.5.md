# The system prompt
Status: review. Design for [Assistant as a plugin](Rewrite-1.4).

One of the design pages of the assistant ([Assistant as a plugin](Rewrite-1.4)): what the model is told before each call, the template with its rules, the sections that the plugin writes from the skills, the board and the focus, the order in which a call sends them, and where a deployment adds instructions of its own.
It shapes the Work items that run the agent loop and write the template, and the rewrite of the `layout` skill.
The tools that the prompt teaches are [The assistant's tools](Rewrite-1.4.2)'s, and how a change to the prompt is judged is [The assistant's benchmark](Rewrite-1.8.1)'s.

## What must hold

1. Every rule of today's template, and of the preambles of its focus section, carries over, changes with what it describes, or goes with its reason (Today).
2. The prompt names only tools that the model has, statuses that the scheduler gives and commands that the command registry holds, and nothing of staging.
3. The model is told the board, the blocks' statuses and the focus as they are when each call goes out.
4. Each section that the plugin writes stays within today's caps, so that no call fills the model's context.
5. A deployment adds instructions of its own through skills alone, and no app script writes the prompt.
6. A change to the template, the preambles, the sections' format or a tool's description merges only once [The assistant's benchmark](Rewrite-1.8.1) has compared it with the version before it.

## Today

Today's prompt has three parts, which `default_system_prompt()` joins in R, and which the server builds again whenever the board or the focus changes ([R/system-prompt.R#L57-L103](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/system-prompt.R#L57-L103)):

- The template, 944 words in ten paragraphs, which 20 commits have shaped ([inst/prompts/system-prompt.md](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md)).
- Three sections that R writes at the template's end: `## Skills`, the catalogue of the skills that no block or plugin scopes, `## Board`, the board with the dock's views, and `## Focus`, the blocks that the user last clicked or has in view and those that the user added with @, each kind under a preamble of its own ([R/system-prompt.R#L160-L190](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/system-prompt.R#L160-L190)).
- The `system_prompt` of `new_assistant_extension()`, which replaces the template, and which no app in the workspace passes ([Assistant as a plugin](Rewrite-1.4#today)).

Each paragraph of the template, and each preamble, goes as follows:

| Today, at `fcbdb27` | Where it goes |
|---|---|
| The role, "an assistant embedded next to a blockr data analysis board" ([#L1-L3](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L1-L3)) | Carried over |
| A result's summary is "a bounded overview, never the object itself", so the model never guesses at a result and reads it with `inspect_results` ([#L5-L12](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L5-L12)) | Carried over, since both tools stay ([The assistant's tools](Rewrite-1.4.2#the-tools)) |
| A block's state is bounded in the Board section too, so the model reads it with `get_block_state` before rewriting it, since `modify_block` "replaces the whole value" ([#L14-L19](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L14-L19)) | Changed, since a delta sets any of a block's state args and leaves the others ([Board updates](Rewrite-1.1.2#deltas)): the model reads an arg that the Board section cuts before it sets that arg anew |
| The statuses that mark a block, `waiting`, `unset`, `failed`, `unevaluated` and `stale`, what each says, and that a commit evaluates the blocks it changed and those linked to them, "and nothing further downstream" ([#L21-L42](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L21-L42)) | Changed, with `invalid` in place of `unset` ([Evaluation in the client](Rewrite-1.1.10#statuses)), and with the edit tool returning once every block downstream of an edit is current, up to `assistant_review_max_blocks` ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)), so that the warning about stale blocks further downstream holds only past that cap |
| Staging: the mutation tools stage, `commit` applies and reads back, `discard` drops, and a turn never ends with changes staged ([#L44-L61](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L44-L61)) | Replaced by the rules of the edit tool (The rules) |
| Ids never change, so renaming one is a removal and an addition, which "tears down the block server", after asking ([#L63-L67](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L63-L67)) | Changed: `blockr.core-rename_block` changes a block's name and never its id ([Board updates](Rewrite-1.1.2#commands)), so changing an id stays a removal and an addition, after asking, which evaluates again what is downstream, while the block's server goes with Shiny |
| The tool `modify_block` changes only the args that the Board section marks with `*`, and the block's name ([#L69-L72](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L69-L72)) | Dropped, since every block's state is open to external control on a board that is not locked ([Board updates](Rewrite-1.1.2#commands)), and the Board section marks no arg |
| The typed tools `add_<type>` and `modify_<type>`, and when to prefer them ([#L74-L83](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L74-L83)) | Dropped with the typed tools ([The assistant's tools](Rewrite-1.4.2#today)) |
| "Build, don't ask": what the user wants analysed is built rather than described, a choice left open takes the default that the data suggests, which the reply names, and only a real ambiguity is asked about ([#L85-L102](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L85-L102)) | Carried over, with an edit in place of staging and committing |
| "Answer concisely." ([#L104](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L104)) | Carried over |
| The preamble on the blocks last clicked or in view: what the user writes without naming a block is "most likely about the block they last clicked", though a click can be old ([R/system-prompt.R#L160-L172](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/system-prompt.R#L160-L172)) | Carried over, with the block that has focus in `CoreApi.focus` ([Plugins](Rewrite-1.1.12#what-a-frontend-offers-other-plugins)) |
| The preamble on the blocks added with @: they say "where the user's attention is", narrow nothing, and ask for no `focus_panel` ([#L174-L190](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/system-prompt.R#L174-L190)) | Carried over, without `focus_panel`, which goes with the view tools ([Assistant as a plugin](Rewrite-1.4#today)) |

## Proposal

### What a call sends, and in which order

Each call to the model sends, in this order:

1. The tools' definitions, which change only with a release of blockr.assistant, since the edit tool takes any command by its id ([The assistant's tools](Rewrite-1.4.2#the-tools)).
2. The system prompt: the template, and the catalogue of the skills that no block or plugin scopes, which changes only with the app's skills.
3. The thread's messages, those that the plugin keeps in its memory included ([The assistant's state](Rewrite-1.4.3#how-much-of-a-thread-the-state-keeps)).
4. The board and the focus as they are when the call goes out, which the plugin adds after the last message, and which the thread never keeps.

A provider's prompt cache serves the start of a call that matches an earlier one, and charges a fraction of the price of new input for it (notes).
Today's board section sits at the end of the system prompt, so each change to the board or the focus changes the system prompt, and the cache serves none of the thread after it, which is read again in full at the price of new input.
In this order, the cache serves the tools, the system prompt and the thread so far, and only the board, the focus and the newest messages are read anew.
During a turn, each call of the loop adds the board as that call finds it, after the edit tool's results, so that the model reads its newest state last.
How each provider takes text after a tool's result is for the issue that runs the loop to settle, and [The assistant's benchmark](Rewrite-1.8.1) compares this order with today's, by the questions that pass and by cost, before the issue that writes the template closes.

### The rules

The template keeps the rules that carry over (Today), and states those of the new tools:

- The model reads what an edit relies on rather than guessing at it, since a result's summary, a block's state in the Board section and a class's description are bounded: through `get_block_result`, `inspect_results`, `get_block_state`, `describe_block_type` or `describe_command` ([The assistant's tools](Rewrite-1.4.2#the-tools)).
- One edit is one list of commands, which applies all or none, as one undo step, in the order given: a block before its links, with an id that the model gives it, so that later commands of the list name it ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).
  An edit holds one change that the user would take back as one, so that the chat's Undo takes back what the user expects ([The assistant's chat](Rewrite-1.4.4#undoing-the-assistants-edits)).
- An edit returns the status of each block that it changed and of those downstream, which the model checks against what the user asked, correcting with another edit, rather than reporting as done a change that left a block `failed`, `invalid` or `waiting`.
- A refused edit names the command and why, so the model changes the args or the commands rather than sending the same list again.
- The commands come from `list_commands`, so the model looks up the frontend's own for views and panels, as the dock's are, and a plugin's own or `blockr.core-set_plugin_state` for that plugin's state, rather than assuming any.
- The tool `undo_edit` takes back the model's last edit, for when the user asks for that in words.
- On a locked board, the model tells the user what the lock refuses, as the edit tool returns it, rather than trying another way ([The assistant's tools](Rewrite-1.4.2#on-a-locked-board)).

The `layout` skill is written again for the dock's commands, since it teaches today's view tools ([Assistant as a plugin](Rewrite-1.4#today)).
It stays a skill, which the model reads where the dock is the frontend, rather than joining the template, which the calls under every frontend send.

### The sections

The plugin writes three sections from what `CoreApi` gives, in place of the generics `describe_board()` and `describe_block()` in R ([Assistant as a plugin](Rewrite-1.4#today)):

| Section | What it holds | Where it goes, within which cap |
|---|---|---|
| Skills | The name and description of each skill that no block or plugin scopes, from the reply to `list_skills` | The system prompt, within `assistant_skill_catalogue_max_chars`, 4000, and each description within `assistant_skill_description_max_chars`, 1024 |
| Board | Each block with its id, name, class, status and conditions, the links, the stacks, the app's plugins by their names, and, where the dock is the frontend, its views with the panels of each, from `store.board()`, `scheduler.status()` and `plugins.appPlugins()` | After the last message, each part within `assistant_board_section_max_chars`, 1500 |
| Focus | The block that has focus in `CoreApi.focus`, the blocks in the dock's active view where the dock is the frontend, and the blocks that the user added with @, each kind under its preamble | After the last message, after the board |

Each section keeps today's headings and markers, but for `invalid` in place of `unset` and the `*` that marked args, so that what the model reads of the board changes no more than the new tools ask, and the first comparison with today's baseline turns on the tools, the rules and the order ([The assistant's benchmark](Rewrite-1.8.1#todays-assistant-as-the-baseline)).

### What a deployment adds

A deployment adds instructions of its own as skills, through the blockr option `assistant_skills`, as CEDX's script adds four ([Assistant as a plugin](Rewrite-1.4#today)).
A skill's description in the catalogue tells the model when to read it, as CEDX's questions expect a clinical question's first call to read `clinical-existing-board` ([The assistant's benchmark](Rewrite-1.8.1#today)).
No app script replaces the template, since the `system_prompt` argument goes ([Assistant as a plugin](Rewrite-1.4#today)).

### One template for every model

The template is the same for every provider and model that [Model access](Rewrite-1.4.1) reaches.
Whether a model does better with words of its own is for the benchmark to show, and a template chosen by the model's id stays possible, which nothing here rules out.

### How the template changes

The template, the preambles and the code that writes the sections live in blockr.assistant, in the plugin's bundle, and change with its releases.
A pull request that changes any of them, or a tool's description, shows the benchmark's comparison of the change with the version before it (condition 6).
A Vitest snapshot of the prompt takes the place of today's golden copy ([tests/testthat/_snaps/system-prompt.md](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/tests/testthat/_snaps/system-prompt.md)), since it catches a change that nobody meant, while only the benchmark says whether a change that someone meant helps.

## Open questions

None.

<details><summary>Notes for implementers</summary>

Read on 2026-11-13:

- Anthropic: "Prompt caching covers the full prefix: `tools`, `system`, and `messages` (in that order)", and "Changes at each level invalidate that level and all subsequent levels", while a cache lives five minutes by default and a read costs 0.1 times the price of new input, 0.05 times on Claude Opus 5.5 and Claude Sonnet 5.5 ([Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)).
- OpenAI: "Prompt caching is enabled by default for supported OpenAI models", "Cache reuse requires the entire rendered prefix to match", and the guide advises "Put stable developer instructions and shared reference material first", with what changes "at the end rather than the beginning" ([Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)).

The commits that shaped today's template hold the lessons behind its rules, such as "Warn that an off-screen block's conditions are a snapshot" ([16a97d3](https://github.com/BristolMyersSquibb/blockr.assistant/commit/16a97d3)), which carries over with the statuses, and "State commit/discard as a hard end-of-turn rule to the model" ([669444b](https://github.com/BristolMyersSquibb/blockr.assistant/commit/669444b)), which goes with staging, so the issue that writes the template reads each with `git log -p -- inst/prompts/system-prompt.md`.

The preambles of the focus section are R code today, `screen_preamble()` and `focus_preamble()`, and become text in the plugin's bundle beside the template.

</details>
