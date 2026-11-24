# Client-Side and Browser Security

## Scope

The application renders Jinja2 templates for authenticated and unauthenticated pages. It has no JavaScript application framework or browser storage usage.

## Source observations

- Jinja2 template interpolation is the normal HTML rendering path and applies auto-escaping.
- `/salut/<nume>` is a separate plain-string route that does not escape attacker-controlled path data before returning `text/html`.
- The login and profile templates display demo credentials for educational use.
- No CSP, frame restriction, or explicit `Referrer-Policy` is configured by an `after_request` hook.

## Required controls

- Escape dynamic text in routes that construct HTML, or set plain-text content where HTML is not required.
- Add security response headers appropriate to the application, especially CSP and frame protection.
- Test browser behavior with dummy accounts and local-only fixtures; do not use live users or shared services.

## Related records

- Reflected XSS: `F-001` in `findings.json`
- Missing security headers: `F-010` in `findings.json`
