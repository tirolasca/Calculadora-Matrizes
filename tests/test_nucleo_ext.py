"""Operações acrescentadas ao núcleo para a interface web (estrutura, adjunta, decomposições)."""

import pytest
import sympy as sp

from matrizes import nucleo as n


def M(*linhas):
    return sp.Matrix(linhas)


def dic(resultado):
    return {r: v for r, v in resultado}


def test_catalogo_preserva_as_operacoes_originais():
    cods = [o.cod for o in n.OPERACOES]
    assert cods[:13] == [str(i) for i in range(4, 17)]
    assert len(cods) == len(set(cods))
    nomes = [o.nome for o in n.OPERACOES]
    assert len(nomes) == len(set(nomes))
    assert n.OPERACOES[0].nome == "Soma (A + B)" and n.OPERACOES[12].nome == "Decomposição LU"


def test_adjunta_e_relacao_com_inversa():
    A = M([2, 1], [1, 1])
    adj = dic(n.f_adjunta(A))["adj(A)"]
    assert adj == M([1, -1], [-1, 2])
    assert A * adj == A.det() * sp.eye(2)
    B = M([2, 1, 1], [1, 3, 2], [1, 0, 0])
    assert B.inv() == n.f_adjunta(B)[0][1] / B.det()
    with pytest.raises(ValueError, match="quadrada"):
        n.f_adjunta(M([1, 2, 3]))


def test_cofatores_e_adjunta_sao_transpostas():
    B = M([2, 1, 1], [1, 3, 2], [1, 0, 0])
    assert n.f_cofatores(B)[0][1].T == n.f_adjunta(B)[0][1]


@pytest.mark.parametrize(
    "A, esperado",
    [
        (
            sp.eye(3),
            {
                "identidade": True,
                "diagonal": True,
                "simetrica": True,
                "ortogonal": True,
                "invertivel": True,
            },
        ),
        (sp.zeros(2, 2), {"nula": True, "invertivel": False, "diagonal": True}),
        (
            M([1, 2], [0, 3]),
            {"triangular_superior": True, "triangular_inferior": False, "diagonal": False},
        ),
        (M([0, 1], [-1, 0]), {"antissimetrica": True, "simetrica": False, "ortogonal": True}),
        (M([1, 2], [2, 1]), {"simetrica": True, "antissimetrica": False}),
        (M([1, 0], [0, 0]), {"idempotente": True, "invertivel": False}),
    ],
)
def test_estrutura(A, esperado):
    est = n.estrutura(A)
    for chave, valor in esperado.items():
        assert est[chave] is valor, chave


def test_estrutura_nao_quadrada_so_tem_o_basico():
    assert set(n.estrutura(M([1, 2, 3]))) == {"quadrada", "nula"}


def test_estrutura_simbolica_e_indeterminada():
    a, b = sp.symbols("a b")
    est = n.estrutura(M([a, 0], [0, b]))
    assert est["diagonal"] is True and est["invertivel"] is None
    assert n.estrutura(M([a, 1], [1, a]))["simetrica"] is True
    texto = dict(n.f_estrutura(M([a, 0], [0, b])))
    assert texto["Invertível:"] == "depende dos valores simbólicos"


def test_partes_triangulares_somam_a_matriz():
    A = M([1, 2, 3], [4, 5, 6], [7, 8, 9])
    r = dic(n.f_partes_triangulares(A))
    L, D, U = (r["L (estritamente inferior)"], r["D (diagonal)"], r["U (estritamente superior)"])
    assert L + D + U == A
    assert n.estrutura(L)["triangular_inferior"] and n.estrutura(U)["triangular_superior"]
    assert n.estrutura(D)["diagonal"]


def test_partes_simetrica_antissimetrica():
    A = M([1, 2], [5, 4])
    r = n.f_partes_simetrica(A)
    S, K = r[0][1], r[1][1]
    assert S + K == A and S == S.T and K == -K.T


def test_qr_cholesky_diagonalizacao():
    A = M([2, 1], [1, 2])
    q, r = n.f_qr(A)[0][1], n.f_qr(A)[1][1]
    assert q * r == A and sp.simplify(q.T * q - sp.eye(2)).is_zero_matrix
    L = n.f_cholesky(A)[0][1]
    assert L * L.T == A and L.is_lower
    P, D = n.f_diagonalizacao(A)[0][1], n.f_diagonalizacao(A)[1][1]
    assert P * D * P.inv() == A


def test_erros_de_decomposicao_viram_valueerror():
    with pytest.raises(ValueError, match="simétrica"):
        n.f_cholesky(M([1, 2], [0, 1]))
    with pytest.raises(ValueError, match="positiva"):
        n.f_cholesky(M([1, 2], [2, 1]))
    with pytest.raises(ValueError, match="diagonalizável"):
        n.f_diagonalizacao(M([1, 1], [0, 1]))
    with pytest.raises(ValueError, match="linearmente"):
        n.f_qr(M([1, 2], [2, 4]))
    with pytest.raises(ValueError, match="linhas"):
        n.f_qr(M([1, 2, 3]))


def test_diagonalizacao_irracional_e_numerica_e_rapida():
    A = M([2, 1, 1], [1, 3, 2], [1, 0, 0])  # raízes de um cúbico irredutível
    res = n.f_diagonalizacao(A)
    assert any("numérico" in str(v) for _, v in res) and any("✓" in str(v) for _, v in res)


def test_operacoes_com_simbolos():
    a, b = sp.symbols("a b")
    S = M([a, 0], [0, b])
    assert n.f_inversa(S)[0][1] == M([1 / a, 0], [0, 1 / b])
    assert n.f_determinante(S)[0][1] == "a*b"
    vals = [r for r, _ in n.f_autovalores(S) if r.startswith("λ")]
    assert set(vals) == {"λ = a", "λ = b"}
    assert n.tem_simbolos(S) and not n.tem_simbolos(sp.eye(2))


def test_geradores():
    assert n.matriz_identidade(3) == sp.eye(3)
    assert n.matriz_nula(2, 3).shape == (2, 3) and n.matriz_nula(2) == sp.zeros(2)
    assert n.matriz_diagonal([1, 2]) == M([1, 0], [0, 2])
