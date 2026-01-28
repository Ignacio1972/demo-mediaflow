# Sistema de Interrupcion TTS en Azuracast

**Fecha**: Enero 2026
**Version**: 1.0
**Requisito**: MediaFlow y Azuracast en el mismo VPS

---

## Resumen

Este documento describe como configurar el sistema de interrupcion TTS que permite a MediaFlow interrumpir la programacion de Azuracast para reproducir mensajes generados.

**Flujo**:
```
MediaFlow genera TTS → Sube a Azuracast → Envia comando de interrupcion → Liquidsoap reproduce inmediatamente
```

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                        MISMO VPS                                │
├─────────────────────────────┬───────────────────────────────────┤
│        MEDIAFLOW            │           AZURACAST               │
│                             │        (Docker container)         │
│  ┌─────────────────┐        │      ┌─────────────────┐          │
│  │ FastAPI Backend │───────────────│  API REST       │          │
│  └────────┬────────┘   HTTP │      │  :10080         │          │
│           │                 │      └─────────────────┘          │
│           │                 │                                   │
│           │ docker exec     │      ┌─────────────────┐          │
│           └─────────────────────── │  Liquidsoap     │          │
│                      socat  │      │  Socket         │          │
│                             │      └─────────────────┘          │
└─────────────────────────────┴───────────────────────────────────┘
```

---

## Requisitos Previos

### 1. Azuracast instalado en Docker

```bash
# Verificar que Azuracast esta corriendo
docker ps | grep azuracast

# Deberia mostrar algo como:
# azuracast   ghcr.io/azuracast/azuracast:latest   ...
```

### 2. Crear API Key en Azuracast

1. Ir a Azuracast Admin Panel
2. `Administration` → `API Keys`
3. Click `Add API Key`
4. Permisos: **Station Administrator** (o al menos permisos de subida y control)
5. Copiar la API Key generada

### 3. Crear carpeta de medios en Azuracast

1. Ir a la estacion
2. `Music Files` → `Folders`
3. Crear carpeta llamada `Grabaciones` (o el nombre que prefieras)

---

## Configuracion MediaFlow

### Variables de entorno (.env)

```bash
# AzuraCast Integration
AZURACAST_URL=http://localhost:10080        # URL interna del contenedor
AZURACAST_API_KEY=tu_api_key_aqui           # API Key creada en Azuracast
AZURACAST_STATION_ID=1                      # ID de la estacion (usualmente 1)
AZURACAST_STATION_NAME=mediaflow            # Nombre corto de la estacion
AZURACAST_MEDIA_FOLDER=Grabaciones          # Carpeta donde se suben los audios
```

**Nota sobre AZURACAST_STATION_NAME**: Este es el "short name" de la estacion en Azuracast, visible en la URL de la estacion. Ej: si la URL es `/station/mediaflow`, el nombre es `mediaflow`.

### Verificar conexion

```bash
# Desde el backend
curl -H "X-API-Key: TU_API_KEY" http://localhost:10080/api/station/1/status
```

---

## Como Funciona

### 1. Subida de archivo (API REST)

MediaFlow sube el audio a la libreria de Azuracast:

```python
# POST /api/station/{station_id}/files
{
    "path": "Grabaciones/archivo.mp3",
    "file": "base64_encoded_content"
}
```

### 2. Comando de interrupcion (Socket Liquidsoap)

Despues de subir, envia un comando al socket de Liquidsoap:

```bash
docker exec azuracast bash -c \
  'echo "interrupting_requests.push file:///var/azuracast/stations/mediaflow/media/Grabaciones/archivo.mp3" | \
   socat - UNIX-CONNECT:/var/azuracast/stations/mediaflow/config/liquidsoap.sock'
```

**Respuesta exitosa**: Devuelve un numero (request ID)

---

## Uso desde MediaFlow

### Endpoint API

```
POST /api/v1/library/{message_id}/send-to-radio
Query params:
  - interrupt: bool (default: true) - Si true, interrumpe reproduccion actual
```

### Ejemplo cURL

```bash
# Enviar mensaje ID 42 a la radio con interrupcion
curl -X POST "http://localhost:3001/api/v1/library/42/send-to-radio?interrupt=true"
```

### Desde el Frontend

El boton "Enviar a Radio" en la libreria llama a este endpoint automaticamente.

---

## Arquitectura del Codigo

### Archivos principales

| Archivo | Descripcion |
|---------|-------------|
| `backend/app/services/azuracast/client.py` | Cliente Azuracast con upload e interrupt |
| `backend/app/api/v1/endpoints/radio.py` | Endpoints de control de radio |
| `backend/app/api/v1/endpoints/library.py` | Endpoint send-to-radio (linea ~490) |
| `backend/app/core/config.py` | Variables de configuracion |

### Metodos principales del cliente

```python
class AzuraCastClient:
    async def upload_file(file_path, target_filename)    # Sube archivo a libreria
    async def interrupt_with_file(filename)              # Envia comando de interrupcion
    async def send_audio_to_radio(file_path, interrupt)  # Flujo completo
    async def check_connection()                          # Verifica conexion
    async def get_now_playing()                          # Info de reproduccion actual
    async def skip_song()                                # Salta cancion actual
```

---

## Troubleshooting

### Error: "Connection refused"

```bash
# Verificar que Azuracast esta corriendo
docker ps

# Verificar URL correcta (puerto interno)
curl http://localhost:10080/api/status
```

### Error: "API Key invalid"

1. Verificar que la API Key esta activa en Azuracast
2. Verificar permisos de la API Key
3. Regenerar si es necesario

### Error: "File not found" en interrupcion

```bash
# Verificar que el archivo existe en Azuracast
docker exec azuracast ls -la /var/azuracast/stations/mediaflow/media/Grabaciones/
```

### Error: Socket de Liquidsoap

```bash
# Verificar que el socket existe
docker exec azuracast ls -la /var/azuracast/stations/mediaflow/config/liquidsoap.sock

# Probar comando directo
docker exec azuracast bash -c 'echo "help" | socat - UNIX-CONNECT:/var/azuracast/stations/mediaflow/config/liquidsoap.sock'
```

### Verificar que socat esta instalado

```bash
docker exec azuracast which socat
# Deberia mostrar: /usr/bin/socat
```

---

## Comandos Utiles

### Ver cola de interrupciones

```bash
docker exec azuracast bash -c \
  'echo "interrupting_requests.queue" | \
   socat - UNIX-CONNECT:/var/azuracast/stations/mediaflow/config/liquidsoap.sock'
```

### Listar comandos disponibles

```bash
docker exec azuracast bash -c \
  'echo "help" | \
   socat - UNIX-CONNECT:/var/azuracast/stations/mediaflow/config/liquidsoap.sock'
```

### Ver estado del backend

```bash
curl -H "X-API-Key: TU_API_KEY" http://localhost:10080/api/station/1/status
```

---

## Configuracion Nginx (Produccion)

Si usas un proxy nginx para Azuracast:

```nginx
# /etc/nginx/sites-available/radio.conf
server {
    listen 80;
    server_name radio.tudominio.com;

    location / {
        proxy_pass http://localhost:10080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Importante**: MediaFlow debe usar la URL interna (`http://localhost:10080`) para comunicarse con Azuracast, no la URL publica.

---

## Limitaciones

| Limitacion | Descripcion |
|------------|-------------|
| Mismo servidor | MediaFlow y Azuracast deben estar en el mismo VPS |
| Docker requerido | Azuracast debe correr en Docker para acceder al socket |
| Permisos | El usuario que corre MediaFlow debe poder ejecutar `docker exec` |

---

## Referencias

- [Azuracast API Docs](https://www.azuracast.com/docs/developers/apis/)
- [Liquidsoap Server Commands](https://www.liquidsoap.info/doc-dev/server.html)
- [Azuracast Docker Installation](https://www.azuracast.com/docs/getting-started/installation/docker/)
