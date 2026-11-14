# Block cards in the dock
Status: settled on 2026-11-12. Design for [Client-drawn dock](Rewrite-1.2).

One of the design pages of the client-drawn dock ([Client-drawn dock](Rewrite-1.2)): the card that the dock draws in a block's panel.
It covers the card's header, after [blockr#492](https://github.com/orgs/BristolMyersSquibb/discussions/492), with the block's mark, status, name, toggles, padlock and menu.
It also covers the card's sections, which show as the dock's state says ([The dock's state](Rewrite-1.2.1#card-sections)), the look of the output by the block's status, the notifications that [Notifications, logging and tracing](Rewrite-1.1.14) has a card show, compact headers, which block has focus, what the dock demands for its cards, the padlock that sets the block's lock, and the card on a locked board.
It builds on [Drawing the board](Rewrite-1.1.8#what-core-gives-plugins), through which core mounts the block's UI and output in the card.
It shapes the card ([blockr.dock#578](https://github.com/BristolMyersSquibb/blockr.dock/issues/578)), its status and notifications ([blockr.dock#579](https://github.com/BristolMyersSquibb/blockr.dock/issues/579)), the toasts of the notifications that no card shows ([blockr.dock#580](https://github.com/BristolMyersSquibb/blockr.dock/issues/580)), and the dock's demand, which drawing a view makes ([blockr.dock#577](https://github.com/BristolMyersSquibb/blockr.dock/issues/577)).
Which panels a view shows and the tab of a block's panel are [The dock's state](Rewrite-1.2.1#grids)'s, and why plugins add nothing to a card for now is [Places the dock offers plugins](Rewrite-1.2.4#places-besides-the-panel)'s.

## What must hold

Condition 4 of [Client-drawn dock](Rewrite-1.2#what-must-hold) rests on this page for block cards, through these:

1. The dock draws everything of a card but the block's UI and output, which core mounts in it, so that every block class draws in the dock with no code for the dock ([Drawing the board](Rewrite-1.1.8#what-must-hold)).
2. The header has a one-click toggle for the block's inputs and one for its output, drawn alike, and a block whose UI draws nothing gets no toggle for its inputs, as [blockr#492](https://github.com/orgs/BristolMyersSquibb/discussions/492) asks.
3. A card's sections show as the dock's state says, and the card changes them only through a command, so that saving, undo and other plugins see each change ([The dock's state](Rewrite-1.2.1#commands)).
4. The card's status dot shows each of the block's statuses, drawn as the design system specs block status, and draws from the block's status and its notifications alone, so that the DAG's badge can show the same status for the same block.
5. A block's notifications show on its card, each once, of the severities that the board option `show_conditions` names, from when core raises them until core withdraws them.
6. Under the board lock, the card draws no control for what a lock fixes, and it mounts the UI only of a block that the board lock leaves open ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).
7. The dock demands the blocks whose cards are on screen, and no other block.
8. The card shows whether the board lock leaves the block open, and its author sets that apart from which sections show, so that how a card looks never decides what readers may change ([Locked boards and the properties of blocks](Rewrite-1.1.11#block-locks)).

## Today

The dock's `edit_block` plugin draws each card in R, and the dock inserts it into an offcanvas, from which it moves the card into the block's panel and back ([R/block-ui.R#L28-L64](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/block-ui.R#L28-L64), [R/block-ui.R#L259-L295](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/block-ui.R#L259-L295)).
The header holds the block's mark with the status dot on it, the name, the preview's eye and the "…" menu, whose first row toggles the controls ([R/plugin-block.R#L1-L36](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L1-L36)).
Errors show above the sections, and warnings and messages fold under the preview behind their count, as "2 issues" ([R/plugin-block.R#L258-L288](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L258-L288)).
Core clears the output of a block that is not `ready` ([R/block-server.R#L64-L66](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/block-server.R#L64-L66)), and Shiny fades an output to 30% opacity while it recalculates ([R/board-server.R#L136-L141](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/board-server.R#L136-L141)).

| Today, at `655e323` | Where it goes |
|---|---|
| The card's frame: `block_ui()`, `insert_block_ui()` and `remove_block_ui()` for the dock board, the offcanvas that parks each card, and `show-block.js`, which moves a card into its panel | Replaced by the card that the dock draws in React in each block's panel, so that nothing parks or moves a card ([The card](#the-card)) |
| The mark, `block_card_mark()`, which draws blockr.ui's `block_mark()` at 32px with the block's type and package as its tooltip | Carried over, from the block registry's entry ([The header](#the-header)) |
| The status dot, `block_status_dot()`, drawn by the spec that `block_status_badge()` gives the card and blockr.dag's node badge, and the notes of a `waiting` and an `unset` block | Carried over into the dock's client, from `scheduler.status()`, with `invalid` in place of `unset`, and with a dot for `ready` and `unevaluated` too ([The status dot](#the-status-dot), [The output](#the-output)) |
| The name, `block_card_title()`, which `block-rename.js` renames in place | Carried over, renaming through `blockr.core-rename_block` ([The header](#the-header)) |
| The toggles, `block_card_toggles()` and `section-toggle.js`: the preview's eye, and the control that a `ctrl_block` plugin adds | The eye carried over, with the Controls toggle beside it, after [blockr#492](https://github.com/orgs/BristolMyersSquibb/discussions/492), while the control goes with `ctrl_block` ([Plugins](Rewrite-1.1.12#today)) |
| The "…" menu, `block_card_dropdown()` and `block-menu.js`: Controls, Rename, Append block, Copy block ID and Remove block | Carried over without Controls, which moves to the header, after [blockr#492](https://github.com/orgs/BristolMyersSquibb/discussions/492), and with core's commands in place of the dock's actions ([The menu](#the-menu)) |
| Whether a block has controls, `has_expr_ui()`, which renders the block's R UI and looks for markup | Replaced by whether the block's UI module draws anything ([The header](#the-header)) |
| The sections, `block_card_content()`: the control's, the inputs and the preview, which fold | The inputs and the preview carried over as the sections `inputs` and `outputs` of the dock's state ([The dock's state](Rewrite-1.2.1#card-sections)), while the control's section goes with `ctrl_block` ([Sections](#sections)) |
| The conditions, which `update_blk_cond_observer()` inserts and removes: errors above the sections, and warnings and messages folded under the preview | Carried over, from the notifications of `CoreApi`, with warnings above the sections beside errors, as the design system has them ([Notifications](#notifications)) |
| The compact header, which the board option `compact` turns on through `compact.js` | Carried over ([Compact headers](#compact-headers)) |
| The sections that a card reports, `reported_sections()`, and core's `frozen` channel, which the dock sets for every block on a locked board and for a block whose card hides its inputs | Replaced by the dock's state and the block's lock, while the channel goes, since a hidden UI takes no input and the store refuses what a lock fixes ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)), so a block whose card hides its inputs is fixed under the board lock unless its author opened it ([The block's lock](#the-blocks-lock)) |
| The ledger of built cards, `built_cards()` and the `mark_cards_*()` functions, which drive core's visibility channels, and the front panels that the dock holds eager | Replaced by the dock's demand of the blocks whose cards are on screen ([Demand](#demand)) |
| Shiny's fade of a recalculating output, and core's clearing of the output of a block that is not `ready` | Replaced by the card's look for each status ([The output](#the-output)) |
| The `callbacks` of `edit_block_server()`, through which a package runs code for every block | Dropped with `extension_block_callback()`, which hands them over, since a plugin reads every block's status through `scheduler.status()` ([Places the dock offers plugins](Rewrite-1.2.4#today)) |

## Proposal

### The card

The dock draws a card in each block's panel, as a React component, from the block in the store and its status in the scheduler ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
Top to bottom, a card holds its header, the block's errors and warnings, and its two sections, `inputs` above `outputs`.
The card fills its panel, on the panel's surface, with today's inset of 16px, and the output runs to the card's edges, as today ([inst/assets/css/blockr-dock.css#L437-L501](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L437-L501)).

The card mounts the block's UI with `mountBlock()` in the body of its `inputs` section, and the block's output with `mountOutput()` in the body of its `outputs` section.
It mounts both when dockview creates its panel, and calls their cleanups when dockview disposes of the panel, as when the panel closes or the block leaves the board.
So the UI and the output stay mounted while the panel sits behind another tab, as [UI modules in JS](Rewrite-1.1.7#the-contract) asks of a frontend.
A block shown in several views has a panel in each, and the card in each panel mounts the block's UI and output again, which loses nothing, since what a mount draws from is core's.
The card follows the board through `store.subscribe()`, so a removed block's card goes because the board changed.

### The header

The header is one row, as the design system's "Dock header" has it ([design-system.Rmd#L337-L346](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/vignettes/articles/design-system.Rmd#L337-L346)):

1. The block's mark, a 32px square in the colour of the block's category with the block's icon, carrying the status dot ([The status dot](#the-status-dot)).
2. The block's name, at 16px, which wraps to a second line and is cut after it.
3. The Controls toggle, the Preview toggle and the padlock, in that order.
4. The "…" button, which opens the block's menu ([The menu](#the-menu)).

The mark takes its icon and category from the entry of the block's class in the block registry, which `core.blockRegistry()` gives by the block's registry id ([Block classes in R](Rewrite-1.1.5#registration)).
Its tooltip is the entry's name, with the package of the registry id as its badge, as "head/tail block · blockr.core".
Today's tooltip is the block's first class in R with spaces for underscores, which no longer reaches the client, since class vectors stay in R ([State in JS](Rewrite-1#principles)).

A double-click on the name, or Rename in the menu, starts renaming the block in place, as today ([inst/assets/js/block-rename.js](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/js/block-rename.js)):

1. The name turns into a field that holds the name, selected.
2. Enter, or a click elsewhere, runs `blockr.core-rename_block` with the new name, as one undo step.
3. Escape restores the name that renaming began with.
4. The field refuses an empty name, or one of spaces alone, on Enter, saying "A block needs a name", and drops it on a click elsewhere.

A single click on the name stays free to select the panel.

Each toggle shows and hides one section of the card: the Controls toggle the `inputs` section and the Preview toggle the `outputs` section.
The toggles are drawn alike, as the design system's header tools: 26px, bare, with the sliders and the eye as their icons, "Controls" and "Preview" as their tooltips and labels, and `aria-pressed` while their section shows.
A click runs `blockr.dock-set_sections` with the block's new set of sections, as one undo step ([The dock's state](Rewrite-1.2.1#commands)).
So the eye keeps its place and look, and the Controls toggle moves from the menu into the header, as [blockr#492](https://github.com/orgs/BristolMyersSquibb/discussions/492) proposes.

The padlock shows whether the board lock leaves the block open to readers: closed while the block's `locked` is `true` or `null`, and open while it is `false` ([The block's lock](#the-blocks-lock)).
It is drawn as the toggles are, with the lock and the open lock as its icons, "Locked for readers" and "Open to readers" as its tooltips and labels, and `aria-pressed` while the block is open.

A block whose UI draws nothing gets no Controls toggle, as today's card gives none to a block whose R UI renders no markup ([R/block-ui.R#L71-L82](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/block-ui.R#L71-L82)).
Every block class names a UI module, since its module ships the schema of its state, and the modules of core's row-bind, static and fixed blocks draw nothing ([Block classes in R](Rewrite-1.1.5#the-block-class)).
So the card watches the module's element, and shows the Controls toggle once the module has put anything there.
Until then the `inputs` section takes no room.
No block class declares whether it has controls, and the registry entry stays as it is.

### The status dot

The status dot sits on the mark's upper right corner: an 8px dot with a 2px ring in the card's surface colour.
It reads `scheduler.status()` for the block and follows `scheduler.subscribe()` ([Evaluation in the client](Rewrite-1.1.10#statuses)):

| Status | Dot | Tooltip |
|---|---|---|
| `stale` | Filled with `text-muted` | Inputs changed since this block last ran |
| `waiting` | A ring of `border-warning` | Waiting for a data input |
| `invalid` | Filled with `border-warning` | Set this block's inputs |
| `failed` | Filled with `border-danger` | Evaluation failed |
| `ready` | Filled with `border-success` | Up to date |
| `unevaluated` | A ring of `text-muted` | Not evaluated yet |

The rows of `stale`, `waiting`, `invalid` and `failed` are today's, with `invalid` in place of `unset` ([R/plugin-block.R#L582-L659](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L582-L659)).
Today's card shows no dot for a block that is `ready` or `unevaluated`, so a card without one leaves open whether the block has run, which the two dots settle.
The two grey dots differ by shape, as the two amber ones do: `stale` is solid, for a block whose result is out of date, and `unevaluated` a ring, for one that has no result yet.
The design system's spec of block status lacks the two rows, and is to follow ([UI kit and design system for the client](Rewrite-1.7)).
Today a block that raises an error reads `failed` even where its status is `ready`, which catches an output that R could not make.
That carries over: the dot reads `failed` while an error about the block's output concerns the block, R's of the request `output` or core's of the code `output_unanswered` ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)).
A `stale` block is the exception, as today, since its errors were raised for inputs it no longer has.
The dot shows no evaluation that is running, as today's shows none, while the card fades the output ([The output](#the-output)).

The dock's client holds this spec as one function, which takes a block's status and its notifications and gives the dot's fill, ring and tooltip, with the light value of each colour for a renderer that cannot read CSS, as today's `block_status_badge()` gives them to the card and to blockr.dag's node badge.
The function uses nothing else of the dock's, so that blockr.dag can draw the same badge, whether it re-implements the function or both take it from another package, which [Client-drawn DAG](Rewrite-1.3#open-questions) leaves open.

### Sections

The card's `inputs` and `outputs` sections show as the dock's `visible` says for the block, and both show where it holds no entry for the block ([The dock's state](Rewrite-1.2.1#card-sections)).
A section folds over 0.22s as it closes and unfolds as it opens, whoever changed `visible`, unless the user's system asks for reduced motion, as today ([inst/assets/js/section-toggle.js](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/js/section-toggle.js)).
A rule divides the two sections only while both show, as today.

A closed section stays mounted and is hidden.
So a block's UI keeps what it holds on screen, such as an open gear tray, whose open state the design system has last for the session.
A hidden output measures 0 by 0, so core asks R for no output while it is hidden, and asks once it shows again ([UI modules in JS](Rewrite-1.1.7)).
Today's third section, for the control that a `ctrl_block` plugin adds, goes with that plugin ([Plugins](Rewrite-1.1.12#today)).

### The output

Core keeps drawing a block's last output whatever the block's status, and the card decides from the status how that output looks ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)):

| Status | The output |
|---|---|
| `ready` | As the renderer draws it |
| `stale` | Faded, as Shiny fades a recalculating output today |
| `failed` | Takes no room, and the errors above the sections say why |
| `waiting` and `invalid` | Hidden, with the status note in its place |
| `unevaluated` | Empty, since no output has come yet |

A block whose card is on screen is demanded, so a `stale` block is about to run, and its output fades until the new one comes, as today ([Demand](#demand)).
The card hides the output of a block that cannot run, as core clears it today, so that no output stands for inputs that the block no longer has.
A failed block's output takes no room, as the `inputs` section of a block whose UI draws nothing takes none, so that the card leaves no blank where the output was, while the status note of a `waiting` or `invalid` block takes the output's place.

The status note says what the block lacks, in one line of italic `text-muted` text at 13px where the output would be, with no icon, as the design system has a block with nothing to draw say what is missing ([design-system.Rmd#L1348-L1356](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/vignettes/articles/design-system.Rmd#L1348-L1356)):

- For a `waiting` block, it holds the block's `reason`: the message that the scheduler writes, which names each unlinked input or each upstream block that keeps the block waiting, or the message of the `blockr_waiting()` that the class signalled, such as "Save to write the file." ([Evaluation in the client](Rewrite-1.1.10#statuses)).
- For an `invalid` block, it holds the block's `reason`: the message of the `blockr_invalid()` that the class signalled, such as "Choose a dataset.", or of R's error for the arg that is unset.

Today's notes say only "Waiting for a data input" and "Set this block's inputs", each with an icon, against the design system ([R/plugin-block.R#L699-L730](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L699-L730)).
The note alone shows those two messages, so the card shows neither again among the block's notifications.

### Notifications

A block's card shows the notifications of `CoreApi` that concern the block and that R or core raised, of the severities that core's board option `show_conditions` names, warnings and errors unless a script, a file or the user sets others ([Notifications, logging and tracing](Rewrite-1.1.14#cores-basic-frontend)).
So the dock filters what a card shows as core's basic frontend does, and as today's block server filters a block's conditions by the same board option.
The dock plugin's class names `show_conditions` among the board options it requires ([Board options and blockr options](Rewrite-1.1.13#which-board-options-a-board-holds)).
The card reads `notifications.get()` as it draws and follows `notifications.subscribe()`, so a notification that core withdraws leaves the card at once.

The card places each notification by its severity:

- Errors and warnings show above the sections, whatever the sections show, in the design system's message style, danger for an error and the amber set for a warning ([design-system.Rmd#L1374-L1377](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/vignettes/articles/design-system.Rmd#L1374-L1377)).
- Messages fold under the output behind their count, such as "2 messages", as warnings and messages fold today.

Today's card folds warnings with the messages, against the design system, which puts a block's warning above its output, as its error.
It also leaves out the two messages that its status note holds ([The output](#the-output)).
A notification that a plugin raises shows as a toast, even where it concerns the block.
So does every notification that concerns no block ([Client-drawn dock](Rewrite-1.2#proposal)).
A notification's message shows as text, never as HTML.

A block whose card is not on screen keeps its notifications in `CoreApi` until its card shows them, as today's card holds its conditions while it is parked.

### The menu

The "…" button opens the block's menu on a click, or on ArrowDown while it has the keyboard's focus, as today ([inst/assets/js/block-menu.js#L93-L99](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/js/block-menu.js#L93-L99)), drawn as the design system's menus are, with these rows ([design-system.Rmd#L1160-L1165](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/vignettes/articles/design-system.Rmd#L1160-L1165)):

1. Rename, which starts renaming the block in place ([The header](#the-header)).
2. Append block, which opens the dock's "+" menu from the button.
   The dock appends a block of the class that the user picks there, as `blockr.core-append_block` does.
3. Copy block ID, with the id as monospaced meta text, which puts the id on the clipboard.
4. A divider, then Remove block, with the bin icon and the danger colour, which runs `blockr.core-remove_block`.

Controls leaves the menu for the header, together with the divider after it, as [blockr#492](https://github.com/orgs/BristolMyersSquibb/discussions/492) proposes.
The rows are the dock's own for now, and entries that plugins come to add to a block's menu would come from core, so that every menu of a block draws them ([Places the dock offers plugins](Rewrite-1.2.4#places-besides-the-panel)).
The rows that edit the board run core's commands, which make the edits that the dock's actions made today, each as one undo step of the user's ([Client-drawn dock](Rewrite-1.2#proposal), [Board updates](Rewrite-1.1.2#undo)).

### Compact headers

The board option `compact` turns every card's header into an eyebrow over the block's content, as today ([inst/assets/css/blockr-dock.css#L234-L283](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/blockr-dock.css#L234-L283)).
The mark shrinks to 20px, and the name to 11px, uppercase and muted, on one line with an ellipsis.
The card reads the option's value through `core.options`, and the dock plugin's class names `compact` among the board options it requires ([Board options and blockr options](Rewrite-1.1.13#reading-a-board-option-in-the-client)).

### Focus

The dock sets which block has focus in `CoreApi.focus`, which the assistant reads to tell which block the user is looking at ([Plugins](Rewrite-1.1.12#what-a-frontend-offers-other-plugins)):

- A block takes focus when the user clicks into its card or onto its tab, when a command shows its panel, such as `blockr.dock-show_panel` ([The dock's state](Rewrite-1.2.1#commands)), or when a plugin shows it through core's `show()`, which gives it focus under every frontend ([Plugins](Rewrite-1.1.12#showing-a-block-or-a-plugin)).
- A block takes focus when the keyboard's focus moves into its card.
- Hovering over a card gives no focus.
- Focus stays where it is when the user clicks into a plugin's panel, so that the block the user clicked before moving to the assistant's panel keeps focus, as today's assistant reads only block panels ([blockr.assistant R/focus.R#L10-L17](https://github.com/BristolMyersSquibb/blockr.assistant/blob/fd5865593fd8b015d00df9238e2e622475c2a9df/R/focus.R#L10-L17)).
- The dock sets focus to `null` when the focused block leaves the board.

### Demand

The dock demands the blocks whose cards are on screen, at the evaluation priority 1, above the default ([Evaluation in the client](Rewrite-1.1.10#demand)).
A card is on screen where it is in the active view and its panel is the one that its tab group shows, or that an open rail shows, as today's dock holds eager the front panel of each tab group and of each rail that is not collapsed ([R/utils-ui.R#L101-L111](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/utils-ui.R#L101-L111)).
A card whose sections are both closed is on screen too, so that its status dot stays current.
The dock replaces its demand with the new set whenever the active view or its grid changes, as when a tab group shows another panel or a rail collapses or opens ([The dock's state](Rewrite-1.2.1#commands)).
It makes its first demand within the frontend's `render()`, from the board, so that the blocks of the opening view are evaluated first ([Drawing the board](Rewrite-1.1.8#starting-the-page)).

### The block's lock

Which sections a card shows and whether readers may change the block are set apart: the toggles set the dock's `visible`, and the padlock sets the block's `locked`, core's property, which says whether the board lock leaves the block open ([Locked boards and the properties of blocks](Rewrite-1.1.11#block-locks)).
So the two never conflict, and they meet only on a locked board, where the card mounts no locked block's UI, whatever `visible` says ([On a locked board](#on-a-locked-board)).

A click on a closed padlock runs `blockr.core-set_block_lock` with `false`, which leaves the block open to readers, and one on an open padlock runs it with `null`, which gives the block back to the board lock, each as one undo step ([Board updates](Rewrite-1.1.2#undo)).
Every block starts with `null`, however it is added, so its padlock shows closed, and readers may change only the blocks whose padlock their author opened, as an author leaves a block open by setting its `locked` to `false` in an app without the board lock ([Locked boards and the properties of blocks](Rewrite-1.1.11#block-locks)).
Without the board lock, core fixes no block, so the author edits a block whatever its padlock shows, and no input greys out.

### On a locked board

Under the board lock, the card draws no control for what a lock fixes, as `core.lock` and `store.locked()` say ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)):

- It shows no toggle and no padlock, since no command sets a card's sections or a block's lock there ([The dock's state](Rewrite-1.2.1#on-a-locked-board), [Locked boards and the properties of blocks](Rewrite-1.1.11#the-board-lock)), and its sections show as the dock's `visible` says, as today's locked card does ([R/plugin-block.R#L131-L137](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L131-L137)).
- A double-click on its name starts no rename, since the board lock fixes every block's name.
- Its menu holds Copy block ID alone, as today.
- It mounts the UI only of a block that the board lock leaves open, and shows no `inputs` section for any other block, whatever `visible` says.

A block whose `inputs` show on a locked board is one that its author left open to readers, by opening its padlock or through a script, so a reader sets its state there as on any board ([The block's lock](#the-blocks-lock)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

Today's code, at `655e323`: the frame of the card, the offcanvas and the ledger of built cards are `R/block-ui.R`; the header, toggles, menu, sections, conditions and status dot are `R/plugin-block.R`; the metadata of the mark is `blks_metadata()` in `R/block-meta.R`; and the browser's side is `section-toggle.js`, `block-menu.js`, `block-rename.js`, `compact.js`, `attr-output.js` and `show-block.js` in `inst/assets/js`, with the card's rules in the first 501 lines of `inst/assets/css/blockr-dock.css`.

The card reads whether the block's UI drew anything with a `MutationObserver` on the element it gave `mountBlock()`, since a module written in React draws after `render()` returns.
The `inputs` section takes no room while that element is empty, so a block whose UI draws nothing shows no empty section either.

The status dot's fills are the design system's meaning tokens, with these light values, as `block_status_style()` gives them today: `text-muted` `#6b7280`, `border-warning` `#d97706`, `border-danger` `#dc2626`, and the ring `bg-surface` `#ffffff`, with `border-success` `#16a34a` for `ready` from the design system's palette ([design-system.Rmd#L78](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/vignettes/articles/design-system.Rmd#L78), [#L137](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/vignettes/articles/design-system.Rmd#L137)).
The rings of `waiting` and `unevaluated` are 1.5px wide, inside an 8px dot.
Today's card reads each token with its light value as the fallback, as `var(--blockr-color-border-danger, #dc2626)`, so the dot draws on a page without blockr.ui's token sheet too ([R/plugin-block.R#L678-L680](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L678-L680)).

Today's card renders a condition's message with `cli::ansi_html()`, which turns cli's ANSI styling into HTML ([R/plugin-block.R#L518-L538](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L518-L538)).
Whether a message still reaches the client with that styling is to be checked on `js-state`, and the card removes any escapes before it shows the text.

A block whose UI draws nothing keeps its padlock, though opening it gives readers no control, since no input shows for it, while a plugin's command could then change its state on a locked board.

The padlock reads the block's `locked` rather than `store.locked()`, which says `false` for every block without the board lock, since the padlock shows what the board lock will do.

The design system has locked mode hide the gear button and nothing else, so that reader controls, such as the patient profile's view toggles, stay on a block's face ([design-system.Rmd#L396-L400](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/vignettes/articles/design-system.Rmd#L396-L400)).
Under the board lock, the card mounts no locked block's UI at all ([UI modules in JS](Rewrite-1.1.7#the-contract)), so those controls go with it, and an author who wants readers to use them opens the block's padlock.
The design system is to follow ([UI kit and design system for the client](Rewrite-1.7)).

Today's locked card already offers no toggle and no rename, and its menu holds Copy block ID alone ([R/plugin-block.R#L191-L247](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/plugin-block.R#L191-L247)).
On a locked board the card mounts no locked block's UI, so no block's gear stays on screen there wired to nothing, which [blockr.dock#423](https://github.com/BristolMyersSquibb/blockr.dock/issues/423) reports today.

Two modes that the design system and blockr.dock's issues describe are not built today, and nothing here closes them off: bare mode, a board option under which a card has no header and its tab carries the mark and the name ([design-system.Rmd#L374-L377](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/vignettes/articles/design-system.Rmd#L374-L377)), and the simplified board of [blockr.dock#489](https://github.com/BristolMyersSquibb/blockr.dock/issues/489), which hides the toggles and the menu.
Both would leave out parts of the header, which the card draws as one component.

</details>
