"""Aprendizado → Passo a passo de qualquer operação, com as suas matrizes."""

from ..components import ui
from ..components.operation_panel import painel


def renderizar() -> None:
    ui.cabecalho(
        "Passo a passo",
        "Escolha uma operação, digite suas matrizes e acompanhe cada etapa em LaTeX. "
        "Cada passo é conferido contra o núcleo de cálculo.",
    )
    painel("pap", ("Operações", "Propriedades"), "Passo a passo", so_com_passos=True)
