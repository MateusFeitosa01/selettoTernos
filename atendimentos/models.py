from django.db import models
from django.conf import settings

from filas.models import Senha


class Atendimento(models.Model):

    senha = models.ForeignKey(
        Senha,
        on_delete=models.CASCADE,
        related_name='atendimentos'
    )

    atendente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='atendimentos'
    )

    iniciado_em = models.DateTimeField(
        auto_now_add=True
    )

    finalizado_em = models.DateTimeField(
        null=True,
        blank=True
    )

    ativo = models.BooleanField(
        default=True
    )

    observacoes = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-iniciado_em']

    def __str__(self):
        return f'{self.senha.codigo} - {self.atendente}'