from django.test import TestCase
from core.models import Aula


class AulaTestCase(TestCase):
    def test_aula_creation(self):
        aula = Aula.objects.create(nome="Aula de Matemática")
        self.assertEqual(aula.nome, "Aula de Matemática")
