# The assistant's benchmark: questions, answer keys and runs
Status: review. Design for [Benchmarks of the new stack](Rewrite-1.8).

One of the design pages of the benchmarks ([Benchmarks of the new stack](Rewrite-1.8)): how the decisions that shape what the assistant's model sees and does are judged, from its system prompt to its tools, what they return and how failures reach it, by how well the assistant then does what users ask, through questions with answer keys that a harness runs.
It shapes the Work items of that part that build the benchmark and take its baseline, and those of [Assistant as a plugin](Rewrite-1.4#work) whose changes merge by its comparisons, such as the one that writes the template ([The system prompt](Rewrite-1.4.5#what-must-hold)).
Each decision is designed on the page that The decisions it compares names, and how fast the new stack runs is the part's.

## What must hold

1. After `js-state` has merged into main ([State in JS](Rewrite-1#migration)), a change to what the model sees or may do, from what it is told to its tools, what they return, how failures reach it, compaction and the model's settings, merges only with a comparison against the version before it, on every question of the benchmark, with the same models.
2. Each question's answer key judges a run without a person, by the values that the data gives, the board that the turn leaves, the page that it draws and the tools that it calls.
3. A run starts each question from its own board and an empty thread, as a reload does in today's checks by hand, and names the model, its settings and the ref of each package that it runs.
4. Each question runs several times, since the misses vary from run to run, and a comparison reports each question's share of runs that pass, with the tokens, calls and seconds of the runs.
5. A turn stops at a cap on its calls, which fails the run, so that what a run costs is bounded.
6. The questions exercise each decision that the benchmark compares, since a question that a decision cannot change says nothing of it, starting from the clinical data explorer's five, with their answer keys.

## Today

Today five questions check the assistant, which someone asks by hand of the clinical data explorer, an app for exploring the data of clinical studies, on a board that runs on the public pharmaverseadam data in development.
Each asks for a different thing, a table, a number, a view, the explanation of a number or a set of panels, such as a table of demographics by treatment arm, and some come with a follow-up.
Each has an answer key, which a script computes from the data, so that a good answer can be told from a plausible one.

Whoever runs them reloads the page before each question, so that no question builds on the blocks of the one before, and checks four things:

- That the assistant first reads the skill that tells it how to work with an existing study board.
- That it counts subjects by the right treatment arm, since a subject-level table holds several, such as the planned and the actual arm, which give different denominators.
- That the view it built shows its outputs, since a block can evaluate cleanly and draw nothing, which no tool call shows.
- The numbers, against the answer key.

Runs are exact more often than not, the misses vary from run to run, and a question costs about $0.30, more where the data cannot answer it, as when one run called its tool for R code 35 times in a row, looking for a column that the data lacks.
The questions and their keys live in blockr.sandbox.

The tests of blockr.assistant chat with a fake model ([tests/testthat/helper-llm.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/tests/testthat/helper-llm.R)) and compare the prompt's text with a golden copy ([tests/testthat/_snaps/system-prompt.md](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/tests/testthat/_snaps/system-prompt.md)).
So they check what the prompt says, and nothing checks what a model does with it.

## Proposal

### The decisions it compares

The benchmark compares two versions of any decision that shapes what the model sees or does:

| Decision | Where it is designed | The questions that exercise it |
|---|---|---|
| What the model is told: the template and its rules, the sections that the plugin writes, and their order | [The system prompt](Rewrite-1.4.5) | Every question |
| The guidance that a package gives on its classes: a skill, such as the dock's `layout` on arranging views, against the same guidance in the descriptions of the package's commands | [The system prompt](Rewrite-1.4.5#what-a-package-adds) | Those that build a view or assemble a set of panels |
| The tools: how many, how they are cut, their names, descriptions and args, such as one edit tool over every command against a tool per command or against tools for each block class, as today's `add_<type>` and `modify_<type>` are, or fewer read tools than today's | [The assistant's tools](Rewrite-1.4.2#the-tools) | Every question |
| What the tools return: the summaries of results and states within their caps, the review of an edit with each block's status, conditions and summary, and plots as images | [The assistant's tools](Rewrite-1.4.2#the-edit-tool) | Those that read results or check an edit |
| How failures reach the model: the failures that a refused edit names, a block that reads `failed`, `invalid` or `waiting` with its conditions, a request that core rejects or R loses, an error in the model's own R code, and what a lock refuses | [The assistant's tools](Rewrite-1.4.2#how-failures-reach-the-model) | Those whose turns fail on the way |
| What the model learns of what others change in the board: what the note of the changes holds, and how much | [The system prompt](Rewrite-1.4.5#what-changed-under-the-model) | Those whose board the user changes between two turns or during one |
| Compaction: when it runs and what its summary keeps | [The assistant's state](Rewrite-1.4.3#compaction) | Those long enough to compact |
| The model's settings, and the library that runs the loop | [Model access](Rewrite-1.4.1#the-models-settings), [Assistant as a plugin](Rewrite-1.4#proposal) | Every question |

A version is a ref of each package that the comparison changes, with every other package at one ref for both versions.
Besides blockr.assistant, whose tools and template the model reads, any package can change what the model reads: core or a plugin's package through the descriptions of its commands, a package of block classes through their guidance and arg specs, and any of them through its skills, as the dock's `layout` skill does.
So the harness compares a pull request's head with its base, whichever of these packages the pull request changes, or two branches that try one decision two ways, as whether fewer tools serve the model better ([The assistant's tools](Rewrite-1.4.2#the-tools)).
A comparison names the decision that it tests.

### A question

A question is a board to start from, what the user writes, with any follow-ups, and its answer key, here the first of today's, in an illustrative shape:

```json
{
  "id": "demographics-by-arm",
  "board": "study-board.json",
  "turns": [
    "Build the demographics and baseline characteristics table, by arm.",
    "Same table, but add an Overall column and split it by sex as well."
  ],
  "key": {
    "tools": ["read_skill:study-board", "read_skill:summary-tables"],
    "board": "one_table_by_arm_and_sex",
    "page": "views_show_outputs",
    "values": "demographics_counts"
  }
}
```

The board is a JSON board, which the harness opens as the page starts ([Serialization](Rewrite-1.1.4#files)).
A question may also hold edits that the harness makes as the user would, between two turns or while a turn runs, so that the board changes under the model ([The system prompt](Rewrite-1.4.5#what-changed-under-the-model)).
Beside today's five, the questions include turns that meet what each decision governs: a column that the data lacks, which one of today's runs looked for in 35 calls of its tool for R code, an edit that a command refuses, a block that fails or reads `invalid` once edited, an error in the model's own R code, a locked board, a board that the user changes during a turn, and a thread long enough to compact.
An answer key holds four kinds of check, each a function in the benchmark's code but for the tools, which it names:

- **The values** that the data gives, computed by the benchmark's code as today's script computes the keys, which the reply or a named block's result must hold, such as the counts by arm.
- **The board** that the turn leaves, such as one table that the follow-up edits rather than a second beside it, as today's first question asks.
- **The page** that the turn leaves, such as each view that it built showing its outputs, since a block can evaluate cleanly and draw nothing.
- **The tools** that the turn calls, in the order given, such as the skill that it reads first.

What no function can check, such as whether a reply explains a number well, a model may judge, which a comparison reports apart from the rest and never lets decide alone.

### A run

The harness serves the question's board with `serve()`, with the app's packages, its skills and a key of its own, as a deployment does ([Model access](Rewrite-1.4.1#the-blockr-options)), and drives the page in a headless browser:

1. It opens the page, and waits until the board is drawn.
2. It follows the board through `core.store.subscribe()`, as any follower of the board does ([Board updates](Rewrite-1.1.2#following-the-board)), and records each message as it enters the thread.
   It records them as they come, since compaction replaces a thread's older messages with a summary, in the saved thread and in what the chat shows alike ([The assistant's state](Rewrite-1.4.3#compaction)).
3. It types each turn into the chat's message field, as a user does, and waits until the turn ends ([The assistant's chat](Rewrite-1.4.4#the-message-field-and-a-turn)).
4. It applies the checks on the page, then saves the board, as a user does, and reads the JSON board, whose assistant's state holds the thread's `usage` ([The assistant's state](Rewrite-1.4.3#the-state)).
5. It applies the checks on the values, the board and the tools, and reads the replies and the tool calls from the messages that it recorded rather than from the saved thread.

The harness makes a question's edits through `core.commands.run()` with the origin `user`, as the frontend makes the user's, at the point that the question names, such as after the turn's first edit.
A turn that passes the cap on its calls is stopped, as the chat's stop button stops it, and the run fails.
The cap is the question's, and the first runs set its default from how many calls a passing run takes.
Each run starts from a new page and the question's board, so that no run sees another's blocks or thread.

### What a comparison reports

A comparison runs each question the same number of times, five unless the question asks for more, on each of the two versions and each model, and reports, for each question and model, with illustrative numbers:

| Version | Runs that pass | Tokens in, of them cached | Tokens out | Calls | Seconds |
|---|---|---|---|---|---|
| Before the change | 4 of 5 | 182,000, 140,000 | 6,100 | 9 | 74 |
| After the change | 5 of 5 | 121,000, 104,000 | 5,800 | 7 | 61 |

The tokens, calls and seconds are medians over the runs, beside their spread.
A change passes where no question passes fewer runs than before, beyond what the spread of its runs allows, and where its tokens do not rise without a question passing more.
The first comparisons, once they show how much runs vary, set the numbers that decide, and the pull request that sets them names them.

The models are OpenAI's and Anthropic's, whose APIs the plugin speaks ([Model access](Rewrite-1.4.1#the-blockr-options)), and any model that a change is meant for.

### Where it lives

The questions, their answer keys and the harness live in blockr.bench, a repo of their own, as the part's other benchmarks do ([Benchmarks of the new stack](Rewrite-1.8#proposal)).
Neither blockr.assistant nor blockr.sandbox holds them, so that neither depends on the other for the benchmark.
A run installs each package at the ref that its comparison names, with the packages of each question's board, such as blockr.sandbox's for the clinical data explorer's, and blockr.bench holds the providers' keys as its secrets.
After `js-state` has merged into main, a pull request of blockr.assistant that changes what the model sees or may do starts a run in blockr.bench, which shows its comparison on that pull request (What must hold 1).
So does a pull request of another package that changes what the model reads, such as one of core that changes a command's description, or one of blockr.dock that changes its `layout` skill ([The system prompt](Rewrite-1.4.5#what-a-package-adds)).

### When it runs

The benchmark runs on demand, with the keys that blockr.bench holds, and after `js-state` has merged into main, on each pull request that changes what the model sees or may do (What must hold 1).
Until then, a comparison informs a decision on `js-state`, such as one on the template or the tools, but holds up no merge and no issue, so that the benchmark does not slow the new stack while it is built.
It never runs on every pull request, since at today's cost of about $0.30 a question, five questions run five times on two versions and two models cost about $30.

### Today's assistant as the baseline

Today's assistant answers the same questions by hand, as they are run today, as many times as the harness runs each, with today's model.
So the new assistant's first comparison has a baseline for What must hold 5 of [Assistant as a plugin](Rewrite-1.4#what-must-hold), what today's assistant offers carrying over.
The harness drives only the new assistant, since today's chat is shinychat's and its board is R's, which the harness does not read.

## Open questions

- Which questions run before the packages of the clinical data explorer's board have moved to the new stack: questions of the same kind on boards of the packages that have.
  It blocks the benchmark's first runs, and the order in which the block packages move settles it ([State in JS](Rewrite-1#parts)).

<details><summary>Notes for implementers</summary>

Today's five questions build a table, answer with a number, build a view, challenge a number and assemble a set of panels, and their answer keys are computed from the public pharmaverseadam data.
They name the traps of the data, such as counting by the wrong treatment arm, or keeping screen failures, subjects who never started treatment, among the treated, each of which has produced a wrong number in a run.

The page check reads the views' outputs from the page, which is what today's third check reads by eye, while the board check reads the saved JSON board.

</details>
