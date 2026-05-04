# Implementation Plan: Modern Login Page

**Branch**: `003-modern-login-page` | **Date**: 2026-05-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003-modern-login-page/spec.md`

## Technical Context

| Aspect | Detail |
|--------|--------|
| Language | Python 3.13 (template is HTML/CSS/JS) |
| Framework | Flask 3.1.3 with Jinja2 templates |
| Template engine | Jinja2 (bundled with Flask) |
| Current template | `nginxauthdaemon/templates/login.html` (131 lines) |
| External deps to remove | Google Fonts (Roboto), weloveiconfonts.com (Entypo), jQuery 3.1.0 CDN |
| Test framework | pytest |
| Existing tests | 55 passing (none check HTML structure, only form POST behavior) |

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Security-First | PASS | No security-sensitive changes. Template only handles display. No secrets involved. |
| II. Explicit Configuration | PASS | No config changes needed. `REALM_NAME` template var unchanged. |
| III. Pluggable Architecture | N/A | No authenticator changes. |
| IV. Defensive Coding | PASS | Error display preserved via `{{ error }}` variable. |
| V. Minimal Dependencies | PASS | Net reduction: removes jQuery CDN dependency. Adds zero new dependencies. |

## Architecture Decision: Single File vs Separate Assets

**Decision**: Keep everything inline in `login.html`.

**Rationale**: The current template already uses inline `<style>`. The login page is the only template in the project. Inline CSS/JS means:
- Single file to maintain
- No cache invalidation concerns
- No static file serving complexity
- The total CSS is ~150 lines — well within reasonable inline size

**Alternative rejected**: Separate `.css` and `.js` files in `static/`. Adds serving complexity for minimal benefit on a single-page template.

## Implementation Strategy

This is a single-file replacement. The implementation has three logical phases:

### Phase 1: Template Rewrite
Rewrite `nginxauthdaemon/templates/login.html` with:
- Dark theme, purple/violet accent, glassmorphism card
- System font stack
- CSS-only interactivity (`:focus-within`, transitions)
- Semantic HTML5 (`<main>`, `<label>`, `role="alert"`)
- Responsive layout (flexbox centering, `max-width` + percentage width)
- Inline SVG for submit button icon (or no icon — text button is cleaner)
- All Jinja2 variables preserved exactly

### Phase 2: Cleanup
- Delete unused `nginxauthdaemon/static/login-sprite.png`

### Phase 3: Verification
- Run existing test suite to confirm no regressions
- Manual visual verification (browser)

## Design Tokens (from research.md)

```
--bg-primary:       #0f0f17
--bg-card:          rgba(255, 255, 255, 0.05)
--bg-input:         rgba(255, 255, 255, 0.08)
--bg-input-focus:   rgba(255, 255, 255, 0.12)
--text-primary:     rgba(255, 255, 255, 0.9)
--text-secondary:   rgba(255, 255, 255, 0.5)
--accent:           #8b5cf6
--accent-hover:     #7c3aed
--error:            #ef4444
--border:           rgba(255, 255, 255, 0.1)
--radius:           12px
--radius-lg:        16px
```

## File Change Summary

| File | Action | Description |
|------|--------|-------------|
| `nginxauthdaemon/templates/login.html` | Rewrite | Complete replacement with modern design |
| `nginxauthdaemon/static/login-sprite.png` | Delete | Unused static asset |

## Project Structure

```
nginxauthdaemon/
├── templates/
│   └── login.html          ← Rewrite (only file changed)
├── static/
│   └── login-sprite.png    ← Delete (unused)
├── nginxauthdaemon.py       (unchanged — route handler preserved)
├── config.py                (unchanged)
└── ...
```

**Structure Decision**: No structural changes. Single template file replacement within existing directory layout.

## Complexity Tracking

No constitution violations. No complexity justifications needed.
