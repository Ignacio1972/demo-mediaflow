# MediaFlow v2.1 - Guía de Deployment Completa

**Última actualización**: 2026-01-26
**Basado en**: Instalación exitosa en VPS Vultr (Mall Barrio Independencia)

---

## Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación Rápida (Script Automatizado)](#instalación-rápida)
3. [Instalación Manual Paso a Paso](#instalación-manual)
4. [Configuración Multi-Tenant](#configuración-multi-tenant)
5. [Problemas Conocidos y Soluciones](#problemas-conocidos)
6. [Docker (Alternativa)](#docker)
7. [Mantenimiento](#mantenimiento)
8. [Checklist de Verificación](#checklist)

---

## Requisitos del Sistema

### Hardware Mínimo

| Recurso | Mínimo | Recomendado |
|---------|--------|-------------|
| RAM | 2 GB | 4 GB |
| CPU | 1 vCPU | 2 vCPU |
| Disco | 20 GB SSD | 50 GB SSD |
| OS | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |

### Software Requerido

| Software | Versión | Notas |
|----------|---------|-------|
| Python | 3.11+ | **No usar 3.10 o inferior** |
| Node.js | 20 LTS | **Crítico: v12 no funciona** |
| PostgreSQL | 14+ | SQLite solo para desarrollo |
| Nginx | 1.18+ | Reverse proxy |
| FFmpeg | 4.4+ | Procesamiento de audio |

### Puertos Requeridos

| Puerto | Servicio | Firewall |
|--------|----------|----------|
| 22 | SSH | Requerido |
| 80 | HTTP | Requerido |
| 443 | HTTPS | Requerido |
| 8000 | Backend (interno) | Solo localhost |

### Servicios Externos

- **ElevenLabs API Key** - Para TTS
- **Anthropic API Key** - Para IA
- **Dominio** configurado en DNS

---

## Instalación Rápida

### Opción 1: Script Automatizado

```bash
# Descargar e instalar
curl -sSL https://raw.githubusercontent.com/your-org/mediaflow-v2/main/deploy/scripts/install.sh | sudo bash
```

### Opción 2: One-liner Manual

```bash
# En un VPS Ubuntu 22.04 limpio:
sudo apt update && sudo apt upgrade -y && \
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash - && \
sudo apt install -y python3.11 python3.11-venv nodejs nginx postgresql ffmpeg certbot python3-certbot-nginx git
```

---

## Instalación Manual

### Paso 1: Actualizar Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### Paso 2: Instalar Node.js 20 LTS

> ⚠️ **IMPORTANTE**: Ubuntu 22.04 viene con Node.js 12 por defecto. **DEBE** actualizarse a v20.

```bash
# Agregar repositorio NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -

# Si hay conflicto con libnode-dev:
sudo apt remove -y libnode-dev

# Instalar Node.js 20
sudo apt install -y nodejs

# Verificar versiones
node -v  # Debe mostrar v20.x.x
npm -v   # Debe mostrar v10.x.x
```

### Paso 3: Instalar Dependencias

```bash
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    nginx \
    postgresql \
    postgresql-contrib \
    certbot \
    python3-certbot-nginx \
    ffmpeg \
    git \
    curl \
    ufw
```

### Paso 4: Crear Usuario del Sistema

```bash
# Crear usuario mediaflow
sudo useradd -r -s /bin/bash -m -d /var/www/mediaflow mediaflow

# Crear directorio
sudo mkdir -p /var/www/mediaflow
sudo chown mediaflow:mediaflow /var/www/mediaflow
```

### Paso 5: Configurar PostgreSQL

```bash
# Iniciar PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Crear usuario y base de datos
sudo -u postgres psql << EOF
CREATE USER mediaflow WITH PASSWORD 'tu_password_seguro';
CREATE DATABASE mediaflow OWNER mediaflow;
GRANT ALL PRIVILEGES ON DATABASE mediaflow TO mediaflow;
EOF

# Verificar conexión
PGPASSWORD='tu_password_seguro' psql -U mediaflow -d mediaflow -c "SELECT 1;"
```

### Paso 6: Clonar/Copiar Proyecto

```bash
# Opción A: Desde Git
sudo -u mediaflow git clone https://github.com/your-org/mediaflow-v2.git /var/www/mediaflow

# Opción B: Desde otro servidor con rsync
rsync -avz --exclude 'node_modules' --exclude 'venv' --exclude '__pycache__' \
    /ruta/origen/ root@servidor:/var/www/mediaflow/
```

### Paso 7: Configurar Backend

```bash
# Cambiar a usuario mediaflow
sudo -u mediaflow bash

# Ir al directorio backend
cd /var/www/mediaflow/backend

# Crear entorno virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Salir del usuario mediaflow
exit
```

### Paso 8: Crear Archivo .env

```bash
sudo -u mediaflow cat > /var/www/mediaflow/backend/.env << 'EOF'
# General
APP_NAME=MediaFlow
APP_VERSION=2.1.0
APP_ENV=production
DEBUG=False

# Server
HOST=0.0.0.0
PORT=8000

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://mediaflow:TU_PASSWORD@localhost:5432/mediaflow
DB_ECHO=False

# API Keys (REQUERIDAS)
ELEVENLABS_API_KEY=tu_elevenlabs_key
ANTHROPIC_API_KEY=tu_anthropic_key

# Storage
STORAGE_PATH=/var/www/mediaflow/storage
AUDIO_PATH=/var/www/mediaflow/storage/audio
MUSIC_PATH=/var/www/mediaflow/storage/music
SOUNDS_PATH=/var/www/mediaflow/storage/sounds
TEMP_PATH=/var/www/mediaflow/storage/temp
MAX_UPLOAD_SIZE=52428800

# CORS (cambiar por tu dominio)
CORS_ORIGINS=["https://tu-dominio.com"]

# Security
SECRET_KEY=genera_una_key_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Tenant Configuration
TENANT_ID=demo
TENANT_NAME=MediaFlow Demo
TENANT_LOGO=/images/mediaflow-logo.png
TENANT_PRIMARY_COLOR=#4F46E5
TENANT_SECONDARY_COLOR=#7C3AED
TENANT_DOMAIN=tu-dominio.com
TENANT_FAVICON=/favicon.ico
EOF

# Asegurar permisos
sudo chown mediaflow:mediaflow /var/www/mediaflow/backend/.env
sudo chmod 600 /var/www/mediaflow/backend/.env
```

### Paso 9: Ejecutar Migraciones

```bash
sudo -u mediaflow bash -c '
cd /var/www/mediaflow/backend
source venv/bin/activate
alembic upgrade head
'
```

> ⚠️ **Si las migraciones fallan**, ver sección [Problemas Conocidos](#problema-1-migraciones-sqlite-vs-postgresql).

### Paso 10: Crear Directorios de Storage

```bash
sudo -u mediaflow mkdir -p /var/www/mediaflow/storage/{audio,music,sounds,temp}
```

### Paso 11: Construir Frontend

```bash
cd /var/www/mediaflow/frontend

# Limpiar instalación previa (si existe)
rm -rf node_modules package-lock.json

# Instalar dependencias
npm install

# Construir para producción
npm run build
```

### Paso 12: Configurar Systemd

```bash
# Copiar archivo de servicio
sudo cp /var/www/mediaflow/deploy/systemd/mediaflow.service /etc/systemd/system/

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar e iniciar
sudo systemctl enable mediaflow
sudo systemctl start mediaflow

# Verificar estado
sudo systemctl status mediaflow
```

### Paso 13: Configurar Nginx

```bash
# Crear configuración
sudo cat > /etc/nginx/sites-available/mediaflow << 'EOF'
upstream mediaflow_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name TU_DOMINIO;

    client_max_body_size 50M;

    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript;

    root /var/www/mediaflow/frontend/dist;
    index index.html;

    # API Proxy
    location /api/ {
        proxy_pass http://mediaflow_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://mediaflow_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    # Storage estático
    location /storage/ {
        alias /var/www/mediaflow/storage/;
        expires 7d;
    }

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF

# Activar sitio
sudo ln -sf /etc/nginx/sites-available/mediaflow /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Probar y recargar
sudo nginx -t && sudo systemctl reload nginx
```

### Paso 14: Configurar Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### Paso 15: Configurar SSL

```bash
# Certificado Let's Encrypt
sudo certbot --nginx -d tu-dominio.com --non-interactive --agree-tos --email tu@email.com --redirect
```

---

## Configuración Multi-Tenant

### Variables de Tenant en .env

```env
# Identificador único del tenant
TENANT_ID=mallbarrio

# Nombre para mostrar
TENANT_NAME=Mall Barrio Independencia

# Ruta al logo (relativa a /public o /dist)
TENANT_LOGO=/tenants/mallbarrio/logo.png

# Colores de marca
TENANT_PRIMARY_COLOR=#E91E63
TENANT_SECONDARY_COLOR=#9C27B0

# Dominio
TENANT_DOMAIN=mbi.mediaflow.cl

# Favicon
TENANT_FAVICON=/tenants/mallbarrio/favicon.ico
```

### Estructura de Assets por Tenant

```
frontend/public/tenants/
├── demo/
│   ├── logo.png
│   ├── favicon.ico
│   └── config.json
└── mallbarrio/
    ├── logo.png
    ├── favicon.ico
    └── config.json
```

### API de Configuración

El frontend obtiene la configuración del tenant desde:

```
GET /api/v1/config/tenant
```

Respuesta:
```json
{
  "tenant_id": "mallbarrio",
  "tenant_name": "Mall Barrio Independencia",
  "tenant_logo": "/tenants/mallbarrio/logo.png",
  "tenant_primary_color": "#E91E63",
  "tenant_secondary_color": "#9C27B0",
  "tenant_domain": "mbi.mediaflow.cl",
  "tenant_favicon": "/tenants/mallbarrio/favicon.ico",
  "app_version": "2.1.0"
}
```

---

## Problemas Conocidos

### Problema 1: Migraciones SQLite vs PostgreSQL

**Síntoma:**
```
asyncpg.exceptions.UndefinedFunctionError: function datetime(unknown) does not exist
```

**Causa:** Las migraciones usan sintaxis SQLite (`datetime('now')`) que no funciona en PostgreSQL.

**Solución:** Editar los archivos de migración en `alembic/versions/`:

```python
# INCORRECTO (SQLite)
datetime('now')

# CORRECTO (PostgreSQL)
NOW()
```

```python
# INCORRECTO (SQLite boolean)
active = 1
is_default = 0

# CORRECTO (PostgreSQL boolean)
active = true
is_default = false
```

**Archivo afectado:** `a1b2c3d4e5f6_add_ai_clients_table.py`

---

### Problema 2: Node.js Versión Incorrecta

**Síntoma:**
```
SyntaxError: Unexpected reserved word
    at await import('source-map-support')
```

**Causa:** Ubuntu 22.04 instala Node.js 12 por defecto. Vite requiere Node.js 18+.

**Solución:**
```bash
# Remover conflictos
sudo apt remove -y libnode-dev

# Instalar Node.js 20 desde NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt install -y nodejs

# Verificar
node -v  # Debe ser v20.x.x
```

---

### Problema 3: Firewall Bloquea Conexiones

**Síntoma:** El sitio no es accesible desde Internet aunque nginx está corriendo.

**Causa:** UFW no tiene los puertos abiertos.

**Solución:**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

---

### Problema 4: Conflicto de Paquetes Node.js

**Síntoma:**
```
trying to overwrite '/usr/include/node/common.gypi', which is also in package libnode-dev
```

**Solución:**
```bash
sudo apt remove -y libnode-dev
sudo apt install -y nodejs
```

---

### Problema 5: Permisos de Archivos

**Síntoma:** Backend no puede escribir en storage o leer .env.

**Solución:**
```bash
sudo chown -R mediaflow:mediaflow /var/www/mediaflow
sudo chmod 600 /var/www/mediaflow/backend/.env
sudo chmod 755 /var/www/mediaflow/storage
```

---

## Docker

### Dockerfile (Backend)

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (cache de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Puerto
EXPOSE 8000

# Comando
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Dockerfile (Frontend)

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: mediaflow
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: mediaflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  backend:
    build: ./backend
    env_file: ./backend/.env
    depends_on:
      - db
    volumes:
      - ./storage:/app/storage
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
    restart: unless-stopped

volumes:
  postgres_data:
```

### Comandos Docker

```bash
# Construir
docker-compose build

# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ejecutar migraciones
docker-compose exec backend alembic upgrade head

# Parar
docker-compose down
```

---

## Mantenimiento

### Logs

```bash
# Backend (systemd)
sudo journalctl -u mediaflow -f

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Reiniciar Servicios

```bash
# Backend
sudo systemctl restart mediaflow

# Nginx
sudo systemctl reload nginx

# PostgreSQL
sudo systemctl restart postgresql
```

### Backup Base de Datos

```bash
# Backup manual
sudo -u postgres pg_dump mediaflow > backup_$(date +%Y%m%d).sql

# Restaurar
sudo -u postgres psql mediaflow < backup_20260126.sql
```

### Actualizar Aplicación

```bash
cd /var/www/mediaflow

# Obtener cambios
sudo -u mediaflow git pull

# Actualizar backend
sudo -u mediaflow bash -c '
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
'

# Reconstruir frontend
cd frontend
npm install
npm run build

# Reiniciar
sudo systemctl restart mediaflow
```

### Renovar SSL

```bash
# Certbot renueva automáticamente, pero para forzar:
sudo certbot renew --force-renewal
```

---

## Checklist

### Pre-Instalación

- [ ] VPS con Ubuntu 22.04 LTS
- [ ] Dominio configurado (DNS A record)
- [ ] API keys de ElevenLabs y Anthropic
- [ ] Acceso SSH al servidor

### Instalación

- [ ] Sistema actualizado (`apt update && upgrade`)
- [ ] Node.js 20 instalado (`node -v` = v20.x)
- [ ] Python 3.11 instalado
- [ ] PostgreSQL configurado y corriendo
- [ ] Usuario `mediaflow` creado
- [ ] Código clonado/copiado
- [ ] Backend: venv creado y dependencias instaladas
- [ ] Backend: .env configurado
- [ ] Backend: Migraciones ejecutadas
- [ ] Frontend: `npm install` completado
- [ ] Frontend: `npm run build` exitoso
- [ ] Systemd: servicio habilitado y corriendo
- [ ] Nginx: configurado y corriendo
- [ ] Firewall: puertos 80/443 abiertos
- [ ] SSL: certificado instalado

### Verificación

- [ ] `curl http://localhost:8000/api/v1/config/tenant` devuelve JSON
- [ ] `curl https://tu-dominio.com/` devuelve HTML
- [ ] `curl https://tu-dominio.com/api/v1/config/tenant` devuelve JSON
- [ ] Frontend carga correctamente en navegador
- [ ] Login funciona
- [ ] Generación de audio TTS funciona

### Post-Instalación

- [ ] Logo del tenant subido
- [ ] Backup configurado
- [ ] Monitoreo configurado (opcional)
- [ ] Documentación interna actualizada

---

## Archivos Importantes

| Archivo | Descripción |
|---------|-------------|
| `/var/www/mediaflow/backend/.env` | Configuración del backend |
| `/etc/systemd/system/mediaflow.service` | Servicio systemd |
| `/etc/nginx/sites-available/mediaflow` | Configuración Nginx |
| `/var/www/mediaflow/frontend/dist/` | Frontend compilado |
| `/var/www/mediaflow/storage/` | Archivos de audio |
| `/etc/letsencrypt/live/*/` | Certificados SSL |

---

## Contacto y Soporte

- **GitHub Issues**: https://github.com/your-org/mediaflow-v2/issues
- **Documentación**: https://docs.mediaflow.cl

---

*Documento generado basado en instalación exitosa del 26-01-2026*
