"""Testes de interface com AppTest: todas as páginas renderizam e os fluxos principais funcionam."""

import pytest

pytest.importorskip("streamlit")
from pathlib import Path  # noqa: E402

from streamlit.testing.v1 import AppTest  # noqa: E402

from matrizes.web.paginas import ESTRUTURA  # noqa: E402

APP = str(Path(__file__).resolve().parents[2] / "matrizes" / "web" / "app.py")
CHAVES = [c for _, c, *_ in ESTRUTURA]


def _app():
    """Renderiza só o corpo da página escolhida (AppTest não troca páginas de st.navigation)."""
    import streamlit as st

    from matrizes.web import paginas, theme
    from matrizes.web.state import obter

    obter()
    theme.aplicar()
    paginas.construir()
    modulo = next(m for _, c, _, m, _ in paginas.ESTRUTURA if c == st.session_state["_alvo"])
    modulo.renderizar()


def novo() -> AppTest:
    return _trocar(AppTest.from_function(_app, default_timeout=90), "inicio")


def _trocar(at, chave, _=""):
    at.session_state["_alvo"] = chave
    return at.run()


def _pg(chave):
    return _trocar(AppTest.from_function(_app, default_timeout=90), chave)


def test_app_principal_com_navegacao_inicia():
    at = AppTest.from_file(APP, default_timeout=90).run()
    assert not at.exception


@pytest.mark.parametrize("chave", CHAVES)
def test_pagina_renderiza_sem_excecao(chave):
    at = _trocar(AppTest.from_function(_app, default_timeout=90), chave)
    assert not at.exception, at.exception


def test_operacao_soma_mostra_resultado_e_passos():
    at = _pg("operacoes")
    at.selectbox(key="op:op").set_value("Soma (A + B)").run()
    at.text_input(
        key=next(k for k in _chaves(at) if k.startswith("op:A:") and k.endswith(":0:0"))
    ).set_value("5").run()
    at.button(key="op:calc").click().run()
    assert not at.exception
    assert any("Passo" in e.label for e in at.expander)
    assert at.session_state["app"].historico.itens[-1].titulo == "Soma (A + B)"


def _chaves(at):
    return [t.key for t in at.text_input if t.key]


def test_erro_de_entrada_nao_quebra():
    at = _pg("operacoes")
    k = next(k for k in _chaves(at) if k.startswith("op:A:") and k.endswith(":0:0"))
    at.text_input(key=k).set_value("__import__('os')").run()
    assert not at.exception
    assert at.error  # mensagem de validação


def test_sistema_spd_classifica():
    at = _pg("sistemas")
    assert not at.exception
    next(
        b for b in at.button if b.label == "Resolver e classificar"
    ).click().run()  # exemplo padrão → SPD
    assert not at.exception
    assert at.session_state["res:sis"][2] == "SPD"


def test_exercicio_certo_e_errado_registra_progresso():
    at = _pg("exercicios")
    assert not at.exception
    est = at.session_state["app"]
    at.button(key="ex:ver").click().run()
    assert not at.exception
    assert est.resumo_progresso()[1] == 1


def test_tema_escuro_injeta_css():
    at = novo()
    at.session_state["app"].preferencias["tema"] = "escuro"
    at.run()
    assert not at.exception
    assert any("stApp" in m.value and "<style>" in m.value for m in at.markdown)
