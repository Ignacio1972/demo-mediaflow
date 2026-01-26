# MediaFlow v2.1 - Referencia de Archivos Importantes

## Estructura del Proyecto

```
mediaflow-v2/
├── backend/                    # API FastAPI
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/      # Endpoints de la API
│   │   │   │   ├── config.py   # 🆕 Endpoint de configuración tenant
│   │   │   │   ├── audio.py    # Generación TTS
│   │   │   │   ├── library.py  # Biblioteca de audios
│   │   │   │   └── ...
│   │   │   └── api.py          # Router principal
│   │   ├── core/
│   │   │   └── config.py       # ⚙️ Settings (incluye tenant config)
│   │   ├── models/             # Modelos SQLAlchemy
│   │   ├── schemas/            # Schemas Pydantic
│   │   └── services/           # Lógica de negocio
│   ├── alembic/
│   │   └── versions/           # ⚠️ Migraciones (verificar PostgreSQL)
│   ├── .env                    # 🔐 Configuración (NO commitear)
│   ├── .env.example            # 📋 Template de configuración
│   ├── requirements.txt        # Dependencias Python
│   └── Dockerfile              # 🐳 Docker backend
│
├── frontend/                   # Vue 3 + TypeScript
│   ├── src/
│   │   ├── stores/
│   │   │   ├── tenant.ts       # 🆕 Store de configuración tenant
│   │   │   └── audio.ts
│   │   ├── components/
│   │   │   └── common/
│   │   │       └── NavigationHeader.vue  # Logo dinámico
│   │   └── App.vue             # Carga config tenant al inicio
│   ├── public/
│   │   ├── tenants/            # 🆕 Assets por tenant
│   │   │   ├── demo/
│   │   │   └── mallbarrio/
│   │   └── images/
│   ├── dist/                   # Build de producción
│   ├── docker/
│   │   └── nginx.conf          # Config Nginx para Docker
│   ├── Dockerfile              # 🐳 Docker frontend (prod)
│   └── Dockerfile.dev          # 🐳 Docker frontend (dev)
│
├── deploy/                     # 📦 Archivos de deployment
│   ├── nginx/
│   │   └── mediaflow.conf.template
│   ├── systemd/
│   │   └── mediaflow.service
│   └── scripts/
│       ├── install.sh          # 🚀 Script de instalación
│       └── setup.sh            # Script legacy
│
├── scripts/                    # Scripts de utilidad
│   └── migrate_sqlite_to_postgres.py
│
├── docs/                       # 📚 Documentación
│   ├── DEPLOYMENT_GUIDE.md     # Guía completa de instalación
│   ├── FILES_REFERENCE.md      # Este archivo
│   └── CAMPAIGN_MASTER_PLAN.md
│
├── docker-compose.yml          # 🐳 Docker Compose principal
├── docker-compose.override.yml # 🐳 Override para desarrollo
├── .env.docker.example         # 📋 Template para Docker
└── CLAUDE.md                   # Contexto para Claude AI
```

---

## Archivos Críticos para Deployment

### 1. Configuración del Backend

**`backend/.env`** - Configuración principal (NUNCA commitear)
```env
# Las variables más importantes:
DATABASE_URL=postgresql+asyncpg://...
ELEVENLABS_API_KEY=...
ANTHROPIC_API_KEY=...
TENANT_ID=...
TENANT_NAME=...
```

### 2. Servicio Systemd

**`/etc/systemd/system/mediaflow.service`**
```ini
[Unit]
Description=MediaFlow v2.1 Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=mediaflow
WorkingDirectory=/var/www/mediaflow/backend
ExecStart=/var/www/mediaflow/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

[Install]
WantedBy=multi-user.target
```

### 3. Configuración Nginx

**`/etc/nginx/sites-available/mediaflow`**
- Proxy reverso a backend (puerto 8000)
- Servir frontend estático
- SSL con Let's Encrypt
- Storage de archivos

### 4. Migraciones de Base de Datos

**`backend/alembic/versions/`**

⚠️ **IMPORTANTE**: Algunas migraciones tienen sintaxis SQLite que NO funciona en PostgreSQL:

| SQLite | PostgreSQL |
|--------|------------|
| `datetime('now')` | `NOW()` |
| `1` (boolean) | `true` |
| `0` (boolean) | `false` |

Archivos que requieren revisión:
- `a1b2c3d4e5f6_add_ai_clients_table.py`

---

## Archivos de Configuración por Ambiente

### Desarrollo Local

| Archivo | Propósito |
|---------|-----------|
| `backend/.env` | Config local con SQLite |
| `docker-compose.override.yml` | Hot-reload, PgAdmin |
| `frontend/vite.config.ts` | Proxy a backend local |

### Producción (VPS)

| Archivo | Ubicación en servidor |
|---------|----------------------|
| `.env` | `/var/www/mediaflow/backend/.env` |
| `mediaflow.service` | `/etc/systemd/system/mediaflow.service` |
| `nginx config` | `/etc/nginx/sites-available/mediaflow` |
| `SSL certs` | `/etc/letsencrypt/live/{domain}/` |

### Docker

| Archivo | Propósito |
|---------|-----------|
| `.env.docker.example` | Template de variables |
| `docker-compose.yml` | Orquestación principal |
| `backend/Dockerfile` | Imagen backend |
| `frontend/Dockerfile` | Imagen frontend (prod) |
| `frontend/Dockerfile.dev` | Imagen frontend (dev) |

---

## Endpoints API Importantes

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/config/tenant` | GET | Configuración del tenant |
| `/api/v1/audio/generate` | POST | Generar audio TTS |
| `/api/v1/audio/voices` | GET | Listar voces disponibles |
| `/api/v1/library/messages` | GET | Listar mensajes |
| `/api/v1/settings/voices` | CRUD | Gestionar voces |
| `/api/v1/campaigns` | CRUD | Gestionar campañas |

---

## Comandos Útiles

### Systemd

```bash
# Estado
sudo systemctl status mediaflow

# Reiniciar
sudo systemctl restart mediaflow

# Ver logs
sudo journalctl -u mediaflow -f

# Recargar después de cambios en .service
sudo systemctl daemon-reload
```

### Nginx

```bash
# Probar configuración
sudo nginx -t

# Recargar
sudo systemctl reload nginx

# Ver logs
sudo tail -f /var/log/nginx/error.log
```

### Base de Datos

```bash
# Conectar a PostgreSQL
sudo -u postgres psql mediaflow

# Backup
sudo -u postgres pg_dump mediaflow > backup.sql

# Restaurar
sudo -u postgres psql mediaflow < backup.sql

# Ejecutar migraciones
cd /var/www/mediaflow/backend
source venv/bin/activate
alembic upgrade head
```

### Docker

```bash
# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Ejecutar migraciones
docker-compose exec backend alembic upgrade head

# Rebuild
docker-compose build --no-cache
```

---

## Variables de Entorno Requeridas

### Backend (.env)

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `DATABASE_URL` | ✅ | URL de conexión PostgreSQL |
| `ELEVENLABS_API_KEY` | ✅ | API key de ElevenLabs |
| `ANTHROPIC_API_KEY` | ✅ | API key de Anthropic |
| `SECRET_KEY` | ✅ | Key para JWT |
| `TENANT_ID` | ✅ | ID único del tenant |
| `TENANT_NAME` | ✅ | Nombre para mostrar |
| `TENANT_DOMAIN` | ✅ | Dominio del sitio |
| `CORS_ORIGINS` | ✅ | Orígenes permitidos |
| `STORAGE_PATH` | ✅ | Ruta de almacenamiento |

### Frontend (build time)

| Variable | Descripción |
|----------|-------------|
| `VITE_API_URL` | URL del backend (vacío usa proxy) |

---

## Troubleshooting Rápido

### Backend no inicia

```bash
# Verificar imports
cd /var/www/mediaflow/backend
source venv/bin/activate
python -c "from app.main import app; print('OK')"

# Ver logs detallados
journalctl -u mediaflow -n 50
```

### Frontend no carga

```bash
# Verificar build
ls -la /var/www/mediaflow/frontend/dist/

# Reconstruir
cd /var/www/mediaflow/frontend
npm run build
```

### API no responde

```bash
# Probar localmente
curl http://localhost:8000/api/v1/config/tenant

# Verificar nginx
nginx -t
curl -I http://localhost/api/v1/config/tenant
```

### Migraciones fallan

```bash
# Ver estado actual
alembic current

# Ver historial
alembic history

# Downgrade si es necesario
alembic downgrade -1
```

---

*Última actualización: 2026-01-26*
