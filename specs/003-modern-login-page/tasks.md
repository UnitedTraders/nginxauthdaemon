# Tasks: Modern Login Page

**Input**: Design documents from `specs/003-modern-login-page/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested. Test tasks limited to running existing suite for regression verification.

**Organization**: Tasks grouped by user story. This feature is a single-file rewrite so most tasks are sequential within the template file, but logically map to user stories.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

> No project setup needed — this is a template rewrite within an existing project.

- [x] T001 Back up current template by reading `nginxauthdaemon/templates/login.html` and noting all Jinja2 variables and form field names for verification

---

## Phase 2: Foundational — HTML Structure & Layout (US-006: Preserved Functionality)

> **Goal**: Establish the new HTML skeleton with all Jinja2 variables, form fields, and semantic structure in place. Existing tests must pass after this phase.

- [x] T002 [US6] Rewrite HTML skeleton in `nginxauthdaemon/templates/login.html` with: DOCTYPE, `<html lang="en">`, `<head>` (meta charset, viewport, title with `{{ realm }}`), `<body>`, `<main>`, `<form action="{{ url_for('show_login') }}" method="POST">`, input fields (`name="user"`, `name="pass"`), hidden field (`name="target"` with `{{ target }}`), error display (`{{ error }}`), and submit button. No styling yet — structure only.
- [x] T003 [US6] Add semantic HTML5 elements: `<label>` elements for username and password inputs (with `for` attribute matching input `id`), `<main>` landmark wrapper, heading structure (`<h1>` with `{{ realm }}`), error message `<div>` with `role="alert"`
- [x] T004 [US6] Run existing test suite with `pytest tests/ -v` to verify form submission contract is preserved (all 55 tests must pass)

---

## Phase 3: US-001 — Zero External Dependencies

> **Goal**: Ensure the template contains no external resource references.

- [x] T005 [US1] Remove all `@import url(...)` rules (Google Fonts, weloveiconfonts.com) from `nginxauthdaemon/templates/login.html`
- [x] T006 [US1] Remove jQuery `<script src="https://code.jquery.com/...">` tag from `nginxauthdaemon/templates/login.html`
- [x] T007 [US1] Remove all Entypo icon font class references (`entypo-login`, `entypo-user`, `entypo-key`, `entypo-lock`) from `nginxauthdaemon/templates/login.html`
- [x] T008 [P] [US1] Delete unused static asset `nginxauthdaemon/static/login-sprite.png`

---

## Phase 4: US-003 — System Font Stack

> **Goal**: Apply system font typography with no external font dependencies.

- [x] T009 [US3] Add CSS custom properties (design tokens) in `<style>` block of `nginxauthdaemon/templates/login.html`: `--font-stack: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` and apply to `body` via `font-family: var(--font-stack)`

---

## Phase 5: US-002 — Modern Visual Design

> **Goal**: Implement the dark theme with glassmorphism card and purple/violet accents. This is the main visual phase.

- [x] T010 [US2] Add full CSS custom properties (design tokens) to `<style>` block in `nginxauthdaemon/templates/login.html`: background (`#0f0f17`), card glass (`rgba(255,255,255,0.05)`), input backgrounds, text colors (`rgba(255,255,255,0.9)`, `rgba(255,255,255,0.5)`), accent (`#8b5cf6`), accent-hover (`#7c3aed`), error (`#ef4444`), border (`rgba(255,255,255,0.1)`), border-radius tokens
- [x] T011 [US2] Style page body and layout in `nginxauthdaemon/templates/login.html`: dark background, full-viewport height (`min-height: 100vh`), flexbox centering (both axes), zero margin
- [x] T012 [US2] Style glassmorphism card container in `nginxauthdaemon/templates/login.html`: `backdrop-filter: blur(20px)`, `-webkit-backdrop-filter: blur(20px)`, semi-transparent background, subtle border (`rgba(255,255,255,0.1)`), `border-radius: 16px`, padding, `max-width: 420px`, `width: 90%`
- [x] T013 [US2] Style form inputs in `nginxauthdaemon/templates/login.html`: transparent background with `rgba(255,255,255,0.08)`, rounded corners, white text, `::placeholder` styling with secondary text color, full width within card, consistent padding and height
- [x] T014 [US2] Style input focus states in `nginxauthdaemon/templates/login.html`: brighter background (`rgba(255,255,255,0.12)`), accent-colored border or outline (`#8b5cf6`), smooth transition (`transition: all 0.2s ease`)
- [x] T015 [US2] Style submit button in `nginxauthdaemon/templates/login.html`: full-width, accent background (`#8b5cf6`), white text, rounded corners, hover state (`#7c3aed`), active state (slight scale/darken), cursor pointer, transition effects
- [x] T016 [US2] Style error message display in `nginxauthdaemon/templates/login.html`: error color (`#ef4444`), subtle error background (`rgba(239,68,68,0.1)`), border-left or border accent, rounded corners, padding, only visible when `{{ error }}` is non-empty (use Jinja2 `{% if error %}` conditional)
- [x] T017 [US2] Style heading and page title in `nginxauthdaemon/templates/login.html`: centered text, appropriate font size/weight, text color using `--text-primary`, margin/spacing within card

---

## Phase 6: US-004 — Vanilla JavaScript

> **Goal**: Replace jQuery with CSS-only or vanilla JS solutions.

- [x] T018 [US4] Replace jQuery focus/blur icon color changes with CSS `:focus-within` selectors in `nginxauthdaemon/templates/login.html`. Structure each input in a `.input-group` wrapper; use `.input-group:focus-within .icon { color: var(--accent) }` for the color transition. Remove the jQuery `<script>` block entirely.

---

## Phase 7: US-005 — Accessible Login Form

> **Goal**: Ensure proper accessibility with keyboard nav, screen readers, and focus management.

- [x] T019 [US5] Verify `<label>` elements are correctly associated with inputs via `for`/`id` attributes in `nginxauthdaemon/templates/login.html`. Labels can be visually hidden with `sr-only` CSS class if using placeholder-only visual design.
- [x] T020 [US5] Add `.sr-only` CSS class in `nginxauthdaemon/templates/login.html` for screen-reader-only labels: `position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); border: 0`
- [x] T021 [US5] Ensure visible focus rings on all interactive elements (inputs, button) in `nginxauthdaemon/templates/login.html` using `outline` or `box-shadow` with accent color. Do NOT suppress focus outlines.
- [x] T022 [US5] Verify Tab order in `nginxauthdaemon/templates/login.html`: username → password → submit button. Ensure no `tabindex` manipulation breaks natural order.

---

## Phase 8: Responsive & Polish (US-002 continued)

> **Goal**: Ensure the design works on all viewports (320px to 2560px).

- [x] T023 [US2] Add responsive styles in `nginxauthdaemon/templates/login.html`: ensure `max-width: 420px` + `width: 90%` on card, input fields `width: 100%`, appropriate touch-target sizes on mobile (min 44px height for inputs and button), adjust padding/margins for small screens via media query if needed

---

## Phase 9: Final Verification

> **Goal**: Confirm no regressions and all acceptance criteria met.

- [x] T024 Run full test suite with `pytest tests/ -v` to confirm all 55 tests still pass
- [x] T025 Verify the rendered template contains zero external URLs by searching `nginxauthdaemon/templates/login.html` for `http://`, `https://`, `//cdn`, `@import url` — must find none
- [x] T026 Review final `nginxauthdaemon/templates/login.html` for completeness: all Jinja2 variables present (`{{ realm }}`, `{{ url_for('show_login') }}`, `{{ error }}`, `{{ target }}`), all form field names preserved (`user`, `pass`, `target`), no external dependencies

---

## Dependencies

```
Phase 1 (Setup) → Phase 2 (HTML Structure) → Phase 3 (Remove External Deps)
                                             → Phase 4 (System Fonts)
                                             → Phase 5 (Visual Design)
                                             → Phase 6 (Vanilla JS)
                                             → Phase 7 (Accessibility)
Phase 5 → Phase 8 (Responsive Polish)
All Phases → Phase 9 (Final Verification)
```

## User Story Dependency Graph

```
US-006 (Preserved Functionality) ─── MUST complete first (Phase 2)
       │
       ├── US-001 (Zero External Deps) ── can start after Phase 2
       ├── US-003 (System Fonts) ── can start after Phase 2
       ├── US-002 (Modern Visual Design) ── can start after Phase 2
       ├── US-004 (Vanilla JS) ── can start after Phase 2
       └── US-005 (Accessibility) ── can start after Phase 2
              │
              └── Phase 8 (Responsive) ── after US-002 visual styles exist
```

## Implementation Strategy

### MVP First

1. Complete Phase 2 (HTML skeleton with preserved functionality) → Run tests → Verify
2. Complete Phases 3-7 (all user stories) → Run tests → Verify
3. Complete Phase 8-9 (polish and final verification)

### Single File Approach

Since this is a single-file rewrite (`login.html`), tasks are logically sequential within the file. The phase structure enables incremental validation: after each phase, the template should be valid HTML that passes tests.

---

## Notes

- All tasks modify a single file (`nginxauthdaemon/templates/login.html`) except T008 (delete static asset)
- [P] tasks = different files, no dependencies
- The single-file nature means most tasks within a phase are sequential
- Commit after each phase completion for clean history
- T004 and T024 are verification checkpoints — stop and fix if tests fail
