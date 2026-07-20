import os
import time
import requests

TOOL_REGISTRY_URL = "http://tool_registry:8003"

# Token interno del runner: si está configurado, se envía en cada petición al
# registry (que ahora exige X-Internal-Token en sus rutas funcionales).
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN", "")
INTERNAL_HEADERS = {"X-Internal-Token": INTERNAL_API_TOKEN} if INTERNAL_API_TOKEN else {}

HERRAMIENTAS = [
    {
        "nombre": "nmap",
        "nombre_UI": "Nmap",
        "descripcion": "Escáner de puertos y detección de servicios",
        "categoria": "reconocimiento",
        "casos_usos": ["descubrir puertos abiertos", "detectar servicios y versiones", "reconocimiento de red"],
        "version_inicial": "1.0.0",
        "docker_imagen": "backend_runner-nmap",
        "esquema_input": {
            "objetivo": {"type": "string", "required": True, "description": "IP o hostname objetivo"},
            "tipo_escaneo": {"type": "string", "required": False, "default": "-sV", "description": "Tipo de escaneo nmap"},
            "velocidad": {"type": "integer", "required": False, "default": 3, "description": "Velocidad T0-T5"},
            "puertos": {"type": "string", "required": False, "default": "", "description": "Puertos a escanear ej: 80,443 o 1-1000"}
        },
        "esquema_output": {
            "objetivo": {"type": "string"},
            "resultado": {
                "hosts": {"type": "array"},
                "resumen": {"type": "object"}
            },
            "codigo_salida": {"type": "integer"},
            "error": {"type": "string"}
        }
    },
    {
        "nombre": "sqlmap",
        "nombre_UI": "SQLMap",
        "descripcion": "Detección y explotación de inyecciones SQL",
        "categoria": "vulnerabilidades",
        "casos_usos": ["detectar SQL injection", "extraer datos de bases de datos", "fingerprinting de DBMS"],
        "version_inicial": "1.0.0",
        "docker_imagen": "backend_runner-sqlmap",
        "esquema_input": {
            "url": {"type": "string", "required": True, "description": "URL objetivo"},
            "parametro": {"type": "string", "required": False, "default": "", "description": "Parámetro a testear"},
            "nivel": {"type": "integer", "required": False, "default": 1, "description": "Nivel de tests 1-5"},
            "riesgo": {"type": "integer", "required": False, "default": 1, "description": "Riesgo 1-3"},
            "data": {"type": "string", "required": False, "default": "", "description": "POST body"},
            "forms": {"type": "boolean", "required": False, "default": False},
            "crawl": {"type": "integer", "required": False, "default": 0},
            "dbms": {"type": "string", "required": False, "default": ""},
            "tecnica": {"type": "string", "required": False, "default": ""},
            "time_sec": {"type": "integer", "required": False, "default": 10},
            "cookies": {"type": "string", "required": False, "default": ""}
        },
        "esquema_output": {
            "url": {"type": "string"},
            "resultado": {
                "vulnerable": {"type": "boolean"},
                "inyecciones_detectadas": {"type": "array"},
                "raw_output": {"type": "string"}
            },
            "codigo_salida": {"type": "integer"},
            "error": {"type": "string"}
        }
    },
    {
        "nombre": "nuclei",
        "nombre_UI": "Nuclei",
        "descripcion": "Escáner de vulnerabilidades basado en templates",
        "categoria": "vulnerabilidades",
        "casos_usos": ["detectar CVEs", "escaneo de exposiciones", "detección de misconfiguraciones"],
        "version_inicial": "1.0.0",
        "docker_imagen": "backend_runner-nuclei",
        "esquema_input": {
            "objetivo": {"type": "string", "required": True, "description": "URL o IP objetivo"},
            "templates": {"type": "array", "required": False, "default": [], "description": "Templates a usar ej: ['cves/', 'exposures/']"},
            "severidad": {"type": "array", "required": False, "default": [], "description": "Filtrar por severidad: info, low, medium, high, critical"},
            "rate_limit": {"type": "integer", "required": False, "default": 150}
        },
        "esquema_output": {
            "objetivo": {"type": "string"},
            "resultado": {
                "vulnerabilidades": {"type": "array"},
                "resumen": {"type": "object"}
            },
            "codigo_salida": {"type": "integer"},
            "error": {"type": "string"}
        }
    },
    {
        "nombre": "curl",
        "nombre_UI": "cURL",
        "descripcion": "Realiza peticiones HTTP/HTTPS a URLs objetivo",
        "categoria": "reconocimiento",
        "casos_usos": ["hacer peticiones HTTP", "inspeccionar headers de respuesta", "testear endpoints REST", "enviar POST con datos"],
        "version_inicial": "1.0.0",
        "docker_imagen": "backend_runner-curl",
        "esquema_input": {
            "url": {"type": "string", "required": True, "description": "URL objetivo"},
            "metodo": {"type": "string", "required": False, "default": "GET", "description": "Método HTTP: GET, POST, PUT, DELETE"},
            "headers": {"type": "object", "required": False, "default": {}, "description": "Headers HTTP clave-valor"},
            "data": {"type": "string", "required": False, "default": "", "description": "Body de la petición"},
            "flags_extra": {"type": "string", "required": False, "default": "", "description": "Flags adicionales de curl ej: --insecure"}
        },
        "esquema_output": {
            "url": {"type": "string"},
            "metodo": {"type": "string"},
            "resultado": {
                "stdout": {"type": "string"},
                "stderr": {"type": "string"}
            },
            "codigo_salida": {"type": "integer"},
            "error": {"type": "string"}
        }
    },
    {
        "nombre": "ls",
        "nombre_UI": "ls",
        "descripcion": "Lista archivos y directorios de una ruta dentro del container",
        "categoria": "reconocimiento",
        "casos_usos": ["listar archivos de un directorio", "explorar estructura de carpetas"],
        "version_inicial": "1.0.0",
        "docker_imagen": "backend_runner-ls",
        "esquema_input": {
            "ruta": {"type": "string", "required": False, "default": ".", "description": "Ruta a listar"},
            "flags": {"type": "string", "required": False, "default": "-la", "description": "Flags de ls ej: -la, -lh"}
        },
        "esquema_output": {
            "ruta": {"type": "string"},
            "resultado": {
                "archivos": {"type": "array"},
                "total": {"type": "integer"},
                "raw": {"type": "string"}
            },
            "codigo_salida": {"type": "integer"},
            "error": {"type": "string"}
        }
    },
    {
        "nombre": "cat",
        "nombre_UI": "cat",
        "descripcion": "Muestra el contenido de un archivo dentro del container",
        "categoria": "reconocimiento",
        "casos_usos": ["leer contenido de un archivo", "inspeccionar archivos de configuración"],
        "version_inicial": "1.0.0",
        "docker_imagen": "backend_runner-cat",
        "esquema_input": {
            "archivo": {"type": "string", "required": True, "description": "Ruta del archivo a leer"},
            "flags": {"type": "string", "required": False, "default": "", "description": "Flags de cat ej: -n para numerar líneas"}
        },
        "esquema_output": {
            "archivo": {"type": "string"},
            "resultado": {
                "contenido": {"type": "string"},
                "lineas": {"type": "integer"}
            },
            "codigo_salida": {"type": "integer"},
            "error": {"type": "string"}
        }
    },
    {
        "nombre": "xsstrike",
        "nombre_UI": "XSStrike",
        "descripcion": "Detección de vulnerabilidades XSS",
        "categoria": "vulnerabilidades",
        "casos_usos": ["detectar XSS reflejado", "detectar XSS en formularios", "crawl de parámetros XSS"],
        "version_inicial": "1.0.0",
        "docker_imagen": "backend_runner-xsstrike",
        "esquema_input": {
            "url": {"type": "string", "required": True, "description": "URL objetivo"},
            "parametro": {"type": "string", "required": False, "default": "", "description": "Parámetro específico a testear"},
            "crawl": {"type": "boolean", "required": False, "default": False, "description": "Hacer crawl del sitio"}
        },
        "esquema_output": {
            "url": {"type": "string"},
            "resultado": {
                "vulnerable": {"type": "boolean"},
                "hallazgos": {"type": "array"},
                "total_encontrados": {"type": "integer"}
            },
            "codigo_salida": {"type": "integer"},
            "error": {"type": "string"}
        }
    }
]


def esperar_registry(max_intentos=30, intervalo=3):
    print("Esperando que tool_registry esté listo...")
    for i in range(max_intentos):
        try:
            r = requests.get(f"{TOOL_REGISTRY_URL}/", timeout=3)
            if r.status_code == 200:
                print("tool_registry disponible.")
                return True
        except Exception:
            pass
        print(f"  intento {i + 1}/{max_intentos}...")
        time.sleep(intervalo)
    print("ERROR: tool_registry no respondió a tiempo.")
    return False


def registrar_herramienta(h):
    nombre = h["nombre"]
    try:
        r = requests.post(f"{TOOL_REGISTRY_URL}/herramientas/", json=h, headers=INTERNAL_HEADERS, timeout=10)
        if r.status_code in (200, 201):
            print(f"  [{nombre}] registrada OK")
        elif r.status_code == 409:
            print(f"  [{nombre}] ya existe, omitiendo")
        else:
            print(f"  [{nombre}] ERROR {r.status_code}: {r.text}")
    except Exception as e:
        print(f"  [{nombre}] ERROR: {e}")


def main():
    if not esperar_registry():
        exit(1)

    print("\nRegistrando herramientas...")
    for h in HERRAMIENTAS:
        registrar_herramienta(h)

    print("\nSeed completado.")


if __name__ == "__main__":
    main()
