from django.urls import path

from . import views

urlpatterns = [
    path("", views.list_noticias_view, name="list_noticias"),
    path("nova/", views.create_noticia_view, name="create_noticia"),
    path("editar/<int:pk>/", views.edit_noticia_view, name="edit_noticia"),
    path("excluir/<int:pk>/", views.delete_noticia_view, name="delete_noticia"),
    path("api/consultar/", views.consultar_todas_noticias, name="consultar_todas_noticias"),
    path("cadastrar/", views.cadastrar_noticia_view, name="cadastrar_noticia"),
    path(
        "consultar/<int:id>/",
        views.consultar_noticia_por_turma,
        name="consultar_noticia_por_turma",
    ),
]
