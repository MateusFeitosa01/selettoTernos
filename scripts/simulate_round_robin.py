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

# Save cache state
cache_key = 'chamar_proxima_last_funcionario'
old_cache = cache.get(cache_key)

# Find one active attendance for an employee
attendance = Atendimento.objects.filter(ativo=True, atendente__tipo_usuario='funcionario').select_related('atendente').first()
if not attendance:
    print('No active attendance for funcionario found')
    sys.exit(1)

print('Simulating finalization for attendance:', attendance.id, attendance.senha.codigo, attendance.atendente.first_name)
attendance.ativo = False
attendance.finalizado_em = timezone.now()
attendance.save()

print('Employees free now:')
for u in User.objects.filter(tipo_usuario='funcionario', is_active=True).order_by('first_name','username'):
    busy = Atendimento.objects.filter(atendente=u, ativo=True).exists()
    print(' ', u.id, u.first_name, busy)

print('Calling chamar_proxima_senha...')
chamar_proxima_senha()
print('Done. last cache:', cache.get(cache_key))
print('New active attendances:')
for a in Atendimento.objects.filter(ativo=True).select_related('senha', 'atendente'):
    print(' ', a.id, a.senha.codigo, a.atendente.first_name)

# revert the attendance
attendance.ativo = True
attendance.finalizado_em = None
attendance.save()
print('State reverted.')
if old_cache is None:
    cache.delete(cache_key)
else:
    cache.set(cache_key, old_cache)
print('Cache reverted to', cache.get(cache_key))
