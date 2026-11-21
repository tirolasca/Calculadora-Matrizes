"""Tema visual: paleta efetiva, CSS dos componentes e cores dos gráficos.

Modos: ``sistema`` (segue o tema do Streamlit/navegador), ``claro`` e ``escuro``. O Streamlit
não permite trocar o tema oficial por usuário, então nos modos forçados aplicamos CSS na
sessão. A geração do CSS (``gerar_css``) é pura e testada sem navegador.
"""

from __future__ import annotations

from ..paleta import TEMAS
from .state import obter

FONTE = '"Inter", "Segoe UI", system-ui, -apple-system, "Helvetica Neue", Arial, sans-serif'
MONO = '"JetBrains Mono", "Cascadia Mono", Consolas, "SF Mono", Menlo, monospace'


def tema_do_sistema() -> str:
    """'claro' ou 'escuro', segundo o tema que o Streamlit está exibindo."""
    import streamlit as st

    try:
        return "escuro" if st.context.theme.type == "dark" else "claro"
    except Exception:
        return "claro"


def nome_efetivo(preferencia: str, sistema: str = "claro") -> str:
    return sistema if preferencia == "sistema" else preferencia


def paleta(preferencia: str | None = None) -> dict[str, str]:
    """Paleta usada pelos nossos componentes e gráficos agora."""
    if preferencia is None:
        preferencia = obter().pref("tema")
    sistema = tema_do_sistema() if preferencia == "sistema" else "claro"
    return TEMAS[nome_efetivo(preferencia, sistema)]


def estilo_grafico(p: dict[str, str]) -> dict[str, str]:
    """Cores para ``nucleo.figura_sistema`` e para os gráficos geométricos."""
    return {"fundo": p["texto_bg"], "texto": p["fg"], "grade": p["border"], "eixos": p["muted"]}


# Efeitos visuais que ficam sempre ativos (foco, hover, brackets do editor...). Só usam as
# variáveis --mx-* definidas em ``gerar_css``, então valem para os dois temas sem f-string.
# Atenção: nada de "}}" colado nem do seletor da barra lateral nativa (os testes conferem).
CSS_EFEITOS = """
::selection { background: color-mix(in srgb, var(--mx-accent) 30%, transparent); }
* { scrollbar-width: thin; scrollbar-color: color-mix(in srgb, var(--mx-accent) 45%, transparent) transparent; }
.stApp button:focus-visible, .stApp a:focus-visible, .stApp summary:focus-visible,
.stApp [role="tab"]:focus-visible { outline: 2px solid var(--mx-accent); outline-offset: 2px; border-radius: 8px; }

/* botões */
.stApp .stButton > button, .stApp .stDownloadButton > button, .stApp .stLinkButton > a {
  border-radius: 10px; font-weight: 600;
  transition: transform .15s ease, box-shadow .2s ease, border-color .2s ease, filter .2s ease;
}
.stApp .stButton > button:hover, .stApp .stDownloadButton > button:hover, .stApp .stLinkButton > a:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 18px -10px color-mix(in srgb, var(--mx-accent) 65%, transparent);
}
.stApp .stButton > button:active, .stApp .stDownloadButton > button:active { transform: scale(.97); box-shadow: none; }
/* botão primário: mesmo visual (índigo → violeta, texto branco) em qualquer tema e em formulários */
.stApp [data-testid^="stBaseButton-primary"] {
  background-color: #4f46e5; background-image: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: #fff; border-color: transparent;
}
.stApp [data-testid^="stBaseButton-primary"] *, .stApp [data-testid^="stBaseButton-primary"] p { color: #fff; }
.stApp [data-testid^="stBaseButton-primary"]:hover { filter: brightness(1.1); color: #fff; }

/* campos, expanders, métricas, abas, avisos e imagens */
.stApp [data-testid="stTextInputRootElement"], .stApp [data-testid="stNumberInputContainer"],
.stApp [data-testid="stTextAreaRootElement"], .stApp [data-testid="stSelectbox"] [role="group"],
.stApp [data-baseweb="select"] > div {
  border-radius: 10px; transition: border-color .2s ease, box-shadow .2s ease;
}
.stApp [data-testid="stTextInputRootElement"]:focus-within, .stApp [data-testid="stNumberInputContainer"]:focus-within,
.stApp [data-testid="stTextAreaRootElement"]:focus-within, .stApp [data-testid="stSelectbox"] [role="group"]:focus-within {
  border-color: var(--mx-accent); box-shadow: 0 0 0 3px color-mix(in srgb, var(--mx-accent) 22%, transparent);
}
.stApp [data-testid="stExpander"] { border-radius: 12px; transition: border-color .2s ease, box-shadow .25s ease; }
.stApp [data-testid="stExpander"]:hover {
  border-color: color-mix(in srgb, var(--mx-accent) 55%, var(--mx-border));
  box-shadow: 0 10px 24px -20px color-mix(in srgb, var(--mx-accent) 80%, transparent);
}
.stApp [data-testid="stExpander"] summary:hover { color: var(--mx-accent); }
.stApp [data-testid="stMetric"] { border-radius: 12px; transition: transform .2s ease, border-color .2s ease; }
.stApp [data-testid="stMetric"]:hover { transform: translateY(-2px); border-color: var(--mx-accent); }
.stApp [data-baseweb="tab"] { transition: color .2s ease, background-color .2s ease; }
.stApp [data-testid="stAlert"], .stApp .stAlert { border-radius: 12px; }
.stApp [data-testid="stImage"] img { border-radius: 12px; border: 1px solid var(--mx-border); }
.stApp [data-testid="stLatex"] { overflow-x: auto; }

/* título de página com barra de destaque */
.stApp h1 { position: relative; padding-bottom: .6rem; }
.stApp h1::after {
  content: ""; position: absolute; left: 0; bottom: 0; width: 64px; height: 4px; border-radius: 4px;
  background: linear-gradient(90deg, var(--mx-accent), color-mix(in srgb, var(--mx-accent) 40%, #ec4899));
}

/* cabeçalho */
.mx-hero { position: relative; overflow: hidden; box-shadow: 0 22px 40px -28px color-mix(in srgb, var(--mx-accent) 90%, transparent); }
.mx-hero::after { display: none; }
.mx-hero h1::after { display: none; }
.mx-hero::before {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background: radial-gradient(circle at 88% 15%, rgba(255, 255, 255, .20), transparent 45%);
}
.mx-hero-body { position: relative; z-index: 1; max-width: 68%; }
.mx-chips { display: flex; flex-wrap: wrap; gap: .45rem; margin-top: .95rem; }
.mx-chip {
  display: inline-flex; align-items: center; gap: .4rem; padding: .22rem .75rem; border-radius: 999px;
  font-size: .8rem; font-weight: 600; background: rgba(255, 255, 255, .14);
  border: 1px solid rgba(255, 255, 255, .30); color: inherit;
}
.mx-chip svg { width: 15px; height: 15px; }
.mx-hero-art {
  position: absolute; right: 1.7rem; top: 50%; width: 150px; height: 150px; margin-top: -75px;
  color: rgba(255, 255, 255, .95); pointer-events: none;
}

/* cartões e ícones */
.mx-card { transition: transform .2s ease, box-shadow .25s ease, border-color .2s ease; }
.mx-card-hover:hover {
  transform: translateY(-4px); border-color: var(--mx-accent);
  box-shadow: 0 16px 30px -20px color-mix(in srgb, var(--mx-accent) 75%, transparent);
}
.mx-card-head { display: flex; align-items: center; gap: .65rem; margin-bottom: .45rem; }
.mx-card-head h4 { margin: 0; }
.mx-ico {
  display: inline-flex; flex: none; align-items: center; justify-content: center; width: 38px; height: 38px;
  border-radius: 11px; color: var(--mx-accent); background: color-mix(in srgb, var(--mx-accent) 14%, transparent);
  transition: background-color .2s ease, color .2s ease, transform .25s ease;
}
.mx-ico svg { width: 21px; height: 21px; }
.stApp .mx-ico { color: var(--mx-accent); }
.mx-card-hover:hover .mx-ico { background: var(--mx-accent); transform: rotate(-6deg) scale(1.07); }
.stApp .mx-card-hover:hover .mx-ico { color: var(--mx-accent-fg); }
.mx-kpi .mx-ico { margin: 0 auto .4rem auto; }
@supports ((-webkit-background-clip: text) or (background-clip: text)) {
  .stApp .mx-kpi .v {
    background: linear-gradient(120deg, var(--mx-accent), color-mix(in srgb, var(--mx-accent) 55%, #ec4899));
    -webkit-background-clip: text; background-clip: text; color: transparent; -webkit-text-fill-color: transparent;
  }
}
.mx-badge { background: color-mix(in srgb, currentColor 12%, transparent); }

/* editor de matrizes: colchetes ao redor da grade */
[class*="st-key-mxgrid"] { position: relative; padding: .9rem 1.7rem; margin: .4rem 0 .7rem 0; }
[class*="st-key-mxgrid"]::before, [class*="st-key-mxgrid"]::after {
  content: ""; position: absolute; top: 0; bottom: 0; width: 14px; border: 3px solid var(--mx-accent);
  pointer-events: none; opacity: .85;
}
[class*="st-key-mxgrid"]::before { left: 0; border-right: none; border-radius: 7px 0 0 7px; }
[class*="st-key-mxgrid"]::after { right: 0; border-left: none; border-radius: 0 7px 7px 0; }
[class*="st-key-mxgrid"] input {
  text-align: center; font-weight: 600; font-variant-numeric: tabular-nums;
  font-family: ui-monospace, "JetBrains Mono", "Cascadia Mono", Consolas, monospace;
}

/* painel lateral */
.mx-side {
  border: 1px solid var(--mx-border); border-radius: 14px; padding: .85rem .95rem; margin-top: .8rem;
  background: var(--mx-surface);
}
.mx-side-t { display: flex; align-items: center; gap: .55rem; font-weight: 700; color: var(--mx-fg); }
.mx-side-t .mx-ico { width: 32px; height: 32px; border-radius: 9px; }
.mx-side-t .mx-ico svg { width: 18px; height: 18px; }
.mx-side-s { color: var(--mx-muted); font-size: .82rem; margin-top: .35rem; }
.mx-side a { color: var(--mx-accent); font-weight: 600; text-decoration: none; }
.mx-side a:hover { text-decoration: underline; }

@media (max-width: 768px) {
  .mx-hero-art { display: none; }
  .mx-hero-body { max-width: 100%; }
  [class*="st-key-mxgrid"] { padding: .7rem 1.2rem; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .001ms !important; animation-iteration-count: 1 !important;
    transition-duration: .001ms !important; scroll-behavior: auto !important;
  }
}
"""

# Animações (desligáveis em Configurações). Os quadros "de partida" usam fill-mode ``backwards``:
# terminada a animação o elemento volta ao estilo normal, então nada fica invisível se ela falhar.
CSS_ANIMACOES = """
@keyframes mx-subir { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
@keyframes mx-surgir { 0% { opacity: 0; transform: scale(.9); } 65% { transform: scale(1.04); } 100% { opacity: 1; transform: none; } }
@keyframes mx-draw { from { stroke-dasharray: 1; stroke-dashoffset: 1; } to { stroke-dasharray: 1; stroke-dashoffset: 0; } }
@keyframes mx-draw-hover { from { stroke-dasharray: 1; stroke-dashoffset: 1; } to { stroke-dasharray: 1; stroke-dashoffset: 0; } }
@keyframes mx-gradiente { 0%, 100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
@keyframes mx-flutuar { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
@keyframes mx-pulso { 0%, 100% { box-shadow: 0 0 0 0 color-mix(in srgb, currentColor 40%, transparent); } 50% { box-shadow: 0 0 0 7px transparent; } }
@keyframes mx-barra { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes mx-matriz {
  0%, 10% { transform: matrix(1, 0, 0, 1, 0, 0); }
  28%, 40% { transform: matrix(1, 0, .85, 1, 0, 0); }
  58%, 70% { transform: matrix(.7071, .7071, -.7071, .7071, 0, 0); }
  88%, 100% { transform: matrix(1, 0, 0, 1, 0, 0); }
}

/* entrada da página: cada bloco sobe e aparece em sequência */
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > * {
  animation: mx-subir .5s cubic-bezier(.2, .7, .2, 1) backwards;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > *:nth-child(2) { animation-delay: 50ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > *:nth-child(3) { animation-delay: 100ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > *:nth-child(4) { animation-delay: 150ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > *:nth-child(5) { animation-delay: 200ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > *:nth-child(6) { animation-delay: 250ms; }
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > *:nth-child(n+7) { animation-delay: 300ms; }

.stApp h1::after { transform-origin: left center; animation: mx-barra .7s .2s cubic-bezier(.2, .7, .2, 1) backwards; }
.mx-hero { background-size: 200% 200%; animation: mx-gradiente 18s ease-in-out infinite; }
.mx-hero-art { animation: mx-flutuar 7s ease-in-out infinite; }
.mx-hero-art .mx-art-forma { transform-origin: 75px 75px; animation: mx-matriz 10s ease-in-out infinite; }
.mx-card[style*="--i"] { animation: mx-surgir .55s cubic-bezier(.2, .7, .2, 1) backwards; animation-delay: calc(var(--i, 0) * 70ms + 120ms); }
.mx-kpi .v { animation: mx-surgir .6s cubic-bezier(.2, .7, .2, 1) backwards; animation-delay: calc(var(--i, 0) * 80ms + 250ms); }
.mx-ico svg *, .mx-chip svg *, .mx-side-t svg * { animation: mx-draw 1s ease-out backwards; animation-delay: calc(var(--i, 0) * 70ms + 300ms); }
.mx-card-hover:hover .mx-ico svg * { animation: mx-draw-hover .7s ease-out; }
.mx-badge { animation: mx-surgir .45s ease backwards, mx-pulso 2.4s ease 1s 2; }
.stApp [data-testid="stAlert"], .stApp .stAlert { animation: mx-subir .4s ease backwards; }
"""

FONTES_IMPORT = (
    "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700"
    "&family=JetBrains+Mono:wght@400;500;600&display=swap');\n"
)


def gerar_css(p: dict[str, str], forcar: bool, animacoes: bool = True) -> str:
    """CSS dos componentes (.mx-*) e, se ``forcar``, das cores nativas do Streamlit.

    ``animacoes=False`` omite as animações (os efeitos de hover e foco continuam).
    """
    base = f"""
:root {{
  --mx-bg:{p["bg"]}; --mx-fg:{p["fg"]}; --mx-muted:{p["muted"]}; --mx-border:{p["border"]};
  --mx-campo:{p["campo"]}; --mx-surface:{p["texto_bg"]}; --mx-accent:{p["accent"]};
  --mx-accent-fg:{p["accent_fg"]}; --mx-ok:{p["ok"]}; --mx-aviso:{p["aviso"]};
  --mx-perigo:{p["perigo"]}; --mx-selecao:{p["selecao"]}; --mx-botao:{p["botao"]};
}}
html, body, .stApp {{ font-family:{FONTE}; }}
.block-container {{ padding-top:4.2rem; max-width:1200px; }}
code, pre, .mx-mono {{ font-family:{MONO}; }}
h1, h2, h3 {{ letter-spacing:-0.01em; }}

.mx-hero {{
  background:linear-gradient(120deg,{p["header_bg"]} 0%,{p["accent"]} 140%);
  color:{p["header_fg"]}; border-radius:16px; padding:1.6rem 1.8rem; margin-bottom:1.1rem;
}}
.mx-hero h1 {{ margin:0 0 .25rem 0; padding:0; font-size:1.9rem; color:{p["header_fg"]}; }}
.mx-hero p {{ margin:0; opacity:.92; font-size:1.02rem; color:{p["header_fg"]}; }}
.mx-card {{
  background:var(--mx-surface); border:1px solid var(--mx-border); border-radius:14px;
  padding:1rem 1.15rem; margin-bottom:.8rem; color:var(--mx-fg);
}}
.mx-card h4 {{ margin:0 0 .35rem 0; font-size:1.02rem; color:var(--mx-accent); }}
.mx-card p {{ margin:.15rem 0; color:var(--mx-fg); }}
.mx-muted {{ color:var(--mx-muted); font-size:.9rem; }}
.mx-kpi {{ text-align:center; }}
.mx-kpi .v {{ font-size:1.7rem; font-weight:700; color:var(--mx-accent); }}
.mx-kpi .r {{ font-size:.85rem; color:var(--mx-muted); }}
.mx-badge {{
  display:inline-block; padding:.12rem .6rem; border-radius:999px; font-size:.82rem;
  font-weight:600; border:1px solid currentColor; margin-right:.3rem;
}}
.mx-ok {{ color:var(--mx-ok); }} .mx-aviso {{ color:var(--mx-aviso); }} .mx-perigo {{ color:var(--mx-perigo); }}
.mx-step {{
  border-left:4px solid var(--mx-accent); background:var(--mx-surface);
  border-radius:0 12px 12px 0; padding:.7rem 1rem; margin:.5rem 0; color:var(--mx-fg);
}}
.mx-step .t {{ font-weight:700; color:var(--mx-accent); margin-bottom:.2rem; }}
table.mx-table {{ border-collapse:collapse; width:100%; margin:.3rem 0 .8rem 0; }}
table.mx-table th, table.mx-table td {{
  border:1px solid var(--mx-border); padding:.4rem .7rem; text-align:left; color:var(--mx-fg);
}}
table.mx-table th {{ background:var(--mx-surface); color:var(--mx-accent); }}
@media (max-width: 768px) {{
  .block-container {{ padding:1rem .8rem; }}
  .mx-hero {{ padding:1.1rem 1.1rem; }} .mx-hero h1 {{ font-size:1.5rem; }}
}}
"""
    partes = [FONTES_IMPORT, base]
    if forcar:
        partes.append(_css_cores_nativas(p))
    partes.append(CSS_EFEITOS)  # depois das cores nativas: precisa vencer regras de mesma força
    if animacoes:
        partes.append(CSS_ANIMACOES)
    return "".join(partes)


def _css_cores_nativas(p: dict[str, str]) -> str:
    """Cores do Streamlit nos modos claro/escuro forçados (o modo 'sistema' não precisa)."""
    return f"""
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{ background:{p["bg"]}; color:{p["fg"]}; }}
[data-testid="stHeader"] {{ background:{p["bg"]}; }}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div {{ background:{p["texto_bg"]}; }}
.stApp p, .stApp li, .stApp label, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp h5, .stApp h6, .stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stWidgetLabel"] {{ color:{p["fg"]}; }}
.stApp .mx-hero, .stApp .mx-hero * {{ color:{p["header_fg"]}; }}
.stApp .mx-card h4, .stApp .mx-step .t, .stApp .mx-kpi .v, .stApp table.mx-table th {{ color:{p["accent"]}; }}
.stApp .mx-muted, .stApp .mx-kpi .r {{ color:{p["muted"]}; }}
.stApp .mx-ok {{ color:{p["ok"]}; }} .stApp .mx-aviso {{ color:{p["aviso"]}; }} .stApp .mx-perigo {{ color:{p["perigo"]}; }}
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="select"] > div, [data-baseweb="textarea"] {{
  background:{p["campo"]}; border-color:{p["border"]}; color:{p["fg"]};
}}
.stApp input, .stApp textarea {{ color:{p["fg"]}; -webkit-text-fill-color:{p["fg"]}; background:{p["campo"]}; }}
[data-baseweb="popover"] [role="listbox"], [data-baseweb="menu"] {{ background:{p["campo"]}; color:{p["fg"]}; }}
[data-baseweb="popover"] li {{ color:{p["fg"]}; }}
.stButton > button, .stDownloadButton > button {{
  background:{p["botao"]}; color:{p["fg"]}; border:1px solid {p["border"]};
}}
.stButton > button:hover, .stDownloadButton > button:hover {{ border-color:{p["accent"]}; color:{p["accent"]}; }}
[data-testid="stExpander"] {{ border-color:{p["border"]}; background:{p["texto_bg"]}; }}
[data-testid="stExpander"] summary {{ color:{p["fg"]}; background:transparent; }}
[data-baseweb="tab-list"] {{ background:transparent; }}
[data-baseweb="tab"] {{ color:{p["muted"]}; }}
[data-baseweb="tab"][aria-selected="true"] {{ color:{p["accent"]}; }}
[data-testid="stMetric"] {{ background:{p["texto_bg"]}; border:1px solid {p["border"]}; border-radius:12px; padding:.6rem .9rem; }}
hr {{ border-color:{p["border"]}; }}
.katex, .katex * {{ color:{p["fg"]}; }}
""" + _css_widgets(p)


def _css_widgets(p: dict[str, str]) -> str:
    """Widgets do Streamlit 1.6x (react-aria, sem ``data-baseweb``) nos temas forçados.

    Foi aqui que apareceram os defeitos do modo escuro: o contêiner externo de cada campo ficava
    claro ao redor do ``input`` escuro, e alertas, uploader, rádios e botões ficavam com fundo
    branco. Cada regra mira o ``data-testid`` do contêiner, não classes geradas (que mudam).
    """
    return f"""
/* campos de texto, número, área de texto e seletor: o contêiner é quem tem fundo e borda */
[data-testid="stTextInputRootElement"], [data-testid="stNumberInputContainer"],
[data-testid="stTextAreaRootElement"], [data-testid="stSelectbox"] [role="group"] {{
  background:{p["campo"]}; border:1px solid {p["border"]}; color:{p["fg"]};
}}
[data-testid="stTextInputRootElement"] input, [data-testid="stNumberInputContainer"] input,
[data-testid="stTextAreaRootElement"] textarea, [data-testid="stSelectbox"] input {{
  background:transparent; color:{p["fg"]}; -webkit-text-fill-color:{p["fg"]};
}}
[data-testid="stTextInputRootElement"] input::placeholder, [data-testid="stTextAreaRootElement"] textarea::placeholder,
[data-testid="stSelectbox"] input::placeholder {{ color:{p["muted"]}; -webkit-text-fill-color:{p["muted"]}; opacity:1; }}
[data-testid="stNumberInputContainer"] button {{ background:{p["botao"]}; color:{p["fg"]}; border-color:{p["border"]}; }}
[data-testid="stNumberInputContainer"] button:hover:not(:disabled) {{ background:{p["botao_hover"]}; color:{p["accent"]}; }}
[data-testid="stNumberInputContainer"] button:disabled {{ opacity:.45; }}
[data-testid="stSelectbox"] [role="group"] svg {{ color:{p["muted"]}; fill:{p["muted"]}; }}

/* botões secundários fora de .stButton (uploader, formulários, popover, barra dos gráficos) */
[data-testid^="stBaseButton-secondary"], [data-testid="stPopoverButton"], [data-testid="stElementToolbarButtonContainer"] {{
  background:{p["botao"]}; color:{p["fg"]}; border:1px solid {p["border"]};
}}
[data-testid^="stBaseButton-secondary"]:hover, [data-testid="stPopoverButton"]:hover {{ border-color:{p["accent"]}; color:{p["accent"]}; }}
[data-testid^="stBaseButton-secondary"] *, [data-testid="stPopoverButton"] *, [data-testid="stElementToolbarButtonContainer"] * {{ color:inherit; }}

/* rádio: círculo vazio com borda; o marcado mantém o ponto branco sobre o acento */
[data-testid="stRadioOption"]:not([data-selected="true"]) > div > div:first-child {{
  background:{p["campo"]}; border:1px solid {p["muted"]};
}}
/* caixa de seleção (o interruptor, role=switch, já vem escuro) */
[data-testid="stCheckbox"]:not([data-selected="true"]):not(:has(input[role="switch"])) label > div:first-of-type {{
  background:{p["campo"]}; border:1px solid {p["muted"]};
}}
[data-testid="stCheckbox"][data-selected="true"]:not(:has(input[role="switch"])) label > div:first-of-type {{
  background:{p["accent"]}; border-color:{p["accent"]};
}}

/* alertas: fundo da superfície, filete lateral na cor do tipo e texto legível */
[data-testid="stAlertContainer"] {{
  background:{p["texto_bg"]}; color:{p["fg"]}; border:1px solid {p["border"]}; border-left-width:4px;
}}
[data-testid="stAlertContainer"] * {{ color:{p["fg"]}; }}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) {{
  border-left-color:{p["ok"]}; background:color-mix(in srgb, {p["ok"]} 12%, {p["texto_bg"]});
}}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) {{
  border-left-color:{p["aviso"]}; background:color-mix(in srgb, {p["aviso"]} 12%, {p["texto_bg"]});
}}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) {{
  border-left-color:{p["perigo"]}; background:color-mix(in srgb, {p["perigo"]} 12%, {p["texto_bg"]});
}}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) {{
  border-left-color:{p["accent"]}; background:color-mix(in srgb, {p["accent"]} 12%, {p["texto_bg"]});
}}

/* envio de arquivos */
[data-testid="stFileUploaderDropzone"] {{ background:{p["campo"]}; border:1px dashed {p["border"]}; }}
[data-testid="stFileUploaderDropzone"] small, [data-testid="stFileUploaderDropzoneInstructions"] * {{ color:{p["muted"]}; }}

/* ícone de ajuda (?): o traço do SVG vem fixo em cinza escuro */
[data-testid="stTooltipIcon"] button {{ color:{p["muted"]}; opacity:1; }}
[data-testid="stTooltipIcon"] svg, [data-testid="stTooltipIcon"] svg * {{ color:{p["muted"]} !important; stroke:{p["muted"]} !important; }}

/* lista aberta do seletor: renderizada num portal fora de .stApp, então não herda nada do tema */
[data-testid="stSelectboxVirtualDropdown"] {{
  background:{p["campo"]}; color:{p["fg"]}; border:1px solid {p["border"]}; border-radius:10px;
}}
[data-testid="stSelectboxVirtualDropdown"] [role="option"], [data-testid="stSelectboxVirtualDropdown"] [role="option"] * {{
  color:{p["fg"]};
}}
[data-testid="stSelectboxVirtualDropdown"] [role="option"][aria-selected="true"],
[data-testid="stSelectboxVirtualDropdown"] [role="option"][data-focused="true"],
[data-testid="stSelectboxVirtualDropdown"] [role="option"]:hover {{ background:{p["selecao"]}; }}
"""


def aplicar() -> dict[str, str]:
    """Injeta o CSS do tema escolhido e devolve a paleta efetiva."""
    import streamlit as st

    est = obter()
    pref = est.pref("tema")
    p = paleta(pref)
    css = gerar_css(p, pref != "sistema", bool(est.pref("animacoes")))
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    return p
