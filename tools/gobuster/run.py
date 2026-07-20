import sys
import json
import subprocess

def main():
    params = json.loads(sys.argv[1])
    
    url = params["url"]
    wordlist = params.get("wordlist", "/wordlists/common.txt")
    threads = params.get("threads", 10)

    cmd = [
        "gobuster", "dir",
        "-u", url,
        "-w", wordlist,
        "-t", str(threads),
        "--no-color",
        "-q"
    ]

    resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    hallazgos = []
    for linea in resultado.stdout.splitlines():
        linea = linea.strip()
        if linea and ("(Status:" in linea):
            # Ejemplo de línea: /admin (Status: 200) [Size: 1234]
            partes = linea.split(" (Status: ")
            if len(partes) == 2:
                ruta = partes[0].strip()
                status_crudo = partes[1].split(")")[0].strip()
                hallazgos.append({
                    "ruta": ruta, 
                    "status": int(status_crudo)
                })

    output = {
        "url": url,
        "resultado": {
            "directorios_encontrados": hallazgos,
            "total_encontrados": len(hallazgos),
            "raw_output": resultado.stdout
        },
        "codigo_salida": resultado.returncode,
        "error": resultado.stderr if resultado.returncode != 0 else None
    }

    print(json.dumps(output))

if __name__ == "__main__":
    main()