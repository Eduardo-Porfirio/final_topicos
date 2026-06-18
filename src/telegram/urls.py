from django.urls import path
from . import views

urlpatterns = [
    path('management/', views.telegram_management_view, name='telegram_management'),
    path('create-group/<int:turma_id>/', views.create_group_for_turma_view, name='telegram_create_group'),
    path('disparos/', views.telegram_disparos_view, name='telegram_disparos'),
    path('settings/', views.telegram_settings_view, name='telegram_settings'),
    path('webhook/', views.telegram_webhook_view, name='telegram_webhook'),
]
