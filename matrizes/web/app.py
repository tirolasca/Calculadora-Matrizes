"""Ponto de entrada do Streamlit: configuração da página, tema, navegação.

Execute com ``streamlit run streamlit_app.py`` (raiz do repositório) ou
``calculadora-matrizes-web``.
"""

from __future__ import annotations

CHAVE_MODO_ESCURO = "mx:escuro"


def _alternar_tema(estado) -> None:
    """Interruptor de modo escuro na barra lateral, sempre em sincronia com as Configurações."""
    import streamlit as st

    from matrizes.web import theme

    atual = theme.nome_efetivo(estado.pref("tema"), theme.tema_do_sistema())
    st.session_state[CHAVE_MODO_ESCURO] = atual == "escuro"

    def trocar() -> None:
        escuro = st.session_state[CHAVE_MODO_ESCURO]
        estado.preferencias["tema"] = "escuro" if escuro else "claro"

    st.toggle(
        ":material/dark_mode: Modo escuro",
        key=CHAVE_MODO_ESCURO,
        on_change=trocar,
        help="Alterna entre os temas claro e escuro. “Automático” fica em Configurações.",
    )


def executar() -> None:
    import streamlit as st

    from matrizes.web import paginas, theme
    from matrizes.web.components import ui
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
        _alternar_tema(estado)
        ui.painel_lateral(VERSAO, len(estado.memoria))
    navegacao.run()


if __name__ == "__main__":
    executar()
