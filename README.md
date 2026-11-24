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

Backup-ul este pseudonimizat automat: username-urile, codurile senzorilor și
locațiile sunt înlocuite cu identificatori HMAC, fără modificarea bazei originale.
Pentru rezultate consistente între backup-uri, setează o cheie secretă:

```bash
PSEUDONYMIZATION_KEY="o-cheie-lunga-si-secreta" ./backup.sh
```

Dacă variabila nu este setată, scriptul generează o cheie temporară pentru
backup-ul curent. Păstrează cheia separat dacă ai nevoie să corelezi pseudonime
între backup-uri. Pseudonimizarea nu este anonimizare și nu trebuie confundată
cu criptarea.

## Conectare cu DBeaver

Poți deschide baza de date SQLite în DBeaver:

1. Deschide DBeaver și selectează **New Database Connection**.
2. Alege **SQLite**.
3. La **Database file**, selectează:

   ```text
   /Users/marian/Proj/prog_sis_info/test_edu/exercitii_03/atelier_senzori.db
   ```

4. Apasă **Test Connection**, apoi **Finish**.

Pentru baza de date folosită de containerul Docker, copiază fișierul din volumul
containerului în directorul proiectului:

```bash
docker compose cp flask:/data/atelier_senzori.db ./atelier_senzori-docker.db
```

Apoi deschide fișierul `atelier_senzori-docker.db` în DBeaver printr-o conexiune
SQLite. Portul `5432` din `docker-compose.yml` este portul aplicației Flask,
nu un port PostgreSQL sau SQLite.

## Raport de securitate

Rapoarte și documente de delimitare pentru auditarea aplicației:

- [Raport sumar](security_reports/REPORT.md)
- [Detalii asupra constatărilor](security_reports/FINDINGS-DETAIL.md)
- [Elemente de validat](security_reports/NEEDS-VALIDATION.md)
- [Arhitectura aplicației](security_reports/architecture.md)
- [Inventarul dependențelor](security_reports/dependency.json)
- [Documente de analiză HTTP și browser](security_reports/ATTACK-CLASSES.md)

Documentele separate pentru protocoale, browser, implementare și clasele de atac sunt:[^1]

- [HTTP și autentificare](security_reports/WEB-PROTOCOL-AND-AUTH.md)
- [Securitate client-side](security_reports/CLIENT-SIDE.md)
- [Implementare în cloud și Docker](security_reports/CLOUD-AND-DEPLOYMENT.md)

[^1]: Aceste documente descriu verificările aplicate în timpul auditului și nu înlocuiesc validarea mediului de implementare.

## Contribuție și instalare

- [Ghid de contribuție](CONTRIBUTION.md)
- [Ghid de instalare](docs/INSTALATION.md)
- [Starea licenței](LICENSE.md)

## Licență

Acest proiect este destinat scopurilor educaționale.
