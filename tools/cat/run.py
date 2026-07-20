import sys
import json
import subprocess


def main():
    params = json.loads(sys.argv[1])

    archivo = params["archivo"]
    flags = params.get("flags", "")

    cmd = ["cat"]
    if flags:
        cmd.extend(flags.split())
    cmd.append(archivo)

    resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    output = {
        "archivo": archivo,
        "resultado": {
            "contenido": resultado.stdout,
            "lineas": len(resultado.stdout.splitlines()) if resultado.stdout else 0
        },
        "codigo_salida": resultado.returncode,
        "error": resultado.stderr if resultado.returncode != 0 else None
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
