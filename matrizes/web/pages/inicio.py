"""Painel inicial: atalhos, indicadores, recursos e atividade recente."""

import streamlit as st

from ..components import ui
from ..state import obter

# (página, título, texto, ícone)
ATALHOS = [
    (
        "operacoes",
        "Operações",
        "Some, multiplique, inverta e mais, com passo a passo.",
        "calculadora",
    ),
    ("sistemas", "Sistemas lineares", "Resolva e classifique em SPD, SPI ou SI.", "sistema"),
    (
        "experimentacao",
        "Laboratório",
        "Mude uma matriz e veja o que acontece com suas propriedades.",
        "laboratorio",
    ),
    (
        "transformacoes",
        "Transformações",
        "Veja rotações, reflexões e cisalhamentos no plano.",
        "transformar",
    ),
    (
        "exercicios",
        "Exercícios",
        "Pratique com correção automática e solução explicada.",
        "lapis",
    ),
    ("conceitos", "Conceitos", "Definições e fórmulas essenciais de Álgebra Linear.", "livro"),
]

# (título, texto, ícone): o que torna a plataforma diferente
RECURSOS = [
    (
        "Aritmética exata",
        "Frações e raízes continuam exatas: 1/3 nunca vira 0,3333.",
        "escudo",
    ),
    (
        "Passo a passo em LaTeX",
        "Cada resultado vem com a fórmula, a substituição e a interpretação.",
        "passos",
    ),
    (
        "Exportação",
        "Copie o LaTeX ou baixe CSV e .tex de qualquer resultado.",
        "baixar",
    ),
    (
        "Atalhos",
        "Ctrl+Enter calcula; cole matrizes de texto e use predefinidas.",
        "raio",
    ),
]

CHIPS = [
    ("escudo", "Resultados exatos"),
    ("passos", "Passo a passo"),
    ("geometria", "Visualização 2D"),
    ("lapis", "Exercícios"),
]


def renderizar() -> None:
    est = obter()
    ui.hero(chips=CHIPS)
    resolvidos, tentados = est.resumo_progresso()
    c = st.columns(4)
    with c[0]:
        ui.kpi(str(len(est.memoria)), "matrizes salvas", "salvar", 0)
    with c[1]:
        ui.kpi(str(len(est.historico)), "operações no histórico", "historico", 1)
    with c[2]:
        ui.kpi(str(len(est.experimentos)), "experimentos salvos", "laboratorio", 2)
    with c[3]:
        ui.kpi(
            f"{resolvidos}/{tentados}" if tentados else "—",
            "exercícios resolvidos",
            "check",
            3,
        )

    st.subheader("Por onde começar")
    paginas = st.session_state.get("_paginas", {})
    cols = st.columns(3)
    for k, (chave, titulo, texto, icone) in enumerate(ATALHOS):
        with cols[k % 3]:
            ui.cartao(titulo, texto, icone, k)
            if chave in paginas:
                st.page_link(
                    paginas[chave], label=f"Abrir {titulo}", icon=":material/arrow_forward:"
                )

    st.subheader("Por que usar")
    cols_recursos = st.columns(len(RECURSOS))
    for k, (titulo, texto, icone) in enumerate(RECURSOS):
        with cols_recursos[k]:
            ui.cartao(titulo, texto, icone, k)

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
