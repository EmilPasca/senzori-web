# Instalarea și rularea aplicației

Acest ghid descrie instalarea locală și în Docker a aplicației senzori-web.

## Cerințe

### Rulare locală

- Python 3.12 sau o versiune compatibilă pentru mediul Flask și testele din CI;
- `pip`;
- `git`;
- opțional, `uv` pentru gestionarea mediului definit în `pyproject.toml`.

Proiectul declară `requires-python = ">=3.14"` în `pyproject.toml`, în timp ce pipeline-ul GitHub Actions testează aplicația cu Python 3.12. Folosește Python 3.12 pentru reproducerea pipeline-ului și Python 3.14 dacă folosești în mod explicit mediul declarat de proiect.

### Rulare în Docker

- Docker Engine sau Docker Desktop;
- Docker Compose;
- un port liber pe gazdă, implicit `8001`.

## Instalare locală cu venv

Clonează proiectul și intră în directorul rădăcină:

```bash
cd senzori-web
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Comanda pentru Windows PowerShell este:

```powershell
.venv\Scripts\Activate.ps1
```

## Pornirea aplicației

Aplicația folosește baza `atelier_senzori.db` din directorul proiectului, dacă variabila `DATABASE` nu este definită.

Setează o cheie locală aleatorie pentru sesiuni și pornește Flask:

```bash
export SECRET_KEY="cheie-locala-de-test-cu-peste-32-de-octeti"
flask --app app run --host=127.0.0.1 --port=8001
```

Aplicția este disponibilă la:

- <http://127.0.0.1:8001>
- <http://127.0.0.1:8001/login>
- <http://127.0.0.1:8001/senzori>

Alternativ, API-ul poate fi pornit pe portul implicit 5000:

```bash
flask --app app run --host=127.0.0.1 --port=5000
```

Folosește `flask run --debug` numai într-un mediu local izolat. Nu expune modul debug în producție.

## Rulare cu uv

```bash
uv venv
source .venv/bin/activate
uv sync
uv run flask --app app run --host=127.0.0.1 --port=8001
```

Pentru testare:

```bash
uv run pytest -v tests/
```

## Rulare în Docker

Construiește imaginea:

```bash
docker build -t senzori-web .
```

Pornește serviciul cu o cheie locală de test:

```bash
SECRET_KEY="cheie-locala-de-test-cu-peste-32-de-octeti" docker compose up --build
```

Compose publică aplicația pe <http://localhost:8001>. Pentru oprire:

```bash
docker compose down
```

Pentru a șterge și volumul SQLite persistent:

```bash
docker compose down -v
```

Nu folosi această configurație direct în producție fără HTTPS, politici de secret și configurări explicite ale cookie-urilor de sesiune.

## Baza de date SQLite

La prima pornire, aplicația creează automat tabelele necesare și utilizatorii demo. Baza poate fi suprascrisă prin variabila `DATABASE`:

```bash
DATABASE=/cale/catre/atelier_senzori.db SECRET_KEY="..." flask --app app run
```

Pentru a deschide baza locală în DBeaver:

1. Alege o conexiune SQLite nouă.
2. Selectează fișierul `atelier_senzori.db` din rădăcina proiectului.
3. Testează conexiunea și apasă **Finish**.

Exemplul portului `5432` din documentația veche nu se aplică: aceasta este o aplicație SQLite și Compose publică Flask pe portul gazdei `8001`.

## Backup

```bash
./backup.sh
```

Implicit, copia este plasată în `backups/`. Pentru altă bază sau alt director:

```bash
DATABASE=/cale/catre/atelier_senzori.db BACKUP_DIR=./backups ./backup.sh
```

Pseudonimizarea folosește cheie opțională:

```bash
PSEUDONYMIZATION_KEY="cheie-secure-pentru-pseudonime" ./backup.sh
```

Pseudonimizarea nu este criptare și nu este echivalentă cu anonimizarea.

## Rularea testelor

```bash
python -m pytest -v tests/
python -m pytest -v tests/test_auth.py --cov=app --cov-report=term-missing
```

Pentru testul k6, pornește aplicația în Docker sau local și rulează:

```bash
k6 run tests/k6/login.js
```

## Depanare

- Dacă portul `8001` este ocupat, pornește Flask pe alt port și actualizează comenzile k6/API în consecință.
- Dacă baza nu se creează, verifică permisiunile directorului și valoarea `DATABASE`.
- Dacă Docker nu pornește, inspectează jurnalul cu `docker compose logs flask`.
- Dacă testele nu găsesc aplicația, verifică că Flask rulează pe URL-ul folosit de variabila `API_URL` sau de testele locale.
