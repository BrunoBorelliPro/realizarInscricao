from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from core.errors import (
    ChoqueDeHorarioError,
    InscritoEmDuasDisciplinasIguaisError,
    NumeroDeCreditosExcedidoError,
)
from core.models import Aluno, Disciplina, ListaEspera, OfertaDisciplina


class ControladorInscricao(TemplateView):
    template_name = "realizar_inscricao.html"
    success_url = "/"
    aluno: Aluno

    def get_context_data(self, **kwargs):
        aluno_id = self.kwargs.get("aluno_id")

        context = super().get_context_data(**kwargs)
        aluno = Aluno.objects.get(id=aluno_id)

        context["passo"] = "selecionar"
        context["aluno"] = aluno
        context["disciplinas"] = aluno.get_disciplinas_disponiveis()
        context["inscricoes"] = aluno.participacao_set.filter(status="C")
        context["inscricoes_espera"] = ListaEspera.objects.filter(alunos=aluno)

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context["error"] = kwargs.get("error")
        context["success"] = kwargs.get("success")

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        aluno_id = self.kwargs.get("aluno_id")

        if request.POST.get("passo") == "selecionar":
            return self.selecionar_disciplinas(request, context)
        elif request.POST.get("passo") == "confirmar":
            try:
                return self.realizar_inscricao(request, context)
            except Exception as e:
                print(e)
                return self.get(request, error=e)

        elif request.POST.get("passo") == "lista_espera":
            return self.entrar_na_lista_espera(request, context)

        elif request.POST.get("passo") == "cancelar":
            return self.cancelar_inscricao(request, context)

        elif request.POST.get("passo") == "sair_lista_espera":
            return self.sair_lista_espera(request, context)

        return redirect("inscricao", aluno_id=aluno_id)

    def selecionar_disciplinas(self, request, context):
        aluno_id = self.kwargs.get("aluno_id")

        context["passo"] = "confirmar"
        aluno = Aluno.objects.get(id=aluno_id)
        context["aluno"] = aluno

        codigo_disciplinas = request.POST.getlist("disciplinas")
        ofertas = OfertaDisciplina.objects.filter(
            disciplina__codigo__in=codigo_disciplinas
        )

        context["ofertas"] = ofertas
        return render(request, self.template_name, context)

    def realizar_inscricao(self, request, context):
        # Obtendo dados necessários
        aluno_id = self.kwargs.get("aluno_id")
        aluno = Aluno.objects.get(id=aluno_id)
        id_ofertas = request.POST.getlist("ofertas")
        ofertas = OfertaDisciplina.objects.filter(id__in=id_ofertas)

        for oferta in ofertas:
            # Verifica se o aluno se inscreveu em duas disciplinas iguais
            num = ofertas.filter(disciplina=oferta.disciplina)
            if len(num) > 1:
                raise InscritoEmDuasDisciplinasIguaisError(num[0].disciplina.codigo)

        if not ofertas:
            return redirect("inscricao", aluno_id=aluno_id)

        ofertas_cursando_ids = aluno.participacao_set.filter(status="C").values_list(
            "ofertaDisciplina", flat=True
        )
        ofertas_cursando = OfertaDisciplina.objects.filter(id__in=ofertas_cursando_ids)
        # Obtendo dados necessários - fim

        # Verificar choque de horários
        # Caso haja choque de horários, uma exceção será lançada,
        #  a inscrição não será realizada e a mensagem de erro será exibida
        choque = self._verificar_choque_de_horario(ofertas, ofertas_cursando)
        if choque:
            raise ChoqueDeHorarioError(
                f"{choque[0]} - {choque[0].horarios()}",
                f"{choque[1]} - {choque[1].horarios()}",
            )
        # Verificar choque de horários - fim

        # Verificar número de créditos
        # Caso o número de créditos exceda 20, uma exceção será lançada,
        # a inscrição não será realizada e a mensagem de erro será exibida
        creditos = self.get_creditos(aluno, ofertas)
        print(f"Créditos: {creditos}")
        if creditos > 20:
            raise NumeroDeCreditosExcedidoError()
        # Verificar número de créditos - fim

        # Verificar disponibilidade de vagas
        # Caso a oferta já tenha atingido o limite de inscrições, o aluno será adicionado à lista de espera
        lista_espera = self._verificar_lista_espera(ofertas)
        if lista_espera:
            ofertas = ofertas.exclude(id__in=[oferta.id for oferta in lista_espera])
        # Verificar disponibilidade de vagas - fim

        # Inscrever o aluno nas disciplinas
        # Caso o aluno não esteja cursando a disciplina, ele será inscrito
        # Caso o aluno já esteja cursando a disciplina, a inscrição será ignorada
        for oferta in ofertas:
            cursando = oferta.participacao_set.filter(aluno=aluno, status="C")
            if not cursando:
                oferta.participacao_set.create(aluno=aluno, status="C")
        # Inscrever o aluno nas disciplinas - fim

        # Adicionar o aluno à lista de espera
        # Caso o aluno tenha sido adicionado à lista de espera,
        # ele será redirecionado para a página informando em quais
        # disciplinas ele foi adicionado à lista de espera
        if lista_espera:
            print(f"Lista de espera: {lista_espera}")
            context["lista_espera"] = lista_espera
            context["aluno"] = aluno

            return render(request, self.template_name, context)
        # Adicionar o aluno à lista de espera - fim

        return self.get(request, success="Inscrição realizada com sucesso")

    def entrar_na_lista_espera(self, request, context):
        if request.POST.get("nao_adicionar"):
            return self.get(
                request,
                warning="Inscrição realizada com sucesso nas outras disciplinas, mas o aluno não foi adicionado à lista de espera",
            )
        aluno_id = self.kwargs.get("aluno_id")
        aluno = Aluno.objects.get(id=aluno_id)
        id_disciplinas = request.POST.getlist("disciplinas")

        disciplinas = Disciplina.objects.filter(id__in=id_disciplinas)
        for disciplina in disciplinas:
            lista_espera = ListaEspera.objects.filter(disciplina=disciplina)
            if not lista_espera:
                lista_espera = ListaEspera.objects.create(disciplina=disciplina)
                lista_espera.alunos.add(aluno)
            else:
                lista_espera = lista_espera[0]
                lista_espera.alunos.add(aluno)

            lista_espera.save()

        return self.get(
            request,
            success="Aluno adicionado na lista de espera e outras disciplinas foram confirmadas",
        )

    def sair_lista_espera(self, request, context):
        aluno_id = self.kwargs.get("aluno_id")

        aluno = Aluno.objects.get(id=aluno_id)
        print(request.POST)
        lista_espera_id = request.POST.get("lista_espera_id")
        lista_espera = ListaEspera.objects.get(id=lista_espera_id)
        lista_espera.alunos.remove(aluno)

        return self.get(request, success="Aluno removido da lista de espera")

    def cancelar_inscricao(self, request, context):
        aluno_id = self.kwargs.get("aluno_id")
        aluno = Aluno.objects.get(id=aluno_id)
        participacao_id = request.POST.get("participacao_id")
        participacao = aluno.participacao_set.get(id=participacao_id)
        participacao.delete()

        return redirect("inscricao", aluno_id=aluno_id)

    def _verificar_choque_de_horario(self, ofertas, ofertas_cursando):
        for oferta in ofertas:
            choque = oferta.verificar_choque_de_horario(
                ofertas
            ) or oferta.verificar_choque_de_horario(ofertas_cursando)
            if choque:
                return oferta, choque

        return False

    def _verificar_lista_espera(self, ofertas):
        lista_espera = []
        for oferta in ofertas:
            # Verifica se a oferta já atingiu o limite de inscrições
            if oferta.vagas_ocupadas() >= oferta.vagas:
                lista_espera.append(oferta)
        return lista_espera

    def get_creditos(self, aluno, ofertas):
        return sum([oferta.creditos() for oferta in ofertas]) + aluno.get_creditos()


def login_view(request):
    context = {}
    context["alunos"] = Aluno.objects.all()
    if request.method == "POST":
        return redirect("inscricao", aluno_id=request.POST.get("aluno"))

    return render(request, "login.html", context)
