# HTTP, Protocol, and Authentication

## Scope

This document summarizes the HTTP and authentication boundaries in the Flask application.

- Browser sessions use a Flask signed session cookie keyed by `SECRET_KEY`.
- `SESSION_COOKIE_HTTPONLY` is enabled and `SESSION_COOKIE_SAMESITE` is explicitly `Lax`.
- Login verifies a Werkzeug password hash, with migration support for legacy plaintext rows.
- Sensor HTML and API routes require authentication and enforce ownership with `owner_user_id`.
- The `/form` and `/logout` state-changing operations are not protected by explicit CSRF tokens.

## Confirmed security observations

- Demo credentials are still visible to users and in configuration/source; never reuse them outside an isolated educational environment.
- The session-key fallback and `/salut/<nume>` XSS are source-confirmed findings documented in `findings.json`.
- There is no login rate limiting.

## Validation items

See `NEEDS-VALIDATION.md` for HTTPS deployment and browser CSRF details that cannot be established from source alone.

## Validation checklist

1. Confirm a deployment secret of at least 32 random bytes is supplied as `SECRET_KEY`.
2. Confirm HTTPS termination and an appropriate `SESSION_COOKIE_SECURE` setting.
3. Confirm explicit CSRF protection or an enforced origin/same-site policy for every state-changing request.
4. Verify ownership checks remain applied to HTML, GET, POST, PUT, and DELETE paths.
