FROM python:3.11-slim
RUN apt-get update && apt-get install -y docker.io && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY shared/ ./shared/
COPY tool_executor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY tool_executor/ ./tool_executor/
CMD ["uvicorn","tool_executor.app.main:app","--host","0.0.0.0","--port","8004"]