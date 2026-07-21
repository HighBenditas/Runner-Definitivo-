# Dani-ETH — Backend Runner

Backend encargado de registrar, versionar y ejecutar herramientas de ciberseguridad dentro de contenedores Docker aislados.

El Runner recibe solicitudes desde el orquestador, valida la información de usuario, objetivo y sesión, selecciona la versión activa de cada herramienta, ejecuta el análisis en un contenedor efímero y almacena el resultado en PostgreSQL/Supabase.

> PRECAUCIÓN
> Utiliza las herramientas únicamente sobre sistemas propios, laboratorios controlados o activos para los que cuentes con autorización explícita.

## Contenido

* [Características principales](#características-principales)
* [Arquitectura](#arquitectura)
* [Estructura del proyecto](#estructura-del-proyecto)
* [Requisitos](#requisitos)
* [Configuración](#configuración)
* [Despliegue](#despliegue)
* [Servicios y puertos](#servicios-y-puertos)
* [Herramientas integradas](#herramientas-integradas)
* [Multi-tenant y autenticación interna](#multi-tenant-y-autenticación-interna)
* [Registro con Supabase Auth](#registro-con-supabase-auth)
* [Endpoints principales](#endpoints-principales)
* [Pruebas de la API](#pruebas-de-la-api)
* [Integración de una herramienta nueva](#integración-de-una-herramienta-nueva)
* [Operación y mantenimiento](#operación-y-mantenimiento)
* [Seguridad de los objetivos](#seguridad-de-los-objetivos)

## Características principales

* API Gateway desarrollado con FastAPI.
* Registro centralizado de herramientas y versiones.
* Activación de versiones y selección de una versión de respaldo.
* Ejecución aislada mediante contenedores Docker efímeros.
* Persistencia de usuarios, objetivos, sesiones, tareas y resultados.
* Separación lógica de información por usuario o tenant.
* Integración de identidad con Supabase Auth.
* Autenticación interna entre el Runner y el orquestador.
* Redis como servicio auxiliar.
* Registro automático de herramientas mediante un servicio `seeder`.
* Acceso controlado al Docker Engine mediante Docker Socket Proxy.

## Arquitectura

```mermaid
flowchart TD
    O[Orquestador] -->|Solicitud y token interno| G[API Gateway]
    G --> R[Tool Registry]
    G --> E[Tool Executor]
    R --> DB[(PostgreSQL / Supabase)]
    E --> DB
    E --> P[Docker Socket Proxy]
    P --> C[Contenedor efímero de herramienta]
    C -->|Resultado JSON| E
```

### Flujo de ejecución

1. El orquestador envía una solicitud al API Gateway.
2. El Runner relaciona la solicitud con un usuario, un objetivo y una sesión.
3. Tool Registry obtiene la herramienta y su versión activa.
4. Tool Executor inicia un contenedor Docker efímero con la imagen correspondiente.
5. El archivo `run.py` recibe los parámetros en JSON, ejecuta la herramienta y normaliza la salida.
6. El resultado se almacena en la base de datos.
7. El contenedor de la herramienta se elimina al finalizar.

## Estructura del proyecto

```text
backend_runner/
├── api_gateway/              # Punto de entrada de la API
├── tool_registry/            # Registro de herramientas y versiones
├── tool_executor/            # Ejecución de herramientas en Docker
├── tools/                    # Dockerfiles y adaptadores run.py
├── scripts/
│   ├── migrations/           # Migraciones de base de datos
│   └── ...                   # Seeder y scripts auxiliares
├── shared/                   # Modelos y componentes compartidos
├── docker-compose.yml
├── .env.example
└── setup.ps1                 # Instalación limpia en Windows
```

Cada herramienta se mantiene de forma independiente:

```text
tools/
└── nombre_herramienta/
    ├── Dockerfile
    └── run.py
```

## Requisitos

Antes de levantar el Runner, instala o configura:

* Git.
* Docker Desktop con contenedores Linux, o Docker Engine con Docker Compose.
* Acceso a una base de datos PostgreSQL compatible, como Supabase, PostgreSQL local o Neon.
* Un proyecto de Supabase configurado si se utilizará el registro mediante Supabase Auth.

La base de datos PostgreSQL no está incluida en `docker-compose.yml`.

## Configuración

### 1. Crear el archivo de variables de entorno

En PowerShell:

```powershell
cd backend_runner
Copy-Item .env.example .env
```

En Linux o macOS:

```bash
cd backend_runner
cp .env.example .env
```

### 2. Configurar las variables principales

Edita `backend_runner/.env`:

```env
DATABASE_URL=postgresql+asyncpg://USUARIO:CONTRASENA@HOST:5432/NOMBRE_BASE_DATOS
TOOL_REGISTRY_URL=http://tool_registry:8003
INTERNAL_API_TOKEN=CAMBIA_ESTE_TOKEN
```

Completa además las credenciales de Supabase indicadas en `.env.example` cuando utilices `POST /auth/register`.

`INTERNAL_API_TOKEN` debe tener el mismo valor en el Runner y en el orquestador. No subas el archivo `.env` al repositorio.

### 3. Ejecutar la migración multi-tenant

Antes de utilizar el sistema en un entorno real, ejecuta una vez la migración:

```text
scripts/migrations/001_multi_tenant.sql
```

La migración incorpora `usuarios.external_id`, utilizado para asociar la identidad de Supabase Auth con el usuario interno del Runner.

## Despliegue

Desde `backend_runner`:

```powershell
docker compose up --build -d
```

Este comando:

1. Construye los servicios FastAPI.
2. levanta Redis y los componentes auxiliares.
3. Construye las imágenes de las herramientas.
4. Inicia API Gateway, Tool Registry y Tool Executor.
5. Ejecuta el seeder para registrar las herramientas.

Comprueba el estado de los servicios:

```powershell
docker compose ps
```

Comprueba las imágenes disponibles:

```powershell
docker image ls "backend_runner-*"
```

### Instalación limpia en Windows

La carpeta `backend_runner` incluye el script `setup.ps1`:

```powershell
.\setup.ps1
```

El script elimina componentes anteriores administrados por el proyecto y reconstruye el sistema. Úsalo solamente cuando necesites una instalación limpia.

## Servicios y puertos

| Servicio      | Puerto del equipo | Puerto interno | Documentación                |
| ------------- | ----------------- | -------------- | ---------------------------- |
| API Gateway   | `8002`            | `8000`         | `http://localhost:8002/docs` |
| Tool Registry | `8003`            | `8003`         | `http://localhost:8003/docs` |
| Tool Executor | `8004`            | `8004`         | `http://localhost:8004/docs` |
| Redis         | `6379`            | `6379`         | No utiliza Swagger           |

El API Gateway es el punto de entrada recomendado para el orquestador y otros clientes de la API.

## Herramientas integradas

Cada herramienta posee su propia imagen Docker y un adaptador `run.py`.

| Herramienta | Imagen Docker             | Uso principal                                                    |
| ----------- | ------------------------- | ---------------------------------------------------------------- |
| Nmap        | `backend_runner-nmap`     | Escaneo de puertos y detección de servicios                      |
| Nuclei      | `backend_runner-nuclei`   | Detección de vulnerabilidades mediante templates                 |
| SQLMap      | `backend_runner-sqlmap`   | Pruebas autorizadas de inyección SQL                             |
| XSStrike    | `backend_runner-xsstrike` | Pruebas autorizadas de vulnerabilidades XSS                      |
| Gobuster    | `backend_runner-gobuster` | Enumeración de rutas, directorios y subdominios                  |
| Nikto       | `backend_runner-nikto`    | Evaluación de configuraciones y fallos comunes en servidores web |
| Trivy       | `backend_runner-trivy`    | Análisis de vulnerabilidades en imágenes y sistemas de archivos  |
| OSQuery     | `backend_runner-osquery`  | Consulta de información del sistema mediante SQL                 |
| Wapiti      | `backend_runner-wapiti`   | Análisis automatizado de aplicaciones web                        |
| Hydra       | `backend_runner-hydra`    | Auditorías autorizadas de credenciales                           |
| Radare2     | `backend_runner-radare2`  | Análisis e ingeniería inversa de binarios                        |
| cURL        | `backend_runner-curl`     | Solicitudes HTTP y revisión de respuestas                        |
| ls          | `backend_runner-ls`       | Listado controlado de archivos dentro del contenedor             |
| cat         | `backend_runner-cat`      | Lectura controlada de archivos dentro del contenedor             |

El inventario vigente y los parámetros aceptados por cada herramienta se pueden consultar a través de Tool Registry.

## Registro automático de herramientas

El servicio `seeder` registra las herramientas después de que Tool Registry queda disponible.

Para ejecutar nuevamente el seeder:

```powershell
docker compose run --rm seeder
```

Para revisar su salida:

```powershell
docker logs runner-seeder
```

## Multi-tenant y autenticación interna

El Runner implementa aislamiento lógico por cliente. Los recursos se relacionan de la siguiente forma:

```text
Supabase Auth
    └── external_id
        └── usuarios
            └── objetivos
                └── sesiones
                    └── ejecuciones y resultados
```

El orquestador crea o recupera el usuario y posteriormente registra el objetivo y la sesión correspondiente a cada campaña.

Las rutas funcionales requieren la cabecera:

```http
X-Internal-Token: VALOR_DE_INTERNAL_API_TOKEN
```

Los endpoints `GET /` permanecen públicos para los healthchecks. Si `INTERNAL_API_TOKEN` se deja vacío, la validación se desactiva para facilitar el desarrollo local; este modo no debe utilizarse en producción.

Tool Executor permite agregar `usuario_id` al consultar una tarea:

```http
GET /ejecutar/tareas/{tarea_id}?usuario_id={usuario_id}
```

Si la tarea no pertenece al usuario indicado, el servicio responde `404` y evita revelar la existencia de tareas ajenas.

## Registro con Supabase Auth

El endpoint de registro crea la identidad en Supabase Auth y sincroniza un registro interno en `public.usuarios`.

```http
POST /auth/register
```

Ejemplo de solicitud:

```json
{
  "nombre": "Usuario Demo",
  "email": "usuario@email.com",
  "password": "password_segura",
  "rol": "admin"
}
```

Supabase Auth administra el almacenamiento seguro de contraseñas, los tokens JWT, las sesiones y la validación de identidad. El Runner conserva el UUID retornado en `usuarios.external_id` y utiliza `SUPABASE_AUTH` como referencia interna en `password_hash`; no almacena allí la contraseña enviada por el usuario.

La unicidad de `external_id` evita duplicar usuarios:

```sql
CREATE UNIQUE INDEX ux_usuarios_external_id
ON public.usuarios(external_id);
```

El proceso es idempotente: si la identidad ya posee un registro interno, este se reutiliza; en caso contrario, se crea.

## Endpoints principales

Todas las rutas se pueden revisar en la documentación Swagger de cada servicio.

### API Gateway — puerto 8002

URL base: `http://localhost:8002`

#### Salud, autenticación y contexto multi-tenant

```http
GET  /
POST /auth/register
POST /usuarios/
POST /objetivos/
POST /sesiones/
```

`POST /usuarios/` crea o recupera un usuario por `external_id` y devuelve su `usuario_id`.

#### Herramientas

```http
GET  /proxy/herramientas
GET  /proxy/herramientas/para-orquestador
GET  /proxy/herramientas/{nombre}
POST /proxy/herramientas
PUT  /proxy/herramientas/{nombre}
```

#### Versiones

```http
GET  /proxy/herramientas/{nombre}/versiones
GET  /proxy/herramientas/{nombre}/versiones/fallback
POST /proxy/herramientas/{nombre}/versiones
PUT  /proxy/herramientas/{nombre}/versiones/{version}/activar
PUT  /proxy/herramientas/{nombre}/versiones/{version}/marcar-fallida
```

#### Ejecución

```http
POST /proxy/ejecutar
GET  /proxy/tareas/{tarea_id}
```

### Tool Registry — puerto 8003

URL base: `http://localhost:8003`

```http
GET  /
GET  /herramientas/
GET  /herramientas/para-orquestador
GET  /herramientas/{nombre}
POST /herramientas/
PUT  /herramientas/{nombre}

GET  /herramientas/{nombre}/versiones
GET  /herramientas/{nombre}/versiones/fallback
POST /herramientas/{nombre}/versiones
PUT  /herramientas/{nombre}/versiones/{version}/activar
PUT  /herramientas/{nombre}/versiones/{version}/marcar-fallida
```

### Tool Executor — puerto 8004

URL base: `http://localhost:8004`

```http
GET  /
POST /ejecutar/
GET  /ejecutar/tareas/{tarea_id}
```

## Pruebas de la API

Los ejemplos siguientes utilizan PowerShell y envían el token interno. Si la autenticación está desactivada en desarrollo, se puede omitir la cabecera.

### Listar herramientas

```powershell
$headers = @{ "X-Internal-Token" = "VALOR_DE_INTERNAL_API_TOKEN" }

Invoke-RestMethod -Method Get `
  -Uri "http://localhost:8002/proxy/herramientas" `
  -Headers $headers
```

### Ejecutar Nmap en un objetivo autorizado

Utiliza un `sesion_id` existente y asociado al usuario que realiza la solicitud.

```powershell
$headers = @{ "X-Internal-Token" = "VALOR_DE_INTERNAL_API_TOKEN" }

$body = @{
  herramienta = "nmap"
  params = @{
    objetivo = "scanme.nmap.org"
    tipo_escaneo = "-sV"
    velocidad = 3
    puertos = "80,443"
  }
  sesion_id = 61
  orden_ejecucion = 1
} | ConvertTo-Json -Depth 5

$respuesta = Invoke-RestMethod -Method Post `
  -Uri "http://localhost:8002/proxy/ejecutar" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body

$respuesta
```

La respuesta entrega un `tarea_id`.

### Consultar una tarea

```powershell
Invoke-RestMethod -Method Get `
  -Uri "http://localhost:8002/proxy/tareas/ID_TAREA" `
  -Headers $headers
```

Reemplaza `ID_TAREA` por el identificador recibido.

## Integración de una herramienta nueva

### 1. Crear la carpeta

```text
backend_runner/tools/nueva_herramienta/
├── Dockerfile
└── run.py
```

### 2. Crear el Dockerfile

Utiliza una imagen base adecuada y elimina la caché del administrador de paquetes para reducir el tamaño final.

```dockerfile
FROM kalilinux/kali-rolling

RUN apt-get update && \
    apt-get install -y python3 nombre_de_la_herramienta && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY run.py /app/run.py

ENTRYPOINT ["python3", "/app/run.py"]
```

El uso de `ENTRYPOINT` permite que Tool Executor entregue el JSON de configuración como argumento al iniciar el contenedor.

### 3. Crear el adaptador run.py

El adaptador debe leer los parámetros, construir el comando sin utilizar una shell, capturar la salida y devolver un único objeto JSON.

```python
import json
import subprocess
import sys


def main():
    try:
        input_data = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
        params = json.loads(input_data)
        objetivo = params.get("objetivo", "127.0.0.1")

        comando = ["herramienta", "-parametro", objetivo]
        proceso = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            check=False,
        )

        resultado = {
            "objetivo_escaneado": objetivo,
            "total_hallazgos": 0,
            "raw_output": proceso.stdout + proceso.stderr,
        }

        print(json.dumps({
            "error": None,
            "resultado": resultado,
            "codigo_salida": proceso.returncode,
        }))
    except Exception as exc:
        print(json.dumps({
            "error": str(exc),
            "resultado": None,
            "codigo_salida": 1,
        }))


if __name__ == "__main__":
    main()
```

Valida y limita los parámetros antes de incorporarlos al comando. No utilices `shell=True` con datos proporcionados por el usuario.

### 4. Agregar el builder a docker-compose.yml

```yaml
tool_nuevaherramienta:
  build:
    context: tools/nuevaherramienta
    dockerfile: Dockerfile
  image: backend_runner-nuevaherramienta
  container_name: runner-tool-nuevaherramienta-builder
  entrypoint: ["echo", "imagen lista"]
```

Construye la imagen:

```bash
docker compose build tool_nuevaherramienta
```

### 5. Registrar la herramienta

Desde Swagger, utiliza `POST /herramientas/` en Tool Registry o la ruta equivalente del API Gateway.

```json
{
  "nombre": "nombre_herramienta",
  "nombre_UI": "Nombre de la herramienta",
  "descripcion": "Descripción de lo que hace.",
  "casos_usos": ["caso 1", "caso 2"],
  "categoria": "categoria_correspondiente",
  "esquema_input": {
    "objetivo": {
      "tipo": "string",
      "requerido": true,
      "descripcion": "Dirección IP, dominio o URL autorizada"
    }
  },
  "esquema_output": {
    "total_hallazgos": {
      "tipo": "integer"
    }
  },
  "version_inicial": "1.0",
  "docker_imagen": "backend_runner-nuevaherramienta",
  "notas_version": "Primera integración"
}
```

Verifica que la versión creada quede asociada a la herramienta y que la imagen indicada coincida con la construida por Docker Compose.

### 6. Validar el pipeline

Ejecuta una prueba sobre un objetivo autorizado:

```json
{
  "herramienta": "nombre_herramienta",
  "params": {
    "objetivo": "127.0.0.1"
  },
  "sesion_id": 61,
  "orden_ejecucion": 1
}
```

Comprueba la respuesta de la tarea, los logs de Tool Executor y el registro creado en la tabla de ejecuciones.

## Operación y mantenimiento

### Logs

Todos los servicios:

```powershell
docker compose logs -f
```

Servicios específicos:

```powershell
docker logs -f runner-api-gateway
docker logs -f runner-tool-registry
docker logs -f runner-tool-executor
docker logs -f runner-seeder
docker logs -f runner-redis
```

### Detener el sistema

```powershell
docker compose down
```

Para eliminar también los volúmenes administrados por Docker Compose:

```powershell
docker compose down --volumes
```

Este comando no elimina la información almacenada en una base PostgreSQL externa.

### Reconstruir servicios

Todo el Runner:

```powershell
docker compose down
docker compose up --build -d
```

Un servicio específico:

```powershell
docker compose build api_gateway
docker compose up -d api_gateway
```

Cambia `api_gateway` por `tool_registry`, `tool_executor` o el builder de una herramienta según corresponda.

### Limpiar imágenes no utilizadas

Elimina imágenes huérfanas:

```bash
docker image prune
```

Elimina imágenes no utilizadas con más de 24 horas, respetando las imágenes asociadas a contenedores activos:

```bash
docker image prune -a --filter "until=24h"
```

Revisa la lista antes de confirmar una limpieza de imágenes en entornos compartidos.

### Limitación conocida

El API Gateway contiene una ruta general `GET /proxy/tareas`, pero la versión documentada de Tool Executor solamente expone la consulta individual:

```http
GET /ejecutar/tareas/{tarea_id}
```

El listado general requiere implementar primero el endpoint equivalente en Tool Executor.

## Seguridad de los objetivos

Actualmente el Runner acepta una dirección IP, un dominio o una URL como objetivo y opera bajo un modelo de confianza: quien solicita la ejecución es responsable de contar con autorización.

Los controles implementados incluyen:

* Separación lógica de recursos por tenant.
* Registro de solicitudes y resultados.
* Ejecución aislada en contenedores Docker efímeros.
* Acceso al Docker Engine mediante Docker Socket Proxy.
* Token interno compartido entre servicios autorizados.

El Runner todavía no valida la propiedad del objetivo. Para una versión productiva se recomienda implementar una allowlist por tenant y rechazar cualquier objetivo que no esté previamente autorizado.

## Comandos rápidos

```powershell
cd backend_runner
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

Documentación local:

```text
API Gateway:   http://localhost:8002/docs
Tool Registry: http://localhost:8003/docs
Tool Executor: http://localhost:8004/docs
```

