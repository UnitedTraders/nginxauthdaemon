# Data Model: Modern Login Page

This feature involves no persistent data model changes. The login page is a stateless Jinja2 template. Below documents the template's input/output contract.

## Template Input Variables

| Variable | Type | Source | Required | Description |
|----------|------|--------|----------|-------------|
| `realm` | string | `app.config['REALM_NAME']` | Yes | Displayed in page title and heading |
| `target` | string | Request param or header | Yes | Redirect URL after successful login (hidden field) |
| `error` | string | Route handler | No | Error message shown on failed login attempt |

## Form Output Fields

| Field Name | HTML Type | Description |
|------------|-----------|-------------|
| `user` | `text` | Username input |
| `pass` | `password` | Password input |
| `target` | `hidden` | Original URL to redirect to after login |

## Form Submission

- **Action**: `{{ url_for('show_login') }}` (resolves to `{auth_url_prefix}/login`)
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded` (standard form submission)

## State Transitions

```
[Initial Load] → GET /auth/login → Render form (no error)
[Submit]        → POST /auth/login → Success → 302 redirect to target
[Submit]        → POST /auth/login → Failure → Render form (with error)
```

## Files Affected

| File | Change Type |
|------|-------------|
| `nginxauthdaemon/templates/login.html` | Complete rewrite |
| `nginxauthdaemon/static/login-sprite.png` | Delete (unused) |
