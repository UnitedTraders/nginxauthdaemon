# Contract: Login Page Template

## Template Path
`nginxauthdaemon/templates/login.html`

## Jinja2 Variable Contract

The template MUST render correctly when passed these variables by the Flask route handler:

```python
render_template('login.html', realm=<str>, target=<str>)           # GET (initial load)
render_template('login.html', realm=<str>, error=<str>), 401       # POST (failed login)
```

### Required Variables
- `realm` (str): Always provided. Used in `<title>` and visible heading.
- `target` (str): Always provided. Set as `value` of hidden `<input name="target">`.

### Optional Variables
- `error` (str): Only provided on failed login. When absent/empty, no error UI should be shown.

## HTML Form Contract

The `<form>` element MUST have:
```html
<form action="{{ url_for('show_login') }}" method="POST">
    <input type="text" name="user" ... />
    <input type="password" name="pass" ... />
    <input type="hidden" name="target" value="{{ target }}" />
</form>
```

These `name` attributes (`user`, `pass`, `target`) are consumed by the route handler and MUST NOT change.

## Network Request Contract

The rendered HTML page MUST make exactly **zero** HTTP requests to external domains. All resources (CSS, JS, fonts, icons) MUST be either:
1. Inline within the HTML file (`<style>`, `<script>`), or
2. Served from the daemon's own `/static/` route

## Browser Support Contract

The page MUST render and function correctly in:
- Chrome/Edge 90+ (2021+)
- Firefox 100+ (2022+)
- Safari 15+ (2021+)
- Mobile Safari (iOS 15+)
- Chrome for Android 90+

CSS features used: `flexbox`, `backdrop-filter`, `custom properties`, `::placeholder`, `:focus-within`.
