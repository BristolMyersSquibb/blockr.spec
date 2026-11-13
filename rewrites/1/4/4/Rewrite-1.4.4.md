# The assistant's chat
Status: review. Design for [Assistant as a plugin](Rewrite-1.4).

One of the design pages of the assistant ([Assistant as a plugin](Rewrite-1.4)): the chat that the assistant's `ui` draws in a panel of any frontend.
It covers the composer and a turn as it streams, stopping a turn, the rows of the tool calls, undoing the assistant's edits, the threads with their branches, attachments, the focus, the commands, the meter, the pick of the model, the visitor's credential and what fails.
It shapes the Work item that draws the chat.
What a thread holds is [The assistant's state](Rewrite-1.4.3)'s, what the tools do is [The assistant's tools](Rewrite-1.4.2)'s, and where the panel goes is the frontend's, as [Places the dock offers plugins](Rewrite-1.2.4) has it for the dock.

## What must hold

1. The chat draws only in the element that a frontend gives it and in the browser's top layer, and works at any size down to a rail's, under every frontend ([Places the dock offers plugins](Rewrite-1.2.4#what-must-hold)).
2. What today's chat offers carries over, but for what Today drops with its reason.
3. The user can stop a turn at any point, and a stopped turn leaves applied every edit that it finished, and none half applied.
4. The user takes back the assistant's edits apart from their own.
5. What fails and the user should know of, such as a call to the model, reaches the user as a notification, which the frontend draws ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)).
6. The chat shows a thread as the assistant's state holds it, whatever changes that state, after the older messages that the plugin keeps in its memory.

## Today

Today's chat is shinychat's `chat_ui()` in the dock's panel of the assistant, with a footer of the assistant's own ([R/ext-server.R#L164-L207](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L164-L207)), and shinychat's `chat_server()` behind it ([#L597-L666](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L597-L666)):

| Today, at `fcbdb27` | Where it goes |
|---|---|
| The composer, "Ask about your board", and the greeting's three suggestions, another three on an empty board ([R/ext-skin.R#L24-L62](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-skin.R#L24-L62)) | Carried over ([The composer and a turn](#the-composer-and-a-turn)) |
| A reply that streams, and shinychat's stop button, which cancels it ([NEWS.md#L16-L22](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/pkg-r/NEWS.md#L16-L22)) | Carried over, with the stop button aborting the turn's signal ([Stopping a turn](#stopping-a-turn)) |
| Tool calls as rows titled from the tool's name, as `list_blocks` shows as "List blocks" ([R/ext-skin.R#L64-L82](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-skin.R#L64-L82)) | Carried over, with the edit tool's row naming its commands ([Tool calls](#tool-calls)) |
| shinychat's drawer, which starts, switches, renames, deletes and searches threads, with the titles that a model call gives | Carried over ([Threads](#threads)) |
| Editing a sent message, which forks the thread, with `‹ 1 / 2 ›` controls to switch between the versions | Carried over ([Branches](#branches)) |
| Attachments of images, PDFs and text files, about 30 MB together | Carried over, with their bytes in the page's memory ([Attachments](#attachments)) |
| The footer: the tags of the focus, the @ button with blockr.ui's multi-select of the blocks in view, the token meter, and the button that opens the drawer ([R/focus.R#L202-L274](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/focus.R#L202-L274), [R/ext-server.R#L845-L864](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L845-L864)) | Carried over ([The focus](#the-focus), [The meter](#the-meter)) |
| The pick of the model where the blockr option `chat_function` offers several, outside the chat, through core's board option `llm_model`, which the dock's options sidebar shows ([blockr.core R/board-option.R#L709-L722](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L709-L722)), after which the thread goes on with the model picked ([R/ext-server.R#L556-L568](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L556-L568)) | In the chat's footer, where the deployment offers more than one model or names none ([The model](#the-model)) |
| The commands `/compact` and `/clear`, and `/name` for each skill that the user may call ([R/ext-commands.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-commands.R), [R/skills-invoke.R#L80-L114](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-invoke.R#L80-L114)) | Carried over ([Commands](#commands)) |
| Blanking the chat in a panel 140 px wide or narrower, as a collapsed rail is ([R/ext-server.R#L365-L376](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L365-L376)) | Dropped, since a collapsed rail hides its panels ([Places the dock offers plugins](Rewrite-1.2.4#a-plugins-panel)) |
| Setting the height of the dock's wrapper through `:has(> .asst-panel)` ([R/ext-server.R#L213-L218](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L213-L218)) | Dropped, since the element that a frontend gives fills the panel ([Places the dock offers plugins](Rewrite-1.2.4#a-plugins-panel)) |
| Toasts where the chat cannot be built, the system prompt fails or compaction fails ([R/ext-server.R#L567-L581](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L567-L581)) | Notifications through `CoreApi` ([What fails](#what-fails)) |
| Up to three reminders, sent as if the user typed them, while changes stay staged at a turn's end ([R/ext-server.R#L988-L1028](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L988-L1028)) | Dropped with staging ([The assistant's tools](Rewrite-1.4.2)) |

## Proposal

### The panel

The assistant's class has a `ui`, a module whose `render()` core calls with the element that the frontend gives `mountPlugin()` ([Plugins](Rewrite-1.1.12#plugin-classes)).
It draws the chat in React, on the one copy that core ships, in a root of its own, in blockr.ui's design system ([UI modules in JS](Rewrite-1.1.7#react), [UI kit and design system for the client](Rewrite-1.7)).
It sizes itself from its element, as a container, so that the composer and the footer fit a rail.
What needs more room than the panel, such as the drawer of threads or the @ menu, opens in the browser's top layer, as a popover or a `<dialog>` ([Places the dock offers plugins](Rewrite-1.2.4#a-plugins-panel)).
The panel's tab shows the plugin's name, Assistant.

The chat follows the assistant's state through `core.store.subscribe()`, so that a thread shows the same whichever command changed it last (condition 6).
The dock may mount the chat again, as when it redraws a view, so what has to outlive the mount, the turn above all, runs from the class's `start`, while the chat keeps only what is the screen's alone, such as the text typed and not sent ([Places the dock offers plugins](Rewrite-1.2.4#a-plugins-panel)).

The chat is built on assistant-ui's primitives over its `ExternalStoreRuntime`, which displays messages that a store of the app's own holds, here the assistant's state (notes).
That runtime takes branches as messages that name their parent, as the state's do, and gives editing, stopping, attachments and a list of threads through handlers that the plugin writes.
Whether it serves, against components of the plugin's own, is the spike's to settle ([Choosing the libraries](Rewrite-1.4.6)).

### The composer and a turn

A turn starts from the composer:

1. The user types into the composer, "Ask about your board", and sends.
2. The plugin adds the user's message to the thread through `blockr.assistant-add_message` ([The assistant's state](Rewrite-1.4.3#commands)), and its `start` runs the turn ([Assistant as a plugin](Rewrite-1.4#proposal)).
3. The reply streams into the transcript from the plugin's memory, and enters the thread as one finished message as it ends.
4. Each tool call shows as a row as it starts, which shows its result once it returns (Tool calls).

A thread with no message shows the greeting, with three suggestions, another three on an empty board, as today, and a suggestion sends itself as the user's message.

### Stopping a turn

While a turn runs, the stop button shows, and pressing it aborts the turn's signal:

1. The library stops the model's stream.
2. A one-time evaluation that the edit tool awaits stops waiting ([Evaluation in the client](Rewrite-1.1.10#demand)).
3. A request that a tool sent is cancelled, through the signal that `core.request()` takes ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
4. What the reply streamed until then enters the thread as its message.

An edit that the store applied before the stop stays applied, and none is half applied, since each edit applies all or none (condition 3).

### Tool calls

Each tool call shows as a row titled from the tool's name, as today's `list_blocks` shows as "List blocks", folded to its title, and opening to its args and its result.
The edit tool's row names the commands that it ran by their labels, which `core.commands.registered()` gives, such as "Add block" and "Add link", and each block that it changed with its status, drawn as the design system draws a block's status ([Block cards in the dock](Rewrite-1.2.7#the-status-dot)).
A refused edit shows the command that refused and why, as the model gets it ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).

### Undoing the assistant's edits

The chat offers Undo and Redo for the assistant's edits, which take back the assistant's last edit or apply it again, through `store.undo("assistant")` and `store.redo("assistant")`, and which show where `store.canUndo("assistant")` and `store.canRedo("assistant")` say ([Board updates](Rewrite-1.1.2#undo)).
So the user takes back the assistant's edits apart from their own, which the frontend's undo takes back (condition 4).
An undo is a new edit on the board as it is, so a change that the user made since keeps its value where the two differ, as every undo does ([Board updates](Rewrite-1.1.2#undo)).

The model can take back its last edit too, through the tool `undo_edit`, when the user asks for that in words ([The assistant's tools](Rewrite-1.4.2#the-tools)).
Both take back the same steps, since the assistant's edits are the only steps of the origin `assistant`, while the changes to its threads take no undo step ([The assistant's state](Rewrite-1.4.3#commands)).

### Threads

A button in the footer opens the drawer of threads in the top layer.
The drawer lists the board's threads, the last updated first, and starts, switches, renames, deletes and searches them, through the assistant's commands ([The assistant's state](Rewrite-1.4.3#commands)).
A thread takes its title from a model call after its first exchange, as shinychat's titles come today, until the user renames it.
Which thread is open stays with the page ([The assistant's state](Rewrite-1.4.3#the-state)).

### Branches

The user edits a sent message of their own, and the chat adds the edited message under the same parent, makes it the head and runs a turn from there ([The assistant's state](Rewrite-1.4.3#the-state)).
A message with siblings shows `‹ 1 / 2 ›` controls, which switch between them through `blockr.assistant-set_head`.

### Attachments

The composer takes images, PDFs and text files, up to about 30 MB together, as today.
The plugin keeps their bytes in memory and sends them to the model with the message and in the turns after it, while the state names each file ([The assistant's state](Rewrite-1.4.3#files-and-images)).
A file that the provider refuses reaches the user as a notification (What fails).

### The focus

The footer shows a tag for the block that has focus in `CoreApi.focus`, which the frontend sets ([Block cards in the dock](Rewrite-1.2.7#focus)), with a × that hides the tag until focus moves to another block.
It shows a tag too for each block that the user added with @, which stays until the user removes it.
The @ button opens blockr.ui's multi-select of the blocks, those of the active view first where the dock is the frontend, and its picks become the thread's `focus` through `blockr.assistant-set_focus` ([The assistant's state](Rewrite-1.4.3#commands)).
Where a frontend sets no focus, the footer shows no tag for it.
The model reads the focus before each call ([The system prompt](Rewrite-1.4.5#the-sections)).

### Commands

The composer takes three kinds of command, which typing `/` lists:

- The command `/compact` compacts the thread ([The assistant's state](Rewrite-1.4.3#compaction)).
- The command `/clear` starts a new thread, as today's starts a new chat.
- For each skill that the user may call, the command `/name` sends the skill with its text, as today ([R/skills-invoke.R#L80-L114](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-invoke.R#L80-L114)).

Neither `/compact` nor `/clear` enters the transcript, as neither does today.

### The meter

The footer shows the tokens that the thread has spent, input and output, from its `usage` ([The assistant's state](Rewrite-1.4.3#the-state)), as today's meter shows them, without the cached input.
### The model

Where the deployment offers more than one model, or names none, the footer shows the model that the next turn talks to, beside the meter, and lists the models offered in the top layer to pick from ([Model access](Rewrite-1.4.1#who-picks-the-model)).
Where it names none, the chat asks for a pick before the first turn, from the models that the place lists for the key.
A pick that the board keeps, as with the deployment's key, runs `blockr.assistant-set_model` ([The assistant's state](Rewrite-1.4.3#commands)), and one that the visitor's browser keeps, as with their own key or a login, goes to its local storage.
Where the board's pick is a model that the deployment does not offer, the footer names it beside the default that the calls go to.
A pick applies from the next turn, so that a turn that runs keeps its model to its end, and the thread goes on with the new model, as today's goes on after a pick ([R/ext-server.R#L556-L568](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L556-L568)).

### The credential

Where the deployment sets no key, the chat asks the visitor for their own before the first turn, in a field whose value the plugin keeps in its memory, and offers a login beside it where the place offers one ([Model access](Rewrite-1.4.1#how-a-call-is-authenticated)).
The login opens in a window of its own, which hands its code back to the page, since leaving the page for the service's login would reload the app, and drop with it what the board holds unsaved.
A reload asks again, since neither a typed key nor the key that a login gives outlives the page.
A key that the place refuses fails the call, as any call fails (What fails), and the chat asks for the key again.

### What fails

A failure that the user should know of becomes a notification of the assistant's, with its class's id as its origin, which the frontend draws as it draws any ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)):

| What | Severity and class |
|---|---|
| A call to the model that fails, as for a missing or refused credential | Error, `assistant_call_failed` |
| A file that the provider refuses | Error, `assistant_attachment_refused` |
| Compaction that fails, which leaves the thread as it was | Warning, `assistant_compaction_failed` |

A failure that ends a turn shows at that turn in the transcript too, so that the thread says why its reply stopped.
What a tool's request returns as a failure, such as `inspect_results` on a locked board, goes to the model as the tool's result, which tells the user in its reply ([The assistant's tools](Rewrite-1.4.2#the-requests-in-r)).

### On a locked board

The chat works on a locked board as on any other: the user asks, and the model reads and answers.
The edit tool returns why the lock refuses an edit, so Undo and Redo have nothing to take back ([The assistant's tools](Rewrite-1.4.2#on-a-locked-board)).
The assistant's commands stay enabled, so that threads, branches, the focus and the board's pick of the model work as on any board ([The assistant's state](Rewrite-1.4.3#commands)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

Read on 2026-11-12, assistant-ui's `ExternalStoreRuntime` "bridges your existing state management with assistant-ui", for messages that live in a store and should stay there ([docs](https://www.assistant-ui.com/docs/runtimes/custom/external-store)).
It takes branches through `messageRepository`, made with `ExportedMessageRepository.fromBranchableArray()`, where every message has an `id` and a `parentId` and "messages with the same `parentId` create branches", and a parent comes before its children in the array.
It needs `onNew` for a new message, `setMessages`, "required for branch switching", `onEdit`, "required for edit feature", and `onCancel` to stop, while `convertMessage` maps the plugin's messages to its own, attachments come through its `adapters`, and threads through `ExternalStoreThreadListAdapter`.
Its `onReload` regenerates a reply, which today's chat does not offer, so the chat leaves it out for now.

Today's code, at `fcbdb27`: the footer's button for the drawer clicks shinychat's hidden trigger ([R/ext-server.R#L318-L364](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L318-L364)), the @ button sends every ticked id as `focus_set` from `inst/assets/focus.js`, the × of the focus's tag sends `focus_dismiss`, and removing a tag added with @ sends `focus_drop` ([R/focus.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/focus.R)), the meter counts each turn's input and output tokens ([R/ext-server.R#L1281-L1309](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L1281-L1309)), and the skin over shinychat's classes is scoped under `.asst-panel` ([R/ext-skin.R#L84-L344](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-skin.R#L84-L344)).
Today's `/clear` starts a new chat through shinychat's `new_chat()` and drops what is staged ([R/ext-server.R#L1055-L1067](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L1055-L1067)).
Today, shinychat bounds attachments through its environment variable `SHINYCHAT_MAX_ATTACHMENT_SIZE`, which goes with shinychat, so the plugin bounds them itself.

</details>
