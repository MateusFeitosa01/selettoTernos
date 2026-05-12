from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from filas.models import Categoria, Senha
from .forms import ClienteForm
from django.views import View
from django.shortcuts import redirect

class ChamarProximaView(View):
    def post(self, request):

        atendente = request.POST.get('atendente')

        if not atendente:
            return redirect('adminSeletto')

        # finaliza atendimento atual (se existir)
        Senha.objects.filter(
            status='EM_ATENDENDO'
        ).update(
            status='ATENDIDA',
            finalizado_em=timezone.now()
        )

        # pega próxima senha
        senha = Senha.objects.filter(
            status='AGUARDANDO'
        ).order_by(
            '-categoria__prioridade',
            'criada_em'
        ).first()

        if not senha:
            return redirect('adminSeletto')

        # atualiza senha atual
        senha.status = 'EM_ATENDENDO'
        senha.atendente = atendente
        senha.chamada_em = timezone.now()
        senha.save()

        return redirect('adminSeletto')

class PularSenhaView(View):
    def post(self, request):
        senha_atual = Senha.objects.filter(
            status='EM_ATENDENDO'
        ).first()

        if not senha_atual:
            return redirect('adminSeletto')

        # volta para fila
        senha_atual.status = 'AGUARDANDO'
        senha_atual.atendente = None
        senha_atual.chamada_em = None
        senha_atual.save()

        return redirect('adminSeletto')


class FinalizarSenhaView(View):
    def post(self, request):
        senha_atual = Senha.objects.filter(
            status='EM_ATENDENDO'
        ).first()

        if not senha_atual:
            return redirect('adminSeletto')

        # finaliza atendimento
        senha_atual.status = 'FINALIZADO'
        senha_atual.finalizado_em = timezone.now()
        senha_atual.save()

        return redirect('adminSeletto')

class HomeView(TemplateView):
    template_name = 'home/index.html'


class DisplayView(TemplateView):
    template_name = 'display/painel_fila.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Buscar senha atual sendo atendida
        senha_atual = Senha.objects.filter(
            status='EM_ATENDENDO'
        ).select_related('categoria').first()

        if senha_atual:
            context['senha_atual'] = {
                'codigo': senha_atual.codigo,
                'tipo': senha_atual.categoria.nome,
                'cliente_nome': senha_atual.cliente_nome,
            }
        else:
            context['senha_atual'] = None

        # Buscar próximas senhas na fila (aguardando)
        proximas_senhas = Senha.objects.filter(
            Q(status='AGUARDANDO') | Q(status__isnull=True)
        ).select_related('categoria').order_by(
            '-categoria__prioridade',  # Maior prioridade primeiro
            'criada_em'  # Depois por ordem de chegada
        )[:10]  # Limitar a 10 próximas

        context['proximas_senhas'] = [
            {
                'codigo': senha.codigo,
                'tipo': senha.categoria.nome,
                'cliente_nome': senha.cliente_nome,
                'status': senha.status or 'AGUARDANDO',
            }
            for senha in proximas_senhas
        ]

        return context


class AdminSelettoView(TemplateView):
    template_name = 'adminSeletto/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Contadores
        aguardando = Senha.objects.filter(status='AGUARDANDO').count()

        em_atendimento = Senha.objects.filter(
            status='EM_ATENDENDO'
        ).count()

        atendidos = Senha.objects.filter(
            status='FINALIZADO'
        ).count()

        # Atendimento atual
        senha_atual = Senha.objects.select_related(
            'categoria'
        ).filter(
            status='EM_ATENDENDO'
        ).first()

        # Fila
        fila = Senha.objects.select_related(
            'categoria'
        ).filter(
            Q(status='AGUARDANDO') |
            Q(status='EM_ATENDENDO')
        ).order_by(
            '-categoria__prioridade',
            'criada_em'
        )

        context.update({
            'aguardando': aguardando,
            'em_atendimento': em_atendimento,
            'atendidos': atendidos,
            'senha_atual': senha_atual,
            'fila': fila,
        })

        return context

class TotemView(TemplateView):
    template_name = 'totem/escolha_atendimento.html'


class DadosClienteView(FormView):
    template_name = 'totem/dados_cliente.html'
    form_class = ClienteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tipo = self.kwargs.get('tipo', '')
        # Converter tipo da URL para nome legível
        tipo_mapeamento = {
            'prova-noivo': 'Prova Noivo',
            'prioritario': 'Prioritário',
            'locar-terno': 'Locar Terno',
            'prova': 'Prova',
            'retrabalho': 'Retrabalho',
            'venda': 'Venda',
        }
        context['tipo'] = tipo_mapeamento.get(tipo, tipo.replace('-', ' ').title())
        return context

    def form_valid(self, form):
        tipo = self.kwargs.get('tipo', '')

        # Mapear tipo para categoria
        tipo_para_categoria = {
            'prova-noivo': 'Prova Noivo',
            'prioritario': 'Prioritário',
            'locar-terno': 'Locar Terno',
            'prova': 'Prova',
            'retrabalho': 'Retrabalho',
            'venda': 'Venda',
        }

        categoria_nome = tipo_para_categoria.get(tipo)
        if not categoria_nome:
            messages.error(self.request, 'Tipo de atendimento inválido.')
            return self.form_invalid(form)

        try:
            # Buscar categoria
            categoria = Categoria.objects.get(
                nome=categoria_nome,
                fila__ativa=True,
                ativa=True
            )
        except Categoria.DoesNotExist:
            messages.error(self.request, 'Categoria de atendimento não encontrada.')
            return self.form_invalid(form)

        # Gerar código único da senha
        hoje = timezone.now().date()
        prefixo = categoria_nome[:2].upper()  # PN, PR, LT, etc.

        # Contar senhas do dia para esta categoria
        senhas_hoje = Senha.objects.filter(
            categoria=categoria,
            criada_em__date=hoje
        ).count()

        numero = senhas_hoje + 1
        codigo = f"{prefixo}{numero:03d}"

        # Salvar senha no banco
        senha = Senha.objects.create(
            codigo=codigo,
            cliente_nome=form.cleaned_data['nome'],
            cliente_telefone=form.cleaned_data['whatsapp'],
            fila=categoria.fila,
            categoria=categoria,
        )

        # Adicionar senha ao contexto da sessão para o próximo view
        self.request.session['senha_gerada'] = {
            'codigo': senha.codigo,
            'tipo': categoria.nome,
            'nome': senha.cliente_nome,
        }

        messages.success(self.request, f'Senha {senha.codigo} gerada com sucesso!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('senha_gerada')


class SenhaGeradaView(TemplateView):
    template_name = 'totem/senha_gerada.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        senha_data = self.request.session.get('senha_gerada', {})
        context.update(senha_data)
        return context


class AcompanharFilaView(TemplateView):
    template_name = 'totem/acompanhar_fila.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Dados da sessão
        senha_session = self.request.session.get('senha_gerada')

        if not senha_session:
            return context

        try:
            senha = Senha.objects.select_related('categoria').filter(
            codigo=senha_session['codigo']
            ).order_by('-id').first()

            # Buscar todas as senhas aguardando da mesma categoria
            fila = Senha.objects.filter(
                categoria=senha.categoria,
                status='AGUARDANDO'
            ).order_by('criada_em')

            # Calcular posição
            posicao = 1

            for index, item in enumerate(fila, start=1):
                if item.id == senha.id:
                    posicao = index
                    break

            # Tempo estimado
            tempo_estimado = posicao * 5

            context.update({
                'senha': senha.codigo,
                'tipo': senha.categoria.nome,
                'posicao': posicao,
                'tempo_estimado': tempo_estimado,
            })

        except Senha.DoesNotExist:
            pass

        return context