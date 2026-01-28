-- MediaFlow v2.1 - Datos Iniciales
-- Ejecutar: sudo -u postgres psql mediaflow < 04-load-initial-data.sql

-- =============================================
-- MUSIC TRACKS
-- =============================================
-- Nota: Solo insertar si la tabla esta vacia
-- Si ya hay datos, comentar esta seccion

INSERT INTO music_tracks (filename, display_name, file_path, file_size, duration, bitrate, is_default, active, "order", genre, mood, created_at, updated_at)
SELECT * FROM (VALUES
    ('Cool.mp3', 'Cool', '/var/www/mediaflow/storage/music/Cool.mp3', 11106725, 273.45, '324kbps', false, true, 0, 'Electronic', 'energetic', NOW(), NOW()),
    ('Kids.mp3', 'Kids', '/var/www/mediaflow/storage/music/Kids.mp3', 9324163, 227.97, '327kbps', false, true, 1, 'Pop', 'happy', NOW(), NOW()),
    ('Pop.mp3', 'Pop', '/var/www/mediaflow/storage/music/Pop.mp3', 9219710, 225.63, '326kbps', false, true, 2, 'Pop', 'upbeat', NOW(), NOW()),
    ('Slow.mp3', 'Slow', '/var/www/mediaflow/storage/music/Slow.mp3', 8508264, 208.87, '325kbps', false, true, 3, 'Ambient', 'calm', NOW(), NOW()),
    ('Smooth.mp3', 'Smooth', '/var/www/mediaflow/storage/music/Smooth.mp3', 6438454, 154.28, '333kbps', false, true, 4, 'Jazz', 'relaxed', NOW(), NOW()),
    ('Uplift.mp3', 'Uplift', '/var/www/mediaflow/storage/music/Uplift.mp3', 10020659, 248.41, '322kbps', true, true, 5, 'Electronic', 'inspiring', NOW(), NOW()),
    ('_Independencia.mp3', 'Independencia', '/var/www/mediaflow/storage/music/_Independencia.mp3', 2464462, 19.72, '999kbps', false, true, 6, 'Latin', 'festive', NOW(), NOW())
) AS v(filename, display_name, file_path, file_size, duration, bitrate, is_default, active, "order", genre, mood, created_at, updated_at)
WHERE NOT EXISTS (SELECT 1 FROM music_tracks LIMIT 1);

-- =============================================
-- VOICE SETTINGS (Voces de ElevenLabs)
-- =============================================
-- Estas son las voces predeterminadas
-- Modificar elevenlabs_id segun las voces de tu cuenta

INSERT INTO voice_settings (id, name, elevenlabs_id, active, is_default, "order", style, stability, similarity_boost, speed, use_speaker_boost, volume_adjustment, created_at, updated_at)
SELECT * FROM (VALUES
    ('juan_carlos', 'Juan Carlos', 'G4IAP30yc6c1gK0csDfu', true, true, 1, 0.0, 50.0, 75.0, 1.0, true, 0.0, NOW(), NOW()),
    ('veronica', 'Veronica', 'FaGOXcXMgPbJBfF7wPF1', true, false, 2, 0.0, 50.0, 75.0, 1.0, true, 0.0, NOW(), NOW()),
    ('catalina', 'Catalina', 'a9f83d9f9c884a89b3d9c1e5f6b2a8d7', true, false, 3, 0.0, 50.0, 75.0, 1.0, true, 0.0, NOW(), NOW())
) AS v(id, name, elevenlabs_id, active, is_default, "order", style, stability, similarity_boost, speed, use_speaker_boost, volume_adjustment, created_at, updated_at)
WHERE NOT EXISTS (SELECT 1 FROM voice_settings LIMIT 1);

-- =============================================
-- CATEGORIES (Categorias de audio)
-- =============================================

INSERT INTO categories (id, name, icon, color, "order", active, created_at, updated_at)
SELECT * FROM (VALUES
    ('general', 'General', 'speaker-wave', '#6366F1', 0, true, NOW(), NOW()),
    ('anuncios', 'Anuncios', 'megaphone', '#EC4899', 1, true, NOW(), NOW()),
    ('promociones', 'Promociones', 'tag', '#F59E0B', 2, true, NOW(), NOW()),
    ('eventos', 'Eventos', 'calendar', '#10B981', 3, true, NOW(), NOW()),
    ('seguridad', 'Seguridad', 'shield-check', '#EF4444', 4, true, NOW(), NOW())
) AS v(id, name, icon, color, "order", active, created_at, updated_at)
WHERE NOT EXISTS (SELECT 1 FROM categories LIMIT 1);

-- =============================================
-- MESSAGE TEMPLATES (Templates de operaciones)
-- =============================================
-- Templates para vehiculos mal estacionados, horarios de cierre y llamado a empleados

INSERT INTO message_templates (id, name, description, template_text, variables, module, "order", active, is_default, use_announcement_sound, created_at, updated_at)
SELECT * FROM (VALUES
    -- Vehiculos mal estacionados
    ('vehiculos_estandar',
     'Vehiculos - Estandar',
     'Solicita acercarse a informaciones',
     'Atención clientes: Se solicita al dueño del vehiculo marca {marca} color {color}. Patente {patente} porfavor acérquese al mesón de servicio al cliente. Repito, {marca} color {color}, Patente {patente}, por favor acérquese a informaciones ubicada en el mesón central.',
     '["marca", "color", "patente"]'::json,
     'vehicles', 0, true, true, true, NOW(), NOW()),

    -- Horarios de cierre
    ('schedules_cierre_normal',
     'Cierre - Normal',
     'Mensaje estándar de cierre próximo',
     'Estimados clientes, les informamos que el establecimiento cerrará pronto. Por favor diríjanse a las cajas para realizar sus compras.',
     '[]'::json,
     'schedules', 2, true, false, false, NOW(), NOW()),

    ('schedules_cierre_minutos',
     'Cierre - En X minutos',
     'Aviso de cierre con tiempo específico. Usa {minutes} para los minutos.',
     'Estimados clientes, les recordamos que el establecimiento cerrará en {minutes} minutos. Les agradecemos su visita. Los esperamos mañana. Muchas gracias.',
     '["minutes"]'::json,
     'schedules', 3, true, true, true, NOW(), NOW()),

    ('schedules_cierre_inmediato',
     'Cierre - Inmediato',
     'Anuncio de que el local ya cerró',
     'Estimados clientes, el establecimiento ha cerrado. Gracias por su visita, los esperamos pronto.',
     '[]'::json,
     'schedules', 4, true, false, false, NOW(), NOW()),

    -- Llamado a empleados
    ('employee_call_default',
     'Llamado estándar',
     'Llamado formal con repetición',
     'Atención: Se solicita la presencia de {nombre} en {ubicacion}. {nombre}, por favor acérquese a {ubicacion}. Gracias.',
     '["nombre", "ubicacion"]'::json,
     'employee_call', 0, true, true, true, NOW(), NOW()),

    ('employee_call_cliente',
     'Llamado a cliente',
     'Mensaje amable para clientes',
     'Estimado cliente {nombre}, por favor diríjase a {ubicacion} donde le están esperando. Gracias.',
     '["nombre", "ubicacion"]'::json,
     'employee_call', 1, true, false, true, NOW(), NOW()),

    ('employee_call_corto',
     'Llamado corto',
     'Mensaje breve y directo',
     '{nombre} a {ubicacion}, por favor.',
     '["nombre", "ubicacion"]'::json,
     'employee_call', 2, true, false, false, NOW(), NOW())
) AS v(id, name, description, template_text, variables, module, "order", active, is_default, use_announcement_sound, created_at, updated_at)
WHERE NOT EXISTS (SELECT 1 FROM message_templates LIMIT 1);

-- =============================================
-- Verificacion
-- =============================================
SELECT 'Music tracks:' as tabla, COUNT(*) as registros FROM music_tracks
UNION ALL
SELECT 'Voice settings:', COUNT(*) FROM voice_settings
UNION ALL
SELECT 'Categories:', COUNT(*) FROM categories
UNION ALL
SELECT 'Templates:', COUNT(*) FROM message_templates;
