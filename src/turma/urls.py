from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_turmas_view, name='list_turmas'),
]
