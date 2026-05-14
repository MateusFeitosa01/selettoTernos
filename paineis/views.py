from django.shortcuts import render
from django.db.models import Q
from filas.models import Senha


def adminSeletto(request):
    """
    View para o painel administrativo com dados reais do banco.
    """
    senha_atual = Senha.objects.select_related('categoria').filter(
        status='EM_ATENDENDO'
    ).first()

    fila = Senha.objects.select_related('categoria').filter(
        Q(status='AGUARDANDO') | Q(status='EM_ATENDENDO')
    ).order_by(
        '-categoria__peso',
        'criada_em'
    )

    context = {
        'titulo': 'Painel Administrativo',
        'usuario': 'Admin',
        'aguardando': Senha.objects.filter(status='AGUARDANDO').count(),
        'em_atendimento': Senha.objects.filter(status='EM_ATENDENDO').count(),
        'atendidos': Senha.objects.filter(status='FINALIZADO').count(),
        'senha_atual': senha_atual,
        'fila': fila,
    }
    return render(request, 'adminSeletto/dashboard.html', context)


def display(request):
    """
    View para o display de senhas usando dados reais.
    """
    senha_atual_obj = Senha.objects.filter(
        status='EM_ATENDENDO'
    ).select_related('categoria').first()

    if senha_atual_obj:
        senha_atual = {
            'codigo': senha_atual_obj.codigo,
            'tipo': senha_atual_obj.categoria.nome,
            'cliente_nome': senha_atual_obj.cliente_nome,
        }
    else:
        senha_atual = None

    proximas_senhas = [
        {
            'codigo': senha.codigo,
            'tipo': senha.categoria.nome,
            'cliente_nome': senha.cliente_nome,
            'status': senha.status or 'AGUARDANDO',
        }
        for senha in Senha.objects.filter(status='AGUARDANDO').select_related('categoria').order_by(
            '-categoria__peso',
            'criada_em'
        )[:10]
    ]

    context = {
        'senha_atual': senha_atual,
        'proximas_senhas': proximas_senhas,
    }

    return render(request, 'display/painel_fila.html', context)

