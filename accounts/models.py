from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    TIPOS = (
        ('admin', 'Admin'),
        ('funcionario', 'Funcionário'),
        ('tv', 'TV'),
        ('totem', 'Totem'),
        ('gerente', 'Gerente'),
    )

    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPOS,
    )

    telefone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.username