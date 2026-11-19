"""Aprendizado → Conceitos e fórmulas."""

import streamlit as st

from ..components import ui
from ..services import education_service as edu


def renderizar() -> None:
    ui.cabecalho("Conceitos", "Definições e fórmulas essenciais, com ligação para o laboratório.")
    busca = (
        st.text_input("Buscar", placeholder="ex.: determinante", key="conc:busca").strip().lower()
    )
    paginas = st.session_state.get("_paginas", {})
    achou = False
    for c in edu.CONCEITOS:
        if busca and busca not in (c.titulo + c.texto).lower():
            continue
        achou = True
        with st.expander(c.titulo, expanded=bool(busca)):
            st.write(c.texto)
            st.latex(c.formula)
            st.markdown("**Exemplo**")
            st.latex(c.exemplo)
            if c.pagina in paginas:
                st.page_link(
                    paginas[c.pagina], label="Experimente na prática", icon=":material/science:"
                )
    if not achou:
        st.info("Nenhum conceito encontrado.")
