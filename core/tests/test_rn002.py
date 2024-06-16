from unittest.mock import MagicMock, patch
from django.test import TestCase
from core.models import Aluno, Disciplina, OfertaDisciplina, Professor, Turma
from core.views import ControladorInscricao


# RN002: Quantidade de alunos possíveis
# Descricao: Uma turma não pode ter mais alunos inscritos do que a capacidade máxima definida para ela.

# TESTES DE UNIDADE


class RealizarInscricaoTestCase(TestCase):
    def setUp(self):
        self.controlador = ControladorInscricao()
        self.controlador.template_name = "realizar_inscricao.html"
        self.controlador.success_url = "/"

    @patch("core.views.render")
    def test_realizar_inscricao_em_disciplina_sem_vagas(self, mock_render):
        # Cria um aluno
        aluno = MagicMock(spec=Aluno)
        aluno.get_creditos.return_value = 0
        # Cria uma oferta de disciplina com 2 créditos
        oferta_disciplina = MagicMock(spec=OfertaDisciplina)
        oferta_disciplina.creditos.return_value = 2
        oferta_disciplina.verificar_choque_de_horario.return_value = False
        oferta_disciplina.vagas_ocupadas.return_value = 40
        oferta_disciplina.vagas = 40
        oferta_disciplina.inscrever_aluno.return_value = None
        oferta_disciplina.aluno_esta_inscrito.return_value = False

        # Emulando a lógica do ORM
        # Cria um base manager com a oferta de disciplina
        # Cria um queryset com a oferta de disciplina
        query_set = MagicMock()
        # Faz o manager retornar a query_set
        # Faz a query_set retornar a oferta de disciplina
        query_set.__iter__.return_value = [oferta_disciplina]

        with patch.object(
            self.controlador,
            "get",
            return_value=query_set,
        ) as mock_get:
            response = self.controlador.realizar_inscricao(
                request=None,
                context={},
                aluno=aluno,
                ofertas=query_set,
                ofertas_cursando=[],
            )
            # Verifica se o método get não foi chamado
            mock_get.assert_not_called()

        # Verifica se a função creditos foi chamada
        oferta_disciplina.creditos.assert_called()
        # Verifica se a função verificar_choque_de_horario foi chamada
        oferta_disciplina.verificar_choque_de_horario.assert_called()

        # Verifica se a função inscrever_aluno não foi chamada
        oferta_disciplina.inscrever_aluno.assert_not_called()

        # Verifica se a função render foi chamada
        mock_render.assert_called_once_with(
            None,
            self.controlador.template_name,
            {
                "lista_espera": [oferta_disciplina],
                "aluno": aluno,
            },
        )

    def test__verificar_lista_espera__turma_cheia(self):
        # Cria uma oferta de disciplina com 2 créditos
        oferta_disciplina = MagicMock(spec=OfertaDisciplina)
        oferta_disciplina.vagas_ocupadas.return_value = 40
        oferta_disciplina.vagas = 40

        # Emulando a lógica do ORM
        # Cria um base manager com a oferta de disciplina
        # Cria um queryset com a oferta de disciplina
        query_set = MagicMock()
        # Faz o manager retornar a query_set
        # Faz a query_set retornar a oferta de disciplina
        query_set.__iter__.return_value = [oferta_disciplina]

        lista_espera = self.controlador._verificar_lista_espera(query_set)
        self.assertEqual(lista_espera, [oferta_disciplina])

    def test__verificar_lista_espera__turma_nao_cheia(self):
        # Cria uma oferta de disciplina com 2 créditos
        oferta_disciplina = MagicMock(spec=OfertaDisciplina)
        oferta_disciplina.vagas_ocupadas.return_value = 39
        oferta_disciplina.vagas = 40

        # Emulando a lógica do ORM
        # Cria um base manager com a oferta de disciplina
        # Cria um queryset com a oferta de disciplina
        query_set = MagicMock()
        # Faz o manager retornar a query_set
        # Faz a query_set retornar a oferta de disciplina
        query_set.__iter__.return_value = [oferta_disciplina]

        lista_espera = self.controlador._verificar_lista_espera(query_set)
        self.assertEqual(lista_espera, [])


# TESTES DE INTEGRAÇÃO


class RealizarInscricaoIntegracaoTestCase(TestCase):
    def setUp(self):
        self.controlador = ControladorInscricao()
        self.controlador.template_name = "realizar_inscricao.html"
        self.controlador.success_url = "/"

    @patch("core.views.render")
    def test_realizar_inscricao_em_disciplina_sem_vagas(self, mock_render):
        # Cria um aluno
        aluno = Aluno.objects.create(nome="Aluno Teste")
        # Cria uma disciplina
        disciplina = Disciplina.objects.create(nome="Disciplina", codigo="DISC01")
        # Cria um professor
        professor = Professor.objects.create(nome="Professor")
        # Cria uma turma
        turma = Turma.objects.create(codigo="T01")

        # Cria uma oferta de disciplina com 2 créditos
        oferta_disciplina = OfertaDisciplina.objects.create(
            disciplina=disciplina,
            professor=professor,
            turma=turma,
            vagas=0,
        )

        oferta_disciplina.save()

        # Emulando a lógica do ORM
        # Cria um base manager com a oferta de disciplina
        # Cria um queryset com a oferta de disciplina
        query_set = OfertaDisciplina.objects.all()

        with patch.object(
            self.controlador,
            "get",
            return_value=query_set,
        ) as mock_get:
            response = self.controlador.realizar_inscricao(
                request=None,
                context={},
                aluno=aluno,
                ofertas=query_set,
                ofertas_cursando=[],
            )
            # Verifica se o método get não foi chamado
            mock_get.assert_not_called()

        # Verifica se a função render foi chamada

        mock_render.assert_called_once_with(
            None,
            self.controlador.template_name,
            {
                "lista_espera": [oferta_disciplina],
                "aluno": aluno,
            },
        )
