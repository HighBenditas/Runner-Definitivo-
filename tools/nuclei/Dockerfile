FROM python:3.11-slim
RUN apt-get update && apt-get install -y wget unzip git && \
    wget -q https://github.com/projectdiscovery/nuclei/releases/download/v3.1.0/nuclei_3.1.0_linux_amd64.zip && \
    unzip nuclei_3.1.0_linux_amd64.zip && \
    mv nuclei /usr/local/bin/ && \
    rm -f nuclei_3.1.0_linux_amd64.zip && \
    rm -rf /var/lib/apt/lists/*
# Pre-descargar templates durante el build
RUN nuclei -update-templates
WORKDIR /app
COPY run.py .
ENTRYPOINT ["python", "run.py"]
