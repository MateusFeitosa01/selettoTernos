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
        ('FINALIZADO', 'Finalizado'),
        ('ATENDIDA', 'Atendida'),
        ('CANCELADA', 'Cancelada'),
    )
    
    codigo = models.CharField(max_length=20, unique=True, db_index=True)

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    cliente_nome = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        
        )

    cliente_email = models.EmailField(
        max_length=254,
        null=True,
        blank=True,
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


class ObservacaoAtendimento(models.Model):
    STATUS_CHOICES = (
        ('FECHOU', 'Fechou'),
        ('NAO_FECHOU', 'Não Fechou'),
    )
    
    TIPO_EVENTO_CHOICES = (
        ('ANIVERSARIO', 'Aniversário'),
        ('CASAMENTO', 'Casamento'),
        ('FORMATURA', 'Formatura'),
        ('OUTRO', 'Outro'),
    )
    
    senha = models.OneToOneField(
        Senha,
        on_delete=models.CASCADE,
        related_name='observacao'
    )
    
    # Campo principal
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        null=True,
        blank=True
    )
    
    # Campos comuns
    tipo_evento = models.CharField(
        max_length=20,
        choices=TIPO_EVENTO_CHOICES,
        null=True,
        blank=True
    )
    
    data_evento = models.DateField(
        null=True,
        blank=True
    )
    
    cidade = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    
    local = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    
    # Campos específicos para casamento
    nomes_noivos = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    
    contato_noivos = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    
    # Campos específicos para formatura
    universidade = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    
    curso = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    
    contato_formando = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    
    # Campos específicos para aniversário
    nome_aniversariante = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    
    # Campos específicos para tipo "OUTRO"
    tipo_evento_outro = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Descrição personalizada do tipo de evento quando 'OUTRO' é selecionado"
    )
    
    nome_cliente_observacao = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Nome do cliente fornecido na observação (quando tipo OUTRO)"
    )
    
    descricao = models.TextField(
        null=True,
        blank=True,
        help_text="Descrição adicional do atendimento"
    )
    
    # Campos específicos para não fechamento
    motivo_nao_fechamento = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    
    # Data de criação
    criada_em = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Observação - {self.senha.codigo}"

