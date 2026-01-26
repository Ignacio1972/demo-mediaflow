#!/bin/bash
#
# MediaFlow v2.1 - Preparar Servidor Destino
# Ejecutar en el NUEVO VPS como root
#
# Uso: ./01-prepare-destination.sh
#

set -e

echo "========================================"
echo "MediaFlow - Preparar Servidor Destino"
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

# Solicitar password de PostgreSQL
echo ""
read -sp "Ingresa password para PostgreSQL (mediaflow user): " DB_PASSWORD
echo ""

if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}Error: Password no puede estar vacio${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}[1/7] Actualizando sistema...${NC}"
apt update && apt upgrade -y

echo ""
echo -e "${YELLOW}[2/7] Instalando Node.js 20...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt remove -y libnode-dev 2>/dev/null || true
apt install -y nodejs

echo ""
echo -e "${YELLOW}[3/7] Instalando dependencias...${NC}"
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

echo ""
echo -e "${YELLOW}[4/7] Creando usuario mediaflow...${NC}"
if id "mediaflow" &>/dev/null; then
    echo "Usuario mediaflow ya existe"
else
    useradd -r -s /bin/bash -m -d /var/www/mediaflow mediaflow
fi

echo ""
echo -e "${YELLOW}[5/7] Configurando PostgreSQL...${NC}"
systemctl start postgresql
systemctl enable postgresql

sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS mediaflow;
DROP USER IF EXISTS mediaflow;
CREATE USER mediaflow WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE mediaflow OWNER mediaflow;
GRANT ALL PRIVILEGES ON DATABASE mediaflow TO mediaflow;
EOF

echo ""
echo -e "${YELLOW}[6/7] Configurando firewall...${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo ""
echo -e "${YELLOW}[7/7] Creando directorios...${NC}"
mkdir -p /var/www/mediaflow
chown mediaflow:mediaflow /var/www/mediaflow

echo ""
echo -e "${GREEN}========================================"
echo "Servidor preparado exitosamente!"
echo "========================================"
echo ""
echo "Versiones instaladas:"
echo "  Node.js: $(node -v)"
echo "  Python:  $(python3.11 --version)"
echo "  FFmpeg:  $(ffmpeg -version 2>&1 | head -1)"
echo ""
echo "Siguiente paso:"
echo "  Ejecutar 02-rsync-from-origin.sh desde el servidor ORIGEN"
echo ""
echo "Password PostgreSQL guardado: $DB_PASSWORD"
echo "(Guardar para usar en .env)"
echo "========================================${NC}"
