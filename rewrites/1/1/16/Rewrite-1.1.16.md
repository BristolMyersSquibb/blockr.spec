# Board actions: menus, quick actions and advanced actions
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): board actions, which users trigger from menus, buttons and gestures.
It covers what a board action is and who registers one, the menus that offer board actions, a board action's quick action and advanced action, the roles that tie board actions to commands, and what a frontend and an app give to draw them.
It builds on commands ([Board updates](Rewrite-1.1.2#commands)), plugins ([Plugins](Rewrite-1.1.12)) and `CoreApi` ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)), and takes over an item that the [Backlog](Backlog) held on the entries of a block's menu.
It changes the card's menu of core's basic frontend and the rows and forms of the Edit board plugin, which [blockr.core#569](https://github.com/BristolMyersSquibb/blockr.core/pull/569) built, and shapes the menu of the dock's card ([blockr.dock#602](https://github.com/BristolMyersSquibb/blockr.dock/pull/602)) and the DAG's menus ([Client-drawn DAG](Rewrite-1.3)).
It shapes core's selection ([blockr.core#740](https://github.com/BristolMyersSquibb/blockr.core/issues/740)), the preflights of core's link commands ([blockr.core#741](https://github.com/BristolMyersSquibb/blockr.core/issues/741)), registering and triggering board actions ([blockr.core#742](https://github.com/BristolMyersSquibb/blockr.core/issues/742)), menus and quick actions ([blockr.core#743](https://github.com/BristolMyersSquibb/blockr.core/issues/743)), advanced actions ([blockr.core#744](https://github.com/BristolMyersSquibb/blockr.core/issues/744)), and core's board actions that add a block ([blockr.core#745](https://github.com/BristolMyersSquibb/blockr.core/issues/745)), that create and edit a link or a stack ([blockr.core#746](https://github.com/BristolMyersSquibb/blockr.core/issues/746)) and that edit a block's inputs ([blockr.core#747](https://github.com/BristolMyersSquibb/blockr.core/issues/747)), and the menus of the Edit board plugin's rows ([blockr.core#783](https://github.com/BristolMyersSquibb/blockr.core/issues/783)), besides the batches that add a block beside another ([blockr.core#695](https://github.com/BristolMyersSquibb/blockr.core/issues/695)).
The edits themselves are commands, which stay [Board updates](Rewrite-1.1.2#commands)'s, what a frontend is stays [Plugins](Rewrite-1.1.12#the-frontend)'s, and where the dock draws its card's menu stays [Block cards in the dock](Rewrite-1.2.7#the-menu)'s.

## What must hold

1. Core registers board actions, and so may any plugin, a frontend among them.
   Any plugin triggers any board action by its id under every frontend, as today's extensions fire the dock's actions by id, and triggers the board action that plays a role by the role's id.
2. A board action changes the board only through commands, core's and any package's.
   Each batch that it runs is one undo step of the user ([Board updates](Rewrite-1.1.2#undo)).
   So a pick in its quick action takes one step, and so does its advanced action, which applies all of its edits as one batch once the user applies them.
3. Each board action says which targets it applies to, and every menu of the board, of one of its board objects, of an input of a block or of a selection of them offers each board action that applies to its target.
   The package that opens a menu names the target alone, and neither adds a row nor leaves one out, so that a board action that one package registers shows in the menus that every package opens.
4. Every board action works the same way from every trigger: its quick action shows at the trigger, and its advanced action shows in a place with enough room, opened from the quick action, or at once where the board action has no quick action.
5. The UI of a board action is written once, by the package that registers it, and every trigger reuses it, as core's block picker serves both the card's menu of core's basic frontend and the Edit board plugin today ([The Edit board plugin](Rewrite-1.1.15#where-it-shows)).
6. A frontend needs to draw nothing for board actions to work: core draws every menu and quick action, and shows advanced actions in a dialog of its own, all with blockr.ui's components, in blockr.ui's look under every frontend ([UI kit and design system for the client](Rewrite-1.7#proposal)).
   A frontend may show advanced actions in a place of its own, as may the package that opens a menu, for the advanced actions that the menu opens.
7. A frontend may let the user pin its place for advanced actions, as the dock lets the user pin its actions sidebar today, and so may the package that opens a menu, for a place of its own, as the DAG's panel does ([Drawing the DAG](Rewrite-1.3.2#its-advanced-actions)).
   A pinned place stays open once an advanced action ends, and may move on to another target by the frontend's own rules, as the pinned sidebar follows the DAG's selection today ([blockr.dag#162](https://github.com/BristolMyersSquibb/blockr.dag/issues/162)).
8. Under a lock, a menu offers no board action whose commands the lock refuses, as a frontend draws no control for what a lock fixes ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
9. Commands stay free of UI, so that what runs commands without a user, such as the assistant, never meets a board action ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).
10. An app may swap what core draws for board actions: core's menu, for a module that draws the menus that core runs, and the board action that plays a role, for one that plays the same role, so that an app may draw board actions with a UI kit other than blockr.ui's.
11. The board action that plays a role runs the role's commands alone, in the role's order, with the args that the target fixes, and core refuses a batch that does not, so that a caller that relies on a role gets the same edit whichever board action plays it.

## Today

Board actions are the dock's today, while core and the DAG keep menus of their own:

| Today | Where it goes |
|---|---|
| The dock's actions: `new_action()`, `register_actions()`, `board_actions()` and `action_triggers()`, with twelve actions that add, append, prepend, insert and remove a block, add, edit and remove a link, edit a block's inputs, and add, edit and remove a stack ([blockr.dock R/action-class.R#L43-L172](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/action-class.R#L43-L172)) | Replaced by core's board actions, which run core's commands under every frontend (Core's board actions) |
| Firing them by id: the DAG fires all twelve from its context menu, its toolbar and its canvas ([Places the dock offers plugins](Rewrite-1.2.4#today)), and blockr.outline the three that add a block ([blockr.outline R/outline-srv.R#L137](https://github.com/cynkra/blockr.outline/blob/d3499f4623f956f6691235f90fa84b46b925852c/R/outline-srv.R#L137), [#L193-L197](https://github.com/cynkra/blockr.outline/blob/d3499f4623f956f6691235f90fa84b46b925852c/R/outline-srv.R#L193-L197)) | Replaced by `core.boardActions.trigger()` (The menus of board objects) |
| An extension's own actions, through its method of `board_actions()`, as the DAG draws a link, removes its selection, copies, cuts and pastes ([blockr.dag R/action.R#L202-L212](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/action.R#L202-L212)) | Replaced by the board actions that a plugin class lists ([Client-drawn DAG](Rewrite-1.3)) |
| The actions sidebar, a drawer at the page's edge that the user may pin, in which five of the dock's actions draw a form with an Update button: create and edit a link, edit a block's inputs, which drags a variadic block's inputs into order, and create and edit a stack ([blockr.dock R/sidebar-inputs.R#L1-L8](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/sidebar-inputs.R#L1-L8)), and whose pinned form follows the DAG's selection through `sidebar_owned_by()` | Replaced by advanced actions, which the dock shows in its sidebar, pinned where the user pins it, and where a pinned one follows the selection that core holds, by the dock's rules ([Places the dock offers plugins](Rewrite-1.2.4#places-besides-the-panel)), so that `sidebar_owned_by()` goes |
| The "+" menu, which since [blockr.dock#483](https://github.com/BristolMyersSquibb/blockr.dock/pull/483) adds, appends, prepends and inserts a block where the gesture was, with the block's default id, name and input | Replaced by the quick actions of core's four board actions that add a block, which core draws in its menus (The quick action) |
| The plan of [blockr.dock#544](https://github.com/BristolMyersSquibb/blockr.dock/issues/544), whose pull requests closed unmerged on 2026-11-12 in favour of this rewrite: every action in a menu where the gesture was, second menus at the same spot, multi-selects that apply as the menu closes, a block's options behind the chevron of its row, and no Edit inputs | Carried over as the rules of a quick action, with an advanced action in place of the options behind the chevron, and with Edit inputs kept, as an advanced action alone, which holds its drag (Core's board actions) |
| The DAG's context menu and toolbar, which take entries through the generics `context_menu_items()` and `toolbar_items()`, which only the DAG's extension implements | Replaced by the menus of board objects, which the DAG opens through core ([Client-drawn DAG](Rewrite-1.3)) |
| Core's `edit_block` plugin, with a field for the block's name and buttons to remove the block and to add one before or after it ([R/plugin-block.R#L252-L294](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-block.R#L252-L294)) | Replaced by core's board actions on a block |
| On `js-state`, at `9f431f0`, the card's menu of core's basic frontend, named "Actions of" the block, with Rename, Add block before, Add block after and Remove ([srcts/modules/basic/card.tsx#L126-L160](https://github.com/BristolMyersSquibb/blockr.core/blob/9f431f0f5612a6aa3271ef58dc1037b69cb343df/srcts/modules/basic/card.tsx#L126-L160)), whose two adds open core's block picker, `BlockPicker`, in a dialog ([srcts/picker/picker.tsx#L1-L28](https://github.com/BristolMyersSquibb/blockr.core/blob/9f431f0f5612a6aa3271ef58dc1037b69cb343df/srcts/picker/picker.tsx#L1-L28)), which the Edit board plugin shows too, beside its forms of a link and of a stack ([blockr.core#569](https://github.com/BristolMyersSquibb/blockr.core/pull/569)) | The menu draws core's board actions on a block, the picker becomes the advanced action of the four board actions that add a block, and the forms become the advanced actions of those that create and edit a link or a stack (Core's board actions) |
| On `js-state`, at `6805109`, the rows of the Edit board plugin, whose own buttons rename and remove a block, and edit and remove a link or a stack, through core's commands ([srcts/modules/edit-board/blocks.tsx#L76-L124](https://github.com/BristolMyersSquibb/blockr.core/blob/6805109b4fa67e8899b956620e9b2faca6a12a99/srcts/modules/edit-board/blocks.tsx#L76-L124), [links.tsx#L107-L175](https://github.com/BristolMyersSquibb/blockr.core/blob/6805109b4fa67e8899b956620e9b2faca6a12a99/srcts/modules/edit-board/links.tsx#L107-L175), [stacks.tsx#L104-L169](https://github.com/BristolMyersSquibb/blockr.core/blob/6805109b4fa67e8899b956620e9b2faca6a12a99/srcts/modules/edit-board/stacks.tsx#L104-L169)) | Replaced by the menus of their blocks, links and stacks, which the plugin opens through core, so that a row offers what every menu of its object offers ([The Edit board plugin](Rewrite-1.1.15#what-it-shows)) |

## Proposal

### A board action

A board action is what a user triggers from a menu, a button or a gesture, on the board, on one of its board objects, a plugin among them, on an input of a block, or on a selection of them.
It may gather input from the user, and then it runs commands of any package, core's among them, each batch as one undo step of the user.
It is no command: a command reads the board, returns deltas and asks nobody anything, since the assistant and undo rely on it ([Board updates](Rewrite-1.1.2#commands)), while a board action is the part with a UI, which runs commands.
With illustrative names:

```ts
type Target =                                                   // what a board action acts on
  | { board: true }                                             // the board, as the DAG's canvas offers it
  | BoardObject                                                 // one block, link, stack, board option or plugin, as a notification names it
  | { block: string; input: string }                            // an input of a block, which the store holds no object for, as the DAG's handle of an input offers it, or with "" a variadic block's next place
  | { selection: BoardObject[] };                               // several, as the DAG's selection holds them

interface BoardAction {
  id: string;                                                   // "blockr.core-append_block_action"
  label: string;                                                // what a menu shows, "Append block"
  icon?: string;                                                // SVG markup, as a block class's icon in the block registry, which a button that offers it shows
  detail?(board: Board, target: Target): string | undefined;    // what its row in a menu shows beside the label, as Copy block ID shows the block's id
  on: ("board" | "block" | "input" | "link" | "stack" | "option" | "plugin" | "selection")[];   // the menus that offer it
  category: string;                                             // what a menu may order and divide its rows by: core's "add", "edit", "clipboard" or "remove", or one that packages name, as "export"
  offers?(board: Board, target: Target, lock: CoreApi["lock"]): boolean;   // whether a menu offers it for the target now
  run?(board: Board, target: Target, core: CoreApi): CommandCall[] | void | Promise<CommandCall[] | void>;   // what it does where it asks nothing, which may wait, as for reading the clipboard
  quick?(board: Board, target: Target, core: CoreApi): QuickLevel | undefined | Promise<QuickLevel | undefined>;   // its quick action, which may wait, as for asking R for a block's columns, or none for the target, as Create link's on the board
  advanced?: AdvancedModule;                                    // its advanced action
  role?: string;                                                // the role that it plays, "append_block_role" (Roles)
}

type CommandCall = { id: string; args?: Json };                 // a command of any package
```

A target names a board object as a notification names one ([Notifications, logging and tracing](Rewrite-1.1.14#notifications)), so that a board action may be about any board object, a board option or a plugin too.
So blockr.md could offer Export as HTML on its plugin, while the DAG's menus open on the board, on its blocks, links and stacks, and on a selection of them.
No frontend opens the menu of a plugin or of a board option yet, and none has to: blockr.md would trigger Export as HTML from its own toolbar through `core.boardActions.trigger()`, and a menu on the dock's panels could offer it later, with no change to core.
A board action on a selection takes the kinds that it knows from it, as Create stack takes only the blocks (Core's board actions).
Core hands a board action only targets of the kinds that its `on` names, so that a kind added later, such as a tab group in the dock's state, reaches no board action that does not name it.
A target may also name an input of a block, as `{ block: "b", input: "y" }`, which is no board object, since the store holds no inputs: an input is a slot that the block's class declares ([Board objects](Rewrite-1.1.1#links)).
A variadic block's places are its links, which a target names as it names any link, and its next place is the input `""`, as `{ block: "b", input: "" }`, since a link with an empty input takes the next place of a variadic block.
So the DAG opens a menu on a handle that no link feeds, which offers the board actions whose `on` names inputs, such as Prepend block and Create link, and on a handle that a link feeds the menu of that link (Core's board actions, [Drawing the DAG](Rewrite-1.3.2#nodes)).
A link that the user drags from an input and drops on the DAG's canvas triggers Prepend block on that input, which feeds it, where the DAG and the dock feed the block's first free input today ([blockr.dag R/srv.R#L412-L425](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/srv.R#L412-L425)).

A board action's id is `{pkg}-{name}`, as the ids of commands are, and ends in `_action` by convention, as the dock names its actions today, so that it does not read as a command's id.
Core's board actions keep the names of the dock's actions and the DAG's that they replace, as `blockr.core-edit_link_action` replaces the dock's `edit_link_action` (Core's board actions).
The id ties a board action to no command, since what it runs is what it returns, from `run`, from a row of its quick action or from its advanced action's `done()`: any batch, whose commands may come from any package.
So a package's Duplicate block would run `blockr.core-add_block`, and a `blockr.core-add_link` for each link into the block.
A role ties a board action to commands instead: the one that plays a role runs only the commands that the role names, which core checks (Roles).
A board action that asks for nothing has `run`, which acts at once.
One that asks has a quick action where one or two picks at the trigger finish the edit, as picking a class finishes most adds of a block, and an advanced action where the edit needs room, as a block's id and name do, or a drag that puts a block's inputs in order.
It has both where both hold, as Add block does, and an advanced action alone where the edit takes more picks than two, as Edit inputs does (Core's board actions).
Its `quick` may give no level for a target on which the edit takes more picks than two, so that its advanced action opens at once there.
So Create link's gives none on the board, where the link starts from no block, while on a block it lists the blocks that the new link can join (Core's board actions).
Its `quick` gives a level wherever the board action has no advanced action, since nothing would open otherwise.
Its `run` returns the batch to run, or does itself what needs no command, as Copy block ID puts the block's id on the clipboard, and may return a promise of the batch, as the DAG's Paste reads the clipboard first ([Drawing the DAG](Rewrite-1.3.2#the-dags-board-actions)).

Core registers every board action in JS, and R lists none.
Core's own are those of its table (Core's board actions), and a plugin class lists its own in `boardActions`, which core registers with the class before every board opens, as it registers the class's commands ([Plugins](Rewrite-1.1.12#a-plugin), [UI modules in JS](Rewrite-1.1.7#modules-of-plugin-classes-and-board-options)).
So blockr.md could offer Add to document on every block, which appends the block's output to its document through a command of its own:

```ts
export default {                                   // blockr.md's, from the module that it lists for its plugin class
  state: { schema: mdState, default: { content: "" } },
  commands: [appendEmbed],                         // blockr.md-append_embed, which appends an embed of a block's output to the content
  boardActions: [{
    id: "blockr.md-add_to_document_action",
    label: "Add to document",
    on: ["block"],
    category: "document",                          // a category of blockr.md's own
    run: (board, target) => [{ id: "blockr.md-append_embed", args: { block: target.block } }],   // a block, since on names blocks alone
  }],
  ui: mdUi,
};
```

Every menu of a block then offers it, whether the dock's card, the DAG's node or core's basic frontend opens the menu.
A frontend lists its board actions as any plugin does, since a frontend is a plugin.
Registering a class refuses the whole class where one of its board actions has the id of another board action, an empty `on`, `run` beside `quick` or `advanced`, or none of the three, as it refuses a class whose id another class has ([Board updates](Rewrite-1.1.2#plugins)).

### The menus of board objects

Core decides which board actions a menu offers, not the package that opens the menu.
The package names what the menu is about, its target, and each board action says in `on` and `offers` which targets it applies to.
VS Code fills its menus the same way, from the `when` clause of each command that an extension contributes to a menu ([VS Code](https://code.visualstudio.com/api/references/contribution-points#contributes.menus)), and so does IntelliJ, from each action's `update()` ([IntelliJ](https://plugins.jetbrains.com/docs/intellij/action-system.html#overriding-the-anactionupdate-method)).
So a right click on block `a` in the DAG opens its menu in three steps:

1. The DAG calls `core.boardActions.menu({ block: "a" }, { el, anchor })`.
2. Core keeps each board action, core's or any package's, whose `on` names blocks, and whose `offers` passes for block `a` or which has no `offers`.
3. Core draws those board actions in its menu at the anchor, with blockr.ui's components, or the module that the app names for its menus draws them (What a frontend gives).

The "…" button of the dock's card makes the same call for its block, and so does every other menu of a block, so that every menu of block `a` offers the same board actions, blockr.md's Add to document among them.
Where no board action applies to the target, `menu()` opens nothing, so that no menu shows empty, as on the board's canvas under the board lock.
No menu greys anything out: it leaves out a board action whose `offers` fails, and a board action leaves out of its quick action each row whose commands would fail their preflight, as Create link's does (Core's board actions).
So a board action's `offers` fails wherever its quick action would hold no row, as Create link's does on a block that no new link can join to another, so that no menu offers a board action that leads nowhere.
Core hands the menu its board actions in a fixed order: core's first, in the order of their table (Core's board actions), then each package's, in the order of the app's plugins and as its class lists them.
Of the board actions that name a role, a menu offers only the one that plays the role in the app, in the place of the role's default, so that the app's pick of another changes no menu's order (Roles).
The menu's row for a board action is an item with the board action's label, icon, `detail` for the target and `category`, as an entry of the block registry carries its block class's category ([Block classes in R](Rewrite-1.1.5#cores-classes-and-hooks)).
Core draws every menu of the board, so that the menus of an app look and order alike, whichever package opens one.
Core's menu shows the rows of each category together, with a divider between two categories: those that add, those that edit and those of the clipboard, then those of the categories that packages name, in the order in which they first come, and those that remove last, so that the rows that remove end the menu.
It draws them as the design system draws the block's menu, with each row's icon, its `detail` as meta text at its end, and the rows that remove in the colour of `destructive` ([design-system.Rmd#L1160-L1165](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/vignettes/articles/design-system.Rmd#L1160-L1165)).
So a package's board action that removes something takes the category "remove", and its row then ends the menu in the colour of `destructive`, as core's rows that remove do.
Picking a board action's row opens its quick action as the menu's next level, or its advanced action where it has no quick action for the target, or runs it where it has `run`.

A package that opens a menu of a board object asks core to open it at the point of its trigger, rather than drawing a list of its own:

```ts
boardActions: {                                                 // in CoreApi
  on(target: Target): BoardAction[];                            // what a menu offers for the target, core's board actions first, then each package's
  menu(target: Target, opts: { el: HTMLElement; anchor: DOMRect;
       extend?(deltas: Delta[]): CommandCall[]; notifier?(n: readonly Notification[], action: BoardAction): void;
       advanced?: FrontendModule["advanced"] }): void;                                                        // opens the target's menu at the anchor
  trigger(id: string, target: Target, opts: { el: HTMLElement; anchor?: DOMRect;
          extend?(deltas: Delta[]): CommandCall[]; notifier?(n: readonly Notification[], action: BoardAction): void;
          advanced?: FrontendModule["advanced"] }): Promise<void>;                                            // opens its quick action or its advanced action, or runs it, by a board action's id or a role's
  mountAdvanced(el: HTMLElement, id: string, target: Target, picked?: Json): () => void;   // an advanced action, in room that a plugin gives, by a board action's id or a role's
};
```

In both `menu()` and `trigger()`, `el` is the element that the user triggered from, to which the keyboard's focus returns as the menu closes, and `anchor` is where the menu opens, such as the pointer of a right click, or the box of `el` where `trigger()` is given none.
The promise that `trigger()` returns resolves once the board action ends, as its batch has run or its menu or advanced action has closed without one, and rejects with the refusal where a command of the batch fails.
Both take a `notifier`, which gets the notifications of a refused batch of the board action that they open, with that board action, in place of core raising them, as `commands.run()` does ([Notifications, logging and tracing](Rewrite-1.1.14#taking-a-calls-notifications)).
So the DAG shows a refusal at the node, the link or the point where it opened the menu ([Drawing the DAG](Rewrite-1.3.2#gestures)), and the Edit board plugin heads a refusal with a sentence that names the edit that failed ([The Edit board plugin](Rewrite-1.1.15#each-edit-at-once)).
Both take an `advanced` too, of the shape of the frontend's `advanced` member (What a frontend gives), which core calls in place of the frontend's member for every advanced action that the menu or the trigger opens.
So the package that opens a menu may show the menu's advanced actions in room of its own.
The Edit board plugin does so for the menu of a row, so that the row turns into Edit link's form, as a row turns into its form today ([The Edit board plugin](Rewrite-1.1.15#what-it-shows)).
The DAG does so in a panel beside the object that it opened a menu on, where that panel holds up ([Drawing the DAG](Rewrite-1.3.2#its-advanced-actions)).
A caller that gives no `advanced` leaves the advanced action to the frontend's place.

The card's menu of core's basic frontend, the "…" menu of the dock's card, the DAG's menus of a node, a link, a stack, its canvas and its selection, the rows of the Edit board plugin and its selection ([The Edit board plugin](Rewrite-1.1.15#what-it-shows)), and the rows of blockr.outline all open their menus through core.
The package that opens a menu adds no row to it and leaves none out, since either would make its menu differ from every other menu of the same target.
No menu needs a row for a package's own UI today, and an option of `menu()` can add one later.
A toolbar of the board, such as the DAG's, offers the board actions on the board as buttons, each with its icon and its label as a tooltip, and, while the user has selected something, those on the selection, so that it offers what the menus of the board and of the selection offer.
Each button opens its board action's quick action under itself, or its advanced action where it has no quick action for the target, or runs the board action where it asks nothing.
A gesture outside a menu triggers a board action directly, as a link that the user drops on the DAG's canvas triggers Append block at the drop, through its role, `append_block_role`, and as Backspace in the DAG triggers the removal of its selection, through `remove_selected_role` ([Drawing the DAG](Rewrite-1.3.2#keys)).
A call of `trigger()` runs nothing where the target's menu would not offer the board action, so that those keys remove nothing under the board lock.
The caller's `extend`, which `menu()` takes as `trigger()` does, adds commands of its own to the batch of the board action that the user picks or triggers, whether its `run`, a row of its quick action or its advanced action's `done()` returns that batch.
Core hands `extend` the deltas that the batch will apply, as `core.commands.plan()` returns them ([Board updates](Rewrite-1.1.2#commands)), and runs the commands that `extend` returns after the batch, in the same step.
So the DAG adds the position of a block that Append block adds where the user dropped a link, and of a block or a stack that the menu of its canvas adds, through a row or a form, where the user right-clicked.
It finds them in the deltas' `blocks.add` and `stacks.add`, whichever command adds them and whoever mints their ids, so that a template of blocks that a package's command adds lands there too.
Core's board actions that add a block, a link or a stack mint its id with `core.mintId()` before they return their batch, so that the later commands of the batch can name the object.

### The quick action

A quick action is a level of rows, in which an item may open a further level at the same spot.
Core draws it as a menu at the trigger.
The rows come in kinds that core defines, as it defines the kinds of the storage controls ([Plugins](Rewrite-1.1.12#storage)):

```ts
type QuickLevel = { title?: string; filter?: boolean; picked?: Json; rows: QuickRow[] };   // filter: a field that narrows the rows as the user types; picked: what was picked so far, which the level's open icon hands the advanced action

type QuickRow =
  | { kind: "item"; label: string; heading?: string; icon?: string; detail?: string; category?: BoardAction["category"]; checked?: boolean;
      pick(): CommandCall[] | QuickLevel | Promise<CommandCall[] | QuickLevel>; advanced?: Json }   // runs, or opens the next level, either of which may wait; category: its board action's, in a menu of a board object; checked: the current pick, or a toggle that is on; advanced: what its open icon hands the advanced action
  | { kind: "multi"; label: string; choices: { id: string; label: string; picked: boolean }[];
      apply(picked: string[]): CommandCall[] }      // ticks rows, and applies them as the menu closes
  | { kind: "text"; label: string; value?: string; check?(value: string): string | undefined;
      submit(value: string): CommandCall[] };       // a field, as for a name
```

An item with `checked` shows a check at the end of its row, as the design system marks the current pick and a toggle that is on ([design-system.Rmd#L1096-L1112](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/vignettes/articles/design-system.Rmd#L1096-L1112)).
So the DAG's Layout checks the current direction, spacing and placement, and Snap to grid while snapping is on ([Drawing the DAG](Rewrite-1.3.2#the-dags-board-actions)).

Core runs every menu by these rules, in logic that draws nothing, which core's menu, or the module that the app names for its menus, draws and the `CoreApi` for tests drives, so that the rules are written once and a test needs no browser (Testing).
They come from the menus that [blockr.dock#544](https://github.com/BristolMyersSquibb/blockr.dock/issues/544) planned:

1. Picking an item whose `pick` returns a batch closes the menu and runs the batch as one step of the user.
2. Picking an item whose `pick` returns a level replaces the menu with that level at the same spot.
   Escape goes back a level, or closes the menu from the first level.
3. A multi applies its picks as the menu closes by a click outside or by Tab, and drops them on Escape.
4. A text row refuses a value in place, with what its `check` returns, and submits on Enter.
5. Where the board action has an advanced action, every level of its quick action shows the open icon at its top right: a box with an arrow out of its top right corner.
   An item that gives `advanced` shows the same icon at its end, and a click elsewhere on the item picks it.
   A click on an icon opens the advanced action with the level's `picked` or the item's `advanced`, and with the text in the level's filter.
   The icon says that the advanced action opens in another place, as blockr.ui's `open` icon, drawn after Bootstrap's `box-arrow-up-right`, marks the tool with which a menu opens its list somewhere fuller and takes the filter's text along ([blockr.ui inst/assets/icons/open.svg](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/icons/open.svg), [design-system.Rmd#L1083-L1087](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/vignettes/articles/design-system.Rmd#L1083-L1087)).
6. The filter narrows the rows by their labels and details as the user types, and Enter picks the first row left.
7. Where `quick` or `pick` returns a promise, the menu shows at the same spot that it is loading until the promise resolves, and the error's message in place of the rows where the promise rejects.
   Escape goes back as from any level, and drops what the promise brings later.

### The advanced action

An advanced action is a module that meets the contract of a UI module ([UI modules in JS](Rewrite-1.1.7#the-contract)), with `CoreApi` in place of a host:

```ts
interface AdvancedModule {
  render(args: { el: HTMLElement; core: CoreApi; target: Target; picked?: Json; filter?: string; signal: AbortSignal;
                 done(calls?: CommandCall[], opts?: { notifier?(n: readonly Notification[]): void }): Promise<void> }): () => void;   // done() runs the batch as one step and closes, or only closes, and rejects where the batch is refused
}
```

It holds every option of its board action, as the block picker holds a new block's class, id, name and input.
Opened from a quick action, it gets as `picked` the level's `picked` or the item's `advanced`, whichever open icon the user clicked, and as `filter` the text in that level's filter.
So the block picker opens on what the user typed in the quick action of Add block, as the design system's add menu hands it to the dock's block browser ([design-system.Rmd#L1199-L1207](https://github.com/BristolMyersSquibb/blockr.ui/blob/e14e8310481e98b156871bf96669b41cb88c8435/vignettes/articles/design-system.Rmd#L1199-L1207)).
An advanced action runs nothing before the user applies it, and then hands all of its edits to `done()` as one batch, which runs as one step.
That holds for one that adds an object, whose id cannot change once the object is on the board, and for one that edits: Edit link, Edit inputs and Edit stack each have an Apply button, as the dock's actions sidebar has an Update button today.
The user's edits in one advanced action, such as a new source for one input and the drops that reorder the others, then undo together, and the board never evaluates a state that the user only passed through on the way to the one they applied.
Where the store or the command registry refuses the batch, the promise that `done()` returns rejects and the advanced action stays open, so that it shows why close to the button that applied it and keeps what the user gave, as every plugin with a UI shows what fails of what the user did in it ([Notifications, logging and tracing](Rewrite-1.1.14#where-a-notification-shows)).
It takes the batch's notifications through the `notifier` of `done()`, so that core raises none.

The frontend shows an advanced action in a place with enough room: at least 420 px wide, or as wide as the window where the window is narrower, as the dock's sidebar is by default ([blockr.dock inst/assets/css/sidebar-server.css#L5-L6](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/sidebar-server.css#L5-L6)).
Where that place is, and whether the user may pin it, is the frontend's choice.
The dock shows an advanced action in its sidebar, which the user may pin, and core shows one in a modal dialog, as core's basic frontend shows its picker today.
The package that opens a menu may show the menu's advanced actions in room of its own instead, through the `advanced` of `menu()` (The menus of board objects).
A place shows one advanced action for one target at a time, and core keeps no rules of pinning a place or of following the selection.
A frontend that pins its place follows the selection by rules of its own, through what its `advanced` member gets (What a frontend gives).
So the dock's pinned sidebar follows the DAG's selection, as a pinned form of today's actions sidebar does ([blockr.dag#162](https://github.com/BristolMyersSquibb/blockr.dag/issues/162), [Places the dock offers plugins](Rewrite-1.2.4#places-besides-the-panel)).
Core holds what the user selected in `core.selection`, as it holds focus ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)): whatever selects board objects sets it, as the DAG does as the user selects nodes, links and stacks, and the DAG opens the menu of a selection with what it holds.
Where a board object that an advanced action's target names leaves the board, core ends the advanced action, as a `done()` without a batch does, so that no form edits what the board no longer holds.

A plugin with room of its own may mount an advanced action there through `mountAdvanced()`, as the Edit board plugin shows the advanced actions of Add block, Create link and Create stack on the board in its sections ([The Edit board plugin](Rewrite-1.1.15#what-it-shows)).
There `done()` runs the batch and core renders the advanced action again, so that the plugin's picker is ready for the next block, as it is today ([blockr.core#569](https://github.com/BristolMyersSquibb/blockr.core/pull/569)).

### Roles

A role is an edit that callers rely on, which one board action plays in each app: the board action that the role names by default, such as core's Append block, or one that the app picks, such as a package's Append block drawn with another UI kit.
The role ties the board action that plays it to commands: it names the commands that each of the board action's batches runs, in a fixed order, for each board object or input of the target, and which of their args the target fixes.
So a board action that an app swaps in does what the one it replaces does, and only its UI differs.
Eclipse splits its commands the same way: a command declares a behaviour by its id, which key bindings name, any plug-in may contribute a handler that implements it, and a command has at most one active handler at a time ([org.eclipse.ui.handlers](https://help.eclipse.org/latest/topic/org.eclipse.platform.doc.isv/reference/extension-points/org_eclipse_ui_handlers.html)).
With illustrative names:

```ts
interface Role {
  id: string;                                                   // "append_block_role", which names no package
  on: BoardAction["on"];                                        // the targets of the board action that plays it
  default: string;                                              // the board action that plays it where the app picks none, "blockr.core-append_block_action"
  advanced?: true;                                              // where a caller mounts the advanced action of the board action that plays it
  commands: {                                                   // what each batch of that board action runs, in this order
    id: string;                                                 // a command of any package, "blockr.core-add_link"
    each?: "block" | "input" | "link" | "stack";                // once for each board object or input of this kind that the target holds, as a selection holds blocks and a block its inputs
    optional?: true;                                            // at most once, rather than exactly once, and for each where it has each
    fixes?(board: Board, target: Target, args: Json): boolean;  // whether the args keep what the target fixes, as the from of add_link on Append block
  }[];
}
```

A role's id is global and names no package, as a board option's does, since one edit has one role, whichever package defines it ([Board options and blockr options](Rewrite-1.1.13#defining-a-board-option)).
It ends in `_role` by convention, so that it reads as neither a board action's id nor a command's.
Core defines a role for each of its board actions that runs commands (Core's board actions), and a plugin class lists roles of its own in `roles`, beside `boardActions`, which core registers with the class ([Plugins](Rewrite-1.1.12#a-plugin)).
Registering a class refuses the whole class where one of its roles has the id of another package's role, and names both packages.
The role's inputs are the args of its commands that the target does not fix, as Append block's are the new block's class, id and name and the input that the link feeds, so that the board action that plays it gathers them, in whatever UI it draws.
A board action that runs no command, such as Copy block ID, plays no role, since no command would tie it to its edit.

In each app, one board action plays each role: the one that the blockr option `board_actions` picks for the role, or else the role's `default`.
The blockr option holds, for each role whose player the app picks, the id of that board action, which an R option gives, since an environment variable holds no list, and which the client reads through `CoreApi.blockrOption()` ([Board options and blockr options](Rewrite-1.1.13#blockr-options)):

```r
options(blockr.board_actions = list(append_block_role = "mykit-append_block_action"))
```

A board action plays a role only where it names the role in `role`.
One that names a role that it does not play in the app is in no menu, and `trigger()` and `mountAdvanced()` run nothing for its id, so that every caller meets one board action for the role.
Once every module is registered, core checks the board action that plays each role: that it names the role in `role`, names the role's targets alone in `on`, and has an advanced action where the role has `advanced`.
Where the app's pick fails the check, or no package registers it, core opens no board and shows in its place an error that names the pick, the role and what failed.
The blockr option is the app's rather than a board's, so a wrong pick breaks every board that the app could open, and the app refuses them all rather than run with a role that its author set to another board action.
The same holds where `board_action_menu` names a module that no package offers.
Core asks R for `board_actions` and `board_action_menu` as soon as R has answered its `hello`, as it asks for the blockr options that its scheduler reads, so that it knows who plays each role and which module draws its menus before the board opens ([Board options and blockr options](Rewrite-1.1.13#blockr-options)).

Core checks each batch of the board action that plays a role, whether its `run`, a row of its quick action or its advanced action's `done()` returns it, before the command registry plans it.
The batch holds the role's commands alone, in their order: each exactly once, or at most once where it has `optional`, and so for each board object or input of its kind that the target holds where it has `each`, and each with args that pass its `fixes`.
So Append block's batch holds `add_block`, then an `add_link` from the target block, while a batch that also removed a block, or linked the new block to another, is refused.
Core refuses a batch that fails the check before anything runs, as a fault of the board action's package, naming the role and the call that broke it.
The commands that the caller's `extend` adds come after the batch and fall outside the check (The menus of board objects).
Then the command registry checks each call's args against its command's JSON Schema and runs its preflight, as it does for every batch ([Board updates](Rewrite-1.1.2#commands)).

A caller that relies on what a board action does triggers or mounts its role, by the role's id, which `trigger()` and `mountAdvanced()` take where they take a board action's, so that it meets the app's pick (The menus of board objects).
So the DAG triggers `append_block_role` or `prepend_block_role` where the user drops a link on its canvas ([Drawing the DAG](Rewrite-1.3.2#gestures)) and `remove_selected_role` on Backspace ([Drawing the DAG](Rewrite-1.3.2#keys)), blockr.outline triggers the roles that add a block, and the Edit board plugin mounts the advanced actions of `add_block_role`, `add_link_role` and `add_stack_role` in its sections ([The Edit board plugin](Rewrite-1.1.15#what-it-shows)).
Core's roles are these:

| Role | On | Its commands, of `blockr.core`, in order | What the target fixes | Advanced action |
|---|---|---|---|---|
| `add_block_role` | The board | `add_block` | Nothing | Needed, since the Edit board plugin mounts it |
| `append_block_role` | A block | `add_block`, then `add_link` | The `from` of `add_link`, the block | Not needed |
| `prepend_block_role` | A block, or an input | `add_block`, then `add_link` | The `to` of `add_link`, the block, and on an input its `input` too | Not needed |
| `insert_block_role` | A link | `add_block`, `add_link`, then `change_link` | The `from` of `add_link`, the link's source, and the link that `change_link` changes | Not needed |
| `add_link_role` | A block, an input, or the board | `add_link` | On a block, the `from` or the `to` of `add_link`, the block, and on an input its `to` and its `input` | Needed, since the Edit board plugin mounts it |
| `add_stack_role` | A block, a selection or the board | `add_stack` | The blocks that the target holds, which the new stack takes | Needed, since the Edit board plugin mounts it |
| `rename_role` | A block or a stack | `rename_block` for a block, `rename_stack` for a stack | The block or the stack | Not needed |
| `edit_link_role` | A link | `change_link`, then `move_link`, each at most once | The link | Not needed |
| `edit_inputs_role` | A block with inputs | `remove_link`, `change_link`, `add_link`, then `move_link`, each at most once for each of the block's inputs | The block and the input, which each link goes into | Not needed |
| `edit_stack_role` | A stack | `change_stack` | The stack | Not needed |
| `add_to_stack_role` | A block, or a selection | `change_stack` | The blocks that the target holds, which the stack takes in | Not needed |
| `remove_block_role`, `remove_link_role` and `remove_stack_role` | A block, a link or a stack | `remove_block`, `remove_link` or `remove_stack` | The block, the link or the stack | Not needed |
| `remove_selected_role` | A selection | `remove_link` for each link, then `remove_block` for each block and `remove_stack` for each stack | The selection's links, blocks and stacks | Not needed |

### What a frontend gives

A frontend draws nothing for board actions to work: core draws every menu and every quick action with blockr.ui's components, and shows every advanced action in a dialog of its own.
Its module may give one member, so that advanced actions show in a place of its own:

```ts
interface FrontendModule {
  // render() and show(), as on Plugins
  advanced?(args: { id: string; title: string; target: Target; mount(el: HTMLElement, target?: Target): () => void; close(): void }): (deltas?: Delta[]) => void;   // shows an advanced action in the frontend's place, and returns what core calls once done() ends it
}
```

Core calls `advanced` with the board action's id, a title, the target and a `mount()`, through which the frontend has core render the advanced action in its place, and the frontend calls `close()` as the user closes the place.
The `advanced` member returns a function, which core calls once `done()` ends the advanced action, with the deltas of the batch that `done()` ran, or with none where it ran none.
The frontend then closes its place, or keeps it open and mounts the advanced action again, as a place that the user pinned does.
It may pass `mount()` another target, on which core renders the same board action where the target's menu would offer it, as `trigger()` checks, so that a pinned place may move on to a block that the batch added, or follow `core.selection`.
A `mount()` on another target renders the module afresh, so that a module never sees its target change.
A package that opens a menu may hand `menu()` or `trigger()` a function of the same shape, which core then calls in place of the frontend's (The menus of board objects).

Core's menu and dialog draw with blockr.ui's `Menu` and `Dialog`, which blockr.ui builds from React Aria's, and take blockr.ui's look under every frontend, as core's other UIs do ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend), [UI kit and design system for the client](Rewrite-1.7#proposal)).
So do the advanced actions of core's board actions, which show under every frontend, in the dock's sidebar too.
The dock draws its other menus with blockr.ui's `Menu` as well, so its menus of board actions look like its other menus.
The dock gives `advanced`: it shows advanced actions in its sidebar, which the user may pin, and where a pinned one follows the selection by the dock's rules ([Places the dock offers plugins](Rewrite-1.2.4#places-besides-the-panel)).
Core's basic frontend gives no member, since core's dialog is its own place.

An app that draws with a UI kit other than blockr.ui's draws the menus of board actions with it too, through the blockr option `board_action_menu`, which names a module that a package offers others, by its id ([Drawing the board](Rewrite-1.1.8#what-a-package-declares-in-r)).
Core loads the module through `CoreApi.module()` as the board opens, and hands it each menu that it opens, as the logic that runs the menu by the rules of a quick action and draws nothing (The quick action).
With illustrative names:

```ts
interface MenuModule {                                          // the module that the blockr option board_action_menu names
  render(args: { menu: OpenMenu; el: HTMLElement; anchor: DOMRect }): () => void;   // draws an open menu at the anchor, and returns what core calls as the menu closes
}

interface OpenMenu {                                            // a menu that core runs by the rules of a quick action, and that draws nothing
  get(): ShownLevel;                                            // the level that the menu shows now
  subscribe(fn: () => void): () => void;                        // calls fn whenever that changes
  pick(row?: number): void;                                     // a click or Enter on a row, by its index, or with none, Enter in the filter
  openAdvanced(row?: number): void;                             // a click on an item's open icon, by its index, or with none, on the level's
  tick(row: number, choice: string): void;                      // a click on a choice of a multi
  type(value: string, row?: number): void;                      // the filter's text, or a text row's value, as the user types
  escape(): void;                                               // Escape
  close(): void;                                                // a click outside the menu, or Tab
}

type ShownLevel = {                                             // a level as the menu shows it
  title?: string;
  filter?: string;                                              // the filter's text, where the level has a filter
  advanced: boolean;                                            // whether the level shows the open icon, as it does where the board action has an advanced action
  back: boolean;                                                // whether Escape goes back a level, rather than closing the menu
  loading: boolean;                                             // while a promise of quick or pick is pending
  error?: string;                                               // the message that it rejected with
  rows: (                                                       // the rows that the filter leaves, without their functions
    | { kind: "item"; label: string; heading?: string; icon?: string; detail?: string; category?: BoardAction["category"]; checked?: boolean; advanced: boolean }   // advanced: whether it shows the open icon
    | { kind: "multi"; label: string; choices: { id: string; label: string; picked: boolean }[] }
    | { kind: "text"; label: string; value: string; refusal?: string }   // refusal: what check returns for the value
  )[];
};
```

The module draws the level that `get()` returns, draws it again whenever `subscribe()` calls it, and calls a member of the open menu for each thing that the user does, while it keeps its own keys for moving between rows.
It may show the rows of a level in any order, as by their categories, and passes `pick()` a row's index in `rows`, whatever the order it shows.
Core calls the functions of the board action's rows, `pick()`, `apply()`, `check()` and `submit()`, and runs the batch that they return, with the caller's `extend`, as one step.
For a click on an open icon, the level's or an item's, core closes the menu and opens the advanced action with the level's `picked` or the item's `advanced`, and with the filter's text.
So the module never sees a board action's functions, never runs a command and writes none of the rules of a quick action, only its look.
Core calls the function that `render()` returned as the menu closes, whatever closed it, and returns the keyboard's focus to `el`.
The open menu's members do not rely on `this`, and `get()` returns the same object until the menu changes, so that a module in React reads it with `useSyncExternalStore(menu.subscribe, menu.get)`.
Core ships tests that a package runs against its module, which open a menu through it and pick rows by their ARIA roles and labels, as a user would, to check that the module passes on what the user does.
No board action changes with the module, since a quick action is data, and core's own menu is such a module, which draws with blockr.ui's components.

### Core's board actions

Core registers a board action for each of the dock's twelve actions, and four more: Rename and Copy block ID, from the menu of the dock's card, Remove on a selection, from the DAG's actions, and Add to stack, which puts blocks into a stack that the board holds, so that Create stack only adds stacks and each of the two runs one command.
Each takes the label that today's menus give it, such as Create link, whose command is labelled Add link.
Its id is under `blockr.core` and keeps the name of the action that it replaces, as `blockr.core-add_link_action` keeps the dock's `add_link_action`, so that only Rename, Copy block ID and Add to stack take new ones.
Each but Copy block ID is the default of one of core's roles, which an app may give another board action (Roles).
Core hands them to a menu in the order of this table:

| Board action, with its id | On | Category | Quick action | Advanced action | Role |
|---|---|---|---|---|---|
| Add block, `add_block_action` | The board | Add | A filter, and a row for each block class under the heading of its category, which adds a block of that class with an id that core mints and the class's name | The block picker on its own: class, id and name | `add_block_role` |
| Append block, `append_block_action` | A block | Add | The block classes that have an input, each of which appends a block of that class through its first free input | The picker after the block: class, input, id and name | `append_block_role` |
| Prepend block, `prepend_block_action` | A block with an input that no link feeds, or such an input | Add | The block classes, each of which adds a block that feeds the input, or the block's first free one | The picker before the block | `prepend_block_role` |
| Insert block, `insert_block_action` | A link | Add | The block classes that have an input | The picker on the link, a fourth mode of the picker | `insert_block_role` |
| Create link, `add_link_action` | A block that a new link can join to another, an input that no link feeds, or the board, where it holds such a block | Add | On a block, the blocks that it can feed, and those that can feed it, without closing a cycle, then the input, where the block that the link goes into has several free ones, as [blockr.dock#549](https://github.com/BristolMyersSquibb/blockr.dock/pull/549) had them, on an input the blocks that can feed it without closing a cycle, and on the board none, since a link from no block takes three picks, so that its row opens its advanced action at once | The Edit board plugin's form of a link, starting from the block or the input, or from no block on the board | `add_link_role` |
| Create stack, `add_stack_action` | A block, a selection that holds a block, or the board | Add | A text row with a name that no other stack has, which adds a stack of the target's blocks, or of none on the board, in a colour that no other stack has | The Edit board plugin's form of a stack, with the blocks given, or with none on the board | `add_stack_role` |
| Rename, `rename_action` | A block or a stack | Edit | A text row with the name | None | `rename_role` |
| Edit link, `edit_link_action` | A link | Edit | Change source…, Move to input… and, into a variadic block, Rename input…, as blockr.dock#549 had them | The form of a link, editing it, with an Apply button | `edit_link_role` |
| Edit inputs, `edit_inputs_action` | A block with inputs | Edit | None, since moving an input would take three picks at the trigger, so that its row opens its advanced action at once | The block's inputs in their order, each with its source, which the user changes or removes, and which the user drags into another order and renames where the block is variadic, as the dock's actions sidebar has them today, with an Apply button | `edit_inputs_role` |
| Edit stack, `edit_stack_action` | A stack | Edit | Colour… and Blocks…, as [blockr.dock#550](https://github.com/BristolMyersSquibb/blockr.dock/pull/550) had them | The form of a stack, editing it, with an Apply button | `edit_stack_role` |
| Add to stack, `add_to_stack_action` | A block, or a selection that holds a block, where the board holds a stack | Edit | The board's stacks, which the blocks join | None | `add_to_stack_role` |
| Copy block ID, `copy_block_id_action` | A block | Clipboard | None, since it acts at once | None | None, since it runs no command |
| Remove block, Remove link and Remove stack, `remove_block_action`, `remove_link_action` and `remove_stack_action` | A block, a link or a stack | Remove | None, since each acts at once | None | `remove_block_role`, `remove_link_role` and `remove_stack_role` |
| Remove, `remove_selected_action` | A selection | Remove | None, since it acts at once, removing every block, link and stack of the selection in one step | None | `remove_selected_role` |

Create link's quick action lists only the blocks for which the preflight of `blockr.core-add_link` passes, through `core.commands.preflight()`.
That preflight refuses a link that would close a cycle, join a block to itself or feed an input that a link feeds already, with a sentence that says which.
So a menu offers no such link, the assistant's edit fails before any command does work, and a user who drops such a link in the DAG learns why ([Drawing the DAG](Rewrite-1.3.2#gestures)).
The store keeps its own check of the same rules behind the preflight ([Board objects](Rewrite-1.1.1#what-the-store-checks)).

The card's menu of core's basic frontend says "Add block before" and "Add block after" today, and takes the labels of the board actions here, "Prepend block" and "Append block", which the dock's menus and the DAG's use today, so that every menu agrees.
Under the board lock, every one of core's board actions but Copy block ID fails its `offers`, since the store refuses what they run ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).
Other packages register board actions of their own, as the DAG does for copy, cut and paste and for laying the board out again ([Client-drawn DAG](Rewrite-1.3)).

### Testing

The `CoreApi` for tests opens the menu of a target and picks its rows by label, since a quick action is data, so a test of a board action needs no browser ([Drawing the board](Rewrite-1.1.8#testing)).
It tests an advanced action as it tests any module.
It checks every batch of a board action that plays a role against the role, as core does, so that a package's test fails where its board action strays from the role that it names.
Core tests the rules of a quick action once, on the logic that runs every menu and draws nothing.

## Open questions

None.

<details><summary>Notes for implementers</summary>

The pull requests of [blockr.dock#544](https://github.com/BristolMyersSquibb/blockr.dock/issues/544), [blockr.dock#549](https://github.com/BristolMyersSquibb/blockr.dock/pull/549) to [blockr.dock#553](https://github.com/BristolMyersSquibb/blockr.dock/pull/553), and [blockr.ui#99](https://github.com/BristolMyersSquibb/blockr.ui/pull/99), keep their branches, with menus opened where the gesture was, their second levels, their multi-selects and their tests, which the quick actions of core's board actions take over.
The drag that reorders a variadic block's inputs is in `R/sidebar-inputs.R` of blockr.dock at `655e323`, with its script and styles, which the advanced action of Edit inputs takes over.
Core's menu draws blockr.ui's open icon, and core's board actions carry blockr.ui's icons, as SVG markup in `icon`, such as those in the shapes of today's `trash` for the board actions that remove and `plus` for those that add ([blockr.ui inst/assets/icons](https://github.com/BristolMyersSquibb/blockr.ui/tree/e14e8310481e98b156871bf96669b41cb88c8435/inst/assets/icons)), since core's menu shows a row's icon, a toolbar's button shows it too, and a menu module draws it whatever kit it draws with.
The check of a batch against a role sits in core's runtime beside the command registry, which takes the batch once the check has passed, and the `CoreApi` for tests runs the same check.
The `mount()` that core hands `advanced` is `mountAdvanced()` with the board action's id given, and core plans the batch of a `done()` once, for the caller's `extend` and for the function that `advanced` returned, and then applies its deltas.

On `js-state`, at `9f431f0`, core's block picker has a mode for each of `add_block`, `append_block` and `prepend_block` ([srcts/picker/picker.tsx#L43-L47](https://github.com/BristolMyersSquibb/blockr.core/blob/9f431f0f5612a6aa3271ef58dc1037b69cb343df/srcts/picker/picker.tsx#L43-L47)), and Insert block gives it a fourth, on a link.
With [blockr.core#695](https://github.com/BristolMyersSquibb/blockr.core/issues/695), its modes after and before a block run batches of `add_block` and `add_link` instead, as [Board updates](Rewrite-1.1.2#commands) has them.
On `js-state`, at `7fd739c`, the preflight of `blockr.core-add_link` checks only that the first block exists and that the second has a free input, and lets a named input pass unchecked (`linkable()` in `srcts/commands/core.ts`), while the store refuses a cycle once the link is added.
A preflight says why it refuses by throwing the `refusal()` of its context, with one sentence per failure, which `commands.run()` rejects with, while `commands.preflight()` answers `false` (`srcts/commands/commands.ts`).
The picker leaves an id that the user does not give to the command ([#L11-L12](https://github.com/BristolMyersSquibb/blockr.core/blob/9f431f0f5612a6aa3271ef58dc1037b69cb343df/srcts/picker/picker.tsx#L11-L12)), so as an advanced action it mints the id itself, through `mintId()`, as every board action of core's that adds an object does (The menus of board objects).
Copy block ID copies through the document's copy command where the page has no clipboard API, and raises an error notification of the code `copy_failed` where the browser refuses both, as the dock's card does since [blockr.dock#602](https://github.com/BristolMyersSquibb/blockr.dock/pull/602).
The Edit board plugin's forms of a link and of a stack are in `srcts/modules/edit-board/links.tsx` and `srcts/modules/edit-board/stacks.tsx`, and the dialog of core's basic frontend, which is at most 576 px wide, is `Dialog` in `srcts/modules/basic/ui.tsx`.

</details>
