# Respuestas Clase 5

## ¿Qué backend de caché usa Django por defecto?

Si no se configura la variable CACHES en settings.py, Django usa **LocMemCache**
(caché en memoria local). Guarda los datos en la memoria RAM del proceso de Python
que está corriendo el servidor.

## ¿Por qué en producción conviene reemplazarlo por Redis?

En producción no corre un solo proceso, sino varios (varios workers de gunicorn, o
varios servidores). Con LocMemCache eso trae problemas:

- **Cada proceso tiene su propia caché, aislada de las demás.** Un worker puede haber
  guardado los feriados de 2026 y otro no, así que el segundo vuelve a llamar a la API
  externa. Se pierde buena parte del beneficio de la caché.
- **Datos inconsistentes entre procesos.** Un proceso puede tener un valor viejo y
  otro uno nuevo, y la respuesta depende de a qué worker le toque la petición.
- **Se pierde al reiniciar.** Está en la RAM del proceso: si el servidor se reinicia
  o se redespliega, la caché empieza vacía.
- **Consume la memoria de cada proceso** y se duplica en cada uno.

Redis es un servidor de caché **aparte**, al que todos los procesos se conectan:

- Todos comparten la misma caché, así que hay una sola llamada a la API externa por
  día sin importar cuántos workers haya.
- Los datos son consistentes para todos.
- No depende del ciclo de vida de los procesos de Django, y puede configurarse para
  persistir en disco.
- Soporta vencimientos (TTL) y está pensado para este uso.

En Django se cambia solo con configuración en CACHES; el código de HolidayService
(cache.get / cache.set) no hay que tocarlo.