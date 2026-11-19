"""Ponto de entrada do Streamlit: configuração da página, tema, navegação.

Execute com ``streamlit run streamlit_app.py`` (raiz do repositório) ou
``calculadora-matrizes-web``.
"""

from __future__ import annotations


def executar() -> None:
    import streamlit as st

    from matrizes.web import paginas, theme
    from matrizes.web.config import NOME_APP, VERSAO
    from matrizes.web.state import obter

    st.set_page_config(
        page_title=NOME_APP,
        page_icon=":material/grid_on:",
        layout="wide",
        initial_sidebar_state="auto",
    )
    estado = obter()
    theme.aplicar()
    navegacao = st.navigation(paginas.construir(), position="sidebar", expanded=True)
    with st.sidebar:
        st.caption(f"v{VERSAO} · {len(estado.memoria)} matriz(es) salva(s)")
    navegacao.run()


if __name__ == "__main__":
    executar()
