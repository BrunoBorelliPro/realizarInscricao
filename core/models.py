from django.contrib.auth.models import User
from django.db import models

from core.errors import ChoqueDeHorarioError


class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10)
    pre_requisito = models.ManyToManyField("self", symmetrical=False, blank=True)

    def __str__(self):
        return self.nome

    def verificar_pre_requisitos(self, aluno):
        for pre_requisito in self.pre_requisito.all():
            if not aluno.participacao_set.filter(
                ofertaDisciplina__disciplina=pre_requisito, status="A"
            ).exists():
                return False
        return True


class Sala(models.Model):
    numero = models.CharField(max_length=10)

    def __str__(self):
        return self.numero


class Professor(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Professores"


class Turma(models.Model):
    codigo = models.CharField(max_length=10)

    def __str__(self):
        return self.codigo


class OfertaDisciplina(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    aulas = models.ManyToManyField("Aula")
    vagas = models.IntegerField(default=40)

    def __str__(self):
        return f"{self.disciplina.nome} - {self.professor.nome}"

    def creditos(self):
        return self.aulas.count()

    def verificar_choque_de_horario(self, lista_de_ofertas):
        # Verifica se há choque de horário
        for o in lista_de_ofertas:
            if self.id != o.id:
                if self._verificar_choque_de_horario(o):
                    return o
        return False

    def _verificar_choque_de_horario(self, oferta_disciplina):
        for aula in self.aulas.all():
            for aula_oferta in oferta_disciplina.aulas.all():
                if aula.verificar_choque_de_horario(aula_oferta):
                    return True
        return False

    def horarios(self):
        return [aula.horario() for aula in self.aulas.all()]

    def vagas_ocupadas(self):
        return self.participacao_set.filter(status="C").count()

    class Meta:
        verbose_name_plural = "Ofertas de Disciplinas"


class Aula(models.Model):
    class DiaDaSemana(models.TextChoices):
        SEGUNDA = "SEG", "Segunda"
        TERCA = "TER", "Terça"
        QUARTA = "QUA", "Quarta"
        QUINTA = "QUI", "Quinta"
        SEXTA = "SEX", "Sexta"

    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    dia_da_semana = models.CharField(
        max_length=3, choices=DiaDaSemana.choices, default=DiaDaSemana.SEGUNDA
    )

    def __str__(self):
        return f"Sala: {self.sala} ({self.dia_da_semana.capitalize()}: {self.horario_inicio} - {self.horario_fim})"

    def horario(self):
        return f"{self.dia_da_semana.capitalize()}: {self.horario_inicio} - {self.horario_fim}"

    def verificar_choque_de_horario(self, aula):
        if self.dia_da_semana != aula.dia_da_semana:
            return False

        if (
            self.horario_inicio >= aula.horario_fim
            or self.horario_fim <= aula.horario_inicio
        ):
            return False

        return True


class Aluno(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

    def get_creditos(self):
        return sum(
            [
                participacao.ofertaDisciplina.creditos()
                for participacao in self.participacao_set.filter(status="C")
            ]
        )

    def get_disciplinas_disponiveis(self):
        disciplinas = Disciplina.objects.all()
        for participacao in self.participacao_set.all():
            disciplinas = disciplinas.exclude(
                id=participacao.ofertaDisciplina.disciplina.id
            )
        for disciplina in disciplinas:
            if not disciplina.verificar_pre_requisitos(self):
                disciplinas = disciplinas.exclude(id=disciplina.id)

        return disciplinas


class ListaEspera(models.Model):
    alunos = models.ManyToManyField(Aluno)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.disciplina.nome} - {self.alunos.count()} alunos"

    class Meta:
        verbose_name_plural = "Listas de Espera"


class Participacao(models.Model):

    class Status(models.TextChoices):
        APROVADO = "A", "Aprovado"
        REPROVADO = "R", "Reprovado"
        CURSANDO = "C", "Cursando"

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    ofertaDisciplina = models.ForeignKey(OfertaDisciplina, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1, choices=Status.choices, default=Status.CURSANDO
    )

    def __str__(self):
        return f"{self.aluno.nome} - {self.ofertaDisciplina}"

    class Meta:
        verbose_name_plural = "Participações"
