from django.urls import path
from .views import *

urlpatterns = [

    path('', HomeView.as_view(), name='home'),

    path(
        'totem/',
        TotemEscolhaView.as_view(),
        name='totem'
    ),

    path(
        'totem/dados/',
        TotemDadosView.as_view(),
        name='totem-dados'
    ),

    path(
        'totem/senha/',
        TotemSenhaView.as_view(),
        name='totem-senha'
    ),

    path(
        'painel/',
        PainelFilaView.as_view(),
        name='painel'
    ),

    path(
        'dashboard/',
        AdminDashboardView.as_view(),
        name='dashboard'
    ),
]