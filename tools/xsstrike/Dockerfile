FROM python:3.11-slim
RUN apt-get update && apt-get install -y git && \
    git clone --depth 1 https://github.com/s0md3v/XSStrike.git /xsstrike && \
    pip install --no-cache-dir -r /xsstrike/requirements.txt && \
    python3 -c "f=open('/xsstrike/core/wafDetector.py','r');c=f.read();f.close();c=c.replace('if int(code) >= 400:','if str(code).isdigit() and int(code) >= 400:');f=open('/xsstrike/core/wafDetector.py','w');f.write(c);f.close()" && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY run.py .
ENTRYPOINT ["python", "run.py"]
