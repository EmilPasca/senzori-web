FROM python:3.12-slim

ARG APP_VERSION=1.0.0
ENV APP_VERSION=${APP_VERSION}
LABEL org.opencontainers.image.version=${APP_VERSION}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py atelier_senzori.db ./
COPY static ./static
COPY templates ./templates

ENV FLASK_APP=app.py
ENV FLASK_DEBUG=1
ENV DATABASE=/app/atelier_senzori.db
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
