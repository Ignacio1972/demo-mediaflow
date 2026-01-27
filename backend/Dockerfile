# MediaFlow Backend - Dockerfile
# Python 3.11 + FastAPI + FFmpeg

FROM python:3.11-slim

# Argumentos de build
ARG APP_ENV=production

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=${APP_ENV}

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (mejor cache)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios de storage
RUN mkdir -p /app/storage/audio /app/storage/music /app/storage/sounds /app/storage/temp

# Usuario no-root para seguridad
RUN useradd -m -u 1000 mediaflow && \
    chown -R mediaflow:mediaflow /app
USER mediaflow

# Puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/config/tenant || exit 1

# Comando por defecto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--loop", "uvloop", "--http", "httptools"]
