FROM python:3.11-slim
WORKDIR /app
COPY shared/ ./shared/
COPY tool_registry/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY tool_registry/ ./tool_registry/
CMD ["uvicorn", "tool_registry.app.main:app", "--host", "0.0.0.0", "--port", "8003"]
