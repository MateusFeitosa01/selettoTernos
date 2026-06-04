from django.db import transaction
from django.utils import timezone

from accounts.models import User
from filas.models import Senha
from atendimentos.models import Atendimento


def chamar_proxima_senha():

    funcionario_livre = User.objects.filter(
        tipo_usuario='funcionario',
        is_active=True
    ).exclude(
        atendimentos__ativo=True
    ).first()

    if not funcionario_livre:
        return

    senha = Senha.objects.filter(
        status='AGUARDANDO'
    ).order_by(
        '-categoria__peso',
        'criada_em'
    ).first()

    if not senha:
        return

    senha.status = 'EM_ATENDIMENTO'
    senha.atendente = funcionario_livre.first_name
    senha.chamada_em = timezone.now()
    senha.save()

    Atendimento.objects.create(
        senha=senha,
        atendente=funcionario_livre,
        ativo=True
    )
