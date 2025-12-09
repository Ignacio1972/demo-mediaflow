# Handover: Sistema de IA y Claude - MediaFlow v2

**Fecha**: 2024-12-09
**Estado**: Backend completo, Frontend 90% completo

---

## Resumen

Se implemento el sistema de IA con gestion de clientes/contextos. Falta completar la integracion final del frontend.

---

## Lo que YA esta hecho

### Backend (100% completo)

| Archivo | Descripcion |
|---------|-------------|
| `backend/app/models/ai_client.py` | Modelo SQLAlchemy AIClient |
| `backend/app/schemas/ai_client.py` | Schemas Pydantic |
| `backend/app/services/ai/client_manager.py` | Servicio CRUD de clientes |
| `backend/app/services/ai/claude.py` | Metodo `generate_announcements()` agregado |
| `backend/app/api/v1/endpoints/settings/ai_clients.py` | Endpoints CRUD completos |
| `backend/app/api/v1/endpoints/ai.py` | Endpoint POST `/api/v1/ai/generate` |
| `backend/app/api/v1/serializers/ai_client_serializer.py` | Serializador |
| `backend/alembic/versions/a1b2c3d4e5f6_add_ai_clients_table.py` | Migracion con 3 clientes ejemplo |

**Routers ya integrados** en:
- `backend/app/api/v1/endpoints/settings/__init__.py`
- `backend/app/api/v1/serializers/__init__.py`
- `backend/app/models/__init__.py`

### Frontend (90% completo)

| Archivo | Descripcion |
|---------|-------------|
| `frontend/src/composables/useAIClients.ts` | Composable clientes |
| `frontend/src/composables/useAISuggestions.ts` | Composable sugerencias |
| `frontend/src/components/settings/ai-clients/AIClientManager.vue` | Manager principal |
| `frontend/src/components/settings/ai-clients/components/AIClientList.vue` | Lista |
| `frontend/src/components/settings/ai-clients/components/AIClientEditor.vue` | Editor |
| `frontend/src/components/settings/ai-clients/components/AIClientCard.vue` | Card |
| `frontend/src/components/settings/ai-clients/components/AIClientAddModal.vue` | Modal crear |
| `frontend/src/components/settings/ai-clients/composables/useAIClientManager.ts` | Composable manager |

---

## Lo que FALTA hacer (Fase 7)

### 1. Agregar ruta en router

**Archivo**: `frontend/src/router/index.ts`

Agregar dentro de las rutas de settings:

```typescript
{
  path: 'ai-clients',
  name: 'settings-ai-clients',
  component: () => import('@/components/settings/ai-clients/AIClientManager.vue'),
}
```

### 2. Agregar link en SettingsNav

**Archivo**: `frontend/src/components/settings/SettingsNav.vue`

Agregar un nuevo link de navegacion para "AI Clients" con icono de robot.

### 3. Ejecutar migracion de base de datos

```bash
cd /var/www/mediaflow-v2/backend
source venv/bin/activate
alembic upgrade head
```

### 4. (Opcional) Actualizar AISuggestions del Dashboard

**Archivo**: `frontend/src/components/dashboard/AISuggestions.vue`

Cambiar llamada de `/api/v1/ai/suggest` a `/api/v1/ai/generate` para usar el nuevo endpoint con contexto de cliente.

El nuevo endpoint espera:
```typescript
{
  context: string,      // descripcion del anuncio
  category?: string,    // 'general', 'ofertas', 'eventos', etc.
  tone?: string,        // 'profesional', 'entusiasta', 'amigable', 'urgente', 'informativo'
  duration?: number,    // 5-30 segundos
  mode?: 'normal' | 'automatic'
}
```

Y retorna:
```typescript
{
  success: boolean,
  suggestions: [{
    id: string,
    text: string,
    char_count: number,
    word_count: number,
    created_at: string
  }],
  model: string,
  active_client_id: string | null
}
```

---

## Verificacion

1. Backend corriendo: `http://localhost:3001/api/docs` - verificar endpoints `/settings/ai-clients/*`
2. Frontend: Navegar a `/settings/ai-clients`
3. Debe mostrar 3 clientes pre-configurados (Default, Supermercado Ejemplo, Mall Ejemplo)
4. CRUD completo funcional
5. Boton "Establecer como Activo" cambia el cliente usado en generacion

---

## Endpoints API disponibles

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/v1/settings/ai-clients` | Listar todos |
| GET | `/api/v1/settings/ai-clients/active` | Obtener cliente activo |
| GET | `/api/v1/settings/ai-clients/{id}` | Obtener uno |
| POST | `/api/v1/settings/ai-clients` | Crear nuevo |
| PATCH | `/api/v1/settings/ai-clients/{id}` | Actualizar |
| DELETE | `/api/v1/settings/ai-clients/{id}` | Eliminar |
| POST | `/api/v1/settings/ai-clients/active/{id}` | Establecer activo |
| PUT | `/api/v1/settings/ai-clients/reorder` | Reordenar |
| POST | `/api/v1/ai/generate` | Generar anuncios con contexto |

---

## Notas importantes

- El cliente "default" viene marcado como `is_default=true`
- No se puede eliminar el cliente activo ni el unico cliente
- El endpoint `/generate` obtiene automaticamente el contexto del cliente activo
- Los tonos estan en espanol: profesional, entusiasta, amigable, urgente, informativo
