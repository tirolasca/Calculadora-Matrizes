"""Calculadora → Propriedades."""

from ..components import ui
from ..components.operation_panel import painel


def renderizar() -> None:
    ui.cabecalho(
        "Propriedades e decomposições",
        "Determinante, posto, traço, RREF, autovalores, LU, QR, Cholesky, diagonalização…",
    )
    painel("prop", ("Propriedades",), "Propriedade")
