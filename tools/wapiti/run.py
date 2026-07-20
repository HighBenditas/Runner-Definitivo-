import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from urllib.parse import urlparse


def validate_url(url):
    if not url:
        raise ValueError("El parámetro url es obligatorio.")

    parsed = urlparse(url)

    if parsed.scheme not in ["http", "https"]:
        raise ValueError("La URL debe comenzar con http:// o https://")

    if not parsed.netloc:
        raise ValueError("La URL no es válida.")

    return url


def build_command(url, max_scan_time, depth, scope, output_file):
    allowed_scopes = ["url", "page", "folder", "subdomain", "domain"]

    if scope not in allowed_scopes:
        raise ValueError(f"Scope inválido. Permitidos: {allowed_scopes}")

    if depth < 1 or depth > 5:
        raise ValueError("La profundidad debe estar entre 1 y 5.")

    if max_scan_time < 60 or max_scan_time > 900:
        raise ValueError("max_scan_time debe estar entre 60 y 900 segundos.")

    return [
        "wapiti",
        "-u",
        url,
        "-f",
        "json",
        "-o",
        output_file,
        "--max-scan-time",
        str(max_scan_time),
        "-d",
        str(depth),
        "--scope",
        scope
    ]


def main():
    parser = argparse.ArgumentParser(description="Runner Dani-ETH para Wapiti")

    parser.add_argument("--url", required=True, help="URL objetivo autorizada")
    parser.add_argument("--max_scan_time", type=int, default=300, help="Tiempo máximo de escaneo en segundos")
    parser.add_argument("--depth", type=int, default=2, help="Profundidad del crawler")
    parser.add_argument("--scope", default="domain", help="Alcance del escaneo")
    parser.add_argument("--output", default="/output/wapiti_report.json", help="Archivo de salida JSON")

    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    started_at = datetime.utcnow().isoformat() + "Z"

    try:
        url = validate_url(args.url)

        command = build_command(
            url=url,
            max_scan_time=args.max_scan_time,
            depth=args.depth,
            scope=args.scope,
            output_file=args.output
        )

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=args.max_scan_time + 60
        )

        finished_at = datetime.utcnow().isoformat() + "Z"

        response = {
            "tool": "wapiti",
            "status": "success" if result.returncode == 0 else "error",
            "exit_code": result.returncode,
            "started_at": started_at,
            "finished_at": finished_at,
            "command": " ".join(command),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_file": args.output
        }

        print(json.dumps(response, indent=2, ensure_ascii=False))

        sys.exit(result.returncode)

    except Exception as e:
        finished_at = datetime.utcnow().isoformat() + "Z"

        response = {
            "tool": "wapiti",
            "status": "error",
            "exit_code": 1,
            "started_at": started_at,
            "finished_at": finished_at,
            "error": str(e),
            "output_file": args.output
        }

        print(json.dumps(response, indent=2, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()