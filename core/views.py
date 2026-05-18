from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.db import transaction, IntegrityError
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from filas.models import Categoria, Senha
from atendimentos.models import Atendimento
from .forms import ClienteForm
from django.views import View
from django.shortcuts import redirect, render
import qrcode
from io import BytesIO
from django.http import HttpResponse
from functools import wraps


def atendente_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        

        if not request.user.is_authenticated:
            return redirect('login')


        print(request.user)


        tipo_usuario = ''

        if request.user.tipo_usuario:
            tipo_usuario = request.user.tipo_usuario.lower()

        if tipo_usuario not in ('admin', 'atendente'):
            messages.error(
                request,
                'Acesso restrito. Faça login com uma conta de atendente ou administrador.'
            )
            return redirect('home')

        return view_func(request, *args, **kwargs)

    return _wrapped_view


@method_decorator(atendente_required, name='dispatch')
class ChamarProximaView(View):
    def post(self, request):

        atendente = request.user.username if request.user.is_authenticated else None

        if not atendente:
            return redirect('adminSeletto')

        active_atendimento = Atendimento.objects.filter(
            atendente=request.user,
            ativo=True
        ).select_related('senha').first()

        if active_atendimento:
            messages.warning(
                request,
                'Finalize o atendimento atual antes de chamar a próxima senha.'
            )
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
            senha.status = 'EM_ATENDENDO'
            senha.atendente = atendente
            senha.chamada_em = timezone.now()
            senha.save()

            Atendimento.objects.create(
                senha=senha,
                atendente=request.user
            )

        return redirect('adminSeletto')

@method_decorator(atendente_required, name='dispatch')
class PularSenhaView(View):
    def post(self, request):
        senha_atual = Senha.objects.filter(
            status='EM_ATENDENDO',
            atendente=request.user.username
        ).order_by('chamada_em').first()

        if not senha_atual:
            messages.warning(
                request,
                'Nenhum atendimento ativo encontrado para o seu usuário.'
            )
            return redirect('adminSeletto')

        # volta para fila
        senha_atual.status = 'AGUARDANDO'
        senha_atual.atendente = None
        senha_atual.chamada_em = None
        senha_atual.save()

        Atendimento.objects.filter(
            senha=senha_atual,
            ativo=True
        ).update(
            finalizado_em=timezone.now(),
            ativo=False
        )

        return redirect('adminSeletto')


@method_decorator(atendente_required, name='dispatch')
class FinalizarSenhaView(View):
    def post(self, request):
        senha_atual = Senha.objects.filter(
            status='EM_ATENDENDO',
            atendente=request.user.username
        ).order_by('chamada_em').first()

        if not senha_atual:
            messages.warning(
                request,
                'Nenhum atendimento ativo encontrado para o seu usuário.'
            )
            return redirect('adminSeletto')

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


@method_decorator(atendente_required, name='dispatch')
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
            'troca': 'Troca',
            'retirada': 'Retirada',
            'gerente': 'Falar com gerente',
            'devolucao': 'Devolução',
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
            'troca': 'Troca',
            'retirada': 'Retirada',
            'gerente': 'Falar com gerente',
            'devolucao': 'Devolução',
        }

        categoria_nome = tipo_para_categoria.get(tipo)

        if not categoria_nome:
            messages.error(
                self.request,
                'Tipo de atendimento inválido.'
            )
            return self.form_invalid(form)

        # Buscar categoria
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

        # Gerar código único da senha
        hoje = timezone.now().date()
        prefixo = categoria.prefixo

        senha = None
        for attempt in range(3):
            with transaction.atomic():
                categoria = Categoria.objects.select_for_update().get(pk=categoria.pk)

                # Contar senhas do dia
                senhas_hoje = Senha.objects.filter(
                    categoria=categoria,
                    criada_em__date=hoje
                ).count()

                numero = senhas_hoje + 1
                codigo = f"{prefixo}{numero:03d}"

                try:
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
                    if attempt == 2:
                        messages.error(
                            self.request,
                            'Não foi possível gerar a senha no momento. Tente novamente.'
                        )
                        return self.form_invalid(form)

        if not senha:
            messages.error(
                self.request,
                'Não foi possível gerar a senha. Tente novamente.'
            )
            return self.form_invalid(form)

        # Salvar sessão
        self.request.session['senha_gerada'] = {
            'codigo': senha.codigo,
            'tipo': categoria.nome,
            'nome': senha.cliente_nome,
        }

        messages.success(
            self.request,
            f'Senha {senha.codigo} gerada com sucesso!'
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('senha_gerada')


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
            if senha.status == 'EM_ATENDENDO':
                context['info'] = 'Sua senha já está em atendimento.'
            else:
                context['info'] = 'Seu atendimento já foi finalizado ou não está mais na fila.'

        context.update({
            'senha': senha.codigo,
            'tipo': senha.categoria.nome,
            'posicao': posicao,
            'tempo_estimado': tempo_estimado,
            'token': senha.token,
        })

        return context


def display_partial(request):

    # senha atual
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
        'senha_atual': senha_atual,
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

@atendente_required
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

@atendente_required
def admin_atendimento_partial(request):

    senha_atual = Senha.objects.select_related(
        'categoria'
    ).filter(
        status='EM_ATENDENDO'
    ).first()

    context = {
        'senha_atual': senha_atual
    }

    return render(
        request,
        'partials/admin_atendimento_atual.html',
        context
    )

@atendente_required
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