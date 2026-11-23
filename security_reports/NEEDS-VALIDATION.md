# Needs Validation — exercitii_03 run-1

These items have a source-grounded hypothesis but require owner-observed or
deployment-specific facts that are not present in the repository.

---

## NV-001 · Session cookie `Secure` flag absent

**Hypothesis:** Flask 3.1.3 defaults `SESSION_COOKIE_SECURE` to `False`. When the app is
accessed over plain HTTP (no TLS-terminating reverse proxy), the signed session cookie is
transmitted in cleartext on every request. A network observer between the client and
server can capture it and replay it for session hijacking.

**Source trace:** `app.py:9` — `SESSION_COOKIE_SECURE` is never set in `app.config`.
Flask 3.1.3 default is `False`.

**Missing fact:** Whether all deployment environments enforce HTTPS at a proxy layer
before traffic reaches Flask. Neither `Dockerfile` nor `docker-compose.yml` configures
a TLS proxy or sets `SESSION_COOKIE_SECURE=True`.

**Validation plan (owner action):**
1. Confirm whether a TLS proxy (nginx, Caddy, Traefik) sits in front of Flask in
   every deployment (dev, staging, production).
2. If yes: add `SESSION_COOKIE_SECURE=True` to `app.config` and set
   `SESSION_COOKIE_SAMESITE="Strict"` explicitly for defence in depth.
3. If no: also enforce HTTPS everywhere and redirect HTTP → HTTPS.

---

## NV-002 · CSRF on `/form` POST — implicit mitigation only

**Hypothesis:** `POST /form` (`app.py:226–248`) and the `<form>` in `templates/form.html`
carry no CSRF token. A cross-origin attacker page could submit a sensor-creation request
on behalf of a logged-in victim. Flask 3.1.3 defaults `SESSION_COOKIE_SAMESITE` to
`"Lax"`, which prevents the session cookie from being sent on cross-origin subresource
requests and cross-origin form submissions in mainstream browsers. This provides
significant de-facto CSRF protection, but it is implicit rather than explicit.

**Source trace:** `templates/form.html:59` — `<form id="senzor-form" method="post"
action="/form">` with no hidden CSRF field. `app.py:226` — no token check.

**Missing fact:** Confirmation that `SESSION_COOKIE_SAMESITE` is not overridden to
`None` or `""` anywhere in the deployment config, and that the Flask version in use
does apply `Lax` as the default.

**Validation plan (owner action):**
1. Verify `SESSION_COOKIE_SAMESITE` is not overridden in `app.config` or any config file.
2. For belt-and-suspenders, either:
   a. Set `app.config["SESSION_COOKIE_SAMESITE"] = "Strict"` explicitly, or
   b. Add Flask-WTF and use `{{ form.hidden_tag() }}` in every state-changing form.
