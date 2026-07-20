import sys
import json
import subprocess


def main():
    params = json.loads(sys.argv[1])

    url = params["url"]
    metodo = params.get("metodo", "GET").upper()
    headers = params.get("headers", {})
    data = params.get("data", "")
    flags_extra = params.get("flags_extra", "")

    cmd = ["curl", "-s", "-i", "-X", metodo]

    for k, v in headers.items():
        cmd.extend(["-H", f"{k}: {v}"])

    if data:
        cmd.extend(["-d", data])

    if flags_extra:
        import shlex
        cmd.extend(shlex.split(flags_extra))

    cmd.append(url)

    resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    output = {
        "url": url,
        "metodo": metodo,
        "resultado": {
            "stdout": resultado.stdout,
            "stderr": resultado.stderr
        },
        "codigo_salida": resultado.returncode,
        "error": resultado.stderr if resultado.returncode != 0 else None
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
