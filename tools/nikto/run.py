import sys
import json
import subprocess
import re

def parsear_nikto(texto):
    vulnerabilidades = []
    # Nikto reporta vulnerabilidades usualmente con el formato "+ Entry..."
    # Buscamos las líneas que empiezan con "+ " para identificar los hallazgos
    lineas = texto.splitlines()
    
    for linea in lineas:
        linea = linea.strip()
        # Las líneas que son hallazgos importantes suelen empezar con '+' y tener información de puerto/vulnerabilidad
        if linea.startswith("+ "):
            # Limpiamos el prefijo '+ '
            info = linea[2:].strip()
            vulnerabilidades.append(info)
            
    # Extraemos el servidor detectado si existe
    servidor = "Desconocido"
    match_server = re.search(r"Server: (.*)", texto)
    if match_server:
        servidor = match_server.group(1)
        
    return {
        "servidor_detectado": servidor,
        "vulnerabilidades_encontradas": vulnerabilidades,
        "total_hallazgos": len(vulnerabilidades)
    }

def main():
    try:
        # Cargar parámetros desde el JSON que envía el orquestador
        params = json.loads(sys.argv[1])
        url = params["url"]
        
        # Ejecutamos Nikto. Usamos -Tuning 123 para un escaneo eficiente
        cmd = ["nikto", "-h", url, "-Tuning", "123"]
        
        resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        # Parseamos la salida solo si el comando no falló (o si tuvo salida parcial)
        parsed_data = parsear_nikto(resultado.stdout)
        
        output = {
            "url": url,
            "resultado": parsed_data,
            "codigo_salida": resultado.returncode,
            "error": resultado.stderr if resultado.returncode != 0 and not resultado.stdout else None
        }
        
        print(json.dumps(output))
        
    except Exception as e:
        # En caso de error crítico en el script, devolvemos un JSON de error
        error_output = {
            "error_ejecucion": str(e),
            "codigo_salida": 1
        }
        print(json.dumps(error_output))

if __name__ == "__main__":
    main()