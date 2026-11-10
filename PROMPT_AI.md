# Atelier: testare asistata de AI

Exemplu de prompt:

> Avem un endpoint Flask `POST /api/senzori` care primeste `cod` si `locatie`.
> Contract: 201 pentru creare, 400 la campuri lipsa/blank, 409 la cod duplicat.
> Propune 8 cazuri de test pozitive/negative, cu valori-limita si date de test.
> Apoi genereaza un draft pytest care foloseste fixture-ul `client`.
> Nu inventa alte reguli de business. Marcheaza orice presupunere.
> Nu utiliza date de productie, parole sau tokenuri reale.

Checklist de verificare umana:
1. Cazurile acopera contractul sau introduc presupuneri neverificate?
2. Asertiunile verifica rezultatul, nu doar codul HTTP?
3. Testele sunt independente si folosesc date izolate?
4. Codul generat ruleaza efectiv? Exista cazuri fals-pozitive?
5. Verificam si cazurile de securitate si confidentialitate relevante?
