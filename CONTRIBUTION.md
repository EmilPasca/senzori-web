# Ghid de contribuție

Acest ghid descrie fluxul curent de dezvoltare pentru aplicația educațională senzori-web. Nu reprezintă un proces oficial aprobat până când acesta este confirmat de maintainers.

## Înainte de a contribui

- Folosește o ediție nouă de Python sau mediul virtual al proiectului.
- Nu adăuga chei reale, parole, tokenuri sau baze de date cu date personale.
- Păstrează scopul schimbarilor educațional: explicații clare, cod lizibil și teste reproductibile.
- Citiți [README.md](README.md) și [docs/INSTALATION.md](docs/INSTALATION.md) înainte de modificări.

## Configurare locală

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Pornirea aplicației:

```bash
export SECRET_KEY="cheie-locala-de-test-cu-peste-32-de-octeti"
flask --app app run --host=127.0.0.1 --port=8001
```

Variabila `SECRET_KEY` este necesară în orice mediu care nu este strict local. Pentru testele și demonstrațiile locale folosește întotdeauna valori false, separate de credențialele reale.

## Fluxul recomandat

1. Actualizează ramura locală și creează o ramură descriptivă.
2. Menține modificarea concentrată pe o singură problemă.
3. Adaugă sau actualizează testele relevante.
4. Rulează lint, teste și acoperire local.
5. Verifică diff-ul și descrie manual efectul modificării.
6. Deschide un pull request cu pași de reproducere și criterii de verificare.

Exemplu de nume de ramură:

```text
fix/session-cookie-security
feature/sensor-api-validation
docs/installation-guide
```

## Verificări

Rulează testele:

```bash
python -m pytest -v tests
```

Compilează sursele:

```bash
python -m compileall -q app.py tests
```

Rulează acoperirea Flask:

```bash
python -m pytest -v tests/test_auth.py \
  --cov=app \
  --cov-fail-under=60 \
  --cov-report=term-missing
```

Dacă sunt instalate instrumentele de dezvoltare, verifică formatarea și lint-ul:

```bash
ruff format --check app.py test.py main.py tests
ruff check app.py test.py main.py tests
bandit -r app.py test.py main.py tests -ll
```

GitHub Actions execută deja compilearea, pytest, acoperirea, Ruff, Bandit, k6 și auditul dependențelor. O modificare trebuie să fie compatibilă cu aceste verificări.

## Teste și date

- Nu modifica fișierele din `backups/` sau baza SQLite fără un motiv explicit.
- Folosește conturi demo și valori fictive în teste.
- Nu testa vulnerabilități împotriva unor sisteme publice, infrastructură partajată sau utilizatori reali.
- Verifică rezultatul IDOR și autentificarea cu doi utilizatori demo înainte de modificări ale autorizării senzorilor.

## Documentație

Pentru modificări de instalare sau utilizare, actualizează și `README.md` sau documentele din `docs/`.

Pentru modificări de securitate, descrie:

- principalul cu privilegii mai mici;
- intrarea controlabilă;
- controlul vizat;
- resursa sau utilizatorul afectat;
- fix-ul și testul de regresie.

Pentru raportarea unei probleme de securitate, nu publica date sensibile într-un issue public. Folosește un canal privat pus la dispoziție de maintainers.
