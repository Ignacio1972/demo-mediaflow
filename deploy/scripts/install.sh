#!/bin/bash
#
# MediaFlow v2.1 - Script de Instalación Automatizado
#
# Uso:
#   curl -sSL https://raw.githubusercontent.com/your-org/mediaflow-v2/main/deploy/scripts/install.sh | sudo bash
#
# O descargando primero:
#   wget https://raw.githubusercontent.com/your-org/mediaflow-v2/main/deploy/scripts/install.sh
#   chmod +x install.sh
#   sudo ./install.sh
#
# Basado en instalación exitosa del 26-01-2026
# Incorpora soluciones a problemas conocidos

set -e

# ============================================
# Colores y utilidades
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============================================
# Configuración
# ============================================
MEDIAFLOW_DIR="/var/www/mediaflow"
MEDIAFLOW_USER="mediaflow"
PYTHON_VERSION="python3.11"
NODE_VERSION="20"

# ============================================
# Verificaciones iniciales
# ============================================
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Este script debe ejecutarse como root (sudo)"
        exit 1
    fi
}

check_ubuntu() {
    if ! grep -q "Ubuntu" /etc/os-release 2>/dev/null; then
        log_error "Este script está diseñado para Ubuntu"
        exit 1
    fi
    log_success "Sistema operativo: Ubuntu detectado"
}

# ============================================
# Recolección de datos
# ============================================
collect_config() {
    echo ""
    echo "=========================================="
    echo "   MediaFlow v2.1 - Configuración"
    echo "=========================================="
    echo ""

    # Dominio
    read -p "Dominio (ej: demo.mediaflow.cl): " DOMAIN
    [[ -z "$DOMAIN" ]] && { log_error "Dominio requerido"; exit 1; }

    # Tenant
    read -p "Tenant ID (ej: demo, mallbarrio): " TENANT_ID
    TENANT_ID=${TENANT_ID:-demo}

    read -p "Nombre del Tenant: " TENANT_NAME
    TENANT_NAME=${TENANT_NAME:-"MediaFlow Demo"}

    # Database
    read -s -p "Password PostgreSQL para mediaflow: " DB_PASSWORD
    echo ""
    [[ -z "$DB_PASSWORD" ]] && { log_error "Password de DB requerido"; exit 1; }

    # API Keys
    read -s -p "ElevenLabs API Key: " ELEVENLABS_KEY
    echo ""
    [[ -z "$ELEVENLABS_KEY" ]] && { log_error "ElevenLabs key requerida"; exit 1; }

    read -s -p "Anthropic API Key: " ANTHROPIC_KEY
    echo ""
    [[ -z "$ANTHROPIC_KEY" ]] && { log_error "Anthropic key requerida"; exit 1; }

    # Color primario
    read -p "Color primario (default: #4F46E5): " PRIMARY_COLOR
    PRIMARY_COLOR=${PRIMARY_COLOR:-"#4F46E5"}

    # Secret key
    SECRET_KEY=$(openssl rand -hex 32)

    echo ""
    log_info "Configuración:"
    echo "  Dominio: $DOMAIN"
    echo "  Tenant: $TENANT_ID ($TENANT_NAME)"
    echo "  Color: $PRIMARY_COLOR"
    echo ""

    read -p "¿Continuar con la instalación? (y/N) " -n 1 -r
    echo ""
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 0
}

# ============================================
# Instalación de paquetes
# ============================================
install_packages() {
    log_info "Actualizando sistema..."
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

    log_info "Instalando dependencias base..."
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        curl \
        git \
        ufw \
        ${PYTHON_VERSION} \
        ${PYTHON_VERSION}-venv \
        ${PYTHON_VERSION}-dev \
        nginx \
        postgresql \
        postgresql-contrib \
        certbot \
        python3-certbot-nginx \
        ffmpeg

    # ===========================================
    # IMPORTANTE: Node.js 20 desde NodeSource
    # Ubuntu 22.04 trae Node.js 12 que NO funciona
    # ===========================================
    log_info "Instalando Node.js ${NODE_VERSION} (desde NodeSource)..."

    # Remover versiones antiguas y conflictos
    apt-get remove -y nodejs npm libnode-dev 2>/dev/null || true

    # Agregar repositorio NodeSource
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash -

    # Instalar Node.js
    DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs

    # Verificar versiones
    log_info "Verificando versiones instaladas..."
    echo "  Node.js: $(node -v)"
    echo "  npm: $(npm -v)"
    echo "  Python: $(${PYTHON_VERSION} --version)"
    echo "  PostgreSQL: $(psql --version | head -1)"
    echo "  FFmpeg: $(ffmpeg -version 2>&1 | head -1)"

    log_success "Paquetes instalados correctamente"
}

# ============================================
# Crear usuario del sistema
# ============================================
create_user() {
    log_info "Creando usuario ${MEDIAFLOW_USER}..."

    if id "$MEDIAFLOW_USER" &>/dev/null; then
        log_warning "Usuario ${MEDIAFLOW_USER} ya existe"
    else
        useradd -r -s /bin/bash -m -d "$MEDIAFLOW_DIR" "$MEDIAFLOW_USER"
        log_success "Usuario ${MEDIAFLOW_USER} creado"
    fi

    mkdir -p "$MEDIAFLOW_DIR"
    chown -R "$MEDIAFLOW_USER:$MEDIAFLOW_USER" "$MEDIAFLOW_DIR"
}

# ============================================
# Configurar PostgreSQL
# ============================================
setup_postgresql() {
    log_info "Configurando PostgreSQL..."

    systemctl start postgresql
    systemctl enable postgresql

    # Crear usuario y base de datos
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS mediaflow;" 2>/dev/null || true
    sudo -u postgres psql -c "DROP USER IF EXISTS mediaflow;" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE USER mediaflow WITH PASSWORD '${DB_PASSWORD}';"
    sudo -u postgres psql -c "CREATE DATABASE mediaflow OWNER mediaflow;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mediaflow TO mediaflow;"

    log_success "PostgreSQL configurado"
}

# ============================================
# Clonar/Copiar proyecto
# ============================================
setup_project() {
    log_info "Configurando proyecto..."

    if [[ -d "$MEDIAFLOW_DIR/.git" ]]; then
        log_warning "Repositorio existente, actualizando..."
        sudo -u "$MEDIAFLOW_USER" git -C "$MEDIAFLOW_DIR" pull
    else
        log_info "Clonando repositorio..."
        sudo -u "$MEDIAFLOW_USER" git clone https://github.com/your-org/mediaflow-v2.git "$MEDIAFLOW_DIR"
    fi

    log_success "Proyecto configurado"
}

# ============================================
# Configurar Backend
# ============================================
setup_backend() {
    log_info "Configurando backend..."

    # Crear entorno virtual e instalar dependencias
    sudo -u "$MEDIAFLOW_USER" bash << EOF
cd "$MEDIAFLOW_DIR/backend"
${PYTHON_VERSION} -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF

    # Crear archivo .env
    cat > "$MEDIAFLOW_DIR/backend/.env" << EOF
# General
APP_NAME=MediaFlow
APP_VERSION=2.1.0
APP_ENV=production
DEBUG=False

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://mediaflow:${DB_PASSWORD}@localhost:5432/mediaflow
DB_ECHO=False

# Redis
REDIS_URL=redis://localhost:6379/0

# ElevenLabs
ELEVENLABS_API_KEY=${ELEVENLABS_KEY}
ELEVENLABS_MODEL_ID=eleven_multilingual_v2

# Anthropic
ANTHROPIC_API_KEY=${ANTHROPIC_KEY}
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Storage
STORAGE_PATH=${MEDIAFLOW_DIR}/storage
AUDIO_PATH=${MEDIAFLOW_DIR}/storage/audio
MUSIC_PATH=${MEDIAFLOW_DIR}/storage/music
SOUNDS_PATH=${MEDIAFLOW_DIR}/storage/sounds
TEMP_PATH=${MEDIAFLOW_DIR}/storage/temp
MAX_UPLOAD_SIZE=52428800

# CORS
CORS_ORIGINS=["https://${DOMAIN}","http://${DOMAIN}"]

# Security
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Tenant
TENANT_ID=${TENANT_ID}
TENANT_NAME=${TENANT_NAME}
TENANT_LOGO=/images/mediaflow-logo.png
TENANT_PRIMARY_COLOR=${PRIMARY_COLOR}
TENANT_SECONDARY_COLOR=#7C3AED
TENANT_DOMAIN=${DOMAIN}
TENANT_FAVICON=/favicon.ico
EOF

    chown "$MEDIAFLOW_USER:$MEDIAFLOW_USER" "$MEDIAFLOW_DIR/backend/.env"
    chmod 600 "$MEDIAFLOW_DIR/backend/.env"

    # Crear directorios de storage
    sudo -u "$MEDIAFLOW_USER" mkdir -p "$MEDIAFLOW_DIR/storage"/{audio,music,sounds,temp}

    # Ejecutar migraciones
    log_info "Ejecutando migraciones de base de datos..."
    sudo -u "$MEDIAFLOW_USER" bash << EOF
cd "$MEDIAFLOW_DIR/backend"
source venv/bin/activate
alembic upgrade head
EOF

    # Cargar datos iniciales (campañas, voces, etc.)
    log_info "Cargando datos iniciales..."
    sudo -u "$MEDIAFLOW_USER" bash << EOF
cd "$MEDIAFLOW_DIR/backend"
source venv/bin/activate
python ../scripts/seed_default_data.py
EOF

    log_success "Backend configurado"
}

# ============================================
# Configurar Frontend
# ============================================
setup_frontend() {
    log_info "Construyendo frontend..."

    cd "$MEDIAFLOW_DIR/frontend"

    # Limpiar instalación previa
    rm -rf node_modules package-lock.json

    # Instalar y construir
    npm install
    npm run build

    log_success "Frontend construido"
}

# ============================================
# Configurar Systemd
# ============================================
setup_systemd() {
    log_info "Configurando servicio systemd..."

    cp "$MEDIAFLOW_DIR/deploy/systemd/mediaflow.service" /etc/systemd/system/

    systemctl daemon-reload
    systemctl enable mediaflow
    systemctl start mediaflow

    sleep 3

    if systemctl is-active --quiet mediaflow; then
        log_success "Servicio mediaflow activo"
    else
        log_error "El servicio no inició correctamente"
        journalctl -u mediaflow -n 20
        exit 1
    fi
}

# ============================================
# Configurar Nginx
# ============================================
setup_nginx() {
    log_info "Configurando Nginx..."

    cat > /etc/nginx/sites-available/mediaflow << EOF
upstream mediaflow_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name ${DOMAIN};

    client_max_body_size 50M;

    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript;

    root ${MEDIAFLOW_DIR}/frontend/dist;
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

    location /storage/ {
        alias ${MEDIAFLOW_DIR}/storage/;
        expires 7d;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

    rm -f /etc/nginx/sites-enabled/default
    ln -sf /etc/nginx/sites-available/mediaflow /etc/nginx/sites-enabled/

    nginx -t && systemctl reload nginx

    log_success "Nginx configurado"
}

# ============================================
# Configurar Firewall
# ============================================
setup_firewall() {
    log_info "Configurando firewall..."

    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable

    log_success "Firewall configurado"
}

# ============================================
# Configurar SSL
# ============================================
setup_ssl() {
    log_info "Configurando SSL con Let's Encrypt..."

    echo ""
    read -p "¿Configurar SSL ahora? (requiere DNS configurado) (y/N) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email "admin@${DOMAIN}" --redirect
        log_success "SSL configurado"
    else
        log_warning "SSL no configurado. Ejecutar después: certbot --nginx -d ${DOMAIN}"
    fi
}

# ============================================
# Verificación final
# ============================================
final_check() {
    echo ""
    echo "=========================================="
    echo "   Instalación Completada"
    echo "=========================================="
    echo ""

    echo "Estado de servicios:"
    systemctl is-active --quiet mediaflow && echo "  ✓ MediaFlow: Activo" || echo "  ✗ MediaFlow: Inactivo"
    systemctl is-active --quiet nginx && echo "  ✓ Nginx: Activo" || echo "  ✗ Nginx: Inactivo"
    systemctl is-active --quiet postgresql && echo "  ✓ PostgreSQL: Activo" || echo "  ✗ PostgreSQL: Inactivo"

    echo ""
    echo "Verificación de API:"
    if curl -s http://localhost:8000/api/v1/config/tenant | grep -q "tenant_id"; then
        echo "  ✓ API respondiendo correctamente"
    else
        echo "  ✗ API no responde"
    fi

    echo ""
    echo "Próximos pasos:"
    echo "  1. Configurar DNS: A record ${DOMAIN} -> $(curl -s ifconfig.me)"
    echo "  2. Ejecutar SSL: certbot --nginx -d ${DOMAIN}"
    echo "  3. Acceder: https://${DOMAIN}"
    echo ""
    echo "Comandos útiles:"
    echo "  Logs: journalctl -u mediaflow -f"
    echo "  Reiniciar: systemctl restart mediaflow"
    echo "  Estado: systemctl status mediaflow"
    echo ""
}

# ============================================
# Main
# ============================================
main() {
    echo ""
    echo "=========================================="
    echo "   MediaFlow v2.1 - Instalación"
    echo "=========================================="
    echo ""

    check_root
    check_ubuntu
    collect_config

    install_packages
    create_user
    setup_postgresql
    setup_project
    setup_backend
    setup_frontend
    setup_systemd
    setup_nginx
    setup_firewall
    setup_ssl
    final_check
}

main "$@"
