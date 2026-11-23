## Rularea testelor

Din directorul proiectului, rulează:

```bash
pytest
```

Pentru a rula doar testele din acest director:

```bash
pytest tests/
```

Pentru rezultate detaliate:

```bash
pytest -v
```

Comenzi uzuale `uv`:

```bash
# Creează și activează un mediu virtual cu uv
uv venv && source .venv/bin/activate

# Creează un mediu virtual Python
python3 -m venv .venv

# Activează mediul virtual
source .venv/bin/activate

# Instalează o dependență
python -m pip install <nume-dependență>

# Instalează toate dependențele proiectului
python -m pip install -r requirements.txt

# Instalează dependențele proiectului
uv sync

# Rulează testele în mediul virtual al proiectului
uv run pytest

# Rulează doar testele din acest director
uv run pytest tests/

# Rulează testele cu rezultate detaliate
uv run pytest -v


```

Pentru raportul de acoperire a codului Flask:

```bash
uv run pytest -v tests/test_auth.py --cov=app --cov-report=term-missing --cov-report=html:htmlcov
```


