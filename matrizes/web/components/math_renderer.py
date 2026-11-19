"""Exibição de matemática: matrizes, resultados do núcleo e passo a passo (LaTeX)."""

from __future__ import annotations

import streamlit as st
import sympy as sp

from ..services import matrix_service as ms
from ..services import step_service as ss
from ..state import obter


def latex_de_valor(v) -> str | None:
    """LaTeX de um valor do núcleo (Matrix ou texto de expressão); None se for só texto."""
    if isinstance(v, sp.MatrixBase):
        return ss.latex_matriz(v)
    if isinstance(v, sp.Basic):
        return sp.latex(v)
    if isinstance(v, str):
        try:
            return sp.latex(ms.expressao(v))
        except ValueError:
            return None
    return None


def matriz(M: sp.Matrix, rotulo: str = "") -> None:
    st.latex((rotulo + " = " if rotulo else "") + ss.latex_matriz(M))


def aproximacao(valor, casas: int | None = None) -> str | None:
    """Texto decimal para um valor exato não inteiro; None se não se aplica."""
    casas = casas or int(obter().pref("casas"))
    try:
        v = ms.expressao(valor) if isinstance(valor, str) else sp.sympify(valor)
        if v.free_symbols or v.is_Integer or not v.is_number:
            return None
        return str(sp.N(v, casas + 2).round(casas)) if v.is_real else str(sp.N(v, casas + 2))
    except Exception:
        return None


def resultados(res: list[tuple[str, object]]) -> None:
    """Mostra a lista (rótulo, valor) devolvida por uma operação do núcleo."""
    est = obter()
    casas = int(est.pref("casas"))
    for rotulo, valor in res:
        tex = latex_de_valor(valor)
        if isinstance(valor, sp.MatrixBase):
            st.markdown(f"**{rotulo}**")
            st.latex(tex)
            if est.pref("aproximacao") and any(
                not x.is_Integer and x.is_number and not x.free_symbols for x in valor
            ):
                with st.expander("Valores decimais"):
                    st.latex(
                        ss.latex_matriz(valor.applyfunc(lambda x: sp.N(x, casas + 2).round(casas)))
                    )
        elif tex and rotulo.rstrip().endswith("="):
            extra = aproximacao(valor) if est.pref("aproximacao") else None
            st.latex(f"\\text{{{rotulo.rstrip(' =')}}} = {tex}")
            if extra:
                st.caption(f"≈ {extra}")
        else:
            st.markdown(f"**{rotulo}** {valor}" if isinstance(valor, str) else f"**{rotulo}**")


def solucao(sol: ss.Solucao, chave: str, expandir: bool = True) -> None:
    """Passo a passo em 8 partes: identificação, entradas, fórmula, substituição,
    desenvolvimento, passos intermediários, resultado e interpretação."""
    st.markdown(f"#### {sol.operacao}")
    st.caption(sol.identificacao)
    if sol.aviso:
        st.info(sol.aviso)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("**Dados de entrada**")
        for e in sol.entradas:
            st.latex(e)
    with c2:
        st.markdown("**Fórmula / método**")
        st.latex(sol.formula)
    n = len(sol.passos)
    atual = 1
    if n > 1:
        atual = st.slider(
            "Passo em destaque", 1, n, 1, key=f"{chave}:passo", help="Percorra as etapas uma a uma."
        )
    todos = st.toggle("Expandir todos os passos", value=False, key=f"{chave}:todos")
    for i, p in enumerate(sol.passos, 1):
        ativo = i == atual
        marca = "▶ " if ativo and n > 1 else ""
        with st.expander(
            f"{marca}Passo {i} de {n} — {p.titulo}", expanded=expandir and (ativo or todos)
        ):
            if p.texto:
                st.write(p.texto)
            if p.latex:
                st.latex(p.latex)
    st.markdown("**Resultado final**")
    st.latex(sol.resultado_latex)
    st.success(sol.interpretacao, icon=":material/lightbulb:")
