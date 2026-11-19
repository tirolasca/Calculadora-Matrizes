"""Aprendizado → Exercícios com correção automática e solução explicada."""

import random

import streamlit as st

from ..components import math_renderer as mr
from ..components import ui
from ..components.matrix_editor import editor_matriz
from ..services import education_service as edu
from ..state import obter


def _novo(nivel: str) -> None:
    st.session_state["ex:semente"] = random.randrange(10**6)
    st.session_state["ex:feedback"] = None


def renderizar() -> None:
    est = obter()
    ui.cabecalho("Exercícios", "Resolva, confira e veja a solução explicada.")
    resolvidos, tentados = est.resumo_progresso()
    st.caption(f"Progresso: {resolvidos} resolvido(s) de {tentados} tentado(s).")
    nivel = st.radio(
        "Nível", edu.NIVEIS, horizontal=True, key="ex:nivel", on_change=_novo, args=("",)
    )
    if "ex:semente" not in st.session_state:
        _novo(nivel)
    ex = edu.gerar(nivel, st.session_state["ex:semente"])
    st.subheader(ex.titulo)
    st.write(ex.enunciado)
    cols = st.columns(len(ex.dados))
    for col, (rot, M) in zip(cols, ex.dados.items(), strict=True):
        with col:
            mr.matriz(M, rot)

    resposta = None
    if ex.formato == "matriz":
        r, c = ex.resposta.shape
        resposta = editor_matriz(f"ex:resp:{ex.id}", "Sua resposta", (r, c), ferramentas=False)
    elif ex.formato == "classe":
        resposta = st.radio(
            "Classificação", ["SPD", "SPI", "SI"], horizontal=True, key=f"ex:cl:{ex.id}"
        )
    else:
        resposta = st.text_input(
            "Sua resposta", key=f"ex:txt:{ex.id}", placeholder="número ou fração, ex.: -3/2"
        )

    c1, c2, c3 = st.columns(3)
    if c1.button("Verificar", type="primary", key="ex:ver"):
        if resposta is None:
            st.error("Corrija a resposta antes de verificar.")
        else:
            cor = edu.corrigir(ex, resposta)
            est.registrar_tentativa(ex.id, cor.ok)
            st.session_state["ex:feedback"] = (ex.id, cor)
    c2.button("Outro exercício", key="ex:novo", on_click=_novo, args=(nivel,))
    mostrar = c3.toggle("Ver dica", key=f"ex:dica:{ex.id}")
    if mostrar:
        st.info(ex.dica, icon=":material/tips_and_updates:")
    fb = st.session_state.get("ex:feedback")
    if fb and fb[0] == ex.id:
        (st.success if fb[1].ok else st.error)(fb[1].feedback)
    with st.expander("Solução explicada"):
        try:
            mr.solucao(edu.solucao(ex), f"ex:sol:{ex.id}")
        except ValueError as e:
            st.info(str(e))
    if ex.pagina in st.session_state.get("_paginas", {}):
        st.page_link(
            st.session_state["_paginas"][ex.pagina],
            label="Abrir na calculadora",
            icon=":material/calculate:",
        )
