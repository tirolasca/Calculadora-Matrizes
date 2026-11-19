"""Laboratório → Experimentação: modifique uma matriz e veja o que muda, de verdade."""

import streamlit as st

from ..components import math_renderer as mr
from ..components import ui
from ..components.matrix_editor import carregar_no_editor, editor_matriz
from ..components.tabelas import tabela
from ..services import lab_service as lab
from ..services import matrix_service as ms
from ..state import obter


def _comparativo(res: lab.Resultado) -> None:
    c1, c2 = st.columns(2)
    with c1:
        mr.matriz(res.antes, "A")
    with c2:
        mr.matriz(res.depois, "A′")
    ta, td = ms.tabela_propriedades(res.props_antes), ms.tabela_propriedades(res.props_depois)
    tabela(
        ["Propriedade", "Antes (A)", "Depois (A′)", ""],
        [[k, ta[k], td.get(k, "—"), "mudou" if ta[k] != td.get(k) else "igual"] for k in ta],
    )
    for obs in res.observacoes:
        st.markdown(f"**Medido:** {obs}")
    if res.mudancas:
        st.markdown("**Por que mudou?**")
        for prop, antes, depois, expl in res.mudancas:
            st.markdown(f"- **{prop}:** {antes} → {depois}. {expl}")
    else:
        st.success("Nenhuma das propriedades analisadas mudou.")


def renderizar() -> None:
    est = obter()
    ui.cabecalho(
        "Experimentação",
        "Altere uma matriz e compare as propriedades antes e depois — tudo calculado na hora.",
    )
    aba1, aba2, aba3 = st.tabs(
        ["Explorar propriedades", "Experimentos guiados", "Meus experimentos"]
    )

    with aba1:
        A = editor_matriz(
            "lab:A", "Matriz A", exemplo=[["1", "2", "3"], ["4", "5", "6"], ["7", "8", "10"]]
        )
        tipos = list(lab.TIPOS)
        tipo = str(
            st.selectbox("Modificação", tipos, format_func=lambda t: lab.TIPOS[t], key="lab:tipo")
        )
        c = st.columns(3)
        i = int(c[0].number_input("Linha i", 1, 8, 1, key="lab:i"))
        j = int(c[1].number_input("Linha/coluna j", 1, 8, 2, key="lab:j"))
        kt = c[2].text_input("Valor k", "2", key="lab:k")
        if A is None:
            st.stop()
        try:
            k = ms.expressao(kt)
            B = lab.modificar(A, tipo, i, j, k)
        except ValueError as e:
            st.error(str(e))
        else:
            st.caption(f"Operação aplicada: **{lab.descricao(tipo, i, j, k)}**")
            _comparativo(lab.comparar(A, B))
            c1, c2 = st.columns(2)
            c1.button("Usar A′ como novo A", on_click=carregar_no_editor, args=("lab:A", B))
            with c2.popover("Salvar experimento"):
                nome = st.text_input(
                    "Nome", f"Experimento {len(est.experimentos) + 1}", key="lab:nome"
                )
                nota = st.text_area("Anotação (opcional)", key="lab:nota")
                if st.button("Salvar", key="lab:salvar"):
                    try:
                        est.salvar_experimento(nome, {"A": A, "A′": B}, nota)
                        st.toast("Experimento salvo.", icon=":material/check:")
                    except ValueError as e:
                        st.error(str(e))

    with aba2:
        exp = st.selectbox(
            "Experimento", lab.EXPERIMENTOS, format_func=lambda x: x.titulo, key="lab:exp"
        )
        st.markdown(f"**Objetivo:** {exp.objetivo}")
        st.markdown(f"**Pergunta:** {exp.pergunta}")
        st.caption(f"Operação: {lab.descricao(exp.tipo, exp.i, exp.j, exp.k)}")
        if st.button("Executar experimento", type="primary", key="lab:run"):
            st.session_state["lab:resultado"] = (exp.id, lab.executar_experimento(exp))
        guard = st.session_state.get("lab:resultado")
        if guard and guard[0] == exp.id:
            _comparativo(guard[1])
            st.info(exp.conclusao, icon=":material/lightbulb:")
            st.button(
                "Carregar esta matriz no explorador",
                on_click=carregar_no_editor,
                args=("lab:A", guard[1].antes),
            )

    with aba3:
        if not est.experimentos:
            st.info("Nenhum experimento salvo ainda. Salve um na aba “Explorar propriedades”.")
        for nome, ex in list(est.experimentos.items()):
            with st.expander(f"{nome} — {ex['criado']}"):
                if ex["nota"]:
                    st.write(ex["nota"])
                cols = st.columns(len(ex["matrizes"]))
                for col, (rot, M) in zip(cols, ex["matrizes"].items(), strict=True):
                    with col:
                        mr.matriz(M, rot)
                a, b = st.columns(2)

                def restaurar(n=nome):
                    carregar_no_editor("lab:A", est.restaurar_experimento(n)["A"])

                a.button("Restaurar no explorador", key=f"rest:{nome}", on_click=restaurar)
                b.button(
                    "Excluir", key=f"exc:{nome}", on_click=est.excluir_experimento, args=(nome,)
                )
