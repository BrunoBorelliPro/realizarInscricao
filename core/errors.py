class InscritoEmDuasDisciplinasIguaisError(Exception):
    def __init__(self, disciplina):
        self.disciplina = disciplina

    def __str__(self):
        return f"Inscrição duplicada na disciplina {self.disciplina}"


class NumeroDeCreditosExcedidoError(Exception):
    def __str__(self):
        return "Número de créditos excedido"


class ChoqueDeHorarioError(Exception):
    def __init__(self, oferta1, oferta2):
        self.oferta1 = oferta1
        self.oferta2 = oferta2

    def __str__(self):
        return f"Choque de horário: {self.oferta1} | {self.oferta2}"
