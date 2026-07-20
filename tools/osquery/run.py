import sys
import json
import subprocess

def main():
    try:
        # 1. Leer inputs
        if len(sys.argv) > 1:
            input_data = sys.argv[1]
        else:
            input_data = sys.stdin.read()
            
        params = json.loads(input_data)
        
        # Si no le pasamos query, por defecto trae los 5 procesos que más RAM consumen
        query_por_defecto = "SELECT name, pid, resident_size FROM processes ORDER BY resident_size DESC LIMIT 5;"
        consulta_sql = params.get("query", query_por_defecto)

        # 2. Ejecutar OSQuery: le decimos que devuelva directo en JSON
        comando = ["osqueryi", "--json", consulta_sql]
        proceso = subprocess.run(comando, capture_output=True, text=True)

        if proceso.returncode != 0:
            print(json.dumps({
                "error": f"Fallo al ejecutar OSQuery: {proceso.stderr}",
                "resultado": None,
                "codigo_salida": proceso.returncode
            }))
            sys.exit(0)

        # 3. Parsear la salida (OSQuery ya nos da una lista de diccionarios)
        try:
            datos_extraidos = json.loads(proceso.stdout)
        except json.JSONDecodeError:
            datos_extraidos = []

        # 4. Estructurar para tu Orquestador
        resultado = {
            "consulta_ejecutada": consulta_sql,
            "total_filas": len(datos_extraidos),
            "datos_extraidos": datos_extraidos
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