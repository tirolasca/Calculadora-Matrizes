"""Passo a passo didático (com LaTeX) para as operações do núcleo.

Camada de *explicação*: não substitui o núcleo. Cada gerador refaz a conta em etapas
e `passos_para` confere que o resultado das etapas é igual ao do núcleo
(`InconsistenciaMatematica` se não for). Não importa Streamlit.

Estrutura de cada `Solucao` (spec, etapa 5):
identificação · entradas · fórmula · substituição/desenvolvimento (passos)
· resultado final · interpretação.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from matrizes import nucleo

COR = "#d97706"  # destaque do passo atual
LIMITE_MULT = 16  # nº máximo de elementos detalhados na multiplicação
LIMITE_POT = 6
LIMITE_COFATORES = 4


class PassosIndisponiveis(ValueError):
    """A operação existe no núcleo, mas não há passo a passo confiável para este caso."""


class InconsistenciaMatematica(AssertionError):
    """Os passos não reproduzem o resultado do núcleo (bug a corrigir, nunca a mostrar)."""


@dataclass
class Passo:
    titulo: str
    latex: str = ""
    texto: str = ""


@dataclass
class Solucao:
    operacao: str
    identificacao: str
    entradas: list[str]
    formula: str
    passos: list[Passo]
    valor: Any  # Matrix, expressão, ou estrutura própria (sistemas, autovalores)
    resultado_latex: str
    interpretacao: str
    aviso: str = ""
    extras: dict = field(default_factory=dict)


# ----------------------------------------------------------------------
# LaTeX
# ----------------------------------------------------------------------
def _l(x) -> str:
    return sp.latex(x)


def _p(x) -> str:
    """Valor entre parênteses quando necessário (negativos, somas)."""
    x = sp.sympify(x)
    s = sp.latex(x)
    if x.is_Add or (x.is_number and x.could_extract_minus_sign()):
        return rf"\left({s}\right)"
    return s


def _cor(s: str) -> str:
    return rf"{{\color{{{COR}}}{{{s}}}}}"


def latex_matriz(M, linhas=(), colunas=(), barra=None, delim="bmatrix") -> str:
    """Matriz em LaTeX. `linhas`/`colunas` (0-based) são destacadas; `barra` = coluna
    antes da qual aparece a barra vertical (matriz aumentada)."""

    def cel(i, j):
        s = _l(M[i, j])
        return _cor(s) if (i in linhas or j in colunas) else s

    corpo = r" \\ ".join(" & ".join(cel(i, j) for j in range(M.cols)) for i in range(M.rows))
    if barra is None:
        return rf"\begin{{{delim}}} {corpo} \end{{{delim}}}"
    cols = "c" * barra + "|" + "c" * (M.cols - barra)
    return rf"\left[\begin{{array}}{{{cols}}} {corpo} \end{{array}}\right]"


def latex_exprs(linhas: list[list[str]]) -> str:
    corpo = r" \\ ".join(" & ".join(r) for r in linhas)
    return rf"\begin{{bmatrix}} {corpo} \end{{bmatrix}}"


def _rot(nome, M) -> str:
    return rf"{nome} = {latex_matriz(M)}"


def _dim(M) -> str:
    return f"{M.rows}×{M.cols}"


def _num_ou_simbolo(x) -> str:
    return _l(x)


# ----------------------------------------------------------------------
# Gauss-Jordan com registro de operações
# ----------------------------------------------------------------------
def _gauss_jordan(M, ncoef, passos, barra=None):
    """Escalona M até a forma reduzida registrando cada operação elementar.
    Retorna (R, colunas_pivô). Só para matrizes numéricas."""
    if nucleo.tem_simbolos(M):
        raise PassosIndisponiveis(
            "O escalonamento passo a passo só está disponível para entradas numéricas."
        )
    M = M.copy()
    passos.append(Passo("Matriz inicial", latex_matriz(M, barra=barra)))
    r, pivos = 0, []
    for c in range(ncoef):
        if r >= M.rows:
            break
        p = next((i for i in range(r, M.rows) if M[i, c] != 0), None)
        if p is None:
            passos.append(
                Passo(
                    f"Coluna {c + 1}",
                    "",
                    "Nenhum pivô possível nesta coluna: segue para a próxima.",
                )
            )
            continue
        if p != r:
            M.row_swap(r, p)
            passos.append(
                Passo(
                    f"L{r + 1} ↔ L{p + 1}",
                    latex_matriz(M, linhas=(r, p), barra=barra),
                    f"O elemento na posição ({r + 1},{c + 1}) era zero; troca de linhas.",
                )
            )
        if M[r, c] != 1:
            f = 1 / M[r, c]
            M[r, :] = M[r, :] * f
            passos.append(
                Passo(
                    f"L{r + 1} ← ({f})·L{r + 1}",
                    latex_matriz(M, linhas=(r,), barra=barra),
                    f"Torna o pivô da coluna {c + 1} igual a 1.",
                )
            )
        for i in range(M.rows):
            if i != r and M[i, c] != 0:
                f = M[i, c]
                M[i, :] = M[i, :] - f * M[r, :]
                sinal = "−" if f > 0 else "+"
                passos.append(
                    Passo(
                        f"L{i + 1} ← L{i + 1} {sinal} ({abs(f)})·L{r + 1}",
                        latex_matriz(M, linhas=(i,), barra=barra),
                        f"Zera a posição ({i + 1},{c + 1}).",
                    )
                )
        pivos.append(c)
        r += 1
    passos.append(Passo("Forma escalonada reduzida", latex_matriz(M, barra=barra)))
    return M, pivos


def _quadrada(A, o_que):
    if not A.is_square:
        raise ValueError(f"{o_que}: a matriz precisa ser quadrada.")


# ----------------------------------------------------------------------
# Operações elementares
# ----------------------------------------------------------------------
def _soma_sub(A, B, sinal):
    if A.shape != B.shape:
        raise ValueError("As matrizes precisam ter as mesmas dimensões.")
    op = "+" if sinal == 1 else "-"
    nome = "Soma" if sinal == 1 else "Subtração"
    R = A + B if sinal == 1 else A - B
    subst = latex_exprs(
        [[rf"{_l(A[i, j])} {op} {_p(B[i, j])}" for j in range(A.cols)] for i in range(A.rows)]
    )
    return Solucao(
        operacao=f"{nome} de matrizes",
        identificacao=f"{nome} de duas matrizes {_dim(A)}.",
        entradas=[_rot("A", A), _rot("B", B)],
        formula=rf"(A {op} B)_{{ij}} = a_{{ij}} {op} b_{{ij}}",
        passos=[
            Passo("Mesma dimensão", "", f"As duas matrizes são {_dim(A)}: a operação é possível."),
            Passo("Substituição elemento a elemento", subst),
            Passo("Resultado das contas", latex_matriz(R)),
        ],
        valor=R,
        resultado_latex=rf"A {op} B = {latex_matriz(R)}",
        interpretacao="Cada posição do resultado depende só das posições correspondentes de A e B.",
    )


def _escalar(A, k):
    R = A * k
    subst = latex_exprs(
        [[rf"{_p(k)} \cdot {_p(A[i, j])}" for j in range(A.cols)] for i in range(A.rows)]
    )
    return Solucao(
        operacao="Multiplicação por escalar",
        identificacao=f"Multiplica a matriz {_dim(A)} pelo escalar k = {k}.",
        entradas=[_rot("A", A), rf"k = {_l(k)}"],
        formula=r"(kA)_{ij} = k \cdot a_{ij}",
        passos=[
            Passo("Substituição", subst, "O escalar multiplica todos os elementos."),
            Passo("Resultado das contas", latex_matriz(R)),
        ],
        valor=R,
        resultado_latex=rf"{_p(k)}A = {latex_matriz(R)}",
        interpretacao="Multiplicar por k muda a escala de todos os elementos; k = 0 anula a matriz.",
    )


def _multiplicacao(A, B):
    if A.cols != B.rows:
        raise ValueError(f"Colunas de A ({A.cols}) ≠ linhas de B ({B.rows}).")
    R = A * B
    m, n, p = A.rows, A.cols, B.cols
    passos = [
        Passo(
            "Compatibilidade",
            rf"({m}\times {n})\cdot({n}\times {p}) \to {m}\times {p}",
            "Colunas de A = linhas de B: o produto existe e tem o tamanho acima.",
        )
    ]
    pares = [(i, j) for i in range(m) for j in range(p)]
    aviso = ""
    if len(pares) > LIMITE_MULT:
        pares = pares[:2]
        aviso = (
            f"O resultado tem {m * p} elementos; aqui são detalhados apenas c₁₁ e c₁₂ como "
            "exemplo. Os demais seguem a mesma fórmula."
        )
    for i, j in pares:
        termos = " + ".join(rf"{_p(A[i, k])} \cdot {_p(B[k, j])}" for k in range(n))
        passos.append(
            Passo(
                f"c{i + 1}{j + 1} = (linha {i + 1} de A) · (coluna {j + 1} de B)",
                rf"c_{{{i + 1}{j + 1}}} = {termos} = {_l(R[i, j])}",
            )
        )
    passos.append(Passo("Montagem do resultado", latex_matriz(R)))
    return Solucao(
        operacao="Multiplicação de matrizes",
        identificacao=f"Produto A·B com A {_dim(A)} e B {_dim(B)}.",
        entradas=[_rot("A", A), _rot("B", B)],
        formula=r"c_{ij} = \sum_{k=1}^{n} a_{ik}\, b_{kj}",
        passos=passos,
        valor=R,
        resultado_latex=rf"A \cdot B = {latex_matriz(R)}",
        interpretacao="Cada elemento é o produto escalar de uma linha de A por uma coluna de B. "
        "Em geral A·B ≠ B·A.",
        aviso=aviso,
    )


def _transposta(A):
    R = A.T
    return Solucao(
        operacao="Transposta",
        identificacao=f"Transposta de uma matriz {_dim(A)}.",
        entradas=[_rot("A", A)],
        formula=r"(A^{T})_{ij} = a_{ji}",
        passos=[
            Passo(
                "Linhas viram colunas",
                "",
                f"A linha i de A passa a ser a coluna i de Aᵀ ({_dim(A)} → {_dim(R)}).",
            ),
            Passo("Resultado", latex_matriz(R)),
        ],
        valor=R,
        resultado_latex=rf"A^{{T}} = {latex_matriz(R)}",
        interpretacao="A transposta espelha a matriz pela diagonal principal.",
    )


def _traco(A):
    _quadrada(A, "Traço")
    n = A.rows
    soma = " + ".join(_p(A[i, i]) for i in range(n))
    t = A.trace()
    return Solucao(
        operacao="Traço",
        identificacao=f"Traço de uma matriz {_dim(A)}.",
        entradas=[_rot("A", A)],
        formula=r"\operatorname{tr}(A) = \sum_{i=1}^{n} a_{ii}",
        passos=[
            Passo("Diagonal principal", "", "Somam-se apenas os elementos a₁₁, a₂₂, …, aₙₙ."),
            Passo("Substituição", rf"\operatorname{{tr}}(A) = {soma} = {_l(t)}"),
        ],
        valor=t,
        resultado_latex=rf"\operatorname{{tr}}(A) = {_l(t)}",
        interpretacao="O traço também é a soma dos autovalores (contados com multiplicidade).",
    )


def _potencia(A, n):
    _quadrada(A, "Potência")
    n = int(n)
    if abs(n) > LIMITE_POT:
        raise PassosIndisponiveis(f"Passo a passo disponível para |n| ≤ {LIMITE_POT}.")
    if n < 0 and A.det() == 0:
        raise ValueError("Matriz singular: não existe potência negativa.")
    passos: list[Passo] = []
    base = A
    if n < 0:
        base = A.inv()
        passos.append(
            Passo(
                "Potência negativa = potência da inversa",
                rf"A^{{{n}}} = \left(A^{{-1}}\right)^{{{-n}}},\quad A^{{-1}} = {latex_matriz(base)}",
            )
        )
    k = abs(n)
    if k == 0:
        passos.append(Passo("Potência zero", "", "Por definição A⁰ = I."))
        R = sp.eye(A.rows)
    else:
        R = base
        for e in range(2, k + 1):
            novo = R * base
            passos.append(
                Passo(
                    f"Potência {e}: M^{e} = M^{e - 1} · M",
                    rf"{latex_matriz(R)} \cdot {latex_matriz(base)} = {latex_matriz(novo)}",
                    "M = A" if n > 0 else "M = A⁻¹",
                )
            )
            R = novo
        if k == 1:
            passos.append(Passo("Expoente 1", "", "Basta tomar a própria base."))
    return Solucao(
        operacao="Potência de matriz",
        identificacao=f"Aⁿ com n = {n} para A {_dim(A)}.",
        entradas=[_rot("A", A), f"n = {n}"],
        formula=r"A^{n} = \underbrace{A \cdot A \cdots A}_{n\ \text{vezes}}",
        passos=passos,
        valor=R,
        resultado_latex=rf"A^{{{n}}} = {latex_matriz(R)}",
        interpretacao="Só existe para matrizes quadradas; expoentes negativos exigem inversa.",
    )


# ----------------------------------------------------------------------
# Determinante
# ----------------------------------------------------------------------
def _det_triangularizacao(A, passos):
    M = A.copy()
    sinal = 1
    n = M.rows
    passos.append(Passo("Matriz inicial", latex_matriz(M)))
    for c in range(n):
        p = next((i for i in range(c, n) if M[i, c] != 0), None)
        if p is None:
            passos.append(
                Passo(
                    f"Coluna {c + 1}", "", "Coluna sem pivô abaixo da diagonal: o determinante é 0."
                )
            )
            return sp.Integer(0)
        if p != c:
            M.row_swap(c, p)
            sinal = -sinal
            passos.append(
                Passo(
                    f"L{c + 1} ↔ L{p + 1}",
                    latex_matriz(M, linhas=(c, p)),
                    "Trocar duas linhas inverte o sinal do determinante.",
                )
            )
        for i in range(c + 1, n):
            if M[i, c] != 0:
                f = M[i, c] / M[c, c]
                M[i, :] = M[i, :] - f * M[c, :]
                passos.append(
                    Passo(
                        f"L{i + 1} ← L{i + 1} − ({f})·L{c + 1}",
                        latex_matriz(M, linhas=(i,)),
                        "Esta operação não altera o determinante.",
                    )
                )
    diag = [M[i, i] for i in range(n)]
    prod = sp.Integer(1)
    for d in diag:
        prod *= d
    s = "(-1)" if sinal < 0 else "(+1)"
    passos.append(
        Passo(
            "Produto da diagonal",
            rf"\det(A) = {s}\cdot "
            + r" \cdot ".join(_p(d) for d in diag)
            + rf" = {_l(sinal * prod)}",
            "Em uma matriz triangular o determinante é o produto da diagonal; "
            "o sinal vem das trocas de linhas.",
        )
    )
    return sinal * prod


def _determinante(A):
    _quadrada(A, "Determinante")
    n = A.rows
    passos: list[Passo] = []
    if n == 1:
        formula = r"\det([a]) = a"
        d = A[0, 0]
        passos.append(Passo("Matriz 1×1", rf"\det(A) = {_l(d)}"))
    elif n == 2:
        formula = r"\det\begin{bmatrix} a & b \\ c & d \end{bmatrix} = ad - bc"
        a, b, c, e = A[0, 0], A[0, 1], A[1, 0], A[1, 1]
        d = a * e - b * c
        passos.append(
            Passo(
                "Substituição",
                rf"\det(A) = {_p(a)}\cdot{_p(e)} - {_p(b)}\cdot{_p(c)}",
            )
        )
        passos.append(
            Passo(
                "Produtos",
                rf"= {_l(a * e)} - {_p(b * c)}",
                "Diagonal principal menos diagonal secundária.",
            )
        )
        passos.append(Passo("Resultado", rf"\det(A) = {_l(d)}"))
    elif n == 3:
        formula = (
            r"\det(A) = a_{11}a_{22}a_{33} + a_{12}a_{23}a_{31} + a_{13}a_{21}a_{32}"
            r" - a_{13}a_{22}a_{31} - a_{11}a_{23}a_{32} - a_{12}a_{21}a_{33}"
        )
        a = A
        pos = [
            a[0, 0] * a[1, 1] * a[2, 2],
            a[0, 1] * a[1, 2] * a[2, 0],
            a[0, 2] * a[1, 0] * a[2, 1],
        ]
        neg = [
            a[0, 2] * a[1, 1] * a[2, 0],
            a[0, 0] * a[1, 2] * a[2, 1],
            a[0, 1] * a[1, 0] * a[2, 2],
        ]
        idx_pos = [(0, 0, 1, 1, 2, 2), (0, 1, 1, 2, 2, 0), (0, 2, 1, 0, 2, 1)]
        idx_neg = [(0, 2, 1, 1, 2, 0), (0, 0, 1, 2, 2, 1), (0, 1, 1, 0, 2, 2)]

        def prod(ix):
            return r"\cdot".join(_p(a[ix[k], ix[k + 1]]) for k in (0, 2, 4))

        subst = (
            " + ".join(prod(ix) for ix in idx_pos)
            + " - "
            + " - ".join(rf"\left({prod(ix)}\right)" for ix in idx_neg)
        )
        passos.append(Passo("Regra de Sarrus — substituição", rf"\det(A) = {subst}"))
        passos.append(
            Passo(
                "Produtos",
                rf"= {_l(pos[0])} + {_p(pos[1])} + {_p(pos[2])}"
                rf" - {_p(neg[0])} - {_p(neg[1])} - {_p(neg[2])}",
                "Três produtos de diagonais principais somam; três de secundárias subtraem.",
            )
        )
        d = sum(pos) - sum(neg)
        passos.append(Passo("Resultado", rf"\det(A) = {_l(sp.expand(d))}"))
        d = sp.expand(d)
    else:
        if nucleo.tem_simbolos(A):
            raise PassosIndisponiveis("Para n ≥ 4 o passo a passo exige entradas numéricas.")
        formula = r"\det(A) = (-1)^{s}\prod_i u_{ii}\quad (\text{eliminação de Gauss})"
        d = _det_triangularizacao(A, passos)
    return Solucao(
        operacao="Determinante",
        identificacao=f"Determinante de uma matriz {_dim(A)}.",
        entradas=[_rot("A", A)],
        formula=formula,
        passos=passos,
        valor=d,
        resultado_latex=rf"\det(A) = {_l(d)}",
        interpretacao=(
            "det(A) = 0: matriz singular (sem inversa; linhas/colunas dependentes)."
            if d == 0 and not nucleo.tem_simbolos(A)
            else "det(A) ≠ 0 indica matriz invertível; |det| é o fator de escala de áreas/volumes."
            if not nucleo.tem_simbolos(A)
            else "Com parâmetros, a matriz é invertível exatamente quando esta expressão ≠ 0."
        ),
    )


# ----------------------------------------------------------------------
# Inversa, adjunta e cofatores
# ----------------------------------------------------------------------
def _cofatores_passos(A, passos):
    n = A.rows
    C = sp.zeros(n, n)
    for i in range(n):
        for j in range(n):
            minor = A.minor_submatrix(i, j)
            m = minor.det() if n > 1 else sp.Integer(1)
            C[i, j] = (-1) ** (i + j) * m
            if n <= 3 or (i, j) == (0, 0):
                passos.append(
                    Passo(
                        f"C{i + 1}{j + 1}",
                        rf"C_{{{i + 1}{j + 1}}} = (-1)^{{{i + 1}+{j + 1}}}"
                        rf"\det{latex_matriz(minor, delim='vmatrix') if n > 1 else ''} = {_l(C[i, j])}",
                    )
                )
    if n > 3:
        passos.append(
            Passo(
                "Demais cofatores",
                "",
                "Calculados do mesmo modo (menor complementar com sinal alternado).",
            )
        )
    return C


def _cofatores(A):
    _quadrada(A, "Cofatores")
    if A.rows > LIMITE_COFATORES:
        raise PassosIndisponiveis(f"Passo a passo disponível para n ≤ {LIMITE_COFATORES}.")
    passos: list[Passo] = []
    C = _cofatores_passos(A, passos)
    passos.append(Passo("Matriz de cofatores", latex_matriz(C)))
    return Solucao(
        operacao="Matriz de cofatores",
        identificacao=f"Cofatores de uma matriz {_dim(A)}.",
        entradas=[_rot("A", A)],
        formula=r"C_{ij} = (-1)^{i+j} M_{ij}",
        passos=passos,
        valor=C,
        resultado_latex=rf"\operatorname{{cof}}(A) = {latex_matriz(C)}",
        interpretacao="O cofator é o determinante do menor complementar com o sinal do tabuleiro (+ − +…).",
    )


def _adjunta(A):
    _quadrada(A, "Adjunta")
    if A.rows > LIMITE_COFATORES:
        raise PassosIndisponiveis(f"Passo a passo disponível para n ≤ {LIMITE_COFATORES}.")
    passos: list[Passo] = []
    C = _cofatores_passos(A, passos)
    passos.append(Passo("Matriz de cofatores", latex_matriz(C)))
    R = C.T
    passos.append(Passo("Transposição", rf"\operatorname{{adj}}(A) = C^{{T}} = {latex_matriz(R)}"))
    return Solucao(
        operacao="Adjunta",
        identificacao=f"Adjunta clássica de uma matriz {_dim(A)}.",
        entradas=[_rot("A", A)],
        formula=r"\operatorname{adj}(A) = C^{T}",
        passos=passos,
        valor=R,
        resultado_latex=rf"\operatorname{{adj}}(A) = {latex_matriz(R)}",
        interpretacao="A·adj(A) = det(A)·I; por isso A⁻¹ = adj(A)/det(A).",
    )


def _inversa(A, metodo="gauss"):
    _quadrada(A, "Inversa")
    if A.det() == 0:
        raise ValueError("Determinante = 0: a matriz não possui inversa.")
    n = A.rows
    passos: list[Passo] = []
    if metodo == "adjunta":
        if n > LIMITE_COFATORES:
            raise PassosIndisponiveis(f"Método da adjunta disponível para n ≤ {LIMITE_COFATORES}.")
        d = A.det()
        passos.append(Passo("Determinante", rf"\det(A) = {_l(d)} \neq 0", "A inversa existe."))
        C = _cofatores_passos(A, passos)
        passos.append(Passo("Adjunta = cofatores transpostos", latex_matriz(C.T)))
        R = C.T / d
        passos.append(
            Passo(
                "Divisão pelo determinante",
                rf"A^{{-1}} = \frac{{1}}{{{_l(d)}}}\cdot {latex_matriz(C.T)} = {latex_matriz(R)}",
            )
        )
        formula = r"A^{-1} = \dfrac{1}{\det(A)}\,\operatorname{adj}(A)"
    else:
        aug = A.row_join(sp.eye(n))
        passos.append(
            Passo(
                "Monta [A | I]",
                latex_matriz(aug, barra=n),
                "Aplicando as mesmas operações em A e em I, A vira I e I vira A⁻¹.",
            )
        )
        M, _ = _gauss_jordan(aug, n, passos, barra=n)
        R = M[:, n:]
        passos.append(Passo("Lado direito = A⁻¹", latex_matriz(R)))
        formula = r"[A \mid I] \longrightarrow [I \mid A^{-1}]"
    passos.append(
        Passo(
            "Conferência",
            rf"A \cdot A^{{-1}} = {latex_matriz(A * R)} = I",
            "Produto igual à identidade.",
        )
    )
    return Solucao(
        operacao="Inversa",
        identificacao=f"Inversa de uma matriz {_dim(A)} pelo método "
        f"{'da adjunta' if metodo == 'adjunta' else 'de Gauss-Jordan'}.",
        entradas=[_rot("A", A)],
        formula=formula,
        passos=passos,
        valor=R,
        resultado_latex=rf"A^{{-1}} = {latex_matriz(R)}",
        interpretacao="A inversa desfaz a transformação de A: A·A⁻¹ = A⁻¹·A = I.",
    )


# ----------------------------------------------------------------------
# Escalonamento e posto
# ----------------------------------------------------------------------
def _rref(A):
    passos: list[Passo] = []
    R, pivos = _gauss_jordan(A, A.cols, passos)
    return Solucao(
        operacao="Escalonamento (RREF)",
        identificacao=f"Forma escalonada reduzida de uma matriz {_dim(A)} (Gauss-Jordan).",
        entradas=[_rot("A", A)],
        formula=r"L_i \leftrightarrow L_j,\quad L_i \leftarrow c\,L_i,\quad L_i \leftarrow L_i + c\,L_j",
        passos=passos,
        valor=R,
        resultado_latex=rf"\operatorname{{RREF}}(A) = {latex_matriz(R)},\quad "
        rf"\text{{pivôs nas colunas }} {', '.join(str(p + 1) for p in pivos) or '-'}",
        interpretacao="Operações elementares não mudam o conjunto de soluções nem o posto.",
        extras={"pivos": pivos},
    )


def _posto(A):
    passos: list[Passo] = []
    R, pivos = _gauss_jordan(A, A.cols, passos)
    r = len(pivos)
    passos.append(
        Passo(
            "Contagem de pivôs", rf"\operatorname{{posto}}(A) = {r}", "Número de linhas não nulas."
        )
    )
    return Solucao(
        operacao="Posto",
        identificacao=f"Posto de uma matriz {_dim(A)} por escalonamento.",
        entradas=[_rot("A", A)],
        formula=r"\operatorname{posto}(A) = \text{nº de pivôs na forma escalonada}",
        passos=passos,
        valor=sp.Integer(r),
        resultado_latex=rf"\operatorname{{posto}}(A) = {r}",
        interpretacao="É o número de linhas (ou colunas) linearmente independentes.",
    )


# ----------------------------------------------------------------------
# Sistemas lineares
# ----------------------------------------------------------------------
def _entrada_sistema(A, b):
    return [
        _rot("A", A),
        _rot("b", b),
        rf"[A \mid b] = {latex_matriz(A.row_join(b), barra=A.cols)}",
    ]


def _ler_solucao(R, pivos, n, tipo):
    """Lê a solução na forma escalonada reduzida [R | c]. Retorna lista em x1..xn."""
    xs = sp.symbols(f"x1:{n + 1}")
    if tipo != "SPD" and tipo != "SPI":
        return None
    livres = [j for j in range(n) if j not in pivos]
    sol = [None] * n
    for k, j in enumerate(pivos):
        expr = R[k, n]
        for jl in livres:
            expr -= R[k, jl] * xs[jl]
        sol[j] = sp.simplify(expr)
    for jl in livres:
        sol[jl] = xs[jl]
    return sol


def _sistema_gauss(A, b):
    n = A.cols
    tipo, rA, rAug, _ = nucleo.classificar(A, b)
    passos: list[Passo] = []
    R, pivos = _gauss_jordan(A.row_join(b), n, passos, barra=n)
    passos.append(
        Passo(
            "Teorema de Rouché-Capelli",
            rf"\operatorname{{posto}}(A) = {rA},\quad \operatorname{{posto}}([A|b]) = {rAug},"
            rf"\quad n = {n}",
            "Compare os postos: iguais e = n → SPD; iguais e < n → SPI; diferentes → SI.",
        )
    )
    xs = sp.symbols(f"x1:{n + 1}")
    sol = None
    if tipo == "SI":
        linha = next(
            i for i in range(R.rows) if all(R[i, j] == 0 for j in range(n)) and R[i, n] != 0
        )
        passos.append(
            Passo(
                "Linha contraditória",
                rf"0 = {_l(R[linha, n])}",
                f"A linha {linha + 1} diz 0 = {R[linha, n]}, o que é impossível.",
            )
        )
        res = r"\text{Sem solução}"
        interp = "As equações se contradizem: nenhum vetor x satisfaz todas."
    else:
        sol = _ler_solucao(R, pivos, n, tipo)
        linhas = r" \\ ".join(rf"{_l(x)} &= {_l(v)}" for x, v in zip(xs, sol, strict=True))
        passos.append(Passo("Leitura da solução", rf"\begin{{aligned}} {linhas} \end{{aligned}}"))
        res = rf"\begin{{aligned}} {linhas} \end{{aligned}}"
        interp = (
            "Há exatamente uma solução (interseção única)."
            if tipo == "SPD"
            else f"Há infinitas soluções, com {n - rA} variável(is) livre(s)."
        )
    return Solucao(
        operacao="Sistema linear — escalonamento",
        identificacao=f"Sistema {A.rows}×{n} resolvido por Gauss-Jordan e classificado: {tipo}.",
        entradas=_entrada_sistema(A, b),
        formula=r"[A \mid b] \longrightarrow [R \mid c]",
        passos=passos,
        valor=(tipo, sol),
        resultado_latex=res,
        interpretacao=interp,
        extras={"tipo": tipo},
    )


def _sistema_cramer(A, b):
    _, sol_core = nucleo.resolver_cramer(A, b)  # lança ValueError se não aplicável
    n = A.cols
    d = A.det()
    passos = [
        Passo("Determinante de A", rf"\det(A) = {_l(d)} \neq 0", "A regra de Cramer se aplica.")
    ]
    sol = []
    for i in range(n):
        Ai = A.copy()
        Ai[:, i] = b
        di = Ai.det()
        xi = sp.nsimplify(di / d)
        sol.append(xi)
        passos.append(
            Passo(
                f"x{i + 1}",
                rf"A_{{{i + 1}}} = {latex_matriz(Ai, colunas=(i,))},\quad "
                rf"x_{{{i + 1}}} = \frac{{\det(A_{{{i + 1}}})}}{{\det(A)}} = \frac{{{_l(di)}}}{{{_l(d)}}} = {_l(xi)}",
                f"Troca-se a coluna {i + 1} de A pelo vetor b.",
            )
        )
    linhas = r" \\ ".join(rf"x_{{{i + 1}}} &= {_l(v)}" for i, v in enumerate(sol))
    return Solucao(
        operacao="Sistema linear — Cramer",
        identificacao=f"Sistema {n}×{n} com det(A) ≠ 0 resolvido pela regra de Cramer (SPD).",
        entradas=_entrada_sistema(A, b),
        formula=r"x_i = \dfrac{\det(A_i)}{\det(A)}",
        passos=passos,
        valor=("SPD", sol),
        resultado_latex=rf"\begin{{aligned}} {linhas} \end{{aligned}}",
        interpretacao="Com det(A) ≠ 0 o sistema é SPD; Cramer é elegante, mas caro para n grande.",
        extras={"tipo": "SPD", "core": sol_core},
    )


def _sistema_inversa(A, b):
    nucleo.resolver_inversa(A, b)  # valida aplicabilidade
    inv = _inversa(A)
    x = inv.valor * b
    passos = list(inv.passos)
    passos.append(
        Passo(
            "x = A⁻¹·b",
            rf"x = {latex_matriz(inv.valor)}\cdot{latex_matriz(b)} = {latex_matriz(x)}",
        )
    )
    linhas = r" \\ ".join(rf"x_{{{i + 1}}} &= {_l(v)}" for i, v in enumerate(x))
    return Solucao(
        operacao="Sistema linear — matriz inversa",
        identificacao=f"Sistema {A.rows}×{A.cols} resolvido por x = A⁻¹·b (SPD).",
        entradas=_entrada_sistema(A, b),
        formula=r"A x = b \;\Rightarrow\; x = A^{-1} b",
        passos=passos,
        valor=("SPD", list(x)),
        resultado_latex=rf"\begin{{aligned}} {linhas} \end{{aligned}}",
        interpretacao="Multiplicar os dois lados por A⁻¹ isola x.",
        extras={"tipo": "SPD"},
    )


SISTEMAS = {"gauss": _sistema_gauss, "cramer": _sistema_cramer, "inversa": _sistema_inversa}


def passos_sistema(A, b, metodo="gauss"):
    """Passo a passo de A·x = b e conferência com o núcleo (classificação e solução)."""
    sol = SISTEMAS[metodo](A, b)
    tipo, resposta = sol.valor
    tipo_core, *_ = nucleo.classificar(A, b)
    if tipo != tipo_core:
        raise InconsistenciaMatematica(f"classificação {tipo} ≠ {tipo_core}")
    if tipo != "SI":
        xs = sp.symbols(f"x1:{A.cols + 1}")
        ref = next(iter(sp.linsolve((A, b), *xs)))
        if any(sp.simplify(p - q) != 0 for p, q in zip(resposta, ref, strict=True)):
            raise InconsistenciaMatematica(f"solução {resposta} ≠ {list(ref)}")
    return sol


# ----------------------------------------------------------------------
# Autovalores
# ----------------------------------------------------------------------
def _autovalores(A):
    _quadrada(A, "Autovalores")
    n = A.rows
    if n > 3:
        raise PassosIndisponiveis("Passo a passo de autovalores disponível para n ≤ 3.")
    if nucleo.tem_simbolos(A):
        raise PassosIndisponiveis("Autovalores passo a passo exigem entradas numéricas.")
    lam = sp.Symbol("lambda")
    M = A - lam * sp.eye(n)
    poli = sp.expand(M.det())
    passos = [
        Passo("Matriz A − λI", rf"A - \lambda I = {latex_matriz(M)}"),
        Passo("Polinômio característico", rf"p(\lambda) = \det(A - \lambda I) = {_l(poli)}"),
    ]
    poly = sp.Poly(poli, lam)
    # grau 3 com raízes irracionais (Cardano) é ilegível e lento: só o núcleo calcula
    raizes = poly.ground_roots() if n == 3 else sp.roots(poly)
    if sum(raizes.values()) != n:
        raise PassosIndisponiveis(
            "As raízes do polinômio característico não são racionais (grau 3): o passo a passo "
            "não é exibido; os autovalores aparecem no resultado."
        )
    fat = sp.factor(poli)
    passos.append(
        Passo("Fatoração", rf"p(\lambda) = {_l(fat)}", "As raízes de p(λ) são os autovalores.")
    )
    ordem = sorted(raizes, key=lambda r: (not r.is_real, sp.N(sp.re(r)), sp.N(sp.im(r))))
    vecs = {}
    for r in ordem:
        N = A - r * sp.eye(n)
        base = N.nullspace()
        vecs[r] = base
        txt = f"λ = {r} (multiplicidade algébrica {raizes[r]})"
        if r.is_real and r.is_rational:
            sub: list[Passo] = []
            _gauss_jordan(N, n, sub)
            passos.append(Passo(f"Autovetores para {txt}", rf"A - ({_l(r)})I = {latex_matriz(N)}"))
            passos.extend(Passo("  · " + p.titulo, p.latex, p.texto) for p in sub[1:])
        else:
            passos.append(
                Passo(
                    f"Autovetores para {txt}",
                    rf"A - ({_l(r)})I = {latex_matriz(N)}",
                    "Autovalor irracional ou complexo: espaço nulo calculado diretamente.",
                )
            )
        for v in base:
            ok = sp.simplify(A * v - r * v) == sp.zeros(n, 1)
            passos.append(
                Passo(
                    "  Verificação A·v = λ·v",
                    rf"v = {latex_matriz(v)},\quad A v = {latex_matriz(sp.simplify(A * v))}"
                    rf" = {_p(r)}\, v \;{'✓' if ok else '✗'}",
                )
            )
            if not ok:
                raise InconsistenciaMatematica("autovetor não satisfaz A·v = λ·v")
    complexo = any(not r.is_real for r in ordem)
    lista = ",\\; ".join(rf"\lambda_{{{i + 1}}} = {_l(r)}" for i, r in enumerate(ordem))
    return Solucao(
        operacao="Autovalores e autovetores",
        identificacao=f"Autovalores de uma matriz {_dim(A)} pelo polinômio característico.",
        entradas=[_rot("A", A)],
        formula=r"\det(A - \lambda I) = 0,\qquad (A - \lambda I)\,v = 0",
        passos=passos,
        valor=dict(raizes),
        resultado_latex=lista,
        interpretacao=(
            "Há autovalores complexos: nenhuma direção real é preservada por A (a transformação gira)."
            if complexo
            else "Os autovetores são as direções que A apenas estica (ou inverte) por λ."
        ),
        extras={"autovetores": vecs},
    )


# ----------------------------------------------------------------------
# Catálogo e validação
# ----------------------------------------------------------------------
GERADORES = {
    "Soma (A + B)": lambda M, p, m: _soma_sub(M[0], M[1], 1),
    "Subtração (A - B)": lambda M, p, m: _soma_sub(M[0], M[1], -1),
    "Multiplicação (A × B)": lambda M, p, m: _multiplicacao(M[0], M[1]),
    "Multiplicar por escalar": lambda M, p, m: _escalar(M[0], p),
    "Potência (Aⁿ)": lambda M, p, m: _potencia(M[0], p),
    "Transposta": lambda M, p, m: _transposta(M[0]),
    "Inversa": lambda M, p, m: _inversa(M[0], m or "gauss"),
    "Determinante": lambda M, p, m: _determinante(M[0]),
    "Posto (rank)": lambda M, p, m: _posto(M[0]),
    "Traço": lambda M, p, m: _traco(M[0]),
    "Escalonar (RREF)": lambda M, p, m: _rref(M[0]),
    "Autovalores e autovetores": lambda M, p, m: _autovalores(M[0]),
    "Adjunta (adj A)": lambda M, p, m: _adjunta(M[0]),
    "Matriz de cofatores": lambda M, p, m: _cofatores(M[0]),
}


def suporta(nome_op: str) -> bool:
    return nome_op in GERADORES


def _nucleo_op(nome_op):
    return next(o for o in nucleo.OPERACOES if o.nome == nome_op)


def _valor_do_nucleo(nome_op, mats, param):
    op = _nucleo_op(nome_op)
    args = list(mats[: op.nmat])
    if op.param:
        args.append(param)
    return op.fn(*args)


def validar(sol: Solucao, nome_op: str, mats, param=None) -> None:
    """Compara o valor dos passos com o núcleo; lança InconsistenciaMatematica."""
    res = _valor_do_nucleo(nome_op, mats, param)
    if nome_op == "Autovalores e autovetores":
        ref = mats[0].eigenvals()
        if dict(ref) != dict(sol.valor):
            raise InconsistenciaMatematica(f"autovalores {sol.valor} ≠ {ref}")
        return
    ref = res[0][1]
    if isinstance(ref, str):
        ref = sp.sympify(ref)
    mine = sol.valor
    if isinstance(ref, sp.MatrixBase):
        ok = (
            isinstance(mine, sp.MatrixBase)
            and mine.shape == ref.shape
            and ((mine - ref).applyfunc(sp.simplify) == sp.zeros(*ref.shape))
        )
    else:
        ok = sp.simplify(sp.sympify(mine) - ref) == 0
    if not ok:
        raise InconsistenciaMatematica(f"{nome_op}: passos → {mine}, núcleo → {ref}")


def passos_para(nome_op: str, mats, param=None, metodo=None) -> Solucao | None:
    """Passo a passo validado, ou None se a operação não tem explicação passo a passo."""
    if nome_op not in GERADORES:
        return None
    sol = GERADORES[nome_op](list(mats), param, metodo)
    validar(sol, nome_op, list(mats), param)
    return sol
