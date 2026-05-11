from django.urls import path
from .views import (
    HomeView,
    TotemView,
    DadosClienteView,
    SenhaGeradaView,
    AcompanharFilaView,
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
]