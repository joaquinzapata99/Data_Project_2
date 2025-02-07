#!/bin/sh

# Iniciar la API en segundo plano para permitir generación de datos
uvicorn api:app --host 0.0.0.0 --port 8080 &

# Esperar unos segundos para que la API se inicie correctamente
sleep 5

# Contadores de generación
requests_generated=0
helpers_generated=0
max_requests=500
max_helpers=500

echo "Generando datos aleatorios hasta llegar a $max_requests peticiones y $max_helpers voluntarios..."

while [ $requests_generated -lt $max_requests ] || [ $helpers_generated -lt $max_helpers ]
do
    if [ $requests_generated -lt $max_requests ]; then
        curl -X POST "http://localhost:8080/generate_requests?n=10" -s -o /dev/null
        requests_generated=$((requests_generated + 5))
        echo "Peticiones generadas: $requests_generated"
    fi

    if [ $helpers_generated -lt $max_helpers ]; then
        curl -X POST "http://localhost:8080/generate_helpers?n=10" -s -o /dev/null
        helpers_generated=$((helpers_generated + 5))
        echo "Voluntarios generados: $helpers_generated"
    fi

    # Espera 2 segundos antes de la siguiente iteración
    sleep 2
done

echo "Generación completa: $requests_generated peticiones y $helpers_generated voluntarios."

# Mantener el contenedor en ejecución (necesario para Cloud Run)
wait
