# 🗃️ Guía de Importación a Bases de Datos

Una vez generado el archivo SQL, puedes importarlo a diferentes bases de datos. Aquí tienes las instrucciones para los sistemas más comunes:

## 📊 MySQL

### Opción 1: Línea de comandos

```bash
# Conectar a MySQL
mysql -u tu_usuario -p

# Crear base de datos (opcional)
CREATE DATABASE mi_base_datos;
USE mi_base_datos;

# Importar el archivo SQL
source /ruta/al/archivo.sql;
```

### Opción 2: Importación directa

```bash
mysql -u tu_usuario -p mi_base_datos < archivo.sql
```

### Opción 3: Con archivo específico

```bash
mysql -u usuario -p -h localhost -D base_datos < United-States-Washington-1_121_721_insert_statements.sql
```

## 🐘 PostgreSQL

### Opción 1: psql

```bash
# Conectar a PostgreSQL
psql -U tu_usuario -d tu_base_datos

# Importar archivo
\i /ruta/al/archivo.sql
```

### Opción 2: Importación directa

```bash
psql -U tu_usuario -d tu_base_datos -f archivo.sql
```

### Opción 3: Con host específico

```bash
psql -h localhost -U usuario -d base_datos -f United-States-Washington-1_121_721_insert_statements.sql
```

## 🪶 SQLite

### Opción 1: Línea de comandos

```bash
# Crear/abrir base de datos SQLite
sqlite3 mi_base_datos.db

# Importar archivo SQL
.read archivo.sql
```

### Opción 2: Directa

```bash
sqlite3 mi_base_datos.db < archivo.sql
```

### Opción 3: Crear nueva base desde archivo

```bash
sqlite3 washington_data.db < United-States-Washington-1_121_721_insert_statements.sql
```

## 🔧 SQL Server (T-SQL)

### Opción 1: sqlcmd

```bash
sqlcmd -S servidor -d base_datos -i archivo.sql
```

### Opción 2: Con autenticación

```bash
sqlcmd -S localhost -U usuario -P contraseña -d mi_base -i archivo.sql
```

## ☁️ Servicios en la Nube

### 🔴 AWS RDS (MySQL/PostgreSQL)

```bash
# MySQL en RDS
mysql -h tu-instancia.xxxxx.us-east-1.rds.amazonaws.com -u admin -p base_datos < archivo.sql

# PostgreSQL en RDS
psql -h tu-instancia.xxxxx.us-east-1.rds.amazonaws.com -U admin -d base_datos -f archivo.sql
```

### 🔵 Azure Database

```bash
# Azure MySQL
mysql -h servidor.mysql.database.azure.com -u usuario@servidor -p base_datos < archivo.sql

# Azure PostgreSQL
psql -h servidor.postgres.database.azure.com -U usuario@servidor -d base_datos -f archivo.sql
```

### 🟡 Google Cloud SQL

```bash
# Usando Cloud SQL Proxy
mysql -h 127.0.0.1 -u root -p base_datos < archivo.sql

# Directamente (si está configurado)
mysql -h IP_PUBLICA -u usuario -p base_datos < archivo.sql
```

## 🛠️ Herramientas Gráficas

### phpMyAdmin (MySQL)

1. Abrir phpMyAdmin
2. Seleccionar base de datos
3. Ir a "Importar"
4. Seleccionar archivo SQL
5. Hacer clic en "Continuar"

### pgAdmin (PostgreSQL)

1. Conectar a servidor
2. Click derecho en base de datos → "Query Tool"
3. Abrir archivo SQL
4. Ejecutar

### DBeaver (Universal)

1. Conectar a base de datos
2. Abrir SQL Editor
3. Cargar archivo SQL
4. Ejecutar script

## ⚡ Tips de Rendimiento

### Para archivos grandes:

```sql
-- Deshabilitar autocommit
SET autocommit = 0;

-- Para MySQL: Deshabilitar checks temporalmente
SET foreign_key_checks = 0;
SET unique_checks = 0;

-- Importar archivo
SOURCE archivo.sql;

-- Reactivar checks
SET foreign_key_checks = 1;
SET unique_checks = 1;
SET autocommit = 1;
```

### Para PostgreSQL grandes:

```bash
# Usar COPY en lugar de INSERT (más rápido)
# Pero requiere formato CSV, no SQL
```

## 🔍 Verificación Post-Importación

### Verificar importación:

```sql
-- Contar registros
SELECT COUNT(*) FROM nombre_tabla;

-- Ver estructura
DESCRIBE nombre_tabla;  -- MySQL
\d nombre_tabla;        -- PostgreSQL

-- Ver primeros registros
SELECT * FROM nombre_tabla LIMIT 10;
```

### Verificar datos específicos:

```sql
-- Verificar valores únicos en columnas importantes
SELECT DISTINCT gender FROM washington_data;
SELECT DISTINCT industry FROM washington_data;

-- Verificar rangos de datos numéricos
SELECT MIN(pnum_), MAX(pnum_) FROM washington_data;
```

## 🚨 Solución de Problemas Comunes

### Error de sintaxis:

- Verificar que la base de datos soporte el tipo de SQL generado
- Algunos tipos de datos pueden necesitar ajustes

### Error de memoria:

```sql
-- Para MySQL, aumentar buffer
SET global innodb_buffer_pool_size = 1073741824; -- 1GB
```

### Timeout:

```sql
-- Aumentar timeout
SET global net_read_timeout = 120;
SET global net_write_timeout = 120;
```

### Caracteres especiales:

```sql
-- Asegurar UTF-8
SET NAMES utf8mb4; -- MySQL
```

## 📋 Lista de Verificación

- [ ] Base de datos creada
- [ ] Usuario con permisos suficientes
- [ ] Archivo SQL accesible
- [ ] Conexión a base de datos establecida
- [ ] Espacio suficiente en disco
- [ ] Timeouts configurados adecuadamente
- [ ] Backup de datos existentes (si aplica)

## 🎯 Próximos Pasos

Una vez importados los datos, puedes:

1. **Crear índices** para mejorar rendimiento:

```sql
CREATE INDEX idx_location ON washington_data(location_locality_);
CREATE INDEX idx_industry ON washington_data(industry_);
CREATE INDEX idx_gender ON washington_data(gender_);
```

2. **Agregar constraints**:

```sql
ALTER TABLE washington_data ADD CONSTRAINT pk_washington PRIMARY KEY (pnum_);
```

3. **Optimizar tipos de datos** según necesidades específicas

4. **Crear vistas** para consultas frecuentes:

```sql
CREATE VIEW vista_profesionales AS
SELECT full_name_, industry_, location_locality_
FROM washington_data
WHERE industry_ IS NOT NULL;
```
