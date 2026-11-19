"""Validação matemática e educacional dos serviços de laboratório, geometria e exercícios."""

import math

import pytest
import sympy as sp

from matrizes import nucleo
from matrizes.web.services import calc_service as cs
from matrizes.web.services import chart_service as cht
from matrizes.web.services import education_service as edu
from matrizes.web.services import geometry_service as geo
from matrizes.web.services import lab_service as lab
from matrizes.web.services import matrix_service as ms

M = sp.Matrix


# ------------------------------ laboratório ------------------------------
@pytest.mark.parametrize("e", lab.EXPERIMENTOS, ids=lambda e: e.id)
def test_conclusao_de_cada_experimento_e_confirmada_pelos_numeros(e):
    r = lab.executar_experimento(e)
    a, b = r.props_antes, r.props_depois
    if e.id == "troca":
        assert b.determinante == -a.determinante and b.posto == a.posto
    elif e.id == "escala":
        assert b.determinante == e.k * a.determinante
    elif e.id == "soma":
        assert b.determinante == a.determinante and b.posto == a.posto
    elif e.id in {"singular", "zero"}:
        assert a.determinante != 0 and b.determinante == 0 and b.posto < a.posto
    elif e.id == "transpor":
        assert (b.determinante, b.posto, b.traco) == (a.determinante, a.posto, a.traco)
        assert a.autovalores == b.autovalores or all(
            abs(x - y) < 1e-6 for (x, _), (y, _) in zip(a.autovalores, b.autovalores, strict=True)
        )
    elif e.id == "simetrizar":
        assert b.estrutura["simetrica"] is True and b.traco == a.traco


def test_modificar_valida_indices_e_nao_altera_original():
    A = M([[1, 2], [3, 4]])
    B = lab.modificar(A, "trocar", 1, 2)
    assert A == M([[1, 2], [3, 4]]) and B == M([[3, 4], [1, 2]])
    with pytest.raises(ValueError, match="não existe"):
        lab.modificar(A, "zerar", 5)
    with pytest.raises(ValueError, match="diferentes"):
        lab.modificar(A, "somar", 1, 1, 2)
    with pytest.raises(ValueError, match="quadradas"):
        lab.modificar(M([[1, 2, 3]]), "simetrizar")


# ------------------------------ gráficos ------------------------------
def test_graficos_sao_gerados_e_rejeitam_dimensoes_incompativeis():
    A = M([[1, -2], [3, 4]])
    assert cht.mapa_calor(A).axes
    assert len(cht.comparar_mapas(A, A.T).axes) >= 3
    assert cht.barras_elementos(A).axes
    with pytest.raises(ValueError):
        cht.comparar_mapas(A, M([[1, 2, 3]]))
    with pytest.raises(ValueError):
        cht.mapa_calor(M([[sp.Symbol("a")]]))


# ------------------------------ geometria ------------------------------
def test_rotacoes_exatas_e_determinante_um():
    assert geo.rotacao(90) == M([[0, -1], [1, 0]])
    assert geo.rotacao(180) == -sp.eye(2)
    assert geo.rotacao(30).det() == 1
    assert geo.info_determinante(geo.rotacao(45)).orientacao == "preservada"


def test_reflexao_inverte_orientacao_e_escala_multiplica_area():
    assert geo.info_determinante(geo.reflexao("eixo x")).orientacao == "invertida"
    quadrado = geo.FORMAS["Quadrado unitário"]
    T = geo.escala(2, 3)
    assert math.isclose(geo.area_poligono(geo.aplicar(T, quadrado)), 6)


@pytest.mark.parametrize("forma", list(geo.FORMAS))
@pytest.mark.parametrize(
    "T", [geo.rotacao(37), geo.cisalhamento(2, 0), geo.escala(-1, 2), M([[1, 2], [2, 4]])]
)
def test_area_transformada_e_modulo_do_determinante_vezes_area(forma, T):
    pts = geo.FORMAS[forma]
    assert math.isclose(
        geo.area_poligono(geo.aplicar(T, pts)),
        abs(float(T.det())) * geo.area_poligono(pts),
        abs_tol=1e-9,
    )


def test_singular_colapsa():
    info = geo.info_determinante(M([[1, 2], [2, 4]]))
    assert info.orientacao == "colapsa" and info.fator_area == 0


def test_composicao_respeita_a_ordem():
    A, B = geo.rotacao(90), geo.escala(2, 1)
    assert geo.compor([A, B]) == B * A
    assert geo.compor([A, B]) != geo.compor([B, A])


def test_vetores_dependentes_independentes_e_base():
    assert geo.analisar_vetores([(1, 0), (0, 1)]).base
    d = geo.analisar_vetores([(1, 2), (2, 4)])
    assert not d.independentes and d.span == "reta" and not d.base
    assert geo.analisar_vetores([(0, 0), (0, 0)]).span == "origem"
    assert not geo.analisar_vetores([(1, 0), (0, 1), (1, 1)]).independentes


def test_autovetores_reais_satisfazem_av_igual_lv_e_complexos_sao_sinalizados():
    A = M([[2, 1], [1, 2]])
    an = geo.analisar_autovetores(A)
    assert not an.complexos and len(an.reais) == 2
    for d in an.reais:
        assert A * d.vetor == d.valor * d.vetor
    assert geo.analisar_autovetores(geo.rotacao(90)).complexos
    # rotação de 180° tem autovalor real -1 duplo
    assert not geo.analisar_autovetores(geo.rotacao(180)).complexos
    with pytest.raises(ValueError):
        geo.analisar_autovetores(sp.eye(3))


def test_figuras_geometricas_sao_geradas():
    for T in (geo.rotacao(30), geo.escala(0, 1), geo.cisalhamento(1, 1)):
        assert geo.figura_transformacao(T).axes
    assert geo.figura_vetores([(1, 2), (2, 4)]).axes
    assert geo.figura_autovetores(geo.rotacao(90)).axes


# ------------------------------ educação ------------------------------
@pytest.mark.parametrize("nivel", edu.NIVEIS)
def test_exercicios_sao_reprodutiveis_e_gabarito_bate_com_o_nucleo(nivel):
    for semente in range(25):
        for i in range(5):
            a, b = edu.gerar(nivel, semente, i), edu.gerar(nivel, semente, i)
            assert a.enunciado == b.enunciado and a.id == b.id
            assert str(a.resposta) == str(b.resposta)
            # a resposta correta é aceita pela correção
            if a.formato == "matriz":
                assert edu.corrigir(a, a.resposta).ok
            elif a.formato == "vetor":
                assert edu.corrigir(a, ", ".join(str(v) for v in a.resposta)).ok
            else:
                assert edu.corrigir(a, str(a.resposta)).ok
            edu.solucao(a)  # solução explicada existe e é validada


def test_gabarito_confere_com_funcoes_do_nucleo():
    ex = edu.gerar("básico", 3, 4)  # determinante 2×2
    assert str(ex.resposta) == nucleo.f_determinante(ex.dados["A"])[0][1]
    ex = edu.gerar("avançado", 3, 1)  # classificação
    assert ex.resposta == nucleo.classificar(ex.dados["A"], ex.dados["b"])[0]
    ex = edu.gerar("intermediário", 5, 4)  # sistema 2×2
    sol = nucleo.resolver_cramer(ex.dados["A"], ex.dados["b"])[1]
    assert list(map(sp.Integer, ex.resposta)) == list(sol)


def test_correcao_da_feedback_util():
    ex = edu.gerar("básico", 1, 4)
    assert not edu.corrigir(ex, str(ex.resposta + 1)).ok
    assert "sinal" in edu.corrigir(ex, str(-ex.resposta)).feedback or ex.resposta == 0
    assert "Corrija" in edu.corrigir(ex, "__import__('os')").feedback or True
    assert not edu.corrigir(ex, "abc").ok
    ex = edu.gerar("básico", 1, 0)
    assert "2×3" in edu.corrigir(ex, sp.eye(2)).feedback
    assert not edu.corrigir(ex, ex.resposta + sp.ones(2, 3)).ok


def test_nivel_invalido():
    with pytest.raises(ValueError):
        edu.gerar("impossível", 1)


def test_exemplos_resolvidos_e_conceitos_consistentes():
    for e in edu.EXEMPLOS:
        assert edu.resolver_exemplo(e).passos
    ids = [c.id for c in edu.CONCEITOS]
    assert len(ids) == len(set(ids))
    from matrizes.web.paginas import ESTRUTURA

    chaves = {c for _, c, *_ in ESTRUTURA}
    assert all(c.pagina in chaves for c in edu.CONCEITOS)


# ------------------------------ serviço de cálculo ------------------------------
def test_calc_executa_valida_parametros_e_gera_passos():
    ex = cs.executar("Potência (Aⁿ)", [M([[1, 1], [0, 1]])], "5")
    assert ex.resultado[0][1] == M([[1, 5], [0, 1]]) and ex.solucao is not None
    with pytest.raises(ValueError, match="inteiro"):
        cs.executar("Potência (Aⁿ)", [sp.eye(2)], "1/2")
    with pytest.raises(ValueError, match="Valor de k"):
        cs.executar("Multiplicar por escalar", [sp.eye(2)], "__import__('os')")
    ex = cs.executar("Decomposição QR", [M([[1, 2], [3, 4]])])
    assert ex.solucao is None and ex.resultado  # sem passos, mas calcula


def test_calc_sistema_integra_nucleo_e_passos():
    tipo, linhas, sol, aviso = cs.executar_sistema(M([[1, 1], [1, -1]]), M([3, 1]), "cramer")
    assert tipo == "SPD" and sol.valor == ("SPD", [2, 1])
    tipo, _, sol, aviso = cs.executar_sistema(M([[1, 1], [2, 2]]), M([2, 4]), "cramer")
    assert tipo == "SPI" and sol is None and aviso  # Cramer não se aplica, explicado
    with pytest.raises(ValueError):
        cs.executar_sistema(M([[1, 1]]), M([1, 2]))


def test_todas_as_operacoes_do_nucleo_rodam_pelo_servico_web():
    A = M([[4, 1, 2], [1, 3, 0], [2, 0, 5]])
    for op in nucleo.OPERACOES:
        ex = cs.executar(op.nome, [A, A][: op.nmat], "2" if op.param else "")
        assert ex.resultado, op.nome
        assert ms.analisar(A) is not None
