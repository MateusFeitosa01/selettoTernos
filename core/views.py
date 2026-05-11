from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home/index.html'


class TotemEscolhaView(TemplateView):
    template_name = 'totem/escolha_atendimento.html'


class TotemDadosView(TemplateView):
    template_name = 'totem/dados_cliente.html'


class TotemSenhaView(TemplateView):
    template_name = 'totem/senha_gerada.html'


class PainelFilaView(TemplateView):
    template_name = 'display/painel_fila.html'


class AdminDashboardView(TemplateView):
    template_name = 'admin_painel/dashboard.html'