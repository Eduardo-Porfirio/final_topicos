from django.urls import path

from . import views

urlpatterns = [
    path("", views.list_noticias_view, name="list_noticias"),
    path("api/consultar/", views.consultar_todas_noticias, name="consultar_todas_noticias"),
    path("cadastrar/", views.cadastrar_noticia_view, name="cadastrar_noticia"),
    path(
        "consultar/<int:id>/",
        views.consultar_noticia_por_turma,
        name="consultar_noticia_por_turma",
    ),
]
