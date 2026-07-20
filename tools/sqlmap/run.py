import sys
import json
import subprocess


def main():
    params = json.loads(sys.argv[1])

    url = params["url"]
    parametro = params.get("parametro", "")
    nivel = params.get("nivel", 1)
    data = params.get("data", "")
    forms = params.get("forms", False)
    crawl = params.get("crawl", 0)
    riesgo = params.get("riesgo", 1)
    dbms = params.get("dbms", "")
    tecnica = params.get("tecnica", "")
    time_sec = params.get("time_sec", 10)
    cookies = params.get("cookies", "")

    cmd = [
        "python", "/sqlmap/sqlmap.py",
        "-u", url,
        "--level", str(nivel),
        "--risk", str(riesgo),
        "--time-sec", str(time_sec),
        "--batch",
        "--random-agent",
        "--output-dir", "/tmp/sqlmap_output"
    ]
    if parametro:
        cmd.extend(["-p", parametro])
    if data:
        cmd.extend(["--data", data])
    if forms:
        cmd.append("--forms")
    if crawl:
        cmd.extend(["--crawl", str(crawl)])
    if dbms:
        cmd.extend(["--dbms", dbms])
    if tecnica:
        cmd.extend(["--technique", tecnica])
    if cookies:
        cmd.extend(["--cookie", cookies])

    resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=800)

    texto = resultado.stdout
    texto_lower = texto.lower()

    vulnerable = any([
        "sqlmap identified the following injection" in texto_lower,
        "is vulnerable. do you want to exploit" in texto_lower,
        ("---" in texto and "Parameter:" in texto and "Type:" in texto and "Payload:" in texto),
    ])

    inyecciones = []
    capturando = False
    for linea in texto.splitlines():
        stripped = linea.strip()
        if stripped.startswith("Parameter:"):
            capturando = True
        if capturando and stripped:
            inyecciones.append(stripped)
        if capturando and not stripped:
            capturando = False

    output = {
        "url": url,
        "resultado": {
            "vulnerable": vulnerable,
            "inyecciones_detectadas": inyecciones,
            "raw_output": texto
        },
        "codigo_salida": resultado.returncode,
        "error": resultado.stderr if resultado.returncode != 0 and not vulnerable else None
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
