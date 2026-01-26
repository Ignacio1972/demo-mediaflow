#!/bin/bash
#
# MediaFlow v2.1 - Configuracion Post-RSYNC
# Ejecutar en el servidor DESTINO como root
#
# Uso: ./03-post-rsync-setup.sh
#

set -e

echo "========================================"
echo "MediaFlow - Configuracion Post-RSYNC"
echo "========================================"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: Ejecutar como root${NC}"
    exit 1
fi

# Solicitar configuracion
echo ""
echo "Configuracion del nuevo servidor:"
echo "---------------------------------"
read -p "Dominio (ej: demo.mediaflow.cl): " DOMAIN
read -p "Tenant ID (ej: demo, mallbarrio): " TENANT_ID
read -p "Nombre del cliente (ej: Mall Barrio): " TENANT_NAME
read -p "Color primario (default: #4F46E5): " PRIMARY_COLOR
PRIMARY_COLOR=${PRIMARY_COLOR:-#4F46E5}
read -p "Color secundario (default: #7C3AED): " SECONDARY_COLOR
SECONDARY_COLOR=${SECONDARY_COLOR:-#7C3AED}
echo ""
read -sp "Password PostgreSQL (del paso 1): " DB_PASSWORD
echo ""
read -sp "API Key ElevenLabs: " ELEVENLABS_KEY
echo ""
read -sp "API Key Anthropic: " ANTHROPIC_KEY
echo ""
read -p "Email para SSL (certbot): " SSL_EMAIL

# Generar SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)

echo ""
echo -e "${YELLOW}[1/8] Creando directorios...${NC}"
sudo -u mediaflow mkdir -p /var/www/mediaflow/storage/{audio,music,sounds,temp}
mkdir -p /var/www/mediaflow/frontend/public/tenants/$TENANT_ID

echo ""
echo -e "${YELLOW}[2/8] Creando entorno virtual Python...${NC}"
sudo -u mediaflow bash << 'EOF'
cd /var/www/mediaflow/backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF

echo ""
echo -e "${YELLOW}[3/8] Creando archivo .env...${NC}"
cat > /var/www/mediaflow/backend/.env << EOF
# General
APP_NAME=MediaFlow
APP_VERSION=2.1.0
APP_ENV=production
DEBUG=False

# Server
HOST=0.0.0.0
PORT=3001

# Database
DATABASE_URL=postgresql+asyncpg://mediaflow:${DB_PASSWORD}@localhost:5432/mediaflow
DB_ECHO=False

# APIs
ELEVENLABS_API_KEY=${ELEVENLABS_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_KEY}
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
CORS_ORIGINS=["https://${DOMAIN}","http://${DOMAIN}"]

# Security
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Audio
DEFAULT_TARGET_LUFS=-16.0
DEFAULT_SAMPLE_RATE=44100
DEFAULT_BITRATE=192k

# Tenant
TENANT_ID=${TENANT_ID}
TENANT_NAME=${TENANT_NAME}
TENANT_LOGO=/tenants/${TENANT_ID}/logo.png
TENANT_PRIMARY_COLOR=${PRIMARY_COLOR}
TENANT_SECONDARY_COLOR=${SECONDARY_COLOR}
TENANT_DOMAIN=${DOMAIN}
TENANT_FAVICON=/favicon.ico
EOF

chown mediaflow:mediaflow /var/www/mediaflow/backend/.env
chmod 600 /var/www/mediaflow/backend/.env

echo ""
echo -e "${YELLOW}[4/8] Ejecutando migraciones...${NC}"
sudo -u mediaflow bash -c '
cd /var/www/mediaflow/backend
source venv/bin/activate
alembic upgrade head
'

echo ""
echo -e "${YELLOW}[5/8] Build del frontend...${NC}"
cd /var/www/mediaflow/frontend
npm install
npm run build

echo ""
echo -e "${YELLOW}[6/8] Configurando systemd...${NC}"
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

echo ""
echo -e "${YELLOW}[7/8] Configurando nginx...${NC}"
cat > /etc/nginx/sites-available/mediaflow << EOF
upstream mediaflow_backend {
    server 127.0.0.1:3001;
    keepalive 32;
}

server {
    listen 80;
    server_name ${DOMAIN};

    client_max_body_size 50M;

    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript;

    root /var/www/mediaflow/frontend/dist;
    index index.html;

    location /api/ {
        proxy_pass http://mediaflow_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
    }

    location /ws/ {
        proxy_pass http://mediaflow_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
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
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

ln -sf /etc/nginx/sites-available/mediaflow /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo ""
echo -e "${YELLOW}[8/8] Configurando SSL...${NC}"
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $SSL_EMAIL --redirect

echo ""
echo -e "${GREEN}========================================"
echo "Configuracion completada!"
echo "========================================"
echo ""
echo "Verificacion:"
echo "  curl http://localhost:3001/api/v1/config/tenant"
echo "  curl https://${DOMAIN}/"
echo ""
echo "Siguiente paso:"
echo "  1. Subir logo a: /var/www/mediaflow/frontend/public/tenants/${TENANT_ID}/logo.png"
echo "  2. Ejecutar: npm run build (en /var/www/mediaflow/frontend)"
echo "  3. Cargar datos iniciales: psql < 04-load-initial-data.sql"
echo "========================================${NC}"
