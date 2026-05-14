from django.core.management.base import BaseCommand
from filas.models import Fila, Categoria

class Command(BaseCommand):
    help = 'Popula categorias com configurações específicas'

    def handle(self, *args, **options):
        # Criar fila padrão se não existir
        fila, created = Fila.objects.get_or_create(
            nome='Fila Principal',
            defaults={'ativa': True}
        )

        # Categorias com configurações
        categorias_data = [
            {
                'nome': 'Prova noivo',
                'prefixo': 'PN',
                'peso': 3,
                'tempo_estimado_min': 30,
                'tempo_estimado_max': 60,
            },
            {
                'nome': 'Prioritário',
                'prefixo': 'PR',
                'peso': 3,
                'tempo_estimado_min': 20,
                'tempo_estimado_max': 20,
            },
            {
                'nome': 'Locar terno',
                'prefixo': 'LT',
                'peso': 2,
                'tempo_estimado_min': 20,
                'tempo_estimado_max': 20,
            },
            {
                'nome': 'Prova',
                'prefixo': 'PV',
                'peso': 2,
                'tempo_estimado_min': 20,
                'tempo_estimado_max': 20,
            },
            {
                'nome': 'Retrabalho',
                'prefixo': 'RT',
                'peso': 2,
                'tempo_estimado_min': 20,
                'tempo_estimado_max': 20,
            },
            {
                'nome': 'Venda',
                'prefixo': 'VD',
                'peso': 2,
                'tempo_estimado_min': 20,
                'tempo_estimado_max': 20,
            },
            {
                'nome': 'Troca',
                'prefixo': 'TR',
                'peso': 2,
                'tempo_estimado_min': 20,
                'tempo_estimado_max': 20,
            },
            {
                'nome': 'Retirada',
                'prefixo': 'RR',
                'peso': 2,
                'tempo_estimado_min': 20,
                'tempo_estimado_max': 20,
            },
            {
                'nome': 'Devolução',
                'prefixo': 'DV',
                'peso': 1,
                'tempo_estimado_min': 10,
                'tempo_estimado_max': 10,
            },
            {
                'nome': 'Falar com gerente',
                'prefixo': 'FG',
                'peso': 2,
                'tempo_estimado_min': 20,
                'tempo_estimado_max': 20,
            },
        ]

        for data in categorias_data:
            categoria, created = Categoria.objects.get_or_create(
                nome=data['nome'],
                fila=fila,
                defaults={
                    'prefixo': data['prefixo'],
                    'peso': data['peso'],
                    'tempo_estimado_min': data['tempo_estimado_min'],
                    'tempo_estimado_max': data['tempo_estimado_max'],
                    'ativa': True,
                }
            )
            if created:
                self.stdout.write(f'Criada categoria: {categoria.nome}')
            else:
                # Atualizar se já existe
                categoria.prefixo = data['prefixo']
                categoria.peso = data['peso']
                categoria.tempo_estimado_min = data['tempo_estimado_min']
                categoria.tempo_estimado_max = data['tempo_estimado_max']
                categoria.save()
                self.stdout.write(f'Atualizada categoria: {categoria.nome}')

        self.stdout.write('População de categorias concluída!')