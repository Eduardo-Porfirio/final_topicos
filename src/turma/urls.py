from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_turmas_view, name='list_turmas'),
    path('nova/', views.create_turma_view, name='create_turma'),
    path('editar/<int:pk>/', views.edit_turma_view, name='edit_turma'),
    path('excluir/<int:pk>/', views.delete_turma_view, name='delete_turma'),
    path('<int:pk>/alunos/', views.list_alunos_by_turma_view, name='list_alunos_by_turma'),
    path('aluno/<str:matricula>/toggle/', views.toggle_aluno_status_view, name='toggle_aluno_status'),
]
