"""Editor de matrizes reutilizável: dimensões dinâmicas, expressões simbólicas, validação,
predefinidas, duplicar, salvar/carregar e rascunho que sobrevive à troca de página."""

from __future__ import annotations

import streamlit as st
import sympy as sp

from ..config import MAX_DIM
from ..services import matrix_service as ms
from ..state import obter


def _versao(chave: str) -> int:
    return st.session_state.get(f"_v:{chave}", 0)


def _grade(
    chave: str, dims: tuple[int, int], exemplo: list[list[str]] | None = None
) -> list[list[str]]:
    g = obter().rascunho(chave)
    if g:
        return g
    if exemplo:
        return [list(l) for l in exemplo]
    return [["0"] * dims[1] for _ in range(dims[0])]


def carregar_no_editor(chave: str, M: sp.Matrix) -> None:
    """Coloca M no editor `chave` (use em callbacks de botão)."""
    obter().definir_rascunho(chave, ms.matriz_para_texto(M))
    st.session_state[f"_v:{chave}"] = _versao(chave) + 1
    for k in (f"{chave}:m", f"{chave}:n"):
        st.session_state.pop(k, None)


def _redimensionar(g: list[list[str]], m: int, n: int) -> list[list[str]]:
    return [
        [(g[i][j] if i < len(g) and j < len(g[0]) else "0") for j in range(n)] for i in range(m)
    ]


def editor_matriz(
    chave: str,
    titulo: str,
    dims: tuple[int, int] = (2, 2),
    *,
    quadrada: bool = False,
    ferramentas: bool = True,
    exemplo: list[list[str]] | None = None,
) -> sp.Matrix | None:
    """Desenha o editor e devolve a matriz digitada (ou None se houver erro, já exibido)."""
    est = obter()
    g = _grade(chave, dims, exemplo)
    ver = _versao(chave)
    st.markdown(f"**{titulo}**")

    c1, c2, _ = st.columns([1, 1, 2])
    m = c1.number_input("Linhas", 1, MAX_DIM, len(g), key=f"{chave}:m", step=1)
    if quadrada:
        n = m
        c2.number_input("Colunas", 1, MAX_DIM, int(m), key=f"{chave}:n:q", step=1, disabled=True)
    else:
        n = c2.number_input("Colunas", 1, MAX_DIM, len(g[0]), key=f"{chave}:n", step=1)
    m, n = int(m), int(n)
    g = _redimensionar(g, m, n)

    nova = []
    for i in range(m):
        cols = st.columns(n)
        linha = []
        for j in range(n):
            linha.append(
                cols[j].text_input(
                    f"{titulo} [{i + 1},{j + 1}]",
                    value=g[i][j],
                    key=f"{chave}:{ver}:{i}:{j}",
                    label_visibility="collapsed",
                    placeholder=f"a{i + 1}{j + 1}",
                )
            )
        nova.append(linha)
    est.definir_rascunho(chave, nova)

    if ferramentas:
        _ferramentas(chave, titulo, m, n, quadrada)

    try:
        M = ms.matriz_de_texto(nova)
    except ms.EntradaInvalida as e:
        for erro in e.erros:
            st.error(erro, icon=":material/error:")
        return None
    if M.free_symbols:
        st.caption("Matriz simbólica: " + ", ".join(sorted(str(s) for s in M.free_symbols)))
    return M


def _ferramentas(chave: str, titulo: str, m: int, n: int, quadrada: bool) -> None:
    est = obter()
    with st.expander("Ferramentas desta matriz", icon=":material/construction:"):
        a, b = st.columns(2)
        pre = a.selectbox("Predefinida", ms.nomes_predefinidas(), key=f"{chave}:pre")

        def aplicar_pre():
            semente = st.session_state.get("_semente", 0) + 1
            st.session_state["_semente"] = semente
            carregar_no_editor(chave, ms.predefinida(pre, m, n, semente))

        a.button("Aplicar", key=f"{chave}:apl", on_click=aplicar_pre)

        salvas = est.memoria.nomes()
        sel = b.selectbox(
            "Carregar salva", salvas or ["(nenhuma)"], key=f"{chave}:sel", disabled=not salvas
        )

        def carregar():
            carregar_no_editor(chave, est.memoria.obter(sel))
            est.registrar_uso(sel)

        b.button("Carregar", key=f"{chave}:car", on_click=carregar, disabled=not salvas)

        def limpar():
            carregar_no_editor(chave, sp.zeros(m, n))

        nome = st.text_input(
            "Nome para salvar", value=est.memoria.proximo_nome(), key=f"{chave}:nome"
        )
        c, d, e = st.columns(3)
        c.button("Limpar (zeros)", key=f"{chave}:lim", on_click=limpar)

        def salvar():
            try:
                M = ms.matriz_de_texto(est.rascunho(chave) or [])
                est.memoria.salvar(nome, M)
                est.registrar_uso(nome)
                st.toast(f"Matriz {nome} salva.", icon=":material/check:")
            except (ms.EntradaInvalida, ValueError) as err:
                st.toast(str(err), icon=":material/error:")

        d.button("Salvar", key=f"{chave}:sal", on_click=salvar)

        def duplicar():
            try:
                M = ms.matriz_de_texto(est.rascunho(chave) or [])
                novo = est.memoria.salvar(est.memoria.proximo_nome(), M)
                st.toast(f"Cópia salva como {novo}.", icon=":material/content_copy:")
            except (ms.EntradaInvalida, ValueError) as err:
                st.toast(str(err), icon=":material/error:")

        e.button("Duplicar", key=f"{chave}:dup", on_click=duplicar)
