"""Colar matrizes de texto, exportar CSV, novas predefinidas e componentes visuais."""

import pytest
import sympy as sp

pytest.importorskip("streamlit")

from matrizes.paleta import TEMAS  # noqa: E402
from matrizes.web import theme  # noqa: E402
from matrizes.web.components import icones  # noqa: E402
from matrizes.web.config import PREFERENCIAS_PADRAO  # noqa: E402
from matrizes.web.services import matrix_service as ms  # noqa: E402


@pytest.mark.parametrize(
    "texto",
    [
        "[[1, 2], [3, 4]]",
        "[[1,2],[3,4]]",
        "1 2; 3 4",
        "1 2\n3 4",
        "1,2\n3,4",
        "1\t2\n3\t4",
        "| 1 2 |\n| 3 4 |",
    ],
)
def test_grade_de_texto_formatos(texto):
    assert ms.grade_de_texto(texto) == [["1", "2"], ["3", "4"]]


def test_grade_de_texto_aceita_fracoes_e_expressoes():
    g = ms.grade_de_texto("1/2 sqrt(2); 2*pi -3")
    assert ms.matriz_de_texto(g) == sp.Matrix([[sp.Rational(1, 2), sp.sqrt(2)], [2 * sp.pi, -3]])


@pytest.mark.parametrize(
    "texto, trecho",
    [
        ("", "Cole"),
        ("[[1, 2], [3]]", "quantidades diferentes"),
        ("1 2; 3", "quantidades diferentes"),
        ("[[1, 2]", "Colchetes"),
        ("x" * 3000, "longo demais"),
        ("1 2 3 4 5 6 7 8 9", "máximo"),
    ],
)
def test_grade_de_texto_erros(texto, trecho):
    with pytest.raises(ValueError, match=trecho):
        ms.grade_de_texto(texto)


def test_grade_de_texto_nao_executa_codigo():
    g = ms.grade_de_texto("__import__('os') 1")
    with pytest.raises(ms.EntradaInvalida):
        ms.matriz_de_texto(g)


def test_csv_ida_e_volta():
    M = sp.Matrix([[sp.Rational(1, 3), 2], [-1, sp.sqrt(2)]])
    csv = ms.matriz_para_csv(M)
    assert csv == "1/3,2\n-1,sqrt(2)\n"
    assert ms.matriz_de_texto(ms.grade_de_texto(csv)) == M


def test_novas_predefinidas():
    assert ms.predefinida("Pascal", 4)[3, 3] == 20 and ms.predefinida("Pascal", 3).is_symmetric()
    V = ms.predefinida("Vandermonde (1, 2, 3, …)", 3)
    assert V == sp.Matrix([[1, 1, 1], [2, 4, 8], [3, 9, 27]]) or V.det() != 0
    A = ms.predefinida("Anti-identidade (permutação)", 3)
    assert A == sp.Matrix([[0, 0, 1], [0, 1, 0], [1, 0, 0]])


# ---------- ícones ----------
def test_todos_os_icones_geram_svg_valido():
    import xml.dom.minidom as xd

    for nome in icones.nomes():
        doc = xd.parseString(icones.svg(nome, 20))
        assert doc.documentElement.tagName == "svg"
    xd.parseString(icones.ARTE_HERO)


def test_icone_desconhecido_e_classe_escapada():
    with pytest.raises(KeyError):
        icones.svg("nao-existe")
    assert 'class="a&quot;b"' in icones.svg("seta", classe='a"b')


# ---------- tema ----------
@pytest.mark.parametrize("nome", ["claro", "escuro"])
def test_css_animacoes_podem_ser_desligadas(nome):
    p = TEMAS[nome]
    com, sem = theme.gerar_css(p, True, True), theme.gerar_css(p, True, False)
    assert "@keyframes mx-subir" in com and "@keyframes" not in sem
    assert ".mx-card-hover:hover" in sem  # efeitos de hover continuam
    assert "prefers-reduced-motion" in com and "prefers-reduced-motion" in sem
    assert "{{" not in com and "}}" not in com


def test_preferencia_animacoes_padrao_ligada():
    assert PREFERENCIAS_PADRAO["animacoes"] is True


# ---------- interface ----------

from streamlit.testing.v1 import AppTest  # noqa: E402

from matrizes.web.services import calc_service as cs  # noqa: E402

NOVAS = [
    "Produto de Hadamard (A ∘ B)",
    "Produto de Kronecker (A ⊗ B)",
    "Pseudo-inversa (A⁺)",
    "Espaços fundamentais",
    "Normas e número de condição",
]


@pytest.mark.parametrize("nome", NOVAS)
def test_novas_operacoes_executam_pela_camada_web(nome):
    A = sp.Matrix([[2, 1], [1, 3]])
    ex = cs.executar(nome, [A, A])
    assert ex.resultado and ex.latex_principal or ex.resultado


def _app_painel():
    from matrizes.web import theme
    from matrizes.web.pages import operacoes
    from matrizes.web.state import obter

    obter()
    theme.aplicar()
    operacoes.renderizar()


def test_colar_matriz_na_interface_e_exportar():
    at = AppTest.from_function(_app_painel, default_timeout=90).run()
    assert not at.exception
    at.text_area(key="op:A:colar").set_value("[[1, 2], [3, 4]]").run()
    at.button(key="op:A:colbtn").click().run()
    assert not at.exception
    assert at.session_state["app"].rascunho("op:A") == [["1", "2"], ["3", "4"]]
    at.text_area(key="op:B:colar").set_value("1 0; 0 1").run()
    at.button(key="op:B:colbtn").click().run()
    at.button(key="op:calc").click().run()
    assert not at.exception
    assert [e.label for e in at.expander if "exportar" in e.label.lower()]


def test_colar_texto_invalido_nao_altera_o_editor():
    at = AppTest.from_function(_app_painel, default_timeout=90).run()
    antes = at.session_state["app"].rascunho("op:A")
    at.text_area(key="op:A:colar").set_value("[[1, 2], [3]]").run()
    at.button(key="op:A:colbtn").click().run()
    assert not at.exception
    assert at.session_state["app"].rascunho("op:A") == antes


def test_transpor_no_editor():
    at = AppTest.from_function(_app_painel, default_timeout=90).run()
    at.text_area(key="op:A:colar").set_value("1 2 3; 4 5 6").run()
    at.button(key="op:A:colbtn").click().run()
    at.button(key="op:A:trp").click().run()
    assert at.session_state["app"].rascunho("op:A") == [["1", "4"], ["2", "5"], ["3", "6"]]
