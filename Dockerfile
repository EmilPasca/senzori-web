FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py atelier_senzori.db ./
COPY static ./static
COPY templates ./templates

ENV FLASK_APP=app.py
ENV FLASK_DEBUG=0
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
