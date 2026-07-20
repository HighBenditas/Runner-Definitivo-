FROM python:3.11-slim
RUN apt-get update && apt-get install -y gobuster wget && \
    mkdir -p /wordlists && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -O /wordlists/common.txt && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY run.py .
ENTRYPOINT ["python", "run.py"]