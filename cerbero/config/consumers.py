from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import json

class ButtonStateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Unirse al grupo de WebSocket
        await self.channel_layer.group_add('button_state_group', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo de WebSocket
        await self.channel_layer.group_discard('button_state_group', self.channel_name)

    async def send_button_state(self, event):
        # Enviar el estado del botón a todos los clientes conectados
        print(event)
        await self.send(text_data=json.dumps(event))

    async def receive(self, text_data):
        # No se utiliza en este caso, pero debe ser implementado
        pass