"""Painel inicial: atalhos, indicadores e atividade recente."""

import streamlit as st

from ..components import ui
from ..state import obter

ATALHOS = [
    ("operacoes", "Operações", "Some, multiplique, inverta e mais, com passo a passo."),
    ("sistemas", "Sistemas lineares", "Resolva e classifique em SPD, SPI ou SI."),
    (
        "experimentacao",
        "Laboratório",
        "Mude uma matriz e veja o que acontece com suas propriedades.",
    ),
    ("transformacoes", "Transformações", "Veja rotações, reflexões e cisalhamentos no plano."),
    ("exercicios", "Exercícios", "Pratique com correção automática e solução explicada."),
    ("conceitos", "Conceitos", "Definições e fórmulas essenciais de Álgebra Linear."),
]


def renderizar() -> None:
    est = obter()
    ui.hero()
    resolvidos, tentados = est.resumo_progresso()
    c = st.columns(4)
    with c[0]:
        ui.kpi(str(len(est.memoria)), "matrizes salvas")
    with c[1]:
        ui.kpi(str(len(est.historico)), "operações no histórico")
    with c[2]:
        ui.kpi(str(len(est.experimentos)), "experimentos salvos")
    with c[3]:
        ui.kpi(f"{resolvidos}/{tentados}" if tentados else "—", "exercícios resolvidos")

    st.subheader("Por onde começar")
    paginas = st.session_state.get("_paginas", {})
    cols = st.columns(3)
    for k, (chave, titulo, texto) in enumerate(ATALHOS):
        with cols[k % 3]:
            ui.cartao(titulo, texto)
            if chave in paginas:
                st.page_link(
                    paginas[chave], label=f"Abrir {titulo}", icon=":material/arrow_forward:"
                )

    esq, dir_ = st.columns(2)
    with esq:
        st.subheader("Matrizes recentes")
        est.limpar_recentes_inexistentes()
        if est.recentes:
            from ..components import math_renderer as mr

            for nome in est.recentes[:3]:
                mr.matriz(est.memoria.obter(nome), nome)
        else:
            st.caption("Salve uma matriz para vê-la aqui.")
    with dir_:
        st.subheader("Últimas operações")
        if len(est.historico):
            for r in est.historico.recentes(5):
                st.markdown(f"- **{r.titulo}** · {r.categoria} · {r.quando[-8:]}")
        else:
            st.caption("Seus cálculos aparecerão aqui.")
