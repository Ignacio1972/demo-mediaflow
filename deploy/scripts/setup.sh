#!/bin/bash
#
# MediaFlow v2.1 - Automated Setup Script
# For Ubuntu 22.04 LTS
#
# Usage: sudo bash setup.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MEDIAFLOW_DIR="/var/www/mediaflow"
MEDIAFLOW_USER="mediaflow"
PYTHON_VERSION="python3.11"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (sudo)"
        exit 1
    fi
}

# Check Ubuntu version
check_ubuntu() {
    if ! grep -q "Ubuntu 22.04" /etc/os-release 2>/dev/null; then
        log_warning "This script is designed for Ubuntu 22.04 LTS"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Collect configuration
collect_config() {
    echo ""
    echo "========================================="
    echo "  MediaFlow v2.1 - Setup Configuration"
    echo "========================================="
    echo ""

    # Domain
    read -p "Enter domain name (e.g., demo.mediaflow.cl): " DOMAIN
    if [[ -z "$DOMAIN" ]]; then
        log_error "Domain is required"
        exit 1
    fi

    # Tenant ID
    read -p "Enter tenant ID (e.g., demo, mallbarrio): " TENANT_ID
    TENANT_ID=${TENANT_ID:-demo}

    # Tenant Name
    read -p "Enter tenant display name (e.g., MediaFlow Demo): " TENANT_NAME
    TENANT_NAME=${TENANT_NAME:-"MediaFlow Demo"}

    # Database password
    read -s -p "Enter PostgreSQL password for mediaflow user: " DB_PASSWORD
    echo ""
    if [[ -z "$DB_PASSWORD" ]]; then
        log_error "Database password is required"
        exit 1
    fi

    # ElevenLabs API Key
    read -s -p "Enter ElevenLabs API key: " ELEVENLABS_KEY
    echo ""
    if [[ -z "$ELEVENLABS_KEY" ]]; then
        log_error "ElevenLabs API key is required"
        exit 1
    fi

    # Anthropic API Key
    read -s -p "Enter Anthropic API key: " ANTHROPIC_KEY
    echo ""
    if [[ -z "$ANTHROPIC_KEY" ]]; then
        log_error "Anthropic API key is required"
        exit 1
    fi

    # Primary Color
    read -p "Enter primary brand color (default: #4F46E5): " PRIMARY_COLOR
    PRIMARY_COLOR=${PRIMARY_COLOR:-"#4F46E5"}

    # Generate secret key
    SECRET_KEY=$(openssl rand -hex 32)

    echo ""
    log_info "Configuration summary:"
    echo "  Domain: $DOMAIN"
    echo "  Tenant ID: $TENANT_ID"
    echo "  Tenant Name: $TENANT_NAME"
    echo "  Primary Color: $PRIMARY_COLOR"
    echo ""

    read -p "Proceed with installation? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
}

# Install system packages
install_packages() {
    log_info "Installing system packages..."

    apt update
    apt install -y \
        ${PYTHON_VERSION} \
        ${PYTHON_VERSION}-venv \
        ${PYTHON_VERSION}-dev \
        nodejs \
        npm \
        nginx \
        postgresql \
        postgresql-contrib \
        certbot \
        python3-certbot-nginx \
        ffmpeg \
        git \
        curl \
        htop \
        ufw

    log_success "System packages installed"
}

# Create system user
create_user() {
    log_info "Creating system user..."

    if id "$MEDIAFLOW_USER" &>/dev/null; then
        log_warning "User $MEDIAFLOW_USER already exists"
    else
        useradd -r -s /bin/bash -m -d "$MEDIAFLOW_DIR" "$MEDIAFLOW_USER"
        log_success "User $MEDIAFLOW_USER created"
    fi

    mkdir -p "$MEDIAFLOW_DIR"
    chown -R "$MEDIAFLOW_USER:$MEDIAFLOW_USER" "$MEDIAFLOW_DIR"
}

# Setup PostgreSQL
setup_postgresql() {
    log_info "Setting up PostgreSQL..."

    # Start PostgreSQL if not running
    systemctl start postgresql
    systemctl enable postgresql

    # Create user and database
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS mediaflow;" 2>/dev/null || true
    sudo -u postgres psql -c "DROP USER IF EXISTS mediaflow;" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE USER mediaflow WITH PASSWORD '${DB_PASSWORD}';"
    sudo -u postgres psql -c "CREATE DATABASE mediaflow OWNER mediaflow;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mediaflow TO mediaflow;"

    log_success "PostgreSQL configured"
}

# Clone repository
clone_repo() {
    log_info "Cloning repository..."

    if [[ -d "$MEDIAFLOW_DIR/.git" ]]; then
        log_warning "Repository already exists, pulling latest..."
        sudo -u "$MEDIAFLOW_USER" git -C "$MEDIAFLOW_DIR" pull
    else
        sudo -u "$MEDIAFLOW_USER" git clone https://github.com/your-org/mediaflow-v2.git "$MEDIAFLOW_DIR"
    fi

    log_success "Repository ready"
}

# Setup backend
setup_backend() {
    log_info "Setting up backend..."

    sudo -u "$MEDIAFLOW_USER" bash << EOF
cd "$MEDIAFLOW_DIR/backend"

# Create virtual environment
${PYTHON_VERSION} -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
EOF

    # Create .env file
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

# ElevenLabs API
ELEVENLABS_API_KEY=${ELEVENLABS_KEY}
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
ELEVENLABS_BASE_URL=https://api.elevenlabs.io/v1

# Claude AI (Anthropic)
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
CORS_ORIGINS=["https://${DOMAIN}"]

# Security
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Tenant Configuration
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

    # Create storage directories
    sudo -u "$MEDIAFLOW_USER" mkdir -p "$MEDIAFLOW_DIR/storage"/{audio,music,sounds,temp}

    # Run migrations
    sudo -u "$MEDIAFLOW_USER" bash << EOF
cd "$MEDIAFLOW_DIR/backend"
source venv/bin/activate
alembic upgrade head
EOF

    log_success "Backend configured"
}

# Setup frontend
setup_frontend() {
    log_info "Building frontend..."

    sudo -u "$MEDIAFLOW_USER" bash << EOF
cd "$MEDIAFLOW_DIR/frontend"
npm install
npm run build
EOF

    log_success "Frontend built"
}

# Setup systemd
setup_systemd() {
    log_info "Setting up systemd service..."

    cp "$MEDIAFLOW_DIR/deploy/systemd/mediaflow.service" /etc/systemd/system/

    # Adjust paths in service file
    sed -i "s|/var/www/mediaflow|${MEDIAFLOW_DIR}|g" /etc/systemd/system/mediaflow.service

    systemctl daemon-reload
    systemctl enable mediaflow
    systemctl start mediaflow

    # Wait and check status
    sleep 3
    if systemctl is-active --quiet mediaflow; then
        log_success "MediaFlow service started"
    else
        log_error "MediaFlow service failed to start"
        journalctl -u mediaflow -n 20
        exit 1
    fi
}

# Setup Nginx
setup_nginx() {
    log_info "Setting up Nginx..."

    # Copy and configure Nginx
    cp "$MEDIAFLOW_DIR/deploy/nginx/mediaflow.conf.template" /etc/nginx/sites-available/mediaflow

    # Replace domain
    sed -i "s/YOUR_DOMAIN/${DOMAIN}/g" /etc/nginx/sites-available/mediaflow
    sed -i "s|/var/www/mediaflow|${MEDIAFLOW_DIR}|g" /etc/nginx/sites-available/mediaflow

    # For initial setup without SSL, create a temporary config
    cat > /etc/nginx/sites-available/mediaflow-temp << EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN};

    root ${MEDIAFLOW_DIR}/frontend/dist;
    index index.html;

    client_max_body_size 50M;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /storage/audio/ {
        alias ${MEDIAFLOW_DIR}/storage/audio/;
    }

    location /storage/music/ {
        alias ${MEDIAFLOW_DIR}/storage/music/;
    }

    location /storage/sounds/ {
        alias ${MEDIAFLOW_DIR}/storage/sounds/;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

    # Enable temp config
    rm -f /etc/nginx/sites-enabled/default
    rm -f /etc/nginx/sites-enabled/mediaflow
    ln -s /etc/nginx/sites-available/mediaflow-temp /etc/nginx/sites-enabled/mediaflow-temp

    # Test and reload
    nginx -t
    systemctl reload nginx

    log_success "Nginx configured (HTTP only)"
}

# Setup SSL
setup_ssl() {
    log_info "Setting up SSL with Let's Encrypt..."

    echo ""
    read -p "Set up SSL now? (requires DNS to be configured) (y/N) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email "admin@${DOMAIN}" --redirect

        # Replace temp config with full SSL config
        rm -f /etc/nginx/sites-enabled/mediaflow-temp
        ln -sf /etc/nginx/sites-available/mediaflow /etc/nginx/sites-enabled/mediaflow

        nginx -t && systemctl reload nginx

        log_success "SSL configured"
    else
        log_warning "Skipping SSL setup. Run 'sudo certbot --nginx -d ${DOMAIN}' later"
    fi
}

# Setup firewall
setup_firewall() {
    log_info "Configuring firewall..."

    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 'Nginx Full'
    ufw --force enable

    log_success "Firewall configured"
}

# Final checks
final_checks() {
    echo ""
    echo "========================================="
    echo "  Installation Complete!"
    echo "========================================="
    echo ""

    # Check services
    echo "Service Status:"
    systemctl is-active --quiet mediaflow && echo "  MediaFlow: Running" || echo "  MediaFlow: NOT Running"
    systemctl is-active --quiet nginx && echo "  Nginx: Running" || echo "  Nginx: NOT Running"
    systemctl is-active --quiet postgresql && echo "  PostgreSQL: Running" || echo "  PostgreSQL: NOT Running"
    echo ""

    # Test API
    echo "API Health Check:"
    if curl -s http://localhost:8000/api/v1/config/tenant | grep -q "tenant_id"; then
        echo "  API: OK"
    else
        echo "  API: FAILED"
    fi
    echo ""

    echo "Next Steps:"
    echo "  1. Point your DNS to this server's IP"
    echo "  2. Run SSL setup: sudo certbot --nginx -d ${DOMAIN}"
    echo "  3. Access your site at: https://${DOMAIN}"
    echo ""
    echo "Useful commands:"
    echo "  View logs: sudo journalctl -u mediaflow -f"
    echo "  Restart: sudo systemctl restart mediaflow"
    echo "  Status: sudo systemctl status mediaflow"
    echo ""
}

# Main
main() {
    echo ""
    echo "========================================="
    echo "  MediaFlow v2.1 - Installation Script"
    echo "========================================="
    echo ""

    check_root
    check_ubuntu
    collect_config

    install_packages
    create_user
    setup_postgresql
    clone_repo
    setup_backend
    setup_frontend
    setup_systemd
    setup_nginx
    setup_ssl
    setup_firewall
    final_checks
}

main "$@"
