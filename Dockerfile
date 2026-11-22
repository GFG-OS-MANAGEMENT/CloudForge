# syntax=docker/dockerfile:1

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN useradd --create-home --uid 10001 cloudforge

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=cloudforge:cloudforge backend ./backend
COPY --chown=cloudforge:cloudforge infrastructure ./infrastructure

RUN mkdir -p /app/backend/.cloudforge && chown -R cloudforge:cloudforge /app/backend/.cloudforge

USER cloudforge
WORKDIR /app/backend

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
