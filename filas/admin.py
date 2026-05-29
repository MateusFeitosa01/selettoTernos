from django.contrib import admin

from .models import Fila, Categoria, Senha, ObservacaoAtendimento

@admin.register(Fila)
class FilaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativa', 'criada_em')
    list_filter = ('ativa',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'fila', 'prioridade', 'ativa')
    list_filter = ('fila', 'ativa')

@admin.register(Senha)
class SenhaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'cliente_nome', 'categoria', 'status', 'criada_em')
    list_filter = ('status', 'categoria', 'fila')
    search_fields = ('codigo', 'cliente_nome', 'cliente_telefone')

@admin.register(ObservacaoAtendimento)
class ObservacaoAtendimentoAdmin(admin.ModelAdmin):
    list_display = ('senha', 'status', 'tipo_evento', 'data_evento', 'criada_em')
    list_filter = ('status', 'tipo_evento', 'data_evento')
    search_fields = ('senha__codigo', 'nomes_noivos', 'cidade')
