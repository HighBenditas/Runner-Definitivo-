import sys
import json
import subprocess
import re

def main():
    try:
        # 1. Leer los inputs del orquestador (ahora soporta argumentos)
        if len(sys.argv) > 1:
            input_data = sys.argv[1]
        else:
            input_data = sys.stdin.read()
            
        params = json.loads(input_data)
        
        objetivo = params.get("objetivo", "")
        servicio = params.get("servicio", "ssh") # ssh, ftp, http-get, etc.
        usuario = params.get("usuario", "admin")
        
        if not objetivo:
            print(json.dumps({"error": "Falta la IP o dominio objetivo"}))
            sys.exit(1)

        # 2. Armar el comando de Hydra
        # -l: usuario específico | -P: diccionario de contraseñas | -t: hilos
        comando = [
            "hydra",
            "-l", usuario,
            "-P", "/passwords.txt",
            "-t", "4",
            f"{servicio}://{objetivo}"
        ]

        # 3. Ejecutar Hydra
        proceso = subprocess.run(comando, capture_output=True, text=True)
        salida_completa = proceso.stdout + proceso.stderr

        # 4. Parsear los resultados buscando credenciales exitosas
        credenciales_encontradas = []
        
        # Hydra marca los éxitos con "[puerto][servicio] host: IP   login: USUARIO   password: PASSWORD"
        # Usamos una expresión regular sencilla para capturarlo
        matches = re.findall(r"login:\s*(.*?)\s*password:\s*(.*)", salida_completa)
        
        for match in matches:
            credenciales_encontradas.append({
                "usuario": match[0].strip(),
                "password": match[1].strip()
            })

        # 5. Estructurar la salida JSON para Dani-ETH
        resultado = {
            "objetivo_escaneado": objetivo,
            "servicio": servicio,
            "credenciales_descubiertas": credenciales_encontradas,
            "total_hallazgos": len(credenciales_encontradas),
            "raw_output": salida_completa[-500:] # Mandamos el final del log por si hubo error
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