-- Migración multi-tenant (001)
-- Ejecutar UNA vez contra la BD Supabase del runner (SQL editor o psql).
--
-- Añade `external_id` a la tabla `usuarios` para poder resolver (get-or-create)
-- el usuario del runner a partir del uid de Firebase que envía el orquestador.
--
-- Requisitos: la tabla `usuarios` ya debe existir (referenciada por la FK
-- objetivos.usuario_id). Si tu tabla `usuarios` tiene columnas NOT NULL sin
-- valor por defecto (p. ej. email), el get-or-create fallará al insertar solo
-- external_id: en ese caso, hazlas nullable o dales default antes de usar el
-- endpoint POST /usuarios/.

ALTER TABLE usuarios
    ADD COLUMN IF NOT EXISTS external_id text;

CREATE UNIQUE INDEX IF NOT EXISTS ux_usuarios_external_id
    ON usuarios (external_id);

-- Realinea la secuencia IDENTITY de usuarios.id con el MAX(id) real. Si en la
-- tabla hay filas insertadas con id explícito (p. ej. un seed con id=1) sin
-- avanzar la secuencia, el primer INSERT autogenerado choca con
-- "duplicate key value violates unique constraint usuarios_pkey". Esta línea lo
-- corrige (idempotente: se puede correr las veces que haga falta). No modifica
-- ninguna fila existente, solo el contador de la secuencia.
SELECT setval(
    pg_get_serial_sequence('usuarios', 'id'),
    (SELECT COALESCE(MAX(id), 1) FROM usuarios)
);
