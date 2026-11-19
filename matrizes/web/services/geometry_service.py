"""Geometria de transformações lineares em 2D (só cálculo e figuras matplotlib)."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import sympy as sp
from matplotlib.figure import Figure

FORMAS: dict[str, list[tuple[float, float]]] = {
    "Quadrado unitário": [(0, 0), (1, 0), (1, 1), (0, 1)],
    "Triângulo": [(0, 0), (2, 0), (1, 2)],
    "Letra F": [
        (0, 0),
        (0.5, 0),
        (0.5, 1),
        (1.3, 1),
        (1.3, 1.4),
        (0.5, 1.4),
        (0.5, 2),
        (1.6, 2),
        (1.6, 2.5),
        (0, 2.5),
    ],
    "Retângulo 2×1": [(0, 0), (2, 0), (2, 1), (0, 1)],
}


def _estilo(e):
    base = {"fundo": "#ffffff", "texto": "#1f2937", "grade": "#d1d5db", "eixos": "#6b7280"}
    return {**base, **(e or {})}


# ---------------------------- matrizes de transformação ----------------------------
def rotacao(graus: float) -> sp.Matrix:
    """Rotação anti-horária. Ângulos notáveis ficam exatos."""
    t = sp.nsimplify(graus) * sp.pi / 180
    return sp.Matrix([[sp.cos(t), -sp.sin(t)], [sp.sin(t), sp.cos(t)]]).applyfunc(sp.simplify)


REFLEXOES = {
    "eixo x": sp.Matrix([[1, 0], [0, -1]]),
    "eixo y": sp.Matrix([[-1, 0], [0, 1]]),
    "reta y = x": sp.Matrix([[0, 1], [1, 0]]),
    "reta y = −x": sp.Matrix([[0, -1], [-1, 0]]),
}


def reflexao(eixo: str) -> sp.Matrix:
    return REFLEXOES[eixo]


def escala(sx, sy) -> sp.Matrix:
    return sp.Matrix([[sx, 0], [0, sy]])


def cisalhamento(kx=0, ky=0) -> sp.Matrix:
    """kx: x ← x + kx·y (horizontal); ky: y ← y + ky·x (vertical)."""
    return sp.Matrix([[1, kx], [ky, 1]])


def compor(ms_: list[sp.Matrix]) -> sp.Matrix:
    """Aplica na ordem da lista: compor([A, B]) = B·A (primeiro A, depois B)."""
    R = sp.eye(2)
    for M in ms_:
        R = M * R
    return R


# ---------------------------- determinante e área ----------------------------
@dataclass
class InfoDet:
    det: sp.Expr
    fator_area: sp.Expr
    orientacao: str  # "preservada" | "invertida" | "colapsa"
    texto: str


def info_determinante(M: sp.Matrix) -> InfoDet:
    d = sp.simplify(M.det())
    if d == 0:
        return InfoDet(
            d,
            sp.Integer(0),
            "colapsa",
            "det = 0: o plano é achatado sobre uma reta ou um ponto; a área vira 0 e a transformação não tem inversa.",
        )
    ori = "invertida" if d < 0 else "preservada"
    txt = f"As áreas são multiplicadas por |det| = {sp.Abs(d)}."
    txt += (
        " Como det < 0, a orientação é invertida (reflexão)."
        if d < 0
        else " Como det > 0, a orientação é preservada."
    )
    return InfoDet(d, sp.Abs(d), ori, txt)


def area_poligono(pts) -> float:
    """Fórmula do cadarço (valor absoluto)."""
    n = len(pts)
    s = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    return abs(s) / 2


def aplicar(M: sp.Matrix, pts) -> list[tuple[float, float]]:
    m = np.array(M.evalf(), dtype=float)
    return [tuple(m @ np.array(p, dtype=float)) for p in pts]


# ---------------------------- figuras ----------------------------
def _base(lim: float, e, titulo: str):
    fig = Figure(figsize=(5.2, 5.2), layout="constrained", facecolor=e["fundo"])
    ax = fig.add_subplot(111, facecolor=e["fundo"])
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axhline(0, color=e["eixos"], lw=0.9)
    ax.axvline(0, color=e["eixos"], lw=0.9)
    ax.set_title(titulo, color=e["texto"], fontsize=10, fontweight="bold")
    ax.tick_params(colors=e["texto"], labelsize=8)
    for s in ax.spines.values():
        s.set_color(e["grade"])
    return fig, ax


def _limite(*conjuntos, minimo=3.0) -> float:
    m = max((abs(c) for pts in conjuntos for p in pts for c in p), default=1)
    return max(minimo, math.ceil(m * 1.25))


def figura_transformacao(M, forma="Quadrado unitário", estilo=None, grade=True) -> Figure:
    e = _estilo(estilo)
    pts = FORMAS[forma]
    novo = aplicar(M, pts)
    base_t = aplicar(M, [(1, 0), (0, 1)])
    lim = _limite(pts, novo, base_t)
    info = info_determinante(M)
    fig, ax = _base(
        lim, e, f"det = {sp.nsimplify(info.det)}  →  área × {sp.nsimplify(info.fator_area)}"
    )
    if grade:
        ax.grid(color=e["grade"], lw=0.5)
        mm = np.array(M.evalf(), dtype=float)
        for c in range(-int(lim), int(lim) + 1):
            for p, q in (((c, -lim), (c, lim)), ((-lim, c), (lim, c))):
                a, b = mm @ np.array(p, float), mm @ np.array(q, float)
                ax.plot([a[0], b[0]], [a[1], b[1]], color="#4f46e5", lw=0.35, alpha=0.45)
    xs0, ys0 = [p[0] for p in pts], [p[1] for p in pts]
    ax.fill(xs0, ys0, color="#94a3b8", alpha=0.45, label="original")
    cor = "#dc2626" if info.orientacao == "invertida" else "#4f46e5"
    xs1, ys1 = zip(*novo, strict=True)
    ax.fill(xs1, ys1, color=cor, alpha=0.5, label="transformada")
    for v, nome, cv in (((1, 0), "T(e₁)", "#059669"), ((0, 1), "T(e₂)", "#d97706")):
        w = aplicar(M, [v])[0]
        ax.annotate("", xy=w, xytext=(0, 0), arrowprops={"arrowstyle": "->", "color": cv, "lw": 2})
        ax.text(w[0], w[1], " " + nome, color=cv, fontsize=9)
    leg = ax.legend(fontsize=8, facecolor=e["fundo"], edgecolor=e["grade"], loc="upper left")
    for t in leg.get_texts():
        t.set_color(e["texto"])
    return fig


# ---------------------------- vetores, span, independência ----------------------------
@dataclass
class AnaliseVetores:
    independentes: bool
    posto: int
    span: str  # "origem" | "reta" | "plano"
    base: bool
    texto: str


def analisar_vetores(vs: list[tuple]) -> AnaliseVetores:
    """Vetores de R² (colunas de M)."""
    M = sp.Matrix([[v[0] for v in vs], [v[1] for v in vs]])
    r = M.rank()
    span = {0: "origem", 1: "reta", 2: "plano"}[r]
    indep = r == len(vs)
    base = indep and len(vs) == 2
    if len(vs) == 2:
        d = M.det()
        txt = f"det[v₁ v₂] = {d}. " + (
            "≠ 0: os vetores são independentes, geram todo o plano e formam uma base de R²."
            if d != 0
            else "= 0: são dependentes (colineares); geram no máximo uma reta."
        )
    else:
        txt = f"Há {len(vs)} vetores em R² e posto {r}: " + (
            "independentes."
            if indep
            else "dependentes (em R² no máximo 2 podem ser independentes)."
        )
    return AnaliseVetores(indep, r, span, base, txt)


def figura_vetores(vs: list[tuple], estilo=None) -> Figure:
    e = _estilo(estilo)
    lim = _limite(vs, minimo=3.0)
    an = analisar_vetores(vs)
    fig, ax = _base(
        lim, e, f"Span: {an.span}  ·  {'independentes' if an.independentes else 'dependentes'}"
    )
    ax.grid(color=e["grade"], lw=0.5)
    cores = ["#4f46e5", "#059669", "#d97706", "#dc2626"]
    if an.span == "plano":
        ax.set_facecolor("#4f46e51a")
    elif an.span == "reta":
        v = next(v for v in vs if any(c != 0 for c in v))
        n = math.hypot(float(v[0]), float(v[1]))
        ax.plot(
            [-lim * float(v[0]) / n, lim * float(v[0]) / n],
            [-lim * float(v[1]) / n, lim * float(v[1]) / n],
            color="#4f46e5",
            lw=6,
            alpha=0.25,
        )
    for k, v in enumerate(vs):
        ax.annotate(
            "",
            xy=(float(v[0]), float(v[1])),
            xytext=(0, 0),
            arrowprops={"arrowstyle": "->", "color": cores[k % 4], "lw": 2.2},
        )
        ax.text(float(v[0]), float(v[1]), f" v{k + 1}", color=cores[k % 4], fontsize=10)
    if len(vs) == 2 and an.independentes:
        a = [float(c) for c in vs[0]]
        b = [float(c) for c in vs[1]]
        ax.fill(
            [0, a[0], a[0] + b[0], b[0]], [0, a[1], a[1] + b[1], b[1]], color="#94a3b8", alpha=0.35
        )
    return fig


# ---------------------------- autovetores ----------------------------
@dataclass
class Autodirecao:
    valor: sp.Expr
    vetor: sp.Matrix


@dataclass
class AnaliseAutovetores:
    reais: list[Autodirecao]
    complexos: bool
    texto: str


def analisar_autovetores(M: sp.Matrix) -> AnaliseAutovetores:
    if M.shape != (2, 2):
        raise ValueError("Use uma matriz 2×2.")
    vals = M.eigenvals()
    complexos = any(not sp.im(sp.N(v)) == 0 and abs(sp.im(sp.N(v))) > 1e-12 for v in vals)
    if complexos:
        return AnaliseAutovetores(
            [],
            True,
            "Os autovalores são complexos: nenhuma reta real é mantida pela transformação "
            "(ela gira os vetores, possivelmente também esticando-os).",
        )
    reais = [Autodirecao(l, v) for l, _, vs in M.eigenvects() for v in vs]
    if not reais:
        return AnaliseAutovetores([], False, "Sem autovetores reais.")
    if len(reais) < 2 and len(vals) == 1:
        txt = "Há uma única direção própria (matriz não diagonalizável)."
    else:
        txt = "Os autovetores indicam as direções que a transformação apenas estica ou inverte."
    return AnaliseAutovetores(reais, False, txt)


def figura_autovetores(M, estilo=None) -> Figure:
    e = _estilo(estilo)
    an = analisar_autovetores(M)
    t = np.linspace(0, 2 * math.pi, 200)
    circ = np.array([np.cos(t), np.sin(t)])
    img = np.array(M.evalf(), dtype=float) @ circ
    lim = max(3.0, math.ceil(float(np.abs(img).max()) * 1.2))
    fig, ax = _base(
        lim,
        e,
        "Círculo unitário e sua imagem" + (" (autovalores complexos)" if an.complexos else ""),
    )
    ax.grid(color=e["grade"], lw=0.5)
    ax.plot(circ[0], circ[1], color="#94a3b8", lw=1.5, label="círculo unitário")
    ax.plot(img[0], img[1], color="#4f46e5", lw=2, label="imagem")
    for k, d in enumerate(an.reais):
        v = np.array(d.vetor.evalf(), dtype=float).ravel()
        v = v / np.linalg.norm(v)
        c = ("#059669", "#d97706")[k % 2]
        ax.plot(
            [-lim * v[0], lim * v[0]],
            [-lim * v[1], lim * v[1]],
            color=c,
            lw=1.6,
            ls="--",
            label=f"λ = {sp.nsimplify(d.valor)}",
        )
    leg = ax.legend(fontsize=8, facecolor=e["fundo"], edgecolor=e["grade"], loc="upper left")
    for tx in leg.get_texts():
        tx.set_color(e["texto"])
    return fig
