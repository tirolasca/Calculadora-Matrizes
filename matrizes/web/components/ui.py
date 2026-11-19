"""Blocos visuais reutilizáveis (cabeçalho, cartões, indicadores, selos)."""

from __future__ import annotations

from html import escape

import streamlit as st

from ..config import NOME_APP, SUBTITULO


def hero(titulo: str = NOME_APP, subtitulo: str = SUBTITULO) -> None:
    st.markdown(
        f'<div class="mx-hero"><h1>{escape(titulo)}</h1><p>{escape(subtitulo)}</p></div>',
        unsafe_allow_html=True,
    )


def cabecalho(titulo: str, subtitulo: str = "") -> None:
    st.title(titulo)
    if subtitulo:
        st.caption(subtitulo)


def cartao(titulo: str, corpo: str) -> None:
    st.markdown(
        f'<div class="mx-card"><h4>{escape(titulo)}</h4><p>{escape(corpo)}</p></div>',
        unsafe_allow_html=True,
    )


def kpi(valor: str, rotulo: str) -> None:
    st.markdown(
        f'<div class="mx-card mx-kpi"><div class="v">{escape(valor)}</div>'
        f'<div class="r">{escape(rotulo)}</div></div>',
        unsafe_allow_html=True,
    )


def selo(texto: str, tom: str = "ok") -> str:
    """HTML de um selo; tom: ok | aviso | perigo."""
    return f'<span class="mx-badge mx-{tom}">{escape(texto)}</span>'
