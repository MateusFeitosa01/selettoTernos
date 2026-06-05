import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selettoTernos.settings')

import django
django.setup()

from accounts.models import User
from atendimentos.models import Atendimento
from filas.models import Senha

print('FUNCIONARIOS ATIVOS:')
for u in User.objects.filter(tipo_usuario='funcionario', is_active=True).order_by('first_name', 'username'):
    busy = Atendimento.objects.filter(atendente=u, ativo=True).exists()
    print(' ', u.id, u.first_name, u.username, 'busy' if busy else 'free')

print('\nATENDIMENTOS ATIVOS:')
for a in Atendimento.objects.filter(ativo=True).select_related('senha', 'atendente'):
    print(' ', a.id, a.senha.codigo, a.atendente.first_name, a.atendente.username)

print('\nSENHAS AGUARDANDO:')
for s in Senha.objects.filter(status='AGUARDANDO').order_by('-categoria__peso', 'criada_em'):
    print(' ', s.id, s.codigo, s.categoria.nome)
