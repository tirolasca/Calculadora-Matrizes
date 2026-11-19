"""Laboratório: modificações controladas de matrizes e experimentos guiados.

Tudo é calculado de verdade (via `matrix_service.analisar`); nenhum texto afirma algo que
não tenha sido verificado nos números do experimento.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from . import matrix_service as ms

TIPOS = {
    "trocar": "Trocar duas linhas (Lᵢ ↔ Lⱼ)",
    "escalar": "Multiplicar uma linha por k (Lᵢ ← k·Lᵢ)",
    "somar": "Somar a uma linha k vezes outra (Lᵢ ← Lᵢ + k·Lⱼ)",
    "proporcional": "Substituir uma linha por k vezes outra (Lᵢ ← k·Lⱼ)",
    "zerar": "Zerar uma linha",
    "elemento": "Alterar um elemento (aᵢⱼ ← v)",
    "transpor": "Transpor (A → Aᵀ)",
    "simetrizar": "Simetrizar ((A + Aᵀ)/2)",
}


def _idx(A: sp.Matrix, i: int, eixo: str = "linha") -> int:
    n = A.rows if eixo == "linha" else A.cols
    if not 1 <= i <= n:
        raise ValueError(f"A {eixo} {i} não existe (a matriz tem {n}).")
    return i - 1


def modificar(A: sp.Matrix, tipo: str, i: int = 1, j: int = 1, k=1) -> sp.Matrix:
    """Devolve uma cópia de A modificada. Índices de 1 a n. Lança ValueError se inválido."""
    B = A.copy()
    if tipo == "transpor":
        return B.T
    if tipo == "simetrizar":
        if not A.is_square:
            raise ValueError("Só matrizes quadradas podem ser simetrizadas.")
        return (B + B.T) / 2
    r = _idx(A, i)
    if tipo == "zerar":
        B[r, :] = sp.zeros(1, A.cols)
    elif tipo == "escalar":
        B[r, :] = B[r, :] * k
    elif tipo == "elemento":
        B[r, _idx(A, j, "coluna")] = k
    elif tipo in {"trocar", "somar", "proporcional"}:
        s = _idx(A, j)
        if tipo == "trocar":
            B.row_swap(r, s)
        elif r == s and tipo == "proporcional":
            B[r, :] = B[r, :] * k
        elif tipo == "somar":
            if r == s:
                raise ValueError("Escolha duas linhas diferentes.")
            B[r, :] = B[r, :] + k * B[s, :]
        else:
            B[r, :] = k * B[s, :]
    else:
        raise ValueError(f"Modificação desconhecida: {tipo}")
    return B


def descricao(tipo: str, i: int, j: int, k) -> str:
    return {
        "trocar": f"L{i} ↔ L{j}",
        "escalar": f"L{i} ← ({k})·L{i}",
        "somar": f"L{i} ← L{i} + ({k})·L{j}",
        "proporcional": f"L{i} ← ({k})·L{j}",
        "zerar": f"L{i} ← 0",
        "elemento": f"a{i}{j} ← {k}",
        "transpor": "A → Aᵀ",
        "simetrizar": "A → (A + Aᵀ)/2",
    }[tipo]


@dataclass
class Resultado:
    antes: sp.Matrix
    depois: sp.Matrix
    props_antes: ms.Propriedades
    props_depois: ms.Propriedades
    mudancas: list[tuple[str, str, str, str]]
    observacoes: list[str]


def comparar(A: sp.Matrix, B: sp.Matrix) -> Resultado:
    pa, pb = ms.analisar(A), ms.analisar(B)
    obs: list[str] = []
    if pa.determinante is not None and pb.determinante is not None and not pa.simbolica:
        da, db = pa.determinante, pb.determinante
        if da != 0:
            obs.append(f"det(A′)/det(A) = {sp.nsimplify(db / da)}")
        elif db == 0:
            obs.append("O determinante era 0 e continua 0.")
        else:
            obs.append(f"O determinante saiu de 0 para {db}.")
    if pa.posto != pb.posto:
        obs.append(f"posto: {pa.posto} → {pb.posto}")
    return Resultado(A, B, pa, pb, ms.explicar_mudancas(pa, pb), obs)


# ----------------------------------------------------------------------
# Experimentos guiados
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Experimento:
    id: str
    titulo: str
    objetivo: str
    matriz: tuple[tuple[int, ...], ...]
    tipo: str
    i: int
    j: int
    k: int
    pergunta: str
    conclusao: str  # o que o experimento ilustra (confirmado pelo cálculo mostrado)


EXPERIMENTOS = [
    Experimento(
        "troca",
        "Trocar duas linhas",
        "Veja o que a troca de linhas faz com o determinante.",
        ((1, 2), (3, 4)),
        "trocar",
        1,
        2,
        1,
        "O que acontece com det(A) quando trocamos L1 e L2?",
        "Trocar duas linhas multiplica o determinante por −1 (o posto não muda).",
    ),
    Experimento(
        "escala",
        "Multiplicar uma linha por k",
        "Observe o efeito de escalar uma única linha.",
        ((2, 1, 0), (1, 3, 1), (0, 1, 4)),
        "escalar",
        2,
        1,
        3,
        "Se multiplicamos L2 por 3, por quanto fica multiplicado det(A)?",
        "Multiplicar uma linha por k multiplica o determinante por k.",
    ),
    Experimento(
        "soma",
        "Somar múltiplo de outra linha",
        "Esta operação do escalonamento preserva o quê?",
        ((1, 2, 3), (0, 1, 4), (5, 6, 0)),
        "somar",
        3,
        1,
        -2,
        "O que acontece com det(A) e com o posto quando fazemos L3 ← L3 − 2·L1?",
        "Somar um múltiplo de outra linha não altera o determinante nem o posto.",
    ),
    Experimento(
        "singular",
        "Tornar a matriz singular",
        "Faça uma linha depender de outra.",
        ((1, 2, 3), (4, 5, 6), (7, 8, 10)),
        "proporcional",
        3,
        1,
        2,
        "O que acontece quando L3 passa a ser o dobro de L1?",
        "Linhas proporcionais (dependentes) zeram o determinante e reduzem o posto: "
        "a matriz deixa de ser invertível.",
    ),
    Experimento(
        "zero",
        "Zerar uma linha",
        "O caso extremo de dependência linear.",
        ((2, 0, 1), (1, 3, 2), (0, 1, 1)),
        "zerar",
        2,
        1,
        1,
        "Qual o determinante depois de zerar L2?",
        "Uma linha nula torna o determinante 0 e diminui o posto.",
    ),
    Experimento(
        "transpor",
        "Transpor a matriz",
        "Quais propriedades sobrevivem à transposição?",
        ((1, 2, 3), (0, 4, 5), (1, 0, 6)),
        "transpor",
        1,
        1,
        1,
        "det, posto, traço e autovalores mudam ao transpor?",
        "A transposta tem o mesmo determinante, posto, traço e autovalores.",
    ),
    Experimento(
        "simetrizar",
        "Simetrizar",
        "Construa uma matriz simétrica a partir de uma qualquer.",
        ((1, 4, 2), (0, 3, 5), (6, 1, 2)),
        "simetrizar",
        1,
        1,
        1,
        "A matriz (A + Aᵀ)/2 é simétrica? E o traço?",
        "(A + Aᵀ)/2 é sempre simétrica e conserva o traço de A.",
    ),
]


def experimento_por_id(id_: str) -> Experimento:
    return next(e for e in EXPERIMENTOS if e.id == id_)


def executar_experimento(e: Experimento) -> Resultado:
    A = sp.Matrix(e.matriz)
    return comparar(A, modificar(A, e.tipo, e.i, e.j, e.k))
