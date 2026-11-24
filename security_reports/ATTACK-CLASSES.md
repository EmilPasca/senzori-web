# Attack Classes

This project is a small Flask, SQLite, HTML, JSON API, and Docker application. Relevant classes are selected below; each candidate finding requires a source trace, affected principal, observable result, and smallest effective fix.

## Injection and output encoding

- Reflected XSS through route parameters returned as HTML.
- Review Jinja2 templates and any future JavaScript sinks for untrusted input.

## Authentication and sessions

- Session-key fallback and cookie forgery.
- Plaintext or weak credential handling and legacy password migration.
- Login brute force and account lockout policy.
- Logout and session invalidation behavior.

## Access control

- Per-sensor ownership for HTML and REST routes.
- Ensure future create, update, delete, list, and export paths enforce ownership consistently.

## Cross-site requests

- `/form` POST currently has no CSRF token.
- Explicit SameSite and, where required, origin/token controls need deployment and browser confirmation.

## Data and backup handling

- Pseudonymization must not be confused with credential removal or encryption.
- A database copy or backup can expose credential and personal data if password and identifier fields are not protected.

## Deployment and supply chain

- Debug mode, image contents, secret fallback, SQLite persistence, and dependency versions.
- Dependency data belongs in `dependency.json`; confirmed or pending findings belong in `findings.json`.
