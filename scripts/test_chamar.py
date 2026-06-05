import os
import sys
from pathlib import Path
import django
import logging

# garantir que o diretório do projeto esteja no sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selettoTernos.settings')
django.setup()

from django.utils import timezone
from django.core.cache import cache
from accounts.models import User
from filas.models import Senha
from atendimentos.models import Atendimento
from core.utils import chamar_proxima_senha

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

print('===== INICIO TESTE CHAMAR =====')

todos = list(User.objects.filter(tipo_usuario='funcionario', is_active=True).order_by('first_name','username'))
print('Todos funcionarios (ids):', [ (u.id, u.first_name, u.username) for u in todos ])

livres = list(User.objects.filter(tipo_usuario='funcionario', is_active=True).exclude(atendimentos__ativo=True).order_by('first_name','username').distinct())
print('Funcionarios livres (ids):', [ (u.id, u.first_name, u.username) for u in livres ])

aguardando = list(Senha.objects.filter(status='AGUARDANDO').order_by('-categoria__peso','criada_em'))
print('Senhas aguardando:', [ (s.id, s.codigo) for s in aguardando ])

cache_key = 'chamar_proxima_last_funcionario'
print('Cache antes:', cache.get(cache_key))

print('\nChamando chamar_proxima_senha()...')
chamar_proxima_senha()

print('\nCache depois:', cache.get(cache_key))

em_atendimento = list(Senha.objects.filter(status='EM_ATENDIMENTO').order_by('chamada_em'))
print('Senhas em atendimento:', [ (s.id, s.codigo, s.atendente) for s in em_atendimento ])

ult_att = Atendimento.objects.order_by('-iniciado_em').first()
if ult_att:
    print('Ultimo Atendimento:', ult_att.id, ult_att.senha.codigo, ult_att.atendente.id, ult_att.atendente.first_name, 'ativo=', ult_att.ativo)
else:
    print('Nenhum atendimento criado ainda')

print('===== FIM TESTE CHAMAR =====')
