from django.db import models

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
    
    Categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        null=False,
    )

    criada_em = models.DateTimeField(auto_now_add=True)

    chamada_em = models.DateTimeField(
        null=True, 
        blank=True
        )
    
    Finalizado_em = models.DateTimeField(
        null=True,
        blank=True
        )
    
    def __str__(self):
        return self.codigo

