"""Os passos têm de reproduzir exatamente o resultado do núcleo."""

import pytest
import sympy as sp

from matrizes import nucleo
from matrizes.web.services import step_service as ss

M = sp.Matrix
A2 = M([[2, 1], [5, 3]])
B2 = M([[1, 2], [3, 4]])
A3 = M([[2, 1, -1], [-3, -1, 2], [-2, 1, 2]])
A4 = M([[2, 0, 1, 3], [1, 1, 0, 2], [0, 4, 1, 1], [3, 1, 2, 0]])
SING = M([[1, 2], [2, 4]])
RET = M([[1, 2, 3], [4, 5, 6]])
FRAC = M([[sp.Rational(1, 2), 1], [3, sp.Rational(-2, 3)]])
SIMB = M([[sp.Symbol("a"), 1], [2, 3]])

CASOS = [
    ("Soma (A + B)", [A2, B2], None),
    ("Subtração (A - B)", [A3, A3.T], None),
    ("Multiplicação (A × B)", [A2, B2], None),
    ("Multiplicação (A × B)", [RET, RET.T], None),
    ("Multiplicação (A × B)", [A4, A4], None),  # > limite: só exemplos
    ("Multiplicar por escalar", [FRAC], sp.Rational(-3, 2)),
    ("Potência (Aⁿ)", [A2], 3),
    ("Potência (Aⁿ)", [A2], -2),
    ("Potência (Aⁿ)", [A2], 0),
    ("Transposta", [RET], None),
    ("Inversa", [A2], None),
    ("Inversa", [A3], None),
    ("Inversa", [FRAC], None),
    ("Determinante", [M([[7]])], None),
    ("Determinante", [A2], None),
    ("Determinante", [A3], None),
    ("Determinante", [A4], None),
    ("Determinante", [SING], None),
    ("Determinante", [SIMB], None),
    ("Posto (rank)", [RET], None),
    ("Posto (rank)", [SING], None),
    ("Traço", [A3], None),
    ("Escalonar (RREF)", [A3], None),
    ("Escalonar (RREF)", [RET], None),
    ("Escalonar (RREF)", [M([[0, 1], [1, 0]])], None),
    ("Adjunta (adj A)", [A3], None),
    ("Matriz de cofatores", [A2], None),
    ("Autovalores e autovetores", [M([[2, 0], [0, 3]])], None),
    ("Autovalores e autovetores", [M([[4, 1], [2, 3]])], None),
    ("Autovalores e autovetores", [M([[0, -1], [1, 0]])], None),  # complexos
    ("Autovalores e autovetores", [M([[1, 1], [1, 0]])], None),  # irracionais
    ("Autovalores e autovetores", [M([[2, 0, 0], [0, 3, 4], [0, 4, 9]])], None),
]


@pytest.mark.parametrize(("nome", "mats", "param"), CASOS)
def test_passos_reproduzem_o_nucleo(nome, mats, param):
    sol = ss.passos_para(nome, mats, param)  # valida internamente
    assert sol.passos and sol.resultado_latex and sol.formula and sol.interpretacao
    assert sol.entradas and sol.identificacao


def test_inversa_pelo_metodo_da_adjunta():
    sol = ss.passos_para("Inversa", [A3], metodo="adjunta")
    assert sol.valor == A3.inv()
    assert "adj" in sol.formula


def test_todas_as_operacoes_suportadas_existem_no_nucleo():
    nomes = {o.nome for o in nucleo.OPERACOES}
    assert set(ss.GERADORES) <= nomes


def test_operacao_sem_passos_retorna_none():
    assert ss.passos_para("Decomposição QR", [A2]) is None
    assert not ss.suporta("Decomposição QR")


@pytest.mark.parametrize(
    ("nome", "mats"),
    [
        ("Soma (A + B)", [A2, RET]),
        ("Multiplicação (A × B)", [A2, RET.T]),
        ("Determinante", [RET]),
        ("Inversa", [SING]),
        ("Traço", [RET]),
    ],
)
def test_erros_de_uso_sao_valueerror_em_portugues(nome, mats):
    with pytest.raises(ValueError, match=r"\w"):
        ss.passos_para(nome, mats)


def test_simbolico_no_escalonamento_e_indisponivel():
    with pytest.raises(ss.PassosIndisponiveis):
        ss.passos_para("Escalonar (RREF)", [SIMB])
    with pytest.raises(ss.PassosIndisponiveis):
        ss.passos_para("Determinante", [sp.Matrix(4, 4, sp.symbols("a0:16"))])


def test_gauss_registra_operacoes_elementares():
    sol = ss.passos_para("Escalonar (RREF)", [A3])
    titulos = " ".join(p.titulo for p in sol.passos)
    assert "←" in titulos
    assert sol.extras["pivos"] == [0, 1, 2]
    # cada passo de matriz é LaTeX válido (delimitadores balanceados)
    for p in sol.passos:
        if p.latex:
            assert p.latex.count("{") == p.latex.count("}")
            assert p.latex.count(r"\begin") == p.latex.count(r"\end")


def test_troca_de_linhas_quando_pivo_zero():
    sol = ss.passos_para("Escalonar (RREF)", [M([[0, 1], [1, 0]])])
    assert any("↔" in p.titulo for p in sol.passos)


def test_destaque_so_na_linha_alterada():
    tex = ss.latex_matriz(M([[1, 2], [3, 4]]), linhas=(1,))
    assert tex.count(r"\color") == 2


# ---------------------------- sistemas ----------------------------
SPD = (M([[2, 1, -1], [-3, -1, 2], [-2, 1, 2]]), M([8, -11, -3]))
SPI = (M([[1, 1], [2, 2]]), M([2, 4]))
SI = (M([[1, 1], [1, 1]]), M([2, 3]))
SPI3 = (M([[1, 2, 3], [2, 4, 6], [1, 0, 1]]), M([6, 12, 2]))
RETANG = (M([[1, 1, 1], [1, -1, 2]]), M([6, 5]))


@pytest.mark.parametrize("par", [SPD, SPI, SI, SPI3, RETANG])
def test_sistema_gauss_resolve_qualquer_tipo(par):
    A, b = par
    sol = ss.passos_sistema(A, b, "gauss")
    assert sol.extras["tipo"] == nucleo.classificar(A, b)[0]


def test_sistema_spd_valores():
    sol = ss.passos_sistema(*SPD, "gauss")
    assert sol.valor == ("SPD", [2, 3, -1])


def test_sistema_spi_tem_variavel_livre():
    sol = ss.passos_sistema(*SPI, "gauss")
    tipo, x = sol.valor
    assert tipo == "SPI"
    assert sp.Symbol("x2") in x[0].free_symbols


def test_sistema_si_aponta_linha_contraditoria():
    sol = ss.passos_sistema(*SI, "gauss")
    assert any("contradit" in p.titulo.lower() for p in sol.passos)


@pytest.mark.parametrize("metodo", ["cramer", "inversa"])
def test_sistema_cramer_e_inversa(metodo):
    sol = ss.passos_sistema(*SPD, metodo)
    assert sol.valor == ("SPD", [2, 3, -1])


@pytest.mark.parametrize("metodo", ["cramer", "inversa"])
@pytest.mark.parametrize("par", [SPI, SI, RETANG])
def test_cramer_e_inversa_recusam_casos_nao_aplicaveis(metodo, par):
    with pytest.raises(ValueError, match="det|equações"):
        ss.passos_sistema(*par, metodo)


def test_validar_detecta_resultado_errado():
    sol = ss.passos_para("Transposta", [RET])
    sol.valor = sol.valor + sp.ones(3, 2)
    with pytest.raises(ss.InconsistenciaMatematica):
        ss.validar(sol, "Transposta", [RET])


def test_autovalores_cubicos_irracionais_nao_travam_e_sao_indisponiveis():
    with pytest.raises(ss.PassosIndisponiveis):
        ss.passos_para("Autovalores e autovetores", [M([[4, 1, 2], [1, 3, 0], [2, 0, 5]])])
