# Architecture — exercitii_03

## Application

Single-process Flask 3.1.3 web application (`app.py`, ~420 lines) with both HTML UI and
RESTful JSON API. Backed by a local SQLite file (`atelier_senzori.db`).

## Trust boundaries

| Boundary | Lower-trust side | Higher-trust side |
|---|---|---|
| HTTP ingress | Internet / browser | Flask route handlers |
| Session | Browser cookie | Server-side `session["username"]` |
| Resource ownership | Authenticated user | Resource owner (another user) |
| Database | App layer | SQLite file (same process) |
| Docker registry | Image consumer | Image build context |

## Data model

```
users       (id, username, password)          -- plaintext passwords
senzori     (id, cod, locatie, owner_user_id) -- FK → users.id
citiri      (id, senzor_id, temperatura, moment)
```

## Route surface

| Method | Path | Auth required | Note |
|---|---|---|---|
| GET | / | No | Homepage |
| GET/POST | /login | No | Form login; sets session |
| GET | /profil | Yes | Displays username |
| POST | /logout | Yes | Clears session |
| GET | /salut/\<nome\> | No | Returns f-string; **no HTML escaping** |
| GET | /senzori | Yes | Lists authenticated user's sensors |
| GET | /senzori/\<id\> | Yes | Sensor detail; ownership check |
| GET/POST | /form | Yes | Add sensor HTML form |
| GET | /api/senzori | Yes | JSON list |
| GET | /api/senzori/\<id\> | Yes | JSON detail; ownership check |
| POST | /api/senzori | Yes | JSON create |
| PUT | /api/senzori/\<id\> | Yes | JSON update; ownership check |
| DELETE | /api/senzori/\<id\> | Yes | JSON delete; ownership check |

## Authentication mechanism

Flask client-side signed session cookie keyed with `SECRET_KEY`.
No password hashing: passwords stored and compared as plaintext strings.

## Deployment surface

- Local: `flask run --debug`
- Docker: `Dockerfile` + `docker-compose.yml`; `FLASK_DEBUG=1` baked into image;
  database file also baked into image at build time.
- Backup: `backup.sh` creates pseudonymized SQLite copy; pseudonymizes
  usernames/sensor codes/locations but NOT passwords.
