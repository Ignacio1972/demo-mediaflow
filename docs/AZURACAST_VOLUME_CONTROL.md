# Control de Volumen Master en Azuracast

**Fecha**: Enero 2025
**Estado**: Documentado (No implementado)

---

## Resumen

Azuracast **no tiene un endpoint REST** para controlar el volumen master del stream. Sin embargo, es posible implementarlo usando **Liquidsoap interactive variables**.

---

## Cómo funciona

### 1. Configurar Liquidsoap (una vez, en Azuracast)

En Azuracast: `Utilities > Edit Liquidsoap Configuration`
(Requiere habilitar **Advanced Features** en la estación)

Agregar:

```liquidsoap
master_volume = interactive.float("master_volume", 1.)
radio = amplify(master_volume, radio)
```

### 2. Enviar comandos al socket

```bash
# Bajar volumen al 70%
echo "var.set master_volume = 0.7" | socat - UNIX-CONNECT:/path/to/liquidsoap.sock

# Subir volumen al 100%
echo "var.set master_volume = 1.0" | socat - UNIX-CONNECT:/path/to/liquidsoap.sock

# Leer volumen actual
echo "var.get master_volume" | socat - UNIX-CONNECT:/path/to/liquidsoap.sock
```

---

## Implementacion sugerida

### Backend (Python)

Agregar a `backend/app/services/azuracast/client.py`:

```python
async def set_volume(self, level: float) -> dict:
    """
    Set master volume (0.0 to 1.0).
    Requires interactive.float configured in Liquidsoap.
    """
    import asyncio

    level = max(0.0, min(1.0, level))  # Clamp 0-1

    socket_path = f"/var/azuracast/stations/{self.station_name}/config/liquidsoap.sock"
    command = f'var.set master_volume = {level}'
    docker_cmd = [
        'docker', 'exec', 'azuracast', 'bash', '-c',
        f'echo "{command}" | socat - UNIX-CONNECT:{socket_path}'
    ]

    process = await asyncio.create_subprocess_exec(
        *docker_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    return {
        "success": process.returncode == 0,
        "level": level,
        "message": f"Volume set to {int(level * 100)}%"
    }

async def get_volume(self) -> dict:
    """Get current master volume level."""
    import asyncio

    socket_path = f"/var/azuracast/stations/{self.station_name}/config/liquidsoap.sock"
    command = 'var.get master_volume'
    docker_cmd = [
        'docker', 'exec', 'azuracast', 'bash', '-c',
        f'echo "{command}" | socat - UNIX-CONNECT:{socket_path}'
    ]

    process = await asyncio.create_subprocess_exec(
        *docker_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    try:
        level = float(stdout.decode().strip())
    except:
        level = 1.0

    return {"level": level}
```

### Endpoint API

Agregar a `backend/app/api/v1/endpoints/radio.py`:

```python
@router.post("/volume")
async def set_volume(level: float = Query(..., ge=0.0, le=1.0)):
    """Set master volume (0.0 - 1.0)"""
    result = await azuracast_client.set_volume(level)
    return result

@router.get("/volume")
async def get_volume():
    """Get current master volume"""
    return await azuracast_client.get_volume()
```

### Frontend

En `MusicPage.vue`, agregar slider conectado a `/api/v1/radio/volume`.

---

## Limitaciones

| Limitacion | Descripcion |
|------------|-------------|
| Configuracion manual | Requiere editar Liquidsoap una vez en Azuracast |
| Persistencia | El volumen se resetea a 1.0 si Liquidsoap reinicia |
| Regeneracion | Azuracast puede sobreescribir config en actualizaciones |

---

## Alternativas

1. **Volumen por track**: Usar `liq_amplify` en metadata (solo afecta canciones individuales)
2. **ReplayGain**: Normaliza volumen automaticamente entre canciones
3. **LADSPA plugins**: Procesamiento de audio avanzado en Liquidsoap

---

## Referencias

- [Liquidsoap Server Interaction](https://liquidsoap.readthedocs.io/en/latest/content/server.html)
- [Liquidsoap Interactive Variables](https://www.liquidsoap.info/doc-dev/server.html)
- [Azuracast Liquidsoap Customization](https://github.com/AzuraCast/AzuraCast/issues/608)
- [Azuracast Liquidsoap Docs](https://www.azuracast.com/docs/developers/liquidsoap/)
- [Azuracast OpenAPI Spec](https://raw.githubusercontent.com/AzuraCast/AzuraCast/main/web/static/openapi.yml)

---

## Comandos utiles

```bash
# Listar variables interactivas disponibles
docker exec azuracast bash -c 'echo "var.list" | socat - UNIX-CONNECT:/path/to/liquidsoap.sock'

# Ver ayuda de comandos
docker exec azuracast bash -c 'echo "help" | socat - UNIX-CONNECT:/path/to/liquidsoap.sock'
```
