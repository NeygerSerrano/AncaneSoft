# Usamos Python 3.12 (última estable LTS recomendada) ya que 3.14.6 no está disponible en las imágenes base oficiales de DockerHub todavía.
# Esta versión es 100% compatible con tu código.
FROM python:3.12-slim

# Evitar que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Forzar a que la salida de stdout y stderr no se almacene en búfer
ENV PYTHONUNBUFFERED 1

# Instalar dependencias del sistema requeridas para PostgreSQL (psycopg2) y Tailwind (Node.js)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de requerimientos e instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar el resto del código del proyecto
COPY . /app/

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar el servidor usando Gunicorn (recomendado para producción)
# Si no usas gunicorn, puedes cambiarlo por python manage.py runserver 0.0.0.0:8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
