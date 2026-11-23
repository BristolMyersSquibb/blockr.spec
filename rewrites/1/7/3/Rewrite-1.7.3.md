# The components of blockr.ui: the first set, `bound` and their tests
Status: review. Design for [UI kit and design system for the client](Rewrite-1.7).

One of the designs for blockr.ui as the client's UI kit ([UI kit and design system for the client](Rewrite-1.7)): the components that blockr.ui offers every package, after React Aria's Tailwind starter kit, of which the first set moves from core's React SDK on `js-state`.
It covers the interface `Bound`, through which an input takes the value that it shows and submits, and how the components are tested.
It shapes the items of 1.7's Work list that move the components to blockr.ui and import them in the dock and the assistant ([UI kit and design system for the client](Rewrite-1.7#work)).
How a package builds against the components and how they load belong to [Building on blockr.ui](Rewrite-1.7.4), and the jobs that they draw with belong to [The theme's variables](Rewrite-1.7.2).
The binding's rules, core's `useValue()` and where overlays open belong to [UI modules in JS](Rewrite-1.1.7).
The block's mark and status dot, which read core's statuses and categories, belong to [Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot).

## What must hold

1. Every component of core's React SDK on `js-state` moves to blockr.ui with its name and its props, so that a UI that draws with one changes only its import, from `@blockr/core/react` to `@blockr/ui`.
   The one exception is `Stack`, which becomes `FormLayout` ([The first set](#the-first-set)).
2. A component needs nothing of another blockr package: an input takes its value through `Bound`, an interface of blockr.ui's, and knows no host, no block and no board option ([UI kit and design system for the client](Rewrite-1.7#what-must-hold)).
3. An input that takes a `bound` keeps the contract's rules for the value through it: it shows the value that the `bound` gives, except while the user types, and it submits only as the user acts ([UI modules in JS](Rewrite-1.1.7#the-contract)).
4. Every component draws with the theme's jobs alone, never with a colour of Tailwind's palette, and opens its overlays in React Aria's portal, never in the browser's top layer ([UI modules in JS](Rewrite-1.1.7#react)).
5. The components' tests run in blockr.ui, without core.

## Today

On `js-state`, at `79507c4`, core's React SDK holds the components, built after React Aria's Tailwind starter kit ([starters/tailwind/src](https://github.com/adobe/react-spectrum/tree/react-aria-components%401.22.1/starters/tailwind/src)).
They take 6,473 lines of TypeScript, without their 16 files of tests, and `@blockr/core/react` exports them beside core's hooks ([srcts/react/index.ts](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/srcts/react/index.ts)).
By folder, the parts of React Aria that they draw with take 258 lines, the inputs 4,634, the overlays 619, the layout 407, the trees 246, the table 174, the grid list 73, and drag and drop 62.

They import five things from the rest of core:

- The type `Bound`, from core's hooks ([srcts/react/hooks.ts#L61-L74](https://github.com/BristolMyersSquibb/blockr.core/blob/79507c4047268930ead351863d588035488fc887/srcts/react/hooks.ts#L61-L74)).
- The type `Json`.
- The classes in `srcts/styles`, under core's prefix, `bc`.
- The helpers `jsonEqual()` and `own()`.
- The helper `strings()` of core's binding, which reads an answer of R's as strings.

They draw with core's theme, and some of them with colours of Tailwind's palette, as [The theme's variables](Rewrite-1.7.2#today) counts.

## Proposal

### The first set

The first set is every component that core's React SDK holds on `js-state`, each with React Aria's props and those that the starter kit adds, such as `label`:

| Group | Components |
|---|---|
| Fields | `TextField`, `NumberField`, `SearchField`, `TokenField` with `Token`, `Field`, `Form` and `FormLayout` |
| Picks | `Select`, `ComboBox` and `ListBox`, each with its items and sections, `Autocomplete` with `useFilter`, `Checkbox`, `CheckboxGroup`, `Radio`, `RadioGroup`, `Switch`, `Slider`, `ToggleButton`, `ToggleButtonGroup`, and `TagGroup` with `Tag` |
| Dates and times | `DateField`, `TimeField`, `DatePicker`, `DateRangePicker`, `Calendar` and `RangeCalendar` |
| Colours | `ColorField`, `ColorPicker`, `ColorArea`, `ColorSlider`, `ColorWheel`, `ColorThumb`, `ColorSwatch`, and `ColorSwatchPicker` with its items |
| Buttons and files | `Button`, `FieldButton`, `DropZone`, `FileTrigger` and `Text`, with the icons `ChevronRight` and `Tick` |
| Overlays | `Modal`, `Dialog`, `DialogTrigger`, `AlertDialog`, `Sheet`, `Popover`, `Menu` with its items, sections and triggers, `SubmenuTrigger`, `CommandPalette`, `Tooltip` with `TooltipTrigger`, `Toast` with its content, queue and region, `Heading`, `Keyboard` and `Focusable` |
| Layout | `Disclosure` with its header, panel and group, `Tabs` with `TabList`, `Tab` and `TabPanel`, `Toolbar`, `Separator`, `Breadcrumbs` with `Breadcrumb`, `Link`, `Meter` and `ProgressBar` |
| Collections | `Table` with its header, body, columns, rows and cells, `Tree` with `TreeItem`, `NavigationTree` with its parts, `GridList` with its parts, and `useDragAndDrop` with `DropIndicator` and `DragButton` |

Each keeps its name and its props, so that core's UIs, the dock's and the assistant's change only their imports.
The one exception is `Stack`, which lays out the controls of a UI one below the other.
In blockr, a stack is a group of blocks ([Board objects](Rewrite-1.1.1#stacks)), so the component becomes `FormLayout`, as Shopify's Polaris names the component that does the same ([FormLayout.tsx#L18](https://github.com/Shopify/polaris/blob/3f7954ae42fabf26d63cee68c23ceebfd7ef0972/polaris-react/src/components/FormLayout/FormLayout.tsx#L18)).
It pairs with `Form` without being it: `Form` is React Aria's form element with its validation, while `FormLayout` only arranges controls, so a block's UI uses it without a form.
The overlays stack at the theme's `--bk-z-index-overlay` ([The theme's variables](Rewrite-1.7.2#the-defaults)).

Core keeps what binds a value or reads core's own types, and draws it with blockr.ui's components:

- Its hooks, and the helpers `reactModule()` and `outputRenderer()` ([UI modules in JS](Rewrite-1.1.7#react)).
- The function `controls()`, which draws bound inputs for a module written without React.
- The component `NotificationList`, which draws core's notifications.
- The block's mark and status dot ([Drawing the board](Rewrite-1.1.8#the-blocks-mark-and-the-status-dot)).

The components bring along what they use of the rest of core, as blockr.ui's own: the type `Json`, the classes of `srcts/styles` under `bk:`, and the helpers `jsonEqual()`, `own()` and `strings()`.
Core keeps its own copies for its own code.

Each component is rewritten onto the theme's jobs as it moves, in place of the colours of Tailwind's palette, as a component of the starter kit is when it is copied in ([UI kit and design system for the client](Rewrite-1.7#designed-against-tailwind)).
A component that blockr.ui adds later follows the starter kit wherever the kit has one.

### The interface `Bound`

An input takes the value that it shows and submits through its prop `bound`, an object of the interface `Bound`, which blockr.ui defines and core's `useValue()` returns ([UI modules in JS](Rewrite-1.1.7#react)):

```ts
export interface Bound {
  readonly value: Json | undefined;          // the value as the input last showed it
  readonly error: string | null;             // why the last submit was refused, which the input shows below itself
  get(): Json | undefined;                   // the value as it is held now
  commit(value: Json): Promise<boolean>;     // submits a pick at once, and resolves with whether it was taken
  unset(): Promise<boolean>;                 // clears the value, as for an arg without a default
  type(value: Json | undefined): void;       // takes what the user typed, which is submitted once the user pauses
  flush(): void;                             // submits what the user typed at once, as on Enter or as the user leaves the input
}
```

The interface names no host, no block and no board option, so the components hold nothing of core's.
What implements it keeps the contract's rules, as core's binding does, which `useValue()` makes ([UI modules in JS](Rewrite-1.1.7#the-contract)):

1. The binding holds a value of the host's, and gives it to the input as `value`.
2. The input calls `commit()` as the user picks, `type()` as the user types, and `flush()` as the user presses Enter or leaves the input.
3. The binding waits for the user's pause before it submits what the user typed.
4. While the user types, the binding gives the input no value that the host announces.
5. Where the host refuses a submit, the binding gives the input why, as `error`, and the input shows it below itself.

So every input keeps the rules alike, whoever implements `Bound`.
An input without a `bound` takes React Aria's value props, as `value` with `onChange`, or `defaultValue`, and keeps its value itself, as a search field does whose value no host holds ([Glossary](Glossary)).
The interface leaves out the `release()` of core's binding, which core's hook calls as the input unmounts, so that an input never ends a binding that its caller made.

### Testing

The components' tests move with them and run in blockr.ui's CI, on Vitest and happy-dom, with the gates that every package's client has ([State in JS](Rewrite-1#conventions)).
Beside the components, blockr.ui ships a stub of `Bound` for tests.
The stub holds a value, records each value that an input commits, types and flushes, and refuses a submit with an error where a test asks it to.
So blockr.ui tests its inputs without core, and a package tests a component apart from any host.
The preset's check fails blockr.ui's own build where a component names a colour of Tailwind's palette, as it fails any package's build ([Building on blockr.ui](Rewrite-1.7.4#the-build-preset)).
A test that needs a host, such as one of an input bound to a block's state arg, lives in core, with core's stubs of the hosts and `useValue()` ([UI modules in JS](Rewrite-1.1.7#testing)).

## Open questions

None.

<details><summary>Notes for implementers</summary>

- The components at `79507c4` are in `srcts/aria`, `srcts/inputs`, `srcts/overlays`, `srcts/layout`, `srcts/dnd`, `srcts/gridlist`, `srcts/table` and `srcts/tree`, with the classes that they share in `srcts/styles`, and their tests beside them as `*.test.tsx`.
- The helpers that read a `Bound` move with the inputs: `useTyped()` in `inputs/inputs.tsx`, `useBoundDate()` in `inputs/bounddate.ts` and `useDragged()` in `inputs/colors.ts`.
- Core's `Binding`, in `srcts/binding/binding.ts`, has `release()` beside the members of `Bound`, and `PAUSE`, the 500 ms that it waits after the last keystroke before it submits.

</details>
