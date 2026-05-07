FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential

COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app
COPY gunicorn_conf.py .
COPY scripts ./scripts

RUN addgroup --system app \
    && adduser --system --ingroup app app \
    && mkdir -p /app/uploads /app/secrets/google \
    && chown -R app:app /app

USER app

EXPOSE 8000

CMD ["sh", "-c", "python -m scripts.wait_for_db && alembic upgrade head && gunicorn app.main:app -k uvicorn.workers.UvicornWorker -c gunicorn_conf.py"]
