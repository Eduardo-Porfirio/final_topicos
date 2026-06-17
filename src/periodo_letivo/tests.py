from django.test import TestCase
from .models import PeriodoLetivo

class PeriodoLetivoModelTest(TestCase):
    def setUp(self):
        PeriodoLetivo.objects.create(
            nmperiodo="2026.1",
            dtinicial="2026-02-01",
            dtfinal="2026-06-30",
            status=True
        )

    def test_periodo_str(self):
        """O método __str__ deve retornar o nome do período"""
        periodo = PeriodoLetivo.objects.get(nmperiodo="2026.1")
        self.assertEqual(str(periodo), "2026.1")

    def test_periodo_creation(self):
        """Verifica se o período foi criado corretamente"""
        periodo = PeriodoLetivo.objects.get(nmperiodo="2026.1")
        self.assertTrue(periodo.status)
        self.assertEqual(periodo.nmperiodo, "2026.1")
