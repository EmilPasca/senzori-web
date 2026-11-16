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

Pornește aplicația pe portul local `5000`:

```bash
docker run --name senzori-web-container \
  -p 5432:5000 \
  -e SECRET_KEY="schimba-aceasta-cheie" \
  -v "$(pwd)/atelier_senzori.db:/app/atelier_senzori.db" \
  senzori-web
```

Aplicația este disponibilă la <http://localhost:5000>. Pentru oprire:

```bash
docker stop senzori-web-container
```

Volumul păstrează baza de date între reporniri. Dacă nu ai nevoie de persistență,
poți elimina opțiunea `-v`. În PowerShell, înlocuiește `$(pwd)` cu `${PWD}`.

## Licență

Acest proiect este destinat scopurilor educaționale.
