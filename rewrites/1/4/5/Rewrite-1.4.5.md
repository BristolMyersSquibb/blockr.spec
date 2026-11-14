# The system prompt
Status: review. Design for [Assistant as a plugin](Rewrite-1.4).

One of the design pages of the assistant ([Assistant as a plugin](Rewrite-1.4)): what the model is told before each call, the template with its rules, the sections that the plugin writes from the skills, the board and the focus, the order in which a call sends them, the note of what others changed in the board, and where a package or a deployment adds instructions of its own.
It shapes the Work items that run the agent loop, write the template and write the dock's `layout` skill.
The tools that the prompt teaches are [The assistant's tools](Rewrite-1.4.2)'s, and how a change to the prompt is judged is [The assistant's benchmark](Rewrite-1.8.1)'s.

## What must hold

1. Every rule of today's template, and of the preambles of its sections, carries over, changes with what it describes, or goes with its reason (Today).
2. The prompt names only tools that the model has, statuses that the scheduler gives and commands that the command registry holds, and nothing of staging.
3. The model is told the board, the blocks' statuses and the focus as they are when each call goes out.
4. Each section that the plugin writes is bounded as today, so that no call fills the model's context.
5. A deployment adds instructions of its own through skills alone, and no app script writes the prompt.
6. A change to the template, the preambles, the sections' format, a tool's description or a skill that a package of the new stack gives, such as the dock's `layout`, merges only once [The assistant's benchmark](Rewrite-1.8.1) has compared it with the version before it.
7. Before each call, the model learns what the user or another plugin changed in the board's blocks, links and stacks since the thread's previous call, and the thread keeps what it learned.
8. A package gives the model guidance on its block classes and plugins as skills of its own, with no dependency on blockr.assistant, and the model sees them only in an app that offers those block classes or runs those plugins.

## Today

Today's prompt has three parts, which `default_system_prompt()` joins in R ([R/system-prompt.R#L57-L103](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/system-prompt.R#L57-L103)), and which the server builds again whenever the board or the focus changes ([R/ext-server.R#L805-L840](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L805-L840)):

- The template, 944 words in ten paragraphs, which 20 commits have shaped ([inst/prompts/system-prompt.md](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md)).
- Three sections that R writes at the template's end: `## Skills`, the catalogue of the skills that the model may read and that no block class or extension scopes, under a preamble ([R/skills-render.R#L1-L70](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-render.R#L1-L70)), `## Board`, the board with the dock's views ([R/describe-board.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/describe-board.R)), and `## Focus`, the blocks that the user last clicked or has in view and those that the user added with @, each kind under a preamble of its own ([R/system-prompt.R#L105-L190](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/system-prompt.R#L105-L190)).
- The `system_prompt` of `new_assistant_extension()`, which replaces the template, and which no app in the workspace passes ([Assistant as a plugin](Rewrite-1.4#today)).

Each paragraph of the template, and each preamble, goes as follows:

| Today, at `fcbdb27` | Where it goes |
|---|---|
| The role, "an assistant embedded next to a blockr data analysis board", and that "The Board section below is the current shape of the board" ([#L1-L3](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L1-L3)) | Carried over, with the Board section in a message of the app's after the thread's last message, rather than below the template (What a call sends) |
| A result's summary is "a bounded overview, never the object itself", so the model never guesses at a result and reads it with `inspect_results`, "read-only R over any block's result" ([#L5-L12](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L5-L12)) | Carried over, since both tools stay ([The assistant's tools](Rewrite-1.4.2#the-tools)), with `inspect_results` reading the results of the blocks that the model names ([The assistant's tools](Rewrite-1.4.2#the-requests-in-r)) |
| The state that `describe_block` reports is bounded too, with an arg "too long to show" left out and marked, so the model reads it with `get_block_state` before rewriting it, since `modify_block` "replaces the whole value" ([#L14-L19](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L14-L19)) | Changed, since a delta sets any of a block's state args and leaves the others ([Board updates](Rewrite-1.1.2#deltas)): the model reads an arg that `describe_block` leaves out before it sets that arg anew |
| The statuses that mark a block, `waiting`, `unset`, `failed`, `unevaluated` and `stale`, what each says, that an `unevaluated` or `stale` block is off screen and has no result to read, and that a commit evaluates the blocks it changed and those linked to them, "and nothing further downstream" ([#L21-L42](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L21-L42)) | Changed: `invalid` takes the place of `unset`, and `unevaluated` and `stale` hold on screen as off it, as the scheduler gives them ([Evaluation in the client](Rewrite-1.1.10#statuses)). A request evaluates the blocks that it reads first, so `get_block_result` and `inspect_results` read the result of an `unevaluated` or `stale` block rather than finding none ([The assistant's tools](Rewrite-1.4.2#the-requests-in-r)). The edit tool returns once every block downstream of an edit is current ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)), so the warning about stale blocks further downstream goes, and where an edit leaves out the statuses of the blocks past `assistant_review_max_blocks`, the model says that it has not checked them (The rules) |
| Staging: the mutation tools stage, `commit` applies and reads back, `discard` drops, and a turn never ends with changes staged ([#L44-L61](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L44-L61)) | Replaced by the rules of the edit tool (The rules) |
| Ids never change, so renaming one is a removal and an addition, which "tears down the block server", after asking ([#L63-L67](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L63-L67)) | Changed: `blockr.core-rename_block` changes a block's name and never its id ([Board updates](Rewrite-1.1.2#commands)), so changing an id stays a removal and an addition, after asking, which evaluates again what is downstream, while the block's server goes with Shiny |
| The tool `modify_block` changes only the args that the Board section marks with `*`, and the block's name ([#L69-L72](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L69-L72)) | Dropped, since every block's state is open to external control on a board that is not locked ([Board updates](Rewrite-1.1.2#commands)), and the Board section marks no arg |
| The typed tools `add_<type>` and `modify_<type>`, and when to prefer them ([#L74-L83](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L74-L83)) | Dropped with the typed tools ([The assistant's tools](Rewrite-1.4.2#today)) |
| "Build, don't ask": what the user wants analysed is built rather than described, a choice left open takes the default that the data suggests, which the reply names, and only a real ambiguity is asked about ([#L85-L102](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L85-L102)) | Carried over, with an edit in place of staging and committing |
| "Answer concisely." ([#L104](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/inst/prompts/system-prompt.md#L104)) | Carried over |
| The preamble of the skills' catalogue: the skills are "Guidance authored for this deployment", the model reads one with `read_skill` and follows it before acting where the skill bears on what the model is about to do, a skill is "instruction text, not extra capability", and where a skill and the prompt disagree, "this prompt wins" ([R/skills-render.R#L54-L66](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-render.R#L54-L66)) | Changed: the guidance comes from the app's packages as well as from the deployment (What a package adds). The rest carries over, since `read_skill` stays ([The assistant's tools](Rewrite-1.4.2#the-tools)) |
| The preamble on the blocks last clicked or in view: what the user writes without naming a block is "most likely about the block they last clicked", though a click can be old ([R/system-prompt.R#L160-L172](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/system-prompt.R#L160-L172)) | Carried over, with the block that has focus in `CoreApi.focus` ([Plugins](Rewrite-1.1.12#what-a-frontend-offers-other-plugins)), and with the panels that show in place of the blocks in view (The sections) |
| The preamble on the blocks added with @: they say "where the user's attention is", narrow nothing, and ask for no `focus_panel` ([#L174-L190](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/system-prompt.R#L174-L190)) | Dropped with the @ button, since the user no longer picks blocks ([The assistant's chat](Rewrite-1.4.4#today)) |

## Proposal

### What a call sends, and in which order

Each call to the model sends, in this order:

1. The tools' definitions, which change only with a release of blockr.assistant, since the edit tool takes any command by its id ([The assistant's tools](Rewrite-1.4.2#the-tools)).
   That holds for the edit tool, the first version.
   The two versions that the benchmark compares with it put the schemas of the app's commands or block classes into the definitions, so that theirs change with the app's packages, and within a thread where the tools for block classes come a few at a time ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).
   The benchmark reports, for each version, how many of its input tokens the cache served ([The assistant's benchmark](Rewrite-1.8.1#what-a-comparison-reports)).
2. The system prompt: the template, and the catalogue of the skills that no block class or plugin scopes, which changes only with the app's skills.
3. The thread's messages, those that the plugin keeps in its memory included ([The assistant's state](Rewrite-1.4.3#how-much-of-a-thread-the-state-keeps)).
4. The board and the focus as they are when the call goes out, which the plugin adds after the last message, and which the thread never keeps.

The plugin adds the board and the focus through pi's `transformContext`, which runs before each call, so that no call goes out for them alone.
At a turn's first call, they show the board that the user's new message is about.
At each later call of the turn, they come after the results of the tools that the call before it ran, so that the model sees what its own edits did, and what the user changed meanwhile, before it says that it is done.
They go in a user message that the plugin marks as the app's, and the template says that the app writes it, so that the model does not take the board for the user's words.
A system message would speak for the app, but pi sends one after the first only to the models that its catalogue marks, such as Claude Opus 5.5, and folds it into the system prompt at the start for every other model, which breaks the cache as today's prompt does (notes).
The checks of pi in the notes of [Assistant as a plugin](Rewrite-1.4) added the board after the last message on Anthropic's Messages API and on OpenAI's Responses API, and how the Chat Completions API takes it is for the issue that runs the loop to settle.

A provider's prompt cache serves the start of a call that matches an earlier one, and charges a fraction of the price of new input for it (notes).
Today's board section sits at the end of the system prompt, so each change to the board or the focus changes the system prompt, and the cache serves none of the thread after it, which is read again in full at the price of new input.
Today's assistant cannot send the board in a message instead, since shinychat's `chat_server()` sends what the user typed alone, and gives an app no way to add context to it ([shinychat#375](https://github.com/posit-dev/shinychat/issues/375)).
In this order, the cache serves the tools, the system prompt and the thread so far, and only the board, the focus and the newest messages are read anew.
Anthropic's cache keeps the start of a call only up to a block that the call marks.
So each call marks the end of the thread, before the board, since a call that marked the board would keep a start that no later call repeats (notes).
[The assistant's benchmark](Rewrite-1.8.1) compares this order with today's, by the questions that pass and by cost, before the issue that writes the template closes.

### What changed under the model

The board stays open to the user while a turn runs, and between turns, so it can change under the model ([The assistant's chat](Rewrite-1.4.4#while-a-turn-runs)).
The board after the last message shows the board as it is, but neither what changed nor who changed it.
So a model that said it added a block `adults` would later read a board without `adults`, and nothing to tell it why, which is what shinychat#375 describes for a context that a message does not keep.

To tell the model, the plugin follows the store, and records each change to the board's blocks, links and stacks that the thread's own edits did not make, with who made it: the user, the user through the chat's Undo or Redo, or another plugin, by its name ([Board updates](Rewrite-1.1.2#the-store)).
Before each call, the plugin adds a note of the changes since the thread's previous call to the thread, as a message of its own, which it marks as the app's rather than the user's ([The assistant's state](Rewrite-1.4.3#the-state)).
So the thread keeps the note, as shinychat#375 asks of a message's context, and a call with no such changes carries none.
The note comes before the board, which the call adds after the thread's last message, so that the cache serves the thread up to the note on the calls after.
The board itself stays out of the thread, since a board for every call would fill the model's context window.
The note stays within `assistant_board_section_max_chars`, as each part of the Board section does.
The plugin records the changes while the page lives, so the first call after a reload carries no note of what changed before it.

What the note holds and how much, so that the model stays in step without reading updates that it does not need, is a decision that [The assistant's benchmark](Rewrite-1.8.1#the-decisions-it-compares) compares, version against version.

### The rules

The template keeps the rules that carry over (Today), and states those of the new tools:

- The model reads what an edit relies on rather than guessing at it, since a result's summary, the state that `describe_block` reports and a class's description are bounded, and the Board section shows no plugin's state in full: through `get_block_result`, `inspect_results`, `get_block_state`, `get_plugin_state`, `describe_block_type` or `describe_command` ([The assistant's tools](Rewrite-1.4.2#the-tools)).
- One edit is one list of commands, which applies all or none, in the order given: a block before its links, with an id that the model gives it, so that later commands of the list name it ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).
  An edit is one undo step, unless every command of it has `undo: false`, as the dock's command that switches views has, or it sets only board options ([Board updates](Rewrite-1.1.2#undo)).
  An edit holds one change that the user would take back as one, so that the chat's Undo takes back what the user expects ([The assistant's chat](Rewrite-1.4.4#undoing-the-assistants-edits)).
- An edit returns a review of the blocks that it changed, of the blocks that feed them directly and of every block downstream: each block's status, the conditions that appeared since the edit began, what `describe_result()` writes about its result, and the state of each block that it added ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).
  The model checks the review against what the user asked, and corrects with another edit, rather than reporting as done a change that left a block `failed`, `invalid` or `waiting`.
  Where the review leaves out the blocks past `assistant_review_max_blocks`, the model says that it has not checked them, rather than reporting the change as verified.
- A refused edit names the command and why, so the model changes the args or the commands rather than sending the same list again.
- The commands come from `list_commands`, so the model looks up the frontend's own for views and panels, as the dock's are, and a plugin's own or `blockr.core-set_plugin_state` for that plugin's state, rather than assuming any.
- The tool `undo_edit` takes back the assistant's last undo step, for when the user asks for that in words ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).
  That step may be an edit of another thread, and `undo_edit` passes over an edit that took no undo step, such as one that only switched views.
  So the model tells the user what `undo_edit` took back, as its result says, rather than taking for granted that it was the model's own last edit.
- On a locked board, the model tells the user what the lock refuses, as the edit tool returns it, rather than trying another way ([The assistant's tools](Rewrite-1.4.2#on-a-locked-board)).
- A note of what the user changed says what the user wants, so the model builds on it, rather than putting back what the user removed or took back, unless the user asks for that (What changed under the model).

How to arrange the dock's views stays out of the template, which the calls under every frontend send, and comes from the dock's `layout` skill (What a package adds).

### The sections

The plugin writes three sections from what `CoreApi` gives, in place of the generics `describe_board()` and `describe_block()` in R ([Assistant as a plugin](Rewrite-1.4#today)):

| Section | What it holds | Where it goes, within which cap |
|---|---|---|
| Skills | The name and description of each skill that the model may read and that no block class or plugin scopes, from the reply to `list_skills`, under today's preamble, changed as Today has it | The system prompt, each description cut at `assistant_skill_description_max_chars`, 1024, while the catalogue is not cut, and R logs a warning where it passes `assistant_skill_catalogue_max_chars`, 4000, as today |
| Board | Today's parts: a line of counts, the blocks, each with its id, its class, the names of its state args, its status and the counts of its conditions, the links, the stacks, the board options, the app's plugins, and, where the dock is the frontend and has more than one view, its views with the panels of each, from `store.board()`, `scheduler.status()`, `options.inUse()` and `plugins.appPlugins()` | After the last message, each part within `assistant_board_section_max_chars`, 1500 |
| Focus | The block that has focus in `CoreApi.focus`, and, where the dock is the frontend, the active view and the panels that show in it, which are the panel that each of its tab groups shows and that of each rail that is not collapsed ([The dock's state](Rewrite-1.2.1#grids)), under its preamble | After the last message, after the board |

Each section keeps today's headings, lines and markers, with the client's names in place of R's, such as a class's registry id in place of its S3 class, and with these changes:

- The status `invalid` in place of `unset` ([Evaluation in the client](Rewrite-1.1.10#statuses)).
- No `*` on args, and no list of what an extension lets others control, since every block's state and every plugin's state is open to external control on a board that is not locked ([Board updates](Rewrite-1.1.2#commands)).
- The app's plugins in place of the extensions, each by its class's id and name, with the description that the schema of its state gives ([Plugins](Rewrite-1.1.12#which-plugins-a-board-has)).
- The new tools and commands in place of those that today's lines name, such as `get_plugin_state` in place of `list_views`, and core's command `blockr.core-set_option` in place of the tool `set_board_option` ([The assistant's tools](Rewrite-1.4.2#today)).

So what the model reads of the board changes no more than the new tools ask, and the first comparison with today's baseline turns on the tools, the rules, the order and the note of what changed ([The assistant's benchmark](Rewrite-1.8.1#todays-assistant-as-the-baseline)).

### What a package adds

A package that registers block classes or plugin classes may give the model guidance on them, as skills of its own.
Each skill is a directory under `inst/skills` in the package's source, with a `SKILL.md` that has YAML frontmatter, in the form that a deployment's skills and blockr.assistant's own take today.
So a package gives its skills as files, with no code of the assistant's and no dependency on blockr.assistant (condition 8).

R lists the skills in its reply to the request `list_skills` ([The assistant's tools](Rewrite-1.4.2#the-requests-in-r)), in this order:

1. The skills of each package whose block classes the app offers or whose plugin classes it runs, in the order of the packages' names.
2. The skills of the directory that the blockr option `assistant_skills` names.

A skill shadows one of the same name that R listed before it, as today, so a deployment's skill takes the place of a package's (notes).
A skill that names no class in `blocks:` or `plugins:` goes into the catalogue of the system prompt.
A skill that names classes is listed where the model reads those classes ([The assistant's tools](Rewrite-1.4.2#the-tools)).
Either way, the model sees a package's skills only in an app that offers the package's block classes or runs its plugin classes.

A package teaches the model in two other ways, which [The assistant's tools](Rewrite-1.4.2) gives:

- The description and args of each command that the package registers ([The edit tool](Rewrite-1.4.2#the-edit-tool)).
- A method of `describe_result()` for a class of results ([The requests in R](Rewrite-1.4.2#the-requests-in-r)).

The dock gives its guidance on arranging views as the skill `layout` of blockr.dock, in place of blockr.assistant's skill of that name.
The dock knows its views and grids best, and today's skill teaches the view tools, which the dock's commands replace ([Assistant as a plugin](Rewrite-1.4#today)).
The new skill teaches the dock's commands and its grids ([The dock's state](Rewrite-1.2.1#grids)).
It keeps the parts of today's skill that fit them, such as how a grid nests splits and tab groups, what a share and a rail's width mean, and worked examples.
It drops the parts that teach today's view tools, such as probing a layout with `validate_layout`, since each of the dock's commands checks its args.
It names no class in `plugins:`, so the catalogue lists it in every app that runs the dock.
The model then learns of it before it arranges a view, as it learns of today's `layout`.
The skill is the first form to try.
Whether the model does better with it, or with the same guidance in the descriptions of the dock's commands, is for the benchmark to show.
The benchmark compares the two as versions of blockr.dock ([The assistant's benchmark](Rewrite-1.8.1#the-decisions-it-compares)).

### What a deployment adds

A deployment adds instructions of its own as skills, through the blockr option `assistant_skills`, as the script of the clinical data explorer adds eight, two of them scoped to block classes.
A skill's description in the catalogue tells the model when to read it, as the explorer's test questions expect the first call to read its skill on working with an existing study board ([The assistant's benchmark](Rewrite-1.8.1#today)).
A deployment's skill takes the place of a package's skill of the same name (What a package adds).
No app script replaces the template, since the `system_prompt` argument goes ([Assistant as a plugin](Rewrite-1.4#today)).

### One template for every model

The template is the same for every provider and model that [Model access](Rewrite-1.4.1) reaches.
Whether a model does better with words of its own is for the benchmark to show, and a template chosen by the model's id stays possible, which nothing here rules out.

### How the template changes

The template, the preambles and the code that writes the sections live in blockr.assistant, in the plugin's bundle, and change with its releases.
A pull request that changes any of them, or a tool's description, shows the benchmark's comparison of the change with the version before it (condition 6).
So does a pull request of another package that changes what the model reads, such as one of core that changes a command's description, or one of blockr.dock that changes its `layout` skill, since the model reads those as it reads the template ([The assistant's benchmark](Rewrite-1.8.1#where-it-lives)).
A Vitest snapshot of the prompt takes the place of today's golden copy ([tests/testthat/_snaps/system-prompt.md](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/tests/testthat/_snaps/system-prompt.md)), since it catches a change that nobody meant, while only the benchmark says whether a change that someone meant helps.

## Open questions

None.

<details><summary>Notes for implementers</summary>

Read on 2026-11-13:

- Anthropic: "Prompt caching covers the full prefix: `tools`, `system`, and `messages` (in that order)", and "Changes at each level invalidate that level and all subsequent levels", while a cache lives five minutes by default and a read costs 0.1 times the price of new input, 0.05 times on Claude Opus 5.5 and Claude Sonnet 5.5 ([Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)).
  "Cache writes occur only at your breakpoint", and a read walks back from a breakpoint over at most 20 positions, "looking for prior writes, not for stable content", where a run of `tool_result` blocks counts as one position (same page).
- OpenAI: "Prompt caching is enabled by default for supported OpenAI models", "Cache reuse requires the entire rendered prefix to match", and the guide advises "Put stable developer instructions and shared reference material first", with what changes "at the end rather than the beginning" ([Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)).

Read on 2026-11-13 in pi at [`e3da248`](https://github.com/earendil-works/pi/tree/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e): for Anthropic's cache, pi marks the system prompt, the last tool and the last block of the last message ([anthropic-messages.ts#L1236-L1243](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/src/api/anthropic-messages.ts#L1236-L1243), [#L1526-L1552](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/src/api/anthropic-messages.ts#L1526-L1552), [#L1655](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/src/api/anthropic-messages.ts#L1655)).
With the board after the last message, that last mark falls on the board.
The plugin moves it to the block before the board through pi's `onPayload`, whose return replaces the request's params ([#L656-L659](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/src/api/anthropic-messages.ts#L656-L659)).
A system message after the first goes in place only to the models whose `supportsMidConvoSystemMessages` pi's catalogue sets, such as Claude Opus 5.5, Sonnet 5.5 and Haiku 5.5 ([families/anthropic.ts#L28-L34](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/catalog/families/anthropic.ts#L28-L34)), while "Every other model receives `collapseSystemMessages(transcript)`: the replayed prompt and current tools as the leading system message, with later system messages dropped" ([README](https://github.com/earendil-works/pi/blob/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/ai/README.md?plain=1#L1651)).

The commits that shaped today's template hold the lessons behind its rules, such as "Warn that an off-screen block's conditions are a snapshot" ([16a97d3](https://github.com/BristolMyersSquibb/blockr.assistant/commit/16a97d3)), which carries over with the statuses, and "State commit/discard as a hard end-of-turn rule to the model" ([669444b](https://github.com/BristolMyersSquibb/blockr.assistant/commit/669444b)), which goes with staging, so the issue that writes the template reads each with `git log -p -- inst/prompts/system-prompt.md`.

The preambles of the skills' catalogue and of the focus section are R code today, `skill_catalogue_preamble()` and `screen_preamble()`, and become text in the plugin's bundle beside the template, while `focus_preamble()`, on the blocks added with @, goes.

Today, `skill_sources()` lists the directory `skills` that blockr.assistant installs, then the directory that `assistant_skills` names ([R/skills-scan.R#L21-L45](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-scan.R#L21-L45)).
Then `scan_skills()` lets a skill shadow one of the same name listed before it, and logs that it does ([#L54-L68](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-scan.R#L54-L68)).
R finds a package's directory with `system.file("skills", package = pkg)`, as it finds blockr.assistant's own.

</details>
