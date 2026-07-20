FROM aquasec/trivy:latest

USER root

RUN apk add --no-cache python3

COPY run.py /app/run.py

RUN mkdir -p /output

WORKDIR /app

ENTRYPOINT ["python3", "/app/run.py"]