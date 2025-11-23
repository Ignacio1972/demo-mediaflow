# 🚀 MediaFlowDemo v2.1 - Roadmap de Desarrollo (ACTUALIZADO)

**Duración Total**: 6 semanas (42 días)
**Fecha Inicio**: 2025-11-25
**Fecha Objetivo**: 2026-01-06
**Stack**: FastAPI + Vue 3 + TypeScript + Tailwind CSS

> **CAMBIOS v2.1:**
> - Ajustado para custom voice settings
> - Categorías configurables añadidas
> - Library con favoritos y vista dual
> - Dashboard simplificado
> - Playground con control granular

---

## 📊 Resumen Ejecutivo v2.1

### Objetivos Principales Actualizados
1. ✅ Dashboard simplificado sin categorías
2. ✅ Voice settings individuales por voz
3. ✅ Categorías totalmente configurables
4. ✅ Library con favoritos y vista dual
5. ✅ Control granular de volúmenes desde Playground
6. ✅ Mensajes recientes siempre visibles en Dashboard

### Nuevas Métricas de Éxito
- **Configuración por voz**: 100% automática
- **Flexibilidad categorías**: Totalmente personalizable
- **Vistas Library**: Grid + Lista
- **Favoritos**: Cross-category
- **Settings aplicados**: 0 intervención usuario

---

## 🎯 SEMANA 1: Foundation & Setup (ACTUALIZADA)
**Fecha**: Nov 25-29, 2025
**Objetivo**: Estructura base + Dashboard simplificado + Voice settings

### Lunes - Setup Inicial + Models (Día 1)
- [ ] Crear estructura de directorios completa
- [ ] Setup FastAPI con estructura modular
- [ ] Configurar SQLAlchemy + Alembic
- [ ] **NUEVO**: Crear modelo `VoiceSettings` con campos individuales
- [ ] **NUEVO**: Crear modelo `CategoryConfig` para categorías dinámicas
- [ ] **NUEVO**: Crear modelo `AudioMessage` con `is_favorite`
- [ ] Docker Compose para desarrollo local

**Entregable**: Proyecto corriendo con modelos actualizados

### Martes - Backend Core + Voice Manager (Día 2)
- [ ] Implementar modelos SQLAlchemy actualizados
- [ ] **NUEVO**: Crear `VoiceManager` service
- [ ] **NUEVO**: Implementar carga de voice settings individuales
- [ ] **NUEVO**: Crear `CategoryManager` service
- [ ] Crear servicios base (TTSService, AudioProcessor)
- [ ] Setup logging estructurado

**Entregable**: Voice settings funcionando en backend

### Miércoles - Integración ElevenLabs + Settings (Día 3)
- [ ] Implementar cliente ElevenLabs async
- [ ] **NUEVO**: Integrar voice settings automáticos en generación
- [ ] **NUEVO**: Aplicar volume_adjustment por voz
- [ ] Crear endpoint `/api/audio/generate` (sin categoría)
- [ ] Tests unitarios para VoiceManager

**Entregable**: TTS con settings automáticos funcionando

### Jueves - Dashboard Frontend Simplificado (Día 4)
- [ ] Crear layout principal con Vue 3
- [ ] Implementar MessageGenerator (SIN categoría)
- [ ] **NUEVO**: Implementar RecentMessages siempre visible
- [ ] Implementar VoiceSelector con preview de settings
- [ ] **NUEVO**: Voice settings aplicados automáticamente (no editables)
- [ ] Integrar con API de generación

**Entregable**: Dashboard simplificado funcionando

### Viernes - Claude AI + Recent Messages (Día 5)
- [ ] Implementar cliente Anthropic async
- [ ] Crear endpoint `/api/ai/suggest`
- [ ] **NUEVO**: Endpoint `/api/audio/recent` para mensajes recientes
- [ ] Implementar AISuggestions component
- [ ] **NUEVO**: RecentMessages component con quick actions
- [ ] Tests de integración

**Entregable**: Dashboard completo con IA y recientes

### 📈 Métricas Semana 1 Actualizada
- **Voice Settings**: ✅ Implementado
- **Dashboard simplificado**: ✅ Sin categorías
- **Recent Messages**: ✅ Integrado
- **Coverage testing**: 35%

---

## 🎯 SEMANA 2: Player Integration & Audio Processing
**Fecha**: Dic 2-6, 2025
**Objetivo**: WebSocket + Procesamiento con settings por voz

### Lunes - WebSocket Server (Día 6)
- [ ] Implementar WebSocket server en FastAPI
- [ ] Crear protocolo de comunicación bidireccional
- [ ] Implementar heartbeat y reconexión automática
- [ ] Crear PlayerService con cola de mensajes
- [ ] **NUEVO**: Incluir voice settings en metadata de audio

**Entregable**: WebSocket con metadata completo

### Martes - Player Endpoints (Día 7)
- [ ] Endpoint `/api/player/pending`
- [ ] Endpoint `/api/player/delivered`
- [ ] **NUEVO**: Incluir volume_adjustment en response
- [ ] Sistema de prioridades (1-5)
- [ ] Tests con player existente

**Entregable**: Player recibiendo settings correctos

### Miércoles - Audio Processing + Voice Settings (Día 8)
- [ ] Portar AudioProcessor con pydub
- [ ] **NUEVO**: Aplicar volume_adjustment por voz automáticamente
- [ ] Implementar normalización LUFS configurable
- [ ] **NUEVO**: Diferentes LUFS target por categoría (futuro)
- [ ] Tests unitarios de procesamiento

**Entregable**: Audio procesado con settings individuales

### Jueves - Jingle Generation + Custom Settings (Día 9)
- [ ] Mezcla TTS + música con FFmpeg
- [ ] **NUEVO**: Aplicar jingle_settings por voz
- [ ] **NUEVO**: Volúmenes específicos por voz
- [ ] JingleControls component (solo display, no edit)
- [ ] Preview en dashboard

**Entregable**: Jingles con settings por voz

### Viernes - Testing Voice Settings (Día 10)
- [ ] Tests E2E de voice settings
- [ ] Verificar aplicación automática
- [ ] Test de volume adjustments
- [ ] Optimización de performance
- [ ] Deploy a staging

**Entregable**: Sistema con voice settings completo

### 📈 Métricas Semana 2 Actualizada
- **Voice settings aplicados**: 100%
- **Volume adjustments**: ✅ Funcionando
- **Jingle settings por voz**: ✅ Implementado
- **Coverage testing**: 50%

---

## 🎯 SEMANA 3: Library Module (MEJORADA)
**Fecha**: Dic 9-13, 2025
**Objetivo**: Biblioteca con favoritos, categorías, vista dual

### Lunes - Backend CRUD + Favoritos (Día 11)
- [ ] Endpoints CRUD para biblioteca
- [ ] **NUEVO**: Campo `is_favorite` en modelo
- [ ] **NUEVO**: Endpoint `/api/library?filter=favorites`
- [ ] **NUEVO**: PATCH `/api/library/{id}/category` (categorizar)
- [ ] **NUEVO**: PATCH `/api/library/{id}/favorite` (toggle estrella)
- [ ] Soft delete implementation

**Entregable**: API biblioteca con favoritos

### Martes - Library Frontend + Vista Dual (Día 12)
- [ ] **NUEVO**: ViewToggle component (Grid/List)
- [ ] **NUEVO**: LibraryGrid component mejorado
- [ ] **NUEVO**: LibraryList component (tabla)
- [ ] SearchBar expandible
- [ ] FilterPanel con "⭐ Favoritos"

**Entregable**: Vista dual funcionando

### Miércoles - Category Management (Día 13)
- [ ] **NUEVO**: CategoryBadge component
- [ ] **NUEVO**: CategoryDropdown para cambio rápido
- [ ] **NUEVO**: Asignación de categoría post-generación
- [ ] **NUEVO**: Bulk category change
- [ ] Integración con backend

**Entregable**: Categorización flexible funcionando

### Jueves - Edit in Dashboard + Favorites (Día 14)
- [ ] **NUEVO**: "Editar en Dashboard" action
- [ ] **NUEVO**: Copiar texto a Dashboard sin modificar original
- [ ] **NUEVO**: FavoriteButton component
- [ ] **NUEVO**: Favoritos cross-category filter
- [ ] Tests de flujo completo

**Entregable**: Edit copy y favoritos funcionando

### Viernes - File Upload + Actions (Día 15)
- [ ] Endpoint `/api/library/upload`
- [ ] UploadModal con drag & drop
- [ ] **NUEVO**: Asignar categoría al upload
- [ ] Progress tracking
- [ ] Tests de integración

**Entregable**: Library module completo v2.1

### 📈 Métricas Semana 3 Actualizada
- **Favoritos**: ✅ Implementado
- **Vista dual**: ✅ Grid + List
- **Edit in Dashboard**: ✅ Funcionando
- **Categorización post**: ✅ Natural flow

---

## 🎯 SEMANA 4: Calendar & Scheduling
**Fecha**: Dic 16-20, 2025
**Objetivo**: Programación con categorías dinámicas

### Lunes - Schedule Backend + Categories (Día 16)
- [ ] Modelos Schedule y ScheduleLog
- [ ] **NUEVO**: Integración con categorías dinámicas
- [ ] CRUD endpoints para schedules
- [ ] **NUEVO**: Validación de categorías activas
- [ ] Sistema de prioridades

**Entregable**: API scheduling con categorías flexibles

### Martes - Calendar View + Custom Categories (Día 17)
- [ ] CalendarView component
- [ ] **NUEVO**: Colores dinámicos por categoría personalizada
- [ ] **NUEVO**: Iconos/emojis de categorías en calendario
- [ ] Eventos con metadata completo
- [ ] Drag & drop

**Entregable**: Calendario con categorías personalizadas

### Miércoles - Schedule Configuration (Día 18)
- [ ] ScheduleModal para configuración
- [ ] **NUEVO**: Selector de categorías dinámicas
- [ ] Tipos: interval, specific, once
- [ ] Rango de fechas
- [ ] Preview de ejecuciones

**Entregable**: Scheduling con categorías flexibles

### Jueves - Cron Service (Día 19)
- [ ] Implementar scheduler-cron
- [ ] **NUEVO**: Aplicar voice settings en ejecución automática
- [ ] Logging de ejecuciones
- [ ] Manejo de errores
- [ ] Notificaciones

**Entregable**: Cron con settings automáticos

### Viernes - Testing & Polish (Día 20)
- [ ] Tests de categorías dinámicas
- [ ] Tests de voice settings en schedules
- [ ] UI/UX refinements
- [ ] Documentación
- [ ] Deploy a staging

**Entregable**: Calendar module v2.1 completo

### 📈 Métricas Semana 4 Actualizada
- **Categorías dinámicas**: ✅ En calendario
- **Voice settings en cron**: ✅ Automático
- **Coverage testing**: 65%

---

## 🎯 SEMANA 5: Settings/Playground (CRÍTICA)
**Fecha**: Dic 23-27, 2025
**Objetivo**: Control total desde Playground

### Lunes - Settings Structure (Día 21)
- [ ] Crear estructura /settings en Vue Router
- [ ] Layout con sidebar de navegación
- [ ] **NUEVO**: Tabs para Voice/Category/Volume/AI
- [ ] State management con Pinia
- [ ] Sistema de permisos

**Entregable**: Estructura settings completa

### Martes - Voice Manager UI (Día 22) ⭐ CRÍTICO
- [ ] **NUEVO**: VoiceManager component completo
- [ ] **NUEVO**: Settings individuales por voz (style, stability, similarity)
- [ ] **NUEVO**: Volume adjustment slider (-20 to +20 dB)
- [ ] **NUEVO**: Jingle settings por voz
- [ ] **NUEVO**: Test button con preview
- [ ] **NUEVO**: Orden drag & drop

**Endpoints necesarios**:
```
GET    /api/settings/voices
PATCH  /api/settings/voices/{id}
POST   /api/settings/voices/test/{id}
PUT    /api/settings/voices/reorder
```

**Entregable**: Voice settings granular completo

### Miércoles - Category Editor (Día 23) ⭐ NUEVO
- [ ] **NUEVO**: CategoryEditor component
- [ ] **NUEVO**: Editar nombre, color, icono
- [ ] **NUEVO**: Agregar/eliminar categorías
- [ ] **NUEVO**: Reordenar categorías
- [ ] **NUEVO**: Preview en tiempo real
- [ ] **NUEVO**: Activar/desactivar categorías

**Endpoints necesarios**:
```
GET    /api/settings/categories
POST   /api/settings/categories
PATCH  /api/settings/categories/{id}
DELETE /api/settings/categories/{id}
PUT    /api/settings/categories/reorder
```

**Entregable**: Categorías totalmente configurables

### Jueves - Volume Control Panel (Día 24) ⭐ MEJORADO
- [ ] **NUEVO**: VolumeControls component mejorado
- [ ] **NUEVO**: Global TTS settings (LUFS, output volume)
- [ ] **NUEVO**: Global Jingle settings
- [ ] **NUEVO**: Per-voice overrides UI
- [ ] **NUEVO**: Test con diferentes configuraciones
- [ ] **NUEVO**: Presets guardables

**Endpoints necesarios**:
```
GET    /api/settings/audio/global
PATCH  /api/settings/audio/global
POST   /api/settings/audio/presets
GET    /api/settings/audio/presets
```

**Entregable**: Control granular de volúmenes

### Viernes - AI Configuration + Integration (Día 25)
- [ ] AI Configuration para multi-cliente
- [ ] **NUEVO**: Automatic Mode con speech-to-text
- [ ] **NUEVO**: Voice settings aplicados en automatic mode
- [ ] Testing de configuraciones
- [ ] Validación de guardado

**Entregable**: Settings completo y funcional

### 📈 Métricas Semana 5 Actualizada
- **Voice settings UI**: ✅ Completo
- **Category editor**: ✅ Funcional
- **Volume controls**: ✅ Granular
- **Aplicación automática**: 100%

---

## 🎯 SEMANA 6: Testing, Migration & Deployment
**Fecha**: Dic 30 - Ene 3, 2026
**Objetivo**: Production ready con todas las configuraciones

### Lunes - E2E Testing Settings (Día 26)
- [ ] **NUEVO**: Tests de voice settings automáticos
- [ ] **NUEVO**: Tests de categorías dinámicas
- [ ] **NUEVO**: Tests de favoritos
- [ ] **NUEVO**: Tests de edit in dashboard
- [ ] Tests de flujos completos
- [ ] Performance testing

**Entregable**: 75%+ test coverage

### Martes - Data Migration + Configs (Día 27)
- [ ] Script migración SQLite → PostgreSQL
- [ ] **NUEVO**: Migración de voice_settings
- [ ] **NUEVO**: Migración de category_configs
- [ ] **NUEVO**: Migración de favoritos
- [ ] Migración de audio_metadata
- [ ] Validación de integridad

**Entregable**: Datos y configuraciones migrados

### Miércoles - Production Setup (Día 28)
- [ ] Docker production con configs
- [ ] **NUEVO**: Volúmenes para voice configs persistentes
- [ ] **NUEVO**: Backup de configuraciones críticas
- [ ] Setup nginx + SSL
- [ ] Redis para caché

**Entregable**: Infraestructura lista con configs

### Jueves - Documentation v2.1 (Día 29)
- [ ] **NUEVO**: Guía de configuración de voces
- [ ] **NUEVO**: Guía de categorías personalizables
- [ ] **NUEVO**: Guía de favoritos y vistas
- [ ] API documentation actualizada
- [ ] User guide actualizado
- [ ] Video tutoriales de Playground

**Entregable**: Documentación completa v2.1

### Viernes - Launch & Monitoring (Día 30)
- [ ] Deploy a producción
- [ ] **NUEVO**: Verificar voice settings en producción
- [ ] **NUEVO**: Verificar categorías dinámicas
- [ ] Smoke tests completos
- [ ] Monitoring de aplicación de settings
- [ ] Handover al equipo

**Entregable**: 🎉 MediaFlowDemo v2.1 en producción

### 📈 Métricas Semana 6 Actualizada
- **Voice settings migrados**: 100%
- **Categorías configurables**: ✅
- **Test coverage**: 75%+
- **Production ready**: ✅

---

## 📊 Resumen de Nuevas Tareas v2.1

### Tareas Agregadas (20 nuevas)

**Backend (8)**:
- VoiceSettings model y service
- CategoryConfig model y service
- Volume adjustment automático
- Favoritos en AudioMessage
- Edit copy endpoint
- Category assignment post-generation
- Voice test endpoint
- Settings persistence

**Frontend (8)**:
- RecentMessages en Dashboard
- ViewToggle (Grid/List)
- FavoriteButton component
- EditInDashboard action
- VoiceManager UI completo
- CategoryEditor UI
- VolumeControls mejorado
- Voice preview con settings

**Configuración (4)**:
- Migración de voice configs
- Migración de categories
- Backup de settings
- Documentación de Playground

### Tareas Modificadas

**Dashboard**:
- ❌ Removido: CategorySelector
- ✅ Simplificado: Sin voice settings manuales
- ✅ Agregado: Recent messages permanente

**Library**:
- ✅ Mejorado: Vista dual
- ✅ Agregado: Favoritos
- ✅ Agregado: Edit copy
- ✅ Agregado: Category post-assignment

**Settings**:
- ✅ Crítico: Voice settings individuales
- ✅ Nuevo: Category editor
- ✅ Mejorado: Volume controls granular

---

## ⚠️ Riesgos Adicionales v2.1 y Mitigación

### 1. Complejidad de Voice Settings
**Riesgo**: Configuración incorrecta afecta todas las generaciones
**Mitigación**:
- Valores por defecto seguros
- Preview antes de guardar
- Rollback de configuraciones

### 2. Migración de Configuraciones
**Riesgo**: Pérdida de settings personalizados
**Mitigación**:
- Backup antes de migración
- Validación post-migración
- Scripts de rollback

### 3. Performance con Settings Dinámicos
**Riesgo**: Carga de configs en cada request
**Mitigación**:
- Cache en memoria
- Lazy loading
- Invalidación selectiva

---

## 📈 Métricas de Progreso v2.1

```
Semana 1: ████░░░░░░ 17% - Foundation + Voice Settings
Semana 2: ██████████ 33% - Player + Audio con Settings
Semana 3: ███████████████ 50% - Library Mejorada
Semana 4: ████████████████████ 67% - Calendar
Semana 5: █████████████████████████ 83% - Settings CRÍTICO
Semana 6: ██████████████████████████████ 100% - Production
```

---

## 🚀 Criterios de Éxito v2.1

### Funcionales
- ✅ Voice settings automáticos funcionando
- ✅ Categorías totalmente configurables
- ✅ Favoritos cross-category
- ✅ Vista dual en Library
- ✅ Edit in Dashboard sin modificar original
- ✅ Recent messages siempre visible

### Técnicos
- ✅ 0 configuración manual en Dashboard
- ✅ Settings persistentes
- ✅ Volume adjustments aplicados
- ✅ 75%+ test coverage
- ✅ <200ms response time

### UX
- ✅ Dashboard más simple
- ✅ Library más poderosa
- ✅ Playground profesional
- ✅ Flujo natural de trabajo

---

## 🎯 Dependencias Críticas v2.1

### Semana 1 → Todas
**Voice Settings** es la base de todo el sistema
- Debe estar listo antes que cualquier generación
- Afecta Dashboard, Library, Calendar, Player

### Semana 3 → 4
**Categorías dinámicas** deben estar antes del Calendar
- Library define categorías
- Calendar las usa

### Semana 5
**Settings UI** es crítico para configuración
- Sin esto, no hay personalización
- Debe estar perfecto antes de producción

---

## 📝 Notas Finales v2.1

Los cambios de arquitectura **mejoran significativamente** la experiencia:

1. **Dashboard simple** = Generación rápida
2. **Library poderosa** = Organización flexible
3. **Settings automáticos** = Cero fricción
4. **Playground profesional** = Control total

La clave está en que **todo se configura una vez** y luego funciona automáticamente.

**Tiempo adicional**: Los cambios NO agregan tiempo al desarrollo, solo reorganizan tareas para un mejor flujo.

---

**Documento actualizado**: 2025-11-22
**Versión**: 2.1
**Estado**: ✅ Listo para ejecución con mejoras implementadas