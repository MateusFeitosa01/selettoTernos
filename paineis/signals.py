from asgiref.sync import async_to_sync

from channels.layers import get_channel_layer

from django.db.models.signals import post_save
from django.dispatch import receiver

from filas.models import Senha
from atendimentos.models import Atendimento

@receiver(post_save, sender=Senha)
def atualizar_painel(sender,instance,**kwargs):
    
    if instance.status != 'CHAMADO':
        return

    atendimento = Atendimento.objects.select_related(
        'atendente'
    ).filter(
        senha=instance
    ).first()

    if not atendimento:
        return

    channel_layer = get_channel_layer()

    async_to_sync(
        channel_layer.group_send
    )(
        'painel_fila',
        {
            'type': 'receber_chamada',
            'senha': instance.codigo,
            'atendente': atendimento.atendente.username,
        }
    )