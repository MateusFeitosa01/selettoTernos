from django.urls import path

from .views import (
    HomeView,
    TotemView,
    DadosClienteView,
    SenhaGeradaView,
    AcompanharFilaView,
    DisplayView,
    AdminSelettoView,
    ChamarProximaView,
    PularSenhaView,
    FinalizarSenhaView,
    display_partial,
    gerar_qr,
    ListaClientesView
)

urlpatterns = [

    path('', HomeView.as_view(), name='home'),

    path(
        'totem/',
        TotemView.as_view(),
        name='totem'
    ),

    path(
        'totem/dados-cliente/<str:tipo>/',
        DadosClienteView.as_view(),
        name='dados_cliente'
    ),

    path(
        'totem/senha-gerada/',
        SenhaGeradaView.as_view(),
        name='senha_gerada'
    ),

    path(
        'acompanhar-fila/',
        AcompanharFilaView.as_view(),
        name='acompanhar_fila'
    ),

    path(
        'display/',
        DisplayView.as_view(),
        name='display'
    ),

    path(
        'display-partial/',
        display_partial,
        name='display_partial'
    ),

    path(
        'admin/',
        AdminSelettoView.as_view(),
        name='adminSeletto'
    ),

    path(
        'chamar-proxima/',
        ChamarProximaView.as_view(),
        name='chamar_proxima'
    ),

    path(
        'pular-senha/',
        PularSenhaView.as_view(),
        name='pular_senha'
    ),

    path(
        'finalizar-senha/',
        FinalizarSenhaView.as_view(),
        name='finalizar_senha'
    ),

    path(
        'gerar-qr/',
        gerar_qr,
        name='gerar_qr'
    ),

    path(
        'lista-clientes/',
        ListaClientesView.as_view(),
        name='lista_clientes'
    ),
]