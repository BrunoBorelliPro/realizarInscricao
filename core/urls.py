from django.urls import path

from core import views


urlpatterns = [
    path("", views.login_view, name="login"),
    path(
        "inscricao/<aluno_id>", views.ControladorInscricao.as_view(), name="inscricao"
    ),
]
