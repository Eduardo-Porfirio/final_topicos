from django.test import TestCase
from unittest.mock import patch
from .models import Aluno
from turma.models import Turma
from comp_curricular.models import ComponenteCurricular
from periodo_letivo.models import PeriodoLetivo
from telegram.models import TelegramGroup, TelegramAuditLog

class AlunoSignalTest(TestCase):
    def setUp(self):
        self.periodo = PeriodoLetivo.objects.create(
            nmperiodo="2026.1",
            dtinicial="2026-01-01",
            dtfinal="2026-06-01",
            status=True
        )
        self.componente = ComponenteCurricular.objects.create(
            idperiodoletivo=self.periodo,
            codigo="TEST101",
            nmcompcurricular="Componente de Teste",
            status=True
        )
        self.turma = Turma.objects.create(
            idcompcurricular=self.componente,
            matricula=123,
            flstatus=True
        )
        # Cria o grupo para a turma
        self.grupo = TelegramGroup.objects.create(
            id_telegram=-12345,
            turma=self.turma,
            total_membros=2,
            ativo=True
        )
        # Cria o aluno (com status True)
        self.aluno = Aluno.objects.create(
            matricula="2221101030",
            idturma=self.turma,
            num_telefone="(49) 999859750",
            nmaluno="Eduardo Vitor",
            flstatus=True
        )

    @patch('aluno.signals.remove_telegram_group_member')
    def test_aluno_inactivated_triggers_removal(self, mock_remove):
        mock_remove.return_value = True

        # Inativa o aluno
        self.aluno.flstatus = False
        self.aluno.save()

        # Verifica se a função de remoção foi chamada com os parâmetros corretos
        mock_remove.assert_called_once_with(-12345, '+5549999859750')
        
        # Verifica se o log de auditoria do tipo USR foi criado
        self.assertEqual(TelegramAuditLog.objects.filter(tipo='USR', sucesso=True).count(), 1)
