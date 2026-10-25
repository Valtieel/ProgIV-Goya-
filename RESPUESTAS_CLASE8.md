# Respuestas Clase 8

## 1. Registrar los 403 en SecurityLog

En IsProjectAdminOrReadOnly, justo antes de devolver False en el caso de escritura,
se crea un SecurityLog con action="permission_denied", el usuario, el método y la
URL, y la IP. También se escribe en security.log con el logger "security".

Pregunta: ¿por qué un usuario que no es miembro nunca llega a ese punto?
Porque get_queryset filtra por membresía: para un no miembro, el proyecto o la tarea
no existe en el queryset, y get_object() responde 404 antes de que se evalúe
has_object_permission. Ese método solo corre para quienes ya pasaron el filtro de
visibilidad (los miembros). Así, un 404 no le confirma al atacante que el id existe.

## 2. CORS_ALLOWED_ORIGINS vs CORS_ALLOW_CREDENTIALS

- CORS_ALLOWED_ORIGINS: lista de orígenes (protocolo + dominio + puerto) cuyo
  JavaScript puede leer las respuestas de la API desde un navegador.
- CORS_ALLOW_CREDENTIALS: si es True, el servidor agrega el header
  Access-Control-Allow-Credentials: true, y el navegador puede incluir credenciales
  (cookies, autenticación HTTP) en las peticiones entre orígenes.

Se necesita cuando el frontend está en otro origen y la autenticación va por cookies
(por ejemplo, la sesión de Django, o un refresh token guardado en una cookie
HttpOnly), y el frontend hace fetch con credentials: "include".

No hace falta si el frontend manda el JWT en el header Authorization, que es lo que
hace TaskFlow hoy: ese header lo agrega el código de la página, no el navegador solo.

Cuidado: con credenciales no se puede usar un origen comodín; hay que listar
orígenes concretos. Y al volver a usar cookies reaparece el riesgo de CSRF, por eso
hay que mantener CsrfViewMiddleware y configurar CSRF_TRUSTED_ORIGINS.

## Auditoría OWASP del proyecto (ejercicio 1.2)

- Control de acceso: una tarea de un proyecto ajeno da 404; un miembro sin rol admin
  recibe 403 al modificar o borrar (probado con scripts).
- .env: está en .gitignore desde la Clase 1.
- Fuerza bruta: el login permite 5 intentos por minuto por IP; el sexto da 429.