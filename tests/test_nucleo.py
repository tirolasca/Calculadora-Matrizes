"""Testes do núcleo de cálculo (sem interface)."""

import pytest
import sympy as sp

from matrizes import nucleo as n


def M(*linhas):
    return sp.Matrix(linhas)


# ---------- entrada ----------
@pytest.mark.parametrize(
    "txt, esperado",
    [
        ("3", 3),
        ("-2.5", sp.Rational(-5, 2)),
        ("1/2", sp.Rational(1, 2)),
        ("0,25", sp.Rational(1, 4)),
    ],
)
def test_numero_exato(txt, esperado):
    assert n.numero(txt) == esperado


@pytest.mark.parametrize("txt", ["abc", "", "1/0x", "__import__('os')"])
def test_numero_invalido_nao_executa_codigo(txt):
    with pytest.raises((ValueError, TypeError, ZeroDivisionError)):
        n.numero(txt)


def test_parse_matriz_dois_formatos():
    esperado = M([1, 2], [3, 4])
    assert n.parse_matriz_colchetes("[[1,2],[3,4]]") == esperado
    assert n.parse_matriz_colchetes("1 2; 3 4") == esperado
    assert n.parse_matriz_colchetes("[[1/2]]") == M([sp.Rational(1, 2)])


@pytest.mark.parametrize("txt", ["", "[[1,2],[3]]", "[[a]]", "__import__('os')", "1 2; 3"])
def test_parse_matriz_invalida(txt):
    with pytest.raises(ValueError):
        n.parse_matriz_colchetes(txt)


# ---------- operações ----------
def test_soma_subtracao_multiplicacao():
    A, B = M([1, 2], [3, 4]), M([0, 1], [1, 0])
    assert n.f_soma(A, B)[0][1] == M([1, 3], [4, 4])
    assert n.f_subtracao(A, B)[0][1] == M([1, 1], [2, 4])
    assert n.f_multiplicacao(A, B)[0][1] == M([2, 1], [4, 3])


def test_dimensoes_incompativeis():
    A, B = M([1, 2, 3]), M([1, 2])
    for fn in (n.f_soma, n.f_subtracao, n.f_multiplicacao):
        with pytest.raises(ValueError):
            fn(A, B)


def test_escalar_potencia_transposta():
    A = M([1, 2], [3, 4])
    assert n.f_escalar(A, sp.Rational(1, 2))[0][1] == A / 2
    assert n.f_potencia(A, 2)[0][1] == A * A
    assert n.f_potencia(A, -1)[0][1] == A.inv()
    assert n.f_transposta(A)[0][1] == M([1, 3], [2, 4])


def test_inversa_e_singular():
    A = M([2, 1], [1, 1])
    assert n.f_inversa(A)[0][1] * A == sp.eye(2)
    with pytest.raises(ValueError, match="não possui inversa"):
        n.f_inversa(M([1, 2], [2, 4]))
    with pytest.raises(ValueError, match="quadrada"):
        n.f_inversa(M([1, 2, 3]))
    with pytest.raises(ValueError, match="singular"):
        n.f_potencia(M([1, 2], [2, 4]), -1)


def test_propriedades():
    A = M([2, 1, 1], [1, 3, 2], [1, 0, 0])
    assert n.f_determinante(A)[0][1] == "-1"
    assert n.f_posto(A)[0][1] == "3"
    assert n.f_traco(A)[0][1] == "5"
    rref, pivos = n.f_escalonar(A)
    assert rref[1] == sp.eye(3)
    assert pivos[1] == "[1, 2, 3]"


def test_autovalores_exatos_e_aproximados():
    res = dict((r, v) for r, v in n.f_autovalores(M([2, 1], [1, 2])) if r.startswith("λ"))
    assert set(res) == {"λ = 1", "λ = 3"}
    # 3x3 com raízes irracionais: devem sair aproximadas, não expressões gigantes
    texto = " ".join(str(r) for r, _ in n.f_autovalores(M([2, 1, 1], [1, 3, 2], [1, 0, 0])))
    assert "≈" in texto and "sqrt" not in texto


def test_lu_reconstroi_a_matriz():
    A = M([2, 1, 1], [1, 3, 2], [1, 0, 0])
    res = dict(n.f_lu(A))
    assert res["L"] * res["U"] == A


# ---------- classificação (Rouché-Capelli) ----------
SISTEMAS = [
    # (A, b, tipo)
    (M([2, 1, -1], [-3, -1, 2], [-2, 1, 2]), M([8], [-11], [-3]), "SPD"),
    (M([1, 1], [1, -1]), M([2], [0]), "SPD"),
    (M([1, 1], [2, 2]), M([2], [4]), "SPI"),
    (M([1, 1, 1], [1, 2, 3]), M([3], [6]), "SPI"),
    (M([1, 1], [1, 1]), M([2], [3]), "SI"),
    (M([1, 1], [2, -1], [0, 1]), M([2], [-1], [3]), "SI"),
    (M([1, 1], [2, 2], [3, 3]), M([1], [2], [3]), "SPI"),
]


@pytest.mark.parametrize("A, b, tipo", SISTEMAS)
def test_classificacao(A, b, tipo):
    assert n.classificar(A, b)[0] == tipo


def test_spd_solucao_em_todos_os_metodos():
    A, b = SISTEMAS[0][:2]
    _, linhas = n.relatorio_sistema(A, b, "todos")
    # escalonamento
    assert {"  x1 = 2", "  x2 = 3", "  x3 = -1"} <= set(linhas)
    # Cramer: det(A) = -1, det(A1) = -2 → x1 = 2
    assert "det(A) = -1" in linhas
    assert any(l.endswith("x1 = -2/-1 = 2") for l in linhas)
    # inversa: vetor x = (2, 3, -1)
    i = linhas.index("x = A⁻¹·b =")
    assert [l.strip() for l in linhas[i + 1].split("\n")] == ["[  2 ]", "[  3 ]", "[ -1 ]"]


def test_cramer_e_inversa_concordam_com_gauss():
    A, b = M([3, 2], [1, -1]), M([1], [2])
    _, x_cramer = n.resolver_cramer(A, b)
    _, x_inv = n.resolver_inversa(A, b)
    x_gauss = list(next(iter(sp.linsolve((A, b), *sp.symbols("x1:3")))))
    assert x_cramer == x_inv == x_gauss == [1, -1]


@pytest.mark.parametrize(
    "A, b", [(SISTEMAS[2][0], SISTEMAS[2][1]), (SISTEMAS[3][0], SISTEMAS[3][1])]
)
def test_cramer_inversa_nao_se_aplicam_fora_do_spd(A, b):
    for fn in (n.resolver_cramer, n.resolver_inversa):
        with pytest.raises(ValueError):
            fn(A, b)
    # mas o relatório não quebra: explica o motivo
    _, linhas = n.relatorio_sistema(A, b, "todos")
    assert any("não se aplica" in l or "exige" in l for l in linhas)


def test_spi_solucao_parametrica():
    _, linhas = n.relatorio_sistema(M([1, 1, 1], [1, 2, 3]), M([3], [6]), "gauss")
    assert "  x1 = x3" in linhas
    assert "  x2 = 3 - 2*x3" in linhas


def test_equacao_texto():
    assert n._equacao_texto([2, -1, 0], 8) == "2x1 - x2 = 8"
    assert n._equacao_texto([-1, 1], 0) == "-x1 + x2 = 0"


def test_figura_sistema():
    pytest.importorskip("matplotlib")
    A, b = M([1, 1], [1, -1]), M([2], [0])
    fig = n.figura_sistema(A, b, "SPD")
    assert fig is not None and len(fig.axes[0].lines) >= 2
    assert n.figura_sistema(M([1, 1, 1]), M([1]), "SPI") is None  # só 2 incógnitas
