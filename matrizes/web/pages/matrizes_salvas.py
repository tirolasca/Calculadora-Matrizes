"""Ferramentas → Matrizes salvas (criar, renomear, duplicar, excluir, reutilizar, exportar)."""

import streamlit as st

from ..components import math_renderer as mr
from ..components import ui
from ..components.matrix_editor import carregar_no_editor
from ..services import matrix_service as ms
from ..state import obter


def renderizar() -> None:
    est = obter()
    mem = est.memoria
    ui.cabecalho("Matrizes salvas", "Memória da sessão: salve, renomeie, duplique e reutilize.")
    if not mem.nomes():
        st.info("Nenhuma matriz salva ainda. Use “Ferramentas desta matriz → Salvar” nos editores.")
    for nome in mem.nomes():
        M = mem.obter(nome)
        with st.expander(f"{nome} — {M.rows}×{M.cols}", expanded=False):
            mr.matriz(M, nome)
            c1, c2, c3 = st.columns(3)
            novo = c1.text_input("Renomear para", value=nome, key=f"ren:{nome}")

            def renomear(a=nome, b=novo):
                try:
                    est.memoria.renomear(a, b)
                    est.limpar_recentes_inexistentes()
                except ValueError as e:
                    st.toast(str(e), icon=":material/error:")

            c1.button("Renomear", key=f"rb:{nome}", on_click=renomear)

            def duplicar(n=nome):
                est.memoria.duplicar(n)

            def excluir(n=nome):
                est.memoria.excluir(n)
                est.limpar_recentes_inexistentes()

            c2.button("Duplicar", key=f"dup:{nome}", on_click=duplicar)
            c3.button("Excluir", key=f"del:{nome}", on_click=excluir)
            destino = st.selectbox(
                "Enviar para o editor",
                ["op:A", "op:B", "prop:A", "sis"],
                key=f"dest:{nome}",
                format_func=lambda d: {
                    "op:A": "Operações — A",
                    "op:B": "Operações — B",
                    "prop:A": "Propriedades — A",
                    "sis": "Sistemas — [A|b]",
                }[d],
            )
            st.button("Enviar", key=f"env:{nome}", on_click=carregar_no_editor, args=(destino, M))

    st.subheader("Criar matriz")
    with st.form("criar"):
        c1, c2, c3 = st.columns(3)
        pre = c1.selectbox("Tipo", ms.nomes_predefinidas())
        m = c2.number_input("Linhas", 1, 8, 3)
        n = c3.number_input("Colunas", 1, 8, 3)
        nome = st.text_input("Nome", value=mem.proximo_nome())
        if st.form_submit_button("Criar e salvar"):
            try:
                mem.salvar(nome, ms.predefinida(pre, int(m), int(n), len(mem) + 1))
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    st.subheader("Exportar / importar")
    st.download_button(
        "Baixar matrizes (JSON)", mem.exportar_json(), "matrizes.json", "application/json"
    )
    arq = st.file_uploader("Importar JSON", type="json")
    if arq is not None and st.button("Importar arquivo"):
        try:
            qtd = mem.importar_json(arq.getvalue().decode("utf-8"))
            st.success(f"{qtd} matriz(es) importada(s).")
        except (ValueError, UnicodeDecodeError) as e:
            st.error(str(e))
