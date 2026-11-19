"""Smoke test da janela. É pulado automaticamente se não houver display (ex.: CI sem xvfb)."""

import pytest
import sympy as sp

tk = pytest.importorskip("tkinter")

from matrizes import gui  # noqa: E402


@pytest.fixture
def app(monkeypatch):
    try:
        raiz = tk.Tk()
    except tk.TclError:
        pytest.skip("sem display gráfico")
    raiz.withdraw()
    erros = []
    monkeypatch.setattr(gui.messagebox, "showerror", lambda titulo, msg, **kw: erros.append(msg))
    a = gui.App(raiz)
    a.erros = erros
    yield a
    raiz.destroy()


def definir_sistema(app, linhas, metodo):
    app.var_m.set(len(linhas))
    app.var_n.set(len(linhas[0]) - 1)
    app.montar_grade()
    for i, lin in enumerate(linhas):
        for j, v in enumerate(lin):
            app.cel_sis[i][j].delete(0, "end")
            app.cel_sis[i][j].insert(0, str(v))
    app.cb_metodo.set(metodo)
    app.resolver()


def texto(widget):
    return widget.get("1.0", "end")


def test_operacao_e_memoria(app):
    app.guardar("A", sp.Matrix([[2, 1], [1, 1]]))
    app.cb_op.set("Inversa")
    app.ajustar_campos()
    app.cb_a.set("A")
    app.calcular()
    assert not app.erros
    assert "[  1  -1 ]" in texto(app.saida_ops)
    assert app.mem["R"] == sp.Matrix([[1, -1], [-1, 2]])


def test_erros_viram_avisos_e_nao_excecoes(app):
    app.guardar("A", sp.Matrix([[1, 2], [2, 4]]))
    app.cb_op.set("Inversa")
    app.cb_a.set("A")
    app.calcular()
    assert app.erros and "não possui inversa" in app.erros[-1]
    app.erros.clear()
    app.cb_op.set("Multiplicar por escalar")
    app.ajustar_campos()
    app.var_param.set("abc")
    app.calcular()
    assert app.erros


@pytest.mark.parametrize(
    "linhas, tipo",
    [
        ([[1, 1, 2], [1, -1, 0]], "SPD"),
        ([[1, 1, 2], [2, 2, 4]], "SPI"),
        ([[1, 1, 2], [1, 1, 3]], "SI"),
    ],
)
def test_sistema_classifica_e_desenha_grafico(app, linhas, tipo):
    definir_sistema(app, linhas, "Comparar os três")
    assert f"Classificação: {tipo}" in texto(app.saida_sis)
    assert app.ultimo_sistema[2] == tipo
    if gui.GRAFICO:
        assert app.canvas is not None


def test_celula_invalida(app):
    definir_sistema(app, [[1, 1, 2], [1, -1, 0]], "Regra de Cramer")
    app.cel_sis[0][0].delete(0, "end")
    app.cel_sis[0][0].insert(0, "x")
    app.resolver()
    assert app.erros and "equação 1, coluna 1" in app.erros[-1]


def test_alternar_tema(app):
    assert app.nome_tema == "claro"
    definir_sistema(app, [[1, 1, 2], [1, -1, 0]], "Escalonamento (Gauss-Jordan)")
    app.alternar_tema()
    assert app.nome_tema == "escuro" and app.t is gui.TEMAS["escuro"]
    app.alternar_tema()
    assert app.nome_tema == "claro"
