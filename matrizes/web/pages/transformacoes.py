"""Laboratório → Transformações lineares no plano (com composição)."""

import streamlit as st

from ..components import math_renderer as mr
from ..components import ui
from ..components.matrix_editor import editor_matriz
from ..services import geometry_service as geo
from ..services import matrix_service as ms
from ..services import step_service as ss
from ..state import obter
from ..theme import estilo_grafico, paleta

TIPOS = ["—", "Rotação", "Reflexão", "Escala", "Cisalhamento", "Matriz própria"]


def _num(rotulo: str, padrao: str, chave: str):
    return ms.expressao(st.text_input(rotulo, padrao, key=chave))


def _passo(k: int):
    """Matriz do passo k (ou None se '—'). Lança EntradaInvalida em valores ruins."""
    tipo = st.selectbox(f"Passo {k}", TIPOS, key=f"tr:{k}:tipo", index=1 if k == 1 else 0)
    if tipo == "Rotação":
        return geo.rotacao(_num("Ângulo (graus, anti-horário)", "90", f"tr:{k}:ang"))
    if tipo == "Reflexão":
        return geo.reflexao(st.selectbox("Em relação a", list(geo.REFLEXOES), key=f"tr:{k}:ref"))
    if tipo == "Escala":
        c = st.columns(2)
        with c[0]:
            sx = _num("Fator em x", "2", f"tr:{k}:sx")
        with c[1]:
            sy = _num("Fator em y", "1", f"tr:{k}:sy")
        return geo.escala(sx, sy)
    if tipo == "Cisalhamento":
        c = st.columns(2)
        with c[0]:
            kx = _num("Horizontal kx", "1", f"tr:{k}:kx")
        with c[1]:
            ky = _num("Vertical ky", "0", f"tr:{k}:ky")
        return geo.cisalhamento(kx, ky)
    if tipo == "Matriz própria":
        return editor_matriz(
            f"tr:{k}:M",
            "Matriz 2×2",
            quadrada=True,
            ferramentas=False,
            exemplo=[["1", "1"], ["0", "1"]],
        )
    return None


def renderizar() -> None:
    est = obter()
    ui.cabecalho(
        "Transformações lineares",
        "Veja como uma matriz 2×2 deforma o plano. Combine até três passos (composição).",
    )
    forma = st.selectbox("Figura", list(geo.FORMAS), key="tr:forma")
    cols = st.columns(3)
    passos, erro = [], False
    for k in (1, 2, 3):
        with cols[k - 1]:
            try:
                M = _passo(k)
            except ValueError as e:
                st.error(str(e))
                erro = True
                continue
            if M is not None:
                if M.shape != (2, 2):
                    st.error("A matriz precisa ser 2×2.")
                    erro = True
                else:
                    passos.append(M)
    if erro:
        st.stop()
    if not passos:
        st.info("Escolha pelo menos uma transformação.")
        return
    T = geo.compor(passos)
    info = geo.info_determinante(T)

    esq, dir_ = st.columns([3, 2])
    with esq:
        st.pyplot(
            geo.figura_transformacao(
                T, forma, estilo_grafico(paleta()), bool(est.pref("grade_geometria"))
            ),
            clear_figure=True,
        )
    with dir_:
        if len(passos) > 1:
            st.markdown(
                "**Composição** (o primeiro passo é aplicado primeiro, por isso fica à direita):"
            )
            st.latex(
                " ".join(
                    rf"\underbrace{{{ss.latex_matriz(M)}}}_{{\text{{passo {i}}}}}"
                    for i, M in reversed(list(enumerate(passos, 1)))
                )
            )
        mr.matriz(T, "T")
        pts = geo.FORMAS[forma]
        a0, a1 = geo.area_poligono(pts), geo.area_poligono(geo.aplicar(T, pts))
        st.markdown(f"**Área:** {a0:.4g} → {a1:.4g}  ·  **det(T)** = {info.det}")
        (st.warning if info.orientacao != "preservada" else st.success)(info.texto)
        if len(passos) > 1:
            st.caption("A ordem importa: em geral B·A ≠ A·B.")
            if len(passos) == 2:
                inv = geo.compor(passos[::-1])
                st.caption(
                    "Com a ordem trocada: "
                    + ("o resultado é o mesmo." if inv == T else "o resultado é diferente.")
                )
