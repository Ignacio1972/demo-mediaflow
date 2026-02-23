# MediaFlow Website - Workflow V0 ↔ VPS

## Resumen

Desarrollo local en VPS, producción en Vercel. Flujo bidireccional via GitHub.

```
VPS (desarrollo) ←→ GitHub ←→ Vercel (producción)
                       ↑
                      V0 (opcional)
```

---

## Datos del Proyecto

| Campo | Valor |
|-------|-------|
| Repositorio | `https://github.com/Ignacio1972/v0-media-flow-website` |
| Rama | `main` |
| Directorio VPS | `/var/www/mediaflow-website` |
| Puerto desarrollo | `3003` |
| Dominio producción | `mediaflow.cl` (Vercel) |

### Stack

- Next.js 16.0.10
- React 19.2.0
- Node.js 18+ requerido

---

## Credenciales

> ⚠️ **CONFIDENCIAL** - No compartir este archivo

**GitHub Token:**
```
<GITHUB_TOKEN> (ver credenciales privadas)
```

---

## Setup Inicial (una sola vez)

```bash
# 1. Crear directorio
mkdir -p /var/www/mediaflow-website
cd /var/www/mediaflow-website

# 2. Clonar con token
git clone https://<GITHUB_TOKEN>@github.com/Ignacio1972/v0-media-flow-website.git .

# 3. Instalar dependencias (--legacy-peer-deps requerido por React 19)
npm install --legacy-peer-deps

# 4. Verificar que funciona
npm run dev -- -p 3003
```

---

## Comandos Diarios

### Antes de trabajar (traer cambios de V0/Vercel)
```bash
cd /var/www/mediaflow-website
git pull
```

### Mientras trabajas (ver cambios en vivo)
```bash
npm run dev -- -p 3003
# Abrir: http://localhost:3003 o http://IP-VPS:3003
```

### Cuando terminas (enviar a producción)
```bash
git add .
git commit -m "descripción del cambio"
git push
# Vercel despliega automáticamente
```

---

## Flujo de Trabajo

```
1. git pull                    ← Traer cambios de V0/GitHub
2. npm run dev -- -p 3003      ← Desarrollar localmente
3. (editar código)
4. git add . && git commit     ← Guardar cambios
5. git push                    ← Enviar a Vercel
6. (opcional) Usar V0 para más cambios
7. Volver al paso 1
```

---

## Puertos en Uso (referencia)

| Puerto | Servicio |
|--------|----------|
| 3000 | (ocupado) |
| 3001 | MediaFlow Backend |
| **3003** | **MediaFlow Website (dev)** |
| 5173 | MediaFlow Frontend |

---

## Solución de Problemas

### Conflicto de merge
```bash
git stash                 # Guardar cambios locales
git pull                  # Traer cambios remotos
git stash pop             # Aplicar cambios locales
# Resolver conflictos si hay
```

### Puerto ocupado
```bash
# Verificar qué usa el puerto
lsof -i :3003

# Usar otro puerto
npm run dev -- -p 3004
```

### Resetear todo
```bash
cd /var/www/mediaflow-website
git fetch origin
git reset --hard origin/main
npm install --legacy-peer-deps
```

---

*Última actualización: 2026-01-22*
