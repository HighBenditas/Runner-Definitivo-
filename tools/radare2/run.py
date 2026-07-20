import sys
import json
import subprocess

def main():
    try:
        # 1. Leer inputs de forma segura (nuestro parche maestro)
        if len(sys.argv) > 1:
            input_data = sys.argv[1]
        else:
            input_data = sys.stdin.read()
            
        params = json.loads(input_data)
        
        # Por defecto analizamos el binario de prueba que metimos en el Dockerfile
        archivo_objetivo = params.get("archivo", "/app/malware_de_prueba.bin")

        # 2. Comando Radare2: 
        # -q (quiet, sin interfaz), -j (output JSON), -c "iIj" (comando info -> binary info -> json format)
        comando = ["r2", "-q", "-j", "-c", "iIj", archivo_objetivo]

        # 3. Ejecutar
        proceso = subprocess.run(comando, capture_output=True, text=True)

        if proceso.returncode != 0:
            print(json.dumps({
                "error": f"Fallo al ejecutar r2: {proceso.stderr}",
                "resultado": None,
                "codigo_salida": proceso.returncode
            }))
            sys.exit(0)

        # 4. Radare2 nos devuelve el JSON crudo en stdout, lo cargamos
        try:
            data_cruda = json.loads(proceso.stdout)
            # Radare2 guarda la información útil dentro de la llave "bin"
            info_binario = data_cruda.get("bin", {})
        except json.JSONDecodeError:
            info_binario = {}

        # 5. Estructurar para tu Orquestador
        resultado = {
            "archivo_analizado": archivo_objetivo,
            "arquitectura": info_binario.get("arch", "Desconocida"),
            "bits": info_binario.get("bits", 0),
            "sistema_operativo": info_binario.get("os", "Desconocido"),
            "lenguaje": info_binario.get("lang", "Desconocido"),
            "es_ejecutable": info_binario.get("exec", False),
            "total_hallazgos": 1
        }

        print(json.dumps({
            "error": None,
            "resultado": resultado,
            "codigo_salida": 0
        }))

    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "resultado": None,
            "codigo_salida": 1
        }))

if __name__ == "__main__":
    main()