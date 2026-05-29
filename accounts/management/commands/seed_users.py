from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria usuários padrão do sistema'

    def handle(self, *args, **kwargs):

        usuarios = [
            {
                'username': config('ADMIN_USER'),
                'password': config('ADMIN_PASSWORD'),
                'tipo_usuario': 'admin',
            },
            {
                'username': config('FUNC_USER'),
                'password': config('FUNC_PASSWORD'),
                'tipo_usuario': 'funcionario',
            },
            {
                'username': config('TV_USER'),
                'password': config('TV_PASSWORD'),
                'tipo_usuario': 'tv',
            },
            {
                'username': config('TOTEM_USER'),
                'password': config('TOTEM_PASSWORD'),
                'tipo_usuario': 'totem',
            },
            {
                'username': config('GERENTE_USER'),
                'password': config('GERENTE_PASSWORD'),
                'tipo_usuario': 'gerente',
            },
        ]

        for data in usuarios:

            user, created = User.objects.get_or_create(
                username=data['username']
            )

            user.tipo_usuario = data['tipo_usuario']

            # MUITO IMPORTANTE
            user.set_password(data['password'])

            user.save()

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Usuário {user.username} criado.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Usuário {user.username} atualizado.'
                    )
                )