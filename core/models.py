from django.contrib.auth.models import User
from django.db import models


class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10)
    pre_requisito = models.ManyToManyField("self", symmetrical=False, blank=True)

    def __str__(self):
        return self.nome


class Sala(models.Model):
    numero = models.CharField(max_length=10)

    def __str__(self):
        return self.numero


class Professor(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Turma(models.Model):
    codigo = models.CharField(max_length=10)

    def __str__(self):
        return self.codigo


class OfertaDisciplina(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.disciplina.nome} - {self.professor.nome}"


class Aula(models.Model):
    oferta_disciplina = models.ForeignKey(OfertaDisciplina, on_delete=models.CASCADE)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()

    def __str__(self):
        return f"{self.oferta_disciplina.disciplina.nome} ({self.horario_inicio} - {self.horario_fim})"


class Aluno(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class ListaEspera(models.Model):
    alunos = models.ManyToManyField(Aluno)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)


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
