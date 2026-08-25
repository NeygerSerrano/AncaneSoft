# AncaneSoft (MediQQTA)
Sistema Integral de Agendamiento Médico y Administración de Clínicas

## 📋 Descripción del Proyecto
AncaneSoft es una plataforma web desarrollada a la medida para la gestión automatizada y eficiente de citas médicas. El sistema fue diseñado bajo una arquitectura que permite adaptar los correos electrónicos a la identidad corporativa de múltiples clínicas.

## 🚀 Funcionalidades Principales
* **Gestión de Citas Interactiva:** Calendario visual (FullCalendar) con opciones para agendar, cancelar, reagendar y marcar citas como atendidas.
* **Autocompletado de Pacientes:** Búsqueda en tiempo real por número de documento que permite llenar automáticamente los formularios o registrar pacientes nuevos en un solo paso.
* **Bloqueos de Agenda:** Opción para que el personal médico bloquee franjas horarias por permisos o emergencias de forma rápida (botón flotante).
* **Personalización Dinámica (Branding):** Panel de configuración para cambiar logos, colores primarios y colores secundarios del sistema, afectando la interfaz y los correos enviados.
* **Recuperación de Contraseña Segura:** Sistema de validación por token numérico de 6 dígitos enviado por correo electrónico (con expiración de 15 minutos).
* **Correos Asíncronos:** Sistema de hilos de ejecución en segundo plano (`threading`) para el envío de confirmaciones, recordatorios y alertas a pacientes sin congelar la pantalla.
* **Reportes Gerenciales:** Generación de estadísticas y exportación de datos en formato Excel (`.xlsx`).
* **Auditoría Transparente:** Rastreo automático de las acciones críticas (Crear, Cancelar, Atender citas) guardadas en base de datos.

## 🛠️ Tecnologías y Stack
* **Lenguaje:** Python 3
* **Framework Backend:** Django 6.0+
* **Base de Datos:** PostgreSQL
* **Estilos y Frontend:** HTML5, JavaScript ES6, Tailwind CSS
* **Librerías Adicionales:** 
  * `Pillow` (Manejo de imágenes y logos)
  * `openpyxl` (Exportación a Excel)
  * `FullCalendar.js` (Librería JS de calendario)

## 👤 Roles de Sistema
1. **Superadministrador:** Acceso completo al branding de la empresa (Colores y Nombres) y gestión de usuarios.
2. **Secretaria:** Gestión total de la agenda, pacientes y capacidad de modificar el Logo en los correos.
3. **Recepcionista:** Apoyo en visualizar estados de las citas del día.
4. **Doctora / Especialista:** Vista de su propia agenda y control para bloquear franjas horarias.

## ⚙️ Requisitos para Entorno de Desarrollo Local
Para hacer correr este proyecto en local, debes tener Python y PostgreSQL instalados.

1. Clona el repositorio e ingresa a la carpeta del proyecto.
2. Crea e inicia un entorno virtual: `python -m venv venv`
3. Instala las dependencias: `pip install -r requirements.txt`
4. Asegúrate de tener una base de datos creada en tu motor de PostgreSQL.
5. Ejecuta las migraciones: `python manage.py migrate`
6. Levanta el servidor: `python manage.py runserver`
