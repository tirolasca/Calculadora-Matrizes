"""Painel genérico de operações: escolhe a operação, edita as matrizes e mostra o resultado."""

from __future__ import annotations

import re

import streamlit as st

from ..services import calc_service as cs
from ..services import matrix_service as ms
from ..services import step_service as ss
from ..state import obter
from . import math_renderer as mr
from .matrix_editor import carregar_no_editor, editor_matriz

EXEMPLOS = {
    "A": [["2", "1", "-1"], ["-3", "-1", "2"], ["-2", "1", "2"]],
    "B": [["1", "0", "2"], ["0", "1", "-1"], ["3", "2", "1"]],
}


def _guardar(ex: cs.Execucao, chave: str, nome: str, valor) -> None:
    est = obter()
    try:
        est.memoria.salvar(nome, valor)
        est.registrar_uso(nome)
        st.toast(f"Resultado salvo como {nome}.", icon=":material/check:")
    except ValueError as e:
        st.toast(str(e), icon=":material/error:")


def _slug(rotulo: str) -> str:
    """Nome de arquivo seguro a partir do rótulo de um resultado."""
    return re.sub(r"[^A-Za-z0-9]+", "_", rotulo).strip("_").lower() or "matriz"


def _exportar(chave: str, matrizes: list[tuple[str, object]]) -> None:
    """Copiar (LaTeX) ou baixar (CSV e .tex) cada matriz do resultado."""
    with st.expander("Copiar ou exportar", icon=":material/ios_share:"):
        for idx, (rot, val) in enumerate(matrizes):
            latex = ss.latex_matriz(val)
            st.markdown(f"**{rot}**")
            st.code(latex, language="latex")  # o bloco já traz o botão de copiar
            c1, c2, _ = st.columns([1, 1, 2])
            base = _slug(rot)
            c1.download_button(
                "Baixar CSV",
                ms.matriz_para_csv(val),
                f"{base}.csv",
                "text/csv",
                key=f"{chave}:csv{idx}",
                icon=":material/table:",
            )
            c2.download_button(
                "Baixar LaTeX",
                latex + "\n",
                f"{base}.tex",
                "text/x-tex",
                key=f"{chave}:tex{idx}",
                icon=":material/code:",
            )


def painel(
    chave: str, grupos: tuple[str, ...], categoria: str, so_com_passos: bool = False
) -> None:
    est = obter()
    ops = cs.operacoes_do_grupo(*grupos)
    if so_com_passos:
        from ..services import step_service as _ss

        ops = [o for o in ops if _ss.suporta(o.nome)]
    nome = st.selectbox("Operação", [o.nome for o in ops], key=f"{chave}:op")
    op = cs.operacao_por_nome(nome)

    cols = st.columns(op.nmat) if op.nmat > 1 else [st.container()]
    mats = []
    for k, rot in enumerate("AB"[: op.nmat]):
        with cols[k]:
            mats.append(editor_matriz(f"{chave}:{rot}", f"Matriz {rot}", exemplo=EXEMPLOS[rot]))

    param = ""
    if op.param:
        dica = "ex.: 2, -1/2, 3.5 ou 2*pi" if op.param == "k" else "inteiro, ex.: 3 ou -2"
        param = st.text_input(f"Valor de {op.param}", value="2", key=f"{chave}:param", help=dica)
    metodo = None
    if nome == "Inversa":
        metodo = st.radio(
            "Método do passo a passo",
            ["gauss", "adjunta"],
            format_func=lambda x: {
                "gauss": "Gauss-Jordan [A | I]",
                "adjunta": "Adjunta / determinante",
            }[x],
            horizontal=True,
            key=f"{chave}:metodo",
        )

    chave_res = f"res:{chave}"
    if st.button(
        "Calcular",
        type="primary",
        key=f"{chave}:calc",
        icon=":material/calculate:",
        shortcut="Ctrl+Enter",
        help="Atalho: Ctrl+Enter",
    ):
        st.session_state.pop(chave_res, None)
        if any(m is None for m in mats):
            st.error("Corrija os elementos inválidos antes de calcular.")
        else:
            try:
                with st.spinner("Calculando…"):
                    ex = cs.executar(nome, mats, param, metodo=metodo)
            except ValueError as e:
                st.error(str(e), icon=":material/error:")
                est.historico.adicionar(
                    categoria, nome, dict(zip("AB", mats, strict=False)), texto=str(e), ok=False
                )
            else:
                est.historico.adicionar(
                    categoria, nome, ex.entradas, latex=ex.latex_principal, texto=ex.texto
                )
                st.session_state[chave_res] = ex

    atual: cs.Execucao | None = st.session_state.get(chave_res)
    if atual is None or atual.operacao.nome != nome:
        return
    st.divider()
    st.subheader("Resultado")
    mr.resultados(atual.resultado)
    matrizes = [(r, v) for r, v in atual.resultado if hasattr(v, "shape")]
    if matrizes:
        with st.expander("Guardar ou reutilizar o resultado", icon=":material/save:"):
            for idx, (rot, val) in enumerate(matrizes):
                c1, c2, c3 = st.columns([2, 1, 1])
                nm = c1.text_input(
                    f"Nome — {rot}", value=est.memoria.proximo_nome(), key=f"{chave}:sv{idx}"
                )
                c2.button(
                    "Guardar",
                    key=f"{chave}:g{idx}",
                    on_click=_guardar,
                    args=(atual, chave, nm, val),
                )
                c3.button(
                    "Usar como A",
                    key=f"{chave}:u{idx}",
                    on_click=carregar_no_editor,
                    args=(f"{chave}:A", val),
                )
    if matrizes:
        _exportar(chave, matrizes)
    if atual.solucao is not None and est.pref("mostrar_passos"):
        st.divider()
        st.subheader("Passo a passo")
        mr.solucao(atual.solucao, f"{chave}:sol")
    elif atual.aviso_passos:
        st.info(atual.aviso_passos)
