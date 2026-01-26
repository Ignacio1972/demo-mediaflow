# MediaFlow v2.1 - Installation Files

Esta carpeta contiene toda la documentacion y archivos necesarios para instalar MediaFlow en un nuevo servidor.

---

## Metodo Recomendado: RSYNC

**Para nuevas instalaciones, usar el metodo RSYNC** (carpeta `rsync/`).

Es mas rapido y garantiza que el codigo sea identico al servidor origen.

```
rsync/
├── README.md                      # Guia completa RSYNC
├── CHECKLIST.md                   # Checklist rapido
└── scripts/
    ├── 01-prepare-destination.sh  # Preparar VPS destino
    ├── 02-rsync-from-origin.sh    # Ejecutar rsync
    ├── 03-post-rsync-setup.sh     # Configuracion post-rsync
    └── 04-load-initial-data.sql   # Datos iniciales
```

---

## Documentacion Adicional

| Archivo | Descripcion |
|---------|-------------|
| **QUICK_INSTALL.md** | Guia manual (sin rsync) |
| **DEPLOYMENT_GUIDE.md** | Guia completa con explicaciones detalladas |
| **TROUBLESHOOTING.md** | Solucion de problemas comunes |
| **FILES_REFERENCE.md** | Referencia de estructura del proyecto |

---

## Carpeta configs/

Archivos de configuracion listos para usar:

| Archivo | Destino en Servidor |
|---------|---------------------|
| `mediaflow.service` | `/etc/systemd/system/mediaflow.service` |
| `nginx-mediaflow.conf` | `/etc/nginx/sites-available/mediaflow` |
| `env.production.example` | `/var/www/mediaflow/backend/.env` |

---

## Uso Rapido

### Nueva Instalacion

1. Leer `QUICK_INSTALL.md` para instalacion rapida
2. Copiar archivos de `configs/` al servidor
3. Editar configuraciones con tus valores
4. Seguir los pasos de la guia

### Problemas

1. Consultar `TROUBLESHOOTING.md`
2. Revisar logs: `journalctl -u mediaflow -f`

---

## Checklist Pre-Instalacion

- [ ] VPS Ubuntu 22.04 LTS
- [ ] Minimo 2GB RAM
- [ ] Dominio configurado (DNS A record)
- [ ] API Key ElevenLabs
- [ ] API Key Anthropic
- [ ] Acceso SSH root

---

## Configuraciones Importantes

### Puerto del Backend

MediaFlow usa **puerto 3001** por defecto para compatibilidad con Azuracast (que usa 8000).

### PATH del Servicio Systemd

El servicio DEBE incluir `/usr/bin` en el PATH para que ffprobe funcione:

```ini
Environment="PATH=/var/www/mediaflow/backend/venv/bin:/usr/bin:/usr/local/bin"
```

### Modelo de Claude

Usar modelos actuales:
- `claude-sonnet-4-20250514` (recomendado)
- `claude-3-5-sonnet-latest`

**NO usar:** `claude-3-5-sonnet-20241022` (deprecado)

---

## Soporte

- GitHub Issues: https://github.com/tu-org/mediaflow-v2/issues

---

*Ultima actualizacion: 2026-01-26*
