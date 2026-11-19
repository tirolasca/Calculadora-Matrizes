"""Tabelas HTML estilizadas (o tema escuro não alcança st.dataframe/data_editor)."""

from __future__ import annotations

from html import escape

import streamlit as st


def tabela(cabecalho: list[str], linhas: list[list[str]]) -> None:
    th = "".join(f"<th>{escape(c)}</th>" for c in cabecalho)
    corpo = "".join(
        "<tr>" + "".join(f"<td>{escape(str(c))}</td>" for c in linha) + "</tr>" for linha in linhas
    )
    st.markdown(
        f'<table class="mx-table"><thead><tr>{th}</tr></thead><tbody>{corpo}</tbody></table>',
        unsafe_allow_html=True,
    )
