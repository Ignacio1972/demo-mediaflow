#!/bin/bash
#
# MediaFlow v2.1 - RSYNC desde Servidor Origen
# Ejecutar en el servidor ORIGEN (donde funciona MediaFlow)
#
# Uso: ./02-rsync-from-origin.sh
#

set -e

echo "========================================"
echo "MediaFlow - RSYNC al Servidor Destino"
echo "========================================"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuracion - EDITAR ESTOS VALORES
echo ""
read -p "IP del servidor destino: " DEST_IP
read -p "Usuario SSH (default: root): " DEST_USER
DEST_USER=${DEST_USER:-root}
read -sp "Password SSH: " DEST_PASS
echo ""

# Verificar que sshpass esta instalado
if ! command -v sshpass &> /dev/null; then
    echo -e "${YELLOW}Instalando sshpass...${NC}"
    apt install -y sshpass
fi

# Directorio origen (ajustar si es diferente)
ORIGEN="/var/www/mediaflow-v2"
if [ ! -d "$ORIGEN/backend" ]; then
    ORIGEN="/var/www/mediaflow"
fi

if [ ! -d "$ORIGEN/backend" ]; then
    echo -e "${RED}Error: No se encuentra el directorio de MediaFlow${NC}"
    echo "Probados: /var/www/mediaflow-v2 y /var/www/mediaflow"
    exit 1
fi

echo ""
echo -e "${YELLOW}Origen: $ORIGEN${NC}"
echo -e "${YELLOW}Destino: $DEST_USER@$DEST_IP:/var/www/mediaflow/${NC}"
echo ""

# Probar conexion
echo -e "${YELLOW}[1/5] Probando conexion SSH...${NC}"
sshpass -p "$DEST_PASS" ssh -o StrictHostKeyChecking=no $DEST_USER@$DEST_IP "echo 'Conexion OK'"

# rsync Backend
echo ""
echo -e "${YELLOW}[2/5] Sincronizando backend...${NC}"
sshpass -p "$DEST_PASS" rsync -avz --progress \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '.env' \
    --exclude '*.pyc' \
    --exclude '*.db' \
    --exclude 'storage' \
    "$ORIGEN/backend/" \
    $DEST_USER@$DEST_IP:/var/www/mediaflow/backend/

# rsync Frontend
echo ""
echo -e "${YELLOW}[3/5] Sincronizando frontend...${NC}"
sshpass -p "$DEST_PASS" rsync -avz --progress \
    --exclude 'node_modules' \
    --exclude 'dist' \
    "$ORIGEN/frontend/" \
    $DEST_USER@$DEST_IP:/var/www/mediaflow/frontend/

# rsync Musica
echo ""
echo -e "${YELLOW}[4/5] Sincronizando musica...${NC}"
MUSIC_DIR="$ORIGEN/backend/storage/music"
if [ ! -d "$MUSIC_DIR" ]; then
    MUSIC_DIR="$ORIGEN/storage/music"
fi

if [ -d "$MUSIC_DIR" ]; then
    sshpass -p "$DEST_PASS" rsync -avz --progress \
        "$MUSIC_DIR/" \
        $DEST_USER@$DEST_IP:/var/www/mediaflow/storage/music/
else
    echo "No se encontro carpeta de musica, saltando..."
fi

# rsync Sounds
echo ""
echo -e "${YELLOW}[5/5] Sincronizando sounds...${NC}"
SOUNDS_DIR="$ORIGEN/backend/storage/sounds"
if [ ! -d "$SOUNDS_DIR" ]; then
    SOUNDS_DIR="$ORIGEN/storage/sounds"
fi

if [ -d "$SOUNDS_DIR" ]; then
    sshpass -p "$DEST_PASS" rsync -avz --progress \
        "$SOUNDS_DIR/" \
        $DEST_USER@$DEST_IP:/var/www/mediaflow/storage/sounds/ 2>/dev/null || true
else
    echo "No se encontro carpeta de sounds, saltando..."
fi

# Ajustar permisos
echo ""
echo -e "${YELLOW}Ajustando permisos...${NC}"
sshpass -p "$DEST_PASS" ssh -o StrictHostKeyChecking=no $DEST_USER@$DEST_IP \
    "chown -R mediaflow:mediaflow /var/www/mediaflow"

echo ""
echo -e "${GREEN}========================================"
echo "RSYNC completado exitosamente!"
echo "========================================"
echo ""
echo "Siguiente paso:"
echo "  Ejecutar 03-post-rsync-setup.sh en el servidor DESTINO"
echo "========================================${NC}"
