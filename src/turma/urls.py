from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_turmas_view, name='list_turmas'),
    path('nova/', views.create_turma_view, name='create_turma'),
    path('editar/<int:pk>/', views.edit_turma_view, name='edit_turma'),
    path('excluir/<int:pk>/', views.delete_turma_view, name='delete_turma'),
]
