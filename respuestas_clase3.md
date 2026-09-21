# Clase 3 - Tarea 2: select_related vs prefetch_related

## ¿Qué son?

Ambos son optimizaciones del ORM de Django para evitar el problema de
"N+1 queries": sin ellos, Django ejecuta una consulta SQL adicional por
cada fila de una lista para traer sus relaciones, en vez de traerlas todas
de una vez.

## select_related

Se usa en relaciones donde "del otro lado hay uno solo": ForeignKey y
OneToOneField. En nuestro proyecto, el ejemplo es `Task.project` (cada
tarea pertenece a un único proyecto).

Internamente genera un **JOIN en SQL**: en una sola consulta, la base de
datos une la tabla Task con la tabla Project y trae ambos datos juntos.

Ejemplo de uso:
```python
Task.objects.select_related("project").all()
```

## prefetch_related

Se usa en relaciones donde "del otro lado puede haber varios": ManyToMany
o ForeignKey inverso (related_name). En nuestro proyecto, el ejemplo es
`Task.tags` (una tarea puede tener varios tags).

Acá Django **no puede usar un solo JOIN** sin duplicar filas (si una tarea
tiene 3 tags, un JOIN directo generaría 3 filas repetidas de esa misma
tarea). En cambio, `prefetch_related` ejecuta una **consulta SQL separada**
por cada relación, trae todos los objetos relacionados de una vez, y los
une con el resultado original en Python (en memoria), no en la base de
datos.

Ejemplo de uso:
```python
Task.objects.prefetch_related("tags").all()
```
