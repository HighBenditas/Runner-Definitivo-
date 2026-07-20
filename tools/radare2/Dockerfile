# Usamos Kali Linux (que ya tienes descargado, ¡cero peso extra!)
FROM kalilinux/kali-rolling

# En los repositorios de Kali, radare2 sí existe nativamente
RUN apt-get update && \
    apt-get install -y python3 radare2 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY run.py /app/run.py

# Copiamos un binario inofensivo del sistema para usarlo de prueba
RUN cp /bin/ls /app/malware_de_prueba.bin

# Usamos ENTRYPOINT para evitar el error OCI del JSON
ENTRYPOINT ["python3", "/app/run.py"]