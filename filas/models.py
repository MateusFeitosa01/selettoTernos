from django.db import models
import uuid

class Fila(models.Model):
    nome = models.CharField(max_length=100)
    
    ativa = models.BooleanField(default=True)   

    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
    
class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    fila = models.ForeignKey(Fila, on_delete=models.CASCADE, related_name='categorias')

    prioridade = models.IntegerField(default=0)

    prefixo = models.CharField(max_length=10, default='A')  # Ex: PN, PR, A, FG

    peso = models.IntegerField(default=1)  # Para ordenação na fila

    tempo_estimado_min = models.IntegerField(default=10)  # em minutos

    tempo_estimado_max = models.IntegerField(default=20)  # em minutos

    ativa = models.BooleanField(default=True)

    def __str__(self):
        return self.nome
    
class Senha(models.Model):
    STATUS = (
        ('AGUARDANDO', 'Aguardando'),
        ('CHAMADA', 'Chamada'),
        ('EM_ATENDENDO', 'Em Atendendo'),
        ('ATENDIDA', 'Atendida'),
        ('CANCELADA', 'Cancelada'),
    )
    
    codigo = models.CharField(max_length=20)

    token = models.UUIDField(default=uuid.uuid4, editable=False)

    cliente_nome = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        
        )

    cliente_telefone = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        )

    fila = models.ForeignKey(
        Fila, 
        on_delete=models.CASCADE
        )
    
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        null=False,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='AGUARDANDO',
    )

    criada_em = models.DateTimeField(auto_now_add=True)

    chamada_em = models.DateTimeField(
        null=True, 
        blank=True
        )
    
    finalizado_em = models.DateTimeField(
        null=True,
        blank=True
        )
    
    atendente = models.CharField(
        max_length=100,
        null=True,
        blank=True
        )
    
    def __str__(self):
        return self.codigo

