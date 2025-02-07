FROM python:3.9

# Configurar el directorio de trabajo
WORKDIR /app

# Copiar archivos necesarios
COPY requirements.txt .
COPY api.py .
COPY start.sh .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Dar permisos de ejecución al script
RUN chmod +x start.sh

# Exponer el puerto 8080 para Cloud Run
EXPOSE 8080

# Usar el script como comando de inicio
CMD ["sh", "./start.sh"]