import sys
import json
import subprocess
import xml.etree.ElementTree as ET


def parsear_xml(xml_str):
    try:
        root = ET.fromstring(xml_str)
        hosts = []

        for host in root.findall("host"):
            estado = host.find("status").get("state", "unknown")
            ip = ""
            hostname = ""

            for addr in host.findall("address"):
                if addr.get("addrtype") == "ipv4":
                    ip = addr.get("addr", "")

            hostnames_el = host.find("hostnames")
            if hostnames_el is not None:
                hn = hostnames_el.find("hostname")
                if hn is not None:
                    hostname = hn.get("name", "")

            puertos_abiertos = []
            total_filtrados = 0
            ports_el = host.find("ports")
            if ports_el is not None:
                for port in ports_el.findall("port"):
                    state_el = port.find("state")
                    service_el = port.find("service")
                    if state_el is not None and state_el.get("state") == "open":
                        puertos_abiertos.append({
                            "puerto": int(port.get("portid")),
                            "protocolo": port.get("protocol"),
                            "estado": state_el.get("state"),
                            "servicio": service_el.get("name") if service_el is not None else "",
                            "version": service_el.get("version", "") if service_el is not None else ""
                        })

                extraports = ports_el.find("extraports")
                total_filtrados = int(extraports.get("count", 0)) if extraports is not None else 0

            hosts.append({
                "ip": ip,
                "hostname": hostname,
                "estado": estado,
                "puertos_abiertos": puertos_abiertos,
                "total_puertos_abiertos": len(puertos_abiertos),
                "total_puertos_filtrados": total_filtrados
            })

        runstats = root.find("runstats")
        hosts_stats = runstats.find("hosts") if runstats is not None else None

        return {
            "hosts": hosts,
            "resumen": {
                "total_hosts": int(hosts_stats.get("total", 0)) if hosts_stats is not None else 0,
                "hosts_activos": int(hosts_stats.get("up", 0)) if hosts_stats is not None else 0,
                "total_puertos_abiertos": sum(h["total_puertos_abiertos"] for h in hosts)
            }
        }
    except Exception as e:
        return {"error_parseo": str(e), "raw_xml": xml_str}


def main():
    params = json.loads(sys.argv[1])

    objetivo = params["objetivo"]
    puertos = params.get("puertos", "")
    tipo_escaneo = params.get("tipo_escaneo", "-sV")
    velocidad = params.get("velocidad", 3)

    cmd = ["nmap", "-oX", "-", tipo_escaneo, f"-T{velocidad}"]
    if puertos:
        cmd.extend(["-p", puertos])
    cmd.append(objetivo)

    resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if resultado.returncode == 0 and resultado.stdout:
        parsed = parsear_xml(resultado.stdout)
    else:
        parsed = {}

    output = {
        "objetivo": objetivo,
        "resultado": parsed,
        "codigo_salida": resultado.returncode,
        "error": resultado.stderr if resultado.returncode != 0 else None
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
