from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
import logging

from accounts.models import User
from filas.models import Senha
from atendimentos.models import Atendimento

logger = logging.getLogger(__name__)


def chamar_proxima_senha():

    # Consulta todos os funcionários ativos em ordem previsível
    todos_funcionarios = list(User.objects.filter(tipo_usuario='funcionario', is_active=True).order_by('first_name', 'username'))

    if not todos_funcionarios:
        logger.info('Nenhum funcionário cadastrado para chamar a próxima senha.')
        return

    # Funcionários livres (não têm atendimento ativo)
    funcionarios_livres = list(
        User.objects.filter(tipo_usuario='funcionario', is_active=True)
        .exclude(atendimentos__ativo=True)
        .order_by('first_name', 'username')
        .distinct()
    )

    if not funcionarios_livres:
        logger.info('Nenhum funcionário livre no momento para chamar a próxima senha.')
        return

    # Se só houver um livre, mantém comportamento atual
    if len(funcionarios_livres) == 1:
        funcionario_livre = funcionarios_livres[0]

    else:
        cache_key = 'chamar_proxima_last_funcionario'
        data = cache.get(cache_key, {}) or {}
        last_id = data.get('id')
        last_date = data.get('date')
        hoje = str(timezone.localdate())

        # Resetar sequência em novo dia
        if last_date != hoje:
            last_id = None

        ids = [u.id for u in todos_funcionarios]
        livres_ids = {u.id for u in funcionarios_livres}

        if last_id and last_id in ids:
            start_index = (ids.index(last_id) + 1) % len(ids)
        else:
            start_index = 0

        funcionario_livre = None
        for offset in range(len(ids)):
            index = (start_index + offset) % len(ids)
            candidato = todos_funcionarios[index]
            if candidato.id in livres_ids:
                funcionario_livre = candidato
                break

        if not funcionario_livre:
            funcionario_livre = funcionarios_livres[0]

        # salvar último escolhido (para o próximo ciclo)
        cache.set(cache_key, {'id': funcionario_livre.id, 'date': hoje}, timeout=24 * 3600)

    logger.debug('Funcionários livres: %s', [u.id for u in funcionarios_livres])
    logger.info('Funcionário escolhido: %s (id=%s)', funcionario_livre.first_name, funcionario_livre.id)

    # Busca próxima senha aguardando
    senha = Senha.objects.filter(
        status='AGUARDANDO'
    ).order_by(
        '-categoria__peso',
        'criada_em'
    ).first()

    if not senha:
        logger.debug('Nenhuma senha aguardando encontrada.')
        return

    # Marca atendimento
    senha.status = 'EM_ATENDIMENTO'
    senha.atendente = funcionario_livre.first_name
    senha.chamada_em = timezone.now()
    senha.save()

    Atendimento.objects.create(
        senha=senha,
        atendente=funcionario_livre,
        ativo=True
    )

    logger.info('Senha %s atribuída automaticamente ao atendente %s (id=%s).', senha.codigo, funcionario_livre.first_name, funcionario_livre.id)
