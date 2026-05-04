# Feature Specification: Modern Login Page

**Feature**: Modernize login page by removing external dependencies and refreshing visual design
**Date**: 2026-05-04
**Status**: Draft

## Clarifications

### Session 2026-05-04
- Q: Color scheme direction (dark vs light theme)? → A: Dark theme — dark background with light text and accent color
- Q: Accent color for interactive elements? → A: Purple/violet accent — modern tech aesthetic (Discord, Figma style)
- Q: Login form card treatment on dark background? → A: Glassmorphism — semi-transparent card with backdrop blur and subtle border

## Overview

The authentication daemon's login page currently relies on external resources (Google Fonts, weloveiconfonts.com icon font, jQuery) and has an outdated visual design. This feature replaces all external dependencies with self-contained alternatives and delivers a modern, clean login experience using only vanilla JavaScript and system fonts.

## User Stories

### US-001: Zero External Dependencies (P1)
**As a** system administrator,
**I want** the login page to load without any external network requests (no CDNs, no external font services),
**So that** the page works reliably in air-gapped environments, behind restrictive firewalls, and without privacy concerns from third-party requests.

**Acceptance Criteria**:
- The login page makes zero HTTP requests to external domains
- All CSS, JavaScript, and fonts are either inline or served from the daemon itself
- The page loads and functions correctly with no internet access beyond the daemon

### US-002: Modern Visual Design (P1)
**As a** user accessing a protected application,
**I want** the login page to look modern, clean, and professional,
**So that** I have confidence in the security of the system I'm logging into.

**Acceptance Criteria**:
- The page uses a contemporary design language (clean spacing, subtle shadows, rounded inputs, clear visual hierarchy)
- Color scheme uses a dark background with light text and purple/violet accents for interactive elements (buttons, focus rings, links)
- The login form is presented in a glassmorphism card (semi-transparent background, backdrop blur, subtle border) centered on the dark background
- The form is vertically centered on the page and responsive to different screen widths
- Input fields have clear labels or placeholders and visible focus states
- The submit button is clearly identifiable and has hover/active states
- Error messages are displayed prominently in a distinguishable style

### US-003: System Font Stack (P1)
**As a** developer deploying the daemon,
**I want** the login page to use a system font stack instead of web fonts,
**So that** fonts render instantly without FOUT/FOIT and no external requests are needed.

**Acceptance Criteria**:
- Typography uses a system font stack (e.g., `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`)
- Text is legible at all sizes used on the page
- No `@import` or `<link>` tags referencing external font services

### US-004: Vanilla JavaScript (P2)
**As a** developer maintaining the daemon,
**I want** the login page to use vanilla JavaScript instead of jQuery,
**So that** there are no library dependencies to maintain or update for security patches.

**Acceptance Criteria**:
- All interactive behavior (focus states, form handling) uses native DOM APIs
- No `<script src="...">` tags loading external libraries
- The jQuery dependency is completely removed

### US-005: Accessible Login Form (P2)
**As a** user with accessibility needs,
**I want** the login form to be usable with keyboard navigation and screen readers,
**So that** I can authenticate regardless of how I interact with the page.

**Acceptance Criteria**:
- All form fields have associated `<label>` elements (visible or `aria-label`)
- The form is navigable using Tab key in logical order
- Focus states are clearly visible (not suppressed)
- Error messages are associated with the form using appropriate markup
- The page has a sensible heading structure

### US-006: Preserved Functionality (P1)
**As a** system administrator,
**I want** all existing login functionality preserved after the redesign,
**So that** the upgrade is purely visual with no behavioral regressions.

**Acceptance Criteria**:
- Form POSTs to the same `{{ url_for('show_login') }}` endpoint
- Username and password fields use the same `name` attributes (`user`, `pass`)
- The hidden `target` field is preserved with `{{ target }}` value
- The `{{ realm }}` variable is displayed in the page title and heading
- The `{{ error }}` variable is displayed when present
- The page works correctly when served by the Flask/Jinja2 template engine

## Functional Requirements

### FR-001: Self-Contained HTML Template
The login page template (`login.html`) must be a single file containing all CSS (inline `<style>`) and JavaScript (inline `<script>`) with no external resource references.

### FR-002: System Font Typography
All text must use a CSS system font stack. No `@font-face` declarations referencing external files. No `@import` rules for external font services.

### FR-003: CSS-Only Icons
Icon fonts from external services must be replaced with either CSS-only solutions (borders, transforms, Unicode characters) or removed entirely. No icon font `@import` rules.

### FR-004: Native DOM Interactivity
All JavaScript interactions (focus effects, form validation feedback) must use native DOM APIs (`document.querySelector`, `addEventListener`, `classList`, etc.). No external JavaScript libraries.

### FR-005: Responsive Layout
The login form must be centered and usable on viewports from 320px to 2560px wide. The form must not overflow on small screens or appear tiny on large screens.

### FR-006: Template Variable Compatibility
The template must preserve all existing Jinja2 template variables and their usage:
- `{{ realm }}` in page title and heading
- `{{ url_for('show_login') }}` as form action
- `{{ error }}` for error message display
- `{{ target }}` as hidden field value

### FR-007: Visual Error Feedback
Error messages (`{{ error }}`) must be displayed in a visually distinct manner (colored background/border, icon, or similar treatment) so users immediately notice authentication failures.

## User Scenarios & Testing

### Scenario 1: Successful Login
1. User navigates to a protected resource
2. nginx redirects to the login page
3. User sees a clean, modern login form with the realm name displayed
4. User enters credentials and submits
5. On success, user is redirected to the original target URL

### Scenario 2: Failed Login
1. User submits incorrect credentials
2. The login page reloads with an error message prominently displayed
3. The form fields are ready for re-entry

### Scenario 3: Air-Gapped Environment
1. The daemon runs in a network with no internet access
2. User navigates to the login page
3. The page renders completely with all styling and interactivity
4. No browser console errors related to failed resource loads

### Scenario 4: Mobile Device Access
1. User accesses the login page from a mobile phone (320px viewport)
2. The form is readable and usable without horizontal scrolling
3. Input fields are large enough for touch interaction

### Scenario 5: Keyboard-Only Navigation
1. User navigates the login form using only the keyboard
2. Tab order moves logically: username -> password -> submit button
3. Focus states are clearly visible on each element
4. Enter key submits the form

## Success Criteria

### Measurable Outcomes
- **SC-001**: The login page makes exactly zero HTTP requests to external domains (verifiable via browser dev tools Network tab)
- **SC-002**: The page loads and renders fully in under 1 second on a local network with no internet access
- **SC-003**: The login form is usable on viewports from 320px to 2560px wide without horizontal scrolling or layout breakage
- **SC-004**: All existing integration tests continue to pass without modification (form field names, POST endpoint, template variables unchanged)

## Assumptions

- The existing Jinja2 template engine and Flask route structure remain unchanged
- The login page is the only template in the project; no shared component library exists
- No dark mode toggle is required — the page is dark-themed by default
- The page does not need to support browsers older than 3 years (modern CSS features like `flexbox`, `grid`, custom properties are acceptable)
- Static assets directory (`static/`) may be used if needed, but inline CSS/JS is preferred for simplicity
