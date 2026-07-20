import argparse
import json
import os
import subprocess
import sys
from datetime import datetime


def build_command(scan_type, target, scanners, timeout, output_file):
    allowed_scan_types = ["image", "repo", "fs"]

    if scan_type not in allowed_scan_types:
        raise ValueError(f"scan_type inválido. Permitidos: {allowed_scan_types}")

    if not target:
        raise ValueError("El parámetro target es obligatorio.")

    if scanners is None or scanners.strip() == "":
        scanners = "vuln,secret,misconfig"

    if timeout is None or timeout.strip() == "":
        timeout = "5m"

    return [
        "trivy",
        scan_type,
        "--format",
        "json",
        "--output",
        output_file,
        "--scanners",
        scanners,
        "--timeout",
        timeout,
        target
    ]


def main():
    parser = argparse.ArgumentParser(description="Runner Dani-ETH para Trivy")

    parser.add_argument("--scan_type", required=True, help="Tipo de escaneo: image, repo o fs")
    parser.add_argument("--target", required=True, help="Imagen, repositorio o ruta a escanear")
    parser.add_argument("--scanners", default="vuln,secret,misconfig", help="Scanners de Trivy")
    parser.add_argument("--timeout", default="5m", help="Tiempo máximo de ejecución")
    parser.add_argument("--output", default="/output/trivy_report.json", help="Archivo de salida JSON")

    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    started_at = datetime.utcnow().isoformat() + "Z"

    try:
        command = build_command(
            scan_type=args.scan_type,
            target=args.target,
            scanners=args.scanners,
            timeout=args.timeout,
            output_file=args.output
        )

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=600
        )

        finished_at = datetime.utcnow().isoformat() + "Z"

        response = {
            "tool": "trivy",
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
            "tool": "trivy",
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