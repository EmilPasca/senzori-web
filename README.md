# Aplicație pentru senzori

Aplicație simplă pentru citirea, monitorizarea și afișarea datelor furnizate de un senzor.

## Funcționalități

- Preluarea valorilor de la senzor
- Afișarea valorilor măsurate
- Monitorizarea datelor în timp real
- Autentificare și profil pentru utilizatorul conectat

## Autentificare

Accesează `/login` și folosește contul demo:

- Utilizator: `admin`
- Parolă: `admin123`

După autentificare, pagina `/profil` confirmă utilizatorul conectat. Cheia de sesiune
poate fi schimbată prin variabila de mediu `SECRET_KEY`.

Pentru demonstrația IDOR sunt disponibile conturile:

- Alina: `alina` / `alina123` (are senzorii `ALINA-TEMP-01` și `ALINA-UMID-01`)
- Cosmin: `cosmin` / `cosmin123`

Aplicația verifică proprietarul pentru fiecare senzor accesat prin ID. După autentificarea
ca Alina, notează ID-ul unui senzor din `/senzori`. Deconectează-te, autentifică-te ca
Cosmin și deschide `/senzori/<id>` sau `/api/senzori/<id>`. Accesul este refuzat cu
statusul HTTP `403`, deoarece senzorul îi aparține Alinei.

Utilizatorii sunt păstrați în tabela SQLite `users`, creată automat la pornirea
aplicației. Pentru versiunea curentă, parolele sunt stocate în format plain text
doar pentru scop educațional; nu folosi această implementare în producție.

## Utilizare

1. Conectați senzorul la sistem.
2. Porniți aplicația.
3. Urmăriți valorile afișate și verificați starea senzorului.

## Cerințe

- Un senzor compatibil
- Mediul de execuție necesar aplicației

## Rulare în container

Ai nevoie de Docker instalat. Din directorul proiectului, construiește imaginea:

```bash
docker build -t senzori-web .
```

Pornește aplicația și baza de date SQLite persistentă pe portul local `5000`:

```bash
SECRET_KEY="schimba-aceasta-cheie" docker compose up --build
```

Aplicația este disponibilă la <http://localhost:5000>. Pentru oprire:

```bash
docker compose down
```

Compose folosește un volum Docker numit `sqlite_data`, montat în `/data`.
Aplicația folosește `/data/atelier_senzori.db`; tabela `users` este creată și
populată automat la prima pornire. Pentru a șterge și baza de date persistentă:

```bash
docker compose down -v
```

## Backup

Aplicația folosește SQLite, deci backup-ul se face cu scriptul:

```bash
./backup.sh
```

Implicit, scriptul salvează copia în `./backups`. Pentru o altă bază de date sau
alt director:

```bash
DATABASE=/cale/catre/atelier_senzori.db BACKUP_DIR=./backups ./backup.sh
```

## Licență

Acest proiect este destinat scopurilor educaționale.
