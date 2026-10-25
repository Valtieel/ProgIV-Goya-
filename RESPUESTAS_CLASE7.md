# Respuestas Clase 7

## 1. Acción add_member en ProjectViewSet

Se agregó en ProjectViewSet una acción `add_member` (POST /api/projects/<id>/add_member/)
que recibe {"username": "...", "role": "miembro"} y crea la membresía.

- Como es `detail=True` y usa `self.get_object()`, el permiso IsProjectAdminOrReadOnly
  ya verifica el rol: como es un POST, solo un admin del proyecto puede usarla.
- Si el usuario que llama no es miembro del proyecto, responde 404 (el proyecto no
  existe para él). Si es miembro pero no admin, responde 403.
- Si el username no existe, responde 404.
- Si el usuario ya es miembro, responde 400.
- Si no viene el username o el rol no es "admin" ni "miembro", responde 400.
- El rol por defecto es "miembro", por el principio de mínimo privilegio.

Se probó con un script y todos los casos dieron el código esperado (404, 403, 201,
400, 404, 400, 400), y después de agregarla, ana pudo ver el proyecto.

## 2. Flujo de OAuth (Authorization Code) con Google

Navegador = pasos que ocurren en el navegador del usuario.
Servidor a servidor = pasos entre TaskFlow y Google, sin pasar por el navegador.

1. [Navegador] El usuario hace clic en "Ingresar con Google" en TaskFlow.
2. [Navegador] TaskFlow redirige al usuario a Google, con client_id, redirect_uri,
   scope (qué datos pide: profile y email) y state (un valor aleatorio).
3. [Navegador] El usuario inicia sesión en Google y acepta compartir sus datos
   (consentimiento). Nunca le da su contraseña a TaskFlow.
4. [Navegador] Google redirige al usuario de vuelta a la redirect_uri de TaskFlow,
   con un código de autorización (code) de un solo uso y el state en la URL.
5. [Navegador] El navegador entrega ese code y ese state a TaskFlow.
6. [Servidor a servidor] TaskFlow verifica que el state sea el que generó y le manda
   a Google el code junto con su client_secret, que nunca pasa por el navegador.
7. [Servidor a servidor] Google devuelve los tokens, entre ellos el ID token (un JWT
   con la identidad del usuario).
8. [Servidor a servidor / TaskFlow] TaskFlow lee los datos del usuario del ID token,
   lo busca o lo crea en su base y lo deja logueado. Después, la vista
   SocialLoginJWTView le entrega un par de JWT propios.

### Por qué los tokens no viajan por el navegador

El code viaja por el navegador, pero es de un solo uso y de vida corta, y solo sirve
combinado con el client_secret, que conoce únicamente el servidor. Así, aunque alguien
viera la URL del paso 4, no podría canjearlo por tokens.

### Para qué sirven redirect_uri, state y scope

- redirect_uri: tiene que estar registrada de antemano en Google, para que un atacante
  no pueda pedir que el code se mande a su propio sitio.
- state: valor aleatorio que TaskFlow genera y verifica a la vuelta. Protege contra
  que un atacante inyecte su propio código en la sesión del usuario (tipo CSRF).
- scope: define qué datos se piden (acá profile y email). Es el mínimo privilegio
  aplicado a OAuth.

### OAuth vs. OpenID Connect

OAuth 2.0 es un protocolo de autorización (dar acceso a datos). OpenID Connect es una
capa encima, pensada para autenticación ("decime quién es este usuario"): agrega el
ID token. Cuando una app ofrece "Ingresar con Google", usa OpenID Connect.