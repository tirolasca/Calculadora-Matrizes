"""Calculadora → Operações."""

from ..components import ui
from ..components.operation_panel import painel


def renderizar() -> None:
    ui.cabecalho("Operações", "Soma, produto, potência, transposta, inversa, adjunta, cofatores…")
    painel("op", ("Operações",), "Operação")
