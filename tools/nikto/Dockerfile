# Usamos una imagen de Kali, que ya trae Nikto instalado por defecto
FROM kalilinux/kali-rolling

# Instalamos Python para poder ejecutar nuestro run.py y mantenemos nikto
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nikto \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY run.py .
# Usamos python3 ya que esta imagen es Kali
ENTRYPOINT ["python3", "run.py"]