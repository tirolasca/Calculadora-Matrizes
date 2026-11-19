"""Conteúdo e exercícios do Aprendizado. Gabaritos vêm do núcleo; nada é escrito à mão."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from matrizes import nucleo

from . import matrix_service as ms
from . import step_service as ss

NIVEIS = ("básico", "intermediário", "avançado")


# ----------------------------------------------------------------------
# Conceitos
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Conceito:
    id: str
    titulo: str
    texto: str
    formula: str  # LaTeX
    exemplo: str  # LaTeX
    pagina: str  # chave da página relacionada (laboratório/geometria/calculadora)


CONCEITOS = [
    Conceito(
        "matriz",
        "Matriz",
        "Tabela retangular m×n de números (ou expressões). aᵢⱼ é o elemento da linha i, coluna j.",
        r"A = [a_{ij}]_{m\times n}",
        r"\begin{bmatrix}1&2&3\\4&5&6\end{bmatrix}\ \text{é } 2\times 3",
        "operacoes",
    ),
    Conceito(
        "soma",
        "Soma e multiplicação por escalar",
        "Somam-se elementos de mesma posição (mesma dimensão); o escalar multiplica todos os elementos.",
        r"(A+B)_{ij}=a_{ij}+b_{ij},\quad (kA)_{ij}=k\,a_{ij}",
        r"2\begin{bmatrix}1&0\\3&-1\end{bmatrix}=\begin{bmatrix}2&0\\6&-2\end{bmatrix}",
        "operacoes",
    ),
    Conceito(
        "produto",
        "Produto de matrizes",
        "Linha por coluna. Exige colunas de A = linhas de B. Não é comutativo.",
        r"c_{ij}=\sum_k a_{ik}b_{kj}",
        r"\begin{bmatrix}1&2\\3&4\end{bmatrix}\begin{bmatrix}0&1\\1&0\end{bmatrix}=\begin{bmatrix}2&1\\4&3\end{bmatrix}",
        "comparacao",
    ),
    Conceito(
        "transposta",
        "Transposta",
        "Troca linhas por colunas. (AB)ᵀ = BᵀAᵀ.",
        r"(A^T)_{ij}=a_{ji}",
        r"\begin{bmatrix}1&2&3\end{bmatrix}^T=\begin{bmatrix}1\\2\\3\end{bmatrix}",
        "operacoes",
    ),
    Conceito(
        "determinante",
        "Determinante",
        "Número associado a uma matriz quadrada. É zero exatamente quando a matriz não tem inversa; |det| é o fator de escala de áreas/volumes.",
        r"\det\begin{bmatrix}a&b\\c&d\end{bmatrix}=ad-bc",
        r"\det\begin{bmatrix}2&1\\5&3\end{bmatrix}=2\cdot3-1\cdot5=1",
        "transformacoes",
    ),
    Conceito(
        "inversa",
        "Matriz inversa",
        "A⁻¹ é a matriz que desfaz A. Existe se, e somente se, det(A) ≠ 0.",
        r"AA^{-1}=A^{-1}A=I,\quad A^{-1}=\tfrac{1}{\det A}\operatorname{adj}A",
        r"\begin{bmatrix}2&1\\5&3\end{bmatrix}^{-1}=\begin{bmatrix}3&-1\\-5&2\end{bmatrix}",
        "operacoes",
    ),
    Conceito(
        "posto",
        "Posto (rank)",
        "Número de linhas (ou colunas) linearmente independentes; igual ao número de pivôs no escalonamento.",
        r"\operatorname{posto}(A)=\#\text{pivôs}",
        r"\operatorname{posto}\begin{bmatrix}1&2\\2&4\end{bmatrix}=1",
        "experimentacao",
    ),
    Conceito(
        "escalonamento",
        "Escalonamento (Gauss-Jordan)",
        "Operações elementares nas linhas levam a matriz à forma escalonada reduzida sem alterar as soluções.",
        r"L_i\leftrightarrow L_j,\; L_i\leftarrow cL_i,\; L_i\leftarrow L_i+cL_j",
        r"\left[\begin{array}{cc|c}1&1&3\\1&-1&1\end{array}\right]\to\left[\begin{array}{cc|c}1&0&2\\0&1&1\end{array}\right]",
        "sistemas",
    ),
    Conceito(
        "sistemas",
        "Sistemas lineares e Rouché-Capelli",
        "Compare posto(A) e posto([A|b]) com o nº n de incógnitas: iguais e = n → SPD; iguais e < n → SPI; diferentes → SI.",
        r"p(A)=p([A|b])=n\Rightarrow SPD;\ p(A)=p([A|b])<n\Rightarrow SPI;\ p(A)\ne p([A|b])\Rightarrow SI",
        r"x+y=2,\ x+y=3\ \Rightarrow\ SI",
        "sistemas",
    ),
    Conceito(
        "autovalores",
        "Autovalores e autovetores",
        "Av = λv com v ≠ 0: v é uma direção que A apenas estica ou inverte. Os λ são as raízes do polinômio característico.",
        r"\det(A-\lambda I)=0",
        r"\begin{bmatrix}2&1\\1&2\end{bmatrix}:\ \lambda=1,\,3",
        "geometria",
    ),
    Conceito(
        "transformacoes",
        "Transformações lineares",
        "Toda matriz 2×2 define uma transformação do plano: rotação, reflexão, escala, cisalhamento ou combinações.",
        r"T(\mathbf{x})=A\mathbf{x}",
        r"R_{90^\circ}=\begin{bmatrix}0&-1\\1&0\end{bmatrix}",
        "transformacoes",
    ),
    Conceito(
        "independencia",
        "Independência linear, span e base",
        "Vetores são independentes se nenhum é combinação dos outros. Dois vetores independentes de R² geram o plano e formam uma base.",
        r"c_1v_1+c_2v_2=0\Rightarrow c_1=c_2=0",
        r"\det[v_1\ v_2]\neq0\iff\text{independentes}",
        "geometria",
    ),
]


# ----------------------------------------------------------------------
# Exemplos resolvidos
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Exemplo:
    id: str
    titulo: str
    operacao: str  # nome no núcleo, ou "Sistema (método)"
    matrizes: tuple
    param: str = ""
    metodo: str | None = None
    comentario: str = ""


EXEMPLOS = [
    Exemplo(
        "soma",
        "Somar duas matrizes",
        "Soma (A + B)",
        (((1, 2), (3, 4)), ((5, 6), (7, 8))),
        comentario="Mesma dimensão: soma posição a posição.",
    ),
    Exemplo(
        "produto",
        "Produto 2×3 por 3×2",
        "Multiplicação (A × B)",
        (((1, 2, 3), (4, 5, 6)), ((1, 0), (0, 1), (2, 1))),
        comentario="O resultado é 2×2.",
    ),
    Exemplo(
        "det3",
        "Determinante 3×3 (Sarrus)",
        "Determinante",
        (((2, 1, -1), (-3, -1, 2), (-2, 1, 2)),),
    ),
    Exemplo(
        "inversa",
        "Inversa 3×3 por Gauss-Jordan",
        "Inversa",
        (((2, 1, -1), (-3, -1, 2), (-2, 1, 2)),),
        metodo="gauss",
    ),
    Exemplo(
        "inversa2", "Inversa 2×2 pela adjunta", "Inversa", (((2, 1), (5, 3)),), metodo="adjunta"
    ),
    Exemplo(
        "rref", "Escalonar uma matriz", "Escalonar (RREF)", (((1, 2, 1), (2, 4, 0), (1, 1, 1)),)
    ),
    Exemplo("autov", "Autovalores 2×2", "Autovalores e autovetores", (((4, 1), (2, 3)),)),
    Exemplo(
        "spd",
        "Sistema SPD por Gauss",
        "Sistema",
        (((2, 1, -1, 8), (-3, -1, 2, -11), (-2, 1, 2, -3)),),
        metodo="gauss",
    ),
    Exemplo(
        "cramer", "Sistema 2×2 por Cramer", "Sistema", (((3, 2, 12), (1, -1, 1)),), metodo="cramer"
    ),
    Exemplo("spi", "Sistema SPI", "Sistema", (((1, 1, 2), (2, 2, 4)),), metodo="gauss"),
    Exemplo("si", "Sistema SI", "Sistema", (((1, 1, 2), (1, 1, 3)),), metodo="gauss"),
]


def resolver_exemplo(e: Exemplo) -> ss.Solucao:
    mats = [sp.Matrix(m) for m in e.matrizes]
    if e.operacao == "Sistema":
        M = mats[0]
        return ss.passos_sistema(M[:, :-1], M[:, -1], e.metodo or "gauss")
    sol = ss.passos_para(e.operacao, mats, e.param or None, e.metodo)
    if sol is None:
        raise ValueError(f"Sem passo a passo para {e.operacao}")
    return sol


# ----------------------------------------------------------------------
# Exercícios
# ----------------------------------------------------------------------
@dataclass
class Exercicio:
    id: str
    nivel: str
    tipo: str
    titulo: str
    enunciado: str
    dados: dict[str, sp.Matrix]
    formato: str  # matriz | escalar | vetor | classe
    resposta: Any
    dica: str
    operacao: str  # nome da operação (para a solução explicada)
    pagina: str = "operacoes"
    extras: dict = field(default_factory=dict)


@dataclass
class Correcao:
    ok: bool
    feedback: str


def _mat(rng, m, n, lo=-5, hi=9):
    return sp.Matrix(m, n, lambda i, j: rng.randint(lo, hi))


def _inversivel(rng, n, lo=-3, hi=5):
    while True:
        A = _mat(rng, n, n, lo, hi)
        if A.det() != 0:
            return A


def _gen_soma(r):
    A, B = _mat(r, 2, 3), _mat(r, 2, 3)
    return (
        "Soma",
        "Calcule A + B.",
        {"A": A, "B": B},
        "matriz",
        A + B,
        "Some elemento a elemento.",
        "Soma (A + B)",
    )


def _gen_escalar(r):
    A, k = _mat(r, 2, 2), r.choice([-3, -2, 2, 3, 4])
    return (
        "Escalar",
        f"Calcule {k}·A.",
        {"A": A},
        "matriz",
        k * A,
        "O escalar multiplica todos os elementos.",
        "Multiplicar por escalar",
    )


def _gen_transposta(r):
    A = _mat(r, 2, 3)
    return (
        "Transposta",
        "Determine Aᵀ.",
        {"A": A},
        "matriz",
        A.T,
        "Linhas viram colunas.",
        "Transposta",
    )


def _gen_traco(r):
    A = _mat(r, 3, 3)
    return (
        "Traço",
        "Calcule tr(A).",
        {"A": A},
        "escalar",
        A.trace(),
        "Some a diagonal principal.",
        "Traço",
    )


def _gen_det2(r):
    A = _mat(r, 2, 2)
    return (
        "Determinante 2×2",
        "Calcule det(A).",
        {"A": A},
        "escalar",
        A.det(),
        "ad − bc.",
        "Determinante",
    )


def _gen_prod(r):
    A, B = _mat(r, 2, 3, -3, 5), _mat(r, 3, 2, -3, 5)
    return (
        "Produto",
        "Calcule A·B.",
        {"A": A, "B": B},
        "matriz",
        A * B,
        "Linha de A × coluna de B; o resultado é 2×2.",
        "Multiplicação (A × B)",
    )


def _gen_det3(r):
    A = _mat(r, 3, 3, -4, 6)
    return (
        "Determinante 3×3",
        "Calcule det(A).",
        {"A": A},
        "escalar",
        A.det(),
        "Use a regra de Sarrus.",
        "Determinante",
    )


def _gen_inv2(r):
    A = _inversivel(r, 2)
    return (
        "Inversa 2×2",
        "Determine A⁻¹ (use frações se necessário, ex.: 1/2).",
        {"A": A},
        "matriz",
        A.inv(),
        "A⁻¹ = adj(A)/det(A).",
        "Inversa",
    )


def _gen_posto(r):
    A = _mat(r, 3, 3, -3, 4)
    A[2, :] = A[0, :] + A[1, :] if r.random() < 0.6 else A[2, :]
    return (
        "Posto",
        "Determine o posto de A.",
        {"A": A},
        "escalar",
        sp.Integer(A.rank()),
        "Escalone e conte os pivôs.",
        "Posto (rank)",
    )


def _gen_sis2(r):
    while True:
        A = _mat(r, 2, 2, -4, 5)
        if A.det() != 0:
            break
    x = sp.Matrix([r.randint(-4, 5), r.randint(-4, 5)])
    b = A * x
    return (
        "Sistema 2×2",
        "Resolva A·x = b e informe x₁, x₂ separados por vírgula.",
        {"A": A, "b": b},
        "vetor",
        list(x),
        "Escalonamento, Cramer ou x = A⁻¹b.",
        "Sistema",
    )


def _gen_inv3(r):
    A = _inversivel(r, 3, -2, 3)
    return (
        "Inversa 3×3",
        "Determine A⁻¹ (frações permitidas).",
        {"A": A},
        "matriz",
        A.inv(),
        "Gauss-Jordan em [A | I].",
        "Inversa",
    )


def _gen_classe(r):
    tipo = r.choice(["SPD", "SPI", "SI"])
    if tipo == "SPD":
        while True:
            A = _mat(r, 3, 3, -3, 4)
            if A.det() != 0:
                break
        b = _mat(r, 3, 1, -5, 6)
    else:
        base = _mat(r, 2, 3, -3, 4)
        A = sp.Matrix.vstack(base, base[0, :] + base[1, :])
        if A.rank() == 3:
            return _gen_classe(r)
        b0 = _mat(r, 2, 1, -4, 5)
        b = sp.Matrix.vstack(
            b0, sp.Matrix([[b0[0] + b0[1] + (0 if tipo == "SPI" else r.choice([1, 2, 3]))]])
        )
    t, *_ = nucleo.classificar(A, b)
    return (
        "Classificar sistema",
        "Classifique o sistema A·x = b: SPD, SPI ou SI.",
        {"A": A, "b": b},
        "classe",
        t,
        "Compare posto(A), posto([A|b]) e o nº de incógnitas.",
        "Sistema",
    )


def _gen_autov(r):
    d1, d2 = r.sample(range(-3, 6), 2)
    P = sp.Matrix([[1, r.randint(1, 3)], [r.choice([0, 1]), 1]])
    if P.det() != 1:
        P = sp.Matrix([[1, 1], [0, 1]])
    A = P * sp.diag(d1, d2) * P.inv()
    return (
        "Autovalores 2×2",
        "Informe os autovalores de A separados por vírgula.",
        {"A": A},
        "vetor",
        sorted([d1, d2]),
        "Resolva det(A − λI) = 0.",
        "Autovalores e autovetores",
    )


def _gen_pot(r):
    A = _mat(r, 2, 2, -2, 3)
    return "Potência", "Calcule A³.", {"A": A}, "matriz", A**3, "A³ = A·A·A.", "Potência (Aⁿ)"


def _gen_det4(r):
    A = _mat(r, 4, 4, -2, 3)
    return (
        "Determinante 4×4",
        "Calcule det(A).",
        {"A": A},
        "escalar",
        A.det(),
        "Escalone até a forma triangular.",
        "Determinante",
    )


GERADORES = {
    "básico": [_gen_soma, _gen_escalar, _gen_transposta, _gen_traco, _gen_det2],
    "intermediário": [_gen_prod, _gen_det3, _gen_inv2, _gen_posto, _gen_sis2],
    "avançado": [_gen_inv3, _gen_classe, _gen_autov, _gen_pot, _gen_det4],
}


def gerar(nivel: str, semente: int, indice: int | None = None) -> Exercicio:
    """Exercício reproduzível: mesma (nível, semente, índice) → mesmo enunciado e gabarito."""
    if nivel not in GERADORES:
        raise ValueError(f"Nível inválido: {nivel}")
    gens = GERADORES[nivel]
    rng = random.Random(f"{nivel}:{semente}")
    g = gens[(indice if indice is not None else rng.randrange(len(gens))) % len(gens)]
    titulo, enun, dados, fmt, resp, dica, op = g(rng)
    pagina = (
        "sistemas"
        if op == "Sistema"
        else "operacoes"
        if titulo not in {"Posto", "Autovalores 2×2"}
        else "propriedades"
    )
    return Exercicio(
        f"{nivel}:{semente}:{g.__name__[5:]}",
        nivel,
        g.__name__[5:],
        titulo,
        enun,
        dados,
        fmt,
        resp,
        dica,
        op,
        pagina,
    )


def corrigir(ex: Exercicio, resposta) -> Correcao:
    """`resposta`: Matrix (formato matriz) ou str (escalar, vetor, classe)."""
    try:
        if ex.formato == "matriz":
            M = resposta
            if not isinstance(M, sp.MatrixBase):
                return Correcao(False, "Preencha a matriz resposta.")
            if M.shape != ex.resposta.shape:
                return Correcao(
                    False,
                    f"A resposta deveria ser {ex.resposta.rows}×{ex.resposta.cols}, mas você informou {M.rows}×{M.cols}.",
                )
            erradas = [
                (i + 1, j + 1)
                for i in range(M.rows)
                for j in range(M.cols)
                if sp.simplify(M[i, j] - ex.resposta[i, j]) != 0
            ]
            if not erradas:
                return Correcao(True, "Correto!")
            pos = ", ".join(f"({i},{j})" for i, j in erradas[:6])
            return Correcao(False, f"{len(erradas)} elemento(s) incorreto(s): posições {pos}.")
        if ex.formato == "escalar":
            v = ms.expressao(str(resposta))
            if sp.simplify(v - ex.resposta) == 0:
                return Correcao(True, "Correto!")
            dica = (
                " Confira o sinal."
                if sp.simplify(v + ex.resposta) == 0 and ex.resposta != 0
                else ""
            )
            return Correcao(False, "Resposta incorreta." + dica)
        if ex.formato == "vetor":
            partes = [p for p in str(resposta).replace(";", ",").split(",") if p.strip()]
            vs = [ms.expressao(p) for p in partes]
            if len(vs) != len(ex.resposta):
                return Correcao(False, f"Informe {len(ex.resposta)} valores separados por vírgula.")
            alvo = ex.resposta if ex.tipo != "autov" else sorted(ex.resposta)
            ok = all(
                sp.simplify(a - b) == 0
                for a, b in zip(vs if ex.tipo != "autov" else sorted(vs), alvo, strict=True)
            )
            return Correcao(
                ok,
                "Correto!"
                if ok
                else "Algum valor está incorreto. Verifique substituindo no problema.",
            )
        if ex.formato == "classe":
            v = str(resposta).strip().upper()
            if v not in {"SPD", "SPI", "SI"}:
                return Correcao(False, "Escolha SPD, SPI ou SI.")
            return Correcao(
                v == ex.resposta,
                "Correto!" if v == ex.resposta else "Classificação incorreta. Compare os postos.",
            )
    except ValueError as e:
        return Correcao(False, str(e))
    raise ValueError(ex.formato)


def solucao(ex: Exercicio) -> ss.Solucao:
    """Solução explicada (validada contra o núcleo pelo step_service)."""
    if ex.operacao == "Sistema":
        return ss.passos_sistema(ex.dados["A"], ex.dados["b"], "gauss")
    mats = [ex.dados[k] for k in ("A", "B") if k in ex.dados]
    param = {"escalar": None}.get(ex.tipo)
    if ex.tipo == "escalar":
        k = ex.resposta[0, 0] / ex.dados["A"][0, 0] if ex.dados["A"][0, 0] != 0 else None
        param = (
            k
            if k is not None
            else next(c for c in (-3, -2, 2, 3, 4) if c * ex.dados["A"] == ex.resposta)
        )
    if ex.tipo == "pot":
        param = 3
    sol = ss.passos_para(ex.operacao, mats, param, "gauss" if ex.operacao == "Inversa" else None)
    if sol is None:
        raise ValueError(ex.operacao)
    return sol
