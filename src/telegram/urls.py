from django.urls import path
from . import views

urlpatterns = [
    path('management/', views.telegram_management_view, name='telegram_management'),
    path('disparos/', views.telegram_disparos_view, name='telegram_disparos'),
]
