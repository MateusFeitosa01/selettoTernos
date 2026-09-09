from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from filas.models import Categoria, Fila, Senha


class AtendidosViewTests(TestCase):

	def setUp(self):
		self.client.force_login(
			User.objects.create_superuser(
				username='admin-historico',
				email='admin-historico@example.com',
				password='test-password',
			)
		)
		self.fila = Fila.objects.create(nome='Fila de teste')

	def criar_categoria(self, nome, prefixo):
		return Categoria.objects.create(
			nome=nome,
			prefixo=prefixo,
			fila=self.fila,
		)

	def criar_finalizados(self, categoria, quantidade, inicio):
		for indice in range(quantidade):
			Senha.objects.create(
				codigo=f'{categoria.prefixo}{indice + 1:03d}',
				cliente_nome=f'Cliente {categoria.nome} {indice}',
				cliente_telefone=f'1199999{indice:04d}',
				fila=self.fila,
				categoria=categoria,
				status='FINALIZADO',
				finalizado_em=inicio + timedelta(minutes=indice),
			)

	def test_historico_preserva_todos_os_finalizados_por_categoria_id(self):
		inicio = timezone.now() - timedelta(days=1)
		prova_noivo = self.criar_categoria('Prova Noivo', 'PN')
		locar_terno = self.criar_categoria('Locar Terno', 'LT')
		venda = self.criar_categoria('Venda', 'VD')

		self.criar_finalizados(prova_noivo, 5, inicio)
		self.criar_finalizados(locar_terno, 3, inicio)
		self.criar_finalizados(venda, 2, inicio)

		response = self.client.get('/atendidos/')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['atendidos'].count(), 10)
		self.assertEqual(
			response.context['categorias'].values_list('id', flat=True).count(),
			3,
		)
		self.assertContains(response, f'value="{prova_noivo.id}"')
		self.assertContains(response, f'value="{locar_terno.id}"')
		self.assertContains(response, f'value="{venda.id}"')

	def test_categorias_com_mesmo_nome_mantem_ids_distintos(self):
		inicio = timezone.now() - timedelta(days=1)
		primeira = self.criar_categoria('Prova Noivo', 'PN')
		segunda = self.criar_categoria('Prova Noivo', 'P2')
		self.criar_finalizados(primeira, 2, inicio)
		self.criar_finalizados(segunda, 1, inicio)

		response = self.client.get('/atendidos/')

		self.assertEqual(response.context['atendidos'].count(), 3)
		self.assertContains(response, f'value="{primeira.id}"')
		self.assertContains(response, f'value="{segunda.id}"')
		self.assertContains(response, f'ID {primeira.id}')
		self.assertContains(response, f'ID {segunda.id}')
