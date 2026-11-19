"""Núcleo de cálculo: matrizes e sistemas lineares (sem entrada/saída).

Tudo aqui é função pura sobre ``sympy.Matrix``, com aritmética exata (frações).
É usado tanto pelo terminal (``cli.py``) quanto pela janela (``gui.py``).
"""

import re
from collections import namedtuple

import sympy as sp

try:
    from matplotlib.figure import Figure

    MPL = True
except ImportError:  # gráfico é opcional
    MPL = False


def numero(txt):
    """Converte '3', '-2.5' ou '1/2' em número exato (sem eval)."""
    return sp.Rational(str(txt).strip().replace(",", "."))


def matriz_texto(M):
    """Matriz como texto alinhado."""
    if M.rows * M.cols == 0:
        return "  []"
    larg = max(len(str(x)) for x in M)
    return "\n".join(
        "  [ " + "  ".join(str(M[i, j]).rjust(larg) for j in range(M.cols)) + " ]"
        for i in range(M.rows)
    )


def parse_matriz_colchetes(txt):
    """Aceita '[[1,2],[3,4]]' (com frações: [[1/2,3]]) ou '1 2; 3 4'.

    Lança ValueError se inválido. Nunca executa o texto digitado.
    """
    txt = txt.strip()
    try:
        if txt.startswith("["):
            if not re.fullmatch(r"\[\s*(\[[^\[\]]*\]\s*,?\s*)+\]|\[[^\[\]]*\]", txt):
                raise ValueError("colchetes mal formados")
            linhas = re.findall(r"\[([^\[\]]*)\]", txt)
            dados = [[numero(x) for x in re.split(r"[,\s]+", l.strip()) if x] for l in linhas]
        else:
            dados = [[numero(x) for x in l.split()] for l in txt.split(";")]
        M = sp.Matrix(dados)
    except Exception as e:
        raise ValueError("Formato inválido. Ex.: [[1,2],[3,4]] ou 1 2; 3 4") from e
    if M.rows == 0 or M.cols == 0:
        raise ValueError("Matriz vazia.")
    return M


def _quadrada(A, o_que):
    if not A.is_square:
        raise ValueError(f"{o_que}: a matriz precisa ser quadrada.")


# Cada operação devolve uma lista de (rótulo, valor); valor é Matrix ou str.
# Erros de uso lançam ValueError com mensagem em português.
def f_soma(A, B):
    if A.shape != B.shape:
        raise ValueError("As matrizes precisam ter as mesmas dimensões.")
    return [("A + B", A + B)]


def f_subtracao(A, B):
    if A.shape != B.shape:
        raise ValueError("As matrizes precisam ter as mesmas dimensões.")
    return [("A - B", A - B)]


def f_multiplicacao(A, B):
    if A.cols != B.rows:
        raise ValueError(f"Colunas de A ({A.cols}) ≠ linhas de B ({B.rows}).")
    return [("A × B", A * B)]


def f_escalar(A, k):
    return [(f"{k} × A", A * k)]


def f_potencia(A, n):
    _quadrada(A, "Potência")
    if n < 0 and A.det() == 0:
        raise ValueError("Matriz singular: não existe potência negativa.")
    return [(f"A^{n}", A**n)]


def f_transposta(A):
    return [("Aᵀ", A.T)]


def f_inversa(A):
    _quadrada(A, "Inversa")
    if A.det() == 0:
        raise ValueError("Determinante = 0: a matriz não possui inversa.")
    return [("A⁻¹", A.inv())]


def f_determinante(A):
    _quadrada(A, "Determinante")
    return [("det(A) =", str(A.det()))]


def f_posto(A):
    return [("posto(A) =", str(A.rank()))]


def f_traco(A):
    _quadrada(A, "Traço")
    return [("tr(A) =", str(A.trace()))]


def f_escalonar(A):
    R, pivos = A.rref()
    return [
        ("Forma escalonada reduzida (RREF)", R),
        ("Colunas pivô:", str([p + 1 for p in pivos])),
    ]


def _aprox(x, digitos=6):
    """Valor numérico; descarta parte imaginária desprezível. Símbolos ficam como estão."""
    if getattr(x, "free_symbols", None):
        return x
    re, im = sp.N(x, 20).as_real_imag()
    if abs(im) < 1e-12:
        return sp.Float(re, digitos)
    return sp.Float(re, digitos) + sp.Float(im, digitos) * sp.I


def f_autovalores(A):
    _quadrada(A, "Autovalores")
    res = [("Polinômio característico:", str(A.charpoly().as_expr()))]
    aproximado = False
    for val, mult, vetores in A.eigenvects():
        # raízes exatas muito longas (equações de grau 3+) são mostradas aproximadas
        longo = not A.free_symbols and (
            len(str(val)) > 30 or any(len(str(x)) > 30 for v in vetores for x in v)
        )
        if longo:
            aproximado = True
            res.append((f"λ ≈ {_aprox(val)}", f"(multiplicidade {mult})"))
        else:
            aprox = "" if val.free_symbols else f", ≈ {sp.N(val, 6)}"
            res.append((f"λ = {val}", f"(multiplicidade {mult}{aprox})"))
        for v in vetores:
            res.append(("  autovetor", v.applyfunc(_aprox) if longo else v))
    if aproximado:
        res.append(("Obs.:", "autovalores com expressão muito longa foram aproximados."))
    return res


def f_lu(A):
    _quadrada(A, "Decomposição LU")
    try:
        L, U, perm = A.LUdecomposition()
    except Exception as e:
        raise ValueError("Não foi possível decompor esta matriz.") from e
    res = [("L", L), ("U", U)]
    if perm:
        res.append(("Trocas de linhas (pivoteamento):", str(perm)))
    else:
        res.append(("Verificação:", "L×U = A ✓" if L * U == A else "L×U ≠ A"))
    return res


# ----------------------------------------------------------------------
# Estrutura, adjunta e outras decomposições
# ----------------------------------------------------------------------
def tem_simbolos(M):
    """True se a matriz tem parâmetros simbólicos (ex.: a, b, x)."""
    return bool(M.free_symbols)


def _zero(M):
    """A matriz é identicamente nula? True / False / None (indeterminado com símbolos)."""
    z = M.applyfunc(sp.expand).is_zero_matrix
    if z is None:
        z = M.applyfunc(sp.simplify).is_zero_matrix
    return z


def _igual(X, Y):
    """X == Y? True / False / None. Sem símbolos, confere também numericamente."""
    z = _zero(X - Y)
    if z is None and not (X.free_symbols or Y.free_symbols):
        z = all(abs(sp.N(d, 30)) < 1e-12 for d in X - Y)
    return z


def _e(*valores):
    """E lógico de três valores (True / False / None)."""
    if any(v is False for v in valores):
        return False
    if any(v is None for v in valores):
        return None
    return True


def _sim_nao(v):
    return {True: "sim", False: "não"}.get(v, "depende dos valores simbólicos")


ROTULOS_ESTRUTURA = {
    "quadrada": "Quadrada",
    "nula": "Nula",
    "identidade": "Identidade",
    "diagonal": "Diagonal",
    "triangular_superior": "Triangular superior",
    "triangular_inferior": "Triangular inferior",
    "simetrica": "Simétrica",
    "antissimetrica": "Antissimétrica",
    "ortogonal": "Ortogonal (AᵀA = I)",
    "idempotente": "Idempotente (A² = A)",
    "invertivel": "Invertível",
}


def estrutura(A):
    """Classificação estrutural: dict de True / False / None (None = depende de símbolos).

    Para matrizes não quadradas só ``quadrada`` e ``nula`` fazem sentido.
    """
    r = {"quadrada": A.is_square, "nula": _zero(A)}
    if not A.is_square:
        return r
    n = A.rows
    ident = sp.eye(n)
    acima = sp.Matrix(n, n, lambda i, j: A[i, j] if j > i else 0)
    abaixo = sp.Matrix(n, n, lambda i, j: A[i, j] if j < i else 0)
    tri_sup, tri_inf = _zero(abaixo), _zero(acima)
    r["identidade"] = _zero(A - ident)
    r["diagonal"] = _e(tri_sup, tri_inf)
    r["triangular_superior"] = tri_sup
    r["triangular_inferior"] = tri_inf
    r["simetrica"] = _zero(A - A.T)
    r["antissimetrica"] = _zero(A + A.T)
    r["ortogonal"] = _zero(A.T * A - ident)
    r["idempotente"] = _zero(A * A - A)
    d = A.det()
    zero_d = d.is_zero if d.is_zero is not None else (True if sp.simplify(d) == 0 else None)
    r["invertivel"] = None if zero_d is None else not zero_d
    return r


def f_estrutura(A):
    res = [("Dimensões:", f"{A.rows}×{A.cols}")]
    for chave, valor in estrutura(A).items():
        res.append((f"{ROTULOS_ESTRUTURA[chave]}:", _sim_nao(valor)))
    return res


def f_adjunta(A):
    _quadrada(A, "Adjunta")
    adj = A.adjugate()
    ok = _igual(A * adj, A.det() * sp.eye(A.rows)) is True
    return [
        ("adj(A)", adj),
        ("Verificação:", "A·adj(A) = det(A)·I ✓" if ok else "A·adj(A) ≠ det(A)·I"),
    ]


def f_cofatores(A):
    _quadrada(A, "Cofatores")
    return [("Matriz de cofatores", A.cofactor_matrix())]


def f_partes_triangulares(A):
    """A = L + D + U (estritamente inferior, diagonal, estritamente superior)."""
    m, n = A.shape
    L = sp.Matrix(m, n, lambda i, j: A[i, j] if j < i else 0)
    D = sp.Matrix(m, n, lambda i, j: A[i, j] if i == j else 0)
    U = sp.Matrix(m, n, lambda i, j: A[i, j] if j > i else 0)
    return [
        ("L (estritamente inferior)", L),
        ("D (diagonal)", D),
        ("U (estritamente superior)", U),
        ("Verificação:", "L + D + U = A ✓" if L + D + U == A else "L + D + U ≠ A"),
    ]


def f_partes_simetrica(A):
    """A = S + K, com S = (A + Aᵀ)/2 simétrica e K = (A - Aᵀ)/2 antissimétrica."""
    _quadrada(A, "Decomposição simétrica/antissimétrica")
    S, K = (A + A.T) / 2, (A - A.T) / 2
    return [
        ("S = (A + Aᵀ)/2  (simétrica)", S),
        ("K = (A - Aᵀ)/2  (antissimétrica)", K),
        ("Verificação:", "S + K = A ✓" if _zero(S + K - A) else "S + K ≠ A"),
    ]


def f_qr(A):
    if A.rows < A.cols:
        raise ValueError("QR: o nº de linhas deve ser maior ou igual ao nº de colunas.")
    if A.rank() < A.cols:
        raise ValueError("QR: as colunas de A precisam ser linearmente independentes.")
    try:
        Q, R = A.QRdecomposition()
    except Exception as e:
        raise ValueError("QR: as colunas de A precisam ser linearmente independentes.") from e
    ortog = _igual(Q.T * Q, sp.eye(Q.cols)) is True
    return [
        ("Q (colunas ortonormais)", Q),
        ("R (triangular superior)", R),
        ("Verificação:", "Q·R = A ✓" if _igual(Q * R, A) is True else "Q·R ≠ A"),
        ("Ortonormalidade:", "QᵀQ = I ✓" if ortog else "QᵀQ ≠ I"),
    ]


def f_cholesky(A):
    _quadrada(A, "Cholesky")
    if _zero(A - A.T) is False:
        raise ValueError("Cholesky: a matriz precisa ser simétrica.")
    if A.is_positive_definite is False:
        raise ValueError("Cholesky: a matriz precisa ser definida positiva.")
    try:
        L = A.cholesky()
    except Exception as e:
        raise ValueError("Cholesky: a matriz precisa ser simétrica e definida positiva.") from e
    return [
        ("L (triangular inferior)", L),
        ("Lᵀ", L.T),
        ("Verificação:", "L·Lᵀ = A ✓" if _igual(L * L.T, A) is True else "L·Lᵀ ≠ A"),
    ]


def _de_mp(x):
    """Número mpmath → Float/complexo do sympy."""
    if hasattr(x, "imag") and abs(x.imag) > 1e-12:
        return sp.Float(x.real, 12) + sp.Float(x.imag, 12) * sp.I
    return sp.Float(getattr(x, "real", x), 12)


def _diagonalizar_numerico(A):
    """Para autovalores irracionais de grau ≥ 3, a forma exata é inviável: usa mpmath."""
    import mpmath

    mpmath.mp.dps = 30
    E, ER = mpmath.eig(mpmath.matrix(A.evalf(30).tolist()))
    P = sp.Matrix(ER.rows, ER.cols, lambda i, j: _de_mp(ER[i, j]))
    D = sp.diag(*[_de_mp(e) for e in E])
    erro = max(abs(sp.N(x, 15)) for x in (P * D * P.inv() - A.evalf(15)))
    return P, D, erro


def f_diagonalizacao(A):
    _quadrada(A, "Diagonalização")
    longo = not A.free_symbols and any(len(str(v)) > 30 for v in A.eigenvals())
    if longo:
        P, D, erro = _diagonalizar_numerico(A)
        return [
            ("P (autovetores nas colunas, aproximado)", P),
            ("D (autovalores na diagonal, aproximado)", D),
            (
                "Verificação:",
                f"A ≈ P·D·P⁻¹ ✓ (erro máximo ≈ {erro:.1e})" if erro < 1e-8 else "A ≉ P·D·P⁻¹",
            ),
            ("Obs.:", "autovalores irracionais (raízes de grau ≥ 3): resultado numérico."),
        ]
    try:
        P, D = A.diagonalize()
    except Exception as e:
        raise ValueError("A matriz não é diagonalizável (faltam autovetores independentes).") from e
    return [
        ("P (autovetores nas colunas)", P),
        ("D (autovalores na diagonal)", D),
        ("Verificação:", "A = P·D·P⁻¹ ✓" if _igual(P * D * P.inv(), A) is True else "A ≠ P·D·P⁻¹"),
    ]


# Geradores (não dependem de uma matriz existente): usados pelas matrizes predefinidas da web.
def matriz_identidade(n):
    return sp.eye(n)


def matriz_nula(m, n=None):
    return sp.zeros(m, m if n is None else n)


def matriz_diagonal(valores):
    return sp.diag(*valores)


# ----------------------------------------------------------------------
# Sistemas lineares
# ----------------------------------------------------------------------
METODOS = {
    "gauss": "Escalonamento (Gauss-Jordan)",
    "cramer": "Regra de Cramer",
    "inversa": "Matriz inversa (x = A⁻¹·b)",
}


def classificar(A, b):
    """Teorema de Rouché-Capelli → (tipo, posto A, posto [A|b], nº incógnitas)."""
    rA, rAug, n = A.rank(), A.row_join(b).rank(), A.cols
    if rA != rAug:
        return "SI", rA, rAug, n
    return ("SPD" if rA == n else "SPI"), rA, rAug, n


def _checar_quadrado_regular(A, nome):
    if not A.is_square:
        raise ValueError(
            f"{nome} exige nº de equações = nº de incógnitas "
            f"({A.rows} equações, {A.cols} incógnitas). Use o escalonamento."
        )
    d = A.det()
    if d == 0:
        raise ValueError(
            f"det(A) = 0: {nome} não se aplica (o sistema é SPI ou SI). Use o escalonamento."
        )
    return d


def resolver_cramer(A, b):
    """Retorna (linhas_de_texto, lista_solução). Lança ValueError se não aplicável."""
    d = _checar_quadrado_regular(A, "A regra de Cramer")
    linhas = [f"det(A) = {d}"]
    sol = []
    for i in range(A.cols):
        Ai = A.copy()
        Ai[:, i] = b
        di = Ai.det()
        xi = sp.nsimplify(di / d)
        linhas.append(f"det(A{i + 1}) = {di}   →   x{i + 1} = {di}/{d} = {xi}")
        sol.append(xi)
    return linhas, sol


def resolver_inversa(A, b):
    """Retorna (linhas_de_texto, lista_solução). Lança ValueError se não aplicável."""
    _checar_quadrado_regular(A, "O método da inversa")
    Ainv = A.inv()
    x = Ainv * b
    linhas = ["A⁻¹ =", matriz_texto(Ainv), "x = A⁻¹·b =", matriz_texto(x)]
    return linhas, list(x)


def _linhas_gauss(A, b, tipo, xs):
    if tipo == "SI":
        return ["Sem solução (posto(A) ≠ posto([A|b]))."]
    sol = next(iter(sp.linsolve((A, b), *xs)))
    linhas = []
    for x, v in zip(xs, sol, strict=False):
        extra = f"   (≈ {sp.N(v, 6)})" if tipo == "SPD" and not v.is_Integer else ""
        linhas.append(f"  {x} = {v}{extra}")
    return linhas


def relatorio_sistema(A, b, metodo="gauss"):
    """
    Resolve e classifica A·x = b.
    metodo: 'gauss', 'cramer', 'inversa' ou 'todos'.
    Retorna (tipo, linhas). Linhas que começam com 'Classificação' trazem o tipo.
    """
    tipo, rA, rAug, n = classificar(A, b)
    xs = sp.symbols(f"x1:{n + 1}")
    descr = {
        "SPD": "SPD — Sistema Possível e Determinado (solução única).",
        "SPI": f"SPI — Sistema Possível e Indeterminado ({n - rA} grau(s) de liberdade).",
        "SI": "SI — Sistema Impossível (sem solução).",
    }
    linhas = [
        f"posto(A) = {rA}   posto([A|b]) = {rAug}   incógnitas = {n}",
        f"Classificação: {descr[tipo]}",
    ]
    metodos = list(METODOS) if metodo == "todos" else [metodo]
    for m in metodos:
        linhas += ["", f"— {METODOS[m]} —"]
        try:
            if m == "gauss":
                linhas += _linhas_gauss(A, b, tipo, xs)
            elif m == "cramer":
                linhas += resolver_cramer(A, b)[0]
            else:
                linhas += resolver_inversa(A, b)[0]
        except ValueError as e:
            linhas.append(str(e))
    return tipo, linhas


def _equacao_texto(coefs, c):
    """Ex.: [2, -1, 0], 8  →  '2x1 - x2 = 8'."""
    partes = []
    for j, a in enumerate(coefs):
        if a == 0:
            continue
        mod = "" if abs(a) == 1 else str(abs(a))
        sinal = "-" if a < 0 else "+"
        partes.append((sinal, f"{mod}x{j + 1}"))
    if not partes:
        return f"0 = {c}"
    txt = ("-" if partes[0][0] == "-" else "") + partes[0][1]
    for sinal, t in partes[1:]:
        txt += f" {sinal} {t}"
    return f"{txt} = {c}"


CORES_RETAS = [
    "#4f46e5",
    "#e11d48",
    "#059669",
    "#d97706",
    "#0891b2",
    "#9333ea",
    "#475569",
    "#db2777",
]
ESTILO_CLARO = {"fundo": "#ffffff", "texto": "#1f2430", "grade": "#e2e5ee", "eixos": "#9aa1b2"}


def figura_sistema(A, b, tipo, estilo=None):
    """Figure do matplotlib com as retas de um sistema de 2 incógnitas (ou None).

    ``estilo``: dict opcional com as cores 'fundo', 'texto', 'grade' e 'eixos'
    (a janela usa isso para acompanhar o tema claro/escuro).
    """
    if not MPL or A.cols != 2:
        return None
    est = {**ESTILO_CLARO, **(estilo or {})}
    fig = Figure(figsize=(5, 4), dpi=100, layout="constrained", facecolor=est["fundo"])
    ax = fig.add_subplot(111, facecolor=est["fundo"])
    xs = [-10 + 0.1 * i for i in range(201)]
    for i in range(A.rows):
        a1, a2, c = float(A[i, 0]), float(A[i, 1]), float(b[i, 0])
        rot = _equacao_texto(A[i, :], b[i, 0])
        cor = CORES_RETAS[i % len(CORES_RETAS)]
        if a2 != 0:
            ax.plot(xs, [(c - a1 * x) / a2 for x in xs], label=rot, color=cor, lw=2)
        elif a1 != 0:
            ax.axvline(c / a1, label=rot, color=cor, lw=2)
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.axhline(0, color=est["eixos"], lw=0.8)
    ax.axvline(0, color=est["eixos"], lw=0.8)
    ax.grid(color=est["grade"], lw=0.8)
    for lado in ax.spines.values():
        lado.set_color(est["grade"])
    ax.tick_params(colors=est["texto"], labelsize=8)
    ax.set_xlabel("x1", color=est["texto"])
    ax.set_ylabel("x2", color=est["texto"])
    ax.set_title(f"Sistema {tipo}", color=est["texto"], fontweight="bold")
    leg = ax.legend(fontsize=8, facecolor=est["fundo"], edgecolor=est["grade"])
    for t in leg.get_texts():
        t.set_color(est["texto"])
    return fig


# ----------------------------------------------------------------------
# Catálogo de operações (usado pelo menu do terminal e pela janela)
#   param: None | "k" (escalar) | "n" (expoente inteiro)
# ----------------------------------------------------------------------
Operacao = namedtuple("Operacao", "cod grupo nome fn nmat param")

OPERACOES = [
    Operacao("4", "Operações", "Soma (A + B)", f_soma, 2, None),
    Operacao("5", "Operações", "Subtração (A - B)", f_subtracao, 2, None),
    Operacao("6", "Operações", "Multiplicação (A × B)", f_multiplicacao, 2, None),
    Operacao("7", "Operações", "Multiplicar por escalar", f_escalar, 1, "k"),
    Operacao("8", "Operações", "Potência (Aⁿ)", f_potencia, 1, "n"),
    Operacao("9", "Operações", "Transposta", f_transposta, 1, None),
    Operacao("10", "Operações", "Inversa", f_inversa, 1, None),
    Operacao("11", "Propriedades", "Determinante", f_determinante, 1, None),
    Operacao("12", "Propriedades", "Posto (rank)", f_posto, 1, None),
    Operacao("13", "Propriedades", "Traço", f_traco, 1, None),
    Operacao("14", "Propriedades", "Escalonar (RREF)", f_escalonar, 1, None),
    Operacao("15", "Propriedades", "Autovalores e autovetores", f_autovalores, 1, None),
    Operacao("16", "Propriedades", "Decomposição LU", f_lu, 1, None),
    Operacao("18", "Operações", "Adjunta (adj A)", f_adjunta, 1, None),
    Operacao("19", "Operações", "Matriz de cofatores", f_cofatores, 1, None),
    Operacao("20", "Propriedades", "Classificação estrutural", f_estrutura, 1, None),
    Operacao("21", "Propriedades", "Partes L + D + U", f_partes_triangulares, 1, None),
    Operacao(
        "22", "Propriedades", "Partes simétrica e antissimétrica", f_partes_simetrica, 1, None
    ),
    Operacao("23", "Propriedades", "Decomposição QR", f_qr, 1, None),
    Operacao("24", "Propriedades", "Decomposição de Cholesky", f_cholesky, 1, None),
    Operacao("25", "Propriedades", "Diagonalização (A = P·D·P⁻¹)", f_diagonalizacao, 1, None),
]
