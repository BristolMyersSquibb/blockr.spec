# The assistant's state: threads and compaction
Status: review. Design for [Assistant as a plugin](Rewrite-1.4).

One of the design pages of the assistant ([Assistant as a plugin](Rewrite-1.4)): the assistant's plugin state, which holds its threads and each thread's pick of the model, how much of a thread it keeps, the commands that change it, compaction, and how a board saved today opens.
It shapes the Work items of [Assistant as a plugin](Rewrite-1.4#work) that register the assistant's plugin class and port compaction, and the one of [The conversion and the migration notes](Rewrite-1.9#work) that writes blockr.convert's method for the assistant.
What the tools' calls and results in a thread hold is [The assistant's tools](Rewrite-1.4.2)'s, and who picks the model is [Model access](Rewrite-1.4.1#who-picks-the-model)'s.

## What must hold

1. A board's threads are the assistant's plugin state, which a JSON board saves with the rest of the board, and which its class's `migrate` brings to the class's latest shape ([Plugins](Rewrite-1.1.12#a-plugins-state)).
2. No undo takes back a change that the assistant makes to its state, such as a message, and no such change takes an undo step.
3. A reply enters its thread as one finished message, never token by token.
4. A thread goes on once its board is saved and opened again, from the messages that a saved board keeps, which the deployment bounds as today.
5. Boards saved with today's assistant open, with none of their threads, as condition 6 of [Assistant as a plugin](Rewrite-1.4#what-must-hold) asks.

## Today

Today's threads live in R's memory, in a thread store on shinychat's `ConversationStore`, one for each board, with no cap on how many it holds ([R/ext-history.R#L1-L61](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-history.R#L1-L61)).
A thread is shinychat's record: a title, timestamps, a tree of nodes, each holding its turns as `ellmer::contents_record()` writes them and shinychat's messages, and `current_leaf`, the node whose branch shows ([R/ext-history.R#L102-L142](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-history.R#L102-L142)).
The assistant adds `focus`, the blocks that the user added with @, and `spent`, the tokens of the thread so far, to the record's `values` ([R/ext-server.R#L626-L643](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L626-L643)).
The browser keeps which thread is open, since shinychat's default "stores the active conversation ID in `localStorage` so it survives page reloads" ([chat_history.R#L670-L672](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/pkg-r/R/chat_history.R#L670-L672), [R/ext-server.R#L619-L623](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L619-L623)).
So a board opened in another browser "lists its threads without selecting one" ([R/ext-server.R#L66-L68](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L66-L68)).

The tree has branches.
Since shinychat 0.5.0, its `chat_server()`, through which the assistant chats, lets the user "edit and resend a message after sending it", which "forks the conversation from that point", with "`‹ 1 / 2 ›` controls" to switch between the versions ([NEWS.md#L16-L22](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/pkg-r/NEWS.md#L16-L22)).
The same `chat_server()` lets the user attach images, PDFs and text files, about 30 MB together, which it hands the model as ellmer's content, and the assistant leaves that default as it is.

A saved board keeps the last `chat_save_turns` turns of each thread, 50 by default, with each turn's raw response from the provider emptied ([R/ext-serdes.R#L44-L125](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-serdes.R#L44-L125)).
It keeps them from the branch that shows alone, the nodes on the path to `current_leaf`, and drops every other branch, unless `chat_save_turns` is `Inf` ([R/ext-history.R#L172-L271](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-history.R#L172-L271)).
The turns that it keeps hold their attachments and images whole, the plots of `inspect_results` among them, since those are ellmer's content, which a record writes with its data ([R/utils-plot.R#L60-L65](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/utils-plot.R#L60-L65)).

Compaction replaces a thread's older turns with a summary that a model call writes, once the last turn's tokens pass `chat_compact_tokens`, which is never by default ([R/ext-compact.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-compact.R)).
It stores the summary as an exchange, the request that asked for it as the user's turn and the summary as the model's, so that "role alternation survives whatever the kept window opens with" ([R/ext-compact.R#L336-L347](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-compact.R#L336-L347)).
Then it rebuilds the thread from the turns of the branch that shows, which drops every other branch ([R/ext-history.R#L69-L90](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-history.R#L69-L90)), and redraws the transcript to match ([R/ext-server.R#L111-L114](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L111-L114)).
A summary whose thread changed while the model wrote it is dropped, and turns that arrived meanwhile are kept ([R/ext-server.R#L687-L719](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L687-L719)).

## Proposal

### The state

The board holds the assistant's state under its class's id, `blockr.assistant-assistant_plugin`, in the shape that its class's schema gives, with illustrative names:

```ts
interface AssistantState {
  threads: Record<ThreadId, Thread>;
}

interface Thread {
  title: string;                               // "New thread" until the first exchange names it
  updated: string;                             // ISO 8601, by which the drawer orders the threads
  messages: Message[];                         // in the order in which they entered the thread
  usage: { input: number; output: number; last: number };   // the input and output tokens spent so far, which the chat's meter shows, and every token of the last call, which compaction reads
  model: string | null;                        // the thread's pick of the model, such as "gpt-5.4", or null for the default
}

interface Message {
  id: MessageId;                               // by which compaction and the plugin's memory name it
  role: "user" | "assistant" | "tool" | "summary";
  parts: Part[];
  created: string;                             // ISO 8601, which pi's messages carry as their timestamp
}

type Part =
  | { type: "text"; text: string }
  | { type: "tool_call"; id: string; tool: string; args: Json }
  | { type: "tool_result"; id: string; text: string; error?: boolean; images?: number }   // how many images it carried, which the state leaves out
  | { type: "attachment"; name: string; media_type: string }                              // a file that the user attached, which the state leaves out
  | { type: "changes"; text: string }                                                     // the note of what others changed in the board since the thread's previous call, which the model read and the chat leaves out
  | { type: "skill"; name: string; text: string };                                        // the text of a skill that the user called with /name, which the model gets with the request and the chat leaves out
```

The shape is the plugin's own, and the plugin turns it into pi's messages for each call, and pi's messages back into it.
A state in pi's shape would need a migration whenever pi changed its messages, which a library whose 1.0 came out in October 2026 may do often ([Assistant as a plugin](Rewrite-1.4#proposal)).
A move to the AI SDK, which that page keeps open, would need a migration of every saved board as well.
The issue that runs the loop checks that a thread loses nothing that a call needs on its way into pi's messages and back.
The note of what others changed in the board, which the plugin adds before a call, is a message of the role `user` that holds one part of the type `changes` ([The system prompt](Rewrite-1.4.5#what-changed-under-the-model)).
The plugin marks it as the app's in pi's messages, and the chat leaves it out, so that the thread says what the model was told without showing the note as the user's.

A board saved during a turn holds the turn as far as it got, since each message enters as it finishes, so it may hold a reply whose tool calls have no results yet.
A provider takes a tool call only with its result ([The assistant's tools](Rewrite-1.4.2#how-failures-reach-the-model)), so on its way into pi's messages, a tool call without a result gets one that says the turn ended before the call returned, as a stop writes one ([The assistant's chat](Rewrite-1.4.4#stopping-a-turn)).
The issue that runs the loop checks that each provider takes such a thread, whose last reply goes without its reasoning (Files and images).

A thread's messages are one list, in the order in which they entered the thread.
A sent message never changes, since the chat offers no way to edit one, so a thread has no branches, unlike today's (Today).
Editing a sent message, and the branches that it makes, are later work ([The assistant's chat](Rewrite-1.4.4#today)), which nothing here rules out: a later version of the class could give each message its parent, and its `migrate` would give each message the one before it.

A thread holds no focus, unlike today's (Today), since the plugin tells the model which block has focus and which panels show, as each call goes out ([The system prompt](Rewrite-1.4.5#the-sections)).

Which thread is open stays outside the board: the plugin keeps its id in the browser's local storage, as today's chat does (Today).
A board opens on that thread where it holds it.
Otherwise it opens on no thread, and the chat shows the greeting, as a board opened in another browser does today.

### Files and images

The state keeps the text of every message.
It leaves out the bytes of the files that the user attaches and of the images that a tool result carries, such as the plots of `inspect_results` ([The assistant's tools](Rewrite-1.4.2#the-requests-in-r)), which a board saved today keeps (Today).
In the board, those bytes would reach every follower of the store with the message that holds them, and every saved board, while the model needs them most in the turns that follow them.
So the plugin keeps them in memory, by message, and sends them to the model while the board stays open, which ends with a reload or with the opening of another board ([Plugins](Rewrite-1.1.12#running-a-plugin)).
The state names each file and counts each tool result's images, so that once the board opens again the thread still tells the model that a turn had them, but not what they showed.

Raw responses from the provider stay out of the state, as a saved board leaves them out today.
So does a reply's reasoning, which only the provider reads, and which pi asks back for the next call ([Model access](Rewrite-1.4.1#the-models-settings)): the plugin keeps it in memory, by message, as it keeps the bytes of files.

### How much of a thread the state keeps

The state keeps the last `chat_save_turns` messages of each thread, a blockr option that carries over with its default of 50, `0` for none and `Inf` for every one, since it "governs whether a conversation may land in a shared file, which is the deployment's call" ([R/ext-compact.R#L7-L10](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-compact.R#L7-L10)).
Today it bounds only a save, and after the switch a save writes the state, so it bounds the state itself.
A message counts as one of today's turns does, since a message of the role `tool` holds the results of one reply's calls, as one of ellmer's turns holds them.
A note of what others changed in the board counts as none, since it is none of today's turns, and a call adds at most one, so each thread stays bounded, while how many threads a board holds stays unbounded, as today (Today).
The cut falls between whole exchanges, so that what the state keeps starts on a message that the user sent, as today's trimming for a save has it ([R/ext-history.R#L172-L271](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-history.R#L172-L271)), or on a summary, which counts as one message and as an exchange of its own (Compaction).
As a board opens, the plugin cuts every thread to the cap through `blockr.assistant-trim_threads`, as today's save cuts every thread, so that a board saved under a higher cap keeps no more than this one allows.
With `0`, the plugin runs none of the commands that write a thread, so that the state holds none, as today's save writes none ([R/ext-serdes.R#L70-L74](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-serdes.R#L70-L74)), and as a board opens it moves every thread that the state holds into its memory, through `blockr.assistant-remove_thread`.
The threads then live in its memory alone, with their titles, their usage and their picks of the model, as today's live in R's memory (Today).

The plugin keeps what the cap leaves out of the state in its memory while the board stays open, as it keeps the bytes of files (Files and images), so that the chat shows the whole session and the model gets it, as today's chat does.
Once the board opens again, as after a reload, a thread starts from what the board saved, as a board saved today opens.
What the plugin keeps follows the thread: it goes with a thread that a command removes, and with the messages that a summary replaces (Compaction).

Keeping threads in the browser rather than in the board is later work, as an option by which the user chooses what a board saves and what stays in the browser.
Nothing here rules it out, since a thread that the browser keeps could take the shape that the state gives it.

### Commands

The assistant's class registers a command for each change to its state, which its UI and its loop run, each with `undo: false`, so that no undo takes back a message or a thread's pick of the model, and neither takes an undo step ([Board updates](Rewrite-1.1.2#undo)):

| Command | Args | What it does |
|---|---|---|
| `blockr.assistant-add_thread` | `id`, `title`, `model` | Adds an empty thread under `id`, which the chat mints, since running a command returns nothing ([Board updates](Rewrite-1.1.2#commands)), with `model` as its pick of the model, null where that is left out ([Model access](Rewrite-1.4.1#who-picks-the-model)) |
| `blockr.assistant-rename_thread` | `thread`, `title` | Gives a thread a new title |
| `blockr.assistant-remove_thread` | `thread` | Removes a thread |
| `blockr.assistant-add_message` | `thread`, `message`, `keep` | Adds a finished message at the end of the thread, and drops the oldest messages past `keep`, which the plugin passes from `chat_save_turns` and leaves out for `Inf`, since a command's args are JSON, which holds no infinity (How much of a thread the state keeps) |
| `blockr.assistant-trim_threads` | `keep` | Drops the oldest messages of every thread past `keep`, as `blockr.assistant-add_message` drops them |
| `blockr.assistant-compact_thread` | `thread`, `summary`, `from` | Puts a summary in place of the messages before `from`, the first message that it keeps, and is enabled only where the thread in the state still holds `from` (Compaction) |
| `blockr.assistant-add_usage` | `thread`, `input`, `output`, `total` | Adds a call's input and output tokens to the thread's count, and keeps `total`, every token of the call, cached input included, as its `last` (Compaction) |
| `blockr.assistant-set_model` | `thread`, `model` | Sets the thread's pick of the model, or removes it with `null`, after which the thread talks to the default ([Model access](Rewrite-1.4.1#who-picks-the-model)) |

A command that names a thread is not enabled where the state lacks that thread, and `blockr.assistant-add_thread` and `blockr.assistant-add_message` are not enabled for an id that the state holds already, which keeps the ids unique, as no schema can.
So a turn whose thread another plugin removes meanwhile stops at its next message, which no thread takes.

A reply streams in the plugin's memory and enters its thread as one finished message, through `blockr.assistant-add_message`, since a delta for each token would reach every follower of the store ([Board updates](Rewrite-1.1.2#undo)).
After a thread's first exchange, a model call writes its title, which the plugin gives it through `blockr.assistant-rename_thread` where the title is still "New thread", so that a rename that the user made meanwhile stands.
The commands stay enabled on a locked board, since they change the assistant's own state alone, so that a reader of a locked board still chats, while core's `blockr.core-set_plugin_state` is not enabled there ([Plugins](Rewrite-1.1.12#a-plugins-state)).

### Compaction

The plugin compacts a thread once the tokens of its last call pass a rule of its own, and whenever the user types `/compact` ([Assistant as a plugin](Rewrite-1.4#today)).
The thread keeps those tokens as its `last`, so that the rule can judge a thread as soon as its board opens, as today's compaction reads the counts that a saved thread's turns keep ([R/ext-compact.R#L260-L262](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-compact.R#L260-L262)).
When it runs, and how many of the newest messages it keeps, are for the issue that ports compaction to settle, by the comparisons of [The assistant's benchmark](Rewrite-1.8.1#the-decisions-it-compares).
What it keeps starts on a message that the user sent, as what the state keeps does (How much of a thread the state keeps).
It has a model call with no tools write a summary of the older messages, as today's compaction does ([R/ext-compact.R#L327-L375](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-compact.R#L327-L375)), and `blockr.assistant-compact_thread` puts that summary in place of them, as a message of the role `summary`, which goes before the first message that it keeps.
The plugin sends a summary to the model as an exchange, as today's compaction stores it: the request that asked for it is the user's message, and the summary is the model's reply (Today).
Neither pi nor the AI SDK summarizes a thread itself, so the plugin ports today's compaction (notes).

The command names the first message that it keeps, rather than how many, since the thread may grow while the model writes the summary.
With a count, a turn that added two messages meanwhile would have the command replace two messages that the summary does not cover.
The plugin puts the summary in place of the messages before that message in its memory, under `0` too, and through the command in the state.
The command is not enabled where the state no longer holds that message, as where the cap has cut the thread past it, and the state then keeps the messages that it holds, every one of them newer than what the summary covers.
A summary whose thread goes meanwhile goes with it, as today's compaction drops a summary whose thread changed meanwhile (Today).

### The schema, the default and the version

The package ships the JSON Schema of the state beside the module that it lists for the class, under the module's name, as `assistant_plugin.schema.json` beside `assistant_plugin.js` ([UI modules in JS](Rewrite-1.1.7#packaging)).
The default is `{ "threads": {} }`, and the class is at version 1, with no `migrate` until a version 2 needs one.
The class has no `update`, since nothing in the state names one of core's objects, and a message that names a block keeps its text as it was written ([Plugins](Rewrite-1.1.12#a-plugin)).
The schema gives the shape above, while the commands keep each thread's message ids unique (Commands).
In R, `new_assistant_plugin(threads = list())` gives the state of a board that an app script builds, as every plugin's constructor gives its state ([Plugins](Rewrite-1.1.12#a-plugin)).
A script calls it mostly to place the assistant's panel in a grid of the dock under a name, as `plugins = list(assistant = new_assistant_plugin())` with `plg("assistant")` ([Saved boards and app scripts across the switch](Rewrite-1.2.2#app-scripts)).

### Boards saved today

A board saved with today's assistant opens with none of its threads, since today's assistant has never been in production use, so no one depends on a thread that a board saved.
The conversion makes the assistant's plugin with `new_assistant_plugin()`, and no threads, through blockr.convert's method of `blockr_deser()` for the class `assistant_extension` ([The conversion and the migration notes](Rewrite-1.9#the-methods-of-other-packages)).
It leaves out the threads that the file's `history` holds, and a saved `system_prompt`, since the argument goes ([Assistant as a plugin](Rewrite-1.4#today)).
It leaves out the values of today's board options `llm_model`, `chat_compact_tokens` and `chat_compact_keep` too, since all three go ([Assistant as a plugin](Rewrite-1.4#proposal)), so that the store names none of them as a board opens ([Serialization](Rewrite-1.1.4#board-options)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's trimming for a save, `trim_thread()`, walks back from `current_leaf` and keeps whole nodes while their turns fit `chat_save_turns`, then moves the cut forward to a node that opens on a user's turn that holds no tool result ([R/ext-history.R#L172-L271](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-history.R#L172-L271)).

Neither pi nor the AI SDK summarizes a thread: pi leaves compaction to `transformContext`, and the AI SDK's guide prunes through `prepareStep` and `pruneMessages` without a model call ([guide](https://ai-sdk.dev/cookbook/guides/agent-context-compaction)).
The summarizing compaction of pi's CLI is in `pi-coding-agent`, under [`src/core/compaction`](https://github.com/earendil-works/pi/tree/e3da248ea9100a3b5d53f9c701b6a47ef7f58d6e/packages/coding-agent/src/core/compaction), MIT and not exported.
Today's compaction keeps the last `min(chat_compact_keep, n - 2)` turns, or fewer where those do not start on a user's turn, since it moves the cut forward to the next one, to keep "each compaction a strict reduction", and makes no call where a thread has fewer than two turns ([R/ext-compact.R#L296-L325](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-compact.R#L296-L325)).

</details>
