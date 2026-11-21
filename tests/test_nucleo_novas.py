"""Operações acrescentadas na versão 1.1: Hadamard, Kronecker, pseudo-inversa, espaços, normas."""

import pytest
import sympy as sp

from matrizes import nucleo as n


def M(*linhas):
    return sp.Matrix(linhas)


def dic(resultado):
    return dict(resultado)


def test_catalogo_continua_com_codigos_e_nomes_unicos():
    cods = [o.cod for o in n.OPERACOES]
    assert len(cods) == len(set(cods)) and cods[-5:] == ["26", "27", "28", "29", "30"]
    nomes = [o.nome for o in n.OPERACOES]
    assert len(nomes) == len(set(nomes))


def test_hadamard():
    r = dic(n.f_hadamard(M([1, 2], [3, 4]), M([5, 6], [7, 8])))
    assert r["A ∘ B"] == M([5, 12], [21, 32])
    with pytest.raises(ValueError, match="mesmas dimensões"):
        n.f_hadamard(M([1, 2]), M([1], [2]))


def test_kronecker():
    A, B = M([1, 2], [3, 4]), sp.eye(2)
    r = dic(n.f_kronecker(A, B))
    assert r["A ⊗ B"] == sp.kronecker_product(A, B) and r["Dimensão:"] == "4×4"
    with pytest.raises(ValueError, match="12×12"):
        n.f_kronecker(sp.ones(4, 4), sp.ones(4, 4))


@pytest.mark.parametrize(
    "A", [M([1, 2], [3, 4], [5, 6]), M([1, 2, 3], [2, 4, 6], [1, 1, 1]), sp.zeros(2, 3)]
)
def test_pseudoinversa_satisfaz_moore_penrose(A):
    r = dic(n.f_pseudoinversa(A))
    P = r["A⁺ (Moore-Penrose)"]
    assert A * P * A == A and P * A * P == P
    assert (A * P).T == A * P and (P * A).T == P * A
    assert "✓" in r["Verificação:"]


def test_pseudoinversa_de_invertivel_e_a_inversa():
    A = M([2, 1], [1, 1])
    assert dic(n.f_pseudoinversa(A))["A⁺ (Moore-Penrose)"] == A.inv()


def test_espacos_fundamentais_e_teorema_do_posto():
    A = M([1, 2, 3], [2, 4, 6], [1, 1, 1])
    r = dict(n.f_espacos(A))
    assert r["posto(A) ="] == "2" and r["nulidade(A) ="] == "1"
    nuc = r["Base de N(A) — núcleo (vetores nas colunas)"]
    assert A * nuc == sp.zeros(3, 1)
    assert "✓" in r["Verificação:"]


def test_espacos_com_nucleo_trivial_e_matriz_nula():
    r = n.f_espacos(sp.eye(2))
    assert any(k == "Obs." or k.startswith("Obs") for k, _ in r)
    z = dict(n.f_espacos(sp.zeros(2, 2)))
    assert z["posto(A) ="] == "0" and z["nulidade(A) ="] == "2"


def test_normas_e_numero_de_condicao():
    A = M([2, 1, -1], [-3, -1, 2], [-2, 1, 2])
    r = dic(n.f_normas(A))
    assert r["norma de Frobenius ="] == "sqrt(29)"
    assert r["norma-1 (maior soma de colunas) ="] == "7"
    assert r["norma-infinito (maior soma de linhas) ="] == "6"
    assert r["cond-1(A) ="] == "77"
    assert float(r["norma-2 (espectral) ≈"]) == pytest.approx(5.10344, rel=1e-5)


def test_normas_de_singular_e_nao_quadrada():
    r = dic(n.f_normas(M([1, 2, 3], [2, 4, 6], [1, 1, 1])))
    assert "∞" in r["Número de condição:"]
    assert not any(k.startswith("cond") for k in dic(n.f_normas(M([1, 2], [3, 4], [5, 6]))))


@pytest.mark.parametrize("f", [n.f_pseudoinversa, n.f_espacos, n.f_normas])
def test_funcoes_numericas_recusam_simbolos(f):
    with pytest.raises(ValueError, match="números"):
        f(sp.Matrix([[sp.Symbol("a")]]))
