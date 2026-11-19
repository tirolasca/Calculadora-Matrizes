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


def gerar_css(p: dict[str, str], forcar: bool) -> str:
    """CSS dos componentes (.mx-*) e, se ``forcar``, das cores nativas do Streamlit."""
    base = f"""
:root {{
  --mx-bg:{p["bg"]}; --mx-fg:{p["fg"]}; --mx-muted:{p["muted"]}; --mx-border:{p["border"]};
  --mx-campo:{p["campo"]}; --mx-surface:{p["texto_bg"]}; --mx-accent:{p["accent"]};
  --mx-accent-fg:{p["accent_fg"]}; --mx-ok:{p["ok"]}; --mx-aviso:{p["aviso"]};
  --mx-perigo:{p["perigo"]}; --mx-selecao:{p["selecao"]}; --mx-botao:{p["botao"]};
}}
html, body, .stApp {{ font-family:{FONTE}; }}
.block-container {{ padding-top:2.2rem; max-width:1200px; }}
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
    if not forcar:
        return base
    return (
        base
        + f"""
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
.stButton > button[kind="primary"] {{ background:{p["accent"]}; color:{p["accent_fg"]}; border-color:{p["accent"]}; }}
.stButton > button[kind="primary"] * {{ color:{p["accent_fg"]}; }}
[data-testid="stExpander"] {{ border-color:{p["border"]}; background:{p["texto_bg"]}; }}
[data-testid="stExpander"] summary {{ color:{p["fg"]}; }}
[data-baseweb="tab-list"] {{ background:transparent; }}
[data-baseweb="tab"] {{ color:{p["muted"]}; }}
[data-baseweb="tab"][aria-selected="true"] {{ color:{p["accent"]}; }}
[data-testid="stMetric"] {{ background:{p["texto_bg"]}; border:1px solid {p["border"]}; border-radius:12px; padding:.6rem .9rem; }}
.stAlert {{ background:{p["texto_bg"]}; color:{p["fg"]}; }}
hr {{ border-color:{p["border"]}; }}
.katex, .katex * {{ color:{p["fg"]}; }}
"""
    )


def aplicar() -> dict[str, str]:
    """Injeta o CSS do tema escolhido e devolve a paleta efetiva."""
    import streamlit as st

    pref = obter().pref("tema")
    p = paleta(pref)
    st.markdown(f"<style>{gerar_css(p, pref != 'sistema')}</style>", unsafe_allow_html=True)
    return p
