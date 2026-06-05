import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selettoTernos.settings')

import django
from django.utils import timezone

django.setup()

from atendimentos.models import Atendimento
from filas.models import Senha

ativos = list(Atendimento.objects.filter(ativo=True).select_related('senha'))
print(f'Atendimentos ativos encontrados: {len(ativos)}')
for atendimento in ativos:
    atendimento.ativo = False
    atendimento.finalizado_em = timezone.now()
    atendimento.save()

    senha = atendimento.senha
    if senha.status == 'EM_ATENDIMENTO':
        senha.status = 'FINALIZADO'
        senha.finalizado_em = timezone.now()
        senha.save()

print(f'Total de atendimentos encerrados: {len(ativos)}')
