FROM python:3.10.16-slim

# Configurar el directorio de trabajo
WORKDIR /app

# Copiar archivos necesarios
COPY requirements.txt .
COPY api.py .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8080 para Cloud Run
EXPOSE 8080

# Ejecutar FastAPI directamente
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
