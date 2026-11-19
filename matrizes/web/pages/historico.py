"""Ferramentas → Histórico de operações da sessão."""

import streamlit as st

from ..components import math_renderer as mr
from ..components import ui
from ..state import obter


def renderizar() -> None:
    est = obter()
    h = est.historico
    ui.cabecalho("Histórico", "Operações desta sessão (somem ao fechar o navegador).")
    if not len(h):
        st.info("Nada por aqui ainda. Faça um cálculo em Calculadora.")
        return
    c1, c2 = st.columns([1, 4])
    c1.button("Limpar histórico", on_click=h.limpar)
    categorias = sorted({r.categoria for r in h.itens})
    filtro = c2.multiselect("Filtrar por categoria", categorias, default=categorias)
    for r in reversed(h.itens):
        if r.categoria not in filtro:
            continue
        icone = ":material/check_circle:" if r.ok else ":material/error:"
        with st.expander(f"{r.quando} · {r.categoria} · {r.titulo}", icon=icone):
            for nome, M in r.entradas.items():
                mr.matriz(M, nome)
            if r.latex:
                st.latex(r.latex)
            if r.texto:
                st.caption(r.texto)
