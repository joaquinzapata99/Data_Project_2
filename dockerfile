FROM python:3.9

# Configurar el directorio de trabajo
WORKDIR /app

# Copiar archivos necesarios
COPY requirements.txt .
COPY api.py .
COPY /secrets/data-project-2-449815-02b4b3af0560.json /app/secrets/data-project-2-449815-02b4b3af0560.json
COPY start.sh .

# Configurar variable de entorno para credenciales
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/secrets/data-project-2-449815-02b4b3af0560.json"

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Dar permisos de ejecución al script
RUN chmod +x start.sh

# Exponer el puerto 8000 para FastAPI
EXPOSE 8000

# Usar el script como comando de inicio
CMD ["sh", "./start.sh"]
