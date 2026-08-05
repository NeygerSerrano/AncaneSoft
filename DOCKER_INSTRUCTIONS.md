# Guía de Instalación con Docker (MediQQTA)

Esta guía explica paso a paso cómo llevarte este proyecto a **cualquier computadora** y ejecutarlo en cuestión de minutos usando Docker, sin preocuparte por versiones de Python, Node.js ni bases de datos complejas.

## Requisitos Previos (En la nueva computadora)
1. Instalar [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Asegurarse de que Docker Desktop esté abierto y ejecutándose (el ícono de la ballena debe aparecer en la barra de tareas).

## Paso a Paso para Levantar el Proyecto

### 1. Copiar el Proyecto
Copia toda la carpeta raíz de tu proyecto `MediQQTA` a la nueva computadora (puedes usar un USB, un disco duro, o descargarlo de GitHub si lo subes).

### 2. Configurar Variables de Entorno (IMPORTANTE)
Dentro de la carpeta del proyecto verás un archivo llamado `.env` (si no lo ves, es porque está oculto, asegúrate de mostrar archivos ocultos). 
Allí deben estar tus contraseñas (como las credenciales SMTP para enviar correos o cualquier clave secreta).
> [!NOTE]
> Las variables de conexión a la base de datos (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD) se sobreescribirán de forma segura y automática gracias al archivo `docker-compose.yml`. No necesitas configurar un PostgreSQL manual en la nueva computadora, ¡Docker lo hará por ti!

### 3. Ejecutar Docker Compose
Abre una terminal (Símbolo del sistema o PowerShell) dentro de la carpeta del proyecto `MediQQTA` en la nueva computadora y ejecuta este comando:

```bash
docker-compose up --build -d
```

**¿Qué hace este comando?**
- `--build`: Le dice a Docker que lea tu código, instale Python 3.12 (compatible con 3.14+ LTS), Node.js, e instale las librerías de `requirements.txt`.
- `-d`: Significa "Detached", es decir, el sistema correrá silenciosamente en segundo plano sin bloquear tu terminal.

*Nota: La primera vez tardará un par de minutos porque debe descargar las imágenes (Python y PostgreSQL) desde internet. Las siguientes veces iniciará en segundos.*

### 4. Aplicar Migraciones (Solo la primera vez)
Como es un contenedor nuevo, la base de datos PostgreSQL estará completamente vacía. Para crear las tablas, ejecuta:

```bash
docker-compose exec web python manage.py migrate
```

### 5. Crear el Súper Usuario (Administrador)
Para poder iniciar sesión por primera vez:

```bash
docker-compose exec web python manage.py createsuperuser
```
(Te pedirá un usuario, correo y contraseña. Recuerda que la contraseña no se ve al escribirla).

### 6. ¡Listo para usar!
Abre tu navegador y entra a:
[http://localhost:8000](http://localhost:8000)

## Comandos Útiles

- **Para apagar el sistema:**
  ```bash
  docker-compose down
  ```
- **Para ver los logs (si hay algún error):**
  ```bash
  docker-compose logs -f web
  ```
- **Para compilar estilos de Tailwind manualmente (si haces cambios en el HTML):**
  ```bash
  docker-compose exec web python manage.py tailwind build
  ```
