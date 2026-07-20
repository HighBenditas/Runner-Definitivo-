# Guía de Integración de Herramientas - Dani-ETH Backend Runner

Este documento detalla la arquitectura y el flujo de trabajo estandarizado para integrar nuevas herramientas de ciberseguridad, como herramientas de pentesting, fuerza bruta, ingeniería inversa, entre otras, en el Orquestador `tool_executor` de Dani-ETH.

---

## 🔐 0. Multi-tenant y autenticación interna (setup obligatorio)

El runner ahora soporta aislamiento por cliente (tenant). Antes de usarlo en un
entorno real hay que hacer **dos pasos manuales**:

1. **Migración de BD (una vez):** ejecutá
   [`scripts/migrations/001_multi_tenant.sql`](scripts/migrations/001_multi_tenant.sql)
   contra la Supabase del runner. Añade la columna `usuarios.external_id`
   (el `uid` de Firebase del cliente), necesaria para el endpoint
   `POST /usuarios/` (get-or-create de usuario por tenant).

2. **Token interno compartido:** definí `INTERNAL_API_TOKEN` en el `.env` (el
   mismo valor debe ir en el `.env` del orquestador). Todas las rutas
   funcionales del runner exigen la cabecera `X-Internal-Token` con ese valor;
   `GET /` de cada servicio queda público para los healthchecks. Si se deja
   **vacío**, la autenticación interna se **desactiva** (modo desarrollo) y todo
   sigue funcionando sin token — cómodo para probar, inseguro para producción.

**Endpoints nuevos/relevantes del api_gateway (`:8002`):**

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/usuarios/` | Get-or-create de usuario por `external_id` (uid de Firebase). Devuelve `usuario_id`. |
| `POST` | `/objetivos/` | Crea un objetivo para un `usuario_id`. |
| `POST` | `/sesiones/` | Crea una sesión para un `objetivo_id`. |

El orquestador encadena estos tres por campaña para crear una sesión aislada por
cliente. Además, `GET /ejecutar/tareas/{id}` del tool_executor acepta un
`?usuario_id=` opcional: si se pasa, valida que la tarea pertenezca a ese usuario
(responde `404` si no, para no delatar tareas ajenas).

El diseño completo está en el repo del orquestador:
`Orquestador_AI_ETH/Docs/multi_tenant_plan.md`.

---

## 🏗️ 1. Arquitectura Base ("Con peras y manzanas")

Cada herramienta en nuestro ecosistema funciona como una "caja negra" independiente. El ciclo de vida de una herramienta es el siguiente:

1. API `FastAPI` recibe una orden de escaneo.
2. Orquestador levanta un contenedor Docker efímero con la herramienta.
3. El contenedor ejecuta un script `run.py` que recibe parámetros en JSON, dispara el comando real de la herramienta, captura la consola y la traduce de vuelta a JSON.
4. El resultado se guarda en la base de datos y el contenedor se destruye inmediatamente.

La estructura de carpetas para una nueva herramienta debe verse así:

```plaintext id="f2rhm5"
backend_runner/
├── docker-compose.yml
└── tools/
    └── nombre_herramienta/
        ├── Dockerfile
        └── run.py
```

---

## 🛠️ 2. El Dockerfile (El Entorno)

Utilizamos imágenes base ligeras, como `debian-slim`, o imágenes que ya contienen las herramientas en sus repositorios nativos, como `kalilinux/kali-rolling`, para optimizar el almacenamiento y el caché.

Plantilla estándar:

```dockerfile id="dls3m1"
# Usar la imagen base adecuada (Kali suele tener todas las herramientas)
FROM kalilinux/kali-rolling

# Actualizar e instalar python3 y la herramienta específica
RUN apt-get update && \
    apt-get install -y python3 nombre_de_la_herramienta && \
    rm -rf /var/lib/apt/lists/* # LÍNEA VITAL para ahorrar espacio en disco

WORKDIR /app
COPY run.py /app/run.py

# IMPORTANTE: Usar ENTRYPOINT y no CMD para evitar el error "OCI runtime create failed"
# al pasarle el JSON de configuración desde el orquestador.
ENTRYPOINT ["python3", "/app/run.py"]
```

---

## 🐍 3. El run.py (El Traductor a JSON)

Este script es el puente entre el mundo del texto plano, la consola, y la API REST, JSON.

Plantilla estándar:

```python id="svw42a"
import sys
import json
import subprocess

def main():
    try:
        # 1. Leer inputs desde los argumentos del Orquestador (Parche OCI)
        if len(sys.argv) > 1:
            input_data = sys.argv[1]
        else:
            input_data = sys.stdin.read()
            
        params = json.loads(input_data)
        
        # 2. Extraer parámetros (Ejemplo)
        objetivo = params.get("objetivo", "127.0.0.1")

        # 3. Armar y ejecutar el comando
        comando = ["herramienta", "-parametro", objetivo]
        proceso = subprocess.run(comando, capture_output=True, text=True)

        # 4. Procesar la salida (Regex, JSON nativo, etc.)
        # ... lógica de parseo aquí ...

        # 5. Estructurar el JSON de salida estándar para Dani-ETH
        resultado = {
            "objetivo_escaneado": objetivo,
            "total_hallazgos": 0, # Reemplazar con variable real
            "raw_output": proceso.stdout + proceso.stderr
        }

        print(json.dumps({
            "error": None,
            "resultado": resultado,
            "codigo_salida": proceso.returncode
        }))

    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "resultado": None,
            "codigo_salida": 1
        }))

if __name__ == "__main__":
    main()
```

---

## 🐳 4. Integración en docker-compose.yml

Para que el orquestador sepa que la herramienta existe, debe registrarse como un servicio "builder" en el Compose.

```yaml id="cx1z5n"
tool_nuevaherramienta:
  build:
    context: tools/nuevaherramienta
    dockerfile: Dockerfile
  image: backend_runner-nuevaherramienta
  container_name: runner-tool-nuevaherramienta-builder
  entrypoint: ["echo", "imagen lista"]
```

Asegúrate de respetar la indentación vertical estricta del YAML para evitar errores de parseo.

---

## 💻 5. Comandos de Terminal Clave

### Construcción y Despliegue

Construir una herramienta específica:

```bash id="xi2qiy"
docker compose build tool_nuevaherramienta
```

Levantar toda la infraestructura base:

```bash id="lhyh6h"
docker compose up -d
```

### Mantenimiento y Limpieza (Liberar Espacio)

Borrar imágenes huérfanas, como intentos fallidos de build:

```bash id="5yi7be"
docker image prune
```

Limpieza profunda y segura de imágenes viejas, respetando los contenedores activos:

```bash id="5huws3"
docker image prune -a --filter "until=24h"
```

Ver logs en tiempo real del Orquestador:

```bash id="7w7mo4"
docker logs -f runner-tool-executor
```

---

## 🚀 6. Registro en FastAPI y Base de Datos

Una vez que la imagen Docker está construida, la herramienta debe registrarse en la plataforma para que el Frontend pueda consumirla.

### A. Registrar la Herramienta (Swagger: POST /herramientas/)

Se debe enviar un esquema con la definición completa.

Ejemplo:

```json id="ek86b5"
{
  "nombre": "nombre_herramienta",
  "nombre_UI": "Nombre Amigable UI",
  "descripcion": "Descripción de lo que hace.",
  "casos_usos": ["caso 1", "caso 2"],
  "categoria": "categoria correspondiente",
  "esquema_input": {
    "objetivo": {
      "tipo": "string",
      "requerido": true,
      "descripcion": "IP o Dominio"
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

Nota: Tras esto, asociar manualmente el ID generado en la tabla `versiones_herramientas` en Supabase.

### B. Ejecutar una Prueba (Swagger: POST /ejecutar/)

Para validar el pipeline completo:

```json id="6py28k"
{
  "herramienta": "nombre_herramienta",
  "params": {
    "objetivo": "127.0.0.1"
  },
  "sesion_id": 61,
  "orden_ejecucion": 1
}
```

El resultado JSON validado se guardará en la tabla de ejecuciones de Supabase.
