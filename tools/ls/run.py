import sys
import json
import subprocess


def main():
    params = json.loads(sys.argv[1])

    ruta = params.get("ruta", ".")
    flags = params.get("flags", "-la")

    import shlex
    cmd = ["ls"] + shlex.split(flags) + [ruta]

    resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    lineas = resultado.stdout.strip().splitlines() if resultado.stdout else []

    error = None
    if resultado.returncode != 0:
        error = resultado.stderr.strip() or f"No se pudo listar '{ruta}'"

    output = {
        "ruta": ruta,
        "resultado": {
            "archivos": lineas,
            "total": len(lineas),
            "raw": resultado.stdout
        },
        "codigo_salida": resultado.returncode,
        "error": error
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
