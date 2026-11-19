"""Serviço de matrizes da interface web (Python puro, sem Streamlit).

Reúne tudo que não é cálculo básico (``nucleo``) nem apresentação:

* entrada segura de números e expressões simbólicas (sem ``eval``);
* matrizes predefinidas;
* memória de matrizes e histórico de operações (com exportação/importação em JSON);
* análise de propriedades e comparação "antes/depois" (laboratório);
* verificação experimental de propriedades algébricas (comutatividade etc.).
"""

from __future__ import annotations

import ast
import json
import random
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import sympy as sp

from ... import nucleo as core

# ----------------------------------------------------------------------
# Entrada segura: números e expressões simbólicas
# ----------------------------------------------------------------------
NOME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,15}$")
_SIMBOLO_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,3}$")
_FUNCOES = {
    "sqrt": sp.sqrt,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "exp": sp.exp,
    "log": sp.log,
    "ln": sp.log,
    "abs": sp.Abs,
}
_CONSTANTES = {"pi": sp.pi, "E": sp.E, "I": sp.I}
MAX_EXPRESSAO = 80  # caracteres
MAX_EXPOENTE = 12
MAX_DIGITOS = 30


class EntradaInvalida(ValueError):
    """Entrada de matriz inválida; ``erros`` lista uma mensagem por célula com problema."""

    def __init__(self, erros: Sequence[str]):
        self.erros = list(erros)
        super().__init__("; ".join(self.erros))


def _numero(valor: int | float) -> sp.Expr:
    if isinstance(valor, int):
        if len(str(abs(valor))) > MAX_DIGITOS:
            raise ValueError("número grande demais")
        return sp.Integer(valor)
    return sp.Rational(repr(valor))  # decimais ficam exatos: 0.1 -> 1/10


def _avaliar(no: ast.AST) -> sp.Expr:
    """Converte a árvore sintática em expressão sympy aceitando só um subconjunto seguro."""
    if isinstance(no, ast.Constant):
        if isinstance(no.value, bool) or not isinstance(no.value, int | float):
            raise ValueError("só números são permitidos")
        return _numero(no.value)
    if isinstance(no, ast.Name):
        if no.id in _CONSTANTES:
            return _CONSTANTES[no.id]
        if no.id in _FUNCOES:
            raise ValueError(f"'{no.id}' é uma função: use {no.id}(...)")
        if _SIMBOLO_RE.match(no.id):
            return sp.Symbol(no.id)
        raise ValueError(f"nome não permitido: '{no.id}'")
    if isinstance(no, ast.UnaryOp) and isinstance(no.op, ast.UAdd | ast.USub):
        v = _avaliar(no.operand)
        return v if isinstance(no.op, ast.UAdd) else -v
    if isinstance(no, ast.BinOp):
        a, b = _avaliar(no.left), _avaliar(no.right)
        if isinstance(no.op, ast.Add):
            return a + b
        if isinstance(no.op, ast.Sub):
            return a - b
        if isinstance(no.op, ast.Mult):
            return a * b
        if isinstance(no.op, ast.Div):
            if b == 0:
                raise ValueError("divisão por zero")
            return a / b
        if isinstance(no.op, ast.Pow):
            if not (b.is_number and b.is_real) or abs(b) > MAX_EXPOENTE:
                raise ValueError(f"expoente deve ser um número com |expoente| ≤ {MAX_EXPOENTE}")
            if a == 0 and b < 0:
                raise ValueError("divisão por zero")
            return a**b
        raise ValueError("operador não permitido")
    if isinstance(no, ast.Call):
        if not isinstance(no.func, ast.Name) or no.func.id not in _FUNCOES:
            raise ValueError("função não permitida (use sqrt, sin, cos, tan, exp, log, abs)")
        if len(no.args) != 1 or no.keywords:
            raise ValueError(f"{no.func.id}() recebe exatamente um argumento")
        return _FUNCOES[no.func.id](_avaliar(no.args[0]))
    raise ValueError("expressão não permitida")


def expressao(texto: str) -> sp.Expr:
    """Converte '3', '-2.5', '1/2', 'sqrt(2)', 'a+1', 'x^2' em expressão exata.

    Nunca usa ``eval``/``sympify``: a árvore sintática é percorrida por uma lista de
    construções permitidas. Lança ``ValueError`` com uma mensagem em português.
    """
    t = str(texto).strip()
    if not t:
        raise ValueError("célula vazia")
    if len(t) > MAX_EXPRESSAO:
        raise ValueError(f"expressão longa demais (máximo {MAX_EXPRESSAO} caracteres)")
    t = t.replace(",", ".").replace("^", "**").replace("π", "pi")
    t = re.sub(r"√\s*(\d+(?:\.\d+)?|[A-Za-z]\w*)", r"sqrt(\1)", t).replace("√", "sqrt")
    try:
        arvore = ast.parse(t, mode="eval")
    except (SyntaxError, ValueError):
        raise ValueError(
            f"expressão inválida: '{texto}' (para multiplicar use *, ex.: 2*x)"
        ) from None
    try:
        r = _avaliar(arvore.body)
    except RecursionError:
        raise ValueError("expressão complexa demais") from None
    if r.has(sp.zoo, sp.nan, sp.oo, -sp.oo):
        raise ValueError("resultado indefinido")
    return r


def matriz_de_texto(celulas: Sequence[Sequence[str]]) -> sp.Matrix:
    """Grade de textos → ``sympy.Matrix``. Lança ``EntradaInvalida`` com todos os erros."""
    if not celulas or not celulas[0]:
        raise EntradaInvalida(["Matriz vazia."])
    erros: list[str] = []
    linhas: list[list[sp.Expr]] = []
    for i, lin in enumerate(celulas):
        nova: list[sp.Expr] = []
        for j, t in enumerate(lin):
            try:
                nova.append(expressao(t))
            except ValueError as e:
                erros.append(f"Linha {i + 1}, coluna {j + 1}: {e}")
                nova.append(sp.Integer(0))
        linhas.append(nova)
    if erros:
        raise EntradaInvalida(erros)
    return sp.Matrix(linhas)


def matriz_para_texto(M: sp.Matrix) -> list[list[str]]:
    return [[str(M[i, j]) for j in range(M.cols)] for i in range(M.rows)]


def nome_valido(nome: str) -> bool:
    return bool(NOME_RE.match(nome))


# ----------------------------------------------------------------------
# Matrizes predefinidas
# ----------------------------------------------------------------------
def _fabrica(f):
    return lambda m, n, semente=0: sp.Matrix(m, n, f)


def _aleatoria(m: int, n: int, semente: int = 0, limite: int = 9) -> sp.Matrix:
    rng = random.Random(semente)
    return sp.Matrix(m, n, lambda i, j: rng.randint(-limite, limite))


PREDEFINIDAS = {
    "Identidade": ("1 na diagonal, 0 fora dela", _fabrica(lambda i, j: 1 if i == j else 0)),
    "Nula": ("todos os elementos iguais a 0", _fabrica(lambda i, j: 0)),
    "Diagonal (1, 2, 3, …)": (
        "só a diagonal é não nula",
        _fabrica(lambda i, j: i + 1 if i == j else 0),
    ),
    "Triangular superior": (
        "zeros abaixo da diagonal",
        _fabrica(lambda i, j: i + j + 1 if j >= i else 0),
    ),
    "Triangular inferior": (
        "zeros acima da diagonal",
        _fabrica(lambda i, j: i + j + 1 if j <= i else 0),
    ),
    "Simétrica": ("A = Aᵀ", _fabrica(lambda i, j: (i + 1) * (j + 1) + abs(i - j))),
    "Antissimétrica": ("Aᵀ = −A (diagonal nula)", _fabrica(lambda i, j: (j - i) * (i + j + 1))),
    "Tridiagonal (2 e 1)": (
        "2 na diagonal e 1 ao lado; invertível",
        _fabrica(lambda i, j: 2 if i == j else (1 if abs(i - j) == 1 else 0)),
    ),
    "Singular (linhas proporcionais)": (
        "posto 1: não é invertível",
        _fabrica(lambda i, j: (i + 1) * (j + 1)),
    ),
    "Hilbert": (
        "aᵢⱼ = 1/(i+j−1): frações exatas",
        _fabrica(lambda i, j: sp.Rational(1, i + j + 1)),
    ),
    "Aleatória (inteiros de −9 a 9)": ("sorteio com semente fixa", _aleatoria),
}


def nomes_predefinidas() -> list[str]:
    return list(PREDEFINIDAS)


def predefinida(nome: str, m: int, n: int | None = None, semente: int = 0) -> sp.Matrix:
    if nome not in PREDEFINIDAS:
        raise KeyError(nome)
    return PREDEFINIDAS[nome][1](m, m if n is None else n, semente)


# ----------------------------------------------------------------------
# Memória de matrizes
# ----------------------------------------------------------------------
@dataclass
class Memoria:
    """Matrizes salvas pelo usuário, por nome."""

    matrizes: dict[str, sp.Matrix] = field(default_factory=dict)

    def nomes(self) -> list[str]:
        return list(self.matrizes)

    def __contains__(self, nome: object) -> bool:
        return nome in self.matrizes

    def __len__(self) -> int:
        return len(self.matrizes)

    def proximo_nome(self) -> str:
        for letra in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if letra not in self.matrizes:
                return letra
        i = 1
        while f"M{i}" in self.matrizes:
            i += 1
        return f"M{i}"

    def salvar(self, nome: str, M: sp.Matrix, *, sobrescrever: bool = True) -> str:
        nome = nome.strip()
        if not nome_valido(nome):
            raise ValueError(
                "Nome inválido: use letras, números e _ (começando por letra, até 16 caracteres)."
            )
        if nome in self.matrizes and not sobrescrever:
            raise ValueError(f"Já existe uma matriz chamada '{nome}'.")
        self.matrizes[nome] = sp.Matrix(M)
        return nome

    def obter(self, nome: str) -> sp.Matrix:
        if nome not in self.matrizes:
            raise KeyError(nome)
        return self.matrizes[nome]

    def renomear(self, antigo: str, novo: str) -> str:
        if antigo not in self.matrizes:
            raise KeyError(antigo)
        novo = novo.strip()
        if novo == antigo:
            return novo
        if not nome_valido(novo):
            raise ValueError(
                "Nome inválido: use letras, números e _ (começando por letra, até 16 caracteres)."
            )
        if novo in self.matrizes:
            raise ValueError(f"Já existe uma matriz chamada '{novo}'.")
        # preserva a ordem de inserção
        self.matrizes = {(novo if k == antigo else k): v for k, v in self.matrizes.items()}
        return novo

    def duplicar(self, nome: str, novo: str | None = None) -> str:
        if nome not in self.matrizes:
            raise KeyError(nome)
        if novo is None:
            novo, i = f"{nome}_copia", 2
            while novo in self.matrizes:
                novo, i = f"{nome}_copia{i}", i + 1
        return self.salvar(novo, self.matrizes[nome], sobrescrever=False)

    def excluir(self, nome: str) -> None:
        if nome not in self.matrizes:
            raise KeyError(nome)
        del self.matrizes[nome]

    def para_dict(self) -> dict[str, list[list[str]]]:
        return {k: matriz_para_texto(v) for k, v in self.matrizes.items()}

    def carregar_dict(self, dados: dict[str, Any], *, substituir: bool = False) -> int:
        """Importa matrizes de um dict {nome: [[...]]}. Retorna quantas foram importadas."""
        novas = {}
        for nome, grade in dados.items():
            if not nome_valido(str(nome)):
                raise ValueError(f"Nome inválido no arquivo: '{nome}'.")
            novas[str(nome)] = matriz_de_texto([[str(c) for c in lin] for lin in grade])
        if substituir:
            self.matrizes = {}
        self.matrizes.update(novas)
        return len(novas)

    def exportar_json(self) -> str:
        return json.dumps({"versao": 1, "matrizes": self.para_dict()}, ensure_ascii=False, indent=2)

    def importar_json(self, texto: str, *, substituir: bool = False) -> int:
        try:
            dados = json.loads(texto)
            return self.carregar_dict(dados["matrizes"], substituir=substituir)
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
            raise ValueError(
                "Arquivo inválido: esperado um JSON exportado por esta calculadora."
            ) from None


# ----------------------------------------------------------------------
# Histórico de operações
# ----------------------------------------------------------------------
@dataclass
class Registro:
    quando: str
    categoria: str  # "Operação", "Sistema", "Laboratório", ...
    titulo: str
    entradas: dict[str, sp.Matrix]
    latex: str = ""  # resultado em LaTeX (para reexibir)
    texto: str = ""  # resultado em texto simples
    ok: bool = True


@dataclass
class Historico:
    limite: int = 200
    itens: list[Registro] = field(default_factory=list)

    def adicionar(
        self,
        categoria: str,
        titulo: str,
        entradas: dict[str, sp.Matrix] | None = None,
        latex: str = "",
        texto: str = "",
        ok: bool = True,
    ) -> Registro:
        reg = Registro(
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            categoria,
            titulo,
            {k: sp.Matrix(v) for k, v in (entradas or {}).items()},
            latex,
            texto,
            ok,
        )
        self.itens.append(reg)
        if len(self.itens) > self.limite:
            del self.itens[: len(self.itens) - self.limite]
        return reg

    def recentes(self, n: int = 5) -> list[Registro]:
        return list(reversed(self.itens[-n:]))

    def limpar(self) -> None:
        self.itens.clear()

    def __len__(self) -> int:
        return len(self.itens)


# ----------------------------------------------------------------------
# Análise de propriedades (laboratório)
# ----------------------------------------------------------------------
@dataclass
class Propriedades:
    linhas: int
    colunas: int
    quadrada: bool
    simbolica: bool
    determinante: sp.Expr | None
    posto: int
    traco: sp.Expr | None
    invertivel: bool | None
    estrutura: dict[str, bool | None]
    autovalores: list[tuple[complex, int]] | None  # aproximados, com multiplicidade
    autovalores_exatos: dict[sp.Expr, int] | None  # só quando curtos
    dim_autoespacos: int | None  # soma das dimensões dos autoespaços (autovetores independentes)


LIMITE_AUTOVALORES = 6  # acima disso só aproximações numéricas, sem forma exata


def _autovalores_numericos(A: sp.Matrix) -> list[complex]:
    import mpmath

    mpmath.mp.dps = 30
    vals = mpmath.eig(mpmath.matrix(A.evalf(30).tolist()), left=False, right=False)
    return [complex(v) for v in vals]


def _agrupar(vals: list[complex], tol: float = 1e-6) -> list[tuple[complex, int]]:
    grupos: list[list[complex]] = []
    for v in sorted(vals, key=lambda z: (round(z.real, 6), round(z.imag, 6))):
        for g in grupos:
            if abs(g[0] - v) < tol:
                g.append(v)
                break
        else:
            grupos.append([v])
    return [(sum(g) / len(g), len(g)) for g in grupos]


def analisar(A: sp.Matrix) -> Propriedades:
    """Propriedades efetivamente calculadas (nada é presumido)."""
    quad = A.is_square
    simb = core.tem_simbolos(A)
    est = core.estrutura(A)
    det = A.det() if quad else None
    traco = A.trace() if quad else None
    autovals = exatos = None
    dim_auto = None
    if quad and not simb and A.rows <= LIMITE_AUTOVALORES:
        autovals = _agrupar(_autovalores_numericos(A))
        if A.rows <= 3:
            ev = A.eigenvals()
            if all(len(str(v)) <= 30 for v in ev):
                exatos = dict(ev)
            try:
                dim_auto = sum(len(v) for _, _, v in A.eigenvects())
            except Exception:
                dim_auto = None
    elif quad and simb and A.rows <= 3:
        try:
            exatos = dict(A.eigenvals())
        except Exception:
            exatos = None
    return Propriedades(
        A.rows,
        A.cols,
        quad,
        simb,
        det,
        A.rank(),
        traco,
        est.get("invertivel"),
        est,
        autovals,
        exatos,
        dim_auto,
    )


def _fmt_complexo(z: complex, casas: int = 4) -> str:
    if abs(z.imag) < 1e-9:
        return f"{z.real:.{casas}g}"
    return f"{z.real:.{casas}g} {'+' if z.imag >= 0 else '−'} {abs(z.imag):.{casas}g}i"


def resumo_autovalores(p: Propriedades) -> str:
    if p.autovalores is None:
        return "—"
    return ", ".join(
        f"{_fmt_complexo(z)}" + (f" (×{m})" if m > 1 else "") for z, m in p.autovalores
    )


def tabela_propriedades(p: Propriedades) -> dict[str, str]:
    """Propriedades como {rótulo: texto}, na ordem de exibição."""
    sn = {True: "sim", False: "não", None: "depende dos símbolos"}
    t = {
        "Dimensão": f"{p.linhas}×{p.colunas}",
        "Determinante": str(p.determinante) if p.determinante is not None else "—",
        "Posto": str(p.posto),
        "Traço": str(p.traco) if p.traco is not None else "—",
        "Invertível": sn[p.invertivel] if p.quadrada else "— (não quadrada)",
        "Simétrica": sn[p.estrutura.get("simetrica")] if p.quadrada else "—",
        "Antissimétrica": sn[p.estrutura.get("antissimetrica")] if p.quadrada else "—",
        "Autovalores": resumo_autovalores(p)
        if p.autovalores is not None
        else (
            ", ".join(
                f"{k}" + (f" (×{m})" if m > 1 else "") for k, m in p.autovalores_exatos.items()
            )
            if p.autovalores_exatos
            else "—"
        ),
        "Autovetores independentes": str(p.dim_autoespacos)
        if p.dim_autoespacos is not None
        else "—",
    }
    if p.quadrada:
        for chave in (
            "diagonal",
            "triangular_superior",
            "triangular_inferior",
            "ortogonal",
            "idempotente",
        ):
            t[core.ROTULOS_ESTRUTURA[chave]] = sn[p.estrutura.get(chave)]
    return t


def _igual_num(a: Any, b: Any) -> bool:
    if a is None or b is None:
        return a is b
    try:
        return bool(sp.simplify(a - b) == 0)
    except Exception:
        return a == b


def explicar_mudancas(antes: Propriedades, depois: Propriedades) -> list[tuple[str, str, str, str]]:
    """Compara duas análises. Retorna [(propriedade, antes, depois, explicação)] só do que mudou.

    As explicações usam apenas fatos calculados; se nada mudou, a lista vem vazia.
    """
    ta, td = tabela_propriedades(antes), tabela_propriedades(depois)
    saida = []
    explicacoes = {
        "Determinante": lambda: (
            "O determinante virou 0: a matriz deixou de ser invertível e as linhas (e colunas) passaram a ser linearmente dependentes."
            if depois.determinante == 0 and antes.determinante != 0
            else "O determinante deixou de ser 0: a matriz passou a ser invertível."
            if antes.determinante == 0 and depois.determinante != 0
            else "O determinante é o fator de escala de área/volume da transformação; o sinal indica se a orientação se inverte."
        ),
        "Posto": lambda: (
            "O posto diminuiu: há menos linhas independentes; o espaço gerado pelas colunas encolheu."
            if depois.posto < antes.posto
            else "O posto aumentou: surgiu uma nova direção independente."
        ),
        "Traço": lambda: (
            "O traço é a soma da diagonal e também a soma dos autovalores (contando multiplicidades)."
        ),
        "Invertível": lambda: (
            "A invertibilidade mudou junto com o determinante e o posto (invertível ⇔ det ≠ 0 ⇔ posto completo)."
        ),
        "Autovalores": lambda: (
            "Os autovalores mudaram: as direções invariantes e seus fatores de escala são outros."
        ),
        "Autovetores independentes": lambda: (
            "Mudou a quantidade de autovetores independentes; isso decide se a matriz é diagonalizável."
        ),
        "Simétrica": lambda: (
            "Simétrica significa A = Aᵀ; qualquer alteração fora da diagonal precisa ser espelhada para preservá-la."
        ),
        "Antissimétrica": lambda: "Antissimétrica significa Aᵀ = −A (diagonal nula).",
    }
    for chave in ta:
        if chave in td and ta[chave] != td[chave]:
            f = explicacoes.get(chave)
            saida.append(
                (chave, ta[chave], td[chave], f() if f else "Característica estrutural alterada.")
            )
    return saida


# ----------------------------------------------------------------------
# Comparação de matrizes e estatísticas
# ----------------------------------------------------------------------
@dataclass
class Comparacao:
    mesma_dimensao: bool
    iguais: bool | None
    diferenca: sp.Matrix | None
    posicoes_diferentes: list[tuple[int, int]]
    maior_diferenca: float | None
    multiplo: sp.Expr | None  # k tal que A = k·B (se existir)
    uma_e_transposta_da_outra: bool


def comparar_matrizes(A: sp.Matrix, B: sp.Matrix) -> Comparacao:
    transp = A.shape == B.T.shape and _zero(A - B.T)
    if A.shape != B.shape:
        return Comparacao(False, None, None, [], None, None, bool(transp))
    D = (A - B).applyfunc(sp.simplify)
    pos = [(i, j) for i in range(D.rows) for j in range(D.cols) if D[i, j] != 0]
    maior = None
    if not core.tem_simbolos(D):
        maior = max(
            (abs(float(D[i, j])) for i in range(D.rows) for j in range(D.cols)), default=0.0
        )
    k = None
    for i in range(B.rows):
        for j in range(B.cols):
            if B[i, j] != 0:
                k = sp.simplify(A[i, j] / B[i, j])
                break
        if k is not None:
            break
    if k is not None and not _zero(A - k * B):
        k = None
    if k is None and _zero(B):
        k = None
    return Comparacao(not pos, not pos, D, pos, maior, k, bool(transp))


def _zero(M: sp.Matrix) -> bool:
    return core._zero(M) is True


def valores_numericos(M: sp.Matrix) -> list[float]:
    """Elementos como floats (levanta ValueError se houver símbolos ou números complexos)."""
    if core.tem_simbolos(M):
        raise ValueError("A matriz tem símbolos: não é possível obter valores numéricos.")
    out = []
    for x in M:
        c = complex(sp.N(x))
        if abs(c.imag) > 1e-12:
            raise ValueError("A matriz tem elementos complexos.")
        out.append(c.real)
    return out


@dataclass
class Estatisticas:
    minimo: float
    maximo: float
    media: float
    soma: float
    zeros: int
    total: int
    norma_frobenius: float


def estatisticas(M: sp.Matrix) -> Estatisticas:
    v = valores_numericos(M)
    return Estatisticas(
        min(v),
        max(v),
        sum(v) / len(v),
        sum(v),
        sum(1 for x in v if abs(x) < 1e-12),
        len(v),
        sum(x * x for x in v) ** 0.5,
    )


# ----------------------------------------------------------------------
# Verificação experimental de propriedades algébricas
# ----------------------------------------------------------------------
@dataclass
class Verificacao:
    chave: str
    nome: str
    enunciado: str  # LaTeX da identidade testada
    esquerda: Any  # Matrix ou escalar
    direita: Any
    rotulo_esq: str
    rotulo_dir: str
    igual: bool
    vale_em_geral: bool  # a propriedade é um teorema para quaisquer matrizes compatíveis?
    comentario: str


def _eq(x: Any, y: Any) -> bool:
    if isinstance(x, sp.MatrixBase):
        return x.shape == y.shape and (
            _zero(x - y) or bool((x - y).applyfunc(sp.simplify).is_zero_matrix)
        )
    return _igual_num(x, y)


def _exigir(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def verificar_comutatividade(A: sp.Matrix, B: sp.Matrix) -> Verificacao:
    _exigir(
        A.cols == B.rows and B.cols == A.rows, "AB e BA só existem juntas se A é m×n e B é n×m."
    )
    ab, ba = A * B, B * A
    igual = ab.shape == ba.shape and _eq(ab, ba)
    return Verificacao(
        "comutatividade", "Comutatividade", r"AB = BA", ab, ba, "AB", "BA", igual, False,
        "Neste caso AB = BA, mas isso é coincidência: em geral AB ≠ BA." if igual
        else "AB ≠ BA: a multiplicação de matrizes não é comutativa.",
    )  # fmt: skip


def verificar_associatividade(A: sp.Matrix, B: sp.Matrix, C: sp.Matrix) -> Verificacao:
    _exigir(A.cols == B.rows and B.cols == C.rows, "Precisa de A (m×n), B (n×p) e C (p×q).")
    e, d = (A * B) * C, A * (B * C)
    return Verificacao(
        "associatividade", "Associatividade", r"(AB)C = A(BC)", e, d, "(AB)C", "A(BC)", _eq(e, d), True,
        "Vale sempre que os produtos existem: a multiplicação é associativa.",
    )  # fmt: skip


def verificar_distributividade(A: sp.Matrix, B: sp.Matrix, C: sp.Matrix) -> Verificacao:
    _exigir(
        B.shape == C.shape and A.cols == B.rows,
        "Precisa de B e C com a mesma dimensão e A com tantas colunas quanto B tem linhas.",
    )
    e, d = A * (B + C), A * B + A * C
    return Verificacao(
        "distributividade", "Distributividade", r"A(B+C) = AB + AC", e, d, "A(B+C)", "AB + AC", _eq(e, d), True,
        "Vale sempre: a multiplicação distribui sobre a soma.",
    )  # fmt: skip


def verificar_transposta_produto(A: sp.Matrix, B: sp.Matrix) -> Verificacao:
    _exigir(A.cols == B.rows, "Precisa de A (m×n) e B (n×p).")
    e, d = (A * B).T, B.T * A.T
    return Verificacao(
        "transposta_produto", "Transposta do produto", r"(AB)^T = B^T A^T", e, d, "(AB)ᵀ", "BᵀAᵀ", _eq(e, d), True,
        "Vale sempre, e note que a ordem dos fatores se inverte (não é AᵀBᵀ).",
    )  # fmt: skip


def verificar_det_produto(A: sp.Matrix, B: sp.Matrix) -> Verificacao:
    _exigir(
        A.is_square and B.shape == A.shape, "Precisa de duas matrizes quadradas de mesma ordem."
    )
    e, d = (A * B).det(), A.det() * B.det()
    return Verificacao(
        "det_produto", "Determinante do produto", r"\det(AB) = \det(A)\,\det(B)", e, d, "det(AB)", "det(A)·det(B)",
        _eq(e, d), True,
        "Vale sempre para matrizes quadradas de mesma ordem. Já det(A + B) ≠ det(A) + det(B) em geral.",
    )  # fmt: skip


def verificar_inversa(A: sp.Matrix) -> Verificacao:
    _exigir(A.is_square, "A inversa só existe para matrizes quadradas.")
    _exigir(A.det() != 0, "A é singular (det = 0): não tem inversa.")
    e, d = A * A.inv(), sp.eye(A.rows)
    return Verificacao(
        "inversa", "Inversa e identidade", r"A\,A^{-1} = I", e, d, "A·A⁻¹", "I", _eq(e, d), True,
        "Toda matriz invertível satisfaz A·A⁻¹ = A⁻¹·A = I.",
    )  # fmt: skip
