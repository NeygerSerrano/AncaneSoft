# Funcionalidades del Sistema ODONTOQQTA por Rol de Usuario

**Proyecto:** Sistema de Agendamiento de Citas — ODONTOQQTA
**Fuente:** Casos de Uso, Historias de Usuario (HU) y Requerimientos Funcionales/No Funcionales del proyecto.

El sistema define **tres roles de usuario**, cada uno con permisos y alcances de información distintos (RF-11): **Secretaria** (lectura/escritura completa), **Doctora** (gestión de agenda propia y reportes) y **Recepcionista** (lectura restringida, sin datos clínicos ni de contacto).

---

## 1. Rol: Secretaria

Responsable de la gestión operativa completa de la agenda y de los pacientes.

| # | Funcionalidad | Descripción | Referencias |
|---|---|---|---|
| 1 | **Agendar cita de paciente** | Consulta la disponibilidad de la agenda y registra una nueva cita usando el número de documento del paciente. Si el paciente ya existe, el sistema autocompleta sus datos; si es nuevo, habilita el registro. | CU-01, HU-SEC-01 |
| 2 | **Consultar horarios disponibles** | Visualiza los horarios libres y ocupados para una fecha determinada antes de agendar, evitando conflictos. | HU-SEC-02 |
| 3 | **Validación automática de disponibilidad** | Al confirmar una cita, el sistema valida en tiempo real que el horario siga libre, evitando doble agendamiento. | CU-01 (FA-01), HU-SEC-03, RF-04 |
| 4 | **Registrar paciente nuevo** | Si el número de documento no está registrado, ingresa los datos del nuevo paciente durante el agendamiento. | CU-01, HU-SEC-01, RF-01 |
| 5 | **Autocompletado de datos de paciente existente** | Al ingresar el documento de un paciente ya registrado, el sistema completa automáticamente su información. | CU-01, HU-SEC-01, RF-02 |
| 6 | **Cancelar cita** | Cancela una cita previamente agendada, registrando obligatoriamente el motivo de cancelación, y libera el horario en la agenda. | CU-02, HU-SEC-05, RF-05 |
| 7 | **Aplazar / reagendar cita** | Modifica la fecha y hora de una cita existente, conservando el historial del cambio y liberando el horario original. | CU-03, HU-SEC-06, RF-06 |
| 8 | **Consultar agenda general** | Visualiza las citas programadas en vista diaria, semanal o mensual, con filtros por estado (Programada, Cancelada, Aplazada, etc.). | CU-07, HU-SEC-04, RF-09 |
| 9 | **Consultar historial de paciente** | Busca a un paciente por documento o nombre y visualiza su historial completo de citas (pasadas y futuras) con su estado. | CU-08, HU-SEC-07, RF-08 |

---

## 2. Rol: Doctora

Responsable de gestionar la disponibilidad de su propia agenda y de obtener información estadística de su actividad.

| # | Funcionalidad | Descripción | Referencias |
|---|---|---|---|
| 1 | **Bloquear disponibilidad en agenda** | Marca horarios específicos o días completos como "No disponible" para evitar que la Secretaria agende citas en esos espacios (reuniones, descansos, imprevistos). | CU-04, HU-DOC-02, RF-07 |
| 2 | **Bloquear día completo** | Bloquea una jornada entera de una sola vez (ej. vacaciones, congresos), deshabilitando todas las horas del día para agendamiento. | HU-DOC-02 |
| 3 | **Desbloquear horario** | Elimina un bloqueo previamente creado, liberando el horario para que la Secretaria pueda volver a agendar. | HU-DOC-02 |
| 4 | **Consultar agenda propia** | Visualiza las citas del día, fechas futuras y su estado, para conocer los pacientes que debe atender. | HU-DOC-01, CU-07 |
| 5 | **Generar reporte mensual de citas** | Genera un informe estadístico de las citas del mes (atendidas, canceladas, etc.) para evaluar su volumen de trabajo. | CU-05, HU-DOC-03, RF-10 |
| 6 | **Filtrar reporte por estado** | Aplica filtros sobre el reporte generado (ej. "solo canceladas") para un análisis más específico. | HU-DOC-03 |
| 7 | **Exportar reporte** | Descarga el reporte de citas en formato estándar (PDF o Excel) para uso contable o administrativo. | HU-DOC-03, RF-10, RNF-03 |

---

## 3. Rol: Recepcionista

Rol de solo lectura con acceso restringido, orientado a controlar la llegada de pacientes sin exponer información sensible.

| # | Funcionalidad | Descripción | Referencias |
|---|---|---|---|
| 1 | **Monitorear agenda diaria** | Visualiza el calendario del día actual, organizado cronológicamente, para saber qué pacientes llegarán y a qué hora. | CU-06, HU-REC-01 |
| 2 | **Ver detalle restringido de cita** | Al hacer clic o pasar el cursor sobre una cita, visualiza únicamente el nombre completo del paciente y la hora (inicio/fin), sin acceso a datos clínicos, teléfono o motivo de consulta. | CU-06, HU-REC-02, RNF-01 |
| 3 | **Navegar entre fechas** | Usa los controles del calendario para consultar la agenda de otros días (anteriores o siguientes). | HU-REC-01 |
| 4 | **Actualización en tiempo real** | La vista se actualiza automáticamente (sin recargar la página) cuando la Secretaria agenda una cita de último momento para el día en curso. | CU-06 (FA-02), HU-REC-01, RNF-02 |

---

## 4. Funcionalidad compartida entre roles

| # | Funcionalidad | Roles que aplica | Descripción | Referencias |
|---|---|---|---|---|
| 1 | **Consultar agenda con vistas y filtros** | Secretaria, Doctora | Ambos roles pueden alternar entre vista diaria, semanal y mensual, y filtrar las citas por estado. | CU-07, RF-09 |
| 2 | **Inicio de sesión** | Secretaria, Doctora, Recepcionista | Todos los roles requieren autenticación previa para acceder a sus funcionalidades correspondientes. | Precondiciones CU-01, CU-04, CU-06 |

---

## 5. Resumen de control de acceso por rol (RF-11 / RNF-01)

| Rol | Nivel de acceso | Datos visibles |
|---|---|---|
| **Secretaria** | Lectura y escritura completa | Todos los datos del paciente y de la cita (documento, contacto, motivo de consulta, historial) |
| **Doctora** | Gestión de agenda propia + reportes | Citas propias, bloqueos de horario, estadísticas y reportes |
| **Recepcionista** | Lectura restringida | Únicamente nombre completo del paciente y hora de la cita; sin datos clínicos, teléfono ni motivo de consulta |
