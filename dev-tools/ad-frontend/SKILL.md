---
name: ad-frontend
description: Alter Domus UI component library (Photon Design System). Use this skill when building any frontend UI at Alter Domus — whether in Angular, React, Next.js, or any other framework. It documents all available components, their properties, events, and usage patterns.
license: Apache-2.0
---

# Alter Domus Frontend UI Components (Photon Design System)

The Alter Domus UI component library implements the **Photon Design System** and provides 75+ components covering forms, layout, data display, charts, navigation, and more. This skill is the reference for building **any** Alter Domus frontend — regardless of framework.

Official packages exist for both Angular and React:

- **Angular**: `@alterdomus-digital/ad-ui-components-angular`
- **React**: `@alterdomus/ad-ui-components-react` (repo: `AlterDomus/ad-ui-components-react`)

Both packages share the same design tokens (`--dns-*` CSS custom properties), SCSS mixins, and visual output.

## Key Facts

- **Design System**: Photon
- **Angular package**: `@alterdomus-digital/ad-ui-components-angular`
- **React package**: `@alterdomus/ad-ui-components-react`
- **Styling**: CSS custom properties (design tokens), SCSS
- **All class names** are prefixed with `dns-` (e.g. `dns-button`, `dns-select`)

## Installation

### Angular

```bash
npm install @alterdomus-digital/ad-ui-components-angular --registry=https://npm.pkg.github.com
```

Import the global styles in your `styles.scss`:

```scss
@import '@alterdomus-digital/ad-ui-components-angular/styles.scss';
```

### React / Next.js

```bash
npm install @alterdomus/ad-ui-components-react --registry=https://npm.pkg.github.com
```

Import the global styles in your root layout or `_app.tsx`:

```tsx
import '@alterdomus/ad-ui-components-react/dist/styles.css';
```

## Usage

### Angular

```typescript
import { ButtonComponent } from '@alterdomus-digital/ad-ui-components-angular';

@Component({
  standalone: true,
  imports: [ButtonComponent],
  template: `<dns-button label="Click me" type="primary" (buttonClick)="onClick($event)"></dns-button>`
})
export class MyComponent {}
```

### React / Next.js

```tsx
import { Button } from '@alterdomus/ad-ui-components-react';

export function MyComponent() {
  return (
    <Button
      label="Click me"
      type="primary"
      size="large"
      onButtonClick={(e) => console.log('clicked', e)}
    />
  );
}
```

All Angular `@Input()` properties map directly to React props. All `@Output()` events map to `on*` callback props (e.g. `(buttonClick)` becomes `onButtonClick`). The React package also provides:

- **SharedProvider** — React Context replacing Angular's SharedService (wrap your app with `<SharedProvider>`)
- **Hooks** — `useClickOutside`, `useResizeObserver`, `useKeyboardNavigation`, `useTooltip`, `useScrollbar`
- **Radix UI primitives** — Checkbox, Radio, Switch, Slider, Tabs, Accordion, Dialog, Tooltip use Radix UI for accessibility
- **@floating-ui/react** — Dropdown/tooltip positioning

Use the component reference tables below as the single source of truth for props, defaults, and behavior in any framework.

## Component Selectors

All component selectors are prefixed with `dns-`. For example: `dns-button`, `dns-select`, `dns-card-component`.

---

## Components Reference

### Buttons

#### `dns-button` — ButtonComponent

Primary button component with multiple appearances and variants.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | `string` | `''` | Button text |
| `type` | `BtnType` | `'primary'` | `'primary'` \| `'secondary'` \| `'tertiary'` \| `'destructive-primary'` \| `'destructive-tertiary'` \| `'approval-primary'` \| `'icon'` |
| `buttonVariant` | `ButtonVariant` | `'text'` | `'text'` \| `'textWithIcon'` \| `'iconOnly'` |
| `variant` | `ButtonVariantType` | `'default'` | `'default'` \| `'inverse'` \| `'standard'` |
| `size` | `BtnSize` | `'large'` | `'large'` \| `'small'` \| `'mini'` |
| `appearance` | `BtnAppearance` | `'notification'` | `'notification'` \| `'organization'` |
| `disabled` | `boolean` | `false` | Disable the button |
| `loader` | `boolean` | `false` | Show loading spinner |
| `icon` | `string` | `''` | Icon name |
| `leftIcon` | `string` | `''` | Left-side icon name |
| `rightIcon` | `string` | `''` | Right-side icon name |
| `iconPosition` | `ButtonIconPosition` | `'left'` | `'left'` \| `'right'` \| `'both'` |
| `badgeText` | `string` | `''` | Badge text overlay |
| `variation` | `IconVariations` | `'regular'` | Icon variation style |
| `tabIndexValue` | `number` | `-1` | Tab index |

| Output | Type | Description |
|--------|------|-------------|
| `buttonClick` | `EventEmitter<Event>` | Emitted on button click |

```html
<dns-button label="Submit" type="primary" size="large" (buttonClick)="onSubmit($event)"></dns-button>
<dns-button label="Delete" type="destructive-primary" icon="trash" buttonVariant="textWithIcon"></dns-button>
<dns-button icon="plus" buttonVariant="iconOnly" type="secondary"></dns-button>
```

#### `dns-neutral-button` — neutralButtonComponent

Compact neutral button, typically used for close/dismiss actions.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `size` | `NeutralButtonSize` | `'small'` | Button size |
| `iconName` | `string` | `'x'` | Icon to display |
| `isDisabled` | `boolean` | — | Disable state |
| `clickable` | `boolean` | — | Whether clickable |

| Output | Type | Description |
|--------|------|-------------|
| `btnClick` | `EventEmitter<Event>` | Click event |

#### `dns-dual-button` — DualButtonComponent

Split button with primary action and dropdown for secondary actions.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | `string` | `'Label'` | Primary button label |
| `type` | `string` | `'primary'` | `'primary'` \| `'secondary'` |
| `size` | `string` | `'large'` | `'large'` \| `'small'` \| `'mini'` |
| `disabled` | `boolean` | — | Disable state |
| `items` | `any[]` | `[]` | Dropdown menu items |

| Output | Type | Description |
|--------|------|-------------|
| `OnClicked` | `EventEmitter<any>` | Primary button click |
| `dropdownItemClicked` | `EventEmitter<string>` | Dropdown item selected |

#### `dns-button-group` — ButtonGroupComponent

Group of buttons rendered together.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `buttonGroupItems` | `any[]` | `[]` | Array of button configurations |

| Output | Type | Description |
|--------|------|-------------|
| `buttonClick` | `EventEmitter<unknown>` | Button click within group |

#### `dns-toggle-button` — ToggleButtonComponent

Material toggle button group with text/icon variants.

Variations: `'text'` | `'icon'` | `'icons'` | `'borderless'`

---

### Form Inputs

#### `dns-text-field` — TextFieldComponent

Text input field with label, validation, and icon support.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | `string` | `''` | Field label |
| `placeholder` | `string` | `''` | Placeholder text |
| `size` | `TextFieldSize` | `'large'` | `'large'` \| `'small'` |
| `variation` | `TextFieldVariant` | `'simple'` | `'simple'` \| other variants |
| `disabled` | `boolean` | `false` | Disable the field |
| `error` | `boolean` | `false` | Show error state |
| `supportingText` | `string` | `''` | Helper text below field |
| `errorMessage` | `string` | `''` | Error message text |
| `value` | `string` | — | Field value (setter) |
| `isCloseEle` | `boolean` | `false` | Show clear button |

| Output | Type | Description |
|--------|------|-------------|
| `valueChange` | `EventEmitter<string>` | Value changed |
| `inputChange` | `EventEmitter<string>` | Input event |
| `clearEvent` | `EventEmitter<void>` | Clear button clicked |
| `focusEvent` | `EventEmitter<void>` | Field focused |
| `blurEvent` | `EventEmitter<void>` | Field blurred |

```html
<dns-text-field label="Email" placeholder="Enter email" size="large"
  [error]="hasError" errorMessage="Invalid email"
  (valueChange)="onValueChange($event)">
</dns-text-field>
```

#### `dns-select` — SelectComponent

Dropdown select with single/multiple selection, search, and custom display.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | `string` | `''` | Select label |
| `items` | `any[]` | `[]` | Options array |
| `size` | `SelectSize` | `'large'` | `'large'` \| `'small'` \| `'small-with-label'` |
| `variation` | `SelectVariation` | `'filled'` | `'filled'` \| `'outline'` \| `'standard'` |
| `multiple` | `boolean` | `false` | Enable multi-select |
| `isDisabled` | `boolean` | `false` | Disable the select |
| `placeholder` | `string` | `''` | Placeholder text |
| `error` | `boolean` | `false` | Show error state |
| `supportingText` | `string` | `''` | Helper text |
| `errorMessage` | `string` | `''` | Error text |
| `emitAsObject` | `boolean` | `false` | Emit full object instead of value |
| `displayPropertyName` | `string` | `''` | Property name to display from items |
| `defaultValue` | `string` | `''` | Pre-selected value |
| `selectedValue` | `string` | `''` | Current selected value |
| `clearIcon` | `boolean` | `false` | Show clear icon |
| `isPanelOpen` | `boolean` | `false` | Control panel open state |

| Output | Type | Description |
|--------|------|-------------|
| `selectionChange` | `EventEmitter<string \| number \| null>` | Selection changed |
| `fetchOptions` | `EventEmitter<void>` | Request to fetch options (lazy loading) |
| `dropdownToggled` | `EventEmitter<boolean>` | Dropdown opened/closed |

```html
<dns-select label="Country" [items]="countries" placeholder="Select country"
  variation="filled" (selectionChange)="onCountryChange($event)">
</dns-select>
```

#### `dns-select-group` — SelectGroupComponent

Grouped select fields rendered together.

| Input | Type | Default |
|-------|------|---------|
| `selectItems` | `any[]` | `[]` |

#### `dns-checkbox` — CheckboxComponent

Material checkbox with label, error state, and indeterminate support.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | `string` | `''` | Checkbox label |
| `checked` | `boolean` | `true` | Checked state |
| `disabled` | `boolean` | `false` | Disable checkbox |
| `hasError` | `boolean` | `false` | Error state |
| `indeterminate` | `boolean` | `false` | Indeterminate state |
| `labelPosition` | `CheckboxLabelPosition` | `'right'` | `'right'` \| `'left'` |
| `supportingText` | `string` | — | Helper text |

| Output | Type | Description |
|--------|------|-------------|
| `checkedChange` | `EventEmitter<boolean>` | Check state changed |
| `indeterminateChange` | `EventEmitter<boolean>` | Indeterminate changed |
| `focusEvent` | `EventEmitter<void>` | Focus event |
| `blurEvent` | `EventEmitter<void>` | Blur event |

#### `dns-checkbox-group` — CheckboxGroupComponent

Group of checkboxes with layout control.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `options` | `{ label, supportingText, checked, disabled? }[]` | `[]` | Checkbox items |
| `layout` | `string` | `'vertical'` | `'horizontal'` \| `'vertical'` |
| `hasError` | `boolean` | `false` | Show error state |
| `errorMessage` | `string` | — | Error text |

#### `dns-radiobutton` — radiobuttonComponent

Radio button input, single or group mode.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | `string` | `'Default Label'` | Radio label |
| `checked` | `boolean` | `false` | Selected state |
| `disabled` | `boolean` | `false` | Disable state |
| `hasError` | `boolean` | `false` | Error state |
| `layout` | `string` | `'horizontal'` | `'horizontal'` \| `'vertical'` |
| `isGroup` | `string` | `'single'` | `'single'` \| `'group'` |
| `options` | `RadioOption[]` | `[]` | Options for group mode |

| Output | Type | Description |
|--------|------|-------------|
| `checkedChange` | `EventEmitter<string>` | Selection changed |

#### `dns-switch` — SwitchComponent

Toggle switch control.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | `string` | `''` | Switch label |
| `disabled` | `boolean` | `false` | Disable switch |
| `toggledOn` | `boolean` | `false` | Toggle state |
| `alignment` | `SwitchAlignment` | `'left'` | `'left'` \| `'right'` \| `'space-between'` |
| `labelPosition` | `SwitchLabelPosition` | `'after'` | `'before'` \| `'after'` |

| Output | Type | Description |
|--------|------|-------------|
| `toggledChange` | `EventEmitter<boolean>` | Toggle state changed |

#### `dns-slider` — SliderComponent

Range slider for numeric input.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `rangeMinimum` | `number` | `0` | Minimum value |
| `rangeMaximum` | `number` | `100` | Maximum value |
| `start` | `number` | `0` | Start value |
| `end` | `number` | — | End value (range mode) |
| `mode` | `SliderMode` | `'dynamic'` | Slider mode |
| `enableInput` | `boolean` | `false` | Show text input |
| `disabled` | `boolean` | `false` | Disable slider |
| `supportingText` | `string` | `''` | Helper text |

| Output | Type | Description |
|--------|------|-------------|
| `rangeChange` | `EventEmitter<{ start: number; end?: number }>` | Range changed |

#### `dns-datepicker` — DatepickerComponent

Calendar date picker with day/month/year, month/year, or quarter/year modes.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | `string` | `'Select date'` | Picker label |
| `variation` | `DatePickerYearType` | `'dayMonthYear'` | Date mode |
| `size` | `DatePickerDropdownSize` | `'large'` | `'large'` \| `'small'` |
| `disabled` | `boolean` | `false` | Disable picker |
| `error` | `boolean` | `false` | Error state |
| `minSelectableDate` | `Date` | — | Earliest selectable date |
| `maxSelectableDate` | `Date` | — | Latest selectable date |
| `inputValue` | `Date` | — | Pre-selected date |

| Output | Type | Description |
|--------|------|-------------|
| `dateSelected` | `EventEmitter<string>` | Date selected (string) |
| `dateSelectedFinal` | `EventEmitter<Date \| string>` | Final date selection |

#### `dns-date-range-picker` — DateRangePickerComponent

Dual calendar for selecting date ranges.

#### `dns-date-range-picker-dropdown` — DateRangePickerDropdownComponent

Dropdown variant of the date range picker.

#### `dns-autocomplete` — AutocompleteComponent

Autocomplete text input with dropdown suggestions and chip support.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | `string` | — | Field label |
| `options` | `string[]` | `[]` | Autocomplete options |
| `disabled` | `boolean` | `false` | Disable input |
| `loading` | `boolean` | `false` | Show loading state |
| `chipsEnabled` | `boolean` | `false` | Enable chip/tag mode |
| `searchIcon` | `boolean` | `false` | Show search icon |
| `placeholder` | `string` | `'Start typing...'` | Placeholder |
| `error` | `boolean` | `false` | Error state |
| `items` | `any[]` | `[]` | Items for selection |

| Output | Type | Description |
|--------|------|-------------|
| `selectedItems` | `EventEmitter<any>` | Items selected |

#### `dns-file-upload` — FileUploadComponent

File upload with drag-and-drop, progress tracking, and validation.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `uploadState` | `string` | `'enabled'` | `'enabled'` \| `'hover'` \| `'uploading'` \| `'complete'` \| `'failed'` |
| `variation` | `string` | `'select'` | `'select'` \| `'input'` |
| `size` | `string` | `'default'` | `'default'` \| `'mini'` |
| `acceptedFileTypes` | `string` | `'.csv, .pdf, .doc, .txt'` | Accepted MIME types |
| `maximumUploadSize` | `string` | `'200 MB'` | Max file size |
| `error` | `boolean` | — | Error state |
| `isDisabled` | `boolean` | — | Disable upload |
| `indicatorType` | `string` | `'circle'` | `'circle'` \| `'linear'` |

#### `dns-text-editor` — TextEditorComponent

Rich text editor (WYSIWYG).

---

### Dropdown & Menu

#### `dns-dropdown` — DropdownComponent

Generic dropdown menu with search, checkboxes, tags, and action buttons.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `items` | `OptionItem[]` | `[]` | Dropdown options |
| `search` | `boolean` | `false` | Enable search filtering |
| `checkbox` | `boolean` | `false` | Show checkboxes |
| `buttons` | `boolean` | `false` | Show action buttons |
| `statusTags` | `boolean` | `false` | Show status tags |
| `selectAll` | `boolean` | `false` | Show select-all option |
| `switch` | `boolean` | `false` | Show switch toggles |
| `dropdownVariant` | `DropdownVariantType` | `'default'` | `'default'` \| `'inverse'` |
| `emitAsObject` | `boolean` | `false` | Emit full object |
| `displayPropertyName` | `string` | `'name'` | Display property |

| Output | Type | Description |
|--------|------|-------------|
| `optionValue` | `EventEmitter<string>` | Option selected |
| `optionChecked` | `EventEmitter<{ item, checked }>` | Checkbox toggled |

#### `dns-menu` — MenuComponent

Context/popup menu component.

---

### Layout & Containers

#### `dns-card-component` — CardComponent

Flexible card container with title, subtitle, slots, and error/skeleton states.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | `string` | — | Card title (max 30 chars) |
| `subtitle` | `string` | — | Card subtitle (max 90 chars) |
| `cardVariant` | `CardVariant` | `'small'` | `'small'` \| `'large'` |
| `topSlots` | `Slot[]` | `[]` | Top section dynamic components |
| `bodySlots` | `Slot[]` | — | Body section dynamic components |
| `headerActionSlots` | `Slot[]` | `[]` | Header action components |
| `footerActionSlots` | `Slot[]` | `[]` | Footer action components |
| `errorFlag` | `boolean` | — | Show error overlay |
| `errorState` | `ErrorStateModel` | — | Error state configuration |
| `skeletonFlag` | `boolean` | — | Show skeleton loader |
| `skeletonLoader` | `Record<string, unknown>` | — | Skeleton configuration |

```html
<dns-card-component title="Revenue" subtitle="Q4 2024" cardVariant="large"
  [bodySlots]="cardContent" [errorFlag]="isError">
</dns-card-component>
```

#### `dns-widget-card` — WidgetCardComponent

Dashboard widget card with drawer support, tabs, resize, and rich content.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | `string` | `''` | Widget title |
| `subTitle` | `string` | `''` | Widget subtitle |
| `headerActionList` | `Slot[]` | — | Header action components |
| `cardContent` | `Slot[]` | — | Body content slots |
| `tag` | `Badge` | — | Badge/tag in header |
| `isDivider` | `boolean` | `true` | Show header divider |
| `resizeTop/Right/Bottom/Left` | `boolean` | `true` | Enable resize handles |
| `isDrawer` | `boolean` | — | Enable drawer mode |
| `drawerContent` | `DrawerContent` | — | Drawer configuration |
| `errorFlag` | `boolean` | `false` | Show error state |
| `skeletonFlag` | `boolean` | `false` | Show skeleton loader |
| `minHeight` | `number` | `0` | Minimum card height |
| `minWidth` | `number` | `0` | Minimum card width |

| Output | Type | Description |
|--------|------|-------------|
| `widgetDrawerClosed` | `EventEmitter<void>` | Drawer closed |
| `cardResized` | `EventEmitter<void>` | Card resized |
| `footerBtnClicked` | `EventEmitter<Button>` | Footer button clicked |
| `selectedTab` | `EventEmitter<Tab>` | Tab selected |
| `errorBtnClick` | `EventEmitter<void>` | Error retry clicked |

#### `dns-drawer` — DrawerComponent

Slide-out side panel with configurable content slots.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `isOpenDrawer` | `boolean` | `true` | Open/close the drawer |
| `size` | `DrawerSize` | `'medium'` | Drawer width size |
| `titleContent` | `string` | `''` | Drawer title |
| `subTitleContent` | `string` | `''` | Drawer subtitle |
| `enableBackdrop` | `boolean` | `false` | Show backdrop overlay |
| `scrollableSlots` | `Slot[]` | — | Scrollable body content |
| `fixedSlots` | `DrawerFixedSlot` | — | Fixed content slots |
| `tabsContent` | `Tab[]` | `[]` | Tab navigation in drawer |
| `footerLeftButton` | `Button` | `{}` | Left footer button |
| `footerMiddleButton` | `Button` | `{}` | Middle footer button |
| `footerRightButton` | `Button` | `{}` | Right footer button |
| `cardDrawer` | `boolean` | `false` | Card-style drawer |
| `wrapper` | `boolean` | `false` | Wrapper mode |
| `headerSlot` | `Slot` | — | Custom header content |

| Output | Type | Description |
|--------|------|-------------|
| `isDrawerClosed` | `EventEmitter<void>` | Drawer closed |
| `footerBtnClicked` | `EventEmitter<Button>` | Footer button clicked |
| `selectedTab` | `EventEmitter<Tab>` | Tab selected in drawer |
| `moreIconClicked` | `EventEmitter<void>` | More icon clicked |

#### `dns-slot` — SlotComponent\<T\>

Dynamic component injector for rendering components at runtime.

| Input | Type | Description |
|-------|------|-------------|
| `component` | `Type<T>` | Component class to render |
| `inputs` | `Partial<T>` | Input bindings for the component |
| `outputs` | `Record<string, Function \| EventEmitter>` | Output bindings |

```typescript
// Use Slot to dynamically render components
const mySlot: Slot = {
  component: MyChartComponent,
  inputs: { data: chartData },
  outputs: { chartClick: (e) => console.log(e) }
};
```

#### `dns-backdrop` — BackdropComponent

Semi-transparent overlay background.

| Input | Type | Default |
|-------|------|---------|
| `visible` | `boolean` | `false` |
| `background` | `string` | `'#303030'` |
| `opacity` | `string` | `'0.6'` |

| Output | Type |
|--------|------|
| `close` | `EventEmitter<any>` |

#### `dns-small-dialog` — DialogComponent

Small modal dialog component (uses Angular Material dialog).

---

### Navigation

#### `dns-header-nav` — HeaderNavComponent

Top navigation bar with logo, tabs, select, search, user menu, and org switcher.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `logo` | `string` | `''` | Logo image path |
| `logoLink` | `string` | `''` | Logo click URL |
| `variation` | `HeaderNavVariant` | `'tabs'` | `'tabs'` \| `'textAndSelect'` |
| `navItems` | `Tab[]` | `[]` | Navigation tab items |
| `buttonItems` | `Button[]` | `[]` | Header buttons |
| `selectItems` | `FilterItems[]` | `[]` | Select dropdown items |
| `userItems` | `OptionItem[]` | `[]` | User menu items |
| `orgItems` | `OptionItem[]` | `[]` | Organization menu items |
| `appSwitcherEnabled` | `boolean` | `false` | Show app switcher |
| `menuSlot1` | `Slot` | — | Custom menu slot 1 |
| `menuSlot2` | `Slot` | — | Custom menu slot 2 |

| Output | Type | Description |
|--------|------|-------------|
| `triggerEvents` | `EventEmitter<...>` | Navigation events (click, tab change, etc.) |

#### `dns-header-toolbar` — HeaderToolbarComponent

Toolbar area below header with buttons and custom slots.

| Input | Type | Default |
|-------|------|---------|
| `variant` | `string` | default variant |
| `buttonList` | `ToolbarButton[]` | `[]` |
| `slotList` | `Slot[]` | `[]` |

#### `dns-sidenav` — SidenavComponent

Collapsible side navigation with three layout variations.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `variation` | `string` | `'sidenav-A'` | `'sidenav-A'` \| `'sidenav-B'` \| `'sidenav-C'` |
| `items` | `any[]` | `[]` | Navigation items |
| `expandable` | `boolean` | — | Collapsible mode |

#### `dns-breadcrumb` — BreadcrumbComponent

Breadcrumb trail navigation.

| Input | Type | Default |
|-------|------|---------|
| `breadcrumb` | `Breadcrumb[]` | `[]` |

#### `dns-tabs` — TabsComponent

Tab navigation with dropdown overflow, auto/variable width, and routing support.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tabs` | `Tab[]` | — | Tab definitions |
| `variant` | `TabVariant` | — | Tab style variant |
| `allowRouting` | `boolean` | — | Enable Angular routing |
| `tabWrap` | `boolean` | `false` | Allow tab wrapping |
| `alignRight` | `boolean` | `false` | Right-align tabs |

| Output | Type | Description |
|--------|------|-------------|
| `tabChange` | `EventEmitter<Tab>` | Active tab changed |
| `tabClick` | `EventEmitter<Tab>` | Tab clicked |
| `actionTriggered` | `EventEmitter<string>` | Action triggered |

#### `dns-stepper` — StepperComponent

Multi-step process indicator/wizard.

| Input | Type | Default |
|-------|------|---------|
| `stepperItems` | `any[]` | `[]` |

#### `dns-page-footer` — PageFooterComponent

Standard page footer with logo, menus, and copyright.

| Input | Type | Default |
|-------|------|---------|
| `logo` | `string` | — |
| `footerMenus` | `FooterMenuItem[]` | — |
| `copyRightsText` | `string` | — |
| `openInNewTab` | `boolean` | `true` |

#### `dns-title-bar` — TitleBarComponent

Title bar header component.

---

### Data Display

#### `dns-sticky-table` — StickyTableComponent

Table with sticky header, footer, scrollable body, and responsive behavior.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `columns` | `StickyTableColumn[]` | `[]` | Column definitions |
| `columnConfig` | `DonutChartTableConfig[]` | `[]` | Column config (chart integration) |
| `data` | `StickyTableRow[]` | `[]` | Row data |
| `footer` | `StickyTableFooter \| null` | `null` | Footer row data |
| `maxBodyHeight` | `string` | `'300px'` | Maximum body scroll height |
| `fixedRowsHeight` | `boolean` | `true` | Fixed 6-row height mode |
| `hoverable` | `boolean` | `true` | Enable row hover |
| `clickable` | `boolean` | `true` | Enable row click |
| `responsive` | `boolean` | `true` | Responsive layout |

| Output | Type | Description |
|--------|------|-------------|
| `rowClick` | `EventEmitter<{ row, index }>` | Row clicked |
| `rowHover` | `EventEmitter<{ row, index }>` | Row hovered |
| `rowMouseLeave` | `EventEmitter<void>` | Mouse left rows |

#### `dns-table-header-cell` — TableHeaderCellComponent

Table header cell with sorting, icons, buttons, text truncation, and tooltips. Also used as AG Grid custom header component.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `titleText` | `string` | `''` | Header text |
| `type` | `HeaderCellType` | `'header'` | Cell type |
| `color` | `HeaderCellColor` | `'white'` | Background color |
| `align` | `HeaderCellAlign` | `'left'` | `'left'` \| `'center'` \| `'right'` |
| `sort` | `boolean` | `true` | Enable sorting |
| `appearance` | `HeaderCellAppearance` | `'neutral'` | Sort state |
| `textFitting` | `HeaderTextFitting` | `'truncatedEnd'` | Text truncation mode |
| `icon1` / `icon2` | `IconItem` | — | Header icons |
| `button1` / `button2` | `ButtonItem` | — | Header buttons |

| Output | Type | Description |
|--------|------|-------------|
| `sortChanged` | `EventEmitter<HeaderCellAppearance>` | Sort state changed |
| `buttonClicked` | `EventEmitter<{ buttonDetail, event }>` | Button clicked |
| `iconClicked` | `EventEmitter<{ iconDetail, event }>` | Icon clicked |

#### `dns-table-content-first-cell` — TableContentFirstCellComponent

First column cell with expandable, checkbox, radio, level indentation, tag, and link support.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `variation` | `FirstCellVariation` | `'text'` | Cell content type |
| `textSize` | `FirstCellTextSize` | `'small'` | Text size |
| `text` | `string` | `''` | Cell text |
| `tagLabel` | `string` | — | Tag label |
| `tagStatus` | `FirstCellTagStatus` | `'success'` | Tag status color |
| `supportText` | `string` | `''` | Supporting text |
| `url` | `string` | — | Link URL |
| `properties` | `FirstCellProperties` | `'none'` | Additional properties |
| `trackPosition` | `FirstCellTrackPosition` | `'none'` | Track position |
| `levels` | `FirstCellLevel` | `1` | Indentation level |
| `textFitting` | `FirstCellTextFitting` | `'truncatedEnd'` | Text truncation |

| Output | Type | Description |
|--------|------|-------------|
| `checkBoxCheckedItems` | `EventEmitter<any>` | Checkbox toggled |
| `expandable` | `EventEmitter<boolean>` | Row expanded/collapsed |

#### `dns-content-action-cell` — ContentActionCellComponent

Action cell for tables supporting checkbox, radio, expand, icon, and button variants.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `actionContent` | `ContentActionCellActionContent` | `'checkbox'` | `'checkbox'` \| `'radio'` \| `'expandableTrue'` \| `'icon'` \| `'button'` |
| `isExpand` | `boolean` | `false` | Expanded state |
| `buttonLabel` | `string` | — | Button label |
| `iconName` | `string` | — | Icon name |
| `data` | `RadioOption[]` | — | Radio options |

| Output | Type | Description |
|--------|------|-------------|
| `checkBox` | `EventEmitter<any>` | Checkbox toggled |
| `btnOnClick` | `EventEmitter<any>` | Button clicked |
| `expandRows` | `EventEmitter<boolean>` | Expand toggled |
| `iconClicked` | `EventEmitter<{ iconName }>` | Icon clicked |

Also exports: `dns-content-action-checkbox-cell`, `dns-content-action-download-cell`, `dns-content-action-button-cell` — AG Grid cell renderer wrappers.

#### `dns-section-header` — SectionHeaderComponent

Section header row for grouped table data. Also serves as AG Grid group row renderer.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `sectionTitle` | `string` | `'section header'` | Section title |
| `theme` | `string` | `'Grey'` | Color theme |
| `level` | `string` | `'Level1'` | `'Level 1'` through `'Level 4'` |
| `showExpandabels` | `boolean` | `false` | Show expand controls |
| `showCheckbox` | `boolean` | `false` | Show group checkbox |
| `lineDivider` | `boolean` | `false` | Show divider line |
| `buttonEnabel` | `boolean` | `false` | Show action button |
| `buttonText` | `string` | `'Enabled'` | Button label |

#### `dns-paginator` — PaginationComponent

Pagination control with page numbers and items-per-page selector.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `totalItems` | `number` | `300` | Total item count |
| `currentPage` | `number` | `1` | Active page |
| `itemsPerPage` | `number` | `10` | Items per page |
| `resultPerPageList` | `PageOptionItem[]` | `[]` | Page size options |
| `resultPerPageLabel` | `string` | — | Label text |

| Output | Type | Description |
|--------|------|-------------|
| `pageChange` | `EventEmitter<number>` | Page changed |
| `itemsPerPageChange` | `EventEmitter<number>` | Page size changed |

#### `dns-paginator-list` — PaginationListComponent

List with built-in pagination.

| Input | Type | Default |
|-------|------|---------|
| `data` | `string[]` | `[]` |
| `totalItems` | `number` | `300` |
| `currentPage` | `number` | `1` |
| `itemsPerPage` | `number` | `5` |

#### `dns-column-manager` — ColumnManagerComponent

Drawer-based column visibility manager for tables.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `isOpenDrawer` | `boolean` | `false` | Open/close |
| `data` | `ColumnItem[]` | `[]` | Column items |
| `titleContent` | `string` | `''` | Drawer title |
| `navItems` | `Tab[]` | `[]` | Tab navigation |

| Output | Type | Description |
|--------|------|-------------|
| `columnList` | `EventEmitter<{ data, eventName }>` | Column config changed |
| `isDrawerClosed` | `EventEmitter<boolean>` | Drawer closed |

---

### Data Visualization (Charts)

All chart components require `highcharts` and `highcharts-angular` as peer dependencies.

#### `dns-bar-chart` — BarChartComponent

Bar or column chart with categorical or monochromatic color modes.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `data` | `BarChartDataModel[]` | `[]` | Chart data |
| `chartType` | `ChartType` | `'horizontal'` | `'horizontal'` \| `'vertical'` |
| `isChartColorType` | `ChartColorType` | `'categorical'` | Color mode |
| `rotateLabel` | `boolean` | `true` | Rotate x-axis labels |
| `showXAxisValues` | `boolean` | `true` | Show x-axis values |
| `showYAxisValues` | `boolean` | `true` | Show y-axis values |
| `xAxisTitle` | `string` | `''` | X-axis title |
| `yAxisTitle` | `string` | `''` | Y-axis title |
| `title` | `string` | `''` | Chart title |

#### `dns-line-chart` — LineChartComponent

Line chart visualization.

#### `dns-donut-chart` — DonutChartComponent

Donut/pie chart visualization.

#### `dns-cash-flow` — CashFlowComponent

Cash flow waterfall chart.

| Input | Type | Default |
|-------|------|---------|
| `chartData` | `CashFlowChartData` | — |
| `yAxisTitle` | `string` | — |
| `xAxisLabels` | `string[]` | `[]` |

#### `dns-commitment-tracker` — CommitmentTrackerComponent

Commitment tracking chart visualization.

---

### Content & Information

#### `dns-badge` — BadgeComponent

Numeric or text badge indicator.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `badgeContent` | `string` | `'0'` | Badge text/number |
| `appearance` | `string` | `'notification'` | `'notification'` \| `'organization'` |

#### `dns-tag` — TagComponent

Colored label/tag for categorization and status.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | `string` | `'Label'` | Tag text |
| `category` | `TagCategoryTypes` | `'success'` | Color category |
| `type` | `string` | `'with-icon'` | `'text-only'` \| `'with-icon'` |

#### `dns-icon` — IconComponent

Icon renderer with size and style control.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `iconName` | `string` | — | Icon identifier |
| `size` | `string` | — | Icon size |
| `variation` | `IconVariation` | `'regular'` | Icon style variation |
| `isClickable` | `boolean` | — | Enable click interaction |
| `iconColor` | `string` | — | Icon color override |

| Output | Type | Description |
|--------|------|-------------|
| `iconClick` | `EventEmitter<Event>` | Icon clicked |

#### `dns-icon-with-lable` — IconWithLableComponent

Icon paired with a text label.

| Input | Type |
|-------|------|
| `iconName` | `string` |
| `labelName` | `any` |
| `size` | `string` |
| `badgeContent` | `any` |
| `variation` | `any` |

#### `dns-svg` — SvgComponent

SVG graphic renderer.

| Input | Type |
|-------|------|
| `iconName` | `string` |
| `size` | `string` |

#### `dns-chips` — ChipsComponent

Removable chip/pill components for selections or tags.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `chips` | `{ name, disabled }[]` | `[]` | Chip items |
| `size` | `string` | `'large'` | `'large'` \| `'small'` |

| Output | Type | Description |
|--------|------|-------------|
| `chipRemoved` | `EventEmitter<string>` | Chip removed |
| `inputChangeChip` | `EventEmitter<any>` | Input changed |
| `valueChangeChip` | `EventEmitter<any>` | Value changed |

#### `dns-notification` — NotificationComponent

Snackbar/alert notification with icon, title, description, link, and close button.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `contentTitle` | `string` | `'Snackbar Notification Title'` | Notification title |
| `contentDesc` | `string` | — | Description text |
| `notificationtype` | `string` | `''` | `'info'` \| `'success'` \| `'warning'` \| `'error'` |
| `variation` | `string` | `''` | Style variation |
| `showTitle` | `boolean` | `true` | Show title |
| `showDesc` | `boolean` | `true` | Show description |
| `showLink` | `boolean` | `true` | Show action link |
| `showClose` | `boolean` | `true` | Show close button |
| `contentLink` | `string` | `'Action'` | Link text |

#### `dns-notification-list` — NotificationListComponent

Container for notification items with sorting.

| Input | Type | Default |
|-------|------|---------|
| `data` | `Array<NotificationSectionHeading \| NotificationListItemData>` | — |
| `sortBy` | `NotificationSortLabel` | `'mostRecent'` |
| `titleContent` | `string` | — |

| Output | Type |
|--------|------|
| `primaryActionClick` | `EventEmitter<void>` |
| `secondaryActionClick` | `EventEmitter<void>` |
| `replyClick` | `EventEmitter<void>` |
| `flagClick` | `EventEmitter<void>` |

#### `dns-notification-list-item` — NotificationListItemComponent

Individual notification item in a list.

#### `dns-empty-state` — EmptyStateComponent

Placeholder display when no data is available.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `heading` | `string` | — | Heading text |
| `description` | `SafeHtml` | — | Description content |
| `icon` | `EmptyStateIcon` | `'warning-circle'` | Icon type |
| `enableButton` | `boolean` | `false` | Show action button |
| `buttonLabel` | `string` | — | Button label |
| `layout` | `EmptyLayout` | `'page_error'` | `'default'` \| `'card'` \| `'page_error'` \| `'table_error'` |

| Output | Type |
|--------|------|
| `btnClick` | `EventEmitter<boolean>` |

#### `dns-skeleton` — SkeletonComponent

Animated loading placeholder. Configurable shapes, alignment, radius, and theme.

Enums: `SkeletonAlignment`, `SkeletonJustify`, `SkeletonRadius`, `SkeletonTheme`

#### `dns-progress-indicator` — ProgressIndicatorComponent

Circular progress/spinner indicator.

| Input | Type | Default |
|-------|------|---------|
| `size` | `ProgressBarSize` | `'large'` |
| `button` | `boolean` | `true` |
| `visible` | `boolean` | `true` |

#### `dns-progressbar-linear` — ProgressbarLinearComponent

Linear progress bar with multiple variants.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | `string` | — | Progress title |
| `value` | `number` | `20` | Progress value (0-100) |
| `type` | `string` | `'Simple'` | `'Simple'` \| `'Document Upload'` \| `'pageload'` \| `'mini'` |
| `colorVariant` | `string` | `'info'` | `'info'` \| `'success'` \| `'warning'` \| `'error'` \| `'netural'` |
| `progressVariant` | `string` | `'plain'` | `'plain'` \| `'withpercentage'` |
| `documentStatus` | `string` | `'Waiting'` | `'Waiting'` \| `'Uploading'` \| `'Success'` \| `'Error'` |

#### `dns-link-action` — LinkActionComponent

Interactive link with icon.

| Input | Type | Default |
|-------|------|---------|
| `linkLabel` | `string` | `''` |
| `size` | `LinkActionSize` | `'extra-small'` |
| `iconVariant` | `LinkActionIcon` | `'left'` |
| `url` | `string` | `''` |

| Output | Type |
|--------|------|
| `linkClick` | `EventEmitter<Event>` |

#### `dns-dynamic-list` — DynamicListComponent

Ordered or unordered list renderer.

| Input | Type | Default |
|-------|------|---------|
| `items` | `ListItem[]` | `[]` |
| `listType` | `string` | `'ul'` |
| `level` | `number` | `1` |
| `size` | `string` | `'Medium'` |

---

### Data Modules

Structured data display components for detail views and dashboards.

#### `dns-data-module-simple` — DataModuleSimpleComponent

Simple label-value data display with optional icon and link.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `itemLabel` | `string` | `''` | Label text |
| `text` | `string` | `''` | Value text |
| `type` | `DataModuleType` | `'regular'` | Display type |
| `icon` | `boolean` | `false` | Show icon |
| `iconName` | `string` | `'folders'` | Icon name |
| `divider` | `boolean` | `true` | Show bottom divider |
| `link` | `boolean` | `false` | Show link |
| `linkUrl` | `string` | `''` | Link URL |
| `isHyperlink` | `boolean` | `false` | Render as hyperlink |

| Output | Type |
|--------|------|
| `linkClick` | `EventEmitter<DataModuleSimpleEventModel>` |

#### `dns-data-module-contacts` — DataModuleContactsComponent

Contact information display with name, title, phone, email, and avatar badge.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `contactName` | `string` | `''` | Contact name |
| `contactTitle` | `string` | `''` | Contact title |
| `phone` | `string` | `''` | Phone number |
| `email` | `string` | `''` | Email address |
| `showBadge` | `boolean` | `false` | Show avatar badge |
| `badgeText` | `string` | `''` | Badge initials |
| `variant` | `BadgeVariant` | `'initials'` | Badge variant |

#### `dns-data-module-with-badge` — DataModuleWithBadgeComponent

Data module with badge list support and secondary text.

| Input | Type | Default |
|-------|------|---------|
| `itemLabel` | `string` | `''` |
| `text` | `string` | `''` |
| `badgeList` | `BadgeItem[]` | `[]` |
| `badgeVariant` | `BadgeType` | `'text'` |
| `secondaryText` | `string` | `''` |
| `showDivider` | `boolean` | `true` |

#### `dns-data-module-badge` — DataModuleBadgeComponent

Multi-badge data display.

| Input | Type | Default |
|-------|------|---------|
| `type` | `BadgeType` | `'text'` |
| `collapsed` | `boolean` | `true` |
| `badgeList` | `BadgeItem[]` | `[]` |

#### `dns-data-module-layout` — DataModuleLayoutComponent

Grid layout container for data modules.

| Input | Type | Default |
|-------|------|---------|
| `colCount` | `number` | `3` |
| `dataModuleItems` | `Slot[]` | `[]` |

#### `dns-data-module-secondary-line` — DataModuleSecondaryComponent

Data module with secondary text objects and icon support.

| Input | Type | Default |
|-------|------|---------|
| `itemLabel` | `string` | `''` |
| `text` | `string` | `''` |
| `secondaryTextObject` | `SecondaryTextObjectModel[]` | `[]` |
| `type` | `DataModuleType` | `'regular'` |
| `divider` | `boolean` | `true` |

| Output | Type |
|--------|------|
| `linkClick` | `EventEmitter<DataModuleSecondaryEventModel>` |

---

### Miscellaneous Components

#### `dns-accordion` — AccordionComponent

Expandable/collapsible accordion using Angular CDK.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `items` | `AccordionItem[]` | `[]` | Accordion items |
| `size` | `AccordionSize` | `'large'` | Panel size |
| `bodySlot` | `boolean` | `true` | Enable body slot |

#### `dns-enhanced-accordion` — EnhancedAccordionComponent

Advanced accordion variant with additional features.

#### `dns-divider` — DividerComponent

Horizontal divider line.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `border` | `DividerType` | — | `'extra light'` \| `'light'` \| `'medium'` \| `'dark'` |

#### `dns-divider-vertical` — DividerVerticalComponent

Vertical divider line.

| Input | Type | Default |
|-------|------|---------|
| `border` | `DividerType` | `'light'` |

#### `dns-photo-carousel` — PhotoCarouselComponent

Image carousel/gallery with navigation.

#### `dns-cursor-guided-tooltip` — CursorGuidedTooltipComponent

Draggable tooltip that follows cursor position, used with charts.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tooltipTitle` | `string` | `''` | Tooltip title |
| `tooltipDescription` | `string` | `''` | Description text |
| `legendItems` | `LegendItems[]` | `[]` | Legend items |
| `legendAppearance` | `LegendAppearance` | — | Legend display mode |
| `cursorArrowPosition` | `ArrowPosition` | `'right'` | Arrow direction |
| `cursorTooltipSize` | `ComponentSize` | `'small'` | Tooltip size |
| `snapEvent` | `boolean` | `false` | Enable snap behavior |
| `dragBoundary` | `HTMLElement \| null` | `null` | Drag boundary element |

| Output | Type |
|--------|------|
| `dragPosition` | `EventEmitter<{ x, y }>` |
| `tooltipWidth` | `EventEmitter<number>` |
| `tooltipHeight` | `EventEmitter<number>` |
| `enableDoubleClick` | `EventEmitter<boolean>` |

---

## Directives

#### `[dnsTooltip]` — TooltipDirective

Attribute directive for tooltips on any element.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `dnsTooltip` | `string` | `''` | Tooltip text |
| `toolTipTitle` | `string` | `''` | Tooltip title |
| `position` | `TooltipPositionModel` | `'left'` | Position |
| `variation` | `TooltipVariationModel` | `'dark'` | `'dark'` \| `'light'` |
| `size` | `TooltipSizeModel` | `'small'` | Tooltip size |
| `tooltipType` | `TooltipTypeModel` | `'plain'` | Tooltip type |
| `isTooltip` | `boolean` | `true` | Enable/disable |
| `items` | `TooltipItems[]` | `[]` | Rich tooltip items |
| `chart` | `ChartTypeModel` | `'line'` | Chart tooltip type |

```html
<span dnsTooltip="Helpful information" position="top-center" variation="dark">
  Hover me
</span>
```

#### `[dnsCursorTooltip]` — CursorTooltipDirective

Tooltip that tracks cursor position.

#### `dnsScrollbar` — ScrollbarDirective

Custom scrollbar styling directive.

#### `dnsAdvancedScrollbar` — AdvancedScrollbarDirective

Advanced scrollbar with size, orientation, and variant options.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `dnsAdvancedScrollbarSize` | `AdvanceScrollSize` | `'small'` | `'small'` \| `'large'` |
| `dnsAdvancedScrollbarVariant` | `AdvanceScrollVariant` | `'light'` | `'light'` \| `'dark'` |
| `dnsAdvancedScrollbarOrientation` | `AdvanceScrollOrientation` | `'vertical'` | `'vertical'` \| `'horizontal'` |

---

## Shared Types

### Slot

Dynamic component injection model used throughout the library:

```typescript
interface Slot {
  component: Type<any>;
  inputs?: Record<string, any>;
  outputs?: Record<string, Function | EventEmitter<unknown>>;
}
```

### Tab

Navigation tab model:

```typescript
interface Tab {
  label: string;
  icon?: string;
  disabled?: boolean;
  active?: boolean;
  route?: string;
}
```

### Button

Button configuration model used in drawers, footers, and toolbars:

```typescript
interface Button {
  label?: string;
  type?: BtnType;
  size?: BtnSize;
  disabled?: boolean;
  icon?: string;
}
```

---

## Key Enums

| Enum | Values | Used by |
|------|--------|---------|
| `BtnType` | `primary`, `secondary`, `tertiary`, `destructive-primary`, `destructive-tertiary`, `approval-primary`, `icon` | Button, DrawerFooter |
| `BtnSize` | `large`, `small`, `mini` | Button |
| `ButtonVariant` | `text`, `textWithIcon`, `iconOnly` | Button |
| `SelectVariation` | `filled`, `outline`, `standard` | Select |
| `SelectSize` | `large`, `small`, `small-with-label` | Select |
| `CardVariant` | `small`, `large` | Card |
| `DividerType` | `extra light`, `light`, `medium`, `dark` | Divider |
| `HeaderCellAlign` | `left`, `center`, `right` | TableHeaderCell |
| `HeaderCellAppearance` | `neutral`, `ascending`, `descending` | TableHeaderCell |
| `EmptyStateIcon` | `clock`, `list-magnifying-glass`, `link-break`, `undefined`, `warning-circle`, `file-x` | EmptyState |
| `EmptyLayout` | `default`, `card`, `page_error`, `table_error` | EmptyState |
| `TagCategoryTypes` | `success`, and others | Tag |
| `SwitchAlignment` | `space-between`, `left`, `right` | Switch |
| `SwitchLabelPosition` | `before`, `after` | Switch |
| `SkeletonTheme` | `default`, `inverse` | Skeleton |
| `HeaderNavVariant` | `tabs`, `textAndSelect` | HeaderNav |

---

## Project Structure

```
src/
├── component/              # All components
│   ├── Autocomplete/
│   ├── accordion/
│   ├── badge/
│   ├── bar-chart/
│   ├── breadcrumb/
│   ├── button/
│   ├── button-group/
│   ├── card/
│   ├── cash-flow/
│   ├── checkbox/
│   ├── checkbox-group/
│   ├── chips/
│   ├── column-manager/
│   ├── commitment-tracker/
│   ├── cursor-guided-tooltip/
│   ├── data-module-contacts/
│   ├── data-module-layout/
│   ├── data-module-multi-badge/
│   ├── data-module-secondary-line/
│   ├── data-module-simple/
│   ├── data-module-with-badge/
│   ├── date-range-picker/
│   ├── date-range-picker-dropdown/
│   ├── datepicker/
│   ├── dialog-group/dialog-small/
│   ├── divider/
│   ├── divider-vertical/
│   ├── donut-chart/
│   ├── drawer/
│   ├── dropdown/
│   ├── dual-button/
│   ├── empty-state/
│   ├── enhanced-accordion/
│   ├── file-upload/
│   ├── header-nav/
│   ├── header-toolbar/
│   ├── icon/
│   ├── icon-with-lable/
│   ├── line-chart/
│   ├── link-action/
│   ├── list-ordered-unordered/
│   ├── menu/
│   ├── neutral-button/
│   ├── notification/
│   ├── notification-list/
│   ├── notification-list-item/
│   ├── page-footer/
│   ├── pagination/
│   ├── pagination-list/
│   ├── photo-carousel/
│   ├── progress-indicator/
│   ├── progressbar-linear/
│   ├── radiobutton/
│   ├── scrollbar/
│   ├── select/
│   ├── select-group/
│   ├── sidenav/
│   ├── skeleton/
│   ├── slider/
│   ├── slot/
│   ├── stepper/
│   ├── sticky-table/
│   ├── svg/
│   ├── switch/
│   ├── table/
│   │   ├── content-action-cell/
│   │   ├── section-header/
│   │   ├── table-content-first-cell/
│   │   └── table-header-cell/
│   ├── tabs/
│   ├── tag/
│   ├── text-editor/
│   ├── text-field/
│   ├── title-bar/
│   ├── toggle-button/
│   ├── tooltip/
│   └── widget-card/
├── common/
│   ├── const.ts            # Constants, enums, and type definitions
│   ├── enum.ts             # Additional enumerations
│   └── interface.ts        # Shared interfaces
├── directive/              # Shared directives
├── service/                # Shared services
├── public-api.ts           # Library entry point (all exports)
└── styles/                 # Global SCSS styles and design tokens
```
