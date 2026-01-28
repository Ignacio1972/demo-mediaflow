# MediaFlow - Checklist Instalacion RSYNC

Checklist rapido para nuevas instalaciones.

---

## Pre-Instalacion

- [ ] VPS Ubuntu 22.04 LTS listo
- [ ] Dominio apuntando al VPS (DNS A record)
- [ ] Subdominio `radio.` apuntando al VPS (si usa Azuracast)
- [ ] API Key ElevenLabs
- [ ] API Key Anthropic
- [ ] Logo del cliente (PNG)
- [ ] Colores de marca del cliente

---

## Fase 1: Servidor Destino

```bash
# En el NUEVO VPS
./01-prepare-destination.sh
```

- [ ] Sistema actualizado
- [ ] Node.js 20 instalado
- [ ] Python 3.11 instalado
- [ ] PostgreSQL configurado
- [ ] Usuario mediaflow creado
- [ ] Firewall configurado

---

## Fase 2: RSYNC

```bash
# En el servidor ORIGEN
./02-rsync-from-origin.sh
```

- [ ] Backend sincronizado
- [ ] Frontend sincronizado
- [ ] Musica sincronizada
- [ ] **Sounds sincronizados** (intro_announcement.mp3, outro_announcement.mp3)
- [ ] Permisos ajustados

---

## Fase 3: Configuracion

```bash
# En el NUEVO VPS
./03-post-rsync-setup.sh
```

- [ ] Entorno virtual creado
- [ ] Dependencias instaladas
- [ ] .env configurado
- [ ] Migraciones ejecutadas
- [ ] Frontend build completado
- [ ] Systemd configurado
- [ ] Nginx configurado
- [ ] SSL instalado

---

## Fase 4: Datos y Logo

```bash
# Cargar datos
sudo -u postgres psql mediaflow < 04-load-initial-data.sql

# Subir logo
scp logo.png root@VPS:/var/www/mediaflow/frontend/public/tenants/TENANT_ID/logo.png

# Copiar a dist
cp /var/www/mediaflow/frontend/public/tenants/TENANT_ID/logo.png \
   /var/www/mediaflow/frontend/dist/tenants/TENANT_ID/logo.png
```

- [ ] Musica cargada en DB (7 tracks)
- [ ] Voces configuradas (3 voces)
- [ ] Categorias creadas (5 categorias)
- [ ] **Templates cargados** (7: vehiculos, horarios, empleados)
- [ ] Logo subido

---

## Verificacion Final

```bash
# Servicios
systemctl status mediaflow nginx postgresql

# API
curl http://localhost:3001/api/v1/config/tenant
curl http://localhost:3001/api/v1/settings/music
curl http://localhost:3001/api/v1/audio/voices

# Frontend
curl -I https://TU_DOMINIO/
```

- [ ] Backend respondiendo
- [ ] Frontend cargando
- [ ] Logo visible
- [ ] Musica disponible
- [ ] Generacion TTS funciona

---

## Fase 5: Azuracast (Requerido para Radio)

Si el cliente necesita radio streaming con interrupcion TTS:

```bash
# Instalar Docker
curl -fsSL https://get.docker.com | sh

# Instalar Azuracast
mkdir -p /var/azuracast && cd /var/azuracast
curl -fsSL https://raw.githubusercontent.com/AzuraCast/AzuraCast/main/docker.sh > docker.sh
chmod +x docker.sh
./docker.sh install

# Cambiar puertos (nginx usa 80)
docker compose down
sed -i 's/# AZURACAST_HTTP_PORT=80/AZURACAST_HTTP_PORT=8080/' .env
sed -i 's/# AZURACAST_HTTPS_PORT=443/AZURACAST_HTTPS_PORT=8443/' .env
docker compose up -d

# Abrir puertos
ufw allow 8080/tcp
ufw allow 8000/tcp
```

- [ ] Docker instalado
- [ ] Azuracast instalado
- [ ] Puertos cambiados (8080/8443)
- [ ] Panel accesible: http://IP:8080
- [ ] Usuario admin creado
- [ ] **Estacion creada** (anotar el Short Name)
- [ ] **Carpeta `Grabaciones` creada** en Music Files

---

## Fase 6: Integracion MediaFlow ↔ Azuracast (CRITICO)

- [ ] **API Key creada** en Azuracast (Administration → API Keys)
- [ ] **.env actualizado** con variables de Azuracast:
  ```
  AZURACAST_URL=http://localhost:8080
  AZURACAST_API_KEY=<key>
  AZURACAST_STATION_ID=1
  AZURACAST_STATION_NAME=<short_name>
  AZURACAST_MEDIA_FOLDER=Grabaciones
  ```
- [ ] **MediaFlow reiniciado** (`systemctl restart mediaflow`)
- [ ] **Nginx proxy** para radio.dominio (opcional)
- [ ] **SSL** para radio.dominio (opcional)

---

## Fase 7: Verificacion del Sistema de Interrupcion TTS

```bash
# 1. Archivos de sonido
ls -la /var/www/mediaflow/storage/sounds/
# DEBE mostrar intro_announcement.mp3 y outro_announcement.mp3

# 2. Conexion Azuracast
curl http://localhost:3001/api/v1/radio/status
# DEBE responder: {"success":true,"status":"online",...}

# 3. Socket Liquidsoap
docker exec azuracast ls /var/azuracast/stations/STATION_NAME/config/liquidsoap.sock
# DEBE existir (si no, docker compose restart y esperar 30s)

# 4. Prueba de interrupcion real
curl -X POST "http://localhost:3001/api/v1/library/1/send-to-radio?interrupt=true"
# DEBE responder: {"success":true,...,"interrupt":{"success":true,"request_id":"..."}}
```

- [ ] **intro_announcement.mp3 existe** en storage/sounds/
- [ ] **outro_announcement.mp3 existe** en storage/sounds/
- [ ] **Radio status: online** (`/api/v1/radio/status`)
- [ ] **Socket Liquidsoap existe** (dentro del contenedor)
- [ ] **Interrupcion funciona** (enviar audio de prueba a la radio)

---

## Resumen de Puertos

| Puerto | Servicio |
|--------|----------|
| 80/443 | Nginx → MediaFlow |
| 3001 | MediaFlow Backend |
| 8080 | Azuracast Panel |
| 8000 | Radio Stream |

---

## Comandos Utiles

```bash
# MediaFlow logs
journalctl -u mediaflow -f

# Reiniciar MediaFlow
systemctl restart mediaflow

# Rebuild frontend
cd /var/www/mediaflow/frontend && npm run build

# Azuracast logs
cd /var/azuracast && docker compose logs -f

# Reiniciar Azuracast
cd /var/azuracast && docker compose restart

# Verificar socket Liquidsoap
docker exec azuracast ls -la /var/azuracast/stations/STATION_NAME/config/liquidsoap.sock
```

---

*Basado en instalacion MBI (mbi.mediaflow.cl) - 2026-01-26, actualizado 2026-01-28*
