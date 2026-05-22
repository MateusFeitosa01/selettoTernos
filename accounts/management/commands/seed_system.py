from django.core.management.base import BaseCommand
from filas.models import Fila, Categoria

class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        fila, _ = Fila.objects.get_or_create(
            nome="Fila Principal",
            defaults={"ativa": True}
        )

        categorias = [
            ("Prova Noivo", "PN", 100),
            ("Prioritário", "PR", 90),
            ("Locar Terno", "LT", 50),
            ("Prova", "PV", 50),
            ("Retrabalho", "RT", 50),
            ("Venda", "VD", 50),
            ("Troca", "TC", 50),
            ("Retirada", "RE", 50),
            ("Falar com gerente", "GE", 50),
            ("Devolução", "DV", 1),
        ]

        for nome, prefixo, peso in categorias:

            Categoria.objects.get_or_create(
                nome=nome,
                defaults={
                    "prefixo": prefixo,
                    "peso": peso,
                    "ativa": True,
                    "fila": fila
                }
            )

        self.stdout.write(
            self.style.SUCCESS("Sistema populado com sucesso.")
        )