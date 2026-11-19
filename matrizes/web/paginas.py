"""Mapa de navegação: grupos da barra lateral e suas páginas."""

from __future__ import annotations

import streamlit as st

from .pages import (
    comparacao,
    conceitos,
    configuracoes,
    exemplos,
    exercicios,
    experimentacao,
    geometria,
    historico,
    inicio,
    matrizes_salvas,
    operacoes,
    passo_a_passo,
    propriedades,
    sistemas,
    transformacoes,
)

I = ":material/{}:"  # noqa: E741

# (grupo, chave, título, módulo, ícone)
ESTRUTURA = [
    ("", "inicio", "Início", inicio, "home"),
    ("Calculadora", "operacoes", "Operações", operacoes, "calculate"),
    ("Calculadora", "propriedades", "Propriedades", propriedades, "fact_check"),
    ("Calculadora", "sistemas", "Sistemas", sistemas, "rule"),
    ("Laboratório", "experimentacao", "Experimentação", experimentacao, "science"),
    ("Laboratório", "transformacoes", "Transformações lineares", transformacoes, "transform"),
    ("Laboratório", "comparacao", "Comparação de matrizes", comparacao, "compare_arrows"),
    ("Laboratório", "geometria", "Visualização geométrica", geometria, "scatter_plot"),
    ("Aprendizado", "conceitos", "Conceitos", conceitos, "menu_book"),
    ("Aprendizado", "passo_a_passo", "Passo a passo", passo_a_passo, "format_list_numbered"),
    ("Aprendizado", "exemplos", "Exemplos resolvidos", exemplos, "task_alt"),
    ("Aprendizado", "exercicios", "Exercícios", exercicios, "edit_note"),
    ("Ferramentas", "historico", "Histórico", historico, "history"),
    ("Ferramentas", "matrizes_salvas", "Matrizes salvas", matrizes_salvas, "save"),
    ("Ferramentas", "configuracoes", "Configurações", configuracoes, "settings"),
]


def construir() -> dict[str, list[st.Page]]:
    grupos: dict[str, list[st.Page]] = {}
    mapa: dict[str, st.Page] = {}
    for grupo, chave, titulo, modulo, icone in ESTRUTURA:
        pagina = st.Page(
            modulo.renderizar,
            title=titulo,
            icon=I.format(icone),
            url_path=chave,
            default=chave == "inicio",
        )
        grupos.setdefault(grupo, []).append(pagina)
        mapa[chave] = pagina
    st.session_state["_paginas"] = mapa
    return grupos
