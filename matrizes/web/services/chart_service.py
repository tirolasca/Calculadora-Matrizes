"""Gráficos matplotlib (objetos Figure, sem pyplot) para matrizes e comparações."""

from __future__ import annotations

from typing import Any

import numpy as np
from matplotlib.figure import Figure

from . import matrix_service as ms


def _estilo(e: dict[str, str] | None) -> dict[str, str]:
    base = {"fundo": "#ffffff", "texto": "#1f2937", "grade": "#d1d5db", "eixos": "#6b7280"}
    return {**base, **(e or {})}


def _array(M) -> np.ndarray:
    return np.array(ms.valores_numericos(M), dtype=float).reshape(M.rows, M.cols)


def _desenhar(
    ax, V: np.ndarray, titulo: str, e: dict[str, str], vmax: float, casas: int = 2
) -> Any:
    im = ax.imshow(V, cmap="coolwarm", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_title(titulo, color=e["texto"], fontsize=10, fontweight="bold")
    ax.set_xticks(
        range(V.shape[1]), [str(j + 1) for j in range(V.shape[1])], color=e["texto"], fontsize=8
    )
    ax.set_yticks(
        range(V.shape[0]), [str(i + 1) for i in range(V.shape[0])], color=e["texto"], fontsize=8
    )
    ax.tick_params(length=0)
    for sp_ in ax.spines.values():
        sp_.set_visible(False)
    if V.size <= 64:
        for i in range(V.shape[0]):
            for j in range(V.shape[1]):
                cor = "white" if abs(V[i, j]) > 0.6 * vmax else "#111827"
                ax.text(
                    j, i, f"{V[i, j]:.{casas}g}", ha="center", va="center", color=cor, fontsize=9
                )
    return im


def mapa_calor(M, titulo: str = "Matriz", estilo: dict[str, str] | None = None) -> Figure:
    """Mapa de calor dos elementos (azul = negativo, vermelho = positivo)."""
    e = _estilo(estilo)
    V = _array(M)
    vmax = max(float(np.abs(V).max()), 1e-9)
    fig = Figure(figsize=(4.6, 3.6), layout="constrained", facecolor=e["fundo"])
    ax = fig.add_subplot(111, facecolor=e["fundo"])
    im = _desenhar(ax, V, titulo, e, vmax)
    cb = fig.colorbar(im, ax=ax, fraction=0.046)
    cb.ax.tick_params(colors=e["texto"], labelsize=8)
    return fig


def comparar_mapas(A, B, estilo: dict[str, str] | None = None) -> Figure:
    """A, B e A − B lado a lado (mesma escala de cor). Exige mesma dimensão."""
    e = _estilo(estilo)
    VA, VB = _array(A), _array(B)
    if VA.shape != VB.shape:
        raise ValueError("As matrizes precisam ter a mesma dimensão.")
    vmax = max(float(np.abs(VA).max()), float(np.abs(VB).max()), float(np.abs(VA - VB).max()), 1e-9)
    fig = Figure(figsize=(10, 3.4), layout="constrained", facecolor=e["fundo"])
    for k, (V, t) in enumerate([(VA, "A"), (VB, "B"), (VA - VB, "A − B")]):
        ax = fig.add_subplot(1, 3, k + 1, facecolor=e["fundo"])
        _desenhar(ax, V, t, e, vmax)
    return fig


def barras_elementos(M, titulo: str = "Elementos", estilo: dict[str, str] | None = None) -> Figure:
    """Barras dos elementos em ordem de leitura (linha a linha)."""
    e = _estilo(estilo)
    v = ms.valores_numericos(M)
    fig = Figure(figsize=(6, 3), layout="constrained", facecolor=e["fundo"])
    ax = fig.add_subplot(111, facecolor=e["fundo"])
    ax.bar(range(1, len(v) + 1), v, color=["#4f46e5" if x >= 0 else "#dc2626" for x in v])
    ax.axhline(0, color=e["eixos"], lw=0.8)
    ax.set_title(titulo, color=e["texto"], fontsize=10, fontweight="bold")
    ax.set_xlabel("posição (linha a linha)", color=e["texto"], fontsize=8)
    ax.tick_params(colors=e["texto"], labelsize=8)
    ax.grid(axis="y", color=e["grade"], lw=0.6)
    for s in ax.spines.values():
        s.set_color(e["grade"])
    return fig
