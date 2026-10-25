import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Project


class TaskNotificationConsumer(AsyncWebsocketConsumer):
    # Un consumer es como una vista, pero para WebSocket: vive mientras la conexión
    # esté abierta (puede ser horas), no solo lo que dura una petición.

    async def connect(self):
        # self.scope es un diccionario con los datos de la conexión (como el request).
        # project_id viene de la URL, la capturamos en routing.py.
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        self.group_name = f"project_{self.project_id}"

        # El ORM es sincrónico: llamarlo directo desde un async def bloquearía el bucle
        # de eventos y todas las conexiones quedarían esperando. database_sync_to_async
        # lo ejecuta en otro hilo. Ojo con los paréntesis: se envuelve el método
        # (sin llamarlo) y después se llama al resultado.
        existe = await database_sync_to_async(
            Project.objects.filter(id=self.project_id).exists
        )()

        if not existe:
            # Cerramos antes de accept(): el cliente recibe el rechazo del handshake
            await self.close()
            return

        # Nos anotamos en el grupo del proyecto (se profundiza en la Clase 10).
        # channel_name es la "casilla" única que Channels le asigna a cada conexión.
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # Sin accept() la conexión queda pendiente y el cliente nunca llega a conectarse
        await self.accept()

    async def disconnect(self, close_code):
        # Se ejecuta al cerrarse la conexión, por cualquier motivo. Si connect() rechazó
        # antes de anotarnos en el grupo, group_discard simplemente no encuentra nada.
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Se ejecuta por cada mensaje que manda el cliente
        data = json.loads(text_data)
        # Por ahora hacemos "echo": devolvemos el mismo mensaje, a modo de prueba
        await self.send(text_data=json.dumps({"echo": data}))

    async def task_notification(self, event):
        # Todavía no se usa: Channels lo va a llamar en la Clase 10,
        # cuando alguien publique un mensaje en el grupo
        await self.send(text_data=json.dumps(event["payload"]))