from django.contrib import admin

from .models import Atendimento

@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = ('senha', 'atendente', 'iniciado_em', 'finalizado_em', 'ativo')
    list_filter = ('ativo', 'iniciado_em', 'finalizado_em')
    search_fields = ('senha__codigo', 'atendente__username')
