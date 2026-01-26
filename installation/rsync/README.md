# MediaFlow v2.1 - Instalacion via RSYNC

**Metodo recomendado** para nuevas instalaciones.

Copia el codigo desde un servidor funcionando, garantizando que todo esta igual.

---

## Tiempo Estimado: 15-20 minutos

| Paso | Tiempo |
|------|--------|
| Preparar servidor destino | 5 min |
| rsync del codigo | 2 min |
| Configuracion post-rsync | 5 min |
| Build frontend | 2 min |
| SSL y verificacion | 5 min |

---

## Requisitos

### Servidor Origen (funcionando)
- MediaFlow instalado y funcionando
- Acceso SSH

### Servidor Destino (nuevo VPS)
- Ubuntu 22.04 LTS
- Minimo 2GB RAM
- Acceso root SSH
- Dominio apuntando al VPS

### Credenciales necesarias
- API Key ElevenLabs
- API Key Anthropic
- Password para PostgreSQL (nuevo)

---

## Proceso Completo

### FASE 1: Preparar Servidor Destino

Ejecutar en el **servidor destino** (nuevo VPS):

```bash
# 1. Actualizar sistema
apt update && apt upgrade -y

# 2. Instalar Node.js 20 (CRITICO - Ubuntu viene con Node 12)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt remove -y libnode-dev 2>/dev/null
apt install -y nodejs

# 3. Instalar dependencias
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

# 4. Crear usuario mediaflow
useradd -r -s /bin/bash -m -d /var/www/mediaflow mediaflow

# 5. Configurar PostgreSQL
systemctl start postgresql
systemctl enable postgresql

sudo -u postgres psql << EOF
CREATE USER mediaflow WITH PASSWORD 'TU_PASSWORD_SEGURO';
CREATE DATABASE mediaflow OWNER mediaflow;
GRANT ALL PRIVILEGES ON DATABASE mediaflow TO mediaflow;
\q
EOF

# 6. Configurar firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

---

### FASE 2: RSYNC del Codigo

Ejecutar desde el **servidor origen** (donde funciona MediaFlow):

```bash
# Variables - CAMBIAR ESTOS VALORES
DESTINO_IP="IP_DEL_NUEVO_VPS"
DESTINO_USER="root"
DESTINO_PASS="PASSWORD_SSH"

# rsync del backend (sin venv, sin .env, sin __pycache__)
sshpass -p "$DESTINO_PASS" rsync -avz --progress \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '.env' \
    --exclude '*.pyc' \
    --exclude '*.db' \
    /var/www/mediaflow-v2/backend/ \
    $DESTINO_USER@$DESTINO_IP:/var/www/mediaflow/backend/

# rsync del frontend (sin node_modules, sin dist)
sshpass -p "$DESTINO_PASS" rsync -avz --progress \
    --exclude 'node_modules' \
    --exclude 'dist' \
    /var/www/mediaflow-v2/frontend/ \
    $DESTINO_USER@$DESTINO_IP:/var/www/mediaflow/frontend/

# rsync de la musica
sshpass -p "$DESTINO_PASS" rsync -avz --progress \
    /var/www/mediaflow-v2/backend/storage/music/ \
    $DESTINO_USER@$DESTINO_IP:/var/www/mediaflow/storage/music/

# rsync de sounds (si existen)
sshpass -p "$DESTINO_PASS" rsync -avz --progress \
    /var/www/mediaflow-v2/backend/storage/sounds/ \
    $DESTINO_USER@$DESTINO_IP:/var/www/mediaflow/storage/sounds/ 2>/dev/null || true
```

---

### FASE 3: Configuracion Post-RSYNC

Ejecutar en el **servidor destino**:

```bash
# 1. Ajustar permisos
chown -R mediaflow:mediaflow /var/www/mediaflow

# 2. Crear directorios de storage
sudo -u mediaflow mkdir -p /var/www/mediaflow/storage/{audio,music,sounds,temp}

# 3. Crear entorno virtual Python
sudo -u mediaflow bash << 'EOF'
cd /var/www/mediaflow/backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF

# 4. Crear archivo .env (EDITAR CON TUS VALORES)
cat > /var/www/mediaflow/backend/.env << 'EOF'
# General
APP_NAME=MediaFlow
APP_VERSION=2.1.0
APP_ENV=production
DEBUG=False

# Server
HOST=0.0.0.0
PORT=3001

# Database
DATABASE_URL=postgresql+asyncpg://mediaflow:TU_PASSWORD_DB@localhost:5432/mediaflow
DB_ECHO=False

# APIs
ELEVENLABS_API_KEY=TU_ELEVENLABS_KEY
ANTHROPIC_API_KEY=TU_ANTHROPIC_KEY
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

# CORS
CORS_ORIGINS=["https://TU_DOMINIO","http://TU_DOMINIO"]

# Security
SECRET_KEY=GENERA_CON_openssl_rand_hex_32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Audio
DEFAULT_TARGET_LUFS=-16.0
DEFAULT_SAMPLE_RATE=44100
DEFAULT_BITRATE=192k

# Tenant
TENANT_ID=TU_TENANT_ID
TENANT_NAME=TU_NOMBRE_CLIENTE
TENANT_LOGO=/tenants/TU_TENANT_ID/logo.png
TENANT_PRIMARY_COLOR=#4F46E5
TENANT_SECONDARY_COLOR=#7C3AED
TENANT_DOMAIN=TU_DOMINIO
TENANT_FAVICON=/favicon.ico
EOF

chown mediaflow:mediaflow /var/www/mediaflow/backend/.env
chmod 600 /var/www/mediaflow/backend/.env

# 5. Ejecutar migraciones
sudo -u mediaflow bash -c '
cd /var/www/mediaflow/backend
source venv/bin/activate
alembic upgrade head
'

# 6. Instalar y build frontend
cd /var/www/mediaflow/frontend
npm install
npm run build
```

---

### FASE 4: Configurar Servicios

```bash
# 1. Crear servicio systemd
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

# 2. Crear configuracion nginx (CAMBIAR TU_DOMINIO)
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

# 3. Configurar SSL
certbot --nginx -d TU_DOMINIO --non-interactive --agree-tos --email TU_EMAIL --redirect
```

---

### FASE 5: Cargar Datos Iniciales

```bash
# Insertar tracks de musica en la DB
sudo -u postgres psql mediaflow << 'EOF'
INSERT INTO music_tracks (filename, display_name, file_path, file_size, duration, bitrate, is_default, active, "order", genre, mood, created_at, updated_at) VALUES
('Cool.mp3', 'Cool', '/var/www/mediaflow/storage/music/Cool.mp3', 11106725, 273.45, '324kbps', false, true, 0, 'Electronic', 'energetic', NOW(), NOW()),
('Kids.mp3', 'Kids', '/var/www/mediaflow/storage/music/Kids.mp3', 9324163, 227.97, '327kbps', false, true, 1, 'Pop', 'happy', NOW(), NOW()),
('Pop.mp3', 'Pop', '/var/www/mediaflow/storage/music/Pop.mp3', 9219710, 225.63, '326kbps', false, true, 2, 'Pop', 'upbeat', NOW(), NOW()),
('Slow.mp3', 'Slow', '/var/www/mediaflow/storage/music/Slow.mp3', 8508264, 208.87, '325kbps', false, true, 3, 'Ambient', 'calm', NOW(), NOW()),
('Smooth.mp3', 'Smooth', '/var/www/mediaflow/storage/music/Smooth.mp3', 6438454, 154.28, '333kbps', false, true, 4, 'Jazz', 'relaxed', NOW(), NOW()),
('Uplift.mp3', 'Uplift', '/var/www/mediaflow/storage/music/Uplift.mp3', 10020659, 248.41, '322kbps', true, true, 5, 'Electronic', 'inspiring', NOW(), NOW()),
('_Independencia.mp3', 'Independencia', '/var/www/mediaflow/storage/music/_Independencia.mp3', 2464462, 19.72, '999kbps', false, true, 6, 'Latin', 'festive', NOW(), NOW());
EOF
```

---

### FASE 6: Verificacion

```bash
# Verificar servicios
systemctl status mediaflow
systemctl status nginx
systemctl status postgresql

# Verificar API
curl http://localhost:3001/api/v1/config/tenant
curl http://localhost:3001/api/v1/settings/music

# Verificar frontend
curl -I https://TU_DOMINIO/

# Ver logs si hay problemas
journalctl -u mediaflow -f
```

---

## Archivos en esta Carpeta

| Archivo | Descripcion |
|---------|-------------|
| `README.md` | Esta guia |
| `scripts/01-prepare-destination.sh` | Preparar servidor destino |
| `scripts/02-rsync-from-origin.sh` | Ejecutar rsync |
| `scripts/03-post-rsync-setup.sh` | Configuracion post-rsync |
| `scripts/04-load-initial-data.sql` | Datos iniciales (musica) |

---

## Tips

1. **Siempre usar puerto 3001** - El 8000 es para Azuracast
2. **PATH debe incluir /usr/bin** - Para que ffprobe funcione
3. **Modelo Claude** - Usar `claude-sonnet-4-20250514`
4. **Logo del cliente** - Colocar en `/frontend/public/tenants/{tenant_id}/logo.png`

---

*Basado en instalacion exitosa: Mall Barrio Independencia (mbi.mediaflow.cl) - 2026-01-26*
