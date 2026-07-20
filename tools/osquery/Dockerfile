FROM kalilinux/kali-rolling

# 1. Instalamos wget (para descargar) y python3
RUN apt-get update && \
    apt-get install -y python3 wget && \
    # 2. Descargamos el instalador oficial de OSQuery desde GitHub
    wget https://github.com/osquery/osquery/releases/download/5.12.2/osquery_5.12.2-1.linux_amd64.deb && \
    # 3. Lo instalamos en el sistema
    dpkg -i osquery_5.12.2-1.linux_amd64.deb && \
    # 4. Borramos el instalador y limpiamos la caché para ahorrar espacio
    rm osquery_5.12.2-1.linux_amd64.deb && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY run.py /app/run.py

ENTRYPOINT ["python3", "/app/run.py"]