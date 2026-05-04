FROM python:3.9-slim AS base

LABEL org.opencontainers.image.source="https://github.com/UnitedTraders/nginxauthdaemon"
LABEL org.opencontainers.image.description="Authentication daemon for nginx-proxied applications"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

# Install dependencies in a single layer; copy both requirements files together
COPY requirements.txt requirements-run.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-run.txt

# Create non-root user before copying app code
RUN useradd --no-create-home --uid 1001 nginxauthdaemon

# Copy application code
COPY nginxauthdaemon nginxauthdaemon

USER 1001

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/auth/login')"]

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-k", "eventlet", "nginxauthdaemon:app"]
