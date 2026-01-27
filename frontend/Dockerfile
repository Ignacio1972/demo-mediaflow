# MediaFlow Frontend - Dockerfile
# Multi-stage build: Node.js build + Nginx serve

# ============================================
# Stage 1: Build
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production=false

# Copiar código fuente
COPY . .

# Build de producción
RUN npm run build

# ============================================
# Stage 2: Serve con Nginx
# ============================================
FROM nginx:alpine

# Copiar configuración de nginx
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Copiar build desde stage anterior
COPY --from=builder /app/dist /usr/share/nginx/html

# Permisos
RUN chown -R nginx:nginx /usr/share/nginx/html

# Puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Comando
CMD ["nginx", "-g", "daemon off;"]
