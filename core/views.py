from django.shortcuts import render, redirect
from .forms import ClienteForm


def index(request):
    return render(request, 'home/index.html')




def display(request):

    #apenas teste para aparecer senha e tipo no frontend
    teste = {
        'senha' : 'PN001',
        'tipo' : 'Prova Noivo'
    }

    return render(request, 'display/painel_fila.html', teste)


def adminSeletto(request):
    return render(request, 'adminSeletto/dashboard.html')


def totem(request):
    return render(request, 'totem/escolha_atendimento.html')

def formulario_cliente(request, tipo):

    if request.method == 'POST':

        form = ClienteForm(request.POST)

        if form.is_valid():

            request.session['tipo_atendimento'] = tipo
            request.session['nome'] = form.cleaned_data['nome']
            request.session['email'] = form.cleaned_data['email']
            request.session['whatsapp'] = form.cleaned_data['whatsapp']

            return redirect('senhaGerada')

    else:
        form = ClienteForm()

    return render(request, 'totem/dados_cliente.html', {
        'form': form,
        'tipo': tipo
    })

def senhaGerada(request):
    
    nome = request.session.get('nome')
    tipo = request.session.get('tipo_atendimento')

    return render(request, 'totem/senha_gerada.html', {
        'nome': nome,
        'tipo': tipo
    })