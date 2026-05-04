# Research: Modern Login Page

## R1: System Font Stack Best Practices

**Decision**: Use the modern system font stack convention.
**Rationale**: System fonts render instantly (no FOUT/FOIT), are familiar to users on each OS, and require zero network requests. The `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` stack covers macOS, Windows, Linux, Android, and iOS.
**Alternatives considered**:
- Self-hosted web fonts (Roboto WOFF2): Adds file management, ~20KB payload, still causes FOUT. Rejected — not worth it for a single login page.
- CSS `system-ui` generic family: Good but inconsistent across older browsers (renders as Times New Roman on some Linux distros). Rejected — explicit stack is safer.

## R2: Glassmorphism CSS Implementation

**Decision**: Use `backdrop-filter: blur()` with semi-transparent background and subtle border.
**Rationale**: Native CSS property supported by all modern browsers (Chrome 76+, Firefox 103+, Safari 9+, Edge 79+). No JavaScript needed.
**Implementation pattern**:
```css
.card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
}
```
**Fallback**: On browsers without `backdrop-filter` support, the card degrades to a semi-transparent box — still usable, just without blur. The spec allows dropping browsers older than 3 years, so this covers our target.
**Alternatives considered**:
- SVG filter blur: More complex, worse performance. Rejected.
- Solid card with box-shadow: Works everywhere but loses the glass effect. Rejected — the spec specifically chose glassmorphism.

## R3: Icon Replacement Strategy

**Decision**: Replace Entypo icon font with inline SVG icons or Unicode characters.
**Rationale**: The current template uses 3 Entypo icons (`entypo-login`, `entypo-user`, `entypo-key`, `entypo-lock`). Inline SVGs are self-contained, sharp at any size, and require no external requests. For a login form, simple Unicode alternatives also work (e.g., `🔒` for lock).
**Alternatives considered**:
- CSS-only icons (borders/transforms): Possible for simple shapes but fragile and hard to maintain. Rejected.
- Embedded icon font (base64): Bloats HTML significantly for 4 icons. Rejected.
- No icons at all: Clean but loses visual affordance. Rejected.

**Decision**: Use SVG for submit button icon; use label text and input `type` attributes for field identification instead of decorative icons. This is cleaner and more accessible.

## R4: jQuery Replacement

**Decision**: Replace all jQuery with vanilla JavaScript using `addEventListener` and `querySelector`.
**Rationale**: The current jQuery usage is minimal — only focus/blur color changes on 2 icon spans. These can be handled entirely with CSS `:focus-within` on parent elements, eliminating JavaScript entirely for this behavior.
**Implementation pattern**:
```css
.input-group:focus-within .icon { color: var(--accent); }
```
**Alternatives considered**:
- Vanilla JS event listeners: Works but unnecessary when CSS can handle it. Rejected in favor of pure CSS.
- Remove focus color change entirely: Loses visual feedback. Rejected.

## R5: Dark Theme Color Palette

**Decision**: Use a carefully selected dark palette with purple/violet accent.
**Palette**:
- Background: `#0f0f17` (deep dark blue-black)
- Card background: `rgba(255, 255, 255, 0.05)` (glass effect)
- Text primary: `rgba(255, 255, 255, 0.9)`
- Text secondary: `rgba(255, 255, 255, 0.5)`
- Accent: `#8b5cf6` (violet-500, consistent with modern design systems)
- Accent hover: `#7c3aed` (violet-600)
- Error: `#ef4444` (red-500)
- Input background: `rgba(255, 255, 255, 0.08)`
- Input focus background: `rgba(255, 255, 255, 0.12)`
- Border: `rgba(255, 255, 255, 0.1)`

**Rationale**: Purple/violet was chosen in clarification. The palette uses the Tailwind violet scale for consistency with modern design language. Sufficient contrast ratios for WCAG AA compliance (tested: white text on dark background > 15:1, accent on dark > 4.5:1).

## R6: Responsive Layout Strategy

**Decision**: Use CSS flexbox for vertical centering, `min-height: 100vh` for full-page layout, `max-width` with percentage-based padding for mobile.
**Rationale**: Flexbox centering is the simplest modern approach. A single `max-width: 420px` with `width: 90%` handles both desktop and mobile gracefully.
**Alternatives considered**:
- CSS Grid: Overkill for a single centered card. Rejected.
- `position: absolute` + `transform: translate`: Older technique, less flexible. Rejected.

## R7: Accessibility Requirements

**Decision**: Use semantic HTML5 with proper `<label>` elements, `<main>` landmark, and visible focus rings.
**Rationale**: The current template has no `<label>` elements and suppresses focus outlines. The redesign will add proper labels (can be visually hidden with `sr-only` class if floating labels are used), ensure Tab order follows visual order, and use `outline` or `box-shadow` for focus indication.
**Key changes**:
- Add `<label for="...">` for each input
- Use `<main>` landmark wrapper
- Ensure focus ring uses accent color and is clearly visible
- Associate error message with form via `role="alert"`

## R8: Existing Test Compatibility

**Decision**: Preserve all `name` attributes and form action exactly as-is.
**Rationale**: Integration tests POST to `/auth/login` with fields `user`, `pass`, and `target`. The template must keep: `name="user"`, `name="pass"`, `name="target"`, `action="{{ url_for('show_login') }}"`, `method="POST"`. Tests also check for `error` text in responses.
**Verified**: Tests don't check HTML structure, CSS classes, or JavaScript behavior — only form submission and response content.
