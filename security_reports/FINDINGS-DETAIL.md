# Findings Detail — exercitii_03 run-1

---

## F-001 · HIGH · Reflected XSS in `/salut/<nome>`

**CWE:** CWE-79 — Improper Neutralization of Input During Web Page Generation

**Affected file:** `app.py:196`

```python
@app.get("/salut/<nume>")
def salut(nume):
    return f"Salut, {nume}! Bine ai venit în aplicația Flask."
```

Flask returns a bare string as `Content-Type: text/html; charset=utf-8`. The `<nume>`
path parameter is an untyped string converter that accepts any characters. The value is
interpolated into HTML with no escaping. All other templates in the application use
Jinja2's auto-escaping and are not affected.

**Proof of concept (passive — do not probe live systems):**
```
GET /salut/<img src=x onerror=alert(document.origin)>
```
This URL, when visited by any browser user, executes `alert(document.origin)` under the
app's origin. A weaponized payload could make authenticated API requests on behalf of the
victim and exfiltrate their sensor data.

Note: Flask 3.1.3 sets `SESSION_COOKIE_HTTPONLY=True` by default, so direct
`document.cookie` theft is blocked. Script execution under the origin remains exploitable
for authenticated request forgery and UI redressing.

**Smallest fix:**
```python
from markupsafe import escape

@app.get("/salut/<nume>")
def salut(nume):
    return f"Salut, {escape(nume)}! Bine ai venit în aplicația Flask."
```
Or, if plain text is sufficient:
```python
from flask import Response
return Response(f"Salut, {nume}! Bine ai venit.", mimetype="text/plain")
```

---

## F-002 · HIGH · Plaintext password storage

**CWE:** CWE-256 — Plaintext Storage of a Password

**Affected files:** `app.py:91–98` (seed), `app.py:157–162` (login query)

Seed (`app.py:91`):
```python
con.execute(
    "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
    ("admin", "admin123"),
)
```

Login query (`app.py:157`):
```python
query = "SELECT username FROM users WHERE username = ? AND password = ?"
user = con.execute(query, (username, password)).fetchone()
```

The `password` column of the `users` table stores plaintext strings. Database file
access (via Docker image layer inspection — see F-006 — or direct file theft) immediately
yields all credentials. The `test_auth.py:46` test asserts
`user == ("admin", "admin123")` confirming the design intent is plaintext.

**Smallest fix:**
```python
# requirements.txt: add bcrypt
import bcrypt

# On seed / registration:
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
con.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))

# On login:
row = con.execute("SELECT password FROM users WHERE username = ?", (username,)).fetchone()
if row is None or not bcrypt.checkpw(password.encode(), row[0]):
    # login failed
```

---

## F-003 · HIGH · Hardcoded admin credentials in source + public disclosure on login page

**CWE:** CWE-798 — Use of Hard-coded Credentials

**Affected files:** `app.py:91`, `templates/login.html:24`

Source (`app.py:91`):
```python
("admin", "admin123"),
```

Login page (`templates/login.html:24`):
```html
<p class="hint">Cont demo: <strong>admin</strong> / <strong>admin123</strong></p>
```

The admin credentials are both committed to source (discoverable via git history or
source review) and rendered to any unauthenticated visitor of `/login`. Combined with
F-002 and F-004, this gives an attacker a complete authentication bypass with no
enumeration needed.

**Smallest fix:**
1. Remove line 24 from `login.html`.
2. Replace hardcoded seed literals with environment variable reads:
```python
admin_password = os.environ.get("ADMIN_PASSWORD")
if admin_password:
    con.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
                ("admin", hash_password(admin_password)))
```

---

## F-004 · HIGH · Known fallback `SECRET_KEY` enables Flask session cookie forgery

**CWE:** CWE-321 — Use of Hard-coded Cryptographic Key

**Affected files:** `app.py:9`, `docker-compose.yml:6`

```python
# app.py:9
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-secret-key")
```

```yaml
# docker-compose.yml:6
SECRET_KEY: ${SECRET_KEY:-change-this-development-key}
```

Flask's client-side session cookies are HMAC-signed with `SECRET_KEY`. If `SECRET_KEY`
is not provided at runtime, the app starts silently with the known literal. Using
`flask-unsign` (a public tool):

```
# Passive demonstration only — not to run against deployed services
flask-unsign --sign --secret "dev-only-secret-key" --cookie '{"username": "admin"}'
```

The resulting token authenticates as admin on any instance using the fallback key.

**Smallest fix:**
```python
import os, sys

_key = os.environ.get("SECRET_KEY", "")
if len(_key) < 32:
    sys.exit("SECRET_KEY must be set to a random string of at least 32 characters.")
app.config["SECRET_KEY"] = _key
```

Remove the fallback string from `docker-compose.yml` and require the caller to supply it.

---

## F-005 · HIGH · `FLASK_DEBUG=1` in production Dockerfile

**CWE:** CWE-94 — Improper Control of Generation of Code

**Affected file:** `Dockerfile:17`

```dockerfile
ENV FLASK_DEBUG=1
```

Flask debug mode enables the Werkzeug interactive debugger. When an unhandled exception
occurs, the error page renders a Python REPL accessible from the browser. The PIN
protecting it is derived from machine-local data (documented derivation path published
in multiple CVE reports in the CWE-94 / Werkzeug class). Inside a container the relevant
values are predictable.

Any user who can trigger a 500 error (e.g., sending a malformed JSON body to an API
endpoint that crashes before `get_json(silent=True)` can catch it) may gain interactive
Python execution inside the container with access to all container secrets and volumes.

**Smallest fix:**
Remove line 17 from `Dockerfile`. For local development:
```yaml
# docker-compose.override.yml (not committed or deployed)
services:
  flask:
    environment:
      FLASK_DEBUG: "1"
```

---

## F-006 · MEDIUM · SQLite database baked into Docker image

**CWE:** CWE-312 — Cleartext Storage of Sensitive Information

**Affected file:** `Dockerfile:9`

```dockerfile
COPY app.py atelier_senzori.db ./
```

The populated `atelier_senzori.db` file is copied into the image at `/app/`. Combined
with F-002 (plaintext passwords), anyone who pulls the image can read all credentials:

```
# Passive — not to run against pushed images
docker run --rm --entrypoint sqlite3 <image> /app/atelier_senzori.db "SELECT * FROM users"
```

Note: in `docker-compose.yml` deployment, `DATABASE=/data/atelier_senzori.db` points to
a volume, so the image copy is not used at runtime — but it remains inspectable in the
image layer.

**Smallest fix:**
```dockerfile
COPY app.py .
COPY static ./static
COPY templates ./templates
```
Initialize the database at container startup from hashed, environment-supplied values.

---

## F-007 · MEDIUM · No rate limiting on `/login`

**CWE:** CWE-307 — Improper Restriction of Excessive Authentication Attempts

**Affected file:** `app.py:140–178`

The login handler performs a direct database lookup on every POST with no throttling.
There is no counter, lockout, exponential backoff, or IP-based limit. Combined with
F-003 (known username) and F-002 (credential value already exposed), the absence of
rate limiting amplifies all other credential-related findings.

**Smallest fix:**
```python
# requirements.txt: add Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    ...
```

---

## F-008 · LOW · Backup preserves plaintext passwords

**CWE:** CWE-312

**Affected file:** `backup.sh:49–55`

```python
for user_id, username in backup.execute("SELECT id, username FROM users").fetchall():
    backup.execute(
        "UPDATE users SET username = ? WHERE id = ?",
        (pseudonym("user", username), user_id),
    )
```

Only `username` is pseudonymized. The `password` column is never touched. Every backup
file produced by this script contains all plaintext passwords. Because backups are
typically stored with looser access controls than production databases, this widens the
exposure window.

**Smallest fix:**
Add after the username loop:
```python
backup.execute("UPDATE users SET password = 'REDACTED'")
```

---

## F-010 · INFORMATIONAL · Missing HTTP security headers

**Affected file:** `app.py` (no after_request hook)

Flask's default responses include none of:
- `Content-Security-Policy` (mitigates XSS — directly relevant to F-001)
- `X-Frame-Options: DENY` (mitigates clickjacking)
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: same-origin`

**Smallest fix:**
```python
from flask_talisman import Talisman
Talisman(app, content_security_policy={"default-src": "'self'"})
```
Or a manual `after_request` hook if Talisman is not desired.

---

## F-011 · INFORMATIONAL · Demo credentials in profile template

**Affected file:** `templates/profile.html:17–21`

```jinja
{% if username == "alina" %}
<p>Cont demo: <code>alina / alina123</code></p>
{% elif username == "cosmin" %}
<p>Cont demo: <code>cosmin / cosmin123</code></p>
{% endif %}
```

Minimal independent impact (the user already authenticated with these credentials), but
renders plaintext passwords in an HTTP response body, reinforcing the plaintext handling
pattern. Remove both branches from the template.
