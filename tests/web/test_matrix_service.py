"""Serviço de matrizes da web: entrada segura, memória, propriedades, verificações."""

import json

import pytest
import sympy as sp

from matrizes import nucleo as core
from matrizes.web.services import matrix_service as ms

x, a, b = sp.symbols("x a b")


def M(*linhas):
    return sp.Matrix(linhas)


# ---------- entrada segura ----------
@pytest.mark.parametrize(
    "txt, esperado",
    [
        ("3", 3),
        ("-2.5", sp.Rational(-5, 2)),
        ("1/2", sp.Rational(1, 2)),
        ("1,5", sp.Rational(3, 2)),
        ("0.1+0.2", sp.Rational(3, 10)),  # exato, sem erro binário
        ("1e3", 1000),
        ("2^3", 8),
        ("sqrt(2)", sp.sqrt(2)),
        ("√2", sp.sqrt(2)),
        ("√(8)/√2", 2),
        ("π", sp.pi),
        ("x^2", x**2),
        ("a + 2*b", a + 2 * b),
        ("(1+x)*(1-x)", (1 + x) * (1 - x)),
        ("-x", -x),
        ("2**(1/2)", sp.sqrt(2)),
        ("I", sp.I),
        ("sin(pi/2)", 1),
    ],
)
def test_expressao_valida(txt, esperado):
    assert sp.simplify(ms.expressao(txt) - esperado) == 0


@pytest.mark.parametrize(
    "txt",
    [
        "",
        "   ",
        "__import__('os').system('echo hacked')",
        "os.system('ls')",
        "().__class__",
        "[1, 2]",
        "{1: 2}",
        "lambda: 1",
        "open('/etc/passwd')",
        "print(1)",
        "eval('1')",
        "x.y",
        "x[0]",
        "'texto'",
        "True",
        "None",
        "1/0",
        "0**-1",
        "2**1000",
        "x**y",
        "x**100",
        "9" * 40,
        "sqrt()",
        "sqrt(1, 2)",
        "sqrt",
        "2x",
        "2√3",
        "1 +",
        "a" * 200,
        "(" * 100 + "1" + ")" * 100,
        "x if 1 else 2",
        "x and y",
        "x < 2",
        "1 // 2",
        "5 % 2",
        "-",
    ],
)
def test_expressao_rejeita_entradas_perigosas_ou_invalidas(txt):
    with pytest.raises(ValueError):
        ms.expressao(txt)


def test_expressao_nao_executa_codigo():
    ms.expressao("1")
    with pytest.raises(ValueError):
        ms.expressao("__import__('sys').modules.clear()")
    import sys

    assert "sympy" in sys.modules  # nada foi executado


def test_matriz_de_texto_e_ida_e_volta():
    A = ms.matriz_de_texto([["1", "1/2"], ["sqrt(2)", "a+1"]])
    assert A == M([1, sp.Rational(1, 2)], [sp.sqrt(2), a + 1])
    assert ms.matriz_de_texto(ms.matriz_para_texto(A)) == A


def test_matriz_de_texto_lista_todos_os_erros():
    with pytest.raises(ms.EntradaInvalida) as e:
        ms.matriz_de_texto([["1", "x y"], ["", "2"]])
    assert len(e.value.erros) == 2
    assert "Linha 1, coluna 2" in e.value.erros[0] and "Linha 2, coluna 1" in e.value.erros[1]
    with pytest.raises(ms.EntradaInvalida):
        ms.matriz_de_texto([])


# ---------- predefinidas ----------
@pytest.mark.parametrize("nome", ms.nomes_predefinidas())
@pytest.mark.parametrize("dims", [(2, 2), (3, 3), (3, 4)])
def test_predefinidas_tem_a_dimensao_pedida(nome, dims):
    assert ms.predefinida(nome, *dims).shape == dims


def test_predefinidas_tem_as_propriedades_anunciadas():
    est = lambda nome, n=4: core.estrutura(ms.predefinida(nome, n))  # noqa: E731
    assert est("Identidade")["identidade"] and est("Nula")["nula"]
    assert est("Diagonal (1, 2, 3, …)")["diagonal"]
    assert (
        est("Triangular superior")["triangular_superior"]
        and not est("Triangular superior")["triangular_inferior"]
    )
    assert est("Triangular inferior")["triangular_inferior"]
    assert est("Simétrica")["simetrica"] and est("Antissimétrica")["antissimetrica"]
    assert est("Tridiagonal (2 e 1)")["invertivel"] and est("Tridiagonal (2 e 1)")["simetrica"]
    assert not est("Singular (linhas proporcionais)")["invertivel"]
    assert ms.predefinida("Singular (linhas proporcionais)", 4).rank() == 1
    assert ms.predefinida("Hilbert", 3)[1, 2] == sp.Rational(1, 4)


def test_aleatoria_e_deterministica_pela_semente():
    nome = "Aleatória (inteiros de −9 a 9)"
    assert ms.predefinida(nome, 3, semente=7) == ms.predefinida(nome, 3, semente=7)
    assert ms.predefinida(nome, 3, semente=7) != ms.predefinida(nome, 3, semente=8)
    assert all(-9 <= v <= 9 for v in ms.predefinida(nome, 4, semente=1))


# ---------- memória ----------
def test_memoria_crud():
    mem = ms.Memoria()
    assert mem.proximo_nome() == "A"
    assert mem.salvar("A", M([1, 2], [3, 4])) == "A"
    assert mem.proximo_nome() == "B"
    mem.salvar("B", sp.eye(2))
    assert mem.nomes() == ["A", "B"] and "A" in mem and len(mem) == 2
    assert mem.obter("A") == M([1, 2], [3, 4])
    # renomear preserva a ordem
    assert mem.renomear("A", "Mat1") == "Mat1" and mem.nomes() == ["Mat1", "B"]
    # duplicar
    assert mem.duplicar("Mat1") == "Mat1_copia" and mem.duplicar("Mat1") == "Mat1_copia2"
    assert mem.obter("Mat1_copia") == mem.obter("Mat1")
    mem.excluir("B")
    assert "B" not in mem
    with pytest.raises(KeyError):
        mem.obter("B")


def test_memoria_nao_compartilha_referencias():
    mem = ms.Memoria()
    original = sp.Matrix([[1, 2], [3, 4]])
    mem.salvar("A", original)
    original[0, 0] = 99
    assert mem.obter("A")[0, 0] == 1


@pytest.mark.parametrize("nome", ["", "1A", "a b", "A-B", "x" * 17, "é"])
def test_memoria_rejeita_nomes_invalidos(nome):
    with pytest.raises(ValueError):
        ms.Memoria().salvar(nome, sp.eye(2))


def test_memoria_conflitos():
    mem = ms.Memoria()
    mem.salvar("A", sp.eye(2))
    mem.salvar("B", sp.eye(2))
    with pytest.raises(ValueError, match="Já existe"):
        mem.renomear("A", "B")
    with pytest.raises(ValueError, match="Já existe"):
        mem.salvar("A", sp.eye(3), sobrescrever=False)
    with pytest.raises(KeyError):
        mem.renomear("Z", "Y")


def test_memoria_json_ida_e_volta_com_fracoes_e_simbolos():
    mem = ms.Memoria()
    mem.salvar("A", M([sp.Rational(1, 3), sp.sqrt(2)], [a + 1, x**2]))
    mem.salvar("H", ms.predefinida("Hilbert", 3))
    outra = ms.Memoria()
    assert outra.importar_json(mem.exportar_json()) == 2
    assert outra.matrizes == mem.matrizes
    assert json.loads(mem.exportar_json())["versao"] == 1


@pytest.mark.parametrize(
    "texto",
    [
        "",
        "isso não é json",
        "[]",
        '{"matrizes": 3}',
        '{"matrizes": {"A": [["__import__(1)"]]}}',
        '{"matrizes": {"1x": [["1"]]}}',
    ],
)
def test_memoria_importacao_invalida(texto):
    with pytest.raises(ValueError):
        ms.Memoria().importar_json(texto)


def test_importar_substituindo():
    mem = ms.Memoria()
    mem.salvar("A", sp.eye(2))
    mem.importar_json(json.dumps({"matrizes": {"B": [["1"]]}}), substituir=True)
    assert mem.nomes() == ["B"]


# ---------- histórico ----------
def test_historico_limite_e_ordem():
    h = ms.Historico(limite=3)
    for i in range(5):
        h.adicionar("Operação", f"op {i}", {"A": sp.eye(2)}, texto=str(i))
    assert len(h) == 3 and [r.titulo for r in h.recentes(2)] == ["op 4", "op 3"]
    h.limpar()
    assert len(h) == 0


# ---------- propriedades ----------
def test_analisar_matriz_numerica():
    p = ms.analisar(M([2, 1], [1, 2]))
    assert p.determinante == 3 and p.posto == 2 and p.traco == 4 and p.invertivel is True
    assert [round(z.real) for z, _ in p.autovalores] == [1, 3]
    assert p.dim_autoespacos == 2 and p.estrutura["simetrica"] is True
    assert dict(p.autovalores_exatos) == {1: 1, 3: 1}


def test_analisar_singular_e_nao_quadrada():
    p = ms.analisar(M([1, 2], [2, 4]))
    assert p.determinante == 0 and p.posto == 1 and p.invertivel is False
    assert p.dim_autoespacos == 2  # autovalores 0 e 5
    q = ms.analisar(M([1, 2, 3], [4, 5, 6]))
    assert q.determinante is None and q.posto == 2 and q.autovalores is None
    assert ms.tabela_propriedades(q)["Invertível"].startswith("—")


def test_analisar_defectiva_tem_menos_autovetores():
    p = ms.analisar(M([1, 1], [0, 1]))
    assert p.autovalores[0][1] == 2 and p.dim_autoespacos == 1


def test_analisar_simbolica():
    p = ms.analisar(M([a, 0], [0, b]))
    assert p.simbolica and p.determinante == a * b and p.invertivel is None
    assert p.autovalores is None and set(p.autovalores_exatos) == {a, b}


def test_analisar_complexos():
    p = ms.analisar(M([0, -1], [1, 0]))
    assert sorted(round(z.imag) for z, _ in p.autovalores) == [-1, 1]
    assert "i" in ms.tabela_propriedades(p)["Autovalores"]


def test_explicar_mudancas_so_do_que_mudou():
    A = M([1, 2], [3, 4])
    B = M([1, 2], [2, 4])  # agora singular
    mud = {c[0]: c for c in ms.explicar_mudancas(ms.analisar(A), ms.analisar(B))}
    assert "Determinante" in mud and "deixou de ser invertível" in mud["Determinante"][3]
    assert mud["Posto"][1:3] == ("2", "1")
    assert mud["Invertível"][1:3] == ("sim", "não")
    assert ms.explicar_mudancas(ms.analisar(A), ms.analisar(A)) == []


def test_mudanca_nem_sempre_altera_propriedades():
    # alterar um elemento sem mudar nada importante: o código não presume mudança
    A, B = M([1, 0], [0, 1]), M([1, 5], [0, 1])
    mud = {c[0] for c in ms.explicar_mudancas(ms.analisar(A), ms.analisar(B))}
    assert "Determinante" not in mud and "Posto" not in mud and "Traço" not in mud
    assert "Simétrica" in mud


# ---------- comparação ----------
def test_comparar_matrizes():
    c = ms.comparar_matrizes(M([1, 2], [3, 4]), M([1, 2], [3, 5]))
    assert (
        not c.iguais
        and c.posicoes_diferentes == [(1, 1)]
        and c.maior_diferenca == 1.0
        and c.multiplo is None
    )
    c = ms.comparar_matrizes(M([2, 4], [6, 8]), M([1, 2], [3, 4]))
    assert c.multiplo == 2 and not c.iguais
    c = ms.comparar_matrizes(M([1, 2], [3, 4]), M([1, 3], [2, 4]))
    assert c.uma_e_transposta_da_outra
    assert ms.comparar_matrizes(M([1, 2]), M([1, 2, 3])).mesma_dimensao is False
    assert ms.comparar_matrizes(sp.eye(2), sp.eye(2)).iguais is True


def test_estatisticas_e_valores():
    s = ms.estatisticas(M([1, 0], [-2, 5]))
    assert (s.minimo, s.maximo, s.soma, s.zeros, s.total) == (-2, 5, 4, 1, 4)
    assert s.norma_frobenius == pytest.approx(30**0.5)
    with pytest.raises(ValueError):
        ms.valores_numericos(M([a]))
    with pytest.raises(ValueError):
        ms.valores_numericos(M([sp.I]))


# ---------- propriedades algébricas ----------
def test_comutatividade_nao_vale_em_geral():
    A, B = M([1, 1], [0, 1]), M([1, 0], [1, 1])
    v = ms.verificar_comutatividade(A, B)
    assert (
        v.igual is False and v.vale_em_geral is False and v.esquerda == A * B and v.direita == B * A
    )
    # mas pode coincidir em casos especiais (A e uma potência de A)
    v2 = ms.verificar_comutatividade(A, A * A)
    assert v2.igual is True and v2.vale_em_geral is False and "coincidência" in v2.comentario


@pytest.mark.parametrize("semente", range(5))
def test_propriedades_gerais_valem_em_exemplos_aleatorios(semente):
    nome = "Aleatória (inteiros de −9 a 9)"
    A, B, C = (ms.predefinida(nome, 3, semente=semente * 10 + k) for k in range(3))
    for v in (
        ms.verificar_associatividade(A, B, C),
        ms.verificar_distributividade(A, B, C),
        ms.verificar_transposta_produto(A, B),
        ms.verificar_det_produto(A, B),
    ):
        assert v.igual is True and v.vale_em_geral is True, v.nome
    if A.det() != 0:
        assert ms.verificar_inversa(A).igual is True


def test_transposta_do_produto_inverte_a_ordem():
    A, B = M([1, 2, 3], [4, 5, 6]), M([1, 0], [2, 1], [0, 3])
    assert ms.verificar_transposta_produto(A, B).igual
    assert (A.T * B.T).shape != (B.T * A.T).shape or A.T * B.T != B.T * A.T


def test_verificacoes_exigem_dimensoes_compativeis():
    A, B = M([1, 2, 3]), M([1, 2])
    for chamada in (
        lambda: ms.verificar_comutatividade(A, M([1], [2], [3], [4])),
        lambda: ms.verificar_associatividade(A, B, B),
        lambda: ms.verificar_distributividade(A, B, B),
        lambda: ms.verificar_transposta_produto(A, B),
        lambda: ms.verificar_det_produto(A, B),
        lambda: ms.verificar_inversa(A),
        lambda: ms.verificar_inversa(M([1, 2], [2, 4])),
    ):
        with pytest.raises(ValueError):
            chamada()


def test_verificacao_com_simbolos():
    A, B = M([a, 1], [0, 1]), M([1, b], [0, 1])
    assert ms.verificar_det_produto(A, B).igual is True
    assert ms.verificar_transposta_produto(A, B).igual is True
