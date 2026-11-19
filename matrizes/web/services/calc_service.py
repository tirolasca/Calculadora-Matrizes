"""Orquestra uma operação: valida parâmetro, chama o núcleo e (se houver) o passo a passo.

Sem Streamlit. É o único ponto da web que combina `nucleo` + `step_service`.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from matrizes import nucleo

from . import matrix_service as ms
from . import step_service as ss


@dataclass
class Execucao:
    operacao: nucleo.Operacao
    entradas: dict[str, sp.Matrix]
    resultado: list[tuple[str, object]]
    solucao: ss.Solucao | None = None
    aviso_passos: str = ""

    @property
    def titulo(self) -> str:
        return self.operacao.nome

    @property
    def latex_principal(self) -> str:
        from .step_service import latex_matriz

        for _, v in self.resultado:
            if isinstance(v, sp.MatrixBase):
                return latex_matriz(v)
            if isinstance(v, str):
                try:
                    return sp.latex(ms.expressao(v))
                except ValueError:
                    continue
        return ""

    @property
    def texto(self) -> str:
        return " | ".join(f"{r} {v}" if isinstance(v, str) else r for r, v in self.resultado)


def operacao_por_nome(nome: str) -> nucleo.Operacao:
    for o in nucleo.OPERACOES:
        if o.nome == nome:
            return o
    raise KeyError(nome)


def operacoes_do_grupo(*grupos: str) -> list[nucleo.Operacao]:
    return [o for o in nucleo.OPERACOES if o.grupo in grupos]


def ler_parametro(op: nucleo.Operacao, texto: str):
    if not op.param:
        return None
    try:
        v = ms.expressao(texto)
    except ValueError as e:
        raise ValueError(f"Valor de {op.param}: {e}") from e
    if op.param == "n":
        if not v.is_Integer:
            raise ValueError("O expoente n precisa ser um número inteiro.")
        v = int(v)
        if abs(v) > 50:
            raise ValueError("Use |n| ≤ 50.")
    return v


def executar(
    nome_op: str,
    mats: list[sp.Matrix],
    param_texto: str = "",
    *,
    com_passos: bool = True,
    metodo: str | None = None,
) -> Execucao:
    """Roda a operação. Lança ValueError (mensagem em português) em caso de erro de uso."""
    op = operacao_por_nome(nome_op)
    mats = list(mats[: op.nmat])
    if len(mats) < op.nmat:
        raise ValueError("Faltam matrizes para esta operação.")
    param = ler_parametro(op, param_texto)
    args = [*mats, param] if op.param else mats
    resultado = op.fn(*args)
    entradas = dict(zip("AB", mats, strict=False))
    ex = Execucao(op, entradas, resultado)
    if com_passos and ss.suporta(nome_op):
        try:
            ex.solucao = ss.passos_para(nome_op, mats, param, metodo)
        except ss.PassosIndisponiveis as e:
            ex.aviso_passos = str(e)
    return ex


def executar_sistema(A: sp.Matrix, b: sp.Matrix, metodo: str = "gauss"):
    """(tipo, linhas_de_texto, Solucao|None, aviso)."""
    if A.rows != b.rows or b.cols != 1:
        raise ValueError("b precisa ser uma coluna com uma linha por equação.")
    tipo, linhas = nucleo.relatorio_sistema(A, b, metodo)
    sol, aviso = None, ""
    try:
        sol = ss.passos_sistema(A, b, metodo)
    except ss.PassosIndisponiveis as e:
        aviso = str(e)
    except ValueError as e:  # método não se aplica (explicado em `linhas`)
        aviso = str(e)
    return tipo, linhas, sol, aviso
