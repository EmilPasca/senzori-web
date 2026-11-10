# Modulul 8 — Laborator de testare automată

Mini-aplicație demonstrativă Flask + SQLite pentru cursul **Programator de sistem informatic (COR 251204)**. Exemplul continuă tematica registrului de senzori din M5–M7, dar este autocontinut.

## 1. Pregătire

Din directorul `modul8_laborator`:

```bash
python -m venv .venv
# Activează mediul virtual folosind comanda specifică sistemului de operare
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## 2. Teste unitare și API, fără server pornit

```bash
python -m pytest -q
python -m pytest tests/test_logic.py -v
python -m pytest tests/test_api.py -v
```

Fixture-ul `client` creează **câte o bază de date SQLite temporară pe test**, eliminând interferența între teste. Endpoint-urile sunt testate în proces prin `Flask.test_client()`.

## 3. Testul UI cu Playwright

Într-un terminal separat pornește aplicația:

```bash
python app.py
```

Dintr-un al doilea terminal (cu mediul virtual activ):

```bash
python -m pytest -m ui -q --headed
```

Deschide manual `http://127.0.0.1:5000/senzori` pentru demonstrație.
În testele UI, `BASE_URL` poate fi suprascris ca variabilă de mediu. Testul folosește un cod de senzor unic și modifică baza locală `atelier_senzori.db`.

## 4. Testul k6 (necesită k6 instalat separat)

Cu serverul Flask deja pornit:

```bash
k6 run load_test.js
```

Pragurile din exemplu (p95 sub 500 ms, erori sub 1%) sunt **didactice**, nu cerințe SLO reale. Flask development server nu este potrivit pentru benchmark/capacitate de producție. Nu rula teste de încărcare pe sisteme fără autorizare.

## 5. Testare asistată de AI

Folosește `PROMPT_AI.md` pentru generarea unor cazuri de test. Revizuiește manual ipotezele, aserțiunile, izolarea datelor și execuția.

## Resurse oficiale

- https://docs.pytest.org/en/stable/
- https://flask.palletsprojects.com/en/stable/testing/
- https://playwright.dev/python/docs/intro
- https://grafana.com/docs/k6/latest/
