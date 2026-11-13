# The assistant's benchmark: questions, answer keys and runs
Status: draft. Design for [Benchmarks of the new stack](Rewrite-1.8).

One of the design pages of the benchmarks ([Benchmarks of the new stack](Rewrite-1.8)): how the decisions that shape what the assistant's model sees and does are judged, from its system prompt to its tools, what they return and how failures reach it, by how well the assistant then does what users ask, through questions with answer keys that a harness runs.
It shapes the Work items of that part that build the benchmark and take its baseline, and those of [Assistant as a plugin](Rewrite-1.4#work) whose changes merge by its comparisons, such as the one that writes the template ([The system prompt](Rewrite-1.4.5#what-must-hold)).
Each decision is designed on the page that The decisions it compares names, and how fast the new stack runs is the part's.

## What must hold

1. A change to what the model sees or may do, from what it is told to its tools, what they return, how failures reach it, compaction and the model itself, merges only with a comparison against the version before it, on every question of the benchmark, with the same models.
2. Each question's answer key judges a run without a person, by the values that the data gives, the board that the turn leaves, the page that it draws and the tools that it calls.
3. A run starts each question from its own board and an empty thread, as CEDX's reload does, and names the model, its settings and the version of blockr.assistant that it runs.
4. Each question runs several times, since the misses "vary run to run", and a comparison reports each question's share of runs that pass, with the tokens, calls and seconds of the runs.
5. A turn stops at a cap on its calls, which fails the run, so that what a run costs is bounded.
6. The questions exercise each decision that the benchmark compares, since a question that a decision cannot change says nothing of it, starting from CEDX's five with their answer keys.

## Today

Today five clinical questions check the assistant, each against an answer key computed from the data, which someone runs by hand on the CEDX board.
They paste a question into the chat, read the reply against its key, and reload the page before the next question, since without a reload "question 3 builds on question 2's blocks" ([dev/cedx/assistant-intent/README.md#L76-L78](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/0e3e074647a257c1e828e49b92c81ea9d4669570/dev/cedx/assistant-intent/README.md#L76-L78)).
Each question asks for a different thing, "a table, a number, a view, an explanation of a number, a package of panels", some with a follow-up, and a script at the end of the file computes the keys from the data ([questions.md#L8-L13](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/0e3e074647a257c1e828e49b92c81ea9d4669570/dev/cedx/assistant-intent/questions.md#L8-L13)).

Whoever runs them checks four things on each question ([README.md#L80-L93](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/0e3e074647a257c1e828e49b92c81ea9d4669570/dev/cedx/assistant-intent/README.md#L80-L93)):

- That "The first tool call is `read_skill("clinical-existing-board")`".
- That the reply names `TRT` as the arm column, while `ARM` and `ACTARM` give other denominators.
- That the view the assistant built shows something, since "A block can evaluate cleanly and render nothing, and the tool log does not show it".
- The numbers, against the answer key.

"Runs are exact more often than not, and the misses vary run to run", a question costs "roughly $0.30", and one run "made 35 sequential `query_data` calls hunting a column that does not exist" ([#L90-L96](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/0e3e074647a257c1e828e49b92c81ea9d4669570/dev/cedx/assistant-intent/README.md#L90-L96)).

The tests of blockr.assistant chat with a fake model ([tests/testthat/helper-llm.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/tests/testthat/helper-llm.R)) and compare the prompt's text with a golden copy ([tests/testthat/_snaps/system-prompt.md](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/tests/testthat/_snaps/system-prompt.md)).
So they check what the prompt says, and nothing checks what a model does with it.

## Proposal

### The decisions it compares

The benchmark compares two versions of any decision that shapes what the model sees or does:

| Decision | Where it is designed | The questions that exercise it |
|---|---|---|
| What the model is told: the template and its rules, the sections that the plugin writes, and their order | [The system prompt](Rewrite-1.4.5) | Every question |
| The tools: how many, how they are cut, their names, descriptions and args, such as one edit tool over every command against a tool per command, or fewer read tools than today's | [The assistant's tools](Rewrite-1.4.2#the-tools) | Every question |
| What the tools return: the summaries of results and states within their caps, the review of an edit with each block's status, conditions and summary, and plots as images | [The assistant's tools](Rewrite-1.4.2#the-edit-tool) | Those that read results or check an edit |
| How failures reach the model: the failures that a refused edit names, a block that reads `failed`, `invalid` or `waiting` with its conditions, a request that core rejects or R loses, an error in the model's own R code, and what a lock refuses | [The assistant's tools](Rewrite-1.4.2#how-failures-reach-the-model) | Those whose turns fail on the way |
| Compaction: when it runs and what its summary keeps | [The assistant's state](Rewrite-1.4.3#compaction) | Those long enough to compact |
| The model and its settings, and the library that runs the loop | [Model access](Rewrite-1.4.1), [Assistant as a plugin](Rewrite-1.4#proposal) | Every question |

A version is a ref of blockr.assistant, so that the harness compares a pull request's head with its base, or two branches that try one decision two ways, as whether fewer tools serve the model better ([The assistant's tools](Rewrite-1.4.2#the-tools)).
A comparison names the decision that it tests.

### A question

A question is a board to start from, what the user writes, with any follow-ups, and its answer key, here CEDX's first, in an illustrative shape:

```json
{
  "id": "demographics-by-arm",
  "board": "cedx.json",
  "turns": [
    "Build the demographics and baseline characteristics table, by arm.",
    "Same table, but add an Overall column and split it by sex as well."
  ],
  "key": {
    "tools": ["read_skill:clinical-existing-board", "read_skill:composer-tables"],
    "board": "one_table_by_arm_and_sex",
    "page": "views_show_outputs",
    "values": "demographics_counts"
  }
}
```

The board is a JSON board, which the harness opens as the page starts ([Serialization](Rewrite-1.1.4#files)).
Beside CEDX's five, the questions include turns that meet what each decision governs: a column that the data lacks, as the CEDX run that made 35 calls hunted, an edit that a command refuses, a block that fails or reads `invalid` once edited, an error in the model's own R code, a locked board, and a thread long enough to compact.
An answer key holds four kinds of check, each a function in the benchmark's code but for the tools, which it names:

- **The values** that the data gives, computed by the benchmark's code as CEDX's script computes its keys, which the reply or a named block's result must hold, such as the counts by arm.
- **The board** that the turn leaves, such as one table that the follow-up edits rather than a second beside it, as CEDX's first question asks.
- **The page** that the turn leaves, such as each view that it built showing its outputs, since a block can evaluate cleanly and draw nothing.
- **The tools** that the turn calls, in the order given, such as the skill that it reads first.

What no function can check, such as whether a reply explains a number well, a model may judge, which a comparison reports apart from the rest and never lets decide alone.

### A run

The harness serves the question's board with `serve()`, with the app's packages, its skills and a key of its own, as a deployment does ([Model access](Rewrite-1.4.1#the-blockr-options)), and drives the page in a headless browser:

1. It opens the page, and waits until the board is drawn.
2. It types each turn into the chat's composer, as a user does, and waits until the turn ends ([The assistant's chat](Rewrite-1.4.4#the-composer-and-a-turn)).
3. It applies the checks on the page, then saves the board, as a user does, and reads the JSON board, whose assistant's state holds the thread with its tool calls and its `usage` ([The assistant's state](Rewrite-1.4.3#the-state)).
4. It applies the checks on the values, the board and the tools.

The harness sets `chat_save_turns` to `Inf`, so that the saved thread holds every message of the run ([The assistant's state](Rewrite-1.4.3#how-much-of-a-thread-the-state-keeps)).
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

### When it runs

The benchmark runs on demand, and on each pull request that changes what the model sees or may do (What must hold 1), with a key that the repo holds as a secret.
It never runs on every pull request, since at CEDX's cost of about $0.30 a question, five questions run five times on two versions and two models cost about $30.

### Today's assistant as the baseline

Today's assistant answers the same questions by hand, as CEDX's README has them run, as many times as the harness runs each, with today's model.
So the new assistant's first comparison has a baseline for What must hold 5 of [Assistant as a plugin](Rewrite-1.4#what-must-hold), what today's assistant offers carrying over.
The harness drives only the new assistant, since today's chat is shinychat's and its board is R's, which the harness does not read.

## Open questions

- Which repo holds the questions, their answer keys and the harness: blockr.assistant, beside the template whose changes run them, or blockr.sandbox, beside the CEDX board, whose packages its first questions need.
  It blocks the Work item that builds the benchmark, and the part's question of which repo the benchmarks live in settles it ([Benchmarks of the new stack](Rewrite-1.8#open-questions)).
- Which questions run before the packages of the CEDX board have moved to the new stack: questions in CEDX's manner on boards of the packages that have.
  It blocks the benchmark's first runs, and the order in which the block packages move settles it ([State in JS](Rewrite-1#parts)).

<details><summary>Notes for implementers</summary>

Today's five questions build a table, answer with a number, build a view, challenge a number and assemble a package of panels, with a sixth offered, and the keys were "recomputed off `cedx_demo_dm()` on 2026-09-05" ([questions.md](https://github.com/BristolMyersSquibb/blockr.sandbox/blob/0e3e074647a257c1e828e49b92c81ea9d4669570/dev/cedx/assistant-intent/questions.md)).
The traps that its questions name, such as the arm column `TRT` against `ARM`, `Screen Failure` as a level of `TRT`, and `TRTEMFL` being logical rather than `"Y"`, are what the checks on values guard against, since each "has produced a wrong number in a run" (same file).

The page check reads the views' outputs from the page, which is what CEDX's third check reads by eye, while the board check reads the saved JSON board.

</details>
