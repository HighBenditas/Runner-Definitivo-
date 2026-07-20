# Usamos Kali Linux (que ya tienes descargado, ¡cero peso extra!)
FROM kalilinux/kali-rolling

# En los repositorios de Kali, Hydra sí existe nativamente
RUN apt-get update && \
    apt-get install -y python3 hydra && \
    rm -rf /var/lib/apt/lists/*

# Creamos el diccionario básico
RUN echo "123456" > /passwords.txt && \
    echo "password" >> /passwords.txt && \
    echo "admin123" >> /passwords.txt && \
    echo "qwerty" >> /passwords.txt

WORKDIR /app
COPY run.py /app/run.py

# Comando por defecto
ENTRYPOINT ["python3", "/app/run.py"]