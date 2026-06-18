import json
import re
import urllib.request

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# ----------------- GERENCIAMENTO DA INTERFACE -----------------
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from comp_curricular.models import ComponenteCurricular
from noticia.models import Noticia
from turma.models import Turma

from .forms import TelegramSettingsForm
from .models import TelegramAuditLog, TelegramGroup, TelegramSettings
from .services import create_telegram_group


@login_required
def telegram_management_view(request):
    total_grupos = TelegramGroup.objects.count()
    grupos_ativos = TelegramGroup.objects.filter(ativo=True).count()
    total_mensagens = TelegramAuditLog.objects.filter(tipo="MSG", sucesso=True).count()
    total_usuarios = sum(g.total_membros for g in TelegramGroup.objects.all())

    # 1. Paginação dos Logs de Auditoria
    logs_qs = TelegramAuditLog.objects.all().order_by("-data_evento")
    paginator_logs = Paginator(logs_qs, 5)
    page_logs_number = request.GET.get("page_logs")
    ultimos_logs = paginator_logs.get_page(page_logs_number)

    # 2. Paginação da lista de grupos
    grupos_qs = TelegramGroup.objects.all().order_by("-data_criacao")
    paginator_grupos = Paginator(grupos_qs, 5)
    page_grupos_number = request.GET.get("page_grupos")
    lista_grupos = paginator_grupos.get_page(page_grupos_number)

    # 3. Paginação das turmas sem grupo
    turmas_sem_grupo_qs = Turma.objects.filter(telegram_group__isnull=True).order_by(
        "idturma"
    )
    paginator_turmas = Paginator(turmas_sem_grupo_qs, 5)
    page_turmas_number = request.GET.get("page_turmas")
    turmas_sem_grupo = paginator_turmas.get_page(page_turmas_number)

    # Verifica se o bot_token está configurado no BD ou no .env
    configuracao = TelegramSettings.get_settings()
    api_configurada = bool(configuracao.bot_token) or bool(settings.TELEGRAM_BOT_TOKEN)

    # Checagem de Saúde do Microserviço Telethon
    telethon_status = {"online": False, "authorized": False}
    try:
        url_health = "http://telethon_service:8001/health"
        with urllib.request.urlopen(url_health, timeout=2) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                telethon_status["online"] = True
                telethon_status["authorized"] = data.get("authorized", False)
    except:
        pass

    context = {
        "total_grupos": total_grupos,
        "total_mensagens": total_mensagens,
        "total_usuarios": total_usuarios,
        "grupos_ativos": grupos_ativos,
        "ultimos_logs": ultimos_logs,
        "lista_grupos": lista_grupos,
        "turmas_sem_grupo": turmas_sem_grupo,
        "api_configurada": api_configurada,
        "telethon_status": telethon_status,
    }
    return render(request, "telegram/management.html", context)


@login_required
@require_http_methods(["POST"])
def create_group_for_turma_view(request, turma_id):
    """
    Acionada via botão manual no dashboard.
    Busca os alunos da turma, limpa os números e solicita a criação do grupo.
    """
    turma = get_object_or_404(Turma, pk=turma_id)

    if hasattr(turma, "telegram_group"):
        messages.warning(request, f"A turma {turma} já possui um grupo de Telegram.")
        return redirect("telegram_management")

    # Busca alunos vinculados e formata números de telefone
    alunos = turma.alunos.all()
    users_to_add = []
    for aluno in alunos:
        # Remove caracteres não numéricos
        phone = re.sub(r"\D", "", aluno.num_telefone)
        if phone:
            # Garante o prefixo +55 (Brasil) se não houver
            if not phone.startswith("55"):
                phone = "55" + phone
            users_to_add.append("+" + phone)

    nome_grupo = f"Turma {turma.idturma} - {turma.idcompcurricular.nmcompcurricular}"

    # Inclui o Bot de Gestão como membro inicial para que ele possa gerenciar o grupo
    # Buscamos o username dinamicamente se possível, ou usamos o fixo identificado
    bot_username = "@portal_sigaa_bot"
    if bot_username not in users_to_add:
        users_to_add.append(bot_username)

    # Chama o microserviço Telethon
    resultado = create_telegram_group(nome_grupo, users_to_add=users_to_add)

    if resultado and resultado.get("status") == "success":
        chat_id = resultado.get("chat_id")

        # Garante que o ID seja salvo no formato negativo esperado pelo Telegram Bot API para grupos
        chat_id_normalizado = chat_id if chat_id < 0 else -chat_id

        # Cria o registro do grupo no Django
        grupo = TelegramGroup.objects.create(
            id_telegram=chat_id_normalizado,
            turma=turma,
            total_membros=len(users_to_add),
            ativo=True,
        )

        TelegramAuditLog.objects.create(
            tipo="GRP",
            telegram_group=grupo,
            descricao=f"Grupo criado MANUALMENTE para {turma}. {len(users_to_add)} membros convidados.",
            sucesso=True,
        )
        messages.success(
            request, f"Grupo criado com sucesso no Telegram! ID: {chat_id}"
        )
    else:
        TelegramAuditLog.objects.create(
            tipo="GRP",
            descricao=f"Falha na criação MANUAL do grupo para a Turma {turma.idturma}",
            sucesso=False,
        )
        messages.error(
            request,
            "Erro ao criar o grupo. Verifique se o microserviço Telethon está logado e ativo.",
        )

    return redirect("telegram_management")


@login_required
def telegram_disparos_view(request):
    # Exibe apenas as turmas que possuem grupos do Telegram configurados no sistema
    turmas = Turma.objects.filter(telegram_group__isnull=False)
    context = {"turmas": turmas}
    return render(request, "telegram/disparos.html", context)


@login_required
@require_http_methods(["POST"])
def telegram_disparar_action_view(request):
    mensagem = request.POST.get("mensagem", "").strip()
    turma_id = request.POST.get("turma_alvo")

    if not mensagem:
        messages.error(request, "A mensagem não pode ser vazia.")
        return redirect("telegram_disparos")

    if not turma_id:
        messages.error(request, "Selecione uma turma para realizar o disparo.")
        return redirect("telegram_disparos")

    # Busca o grupo associado à turma
    grupo = TelegramGroup.objects.filter(turma_id=turma_id, ativo=True).first()
    if not grupo:
        messages.error(
            request, "Essa turma não possui um grupo de Telegram ativo configurado."
        )
        return redirect("telegram_disparos")

    # Envia a mensagem
    sucesso = enviar_mensagem_telegram(grupo.id_telegram, mensagem)

    # Registra no log de auditoria
    TelegramAuditLog.objects.create(
        tipo="MSG",
        telegram_group=grupo,
        descricao=f"Disparo manual para turma: {mensagem[:60]}...",
        sucesso=sucesso,
    )

    if sucesso:
        messages.success(
            request, f"Mensagem disparada com sucesso para o grupo da Turma {turma_id}!"
        )
    else:
        messages.error(
            request,
            "Falha ao enviar a mensagem. Verifique a chave da API do Telegram nas configurações.",
        )

    return redirect("telegram_disparos")


@login_required
def telegram_settings_view(request):
    # Recupera o registro Singleton
    configuracao = TelegramSettings.get_settings()

    if request.method == "POST":
        form = TelegramSettingsForm(request.POST, instance=configuracao)
        if form.is_valid():
            # Lógica para não sobrescrever com string vazia se já havia token (por causa do password input)
            novo_token = form.cleaned_data.get("bot_token")
            if not novo_token and configuracao.bot_token:
                form.instance.bot_token = configuracao.bot_token
            form.save()
            messages.success(
                request, "Configurações do Telegram atualizadas com sucesso!"
            )
            return redirect("telegram_settings")
    else:
        form = TelegramSettingsForm(instance=configuracao)

    return render(request, "telegram/settings.html", {"form": form})


# ----------------- INTEGRAÇÃO BOT TELEGRAM -----------------


def enviar_mensagem_telegram(chat_id, texto):
    """Função utilitária para enviar mensagem via API do Telegram"""
    configuracao = TelegramSettings.get_settings()
    token = configuracao.bot_token

    if not token:
        token = settings.TELEGRAM_BOT_TOKEN

    if not token:
        print("Erro: Token do Telegram não configurado (nem no BD, nem no .env)")
        return False

    # Normaliza o ID para a API do Telegram.
    # No Telegram Bot API, IDs de grupos/supergrupos são sempre negativos.
    # Se recebermos um ID de grupo positivo (ex: de sessões anteriores), convertemos para negativo.
    chat_id_api = chat_id
    if isinstance(chat_id, (int, float)) and chat_id > 0:
        chat_id_api = -int(chat_id)
    elif isinstance(chat_id, str):
        if not chat_id.startswith('-'):
            try:
                chat_id_api = -int(chat_id)
            except ValueError:
                pass

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps(
        {"chat_id": chat_id_api, "text": texto, "parse_mode": "HTML"}
    ).encode("utf-8")

    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.status == 200
    except Exception as e:
        print(f"Erro na API do Telegram: {e}")
        return False


@csrf_exempt
@require_http_methods(["POST"])
def telegram_webhook_view(request):
    """
    Endpoint que receberá todas as mensagens que os alunos enviarem para o bot.
    O Telegram fará um POST nesta URL.
    """
    try:
        payload = json.loads(request.body)
        print(f"Payload recebido: {payload}")
        # Verifica se o payload contém uma mensagem
        if "message" in payload:
            chat_id = payload["message"]["chat"]["id"]
            texto_recebido = payload["message"].get("text", "").strip()
            print(chat_id)
            print(texto_recebido)
            # --- ROTEAMENTO DE COMANDOS ---
            if texto_recebido.startswith("/start"):
                resposta = "🤖 Olá! Eu sou o Assistente Acadêmico.\n\nUse o comando /noticias para ver os últimos avisos da sua turma."
                enviar_mensagem_telegram(chat_id, resposta)

            elif texto_recebido.startswith("/noticias") or texto_recebido.startswith(
                "/noticia"
            ):
                print("Recebido comando /noticias")
                try:
                    # 1. Identificar de qual turma é esse grupo/usuário
                    # Busca de forma resiliente ao sinal (negativo na Bot API, positivo no Telethon/Histórico)
                    id_options = [chat_id, -chat_id, abs(chat_id)]
                    chat_str = str(chat_id)
                    if chat_str.startswith("-100"):
                        try:
                            stripped_id = int(chat_str[4:])
                            id_options.extend([stripped_id, -stripped_id])
                        except ValueError:
                            pass

                    grupo = TelegramGroup.objects.filter(
                        id_telegram__in=id_options, ativo=True
                    ).first()
                    if not grupo:
                        raise TelegramGroup.DoesNotExist
                    # 2. Buscar as últimas 5 notícias da turma
                    noticias = Noticia.objects.filter(idturma=grupo.turma).order_by(
                        "-dtnoticia"
                    )[:5]
                    noticias_list = list(noticias)

                    if noticias.exists():
                        resposta = f"📰 <b>Últimas notícias de {grupo.turma.idcompcurricular.nmcompcurricular}:</b>\n\n"
                        for n in noticias:
                            resposta += f"🔸 <b>{n.titulo}</b> ({n.dtnoticia.strftime('%d/%m/%Y')})\n{n.desc_noticia}\n\n"
                    else:
                        resposta = (
                            "Não há notícias cadastradas para esta turma no momento."
                        )

                except TelegramGroup.DoesNotExist:
                    resposta = (
                        "⚠️ Este chat não está vinculado a nenhuma turma no sistema."
                    )

                # Responde ao aluno e registra no AuditLog
                sucesso = enviar_mensagem_telegram(chat_id, resposta)
                if sucesso and "grupo" in locals() and grupo:
                    # Atualiza o status de flenvio das notícias retornadas para True
                    for n in noticias_list:
                        if not n.flenvio:
                            n.flenvio = True
                            n.save()

                    TelegramAuditLog.objects.create(
                        tipo="MSG",
                        telegram_group=grupo,
                        descricao=f"Comando /noticias acionado.",
                        sucesso=True,
                    )
            elif texto_recebido.startswith("/") and texto_recebido != "/noticias":
                resposta = "⚠️ Comando inválido. Use /noticias para ver as notícias disponíveis."
                enviar_mensagem_telegram(chat_id, resposta)
        # O Telegram exige que sempre retornemos 200 OK, senão ele tenta reenviar
        return JsonResponse({"status": "ok"})
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "JSON inválido"}, status=400)
    except Exception as e:
        print(f"Erro no webhook: {e}")
        return JsonResponse({"status": "error"}, status=500)
