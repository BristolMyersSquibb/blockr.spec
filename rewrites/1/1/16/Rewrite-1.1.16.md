# Board actions: menus, quick actions and advanced actions
Status: review. Design for [Client-owned board state](Rewrite-1.1).

One of the API proposals for the client-owned board ([Client-owned board state](Rewrite-1.1)): board actions, which users trigger from menus, buttons and gestures.
It covers what a board action is and who registers one, the menus that offer board actions, a board action's quick action and advanced action, and what a frontend gives to draw them.
It builds on commands ([Board updates](Rewrite-1.1.2#commands)), plugins ([Plugins](Rewrite-1.1.12)) and `CoreApi` ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)), and takes over an item that the [Backlog](Backlog) held on the entries of a block's menu.
It changes the card's menu of core's basic frontend and the forms of the Edit board plugin, which [blockr.core#569](https://github.com/BristolMyersSquibb/blockr.core/pull/569) built, and shapes the menu of the dock's card ([blockr.dock#602](https://github.com/BristolMyersSquibb/blockr.dock/pull/602)) and the DAG's menus ([Client-drawn DAG](Rewrite-1.3)).
The edits themselves are commands, which stay [Board updates](Rewrite-1.1.2#commands)'s, what a frontend is stays [Plugins](Rewrite-1.1.12#the-frontend)'s, and where the dock draws its card's menu stays [Block cards in the dock](Rewrite-1.2.7#the-menu)'s.

## What must hold

1. Any package registers board actions, core, a frontend and every other plugin alike, and any plugin triggers any board action by its id under every frontend, as today's extensions fire the dock's actions by id.
2. A board action changes the board only through commands, core's and any package's, and each use of a board action that runs commands is one undo step of the user ([Board updates](Rewrite-1.1.2#undo)).
3. Every menu of the board or of one of its blocks, links or stacks offers the board actions that apply to it, whichever package draws the menu, so that a board action that one package registers shows in all of them, in the same order.
4. Every board action works the same way from every trigger: its quick action shows at the trigger, and where the board action has more options, the quick action opens its advanced action, which shows in a place with enough room.
5. The UI of a board action is written once, by the package that registers it, and every trigger reuses it, as core's block picker serves both the card's menu of core's basic frontend and the Edit board plugin today ([The Edit board plugin](Rewrite-1.1.15#where-it-shows)).
6. A frontend needs to draw nothing for board actions to work: core draws the menus and the quick actions, and shows advanced actions in a dialog of its own, while a frontend may draw menus and quick actions in its own look, and show advanced actions in a place of its own, pinned or not.
7. Under a lock, a menu offers no board action whose commands the lock refuses, as a frontend draws no control for what a lock fixes ([Drawing the board](Rewrite-1.1.8#what-core-gives-plugins)).
8. Commands stay free of UI, so that what runs commands without a user, such as the assistant, never meets a board action ([The assistant's tools](Rewrite-1.4.2#the-edit-tool)).

## Today

Board actions are the dock's today, while core and the DAG keep menus of their own:

| Today | Where it goes |
|---|---|
| The dock's actions: `new_action()`, `register_actions()`, `board_actions()` and `action_triggers()`, with twelve actions that add, append, prepend, insert and remove a block, add, edit and remove a link, edit a block's inputs, and add, edit and remove a stack ([blockr.dock R/action-class.R#L43-L172](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/action-class.R#L43-L172)) | Replaced by core's board actions, which run core's commands under every frontend (Core's board actions) |
| Firing them by id: the DAG fires all twelve from its context menu, its toolbar and its canvas ([Places the dock offers plugins](Rewrite-1.2.4#today)), and blockr.outline the three that add a block ([blockr.outline R/outline-srv.R#L137](https://github.com/cynkra/blockr.outline/blob/d3499f4623f956f6691235f90fa84b46b925852c/R/outline-srv.R#L137), [#L193-L197](https://github.com/cynkra/blockr.outline/blob/d3499f4623f956f6691235f90fa84b46b925852c/R/outline-srv.R#L193-L197)) | Replaced by `core.boardActions.trigger()` (The menus of board objects) |
| An extension's own actions, through its method of `board_actions()`, as the DAG draws a link, removes its selection, copies, cuts and pastes ([blockr.dag R/action.R#L202-L212](https://github.com/BristolMyersSquibb/blockr.dag/blob/898a097ab404db92901c23efd52d6422e43ce4dc/R/action.R#L202-L212)) | Replaced by the board actions that a plugin class lists ([Client-drawn DAG](Rewrite-1.3)) |
| The actions sidebar, a drawer at the page's edge that the user may pin, in which five of the dock's actions draw a form with an Update button: create and edit a link, edit a block's inputs, which drags a variadic block's inputs into order, and create and edit a stack ([blockr.dock R/sidebar-inputs.R#L1-L8](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/R/sidebar-inputs.R#L1-L8)), and whose pinned form follows the DAG's selection through `sidebar_owned_by()` | Replaced by advanced actions, which the dock shows in its sidebar, pinned where the user pins it, and which follow the focused block (The advanced action), so that `sidebar_owned_by()` goes |
| The "+" menu, which since [blockr.dock#483](https://github.com/BristolMyersSquibb/blockr.dock/pull/483) adds, appends, prepends and inserts a block where the gesture was, with the block's default id, name and input | Replaced by the quick actions of core's four board actions that add a block, which the dock draws with its menus (What a frontend gives) |
| The plan of [blockr.dock#544](https://github.com/BristolMyersSquibb/blockr.dock/issues/544), whose pull requests closed unmerged on 2026-11-12 in favour of this rewrite: every action in a menu where the gesture was, second menus at the same spot, multi-selects that apply as the menu closes, a block's options behind the chevron of its row, and no Edit inputs | Carried over as the rules of a quick action, with an advanced action in place of the options behind the chevron, and with Edit inputs kept, its drag in its advanced action (The quick action) |
| The DAG's context menu and toolbar, which take entries through the generics `context_menu_items()` and `toolbar_items()`, which only the DAG's extension implements | Replaced by the menus of board objects, which the DAG draws through core ([Client-drawn DAG](Rewrite-1.3)) |
| Core's `edit_block` plugin, with a field for the block's name and buttons to remove the block and to add one before or after it ([R/plugin-block.R#L252-L294](https://github.com/BristolMyersSquibb/blockr.core/blob/da3fcb499549043d02d0300e05c7161f528c8729/R/plugin-block.R#L252-L294)) | Replaced by core's board actions on a block |
| On `js-state`, at `9f431f0`, the card's menu of core's basic frontend, named "Actions of" the block, with Rename, Add block before, Add block after and Remove ([srcts/modules/basic/card.tsx#L126-L160](https://github.com/BristolMyersSquibb/blockr.core/blob/9f431f0f5612a6aa3271ef58dc1037b69cb343df/srcts/modules/basic/card.tsx#L126-L160)), whose two adds open core's block picker, `BlockPicker`, in a dialog ([srcts/picker/picker.tsx#L1-L28](https://github.com/BristolMyersSquibb/blockr.core/blob/9f431f0f5612a6aa3271ef58dc1037b69cb343df/srcts/picker/picker.tsx#L1-L28)), which the Edit board plugin shows too, beside its forms of a link and of a stack ([blockr.core#569](https://github.com/BristolMyersSquibb/blockr.core/pull/569)) | The menu draws core's board actions on a block, the picker becomes the advanced action of the four board actions that add a block, and the forms become the advanced actions of those that create and edit a link or a stack (Core's board actions) |

## Proposal

### A board action

A board action is what a user triggers from a menu, a button or a gesture, on the board or on one of its blocks, links or stacks.
It may gather input from the user, and then it runs commands of any package, core's among them, as one undo step of the user.
It is no command: a command reads the board, returns deltas and asks nobody anything, since the assistant and undo rely on it ([Board updates](Rewrite-1.1.2#commands)), while a board action is the part with a UI, which runs commands.
With illustrative names:

```ts
type Target =                                                   // what a board action acts on
  | { board: true }                                             // the board, as the DAG's canvas offers it
  | { block: BlockId } | { link: LinkId } | { stack: StackId }  // one board object, as a notification names it
  | { selection: { blocks: BlockId[]; links: LinkId[]; stacks: StackId[] } };   // several, as the DAG's selection holds them

interface BoardAction {
  id: string;                                                   // "blockr.core-append_block_action"
  label: string;                                                // what a menu shows, "Append block"
  icon?: string;                                                // SVG markup, as a block class's icon in the block registry, which a button that offers it shows
  on: ("board" | "block" | "link" | "stack" | "selection")[];   // the menus that offer it
  group: "add" | "edit" | "clipboard" | "remove";               // where those menus show it
  offers?(board: Board, target: Target, lock: Lock): boolean;   // whether a menu offers it for the target now
  run?(board: Board, target: Target, core: CoreApi): CommandCall[] | void | Promise<CommandCall[] | void>;   // what it does where it asks nothing, which may wait, as for reading the clipboard
  quick?(board: Board, target: Target, core: CoreApi): QuickLevel;           // its quick action
  advanced?: AdvancedModule;                                    // its advanced action
}

type CommandCall = { id: string; args?: Json };                 // a command of any package
```

A board action's id is `{pkg}-{name}`, as the ids of commands are, and ends in `_action` by convention, as the dock names its actions today, so that it does not read as a command's id.
Core's board actions take the name of the command that each runs, as `blockr.core-append_block_action` runs `blockr.core-append_block`.
The id ties a board action to no command, since what it runs is what it returns, from `run`, from a row of its quick action or from its advanced action's `done()`: any batch, whose commands may come from any package.
So a package's Duplicate block would run `blockr.core-add_block`, and a `blockr.core-add_link` for each link into the block.
A board action has either `run`, which acts at once, or a quick action, and it has an advanced action only beside a quick action, so that every board action that asks for input starts at its trigger.
Its `run` returns the commands to run, or does itself what needs no command, as Copy block ID puts the block's id on the clipboard, and may return a promise of them, as the DAG's Paste reads the clipboard first ([Drawing the DAG](Rewrite-1.3.2#the-dags-board-actions)).

Core registers its own board actions (Core's board actions), and a plugin class lists its own in `boardActions`, which core registers with the class, as it registers the class's commands ([Plugins](Rewrite-1.1.12#a-plugin)).
A frontend lists its board actions as any plugin does, since a frontend is a plugin.
Registering refuses an id that another board action has, and a board action whose `on` is empty.

### The menus of board objects

The menu of the board, of a block, of a link, of a stack or of a selection offers each board action whose `on` names the target's kind, and whose `offers` passes for the target or which has no `offers`.
It shows them by their groups, in this order: those that add, those that edit, those of the clipboard and those that remove, with a divider between two groups.
Within a group, core's board actions come first, then each package's in the order of the app's plugins.
So every menu of a block offers the same board actions in the same order, whoever draws it.

Whoever draws a menu of a board object asks core to open it at the point of its trigger, rather than drawing a list of its own:

```ts
boardActions: {                                                 // in CoreApi
  on(target: Target): BoardAction[];                            // what a menu offers for the target, in order
  menu(target: Target, opts: { el: HTMLElement; anchor: DOMRect;
       extend?(calls: CommandCall[]): CommandCall[] }): void;        // opens the target's menu at the anchor
  trigger(id: string, target: Target, opts: { el: HTMLElement; anchor?: DOMRect;
          extend?(calls: CommandCall[]): CommandCall[] }): Promise<void>;     // opens its quick action, or runs it
  mountAdvanced(el: HTMLElement, id: string, target: Target, picked?: Json): () => void;   // an advanced action, in room that a plugin gives
  select(target: Target): void;                                 // a board object that the user selected, which a pinned advanced action follows
};
```

The card's menu of core's basic frontend, the "…" menu of the dock's card, the DAG's menus of a node, a link, a stack, its canvas and its selection, and the rows of blockr.outline all open the menus that core draws.
The package that draws a menu adds to it no row that edits the board, since such a row would show in its own menu alone, and adds rows only for its own UI.
A toolbar of the board, such as the DAG's, offers the board actions on the board as buttons, each with its icon and its label as a tooltip, and, while the user has selected something, those on the selection, so that it offers what the menus of the board and of the selection offer.
Each button opens its board action's quick action under itself, or runs the board action where it asks nothing.
A gesture outside a menu triggers a board action directly, as a link that the user drops on the DAG's canvas triggers Append block at the drop, and as Backspace in the DAG triggers the removal of its selection.
The caller's `extend`, which `menu()` takes as `trigger()` does, adds commands of its own to the batch of the board action that the user picks or triggers, whether its `run`, a row of its quick action or its advanced action's `done()` returns that batch.
So the DAG adds the position of a block that Append block adds where the user dropped a link, and of a block or a stack that the menu of its canvas adds, through a row or a form, where the user right-clicked.
Core's board actions that add a block, a link or a stack mint its id before they return their command, so that `extend` can name the object.

### The quick action

A quick action is one level of rows, which core draws as a menu at the trigger, or the frontend through its hook (What a frontend gives).
The rows come in kinds that core defines, as it defines the kinds of the storage controls ([Plugins](Rewrite-1.1.12#storage)):

```ts
type QuickLevel = { title?: string; filter?: boolean; rows: QuickRow[] };   // filter: a field that narrows the rows as the user types

type QuickRow =
  | { kind: "item"; label: string; heading?: string; icon?: string; detail?: string; disabled?: boolean;
      pick(): CommandCall[] | QuickLevel; advanced?: Json }    // runs, or opens the next level; advanced: what its chevron hands the advanced action
  | { kind: "multi"; label: string; choices: { id: string; label: string; picked: boolean }[];
      apply(picked: string[]): CommandCall[] }                 // ticks rows, and applies them as the menu closes
  | { kind: "text"; label: string; value?: string; check?(value: string): string | undefined;
      submit(value: string): CommandCall[] }                   // a field, as for a name
  | { kind: "advanced"; label: string; picked?: Json };        // "Advanced…", which opens the advanced action
```

These rules hold wherever a quick action shows, and come from the menus that [blockr.dock#544](https://github.com/BristolMyersSquibb/blockr.dock/issues/544) planned:

1. Picking an item whose `pick` returns commands closes the menu and runs them as one step of the user.
2. Picking an item whose `pick` returns a level replaces the menu with that level at the same spot.
   Escape goes back a level, or closes the menu from the first level.
3. A multi applies its picks as the menu closes by a click outside or by Tab, and drops them on Escape.
4. A text row refuses a value in place, with what its `check` returns, and submits on Enter.
5. An item that gives `advanced` shows a chevron at its end, which opens the board action's advanced action with that value, as the chevron of a row in the dock's "+" menu was to open a block's options ([blockr.ui#99](https://github.com/BristolMyersSquibb/blockr.ui/pull/99)).
   A row of the kind `advanced` opens it with what was picked so far.
6. The filter narrows the rows by their labels and details as the user types, and Enter picks the first row left.

### The advanced action

An advanced action is a module that meets the contract of a UI module ([UI modules in JS](Rewrite-1.1.7#the-contract)), with `CoreApi` in place of a host:

```ts
interface AdvancedModule {
  render(args: { el: HTMLElement; core: CoreApi; target: Target; picked?: Json; signal: AbortSignal;
                 done(calls?: CommandCall[]): void }): () => void;   // done() runs the commands as one step and closes, or only closes
}
```

It holds every option of its board action, as the block picker holds a new block's class, id, name and input.
One that adds an object runs nothing before the user submits it, since an object's id cannot change once the object is on the board, and then hands its commands to `done()`, which runs them as one step.
One that edits applies each edit as the user makes it, through `core.commands.run()`, as the Edit board plugin does ([The Edit board plugin](Rewrite-1.1.15#each-edit-at-once)).
So it needs no Update button, and each drop that reorders a block's inputs is one step.

The frontend shows an advanced action in a place with enough room: at least 420 px wide, or as wide as the window where the window is narrower, as the dock's sidebar is by default ([blockr.dock inst/assets/css/sidebar-server.css#L5-L6](https://github.com/BristolMyersSquibb/blockr.dock/blob/655e323c990649818627ff0ba216717396e00d5c/inst/assets/css/sidebar-server.css#L5-L6)).
Where that place is, and whether the user may pin it, is the frontend's choice.
The dock shows an advanced action in its sidebar, which the user may pin, and core shows one in a modal dialog, as core's basic frontend shows its picker today.
Where the frontend pins the place, the advanced action stays open and follows the selection, as a pinned form of today's actions sidebar follows the DAG's ([blockr.dag#162](https://github.com/BristolMyersSquibb/blockr.dag/issues/162)):

1. Whatever selects a board object tells core through `core.boardActions.select()`, as the DAG does as the user selects a node, a link or a stack, and core counts a block that gets focus as selected too ([Plugins](Rewrite-1.1.12#what-a-frontend-offers-other-plugins)).
2. Core hands the target to the pinned advanced action where its board action's `on` names the target's kind and its `offers` passes for the target, so that a pinned Edit link follows the links that the user selects.
3. Otherwise the selection changes nothing, so that a selection never swaps one board action's advanced action for another's, which only opening a board action or closing the place does.

A plugin with room of its own may mount an advanced action there through `mountAdvanced()`, as the Edit board plugin shows the advanced action of Add block in its section of blocks.

### What a frontend gives

A frontend draws nothing for board actions to work: core draws every menu and every quick action with components of its own, and shows every advanced action in a dialog of its own.
Its module may give two members, so that board actions look like the rest of the frontend:

```ts
interface FrontendModule {
  // render() and show(), as on Plugins
  menu?(args: { level: QuickLevel; el: HTMLElement; anchor: DOMRect; back?(): void; close(): void }): void;   // draws a menu or a level of a quick action, in the frontend's look
  advanced?(args: { title: string; mount(el: HTMLElement): () => void; close(): void }): void;             // shows an advanced action in the frontend's place
}
```

A frontend that gives `menu` keeps the rules of a quick action (above), which core ships as tests that its own menu passes and that the frontend runs against its own (Testing).
The dock gives both members: it draws menus as the design system draws them ([Block cards in the dock](Rewrite-1.2.7#the-menu)), and shows advanced actions in its sidebar, which the user may pin.
Core's basic frontend gives neither, since core's menu and dialog are its own look.
Core's menu and dialog build on Tailwind CSS and take their colours, fonts and radii from Tailwind's theme variables, so that a frontend may also restyle them without giving either member, as blockr.ui may under the dock ([Drawing the board](Rewrite-1.1.8#cores-basic-frontend)).

### Core's board actions

Core registers a board action for each of its commands that a menu offers, under the command's label, and one more, Copy block ID, which edits nothing.
Each board action's id is the command's with `_action` after it, such as `blockr.core-insert_block_action`.

| Board action | On | Quick action | Advanced action | Commands, of `blockr.core` |
|---|---|---|---|---|
| Add block | The board | A filter, and a row for each block class under the heading of its category, which adds a block of that class with an id that core mints and the class's name | The block picker on its own: class, id and name | `add_block` |
| Append block | A block | The block classes that have an input, each of which appends a block of that class through its first free input | The picker after the block: class, input, id and name | `append_block` |
| Prepend block | A block with an input that no link feeds | The block classes, each of which adds a block that feeds the block's first free input | The picker before the block | `prepend_block` |
| Insert block | A link | The block classes that have an input | The picker on the link, a fourth mode of the picker | `insert_block` |
| Rename | A block or a stack | A text row with the name | None | `rename_block`, `rename_stack` |
| Create link | A block | The blocks that it can feed, and those that can feed it, without closing a cycle, then the input, where the block that the link goes into has several free ones, as [blockr.dock#549](https://github.com/BristolMyersSquibb/blockr.dock/pull/549) had them | The Edit board plugin's form of a link, starting from the block | `add_link` |
| Edit link | A link | Change source…, Move to input… and, into a variadic block, Rename input…, as blockr.dock#549 had them | The form of a link, editing it | `change_link`, `move_link` |
| Edit inputs | A block with inputs | The block's inputs, each with Rename…, Move to… and Remove | The block's inputs in their order, which the user drags into another, as the dock's actions sidebar has them today | `change_link`, `move_link`, `remove_link` |
| Create stack | A block or a selection | The board's stacks, which the block joins, and New stack | The Edit board plugin's form of a stack, with the blocks given | `add_stack`, `change_stack` |
| Edit stack | A stack | Colour… and Blocks…, as [blockr.dock#550](https://github.com/BristolMyersSquibb/blockr.dock/pull/550) had them | The form of a stack, editing it | `change_stack` |
| Copy block ID | A block | None, since it acts at once | None | None |
| Remove block, Remove link and Remove stack | A block, a link or a stack | None, since each acts at once | None | `remove_block`, `remove_link`, `remove_stack` |
| Remove | A selection | None, since it acts at once, removing every block, link and stack of the selection in one step | None | `remove_block`, `remove_link`, `remove_stack` |

The card's menu of core's basic frontend says "Add block before" and "Add block after" today, and takes the commands' labels here, "Prepend block" and "Append block", which the dock's menus and the DAG's use today, so that every menu agrees.
Under the board lock, every one of core's board actions but Copy block ID fails its `offers`, since the store refuses what they run ([Locked boards and the properties of blocks](Rewrite-1.1.11#three-locks)).
Other packages register board actions of their own, as the DAG does for copy, cut and paste and for laying the board out again ([Client-drawn DAG](Rewrite-1.3)).

### Testing

The `CoreApi` for tests opens the menu of a target and picks its rows by label, since a quick action is data, so a test of a board action needs no browser ([Drawing the board](Rewrite-1.1.8#testing)).
It tests an advanced action as it tests any module.
Core ships the tests that its own menu passes for the rules of a quick action, and a frontend that gives `menu` runs them against its own.

## Open questions

None.

<details><summary>Notes for implementers</summary>

The pull requests of [blockr.dock#544](https://github.com/BristolMyersSquibb/blockr.dock/issues/544), [blockr.dock#549](https://github.com/BristolMyersSquibb/blockr.dock/pull/549) to [blockr.dock#553](https://github.com/BristolMyersSquibb/blockr.dock/pull/553), and [blockr.ui#99](https://github.com/BristolMyersSquibb/blockr.ui/pull/99), keep their branches, with menus opened where the gesture was, their second levels, their multi-selects and their tests, which the quick actions of core's board actions take over.
The drag that reorders a variadic block's inputs is in `R/sidebar-inputs.R` of blockr.dock at `655e323`, with its script and styles, which the advanced action of Edit inputs takes over.

On `js-state`, at `9f431f0`, core's block picker has a mode for each of `add_block`, `append_block` and `prepend_block` ([srcts/picker/picker.tsx#L43-L47](https://github.com/BristolMyersSquibb/blockr.core/blob/9f431f0f5612a6aa3271ef58dc1037b69cb343df/srcts/picker/picker.tsx#L43-L47)), and Insert block gives it a fourth, on a link.
The Edit board plugin's forms of a link and of a stack are in `srcts/modules/edit-board/links.tsx` and `srcts/modules/edit-board/stacks.tsx`, and the dialog of core's basic frontend, which is at most 576 px wide, is `Dialog` in `srcts/modules/basic/ui.tsx`.

</details>
