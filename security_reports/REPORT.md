# Security Audit Report — exercitii_03

**Run:** exercitii_03-run-1  
**Profile:** quick  
**Commit:** 5adfa78f (branch: auth, dirty: README.md, backup.sh)  
**Date:** 2026-11-17  
**Scope:** app.py, backup.sh, templates/, Dockerfile, docker-compose.yml, .env

> **Coverage note:** This is a quick-profile single-pass audit. It covers all in-scope
> surfaces in one hunter wave with no independent second verifier pass. It does not imply
> that the application is free of additional vulnerabilities.

---

## Summary

| Severity | Count |
|---|---|
| High | 5 |
| Medium | 2 |
| Low | 1 |
| Informational | 2 |
| Needs validation | 2 |

The application contains several **high-severity** vulnerabilities that together allow an
unauthenticated attacker to gain full access to the application. The most exploitable paths
are:

1. **Known fallback secret key → session forgery**: if `SECRET_KEY` is not set at runtime,
   the hardcoded default allows any attacker to mint a valid admin session cookie with zero
   authentication.
2. **Reflected XSS** in `/salut/<nome>`: an unescaped f-string response allows script
   execution in any visitor's browser.
3. **Plaintext passwords**: a database read (via Docker image inspection, file theft, or
   backup) immediately yields all user credentials.
4. **Debug mode in production image**: the Werkzeug interactive debugger is enabled in the
   Dockerfile and allows code execution when a 500 error can be triggered.

None of the authorization checks (ownership enforcement on sensor access) show bypasses;
IDOR protection is correctly implemented.

---

## Findings overview

### HIGH — F-001: Reflected XSS in `/salut/<nome>`
`app.py:196` returns an f-string with the raw URL path parameter as `text/html`. Any
visitor tricked into clicking a crafted URL executes attacker-controlled JavaScript in
their browser under the app's origin. Example: `/salut/<img src=x onerror=alert(1)>`.

**Fix:** `from markupsafe import escape` and use `escape(nome)` in the return value, or
return `mimetype='text/plain'`.

---

### HIGH — F-002: Plaintext password storage
Passwords are inserted (`app.py:91–98`) and compared (`app.py:157–162`) as plaintext
strings with no hashing. Any database read yields all credentials immediately.

**Fix:** Hash with `bcrypt` or `argon2-cffi` on write; verify with the library's check
function on login. Never store or compare the raw string.

---

### HIGH — F-003: Admin credentials hardcoded in source and displayed on login page
`admin/admin123` is seeded in `app.py:91` and printed verbatim on the public `/login`
page (`templates/login.html:24`). No authentication is needed to retrieve admin
credentials.

**Fix:** Remove the hint from `login.html`. Seed credentials from environment variables,
not source literals.

---

### HIGH — F-004: Known fallback `SECRET_KEY` enables session cookie forgery
`app.py:9` falls back to `"dev-only-secret-key"` when `SECRET_KEY` is unset.
`docker-compose.yml:6` falls back to `"change-this-development-key"`. Either known
string lets an attacker use `flask-unsign` or `itsdangerous` to forge a session cookie
claiming any username, including admin, with no interaction.

**Fix:** Remove both fallback literals. Raise a hard startup error when `SECRET_KEY` is
absent or shorter than 32 bytes.

---

### HIGH — F-005: `FLASK_DEBUG=1` baked into production Dockerfile
`Dockerfile:17` sets `FLASK_DEBUG=1`, enabling the Werkzeug interactive Python debugger
on every 500 error page. The debugger PIN can be derived from container filesystem
metadata (documented attack class). Any user who triggers an unhandled exception gains
a Python shell inside the container.

**Fix:** Remove `ENV FLASK_DEBUG=1` from `Dockerfile`. Use a `docker-compose.override.yml`
for local development only.

---

### MEDIUM — F-006: SQLite database with plaintext credentials baked into Docker image
`Dockerfile:9` copies `atelier_senzori.db` into the image at build time. Combined with
F-002, anyone who pulls the image can run `sqlite3 atelier_senzori.db 'SELECT * FROM users'`
and obtain all plaintext passwords.

**Fix:** Remove `atelier_senzori.db` from the `COPY` instruction. Initialize the database
from hashed, environment-supplied credentials at first run.

---

### MEDIUM — F-007: No rate limiting on `/login` endpoint
The login route (`app.py:140–178`) has no attempt counter, lockout, delay, or CAPTCHA.
An attacker can make unlimited login requests at network speed.

**Fix:** Add `Flask-Limiter` with a per-IP and per-username policy (e.g., 10 attempts
per minute), or implement exponential backoff and temporary lockout.

---

### LOW — F-008: Backup preserves plaintext passwords
`backup.sh` pseudonymizes `users.username`, `senzori.cod`, and `senzori.locatie` but
leaves the `users.password` column unchanged as plaintext in every backup file.

**Fix:** Add `UPDATE users SET password = 'REDACTED'` after pseudonymizing usernames.
(Moot once F-002 is fixed, since hashed values are already not reversible.)

---

### INFORMATIONAL — F-010: Missing HTTP security response headers
Flask default responses include no `Content-Security-Policy`, `X-Frame-Options`,
`X-Content-Type-Options`, or `Referrer-Policy` headers. This amplifies the impact of
F-001 and allows clickjacking.

**Fix:** Add `Flask-Talisman` or an `after_request` hook with the four headers above.

---

### INFORMATIONAL — F-011: Demo credentials exposed to authenticated users
`templates/profile.html:17–21` renders `alina / alina123` or `cosmin / cosmin123` in
the page body after login. Minimal impact (credential already used to log in), but
reinforces plaintext credential handling.

**Fix:** Remove the hints from the profile template.

---

## Needs validation

See `NEEDS-VALIDATION.md` for two items requiring owner confirmation:

- **NV-001**: Session cookie `Secure` flag absent; impact depends on whether HTTPS is
  enforced at the proxy layer.
- **NV-002**: CSRF on `/form` POST is implicitly mitigated by Flask 3.1.3's
  `SameSite=Lax` default, but this is not explicitly configured and should be confirmed
  or hardened with explicit configuration or Flask-WTF tokens.

---

## Authorization (IDOR) — no finding

The sensor ownership check is correctly implemented and consistently applied across the
HTML route (`app.py:207`), the GET API (`app.py:318`), the PUT API (`app.py:335`), and
the DELETE API (`app.py:407`). The separate `senzorul_apartine_utilizatorului` helper
(`app.py:287–298`) is called on every ownership-sensitive operation. No IDOR bypass was
found.
