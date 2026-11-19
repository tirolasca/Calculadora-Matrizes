"""Laboratório → Comparação de matrizes e de propriedades algébricas."""

from collections.abc import Callable

import streamlit as st

from ..components import math_renderer as mr
from ..components import ui
from ..components.matrix_editor import editor_matriz
from ..components.tabelas import tabela
from ..services import chart_service as cht
from ..services import matrix_service as ms
from ..theme import estilo_grafico, paleta

PROPRIEDADES = {
    "comutatividade": ("Comutatividade  AB = BA", 2),
    "associatividade": ("Associatividade  (AB)C = A(BC)", 3),
    "distributividade": ("Distributividade  A(B+C) = AB + AC", 3),
    "transposta_produto": ("Transposta do produto  (AB)ᵀ = BᵀAᵀ", 2),
    "det_produto": ("Determinante do produto  det(AB) = det(A)·det(B)", 2),
    "inversa": ("Inversa  A·A⁻¹ = I", 1),
}
FUNCOES: dict[str, Callable[..., ms.Verificacao]] = {
    "comutatividade": ms.verificar_comutatividade,
    "associatividade": ms.verificar_associatividade,
    "distributividade": ms.verificar_distributividade,
    "transposta_produto": ms.verificar_transposta_produto,
    "det_produto": ms.verificar_det_produto,
    "inversa": ms.verificar_inversa,
}


def renderizar() -> None:
    ui.cabecalho(
        "Comparação de matrizes", "Compare duas matrizes ou teste propriedades algébricas."
    )
    aba1, aba2 = st.tabs(["Comparar A e B", "Propriedades algébricas"])
    estilo = estilo_grafico(paleta())

    with aba1:
        c1, c2 = st.columns(2)
        with c1:
            A = editor_matriz(
                "cmp:A", "Matriz A", exemplo=[["1", "2", "3"], ["4", "5", "6"], ["7", "8", "10"]]
            )
        with c2:
            B = editor_matriz(
                "cmp:B", "Matriz B", exemplo=[["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]
            )
        if A is None or B is None:
            st.stop()
        r = ms.comparar_matrizes(A, B)
        if not r.mesma_dimensao:
            st.warning(f"Dimensões diferentes: A é {A.rows}×{A.cols} e B é {B.rows}×{B.cols}.")
            if r.uma_e_transposta_da_outra:
                st.info("Mas B é a transposta de A.")
        else:
            linhas = [
                ["Iguais?", "sim" if r.iguais else "não"],
                ["Posições diferentes", str(len(r.posicoes_diferentes))],
                ["A = k·B?", f"sim, k = {r.multiplo}" if r.multiplo is not None else "não"],
                ["B é a transposta de A?", "sim" if r.uma_e_transposta_da_outra else "não"],
            ]
            if r.maior_diferenca is not None:
                linhas.append(["Maior diferença absoluta", f"{r.maior_diferenca:g}"])
            tabela(["Critério", "Resultado"], linhas)
            mr.matriz(r.diferenca, "A − B")
            try:
                st.pyplot(cht.comparar_mapas(A, B, estilo), clear_figure=True)
            except ValueError as e:
                st.caption(f"Gráfico indisponível: {e}")
        for rot, M in (("A", A), ("B", B)):
            try:
                s = ms.estatisticas(M)
            except ValueError:
                continue
            st.caption(
                f"{rot}: mín {s.minimo:g} · máx {s.maximo:g} · média {s.media:.4g} · "
                f"soma {s.soma:g} · zeros {s.zeros}/{s.total} · ‖{rot}‖F = {s.norma_frobenius:.4g}"
            )

    with aba2:
        chave = st.selectbox(
            "Propriedade",
            list(PROPRIEDADES),
            format_func=lambda k: PROPRIEDADES[k][0],
            key="prop:sel",
        )
        n = PROPRIEDADES[chave][1]
        cols = st.columns(n)
        mats = []
        for k in range(n):
            with cols[k]:
                mats.append(
                    editor_matriz(
                        f"alg:{'ABC'[k]}",
                        f"Matriz {'ABC'[k]}",
                        exemplo=[["1", "2"], ["3", "4"]]
                        if k == 0
                        else [["0", "1"], ["1", "0"]]
                        if k == 1
                        else [["2", "0"], ["1", "3"]],
                    )
                )
        if st.button("Verificar", type="primary", key="prop:run"):
            if any(m is None for m in mats):
                st.error("Corrija os elementos inválidos.")
            else:
                try:
                    st.session_state["prop:res"] = (chave, FUNCOES[chave](*mats))
                except ValueError as e:
                    st.session_state.pop("prop:res", None)
                    st.error(str(e), icon=":material/error:")
        guard = st.session_state.get("prop:res")
        if guard and guard[0] == chave:
            v = guard[1]
            st.latex(v.enunciado)
            c1, c2 = st.columns(2)
            for col, rot, val in ((c1, v.rotulo_esq, v.esquerda), (c2, v.rotulo_dir, v.direita)):
                with col:
                    if hasattr(val, "shape"):
                        mr.matriz(val, rot)
                    else:
                        st.latex(f"{rot} = {ms_latex(val)}")
            (st.success if v.igual else st.warning)(
                ("✓ Os dois lados são iguais. " if v.igual else "✗ Os lados diferem. ")
                + v.comentario
            )


def ms_latex(x) -> str:
    import sympy as sp

    return sp.latex(x)
