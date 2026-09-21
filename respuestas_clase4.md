# Clase 4 - Tarea: códigos de estado HTTP probados con curl

## 1) 200 OK - GET exitoso

Comando:
curl -i http://127.0.0.1:8000/api/tasks/

Respuesta:
HTTP/1.1 200 OK
Content-Type: application/json

[{"id":1,"project":1,"title":"Arrancar", ... }, ...]

## 2) 201 Created - POST exitoso

Comando:
curl -i -X POST http://127.0.0.1:8000/api/tasks/ -H "Content-Type: application/json" -d "{\"project\": 1, \"title\": \"Tarea de prueba 201\"}"

Respuesta:
HTTP/1.1 201 Created
Content-Type: application/json

{"id":4,"project":1,"title":"Tarea de prueba 201","description":"","priority":"media","status":"pendiente","due_date":null,"tags":[],"created_at":"2026-09-21T20:28:18.027923Z"}

## 3) 204 No Content - DELETE exitoso

Comando:
curl -i -X DELETE http://127.0.0.1:8000/api/tasks/4/

Respuesta:
HTTP/1.1 204 No Content
Content-Length: 0

(body vacío, tal como indica la especificación)

## 4) 400 Bad Request - validación fallida

Comando (falta el campo obligatorio "title"):
curl -i -X POST http://127.0.0.1:8000/api/tasks/ -H "Content-Type: application/json" -d "{\"project\": 1}"

Respuesta:
HTTP/1.1 400 Bad Request
Content-Type: application/json

{"title":["This field is required."]}

También se probaron las validaciones de negocio personalizadas:

- Fecha límite en el pasado:
{"due_date": ["La fecha límite no puede ser en el pasado."]}

- Tarea completada sin fecha límite:
{"error":true,"detail":{"non_field_errors":["No se puede marcar una tarea como completada sin fecha límite registrada."]}}

- Tarea en progreso sin ninguna tarea completada en el proyecto:
{"error":true,"detail":{"non_field_errors":["No se puede poner una tarea en progreso si el proyecto no tiene ninguna tarea completada todavía."]}}

Nota: a partir de la activación del exception_handler personalizado, todas las
respuestas de error quedan envueltas en el formato {"error": true, "detail": ...}

## 5) 404 Not Found - recurso inexistente

Comando:
curl -i http://127.0.0.1:8000/api/tasks/999/

Respuesta:
HTTP/1.1 404 Not Found
Content-Type: application/json

{"detail": "No Task matches the given query."}

## 6) 401 Unauthorized / 403 Forbidden

No se probaron todavía porque el proyecto no tiene autenticación implementada
(se agrega en la Unidad 3). Por ahora todos los endpoints son públicos y
cualquiera puede leer, crear, editar o borrar tareas y proyectos sin loguearse.