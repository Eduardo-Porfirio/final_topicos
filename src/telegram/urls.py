from django.urls import path
from . import views

urlpatterns = [
    path('management/', views.telegram_management_view, name='telegram_management'),
    path('create-group/<int:turma_id>/', views.create_group_for_turma_view, name='telegram_create_group'),
    path('disparos/', views.telegram_disparos_view, name='telegram_disparos'),
    path('disparar/executar/', views.telegram_disparar_action_view, name='telegram_disparar_executar'),
    path('settings/', views.telegram_settings_view, name='telegram_settings'),
    path('webhook/', views.telegram_webhook_view, name='telegram_webhook'),
]
