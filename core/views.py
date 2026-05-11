from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home/index.html'


class DisplayView(TemplateView):
    template_name = 'display/painel_fila.html'


class AdminSelettoView(TemplateView):
    template_name = 'adminSeletto/dashboard.html'


class TotemView(TemplateView):
    template_name = 'totem/escolha_atendimento.html'


class DadosClienteView(TemplateView):
    template_name = 'totem/dados_cliente.html'


class SenhaGeradaView(TemplateView):
    template_name = 'totem/senha_gerada.html'


class AcompanharFilaView(TemplateView):
    template_name = 'totem/acompanhar_fila.html'