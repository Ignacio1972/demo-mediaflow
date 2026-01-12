# Fase 5: Testing y Documentación

**Plan Maestro**: `CLIENT_PROFILE_SYSTEM.md`
**Dependencia**: Fase 4 completada
**Estado**: Pendiente

---

## Objetivo

Realizar testing exhaustivo del sistema completo y actualizar la documentación.

---

## Tests E2E

### Test Suite 1: Flujo Completo de Configuración

```
ESCENARIO: Configurar nuevo cliente con instrucciones por campaña

PASOS:
1. Ir a Settings > AI Clients
2. Click "Agregar Cliente"
3. Llenar:
   - Nombre: "Supermercado Test"
   - Contexto: "Somos un supermercado de prueba..."
4. Guardar
5. Activar el nuevo cliente
6. Expandir "Instrucciones por Campaña"
7. Configurar instrucciones para:
   - Navidad: "Tono festivo, ofertas navideñas..."
   - Pedidos: "Mencionar nombre del cliente..."
8. Guardar cada una
9. Ir a Campaigns > Navidad
10. Verificar:
    - Cliente activo: "Supermercado Test"
    - Instrucciones: "Tono festivo..."
11. Generar sugerencia de audio
12. Verificar que las sugerencias reflejan el contexto

RESULTADO ESPERADO:
- Todas las sugerencias tienen tono festivo/navideño
- El contexto del cliente se aplica correctamente
```

### Test Suite 2: Cambio de Cliente

```
ESCENARIO: Cambiar de cliente y verificar que todo cambia

PREREQUISITO:
- Cliente A (Supermercado) configurado con instrucciones
- Cliente B (Farmacia) configurado con instrucciones diferentes

PASOS:
1. En Settings, verificar que Cliente A está activo
2. Ir a Campaigns > Navidad
3. Anotar las instrucciones actuales
4. Volver a Settings
5. Activar Cliente B (Farmacia)
6. Volver a Campaigns > Navidad
7. Verificar que:
   - El cliente mostrado cambió a "Farmacia"
   - Las instrucciones son las de Farmacia (diferentes)
8. Generar sugerencia
9. Verificar que refleja contexto de Farmacia

RESULTADO ESPERADO:
- Todo cambia automáticamente al cambiar cliente activo
- Sin necesidad de recargar página manualmente
```

### Test Suite 3: Edición desde Campaigns

```
ESCENARIO: Usuario de Marketing edita instrucciones

PASOS:
1. Ir a Campaigns > Ofertas
2. Verificar que el cliente activo es read-only
3. Editar instrucciones: "Esta semana descuentos en lácteos"
4. Click Guardar
5. Ir a Settings > AI Clients
6. Seleccionar el cliente activo
7. Expandir "Instrucciones por Campaña"
8. Verificar que Ofertas tiene: "Esta semana descuentos en lácteos"

RESULTADO ESPERADO:
- Cambios desde Campaigns se reflejan en Settings
- Sincronización bidireccional funciona
```

### Test Suite 4: Sin Cliente Activo

```
ESCENARIO: Sistema sin cliente activo configurado

PASOS:
1. En BD, desactivar todos los clientes (is_default = false)
2. Ir a Campaigns > Navidad
3. Verificar:
   - Mensaje: "Sin cliente configurado"
   - Textarea deshabilitado
   - No se puede guardar
4. Intentar generar sugerencia
5. Verificar que usa prompt genérico (sin contexto de cliente)

RESULTADO ESPERADO:
- Sistema funciona aunque no haya cliente activo
- Mensajes claros al usuario
```

### Test Suite 5: Múltiples Campañas

```
ESCENARIO: Verificar aislamiento entre campañas

PASOS:
1. Configurar cliente con:
   - Navidad: "Instrucciones de Navidad"
   - Ofertas: "Instrucciones de Ofertas"
   - Pedidos: (vacío)
2. Ir a Campaigns > Navidad
3. Verificar instrucciones de Navidad
4. Ir a Campaigns > Ofertas
5. Verificar instrucciones de Ofertas (diferentes)
6. Ir a Campaigns > Pedidos
7. Verificar que está vacío
8. Generar audio en Pedidos
9. Verificar que usa solo contexto general (sin instrucciones de campaña)

RESULTADO ESPERADO:
- Cada campaña tiene sus propias instrucciones
- No hay mezcla entre campañas
```

---

## Tests de Regresión

### Dashboard debe seguir funcionando

```
PASOS:
1. Ir a Dashboard
2. Generar audio con cualquier configuración
3. Verificar que funciona correctamente
4. No debe haber errores en consola

RESULTADO: Dashboard no afectado por cambios
```

### Library debe seguir funcionando

```
PASOS:
1. Ir a Library
2. Reproducir audios existentes
3. Filtrar por categoría
4. Verificar que todo funciona

RESULTADO: Library no afectada por cambios
```

---

## Checklist de Testing

### Backend
- [ ] GET /active/campaign-prompts funciona
- [ ] GET /active/campaign-prompts/{id} funciona
- [ ] PATCH /active/campaign-prompts/{id} funciona
- [ ] DELETE /active/campaign-prompts/{id} funciona
- [ ] /ai/generate usa AIClient.custom_prompts
- [ ] /ai/generate funciona sin cliente activo
- [ ] /ai/generate funciona sin campaign_id
- [ ] Migración de datos exitosa

### Frontend - Campaigns
- [ ] AITrainingPanel muestra cliente activo
- [ ] Cliente activo es read-only
- [ ] Cargar instrucciones funciona
- [ ] Guardar instrucciones funciona
- [ ] Cancelar cambios funciona
- [ ] Estados loading/error correctos
- [ ] Watch de campaignId funciona

### Frontend - Settings
- [ ] CampaignPromptsEditor carga campañas
- [ ] Expandir/colapsar funciona
- [ ] Editar instrucciones funciona
- [ ] Guardar individual funciona
- [ ] Contador de configuradas correcto
- [ ] Sincronización con Campaigns funciona
- [ ] Invalidación de cache al cambiar cliente

### Integración
- [ ] Cambio de cliente activo actualiza todo
- [ ] Edición bidireccional funciona
- [ ] Generación de audio usa contexto correcto
- [ ] Sin mezcla de contextos

---

## Actualizar Documentación

### 4.1 Actualizar CLAUDE.md

Agregar sección sobre el nuevo sistema:

```markdown
## Sistema de Perfiles de Cliente (2025-01)

### Arquitectura

Las instrucciones de IA por campaña están vinculadas al cliente activo:

```
AIClient {
  id: "supermercado",
  context: "Contexto global...",
  custom_prompts: {
    "navidad": "Instrucciones para Navidad...",
    "ofertas": "Instrucciones para Ofertas...",
  }
}
```

### Flujo de Datos

1. Admin activa cliente en Settings
2. Marketing edita instrucciones en Campaigns
3. Instrucciones se guardan en AIClient.custom_prompts[campaign_id]
4. Al generar audio, se combinan:
   - AIClient.context (contexto general)
   - AIClient.custom_prompts[campaign_id] (instrucciones de campaña)

### Endpoints Relevantes

| Endpoint | Descripción |
|----------|-------------|
| GET /settings/ai-clients/active/campaign-prompts | Listar todas |
| GET /settings/ai-clients/active/campaign-prompts/{id} | Obtener una |
| PATCH /settings/ai-clients/active/campaign-prompts/{id} | Actualizar |

### Composable

```typescript
import { useClientCampaignPrompts } from '@/composables/useClientCampaignPrompts'

const {
  activeClient,
  getCampaignInstructions,
  saveCampaignInstructions
} = useClientCampaignPrompts()
```

### Gotchas

1. **Category.ai_instructions está DEPRECADO**
   - Ya no se usa, pero no se eliminó de la BD
   - Leer siempre de AIClient.custom_prompts

2. **El cliente activo es read-only en Campaigns**
   - Solo se puede cambiar desde Settings
   - Marketing no puede cambiar de cliente
```

### 4.2 Crear Guía de Usuario

**Archivo**: `docs/USER_GUIDE_CLIENT_PROFILES.md`

```markdown
# Guía de Usuario: Sistema de Perfiles de Cliente

## Para Administradores

### Configurar un Nuevo Cliente

1. Ir a **Settings > AI Clients**
2. Click en **Agregar Cliente**
3. Llenar:
   - **Nombre**: Nombre del cliente (ej: "Supermercado Líder")
   - **Contexto**: Descripción del negocio para la IA
4. **Guardar**
5. Click en **Activar** para hacer este cliente el activo

### Configurar Instrucciones por Campaña

1. En **Settings > AI Clients**, seleccionar el cliente
2. Expandir **Instrucciones por Campaña**
3. Click en la campaña que desea configurar
4. Escribir las instrucciones específicas
5. Click **Guardar**

### Cambiar de Cliente Activo

1. Ir a **Settings > AI Clients**
2. En la lista de clientes, click **Activar** en el cliente deseado
3. Todas las campañas usarán automáticamente el nuevo cliente

## Para Marketing

### Ver el Cliente Activo

Al entrar a cualquier campaña, verá en el panel derecho:
- 🏪 **Cliente: [Nombre del cliente]**
- Este es el cliente actualmente configurado por el administrador

### Editar Instrucciones de Campaña

1. Ir a **Campaigns** y seleccionar una campaña
2. En el panel **Entrenamiento IA**:
   - Escribir las instrucciones específicas
   - Click **Guardar**
3. Las instrucciones se guardarán para el cliente activo

### Importante

- No puede cambiar el cliente activo desde Campaigns
- Para cambiar de cliente, contacte al administrador
- Las instrucciones que edite se guardan para el cliente actual

## Preguntas Frecuentes

### ¿Por qué cambiaron mis instrucciones?

Si el administrador cambió el cliente activo, verá las instrucciones
del nuevo cliente. Sus instrucciones anteriores no se perdieron,
siguen guardadas en el cliente anterior.

### ¿Cómo sé qué cliente está activo?

En cualquier campaña, el panel de Entrenamiento IA muestra
el cliente activo en la parte superior.

### ¿Puedo ver instrucciones de otro cliente?

Solo el administrador puede ver y editar instrucciones de
clientes no activos desde Settings.
```

---

## Checklist Final

- [ ] Todos los tests E2E pasan
- [ ] Tests de regresión pasan
- [ ] CLAUDE.md actualizado
- [ ] Guía de usuario creada
- [ ] Build de producción funciona
- [ ] No hay errores en consola
- [ ] No hay warnings de TypeScript
- [ ] Código revisado y limpio

---

## Despliegue

### Pre-despliegue

```bash
# 1. Backup de base de datos
pg_dump mediaflow > backup_$(date +%Y%m%d).sql

# 2. Verificar que migración funciona
python scripts/migrate_campaign_instructions.py --dry-run
```

### Despliegue

```bash
# 1. Pull cambios
git pull origin main

# 2. Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python scripts/migrate_campaign_instructions.py  # Solo primera vez

# 3. Frontend
cd ../frontend
npm install
npm run build

# 4. Reiniciar servicios
sudo systemctl restart mediaflow-backend
sudo systemctl restart nginx
```

### Post-despliegue

1. Verificar que Settings > AI Clients funciona
2. Verificar que Campaigns muestra cliente activo
3. Crear/editar una instrucción desde Campaigns
4. Verificar que aparece en Settings
5. Generar un audio y verificar contexto

---

## Rollback (si es necesario)

```bash
# 1. Revertir código
git revert HEAD

# 2. En backend/app/api/v1/endpoints/ai.py:
#    Descomentar código que lee de Category.ai_instructions
#    Comentar código que lee de AIClient.custom_prompts

# 3. Rebuild y restart
cd frontend && npm run build
sudo systemctl restart mediaflow-backend
```

---

**Documento completado**: Sistema de Perfiles de Cliente
**Fecha**: 2025-01-09
