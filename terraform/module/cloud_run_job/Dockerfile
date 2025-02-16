# Usar una imagen de Python más completa para evitar errores con dependencias
FROM python:3.10-slim

# Instalar herramientas necesarias para compilar algunas dependencias
RUN apt-get update && apt-get install -y gcc python3-dev libpq-dev && rm -rf /var/lib/apt/lists/*

# Configurar el directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias antes del código para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar pip y dependencias
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código después de instalar dependencias
COPY . .

# Exponer el puerto 8080 para Cloud Run
EXPOSE 8080

# Ejecutar la aplicación FastAPI
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]

