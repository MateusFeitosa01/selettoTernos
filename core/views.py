from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.db import transaction, IntegrityError
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from filas.models import Categoria, Senha, ObservacaoAtendimento
from atendimentos.models import Atendimento
from .forms import ClienteForm
from django.views import View
from django.shortcuts import redirect, render
import qrcode
from io import BytesIO
from django.http import HttpResponse
from accounts.decorators import role_required
import logging 


logger = logging.getLogger(__name__)

@method_decorator(role_required('admin', 'funcionario', 'gerente'), name='dispatch')
class ChamarProximaView(View):
    def post(self, request):

        atendente = request.POST.get('atendente', '').strip()

        if not atendente:
            messages.error(request, 'Informe o nome do atendente.')
            return redirect('adminSeletto')


        with transaction.atomic():
            # pega próxima senha
            senha = Senha.objects.select_for_update().filter(
                status='AGUARDANDO'
            ).order_by(
                '-categoria__peso',
                'criada_em'
            ).first()

            if not senha:
                messages.info(request, 'Nenhuma senha aguardando no momento.')
                return redirect('adminSeletto')

            # atualiza senha atual
            senha.status = 'EM_ATENDIMENTO'
            senha.atendente = atendente
            senha.chamada_em = timezone.now()
            senha.save()

            Atendimento.objects.create(
                senha=senha,
                atendente=request.user
            )

        return redirect('adminSeletto')

from datetime import timedelta

@method_decorator(role_required('admin', 'funcionario', 'gerente'), name='dispatch')
class PularSenhaView(View):

    def post(self, request):

        senha_atual = Senha.objects.filter(
        status='EM_ATENDIMENTO'
        ).order_by('chamada_em').first()

        if not senha_atual:
            messages.warning(
                request,
                'Nenhum atendimento ativo encontrado.'
            )
            return redirect('adminSeletto')

        # fila da mesma prioridade/categoria
        fila = list(
            Senha.objects.filter(
                status='AGUARDANDO',
                categoria__peso=senha_atual.categoria.peso
            ).exclude(
                id=senha_atual.id
            ).order_by(
                'criada_em'
            )
        )

        # volta para aguardando
        senha_atual.status = 'AGUARDANDO'
        senha_atual.atendente = None
        senha_atual.chamada_em = None

        # coloca em terceiro
        if len(fila) >= 3:

            referencia = fila[2]

            senha_atual.criada_em = (
                referencia.criada_em - timedelta(milliseconds=1)
            )

        elif len(fila) >= 2:

            referencia = fila[1]

            senha_atual.criada_em = (
                referencia.criada_em + timedelta(milliseconds=1)
            )

        elif len(fila) >= 1:

            referencia = fila[0]

            senha_atual.criada_em = (
                referencia.criada_em + timedelta(milliseconds=1)
            )

        else:
            senha_atual.criada_em = timezone.now()

        senha_atual.save()

        Atendimento.objects.filter(
            senha=senha_atual,
            ativo=True
        ).update(
            finalizado_em=timezone.now(),
            ativo=False
        )

        messages.success(
            request,
            f'Senha {senha_atual.codigo} movida para a terceira posição.'
        )

        return redirect('adminSeletto')

@method_decorator(role_required('admin', 'funcionario', 'gerente'), name='dispatch')
class FinalizarSenhaView(View):
    def post(self, request):
        senha_id = request.POST.get('senha_id')
        com_observacoes = request.POST.get('com_observacoes')
        
        if not senha_id:
            messages.warning(
                request,
                'Nenhuma senha especificada para finalizar.'
            )
            return redirect('adminSeletto')
        
        try:
            senha_atual = Senha.objects.get(
            id=senha_id,
            status='EM_ATENDIMENTO'
            )
        except Senha.DoesNotExist:
            messages.warning(
                request,
                'Nenhum atendimento ativo encontrado para o seu usuário.'
            )
            return redirect('adminSeletto')

        # Se tem observações, processar formulário
        if com_observacoes:
            status = request.POST.get('status')
            
            # Criar ou atualizar observação
            observacao, created = ObservacaoAtendimento.objects.get_or_create(
                senha=senha_atual
            )
            
            observacao.status = status
            
            if status == 'FECHOU':
                observacao.tipo_evento = request.POST.get('tipo_evento_fechou')
                observacao.data_evento = request.POST.get('data_evento_fechou') or None
                observacao.cidade = request.POST.get('cidade_fechou')
                observacao.local = request.POST.get('local_fechou')
                
                # Campos de casamento
                if observacao.tipo_evento == 'CASAMENTO':
                    observacao.nomes_noivos = request.POST.get('nomes_noivos_fechou')
                    observacao.contato_noivos = request.POST.get('contato_noivos_fechou')
                
                # Campos de formatura
                elif observacao.tipo_evento == 'FORMATURA':
                    observacao.contato_formando = request.POST.get('contato_formando_fechou')
                    observacao.universidade = request.POST.get('universidade_fechou')
                    observacao.curso = request.POST.get('curso_fechou')
                
                # Campos de aniversário
                elif observacao.tipo_evento == 'ANIVERSARIO':
                    observacao.nome_aniversariante = request.POST.get('nome_aniversariante_fechou')
                
                # Campos de outro
                elif observacao.tipo_evento == 'OUTRO':
                    observacao.tipo_evento_outro = request.POST.get('tipo_evento_outro_fechou')
                    observacao.nome_cliente_observacao = request.POST.get('nome_cliente_obs_fechou')
                    observacao.descricao = request.POST.get('descricao_fechou')
            
            elif status == 'NAO_FECHOU':
                observacao.motivo_nao_fechamento = request.POST.get('motivo_nao_fechamento')
                observacao.tipo_evento = request.POST.get('tipo_evento_nao_fechou')
                observacao.data_evento = request.POST.get('data_evento_nao_fechou') or None
                observacao.cidade = request.POST.get('cidade_nao_fechou')
                observacao.local = request.POST.get('local_nao_fechou')
                
                # Campos de casamento
                if observacao.tipo_evento == 'CASAMENTO':
                    observacao.nomes_noivos = request.POST.get('nomes_noivos_nao_fechou')
                    observacao.contato_noivos = request.POST.get('contato_noivos_nao_fechou')
                
                # Campos de formatura
                elif observacao.tipo_evento == 'FORMATURA':
                    observacao.contato_formando = request.POST.get('contato_formando_nao_fechou')
                    observacao.universidade = request.POST.get('universidade_nao_fechou')
                    observacao.curso = request.POST.get('curso_nao_fechou')
                
                # Campos de aniversário
                elif observacao.tipo_evento == 'ANIVERSARIO':
                    observacao.nome_aniversariante = request.POST.get('nome_aniversariante_nao_fechou')
                
                # Campos de outro
                elif observacao.tipo_evento == 'OUTRO':
                    observacao.tipo_evento_outro = request.POST.get('tipo_evento_outro_nao_fechou')
                    observacao.nome_cliente_observacao = request.POST.get('nome_cliente_obs_nao_fechou')
                    observacao.descricao = request.POST.get('descricao_nao_fechou')
            
            observacao.save()

        # finaliza atendimento
        senha_atual.status = 'FINALIZADO'
        senha_atual.finalizado_em = timezone.now()
        senha_atual.save()

        Atendimento.objects.filter(
            senha=senha_atual,
            ativo=True
        ).update(
            finalizado_em=timezone.now(),
            ativo=False
        )

        return redirect('adminSeletto')



@method_decorator(role_required('admin', 'gerente', 'funcionario'), name='dispatch')
class VoltarFilaView(View):

    def post(self, request):

        senha_id = request.POST.get('senha_id')

        if not senha_id:
            messages.warning(
                request,
                'Senha não informada.'
            )
            return redirect('adminSeletto')

        try:
            senha = Senha.objects.get(id=senha_id)

        except Senha.DoesNotExist:
            messages.warning(
                request,
                'Senha não encontrada.'
            )
            return redirect('adminSeletto')

        # fila da mesma prioridade/categoria
        fila = list(
            Senha.objects.filter(
                status='AGUARDANDO',
                categoria__peso=senha.categoria.peso
            ).exclude(
                id=senha.id
            ).order_by(
                'criada_em'
            )
        )

        senha.status = 'AGUARDANDO'
        senha.atendente = None
        senha.chamada_em = None
        senha.finalizado_em = None

        # coloca em terceiro
        if len(fila) >= 3:

            referencia = fila[2]

            senha.criada_em = (
                referencia.criada_em - timedelta(milliseconds=1)
            )

        elif len(fila) >= 2:

            referencia = fila[1]

            senha.criada_em = (
                referencia.criada_em + timedelta(milliseconds=1)
            )

        elif len(fila) >= 1:

            referencia = fila[0]

            senha.criada_em = (
                referencia.criada_em + timedelta(milliseconds=1)
            )

        else:
            senha.criada_em = timezone.now()

        senha.save()

        messages.success(
            request,
            f'Senha {senha.codigo} voltou para a fila na terceira posição.'
        )

        return redirect('adminSeletto')
    
class HomeView(TemplateView):
    template_name = 'home/index.html'

@method_decorator(role_required('tv'), name='dispatch')
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
            status='AGUARDANDO'
        ).select_related('categoria').order_by(
            '-categoria__peso',  # Maior peso primeiro
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


@method_decorator(role_required('admin', 'funcionario'), name='dispatch')
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
            '-categoria__peso',
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
@method_decorator(role_required('totem'), name='dispatch')
class TotemView(TemplateView):
    template_name = 'totem/escolha_atendimento.html'

@method_decorator(role_required('totem'), name='dispatch')
class DadosClienteView(FormView):

    template_name = 'totem/dados_cliente.html'
    form_class = ClienteForm

    TIPO_MAPEAMENTO = {
        'prova-noivo': 'Prova Noivo',
        'prioritario': 'Prioritário',
        'locar-terno': 'Locar Terno',
        'prova': 'Prova',
        'retrabalho': 'Retrabalho',
        'venda': 'Venda',
        'troca': 'Troca',
        'retirada': 'Retirada',
        'gerente': 'Falar com gerente',
        'devolucao': 'Devolução',
    }

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        tipo = self.kwargs.get('tipo', '')

        context['tipo'] = self.TIPO_MAPEAMENTO.get(
            tipo,
            tipo.replace('-', ' ').title()
        )

        return context

    def form_invalid(self, form):

        logger.error('Formulário inválido: %s', form.errors)  # Log detalhado do erro
        

        return super().form_invalid(form)

    def form_valid(self, form):

        tipo = self.kwargs.get('tipo', '')

        categoria_nome = self.TIPO_MAPEAMENTO.get(tipo)

        if not categoria_nome:

            messages.error(
                self.request,
                'Tipo de atendimento inválido.'
            )

            return self.form_invalid(form)

        categoria = Categoria.objects.filter(
            nome__iexact=categoria_nome,
            fila__ativa=True,
            ativa=True
        ).first()

        if not categoria:

            messages.error(
                self.request,
                'Categoria de atendimento não encontrada.'
            )

            return self.form_invalid(form)

        prefixo = categoria.prefixo

        senha = None

        for attempt in range(3):

            try:

                with transaction.atomic():

                    categoria = Categoria.objects.select_for_update().get(
                        pk=categoria.pk
                    )

                    ultima_senha = Senha.objects.filter(
                        categoria=categoria,
                        codigo__startswith=prefixo
                    ).order_by('-id').first()

                    if ultima_senha:

                        ultimo_numero = int(
                            ultima_senha.codigo.replace(prefixo, '')
                        )

                        numero = ultimo_numero + 1

                    else:

                        numero = 1

                    codigo = f'{prefixo}{numero:03d}'

                    senha = Senha.objects.create(
                        codigo=codigo,
                        cliente_nome=form.cleaned_data['nome'],
                        cliente_email=form.cleaned_data['email'],
                        cliente_telefone=form.cleaned_data['whatsapp'],
                        fila=categoria.fila,
                        categoria=categoria,
                    )

                    break

            except IntegrityError:

                logger.warning('Conflito ao gerar senha para categoria %s, tentativa %d', categoria.nome, attempt + 1)

                if attempt == 2:

                    messages.error(
                        self.request,
                        'Não foi possível gerar a senha no momento.'
                    )

                    return self.form_invalid(form)

        if not senha:

            messages.error(
                self.request,
                'Não foi possível gerar a senha.'
            )

            return self.form_invalid(form)

        self.request.session['senha_gerada'] = {
            'codigo': senha.codigo,
            'tipo': categoria.nome,
            'nome': senha.cliente_nome,
        }

        messages.success(
            self.request,
            f'Senha {senha.codigo} gerada com sucesso!'
        )

        return redirect('senha_gerada')


class SenhaGeradaView(TemplateView):
    template_name = 'totem/senha_gerada.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        senha_data = self.request.session.get('senha_gerada', {})
        context.update(senha_data)
        
        # Buscar a senha gerada para pegar o token
        if 'codigo' in senha_data:
            try:
                senha = Senha.objects.filter(codigo=senha_data['codigo']).order_by('-id').first()
                if senha:
                    context['token'] = str(senha.token)
            except Senha.DoesNotExist:
                pass
        
        return context


class AcompanharFilaView(TemplateView):
    template_name = 'totem/acompanhar_fila.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Buscar senha pelo token da URL ou pela sessão
        token = self.kwargs.get('token')
        
        if token:
            # Token vem da URL (QR code)
            try:
                senha = Senha.objects.select_related('categoria').get(token=token)
            except Senha.DoesNotExist:
                context['error'] = 'Senha não encontrada. Verifique o QR code ou tente gerar uma nova senha.'
                return context
        else:
            # Fallback para sessão (compatibilidade)
            senha_session = self.request.session.get('senha_gerada')
            if not senha_session:
                context['error'] = 'Nenhuma senha encontrada na sessão. Gere uma nova senha no totem.'
                return context
            
            senha = Senha.objects.select_related('categoria').filter(
                codigo=senha_session['codigo']
            ).order_by('-id').first()
            
            if not senha:
                context['error'] = 'Senha não encontrada. Gere uma nova senha no totem.'
                return context

        if senha.status == 'AGUARDANDO':
            fila = Senha.objects.filter(
                status='AGUARDANDO'
            ).select_related('categoria').order_by(
                '-categoria__peso',
                'criada_em'
            )

            posicao = 0
            for index, item in enumerate(fila, start=1):
                if item.id == senha.id:
                    posicao = index
                    break

            tempo_estimado = posicao * (senha.categoria.tempo_estimado_min or 5)
        else:
            posicao = 0
            tempo_estimado = 0
            if senha.status == 'EM_ATENDIMENTO':
                context['info'] = 'Chegou a sua vez! Dirija-se ao atendimento, por favor.'
            else:
                context['info'] = 'Esta senha já foi atendida e não se encontra mais na fila de espera.'

        context.update({
            'senha': senha.codigo,
            'tipo': senha.categoria.nome,
            'posicao': posicao,
            'tempo_estimado': tempo_estimado,
            'token': senha.token,
        })

        return context


def display_partial(request):

    # senhas em atendimento
    senhas_atendendo_obj = Senha.objects.filter(
        status='EM_ATENDENDO'
    ).select_related('categoria').order_by('chamada_em')

    senhas_atendendo = [
        {
            'codigo': senha.codigo,
            'tipo': senha.categoria.nome,
            'cliente_nome': senha.cliente_nome,
        }
        for senha in senhas_atendendo_obj
    ]

    # próximas senhas
    proximas_senhas_obj = Senha.objects.filter(
        status='AGUARDANDO'
    ).select_related('categoria').order_by(
        '-categoria__peso',
        'criada_em'
    )[:3]

    proximas_senhas = [
        {
            'codigo': senha.codigo,
            'tipo': senha.categoria.nome,
            'cliente_nome': senha.cliente_nome,
            'status': senha.status or 'AGUARDANDO',
        }
        for senha in proximas_senhas_obj
    ]

    context = {
        'senhas_atendendo': senhas_atendendo,
        'proximas_senhas': proximas_senhas
    }

    return render(
        request,
        'partials/display_content.html',
        context
    )


class ListaClientesView(TemplateView):
    template_name = "core/lista_clientes.html"


def gerar_qr(request):
    """Gera QR code para acompanhar fila com token específico"""
    token = request.GET.get('token')
    
    if token:
        # Gerar URL com token específico
        url = request.build_absolute_uri(reverse('acompanhar_fila_token', kwargs={'token': token}))
    else:
        # Fallback para URL genérica (compatibilidade)
        url = request.build_absolute_uri(reverse('acompanhar_fila'))
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return HttpResponse(buffer.getvalue(), content_type="image/png")

@role_required('admin', 'funcionario')
def admin_stats_partial(request):

    aguardando = Senha.objects.filter(
        status='AGUARDANDO'
    ).count()

    em_atendimento = Senha.objects.filter(
        status='EM_ATENDENDO'
    ).count()

    atendidos = Senha.objects.filter(
        status='FINALIZADO'
    ).count()

    context = {
        'aguardando': aguardando,
        'em_atendimento': em_atendimento,
        'atendidos': atendidos,
    }

    return render(
        request,
        'partials/admin_stats.html',
        context
    )

@role_required('admin', 'funcionario')
def admin_atendimento_partial(request):

    senhas_atendendo = Senha.objects.select_related(
        'categoria'
    ).filter(
        status='EM_ATENDIMENTO',
    ).order_by('chamada_em')

    context = {
        'senhas_atendendo': senhas_atendendo
    }

    return render(
        request,
        'partials/admin_atendimento_atual.html',
        context
    )

@role_required('admin', 'funcionario')
def admin_fila_partial(request):

    fila = Senha.objects.select_related(
        'categoria'
    ).filter(
        Q(status='AGUARDANDO') |
        Q(status='EM_ATENDENDO')
    ).order_by(
        '-categoria__peso',
        'criada_em'
    )

    context = {
        'fila': fila
    }

    return render(
        request,
        'partials/admin_fila.html',
        context
    )

def fila_status_partial(request):

    context = {
        'posicao': 0,
        'tempo_estimado': 0,
    }

    # Buscar pela token da query string ou pela sessão
    token = request.GET.get('token')
    
    if token:
        try:
            senha = Senha.objects.select_related(
                'categoria'
            ).get(token=token)
        except Senha.DoesNotExist:
            return render(
                request,
                'partials/fila_status.html',
                context
            )
    else:
        # Fallback para sessão
        senha_session = request.session.get('senha_gerada')
        
        if not senha_session:
            return render(
                request,
                'partials/fila_status.html',
                context
            )
        
        senha = Senha.objects.select_related(
            'categoria'
        ).filter(
            codigo=senha_session['codigo']
        ).order_by('-id').first()
        
        if not senha:
            return render(
                request,
                'partials/fila_status.html',
                context
            )

    if senha.status == 'AGUARDANDO':
        fila = Senha.objects.filter(
            status='AGUARDANDO'
        ).select_related('categoria').order_by(
            '-categoria__peso',
            'criada_em'
        )

        posicao = 0
        for index, item in enumerate(fila, start=1):
            if item.id == senha.id:
                posicao = index
                break

        tempo_estimado = posicao * (senha.categoria.tempo_estimado_min or 5)
    else:
        posicao = 0
        tempo_estimado = 0
        if senha.status == 'EM_ATENDENDO':
            context['info'] = 'Sua senha já está em atendimento.'
        else:
            context['info'] = 'Seu atendimento já foi finalizado ou não está mais na fila.'

    context.update({
        'posicao': posicao,
        'tempo_estimado': tempo_estimado,
    })

    return render(
        request,
        'partials/fila_status.html',
        context
    )

@method_decorator(role_required('admin', 'gerente'), name='dispatch')
class AtendidosView(TemplateView):

    template_name = 'adminSeletto/atendidos.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        atendidos = Senha.objects.select_related(
            'categoria'
        ).filter(
            status='FINALIZADO'
        ).order_by(
            '-finalizado_em'
        )

        context['atendidos'] = atendidos

        return context
    
@role_required('admin')
def excluir_atendido(request, senha_id):

    try:
        senha = Senha.objects.get(
            id=senha_id,
            status='FINALIZADO'
        )

        senha.delete()

        messages.success(
            request,
            f'Atendimento {senha.codigo} excluído com sucesso.'
        )

    except Senha.DoesNotExist:

        messages.warning(
            request,
            'Atendimento não encontrado.'
        )

    return redirect('atendidos')