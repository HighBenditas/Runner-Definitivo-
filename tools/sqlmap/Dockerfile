FROM python:3.11-slim
RUN apt-get update && apt-get install -y git && \
    git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git /sqlmap && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY run.py .
ENTRYPOINT ["python", "run.py"]
