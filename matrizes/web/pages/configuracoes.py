"""Ferramentas → Configurações e dados da sessão."""

import streamlit as st

from ..components import ui
from ..config import PREFERENCIAS_PADRAO, ROTULOS_TEMA, TEMAS_OPCOES
from ..state import obter


def renderizar() -> None:
    est = obter()
    p = est.preferencias
    ui.cabecalho("Configurações", "Preferências e dados da sua sessão.")
    tema = st.radio(
        "Tema",
        TEMAS_OPCOES,
        index=TEMAS_OPCOES.index(p["tema"]),
        format_func=ROTULOS_TEMA.get,
        horizontal=True,
        help="“Automático” segue o tema do navegador/Streamlit.",
    )
    if tema != p["tema"]:
        p["tema"] = tema
        st.rerun()  # reaplica o CSS do tema já nesta interação
    p["aproximacao"] = st.toggle(
        "Mostrar aproximação decimal de resultados exatos", p["aproximacao"]
    )
    p["casas"] = st.slider("Casas decimais", 1, 10, p["casas"])
    p["mostrar_passos"] = st.toggle(
        "Mostrar o passo a passo junto do resultado", p["mostrar_passos"]
    )
    p["grade_geometria"] = st.toggle(
        "Mostrar a malha nas visualizações geométricas", p["grade_geometria"]
    )
    if st.button("Restaurar padrões"):
        est.preferencias = dict(PREFERENCIAS_PADRAO)
        st.rerun()

    st.subheader("Sessão")
    st.caption("Tudo fica na memória desta sessão. Exporte para guardar e importe para retomar.")
    st.download_button(
        "Exportar sessão (JSON)", est.exportar(), "sessao-matrizes.json", "application/json"
    )
    arq = st.file_uploader("Importar sessão", type="json")
    substituir = st.checkbox("Substituir dados atuais")
    if arq is not None and st.button("Importar"):
        try:
            r = est.importar(arq.getvalue().decode("utf-8"), substituir=substituir)
            st.success(
                f"{r['matrizes']} matriz(es) e {r['experimentos']} experimento(s) importados."
            )
        except (ValueError, UnicodeDecodeError) as e:
            st.error(str(e))
