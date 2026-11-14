# The assistant's chat
Status: review. Design for [Assistant as a plugin](Rewrite-1.4).

One of the design pages of the assistant ([Assistant as a plugin](Rewrite-1.4)): the chat that the assistant's `ui` draws in a panel of any frontend.
It covers the message field and a turn as it streams, what waits while a turn runs, stopping a turn, the rows of the tool calls, undoing the assistant's edits, the threads, attachments, the slash commands, the meter, the pick of the model, the visitor's credential and what fails.
It shapes the Work item that draws the chat, and the two that let a visitor use their own key and log in.
What a thread holds is [The assistant's state](Rewrite-1.4.3)'s, what the tools do is [The assistant's tools](Rewrite-1.4.2)'s, how a call is authenticated and who picks the model is [Model access](Rewrite-1.4.1)'s, and where the panel goes is the frontend's, as [Places the dock offers plugins](Rewrite-1.2.4) has it for the dock.

## What must hold

1. The chat draws only in the element that a frontend gives it and in the browser's top layer, and works at any size down to a rail's, under every frontend ([Places the dock offers plugins](Rewrite-1.2.4#what-must-hold)).
2. What today's chat offers carries over, but for what Today drops with its reason.
3. The user can stop a turn at any point, and a stopped turn leaves applied every edit that it finished, and none half applied.
4. The user takes back the assistant's edits with the frontend's Undo, in one history with their own.
5. What fails and the user should know of, such as a call to the model, reaches the user as a notification, which the frontend draws ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)).
6. The chat shows a thread as the assistant's state holds it, whatever changes that state, after the older messages that the plugin keeps in its memory.
7. The user can edit the board while a turn runs, and take back the assistant's edits, as at any other time.
8. One turn runs at a time on a board, and the user can switch and start threads while it runs.

## Today

Today's chat is shinychat's `chat_ui()` in the dock's panel of the assistant, with a footer of the assistant's own ([R/ext-server.R#L164-L207](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L164-L207)), and shinychat's `chat_server()` behind it ([#L597-L666](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L597-L666)):

| Today, at `fcbdb27` | Where it goes |
|---|---|
| The message field, "Ask about your board", and the greeting's three suggestions, another three on an empty board ([R/ext-skin.R#L24-L62](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-skin.R#L24-L62)) | Carried over ([The message field and a turn](#the-message-field-and-a-turn)) |
| Replies drawn as Markdown, with tables, and with code blocks that a button copies ([CopyableCodeBlock.tsx](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/js/src/markdown/components/CopyableCodeBlock.tsx)) | Carried over ([The message field and a turn](#the-message-field-and-a-turn)) |
| The message field's keys: Enter sends, Shift+Enter starts a new line, and Up and Down bring back the user's earlier messages into an empty message field ([TiptapInput.tsx#L151-L152](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/js/src/chat/TiptapInput.tsx#L151-L152), [#L217-L230](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/js/src/chat/TiptapInput.tsx#L217-L230)) | Carried over ([The message field and a turn](#the-message-field-and-a-turn)) |
| A button that scrolls to the newest message, and a dialog before a link opens another site, whose "Always open external links" holds until the page reloads ([ScrollToBottomButton.tsx](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/js/src/chat/ScrollToBottomButton.tsx), [ExternalLinkDialog.tsx#L62-L86](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/js/src/chat/ExternalLinkDialog.tsx#L62-L86), [ChatContainer.tsx#L889-L892](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/js/src/chat/ChatContainer.tsx#L889-L892)) | Carried over ([The message field and a turn](#the-message-field-and-a-turn)) |
| A reply that streams, and shinychat's stop button, which cancels it ([NEWS.md#L16-L22](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/pkg-r/NEWS.md#L16-L22)) | Carried over, with the stop button aborting the turn's signal ([Stopping a turn](#stopping-a-turn)) |
| Typing while a reply streams, with sending held back until it ends ([NEWS.md#L35](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/pkg-r/NEWS.md#L35)), and switching, starting and deleting threads held back too, with "Wait for the response to finish" ([ChatHistoryDrawer.tsx#L450-L460](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/js/src/chat/ChatHistoryDrawer.tsx#L450-L460)) | Carried over for sending, which waits for the turn in any thread, while switching, starting and deleting threads stay open, since the turn runs apart from the chat ([While a turn runs](#while-a-turn-runs)) |
| The model's thinking, as a panel that folds, where the provider returns it ([NEWS.md#L87](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/pkg-r/NEWS.md#L87)), which the skin styles ([R/ext-skin.R#L101-L110](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-skin.R#L101-L110)) | Carried over, since the plugin's `thinkingLevel` of `medium` has pi ask the provider for it, such as OpenAI's summary of the model's reasoning ([Model access](Rewrite-1.4.1#the-models-settings), [The message field and a turn](#the-message-field-and-a-turn)) |
| Tool calls as rows titled from the tool's name, as `list_blocks` shows as "List blocks" ([R/ext-skin.R#L64-L82](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-skin.R#L64-L82)), the calls to one tool with no text between them in one row ([NEWS.md#L28-L31](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/pkg-r/NEWS.md#L28-L31)), a failed call marked as failed, and the plots of `inspect_results` in its result ([ToolResult.tsx#L96-L98](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/js/src/chat/ToolResult.tsx#L96-L98), [#L207-L209](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/js/src/chat/ToolResult.tsx#L207-L209)) | Carried over, with the edit tool's row naming its commands ([Tool calls](#tool-calls)) |
| The drawer of shinychat, which starts, switches, renames, deletes and searches threads, with the titles that a model call gives ([NEWS.md#L16](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/pkg-r/NEWS.md#L16)), groups them by how recently each was updated, searches their titles ([ChatHistoryDrawer.tsx#L220-L226](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/js/src/chat/ChatHistoryDrawer.tsx#L220-L226)), and asks before it deletes one ([#L323-L332](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/js/src/chat/ChatHistoryDrawer.tsx#L323-L332)) | Carried over ([Threads](#threads)) |
| Editing a sent message, which forks the thread, with `‹ 1 / 2 ›` controls to switch between the versions | Dropped for now, since an edit forks the thread but not the board: the blocks that the assistant added in the first version stay on the board, while the thread of the second never mentions them. So the user corrects the assistant with a new message, which the model reads after its own earlier edits. Editing and its branches are later work, which nothing here rules out ([The assistant's state](Rewrite-1.4.3#the-state)) |
| Attachments of images, PDFs and text files, about 30 MB together, which open large when clicked ([ChatMessage.tsx#L135-L139](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/js/src/chat/ChatMessage.tsx#L135-L139)) | Carried over, with their bytes in the page's memory, and the bound set by the plugin, since no app sets the variable that sets it today ([Attachments](#attachments)) |
| The footer: the tags of the focus, the @ button with blockr.ui's multi-select of the blocks in view, the token meter, and the button that opens the drawer ([R/focus.R#L202-L274](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/focus.R#L202-L274), [R/ext-server.R#L845-L864](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L845-L864)) | Carried over for the meter and the drawer's button ([The meter](#the-meter), [Threads](#threads)), while the tags of the focus and the @ button are dropped, since the plugin tells the model which block has focus and which panels show, so that the user sets nothing ([The system prompt](Rewrite-1.4.5#the-sections)) |
| The pick of the model where the blockr option `chat_function` offers several, outside the chat, through core's board option `llm_model`, which the dock's options sidebar shows ([blockr.core R/board-option.R#L709-L722](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/board-option.R#L709-L722)), after which the thread goes on with the model picked ([R/ext-server.R#L556-L568](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L556-L568)) | In the chat's footer, where the deployment offers more than one model or names none ([The model](#the-model)) |
| The slash commands `/compact` and `/clear`, and `/name` for each skill that the user may call ([R/ext-commands.R](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-commands.R), [R/skills-invoke.R#L80-L114](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-invoke.R#L80-L114)) | Carried over ([Slash commands](#slash-commands)) |
| Blanking the chat in a panel 140 px wide or narrower, as a collapsed rail is ([R/ext-server.R#L365-L376](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L365-L376)) | Dropped, since a collapsed rail hides its panels ([Places the dock offers plugins](Rewrite-1.2.4#a-plugins-panel)) |
| Setting the height of the dock's wrapper through `:has(> .asst-panel)` ([R/ext-server.R#L213-L218](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L213-L218)) | Dropped, since the element that a frontend gives fills the panel ([Places the dock offers plugins](Rewrite-1.2.4#a-plugins-panel)) |
| Toasts where the chat cannot be built, compaction fails or the system prompt fails ([R/ext-server.R#L567-L581](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L567-L581), [#L745-L755](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L745-L755), [#L817-L823](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L817-L823)) | Notifications through `CoreApi` ([What fails](#what-fails)) |
| Up to three reminders, sent as if the user typed them, while changes stay staged at a turn's end ([R/ext-server.R#L988-L1028](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L988-L1028)) | Dropped with staging ([The assistant's tools](Rewrite-1.4.2)) |

## Proposal

### The panel

The assistant's class has a `ui`, a module whose `render()` core calls with the element that the frontend gives `mountPlugin()` ([Plugins](Rewrite-1.1.12#plugin-classes)).
It draws the chat in React, on the one copy that core ships, in a root of its own, in blockr.ui's design system ([UI modules in JS](Rewrite-1.1.7#react), [UI kit and design system for the client](Rewrite-1.7)).
It sizes itself from its element, as a container, so that the message field and the footer fit a rail.
What needs more room than the panel, such as the drawer of threads or the @ menu, opens in the browser's top layer, as a popover or a `<dialog>` ([Places the dock offers plugins](Rewrite-1.2.4#a-plugins-panel)).
The panel's tab shows the plugin's name, Assistant.

The chat follows the assistant's state through `core.store.subscribe()`, so that a thread shows the same whichever command changed it last (condition 6).
The dock may mount the chat again, as when it redraws a view, so what has to outlive the mount, the turn above all, runs from the class's `start`, while the chat keeps only what is the screen's alone, such as the text typed and not sent ([Places the dock offers plugins](Rewrite-1.2.4#a-plugins-panel)).

The chat is built on assistant-ui's primitives over its `ExternalStoreRuntime`, which displays messages that a store of the app's own holds, here the assistant's state (notes).
That runtime gives stopping, attachments and a list of threads through handlers that the plugin writes.
Whether it serves, against components of the plugin's own, is for the issue that draws the chat to settle ([Assistant as a plugin](Rewrite-1.4#proposal)).
It serves only where it meets conditions 1 and 6, draws on core's React in blockr.ui's design system, as above, and has a license that lets blockr.assistant ship it in the plugin's bundle, as MIT does (notes).
Where both serve, the issue keeps the one that needs fewer lines of the plugin's own TypeScript for the transcript, the message field and the stop button, and the smaller bundle breaks a tie.

### The message field and a turn

A turn starts from the message field:

1. The user types a message into the message field, whose placeholder reads "Ask about your board", and sends it.
2. The plugin adds the user's message to the open thread through `blockr.assistant-add_message`, after adding a thread through `blockr.assistant-add_thread` where none is open ([The assistant's state](Rewrite-1.4.3#commands)), and its `start` runs the turn ([Assistant as a plugin](Rewrite-1.4#proposal)).
3. The reply streams into the transcript from the plugin's memory, and enters the thread as one finished message as it ends.
4. Each tool call shows as a row as it starts, which shows its result once it returns (Tool calls).

A thread with no message shows the greeting, with three suggestions, or three others on an empty board, as today, and a suggestion sends itself as the user's message.

A reply shows as Markdown, with tables, and with code blocks that a button copies, as today.
Where the provider returns the model's thinking, the reply shows it where it came, as a panel that folds, as today, while the board stays open, since the plugin keeps a reply's reasoning in its memory rather than in the thread ([The assistant's state](Rewrite-1.4.3#files-and-images)).
The message field keeps today's keys: Enter sends, Shift+Enter starts a new line, and Up and Down bring back the user's earlier messages into an empty message field.
A button scrolls to the newest message once the user has scrolled up.
A link in a reply that leads to another site opens only after a dialog, as today.
The dialog's "Always open external links" holds until the page reloads.

### While a turn runs

While a turn runs, the board stays open (condition 7).
The user edits it through the frontend, and takes back the assistant's edits with the frontend's Undo, as at any other time.
So the board can change under a turn, and the model learns what changed before its next call, from a note that the thread keeps ([The system prompt](Rewrite-1.4.5#what-changed-under-the-model)).
The chat leaves that note out of the transcript, since the user sees on the board what changed.
The tools say what changed under them too, such as a block that the user removed while the edit tool waited ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).

The chat stays open too, but only one turn runs at a time on a board, in whichever thread (condition 8).
Two turns at once would each edit the board under the other, and `undo_edit` in one would take back the other's last step, since both edit as the origin `assistant` ([The assistant's tools](Rewrite-1.4.2#the-tools)).
The user can switch threads, start one, rename one and delete one, while the turn goes on in its own thread, which the drawer marks (Threads).
The user can type in any thread too, but sends a message or a slash command only once the turn ends, and the send button says which thread's turn it waits for.
Only `/clear` stays open, since it starts a thread, as the drawer does (Slash commands).
Deleting the thread whose turn runs asks to confirm, as any deletion does, and then stops the turn, as the stop button does, before the thread goes (Stopping a turn).
The pick of the model stays open as well, and applies from the next turn (The model).

### Stopping a turn

While a turn runs, the stop button shows in its thread, and pressing it aborts the turn's signal:

1. The library stops the model's stream.
2. A one-time evaluation that the edit tool awaits stops waiting ([Evaluation in the client](Rewrite-1.1.10#demand)).
   The edit tool then returns that its commands applied, with as much of its review as it has, and that the user stopped the turn ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).
3. A request that a tool sent is cancelled, through the signal that `core.request()` takes, where R has not started it ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
   Once R has started it, it runs to its end, and every request sent after it waits, unless the app runs its requests in a worker that can stop one ([Wire protocol](Rewrite-1.1.9#cancelling)).
4. What the reply streamed until then enters the thread as its message, and each tool call left without a result gets one that says the user stopped the turn ([The assistant's tools](Rewrite-1.4.2#how-failures-reach-the-model)).

An edit that the store applied before the stop stays applied, and none is half applied, since each edit applies all or none (condition 3).

### Tool calls

Each tool call shows as a row titled from the tool's name, as today's `list_blocks` shows as "List blocks", folded to its title, and opening to its args and its result.
Where the model calls tools with no text between the calls, the calls to each tool share one row, which opens to each call, as today's chat groups them.
A call whose result is marked as an error shows as failed, as today's rows show it ([The assistant's tools](Rewrite-1.4.2#how-failures-reach-the-model)).
The plots that `inspect_results` returns show in its result while the page lives, since the plugin keeps their bytes in its memory ([The assistant's state](Rewrite-1.4.3#files-and-images)).
The edit tool's row names the commands that it ran by their labels, which `core.commands.registered()` gives, such as "Add block" and "Add link", and each block that it changed with its status, drawn as the design system draws a block's status ([Block cards in the dock](Rewrite-1.2.7#the-status-dot)).
A refused edit shows the command that refused and why, as the model gets it ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).

### Undoing the assistant's edits

The chat offers no Undo or Redo of its own.
The frontend's Undo and Redo take back the assistant's edits as they take back the user's, in the order the board took them, since the store keeps one history of every origin's steps ([Board updates](Rewrite-1.1.2#undo)).
So one Undo serves the user, whoever made the last edit (condition 4).

The model can take back the assistant's last undo step through the tool `undo_edit`, when the user asks for that in words ([The assistant's tools](Rewrite-1.4.2#the-tools)).
It takes back that step even where the user edited the board after it, since an undo is a new edit on the board as it is ([Board updates](Rewrite-1.1.2#undo)).
So it keeps a change that the user made since, but where the user changed the same thing as the assistant's edit, the undo sets it back to its value before that edit, since the last writer wins.
Changes to the threads take no undo step, so neither the frontend's Undo nor `undo_edit` takes back a message ([The assistant's state](Rewrite-1.4.3#commands)).

### Threads

A button in the footer opens the drawer of threads in the top layer.
The drawer lists the board's threads, the last updated first, grouped by how recently each was updated, as today's drawer groups them.
Its buttons start, rename and delete threads, as today's drawer does, and it asks the user to confirm before it deletes one.
Each button runs a command of the assistant's class, `blockr.assistant-add_thread`, `blockr.assistant-rename_thread` or `blockr.assistant-remove_thread` ([The assistant's state](Rewrite-1.4.3#commands)).
It marks the thread whose turn runs, which the user can leave and come back to while the turn goes on (While a turn runs).
It switches threads and searches their titles without a command, since neither changes the board.
A thread takes its title from a model call after its first exchange, as shinychat's titles come today, until the user renames it.
Which thread is open stays in the browser's local storage, and a board that lacks that thread opens on the greeting ([The assistant's state](Rewrite-1.4.3#the-state)).

### Attachments

The message field takes images, PDFs and text files, up to about 30 MB together, as today, and an attachment opens large when the user clicks it.
The plugin sets that bound itself, since the environment variable that sets it today goes with shinychat, and no app sets it (notes).
The plugin keeps their bytes in memory and sends them to the model with the message and in the turns after it, while the state names each file ([The assistant's state](Rewrite-1.4.3#files-and-images)).
A file that the provider refuses reaches the user as a notification (What fails).

### Slash commands

The message field takes three kinds of slash command, which typing `/` lists:

- The slash command `/compact` compacts the thread ([The assistant's state](Rewrite-1.4.3#compaction)).
- The slash command `/clear` starts a new thread, as today's starts a new chat.
- For each skill that the user may call, the slash command `/name` sends the skill with its text, as today ([R/skills-invoke.R#L80-L114](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-invoke.R#L80-L114)).

Neither `/compact` nor `/clear` enters the transcript, as neither does today.
The message of a `/name` keeps both the line that the user typed, which the transcript shows, and the skill's text, which the model gets with the user's request on that call and every later one, as today's prompt words it ([R/skills-invoke.R#L106-L114](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/skills-invoke.R#L106-L114)).
So the transcript shows the slash command as the user typed it, as today's shows shinychat's echo of it ([NEWS.md#L10](https://github.com/posit-dev/shinychat/blob/6cb14177de45a78ab50aeb54a1540d8ac560a3de/pkg-r/NEWS.md#L10)), while the thread says what the model was told ([The assistant's state](Rewrite-1.4.3#the-state)).

### The meter

The footer shows the tokens that the thread has spent, input and output, from its `usage` ([The assistant's state](Rewrite-1.4.3#the-state)), as today's meter shows them, without the cached input.

### The model

Where the deployment offers more than one model, or names none, the footer shows the model that the open thread's next turn talks to, beside the meter, and lists the models offered in the top layer to pick from ([Model access](Rewrite-1.4.1#who-picks-the-model)).
A pick sets the model of the open thread alone, through `blockr.assistant-set_model` ([The assistant's state](Rewrite-1.4.3#commands)).
A new thread starts on the open thread's pick, which the chat passes to `blockr.assistant-add_thread`.
Where no thread is open, the footer shows the default, and a pick made then goes to the thread that the first message adds ([Model access](Rewrite-1.4.1#who-picks-the-model)).
Where the thread's pick is a model that the deployment does not offer, the footer names it beside the default that the calls go to.
A pick applies from the next turn, so that a turn that runs keeps its model to its end, and the thread goes on with the new model, as today's goes on after a pick ([R/ext-server.R#L556-L568](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L556-L568)).

### The credential

Where the deployment leaves `assistant_api_key` unset, the chat asks the visitor for their own key before the first turn, in a field whose value the plugin keeps in its memory, and offers a login beside it where the base URL belongs to a service that offers one ([Model access](Rewrite-1.4.1#how-a-call-is-authenticated)).
The login opens in a window of its own, which hands its code back to the page, since leaving the page for the service's login would reload the app, and drop with it what the board holds unsaved.
When another board opens in the same page, the key stays, since it is the visitor's rather than the board's (notes).
A reload asks again, since neither a typed key nor the key that a login gives outlives the page.
A key that the base URL refuses fails the call, as any call fails (What fails), and the chat asks for the key again.
OpenAI's refusal reaches a page only as a failed connection, since its 401 carries no CORS header ([Model access](Rewrite-1.4.1#how-a-call-is-authenticated)), so where a call to OpenAI fails that way, the chat says that the key may be wrong as well as the connection lost.

### What fails

A failure that the user should know of becomes a notification that the assistant raises through `notify()`, naming its class's id, which the frontend draws as it draws any ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)):

| What | Severity and code |
|---|---|
| A call to the model that fails, as for a missing or refused credential, or a turn that cannot start, as when the loop's code fails to load | Error, `assistant_call_failed` |
| A file that the provider refuses | Error, `assistant_attachment_refused` |
| Compaction that fails, which leaves the thread as it was | Warning, `assistant_compaction_failed` |
| The skills that R cannot list, as for a directory in `assistant_skills` that does not exist | Error, `assistant_skills_failed` |
| A list of models that leaves none to offer, where the deployment names none, as at a company's own proxy that lists none, or where no model in the list takes tools | Error, `assistant_models_failed` |

Where the deployment names no models and the base URL's list leaves none to offer, the user can send nothing, and the plugin asks for the list again as the next board opens or a new key comes ([Model access](Rewrite-1.4.1#who-picks-the-model)).
A list that the base URL refuses for its key goes as any refused key does, and where the key is the visitor's, the chat asks for it again (The credential).
Where R cannot list the skills, the chat goes on without any, until the plugin asks again as the next board opens ([The assistant's tools](Rewrite-1.4.2#the-requests-in-r)).
A failure that ends a turn shows at that turn in the transcript too, so that the user sees why the reply stopped.
The thread keeps what the turn finished, and what its reply streamed until the failure, as after a stop (Stopping a turn).
What a tool's request returns as a failure, such as `inspect_results` on a locked board, goes to the model as the tool's result, which tells the user in its reply ([The assistant's tools](Rewrite-1.4.2#the-requests-in-r)).

### On a locked board

The chat works on a locked board as on any other: the user asks, and the model reads and answers.
The edit tool returns why a lock refuses an edit ([The assistant's tools](Rewrite-1.4.2#on-a-locked-board)).
An edit that the locks leave open applies as on any board, such as one to the state of a block whose `locked` is `FALSE`, and Undo and Redo take it back ([Locked boards and the properties of blocks](Rewrite-1.1.11#the-board-lock)).
The assistant's commands stay enabled, so that threads and the pick of the model work as on any board ([The assistant's state](Rewrite-1.4.3#commands)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

Read on 2026-11-12, assistant-ui's `ExternalStoreRuntime` "bridges your existing state management with assistant-ui", for messages that live in a store and should stay there ([docs](https://www.assistant-ui.com/docs/runtimes/custom/external-store)).
It takes a thread's messages as an array in `messages`, and needs `onNew` for a new message and `onCancel` to stop, while `convertMessage` maps the plugin's messages to its own, attachments come through its `adapters`, and threads through `ExternalStoreThreadListAdapter`.
Editing and its branches, once they come, go through `onEdit`, "required for edit feature", `setMessages`, "required for branch switching", and a `messageRepository` made with `ExportedMessageRepository.fromBranchableArray()`, where every message has an `id` and a `parentId` and "messages with the same `parentId` create branches".
Its `onReload` regenerates a reply, which today's chat does not offer, so the chat leaves it out for now.
Its package, `@assistant-ui/react`, is under MIT, read on npm on 2026-11-13 for 0.15.36, so its text joins those that the plugin's build writes beside the bundle ([Assistant as a plugin](Rewrite-1.4#proposal)).

Today's code, at `fcbdb27`: the footer's button for the drawer clicks shinychat's hidden trigger ([R/ext-server.R#L318-L364](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L318-L364)), the meter counts each turn's input and output tokens ([R/ext-server.R#L1281-L1309](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L1281-L1309)), and the skin over shinychat's classes is scoped under `.asst-panel` ([R/ext-skin.R#L84-L344](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-skin.R#L84-L344)).
Today's `/clear` starts a new chat through shinychat's `new_chat()` and drops what is staged ([R/ext-server.R#L1055-L1067](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L1055-L1067)).
Today, shinychat bounds attachments through its environment variable `SHINYCHAT_MAX_ATTACHMENT_SIZE`, which no app in the workspace sets.
Today's assistant drops the last turns of a failed exchange as it hands a thread to another model, since an empty reply would show as a spinner ([R/ext-server.R#L510-L536](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fcbdb2756a8965915159b7b5ec51197ae458c2c8/R/ext-server.R#L510-L536)), so a reply that streamed nothing before a stop or a failure adds no message.

The plugin keeps the visitor's key in its module's scope rather than in what `start` keeps, since core starts the plugin again as each board opens, and nothing that `start` keeps outlives its board ([Plugins](Rewrite-1.1.12#running-a-plugin)).

In `@earendil-works/pi-ai` 1.5.2, a call that sends an effort asks OpenAI's Responses API for a summary of the reasoning, `summary: "auto"` (`dist/api/openai-responses.js`), and pi streams that summary, as it streams Anthropic's thinking, into a content block of the type `thinking` (`dist/api/openai-responses-shared.js`, `dist/api/anthropic-messages.js`, `dist/types.d.ts`).

</details>
