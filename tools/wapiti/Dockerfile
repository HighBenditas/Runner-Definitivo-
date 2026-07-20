FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libffi-dev \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir wapiti3

COPY run.py /app/run.py

RUN mkdir -p /output /session

WORKDIR /app

ENTRYPOINT ["python", "/app/run.py"]