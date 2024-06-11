import pprint
from django.contrib.auth import authenticate, logout, login
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from core.forms import LoginForm
from core.models import Aluno, Disciplina


class ControladorInscricao(TemplateView):
    template_name = "realizar_inscricao.html"
    success_url = "/"

    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect("login")

        aluno_id = self.kwargs.get("aluno_id")

        context = super().get_context_data(**kwargs)
        context["aluno"] = Aluno.objects.get(id=aluno_id)

        disciplinas = Disciplina.objects.all()

        disciplinas_cursadas = [
            ofertaDisciplina.disciplina
            for ofertaDisciplina in [
                participacao.ofertaDisciplina
                for participacao in context["aluno"].participacao_set.all()
            ]
        ]

        disciplinas = disciplinas.exclude(
            id__in=[disciplina.id for disciplina in disciplinas_cursadas]
        )
        dis = []
        for disciplina in disciplinas:
            dis.append(
                {
                    "requisitos": [
                        d in disciplinas_cursadas
                        for d in [
                            pre_requisito
                            for pre_requisito in disciplina.pre_requisito.all()
                        ]
                    ],
                    "disciplina": disciplina,
                }
            )

        context["disciplinas"] = [d["disciplina"] for d in dis if all(d["requisitos"])]
        return context


def login_view(request):
    context = {}
    context["alunos"] = Aluno.objects.all()
    print(request.POST)
    if request.method == "POST":
        return redirect("inscricao", aluno_id=request.POST.get("aluno"))

    return render(request, "login.html", context)
