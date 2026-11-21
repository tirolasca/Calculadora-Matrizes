"""Ícones SVG embutidos (traço, estilo "outline"), sem fontes nem arquivos externos.

Cada ícone é uma lista de formas SVG num quadro 24×24, desenhada com ``currentColor``: herdam a
cor do texto e funcionam nos temas claro e escuro. As formas recebem ``pathLength="1"`` para que a
animação de "desenhar o traço" (``mx-draw`` em ``theme.py``) funcione igual em todas.

Módulo puro (não importa o Streamlit) para ser testado sem navegador.
"""

from __future__ import annotations

import re
from html import escape

ICONES: dict[str, str] = {
    # navegação e marca
    "matriz": '<path d="M8 3H5v18h3"/><path d="M16 3h3v18h-3"/><path d="M10 8h.01M14 8h.01M10 12h.01M14 12h.01M10 16h.01M14 16h.01"/>',
    "casa": '<path d="M3 11 12 3l9 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
    "calculadora": '<rect x="5" y="2.5" width="14" height="19" rx="2"/><path d="M8.5 6.5h7"/><path d="M8.5 11h.01M12 11h.01M15.5 11h.01M8.5 15h.01M12 15h.01M15.5 15h.01M8.5 18.5h.01M12 18.5h.01"/>',
    "sistema": '<path d="M8 3H7a2 2 0 0 0-2 2v4a2 2 0 0 1-2 2 2 2 0 0 1 2 2v4a2 2 0 0 0 2 2h1"/><path d="M16 21h1a2 2 0 0 0 2-2v-4a2 2 0 0 1 2-2 2 2 0 0 1-2-2V5a2 2 0 0 0-2-2h-1"/><path d="M9 9h6M9 15h6"/>',
    "laboratorio": '<path d="M9 3h6"/><path d="M10 3v6L4.6 18.4A1.6 1.6 0 0 0 6 21h12a1.6 1.6 0 0 0 1.4-2.6L14 9V3"/><path d="M7.5 15h9"/>',
    "transformar": '<path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 4v5h-5"/>',
    "comparar": '<path d="M4 8h16M16 4l4 4-4 4"/><path d="M20 16H4M8 12l-4 4 4 4"/>',
    "geometria": '<path d="M3 3v18h18"/><path d="M7 17 17 7"/><path d="M12 7h5v5"/>',
    "livro": '<path d="M4 5a2 2 0 0 1 2-2h14v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5"/><path d="M9 8h7"/>',
    "passos": '<path d="M9 6h12M9 12h12M9 18h12"/><path d="M3.5 6h.01M3.5 12h.01M3.5 18h.01"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="m8 12.5 2.8 2.8L16 9.5"/>',
    "lapis": '<path d="M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>',
    "historico": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "salvar": '<path d="M5 3h11l3 3v15H5z"/><path d="M8 3v5h7V3"/><path d="M8 21v-7h8v7"/>',
    "ajustes": '<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
    # destaques
    "raio": '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    "lampada": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-4 10.5c.8.8 1 1.5 1 2.5h6c0-1 .2-1.7 1-2.5A6 6 0 0 0 12 3z"/>',
    "codigo": '<path d="m8 8-4 4 4 4M16 8l4 4-4 4"/><path d="m13.5 5-3 14"/>',
    "baixar": '<path d="M12 3v12M7 10l5 5 5-5"/><path d="M4 21h16"/>',
    "seta": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "alvo": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "escudo": '<path d="M12 3 4 6v6c0 4.5 3.2 7.8 8 9 4.8-1.2 8-4.5 8-9V6z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
}

_FORMA_RE = re.compile(r"<(path|rect|circle)\s")


def nomes() -> list[str]:
    return list(ICONES)


def svg(nome: str, tamanho: int = 24, classe: str = "") -> str:
    """HTML de um ícone. Decorativo (``aria-hidden``): o texto ao lado já diz o que é."""
    if nome not in ICONES:
        raise KeyError(f"ícone desconhecido: {nome!r}")
    corpo = _FORMA_RE.sub(r'<\1 pathLength="1" ', ICONES[nome])
    cls = f' class="{escape(classe, quote=True)}"' if classe else ""
    return (
        f'<svg{cls} xmlns="http://www.w3.org/2000/svg" width="{int(tamanho)}" height="{int(tamanho)}" '
        'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{corpo}</svg>'
    )


# Arte do cabeçalho: o quadrado unitário e os vetores i e j sendo transformados por uma matriz
# (a animação CSS ``mx-matriz`` alterna entre identidade, cisalhamento e rotação).
ARTE_HERO = (
    '<svg class="mx-hero-art" viewBox="0 0 150 150" xmlns="http://www.w3.org/2000/svg" '
    'aria-hidden="true">'
    '<g class="mx-art-grade" stroke="currentColor" stroke-width="1" opacity=".22">'
    '<path d="M15 75h120M15 35h120M15 115h120M35 15v120M75 15v120M115 15v120"/></g>'
    '<g class="mx-art-eixos" stroke="currentColor" stroke-width="1.6" opacity=".55">'
    '<path d="M10 75h130M75 140V10"/></g>'
    '<g class="mx-art-forma">'
    '<rect x="75" y="35" width="40" height="40" rx="2" fill="currentColor" fill-opacity=".16" '
    'stroke="currentColor" stroke-width="2"/>'
    '<path d="M75 75h40" stroke="#fbbf24" stroke-width="3.2" stroke-linecap="round"/>'
    '<path d="M75 75V35" stroke="#34d399" stroke-width="3.2" stroke-linecap="round"/>'
    '<circle cx="75" cy="75" r="3.4" fill="currentColor"/></g>'
    "</svg>"
)
