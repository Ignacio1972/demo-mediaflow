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

# rsync de sounds (OBLIGATORIO para announcements)
sshpass -p "$DESTINO_PASS" rsync -avz --progress \
    /var/www/mediaflow-v2/backend/storage/sounds/ \
    $DESTINO_USER@$DESTINO_IP:/var/www/mediaflow/storage/sounds/

# Verificar que sounds se copiaron
sshpass -p "$DESTINO_PASS" ssh $DESTINO_USER@$DESTINO_IP \
    "ls -la /var/www/mediaflow/storage/sounds/*.mp3" || echo "⚠️ ERROR: Sounds no copiados!"
```

**Archivos de sounds requeridos:**
- `intro_announcement.mp3` - Sonido antes del anuncio de vehículos
- `outro_announcement.mp3` - Sonido después del anuncio

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

# AzuraCast Integration (configurar despues de instalar Azuracast)
AZURACAST_URL=http://localhost:8080
AZURACAST_API_KEY=
AZURACAST_STATION_ID=1
AZURACAST_STATION_NAME=TU_STATION_NAME
AZURACAST_MEDIA_FOLDER=Grabaciones
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

El script carga musica, voces, categorias y **templates de operaciones** (vehiculos, horarios, empleados):

```bash
sudo -u postgres psql mediaflow < /var/www/mediaflow/installation/rsync/scripts/04-load-initial-data.sql
```

Verificar que se cargaron todos los datos:
```bash
sudo -u postgres psql mediaflow -c "
  SELECT 'Music tracks' as tabla, COUNT(*) FROM music_tracks
  UNION ALL SELECT 'Voice settings', COUNT(*) FROM voice_settings
  UNION ALL SELECT 'Categories', COUNT(*) FROM categories
  UNION ALL SELECT 'Templates', COUNT(*) FROM message_templates;
"
# Esperado: Music 7, Voices 3, Categories 5, Templates 7
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

## FASE 7: Instalar Azuracast (Requerido para Radio)

Si el cliente necesita streaming de radio con interrupcion TTS.

### 7.1 Instalar Docker

```bash
curl -fsSL https://get.docker.com | sh
docker --version
```

### 7.2 Instalar Azuracast

```bash
mkdir -p /var/azuracast
cd /var/azuracast
curl -fsSL https://raw.githubusercontent.com/AzuraCast/AzuraCast/main/docker.sh > docker.sh
chmod +x docker.sh
./docker.sh install
```

### 7.3 Configurar Puertos (IMPORTANTE)

Azuracast intenta usar puerto 80, pero nginx ya lo usa. Cambiar puertos:

```bash
cd /var/azuracast
docker compose down

# Editar .env
nano .env
```

Descomentar y cambiar estas lineas:
```env
AZURACAST_HTTP_PORT=8080
AZURACAST_HTTPS_PORT=8443
```

Iniciar con nuevos puertos:
```bash
docker compose up -d
```

### 7.4 Abrir puertos en firewall

```bash
ufw allow 8080/tcp
ufw allow 8443/tcp
ufw allow 8000/tcp
```

### 7.5 Configurar Estacion en Azuracast

1. Acceder al panel: `http://IP_DEL_VPS:8080`
2. Crear cuenta de administrador
3. Crear nueva estacion con estos valores:
   - **Name**: Nombre del cliente (ej: "Mall Barrio Independencia")
   - **Short Name**: Identificador corto SIN espacios (ej: `mbi`) - **ANOTAR ESTE VALOR**
4. En la estacion, ir a `Music Files` → crear carpeta `Grabaciones`

### 7.6 Crear API Key para MediaFlow

1. En Azuracast: `Administration` → `API Keys`
2. Click `Add API Key`
3. Nombre: `MediaFlow Integration`
4. Permisos: **Station Administrator** (o minimo: Station Media, Station Broadcasting)
5. **Copiar la API Key generada** - solo se muestra una vez

### 7.7 Configurar MediaFlow para Azuracast

Editar el `.env` de MediaFlow:

```bash
nano /var/www/mediaflow/backend/.env
```

Actualizar estas variables con los valores reales:

```env
# AzuraCast Integration
AZURACAST_URL=http://localhost:8080
AZURACAST_API_KEY=TU_API_KEY_DE_AZURACAST
AZURACAST_STATION_ID=1
AZURACAST_STATION_NAME=mbi
AZURACAST_MEDIA_FOLDER=Grabaciones
```

**IMPORTANTE**: `AZURACAST_STATION_NAME` debe ser el **Short Name** exacto de la estacion (sin espacios).

Reiniciar MediaFlow:
```bash
systemctl restart mediaflow
```

### 7.8 Nginx Proxy para Panel Azuracast (Opcional)

Si quieres acceder al panel via `radio.tudominio.cl`:

```bash
cat > /etc/nginx/sites-available/azuracast << 'EOF'
server {
    listen 80;
    server_name radio.TU_DOMINIO;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

ln -sf /etc/nginx/sites-available/azuracast /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# SSL para el subdominio
certbot --nginx -d radio.TU_DOMINIO --non-interactive --agree-tos --email TU_EMAIL --redirect
```

### Puertos Azuracast

| Puerto | Servicio |
|--------|----------|
| 8080 | Panel web Azuracast (interno) |
| 8443 | Azuracast HTTPS (interno) |
| 8000 | Stream de radio principal |
| 8005+ | Streams adicionales |

### Comandos utiles Azuracast

```bash
cd /var/azuracast

# Ver estado
docker compose ps

# Reiniciar
docker compose restart

# Ver logs
docker compose logs -f

# Actualizar
./docker.sh update
```

---

## FASE 8: Verificar Sistema de Interrupcion TTS (CRITICO)

Esta verificacion es **OBLIGATORIA** para que los anuncios interrumpan la radio.

### 8.1 Verificar archivos de sonido

```bash
ls -la /var/www/mediaflow/storage/sounds/
# DEBE mostrar:
# - intro_announcement.mp3 (~110KB)
# - outro_announcement.mp3 (~110KB)
```

**Si faltan**, copiar desde servidor origen:
```bash
# Desde el servidor ORIGEN ejecutar:
scp /var/www/mediaflow-v2/backend/storage/sounds/*.mp3 \
    root@IP_DESTINO:/var/www/mediaflow/storage/sounds/

# En el servidor DESTINO:
chown mediaflow:mediaflow /var/www/mediaflow/storage/sounds/*.mp3
```

### 8.2 Verificar conexion MediaFlow → Azuracast

```bash
curl http://localhost:3001/api/v1/radio/status
# Esperado: {"success":true,"status":"online","message":"Radio backend is running"}
```

Si responde `"status":"offline"`, verificar:
- API Key correcta en .env
- Azuracast esta corriendo (`docker ps`)
- AZURACAST_URL es correcto

### 8.3 Verificar socket Liquidsoap

El socket es CRITICO para la interrupcion. Verificar que existe:

```bash
# Reemplazar STATION_NAME con el short name de tu estacion
docker exec azuracast ls -la /var/azuracast/stations/STATION_NAME/config/liquidsoap.sock
```

**Si no existe**, reiniciar Azuracast y esperar 30 segundos:
```bash
cd /var/azuracast && docker compose restart
sleep 30
# Verificar de nuevo
docker exec azuracast ls -la /var/azuracast/stations/STATION_NAME/config/liquidsoap.sock
```

### 8.4 Probar interrupcion completa

Generar un audio de prueba y enviarlo a la radio:

```bash
# Verificar que hay al menos un audio en la biblioteca
curl http://localhost:3001/api/v1/library/messages | head -20

# Enviar el audio ID 1 a la radio (cambiar ID si es necesario)
curl -X POST "http://localhost:3001/api/v1/library/1/send-to-radio?interrupt=true"
```

Respuesta exitosa:
```json
{
  "success": true,
  "message": "Audio uploaded and playing on radio",
  "data": {
    "azuracast": {
      "upload": {"success": true},
      "interrupt": {"success": true, "request_id": "1"}
    }
  }
}
```

### 8.5 Troubleshooting

| Problema | Causa | Solucion |
|----------|-------|----------|
| `Socket not found` | Liquidsoap no inicio | `docker compose restart` y esperar 30s |
| `API Key invalid` | Key incorrecta/expirada | Crear nueva API Key en Azuracast |
| `Upload failed` | Carpeta no existe | Crear carpeta `Grabaciones` en Azuracast |
| `Sounds not found` | Archivos faltantes | Copiar intro/outro_announcement.mp3 |
| `status: offline` | Azuracast caido o URL mal | Verificar docker ps y AZURACAST_URL |

---

## Resumen de Puertos Final

| Puerto | Servicio |
|--------|----------|
| 80 | Nginx (HTTP → HTTPS redirect) |
| 443 | Nginx (MediaFlow HTTPS) |
| 3001 | MediaFlow Backend (interno) |
| 8080 | Azuracast Panel Web |
| 8443 | Azuracast HTTPS |
| 8000 | Azuracast Radio Stream |

---

## Tips

1. **MediaFlow en puerto 3001** - El 8000 es para Azuracast stream
2. **PATH debe incluir /usr/bin** - Para que ffprobe funcione
3. **Modelo Claude** - Usar `claude-sonnet-4-20250514`
4. **Logo del cliente** - Colocar en `/frontend/public/tenants/{tenant_id}/logo.png`
5. **Azuracast puertos** - Cambiar HTTP a 8080 porque nginx usa 80

---

*Basado en instalacion exitosa: Mall Barrio Independencia (mbi.mediaflow.cl) - 2026-01-26*
