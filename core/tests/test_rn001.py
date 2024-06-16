from django.test import TestCase
from unittest.mock import MagicMock, create_autospec, patch
from core.errors import NumeroDeCreditosExcedidoError
from core.models import (
    Aluno,
    Aula,
    Disciplina,
    OfertaDisciplina,
    Participacao,
    Professor,
    Sala,
    Turma,
)
from core.views import ControladorInscricao

# RN001: Quantidade máxima de inscrições por semestre letivo
# Descricao: Em um semestre letivo, um aluno não pode se
# inscrever em uma quantidade de turmas cuja soma de créditos
# nas disciplinas correspondentes ultrapasse vinte


# TESTES DE UNIDADE


class AlunoTestCase(TestCase):
    def setUp(self):
        self.aluno = Aluno.objects.create(nome="Aluno Teste")

    def test_get_creditos_retorna_o_numero_correto_de_creditos(self):
        # Mock para Participacao e OfertaDisciplina
        mock_participacao = MagicMock(spec=Participacao)
        mock_oferta_disciplina = MagicMock()

        # Define o retorno esperado para a função creditos
        mock_oferta_disciplina.creditos.return_value = 4

        # Associa mock_oferta_disciplina ao mock_participacao
        mock_participacao.ofertaDisciplina = mock_oferta_disciplina
        mock_participacao.status = "C"

        # Mock para o queryset de Participacao
        mock_participacao_manager = MagicMock(spec=Participacao.objects)
        mock_participacao_manager.filter.return_value = [
            mock_participacao,
            mock_participacao,
        ]

        with patch.object(Aluno, "participacao_set", mock_participacao_manager):
            # Chama a função get_creditos
            creditos = self.aluno.get_creditos()
        # Verifica se o valor retornado está correto (4 créditos multiplicados por 2)
        self.assertEqual(creditos, 8)


class OfertaDisciplinaTestCase(TestCase):
    def setUp(self):
        self.oferta_disciplina = OfertaDisciplina.objects.create(
            disciplina=Disciplina.objects.create(nome="Disciplina Teste"),
            professor=Professor.objects.create(nome="Professor Teste"),
            turma=Turma.objects.create(codigo="T1"),
            vagas=40,
        )

    def test_creditos_retorna_o_numero_correto_de_creditos(self):
        # Cria uma aula
        aula1 = Aula.objects.create(
            sala=Sala.objects.create(numero="S1"),
            dia_da_semana=Aula.DiaDaSemana.SEGUNDA,
            horario_inicio="08:00",
            horario_fim="10:00",
        )
        aula2 = Aula.objects.create(
            sala=Sala.objects.create(numero="S2"),
            dia_da_semana=Aula.DiaDaSemana.QUARTA,
            horario_inicio="08:00",
            horario_fim="10:00",
        )
        # Associa a aula à oferta de disciplina
        self.oferta_disciplina.aulas.add(aula1)
        self.oferta_disciplina.aulas.add(aula2)
        # Verifica se a função creditos retorna o número correto de créditos
        creditos = self.oferta_disciplina.creditos()
        self.assertEqual(creditos, 2)


class RealizarInscricaoTestCase(TestCase):

    def setUp(self):
        self.controlador = ControladorInscricao()
        self.controlador.template_name = "realizar_inscricao.html"
        self.controlador.success_url = "/"

    def test_realizar_inscricao_mais_de_20_creditos(self):
        # Cria um aluno com 19 créditos
        aluno = MagicMock(spec=Aluno)
        aluno.get_creditos.return_value = 19
        # Cria uma oferta de disciplina com 2 créditos
        oferta_disciplina = MagicMock(spec=OfertaDisciplina)
        oferta_disciplina.creditos.return_value = 2
        oferta_disciplina.verificar_choque_de_horario.return_value = False
        # Cria um base manager com a oferta de disciplina
        manager = MagicMock(spec=OfertaDisciplina.objects)
        # Cria um queryset com a oferta de disciplina
        query_set = MagicMock()
        # Faz o manager retornar a query_set
        manager.filter.return_value = query_set
        # Faz a query_set retornar a oferta de disciplina
        query_set.__iter__.return_value = [oferta_disciplina]
        with self.assertRaises(NumeroDeCreditosExcedidoError):
            self.controlador.realizar_inscricao(
                request=None,
                context=None,
                aluno=aluno,
                ofertas=query_set,
                ofertas_cursando=[],
            )

    def test_realizar_inscricao_com_20_creditos(self):
        # Cria um aluno com 18 créditos
        aluno = MagicMock(spec=Aluno)
        aluno.get_creditos.return_value = 18
        # Cria uma oferta de disciplina com 2 créditos
        oferta_disciplina = MagicMock(spec=OfertaDisciplina)
        oferta_disciplina.creditos.return_value = 2
        oferta_disciplina.verificar_choque_de_horario.return_value = False
        oferta_disciplina.vagas_ocupadas.return_value = 0
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

        with patch.object(self.controlador, "get", return_value=True) as mock_get:
            self.controlador.realizar_inscricao(
                request=None,
                context=None,
                aluno=aluno,
                ofertas=query_set,
                ofertas_cursando=[],
            )
            mock_get.assert_called()

        # Verifica se o método get_creditos foi chamado
        aluno.get_creditos.assert_called()
        # Verifica se a função creditos foi chamada
        oferta_disciplina.creditos.assert_called()
        # Verifica se a função verificar_choque_de_horario foi chamada
        oferta_disciplina.verificar_choque_de_horario.assert_called()
        # Verifica se a função inscrever_aluno foi chamada
        oferta_disciplina.inscrever_aluno.assert_called_with(aluno)

    def test__get_creditos(self):
        # Cria um aluno com 19 créditos
        aluno = MagicMock(spec=Aluno)
        aluno.get_creditos.return_value = 19
        # Cria uma oferta de disciplina com 2 créditos
        oferta_disciplina = MagicMock(spec=OfertaDisciplina)
        oferta_disciplina.creditos.return_value = 2
        oferta_disciplina.verificar_choque_de_horario.return_value = False
        # Cria um base manager com a oferta de disciplina
        manager = MagicMock(spec=OfertaDisciplina.objects)
        # Cria um queryset com a oferta de disciplina
        query_set = MagicMock()
        # Faz o manager retornar a query_set
        manager.filter.return_value = query_set
        # Faz a query_set retornar a oferta de disciplina
        query_set.__iter__.return_value = [oferta_disciplina]

        creditos = self.controlador._get_creditos(aluno, query_set)

        # Verifica se o método get_creditos foi chamado
        aluno.get_creditos.assert_called()
        # Verifica se a função creditos foi chamada
        oferta_disciplina.creditos.assert_called()
        self.assertEqual(creditos, 21)


# TESTES DE INTEGRAÇÃO


class RealizarInscricaoIntegracaoTestCase(TestCase):
    def setUp(self):
        self.controlador = ControladorInscricao()
        self.controlador.template_name = "realizar_inscricao.html"
        self.controlador.success_url = "/"

        self.aluno = Aluno.objects.create(nome="Aluno Teste")

        self.oferta_disciplina = OfertaDisciplina.objects.create(
            disciplina=Disciplina.objects.create(nome="Disciplina Teste"),
            professor=Professor.objects.create(nome="Professor Teste"),
            turma=Turma.objects.create(codigo="T1"),
            vagas=40,
        )

    def test_realizar_inscricao_com_20_creditos(self):
        # Cria 20 aulas sem horários conflitantes
        aulas = []
        sala = Sala.objects.create(numero="S1")
        for i in range(20):
            hora_inicio = f"{i+1}:00"
            hora_fim = f"{i+2}:00"
            aula = Aula.objects.create(
                sala=sala,
                dia_da_semana=Aula.DiaDaSemana.SEGUNDA,
                horario_inicio=hora_inicio,
                horario_fim=hora_fim,
            )
            aulas.append(aula)

        # Associa as aulas à oferta de disciplina
        for aula in aulas:
            self.oferta_disciplina.aulas.add(aula)

        id_ofertas = [self.oferta_disciplina.id]
        ofertas = OfertaDisciplina.objects.filter(id__in=id_ofertas)

        with patch.object(self.controlador, "get", return_value=True) as mock_get:
            self.controlador.realizar_inscricao(
                request=None,
                context=None,
                aluno=self.aluno,
                ofertas=ofertas,
                ofertas_cursando=[],
            )
            mock_get.assert_called()

    def test_realizar_inscricao_com_21_creditos(self):
        # Cria 21 aulas sem horários conflitantes
        num_aulas = 21
        aulas = []
        sala = Sala.objects.create(numero="S1")
        for i in range(num_aulas):
            hora_inicio = f"{i+1}:00"
            hora_fim = f"{i+2}:00"
            aula = Aula.objects.create(
                sala=sala,
                dia_da_semana=Aula.DiaDaSemana.SEGUNDA,
                horario_inicio=hora_inicio,
                horario_fim=hora_fim,
            )
            aulas.append(aula)

        # Associa as aulas à oferta de disciplina
        for aula in aulas:
            self.oferta_disciplina.aulas.add(aula)

        id_ofertas = [self.oferta_disciplina.id]
        ofertas = OfertaDisciplina.objects.filter(id__in=id_ofertas)

        with self.assertRaises(NumeroDeCreditosExcedidoError):
            self.controlador.realizar_inscricao(
                request=None,
                context=None,
                aluno=self.aluno,
                ofertas=ofertas,
                ofertas_cursando=[],
            )
