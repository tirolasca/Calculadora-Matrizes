"""Calculadora → Sistemas lineares."""

import streamlit as st

from matrizes import nucleo

from ..components import math_renderer as mr
from ..components import ui
from ..components.matrix_editor import editor_matriz
from ..services import calc_service as cs
from ..services import step_service as ss
from ..state import obter
from ..theme import estilo_grafico, paleta

ROTULOS = {
    "gauss": "Escalonamento (Gauss-Jordan)",
    "cramer": "Regra de Cramer",
    "inversa": "Matriz inversa",
    "todos": "Comparar os três métodos",
}
TOM = {"SPD": "ok", "SPI": "aviso", "SI": "perigo"}


def renderizar() -> None:
    est = obter()
    ui.cabecalho(
        "Sistemas lineares",
        "Digite a matriz aumentada [A | b]: a última coluna é o termo independente.",
    )
    M = editor_matriz(
        "sis",
        "Matriz aumentada [A | b]",
        exemplo=[["2", "1", "-1", "8"], ["-3", "-1", "2", "-11"], ["-2", "1", "2", "-3"]],
    )
    metodo = st.radio(
        "Método", list(ROTULOS), format_func=ROTULOS.get, horizontal=True, key="sis:metodo"
    )

    if st.button("Resolver e classificar", type="primary", icon=":material/rule:"):
        st.session_state.pop("res:sis", None)
        if M is None:
            st.error("Corrija os elementos inválidos antes de resolver.")
        elif M.cols < 2:
            st.error("A matriz aumentada precisa de pelo menos 2 colunas.")
        else:
            A, b = M[:, :-1], M[:, -1]
            try:
                if A.free_symbols or b.free_symbols:
                    raise ValueError(
                        "Sistemas com parâmetros simbólicos não são suportados; use números."
                    )
                metodos = ["gauss", "cramer", "inversa"] if metodo == "todos" else [metodo]
                tipo, linhas = nucleo.relatorio_sistema(A, b, metodo)
                solucoes = {}
                for m in metodos:
                    _, _, sol, aviso = cs.executar_sistema(A, b, m)
                    solucoes[m] = (sol, aviso)
            except ValueError as e:
                st.error(str(e), icon=":material/error:")
                est.historico.adicionar(
                    "Sistema", "Sistema linear", {"[A|b]": M}, texto=str(e), ok=False
                )
            else:
                est.historico.adicionar(
                    "Sistema",
                    f"Sistema {A.rows}×{A.cols} ({ROTULOS[metodo]})",
                    {"A": A, "b": b},
                    texto=f"{tipo}",
                )
                st.session_state["res:sis"] = (A, b, tipo, linhas, solucoes)

    dados = st.session_state.get("res:sis")
    if not dados:
        return
    A, b, tipo, linhas, solucoes = dados
    st.divider()
    nomes = {"SPD": "Possível e Determinado", "SPI": "Possível e Indeterminado", "SI": "Impossível"}
    st.markdown(ui.selo(tipo, TOM[tipo]) + f" **Sistema {nomes[tipo]}**", unsafe_allow_html=True)
    st.code("\n".join(linhas), language=None)

    fig = nucleo.figura_sistema(A, b, tipo, estilo_grafico(paleta()))
    if fig is not None:
        _, centro, _ = st.columns([1, 2, 1])
        with centro:
            st.pyplot(fig, clear_figure=True)
    if len(solucoes) > 1:
        abas = st.tabs([ROTULOS[m] for m in solucoes])
        for aba, (m, (sol, aviso)) in zip(abas, solucoes.items(), strict=True):
            with aba:
                _mostrar(sol, aviso, f"sis:{m}")
    else:
        ((m, (sol, aviso)),) = solucoes.items()
        st.subheader("Passo a passo")
        _mostrar(sol, aviso, f"sis:{m}")


def _mostrar(sol: ss.Solucao | None, aviso: str, chave: str) -> None:
    if sol is not None:
        mr.solucao(sol, chave)
    elif aviso:
        st.info(aviso)
