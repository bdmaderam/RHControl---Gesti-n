CREATE TABLE IF NOT EXISTS empleados (
    id SERIAL PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    tipo_documento VARCHAR(2) NOT NULL DEFAULT 'CC' CHECK (tipo_documento IN ('CC','CE','PA')),
    numero_documento VARCHAR(30) NOT NULL UNIQUE,
    fecha_nacimiento DATE,
    cargo VARCHAR(120) NOT NULL DEFAULT '',
    salario NUMERIC(14,2) NOT NULL DEFAULT 0 CHECK (salario >= 0),
    dependencia VARCHAR(120) NOT NULL DEFAULT '',
    tiene_cuenta_bancaria BOOLEAN NOT NULL DEFAULT FALSE,
    es_temporal BOOLEAN NOT NULL DEFAULT FALSE,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS anotaciones (
    id SERIAL PRIMARY KEY,
    empleado_id INTEGER NOT NULL REFERENCES empleados(id) ON DELETE CASCADE,
    tipo VARCHAR(40) NOT NULL DEFAULT 'Llamado de atención',
    descripcion TEXT NOT NULL,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    creado_en TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_anotaciones_empleado ON anotaciones(empleado_id);
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    nombre VARCHAR(120) NOT NULL
);
