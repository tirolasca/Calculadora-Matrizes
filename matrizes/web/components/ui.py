"""Blocos visuais reutilizáveis (cabeçalho, cartões, indicadores, selos, painel lateral)."""

from __future__ import annotations

from collections.abc import Sequence
from html import escape

import streamlit as st

from ..config import NOME_APP, REPO_URL, SUBTITULO
from . import icones


def hero(
    titulo: str = NOME_APP,
    subtitulo: str = SUBTITULO,
    chips: Sequence[tuple[str, str]] = (),
    arte: bool = True,
) -> None:
    """Cabeçalho em destaque. ``chips`` é uma lista de (ícone, texto) exibida sob o subtítulo."""
    selos = "".join(
        f'<span class="mx-chip" style="--i:{k}">{icones.svg(ic, 15)}{escape(txt)}</span>'
        for k, (ic, txt) in enumerate(chips)
    )
    bloco_chips = f'<div class="mx-chips">{selos}</div>' if selos else ""
    st.markdown(
        '<div class="mx-hero">'
        f'<div class="mx-hero-body"><h1>{escape(titulo)}</h1><p>{escape(subtitulo)}</p>'
        f"{bloco_chips}</div>"
        f"{icones.ARTE_HERO if arte else ''}</div>",
        unsafe_allow_html=True,
    )


def cabecalho(titulo: str, subtitulo: str = "") -> None:
    st.title(titulo)
    if subtitulo:
        st.caption(subtitulo)


def cartao(titulo: str, corpo: str, icone: str | None = None, indice: int | None = None) -> None:
    """Cartão com ícone opcional. ``indice`` escalona a animação de entrada e liga o efeito de
    elevação ao passar o mouse."""
    ico = f'<span class="mx-ico">{icones.svg(icone, 21)}</span>' if icone else ""
    classe = "mx-card" + (" mx-card-hover" if indice is not None else "")
    estilo = f' style="--i:{int(indice)}"' if indice is not None else ""
    st.markdown(
        f'<div class="{classe}"{estilo}><div class="mx-card-head">{ico}<h4>{escape(titulo)}</h4></div>'
        f"<p>{escape(corpo)}</p></div>",
        unsafe_allow_html=True,
    )


def kpi(valor: str, rotulo: str, icone: str | None = None, indice: int = 0) -> None:
    ico = f'<span class="mx-ico">{icones.svg(icone, 21)}</span>' if icone else ""
    st.markdown(
        f'<div class="mx-card mx-kpi" style="--i:{int(indice)}">{ico}<div class="v">{escape(valor)}</div>'
        f'<div class="r">{escape(rotulo)}</div></div>',
        unsafe_allow_html=True,
    )


def selo(texto: str, tom: str = "ok") -> str:
    """HTML de um selo; tom: ok | aviso | perigo."""
    return f'<span class="mx-badge mx-{tom}">{escape(texto)}</span>'


def painel_lateral(versao: str, n_matrizes: int) -> None:
    """Cartão no rodapé da barra lateral: marca, versão, memória e link do projeto."""
    st.markdown(
        '<div class="mx-side">'
        f'<div class="mx-side-t"><span class="mx-ico">{icones.svg("matriz", 18)}</span>{escape(NOME_APP)}</div>'
        f'<div class="mx-side-s">v{escape(versao)} · {n_matrizes} matriz(es) salva(s)</div>'
        f'<div class="mx-side-s"><a href="{escape(REPO_URL, quote=True)}" target="_blank" '
        'rel="noopener noreferrer">Código no GitHub</a> · licença MIT</div>'
        "</div>",
        unsafe_allow_html=True,
    )
