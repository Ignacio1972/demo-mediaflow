# MediaFlow v2.1 - Instalacion Rapida

**Ultima actualizacion**: 2026-01-26
**Probado en**: Ubuntu 22.04 LTS (Vultr VPS)

---

## Prerequisitos

- VPS Ubuntu 22.04 LTS (minimo 2GB RAM)
- Dominio apuntando al VPS
- API Keys: ElevenLabs + Anthropic

---

## Instalacion en 15 Pasos

### 1. Actualizar sistema

```bash
apt update && apt upgrade -y
```

### 2. Instalar Node.js 20 (CRITICO)

```bash
# Ubuntu 22.04 viene con Node 12 - DEBE actualizarse
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt remove -y libnode-dev 2>/dev/null
apt install -y nodejs

# Verificar
node -v  # Debe ser v20.x.x
```

### 3. Instalar dependencias

```bash
apt install -y \
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

### 4. Crear usuario

```bash
useradd -r -s /bin/bash -m -d /var/www/mediaflow mediaflow
```

### 5. Configurar PostgreSQL

```bash
systemctl start postgresql
systemctl enable postgresql

sudo -u postgres psql << EOF
CREATE USER mediaflow WITH PASSWORD 'TU_PASSWORD_SEGURO';
CREATE DATABASE mediaflow OWNER mediaflow;
GRANT ALL PRIVILEGES ON DATABASE mediaflow TO mediaflow;
EOF
```

### 6. Clonar/Copiar proyecto

```bash
# Opcion A: Git
sudo -u mediaflow git clone https://github.com/tu-org/mediaflow-v2.git /var/www/mediaflow

# Opcion B: rsync desde otro servidor
rsync -avz --exclude 'node_modules' --exclude 'venv' --exclude '__pycache__' \
    origen:/var/www/mediaflow-v2/ /var/www/mediaflow/
chown -R mediaflow:mediaflow /var/www/mediaflow
```

### 7. Configurar backend

```bash
sudo -u mediaflow bash << 'EOF'
cd /var/www/mediaflow/backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF
```

### 8. Crear .env

```bash
cat > /var/www/mediaflow/backend/.env << 'EOF'
# General
APP_NAME=MediaFlow
APP_VERSION=2.1.0
APP_ENV=production
DEBUG=False

# Server - PUERTO 3001 para compatibilidad con Azuracast
HOST=0.0.0.0
PORT=3001

# Database
DATABASE_URL=postgresql+asyncpg://mediaflow:TU_PASSWORD_SEGURO@localhost:5432/mediaflow
DB_ECHO=False

# APIs (REQUERIDAS)
ELEVENLABS_API_KEY=tu_elevenlabs_key
ANTHROPIC_API_KEY=tu_anthropic_key
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
ELEVENLABS_BASE_URL=https://api.elevenlabs.io/v1
CLAUDE_MODEL=claude-sonnet-4-20250514

# Storage
STORAGE_PATH=/var/www/mediaflow/storage
AUDIO_PATH=/var/www/mediaflow/storage/audio
MUSIC_PATH=/var/www/mediaflow/storage/music
SOUNDS_PATH=/var/www/mediaflow/storage/sounds
TEMP_PATH=/var/www/mediaflow/storage/temp
MAX_UPLOAD_SIZE=52428800

# CORS (cambiar dominio)
CORS_ORIGINS=["https://TU_DOMINIO","http://TU_DOMINIO"]

# Security
SECRET_KEY=genera_key_segura_con_openssl_rand_hex_32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Audio
DEFAULT_TARGET_LUFS=-16.0
DEFAULT_SAMPLE_RATE=44100
DEFAULT_BITRATE=192k

# Tenant
TENANT_ID=tu_tenant
TENANT_NAME=Tu Nombre
TENANT_LOGO=/images/mediaflow-logo.png
TENANT_PRIMARY_COLOR=#4F46E5
TENANT_SECONDARY_COLOR=#7C3AED
TENANT_DOMAIN=TU_DOMINIO
TENANT_FAVICON=/favicon.ico
EOF

chown mediaflow:mediaflow /var/www/mediaflow/backend/.env
chmod 600 /var/www/mediaflow/backend/.env
```

### 9. Crear directorios storage

```bash
sudo -u mediaflow mkdir -p /var/www/mediaflow/storage/{audio,music,sounds,temp}
```

### 10. Ejecutar migraciones

```bash
sudo -u mediaflow bash -c '
cd /var/www/mediaflow/backend
source venv/bin/activate
alembic upgrade head
'
```

### 11. Construir frontend

```bash
cd /var/www/mediaflow/frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### 12. Configurar Systemd

```bash
cat > /etc/systemd/system/mediaflow.service << 'EOF'
[Unit]
Description=MediaFlow v2.1 Backend API
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=mediaflow
Group=mediaflow
WorkingDirectory=/var/www/mediaflow/backend

# IMPORTANTE: Incluir /usr/bin para ffprobe
Environment="PATH=/var/www/mediaflow/backend/venv/bin:/usr/bin:/usr/local/bin"
EnvironmentFile=/var/www/mediaflow/backend/.env

ExecStart=/var/www/mediaflow/backend/venv/bin/uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 3001 \
    --workers 4 \
    --loop uvloop \
    --http httptools

Restart=always
RestartSec=5
StartLimitInterval=60
StartLimitBurst=3

LimitNOFILE=65536
LimitNPROC=4096

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/www/mediaflow/storage
ReadWritePaths=/var/www/mediaflow/backend

StandardOutput=journal
StandardError=journal
SyslogIdentifier=mediaflow

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable mediaflow
systemctl start mediaflow
systemctl status mediaflow
```

### 13. Configurar Nginx

```bash
cat > /etc/nginx/sites-available/mediaflow << 'EOF'
upstream mediaflow_backend {
    server 127.0.0.1:3001;
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

    location /ws/ {
        proxy_pass http://mediaflow_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    location /storage/audio/ {
        alias /var/www/mediaflow/storage/audio/;
        expires 7d;
    }

    location /storage/music/ {
        alias /var/www/mediaflow/storage/music/;
        expires 30d;
    }

    location /storage/sounds/ {
        alias /var/www/mediaflow/storage/sounds/;
        expires 30d;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF

ln -sf /etc/nginx/sites-available/mediaflow /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
```

### 14. Firewall

```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

### 15. SSL

```bash
certbot --nginx -d TU_DOMINIO --non-interactive --agree-tos --email tu@email.com --redirect
```

---

## Verificacion

```bash
# Backend
curl http://localhost:3001/api/v1/config/tenant

# Frontend
curl -I https://TU_DOMINIO/

# Logs
journalctl -u mediaflow -f
```

---

## Problemas Comunes y Soluciones

### Error: ffprobe not found

**Causa**: El PATH del servicio systemd no incluye /usr/bin

**Solucion**:
```bash
# Editar servicio
sed -i 's|Environment="PATH=/var/www/mediaflow/backend/venv/bin"|Environment="PATH=/var/www/mediaflow/backend/venv/bin:/usr/bin:/usr/local/bin"|' /etc/systemd/system/mediaflow.service
systemctl daemon-reload
systemctl restart mediaflow
```

### Error: modelo Claude no existe

**Causa**: El modelo `claude-3-5-sonnet-20241022` ya no existe

**Solucion**:
```bash
sed -i 's/claude-3-5-sonnet-20241022/claude-sonnet-4-20250514/' /var/www/mediaflow/backend/.env
systemctl restart mediaflow
```

### Error: Node.js syntax error

**Causa**: Ubuntu 22.04 tiene Node 12, se requiere Node 20

**Solucion**:
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt remove -y libnode-dev
apt install -y nodejs
```

### Error: datetime('now') does not exist

**Causa**: Migraciones con sintaxis SQLite en PostgreSQL

**Solucion**: Editar archivos en `alembic/versions/`:
- Cambiar `datetime('now')` por `NOW()`
- Cambiar `1`/`0` por `true`/`false` en booleanos

### Puerto 8000 ocupado por Azuracast

**Causa**: Azuracast usa puerto 8000 por defecto

**Solucion**: MediaFlow usa puerto 3001
- En `.env`: `PORT=3001`
- En systemd: `--port 3001`
- En nginx: `server 127.0.0.1:3001`

---

## Comandos Utiles

```bash
# Reiniciar backend
systemctl restart mediaflow

# Ver logs
journalctl -u mediaflow -f

# Reiniciar nginx
systemctl reload nginx

# Estado de servicios
systemctl status mediaflow nginx postgresql
```

---

*Documento basado en instalacion exitosa VPS Vultr - 2026-01-26*
