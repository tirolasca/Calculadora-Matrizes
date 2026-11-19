"""Laboratório → Visualização geométrica: vetores, span, independência e autovetores."""

import streamlit as st
import sympy as sp

from ..components import math_renderer as mr
from ..components import ui
from ..components.matrix_editor import editor_matriz
from ..services import geometry_service as geo
from ..services import matrix_service as ms
from ..theme import estilo_grafico, paleta


def renderizar() -> None:
    ui.cabecalho(
        "Visualização geométrica", "Vetores, span, independência linear, bases e autovetores."
    )
    aba1, aba2 = st.tabs(["Vetores, span e bases", "Autovetores"])
    estilo = estilo_grafico(paleta())

    with aba1:
        n = st.radio("Quantidade de vetores", [2, 3], horizontal=True, key="geo:n")
        padrao = [("1", "0"), ("1", "1"), ("2", "2")]
        vs, ok = [], True
        cols = st.columns(n)
        for k in range(n):
            with cols[k]:
                st.markdown(f"**v{k + 1}**")
                try:
                    x = ms.expressao(st.text_input("x", padrao[k][0], key=f"geo:{k}:x"))
                    y = ms.expressao(st.text_input("y", padrao[k][1], key=f"geo:{k}:y"))
                    vs.append((x, y))
                except ValueError as e:
                    st.error(str(e))
                    ok = False
        if ok:
            if any(v[0].free_symbols or v[1].free_symbols for v in vs):
                st.error("Use apenas números.")
            else:
                an = geo.analisar_vetores(vs)
                c1, c2 = st.columns([3, 2])
                with c1:
                    st.pyplot(geo.figura_vetores(vs, estilo), clear_figure=True)
                with c2:
                    st.markdown(f"**Span:** {an.span}  \n**Posto:** {an.posto}")
                    (st.success if an.independentes else st.warning)(an.texto)
                    if an.base:
                        st.info("{v₁, v₂} é uma base de R².")

    with aba2:
        A = editor_matriz("geo:A", "Matriz 2×2", quadrada=True, exemplo=[["2", "1"], ["1", "2"]])
        if A is None:
            return
        if A.shape != (2, 2) or A.free_symbols:
            st.error("Use uma matriz 2×2 numérica.")
            return
        ae = geo.analisar_autovetores(A)
        c1, c2 = st.columns([3, 2])
        with c1:
            st.pyplot(geo.figura_autovetores(A, estilo), clear_figure=True)
        with c2:
            if ae.complexos:
                st.warning(ae.texto)
                st.latex(r"\lambda = " + ", ".join(sp.latex(v) for v in A.eigenvals()))
            else:
                st.success(ae.texto)
                for d in ae.reais:
                    mr.matriz(d.vetor, rf"v\ (\lambda={sp.latex(d.valor)})")
