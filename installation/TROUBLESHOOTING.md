# MediaFlow v2.1 - Troubleshooting Guide

Guia de solucion de problemas basada en instalaciones reales.

---

## Errores de Audio Generation

### Error: ffprobe not found

**Mensaje de error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffprobe'
```

**Causa:** El servicio systemd tiene un PATH restringido que no incluye `/usr/bin` donde esta ffprobe.

**Solucion:**
```bash
# Verificar que ffmpeg esta instalado
which ffprobe  # Debe mostrar /usr/bin/ffprobe

# Editar el servicio
sed -i 's|Environment="PATH=/var/www/mediaflow/backend/venv/bin"|Environment="PATH=/var/www/mediaflow/backend/venv/bin:/usr/bin:/usr/local/bin"|' /etc/systemd/system/mediaflow.service

# Reiniciar
systemctl daemon-reload
systemctl restart mediaflow
```

**Prevencion:** Usar el archivo `mediaflow.service` actualizado de `/installation/configs/`.

---

### Error: 500 en /api/v1/audio/generate

**Pasos de diagnostico:**
```bash
# Ver logs del backend
journalctl -u mediaflow -n 50 --no-pager

# Buscar el error especifico
journalctl -u mediaflow | grep -A 10 "audio/generate"
```

**Causas comunes:**
1. ffprobe no encontrado (ver arriba)
2. ElevenLabs API key invalida
3. Permisos de escritura en storage

---

## Errores de AI Suggestions

### Error: model not found (Claude)

**Mensaje de error:**
```
anthropic.NotFoundError: Error code: 404 - model: claude-3-5-sonnet-20241022
```

**Causa:** El modelo de Claude configurado no existe o fue deprecado.

**Solucion:**
```bash
# Actualizar el modelo en .env
sed -i 's/claude-3-5-sonnet-20241022/claude-sonnet-4-20250514/' /var/www/mediaflow/backend/.env

# Reiniciar
systemctl restart mediaflow
```

**Modelos validos (2026):**
- `claude-sonnet-4-20250514` (recomendado)
- `claude-3-5-sonnet-latest`
- `claude-opus-4-5-20251101`

---

## Errores de Build Frontend

### Error: SyntaxError await import

**Mensaje de error:**
```
SyntaxError: Unexpected reserved word
    at await import('source-map-support')
```

**Causa:** Version de Node.js muy antigua. Ubuntu 22.04 instala Node 12 por defecto.

**Solucion:**
```bash
# Instalar Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt remove -y libnode-dev
apt install -y nodejs

# Verificar
node -v  # Debe ser v20.x.x

# Reconstruir
cd /var/www/mediaflow/frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

### Error: conflicto libnode-dev

**Mensaje de error:**
```
trying to overwrite '/usr/include/node/common.gypi', which is also in package libnode-dev
```

**Solucion:**
```bash
apt remove -y libnode-dev
apt install -y nodejs
```

---

## Errores de Base de Datos

### Error: datetime('now') does not exist

**Mensaje de error:**
```
asyncpg.exceptions.UndefinedFunctionError: function datetime(unknown) does not exist
```

**Causa:** Las migraciones de Alembic usan sintaxis SQLite que no funciona en PostgreSQL.

**Solucion:**
Editar los archivos en `backend/alembic/versions/`:

```python
# INCORRECTO (SQLite)
server_default=sa.text("datetime('now')")

# CORRECTO (PostgreSQL)
server_default=sa.text("NOW()")
```

```python
# INCORRECTO (SQLite boolean)
sa.Column('active', sa.Boolean(), server_default='1')

# CORRECTO (PostgreSQL boolean)
sa.Column('active', sa.Boolean(), server_default='true')
```

**Archivos comunmente afectados:**
- `a1b2c3d4e5f6_add_ai_clients_table.py`

---

### Error: conexion a PostgreSQL

**Pasos de diagnostico:**
```bash
# Verificar que PostgreSQL esta corriendo
systemctl status postgresql

# Probar conexion
sudo -u postgres psql -c "SELECT 1;"

# Verificar usuario y base de datos
sudo -u postgres psql -c "\du"
sudo -u postgres psql -c "\l"

# Probar conexion con usuario mediaflow
PGPASSWORD='tu_password' psql -U mediaflow -d mediaflow -c "SELECT 1;"
```

---

## Errores de Nginx

### Error: 502 Bad Gateway

**Causa:** El backend no esta corriendo o nginx no puede conectarse.

**Solucion:**
```bash
# Verificar backend
systemctl status mediaflow
curl http://localhost:3001/api/v1/config/tenant

# Si el backend esta en otro puerto, actualizar nginx
grep "server 127" /etc/nginx/sites-available/mediaflow

# Reiniciar nginx
nginx -t && systemctl reload nginx
```

---

### Error: 404 en rutas del frontend

**Causa:** Falta la configuracion de SPA fallback en nginx.

**Solucion:** Asegurar que nginx tenga:
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

---

## Errores de Permisos

### Error: Permission denied en storage

**Solucion:**
```bash
chown -R mediaflow:mediaflow /var/www/mediaflow
chmod 755 /var/www/mediaflow/storage
chmod 755 /var/www/mediaflow/storage/*
```

---

### Error: Permission denied en .env

**Solucion:**
```bash
chown mediaflow:mediaflow /var/www/mediaflow/backend/.env
chmod 600 /var/www/mediaflow/backend/.env
```

---

## Errores de Puerto

### Error: Puerto 8000 ocupado por Azuracast

**Causa:** Azuracast usa el puerto 8000 por defecto.

**Solucion:** MediaFlow debe usar puerto 3001:

1. En `.env`:
```env
PORT=3001
```

2. En `mediaflow.service`:
```ini
ExecStart=... --port 3001 ...
```

3. En nginx:
```nginx
upstream mediaflow_backend {
    server 127.0.0.1:3001;
}
```

4. Reiniciar:
```bash
systemctl daemon-reload
systemctl restart mediaflow
systemctl reload nginx
```

---

## Comandos de Diagnostico

```bash
# Estado general
systemctl status mediaflow nginx postgresql

# Logs del backend
journalctl -u mediaflow -f

# Logs de nginx
tail -f /var/log/nginx/error.log

# Probar backend directamente
curl http://localhost:3001/api/v1/config/tenant

# Probar a traves de nginx
curl -I https://tu-dominio.com/api/v1/config/tenant

# Ver puertos en uso
ss -tlnp | grep -E '3001|8000|80|443'

# Verificar imports del backend
cd /var/www/mediaflow/backend
source venv/bin/activate
python -c "from app.main import app; print('OK')"
```

---

*Ultima actualizacion: 2026-01-26*
