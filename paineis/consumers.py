import json 

from channels.generic.websocket import AsyncWebsocketConsumer

class PainelConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add(
            'painel_fila',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'painel_fila',
            self.channel_name
        )
    
    async def receber_chamada(self, event):
        await self.send(
            text_data=json.dumps({
                'senha': event['senha'],
                'atendente': event['atendente'],
            })
        )