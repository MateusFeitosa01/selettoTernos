import json 

from channels.generic.websocket import AsyncWebsocketConsumer

class PainelConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()
            return
        if user.tipo_usuario not in ['tv', 'admin', 'funcionario']:
            await self.close()
            return
        
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