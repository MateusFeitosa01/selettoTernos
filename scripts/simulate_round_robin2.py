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
from core.utils import chamar_proxima_senha
from django.utils import timezone
from django.core.cache import cache

cache_key = 'chamar_proxima_last_funcionario'
old_cache = cache.get(cache_key)
attendance = Atendimento.objects.filter(ativo=True, atendente__tipo_usuario='funcionario').select_related('atendente').first()
print('attendance', attendance.id, attendance.senha.codigo, attendance.atendente.first_name)
attendance.ativo = False
attendance.finalizado_em = timezone.now()
attendance.save()

print('employees free now:')
for u in User.objects.filter(tipo_usuario='funcionario', is_active=True).order_by('first_name','username'):
    busy = Atendimento.objects.filter(atendente=u, ativo=True).exists()
    print(' ', u.id, u.first_name, busy)

print('calling 1')
chamar_proxima_senha()
print('cache after 1', cache.get(cache_key))
for a in Atendimento.objects.filter(ativo=True).select_related('senha','atendente'):
    print(' ', a.id, a.senha.codigo, a.atendente.first_name)

print('calling 2')
chamar_proxima_senha()
print('cache after 2', cache.get(cache_key))
for a in Atendimento.objects.filter(ativo=True).select_related('senha','atendente'):
    print(' ', a.id, a.senha.codigo, a.atendente.first_name)

attendance.ativo = True
attendance.finalizado_em = None
attendance.save()
print('reverted, cache before revert', cache.get(cache_key))
if old_cache is None:
    cache.delete(cache_key)
else:
    cache.set(cache_key, old_cache)
print('cache reverted', cache.get(cache_key))
