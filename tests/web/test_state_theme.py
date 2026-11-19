"""Estado da sessão (EstadoApp) e geração do CSS do tema."""

import json

import pytest
import sympy as sp

pytest.importorskip("streamlit")

from matrizes.paleta import TEMAS  # noqa: E402
from matrizes.web import state, theme  # noqa: E402

a = sp.Symbol("a")


def test_estado_inicial():
    e = state.EstadoApp()
    assert len(e.memoria) == 0 and len(e.historico) == 0 and e.pref("tema") == "sistema"
    # cada instância tem preferências próprias (sem estado compartilhado)
    e.preferencias["tema"] = "escuro"
    assert state.EstadoApp().pref("tema") == "sistema"


def test_matrizes_recentes():
    e = state.EstadoApp()
    for n in "ABCDEFGHIJ":
        e.memoria.salvar(n, sp.eye(2))
    e.registrar_uso("A", "B")
    e.registrar_uso("A")
    assert e.recentes[:2] == ["A", "B"]
    e.registrar_uso(*"CDEFGHIJ")
    assert len(e.recentes) == state.MAX_RECENTES
    e.registrar_uso("inexistente")  # ignora nomes que não existem
    assert "inexistente" not in e.recentes
    e.memoria.excluir(e.recentes[0])
    e.limpar_recentes_inexistentes()
    assert all(n in e.memoria for n in e.recentes)


def test_rascunhos_sobrevivem_e_nao_sao_alias():
    e = state.EstadoApp()
    grade = [["1", "2"], ["3", "4"]]
    e.definir_rascunho("ed", grade)
    grade[0][0] = "99"
    assert e.rascunho("ed") == [["1", "2"], ["3", "4"]]
    e.descartar_rascunho("ed")
    assert e.rascunho("ed") is None


def test_experimentos():
    e = state.EstadoApp()
    A = sp.Matrix([[1, 2], [3, 4]])
    e.salvar_experimento("det zero", {"A": A}, nota="mudei o 4")
    A[1, 1] = 0  # não deve afetar o experimento salvo
    assert e.restaurar_experimento("det zero")["A"] == sp.Matrix([[1, 2], [3, 4]])
    with pytest.raises(ValueError):
        e.salvar_experimento("  ", {"A": A})
    with pytest.raises(KeyError):
        e.restaurar_experimento("nada")
    e.excluir_experimento("det zero")
    assert not e.experimentos


def test_progresso():
    e = state.EstadoApp()
    assert e.resumo_progresso() == (0, 0)
    e.registrar_tentativa("ex1", False)
    e.registrar_tentativa("ex1", True)
    e.registrar_tentativa("ex2", False)
    assert e.progresso["ex1"] == {"tentativas": 2, "acertos": 1, "resolvido": True}
    assert e.resumo_progresso() == (1, 2)


def test_exportar_importar_sessao():
    e = state.EstadoApp()
    e.memoria.salvar("A", sp.Matrix([[sp.Rational(1, 3), a], [sp.sqrt(2), 4]]))
    e.salvar_experimento("x", {"M": sp.eye(2)}, nota="n")
    e.registrar_tentativa("ex1", True)
    e.preferencias["tema"] = "escuro"
    texto = e.exportar()
    assert json.loads(texto)["versao"] == 1

    novo = state.EstadoApp()
    cont = novo.importar(texto)
    assert cont == {"matrizes": 1, "experimentos": 1}
    assert novo.memoria.matrizes == e.memoria.matrizes
    assert novo.restaurar_experimento("x")["M"] == sp.eye(2)
    assert novo.progresso == e.progresso and novo.pref("tema") == "escuro"


@pytest.mark.parametrize(
    "texto",
    [
        "",
        "nao-json",
        "[]",
        "{}",
        '{"matrizes": {"A": [["__import__(1)"]]}}',
        '{"matrizes": {}, "experimentos": {"x": {}}}',
    ],
)
def test_importacao_invalida_nao_altera_o_estado(texto):
    e = state.EstadoApp()
    e.memoria.salvar("A", sp.eye(2))
    with pytest.raises(ValueError):
        e.importar(texto)
    assert e.memoria.nomes() == ["A"]


def test_importacao_ignora_preferencias_de_tipo_errado():
    e = state.EstadoApp()
    dados = {
        "matrizes": {},
        "preferencias": {"tema": 3, "casas": "muitas", "desconhecida": 1, "aproximacao": False},
    }
    e.importar(json.dumps(dados))
    assert e.pref("tema") == "sistema" and e.pref("casas") == 4 and e.pref("aproximacao") is False
    assert "desconhecida" not in e.preferencias


def test_obter_cria_o_estado_uma_vez_por_sessao():
    from streamlit.testing.v1 import AppTest

    def app():
        from matrizes.web import state as s

        e = s.obter()
        e.memoria.salvar("A", __import__("sympy").eye(2))
        import streamlit as st

        st.write(f"{s.obter() is e}|{len(s.obter().memoria)}")

    at = AppTest.from_function(app).run()
    assert at.markdown[0].value == "True|1"
    at.run()  # novo rerun: o estado persiste
    assert at.markdown[0].value == "True|1"


# ---------- tema ----------
def test_nome_efetivo():
    assert theme.nome_efetivo("sistema", "escuro") == "escuro"
    assert theme.nome_efetivo("claro", "escuro") == "claro"
    assert theme.nome_efetivo("escuro", "claro") == "escuro"


@pytest.mark.parametrize("nome", ["claro", "escuro"])
def test_css_forcado_inclui_cores_nativas_e_o_nao_forcado_nao(nome):
    p = TEMAS[nome]
    forcado, livre = theme.gerar_css(p, True), theme.gerar_css(p, False)
    for css in (forcado, livre):
        assert p["accent"] in css and ".mx-card" in css and "@media" in css  # responsivo
    assert ".stApp" in forcado and p["bg"] in forcado
    assert '[data-testid="stSidebar"]' in forcado and '[data-testid="stSidebar"]' not in livre
    assert "{{" not in forcado and "}}" not in forcado  # sem chaves de f-string vazadas


def test_estilo_grafico_tem_as_chaves_esperadas():
    for nome in ("claro", "escuro"):
        assert set(theme.estilo_grafico(TEMAS[nome])) == {"fundo", "texto", "grade", "eixos"}
