FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libffi-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY main.py ./
COPY app/config.py ./app/

EXPOSE 5000

CMD exec gunicorn -w 2 -k gthread --threads 4 -b 0.0.0.0:${PORT} 'app.app:create_app()'
