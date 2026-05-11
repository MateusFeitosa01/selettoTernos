from django.shortcuts import render, redirect
from django.contrib import messages


def adminSeletto(request):
    """
    View para o painel administrativo.
    Em produção, incluiria lógica de autenticação e dados reais.
    """
    context = {
        'titulo': 'Painel Administrativo',
        'usuario': 'Admin',  # Em produção, viria da sessão
    }
    return render(request, 'adminSeletto/dashboard.html', context)


def display(request):
    """
    View para o display de senhas.
    Mostra a senha atual e próximas na fila.
    """
    context = {
        'senha': 'PR001',
        'tipo': 'Prova Noivo',
        'proximas_senhas': [
            {'senha': 'PR002', 'tipo': 'Locar Terno', 'status': 'Aguardando'},
            {'senha': 'PR003', 'tipo': 'Prova', 'status': 'Aguardando'},
            {'senha': 'PR004', 'tipo': 'Retrabalho', 'status': 'Aguardando'},
        ]
    }
    return render(request, 'display/painel_fila.html', context)

