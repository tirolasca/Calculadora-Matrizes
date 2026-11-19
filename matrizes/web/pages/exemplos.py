"""Aprendizado → Exemplos resolvidos (passo a passo gerado e validado pelo núcleo)."""

import streamlit as st

from ..components import math_renderer as mr
from ..components import ui
from ..services import education_service as edu


def renderizar() -> None:
    ui.cabecalho("Exemplos resolvidos", "Problemas clássicos resolvidos em detalhe.")
    ex = st.selectbox("Exemplo", edu.EXEMPLOS, format_func=lambda e: e.titulo, key="exm:sel")
    if ex.comentario:
        st.caption(ex.comentario)
    mr.solucao(edu.resolver_exemplo(ex), f"exm:{ex.id}")
    st.caption("Quer variar os números? Use a página Passo a passo com as suas matrizes.")
