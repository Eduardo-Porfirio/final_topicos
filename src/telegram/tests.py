import json
from unittest.mock import patch, MagicMock
from django.test import TestCase
from turma.models import Turma
from comp_curricular.models import ComponenteCurricular
from periodo_letivo.models import PeriodoLetivo
from telegram.models import TelegramGroup, TelegramAuditLog

class TelegramIntegrationTest(TestCase):
    def setUp(self):
        # Criação de dados básicos para a Turma
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

    @patch('urllib.request.urlopen')
    def test_manual_create_group_success(self, mock_urlopen):
        """
        Testa se ao acionar a view manual, o sistema busca alunos,
        chama o Telethon e cria o TelegramGroup.
        """
        # Cria um aluno para a turma
        from aluno.models import Aluno
        Aluno.objects.create(
            matricula="2221101030",
            idturma=self.turma,
            num_telefone="(49) 999859750",
            nmaluno="Eduardo Vitor"
        )

        # Configura o mock para retornar sucesso
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({
            "status": "success",
            "chat_id": 123456789,
            "turma": "Turma Teste"
        }).encode('utf-8')
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Simula login
        from django.contrib.auth.models import User
        user = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        self.client.force_login(user)

        # Chama a view via POST
        from django.urls import reverse
        response = self.client.post(reverse('telegram_create_group', args=[self.turma.idturma]))

        # Verificações
        self.assertEqual(response.status_code, 302) # Redirecionamento
        self.assertTrue(mock_urlopen.called)
        
        # Verifica se o grupo foi criado com a contagem correta de membros (1 aluno)
        self.assertEqual(TelegramGroup.objects.count(), 1)
        grupo = TelegramGroup.objects.first()
        self.assertEqual(grupo.total_membros, 1)
        
        # Verifica se o log de auditoria foi criado
        self.assertEqual(TelegramAuditLog.objects.filter(tipo='GRP', sucesso=True).count(), 1)

    def test_manual_create_group_already_exists(self):
        """Testa se o sistema impede a criação duplicada de grupo."""
        # Cria um grupo prévio
        TelegramGroup.objects.create(id_telegram=999, turma=self.turma)
        
        from django.contrib.auth.models import User
        user = User.objects.create_superuser('admin2', 'admin2@test.com', 'pass')
        self.client.force_login(user)

        from django.urls import reverse
        response = self.client.post(reverse('telegram_create_group', args=[self.turma.idturma]))
        
        self.assertEqual(TelegramGroup.objects.count(), 1) # Continua sendo 1
