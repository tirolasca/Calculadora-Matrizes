"""Interface de terminal (menu numerado) da calculadora de matrizes."""

import sympy as sp

from .nucleo import (
    MPL,
    OPERACOES,
    figura_sistema,
    matriz_texto,
    numero,
    parse_matriz_colchetes,
    relatorio_sistema,
)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    console = Console()
    RICH = True
except ImportError:  # rich é opcional
    RICH = False


def msg(texto, estilo=""):
    if RICH:
        console.print(texto, style=estilo, markup=False, highlight=False)
    else:
        print(texto)


def erro(texto):
    msg(f"✗ {texto}", "bold red")


def titulo(texto):
    if RICH:
        console.print(Panel(texto, style="bold cyan", expand=False))
    else:
        print(f"\n=== {texto} ===")


def mostrar(M, nome=""):
    """Exibe uma matriz com tabela (rich) ou texto alinhado."""
    if nome:
        msg(f"{nome} ({M.rows}x{M.cols}):", "bold")
    if RICH:
        t = Table(show_header=False, box=None, padding=(0, 2))
        for _ in range(M.cols):
            t.add_column(justify="right")
        for i in range(M.rows):
            t.add_row(*[str(M[i, j]) for j in range(M.cols)])
        console.print(t)
    else:
        print(matriz_texto(M))


def ler_int(prompt, minimo=1):
    while True:
        try:
            n = int(input(prompt))
            if n >= minimo:
                return n
        except ValueError:
            pass
        erro(f"Digite um inteiro >= {minimo}.")


def ler_numero(prompt):
    while True:
        try:
            return numero(input(prompt))
        except (ValueError, TypeError, ZeroDivisionError):
            erro("Número inválido (use 3, -2.5 ou 1/2).")


def ler_linha(prompt, qtd):
    while True:
        try:
            v = [numero(x) for x in input(prompt).split()]
            if len(v) == qtd:
                return v
        except (ValueError, TypeError, ZeroDivisionError):
            pass
        erro(f"Digite exatamente {qtd} números separados por espaço.")


def ler_matriz_teclado(nome="matriz"):
    linhas = ler_int(f"  Nº de linhas de {nome}: ")
    cols = ler_int(f"  Nº de colunas de {nome}: ")
    msg(f"  Digite cada linha com {cols} número(s) separados por espaço.", "dim")
    return sp.Matrix([ler_linha(f"  Linha {i + 1}: ", cols) for i in range(linhas)])


memoria = {}


def salvar_opcional(M):
    resp = input("  Salvar na memória? Nome (ex.: A) ou Enter para pular: ").strip().upper()
    if resp:
        memoria[resp] = M
        msg(f"  ✓ Salva como {resp}", "green")


def escolher(nome_pedido):
    """Pede uma matriz: nome da memória ou digitação na hora."""
    while True:
        if memoria:
            print(f"  Memória: {', '.join(memoria)}")
        resp = input(f"  {nome_pedido} (nome da memória, ou 'n' para digitar nova): ").strip()
        if resp.upper() in memoria:
            return memoria[resp.upper()]
        if resp.lower() == "n" or not memoria:
            M = ler_matriz_teclado(nome_pedido)
            salvar_opcional(M)
            return M
        erro("Nome não encontrado.")


def op_cadastrar():
    nome = input("  Nome da matriz (ex.: A): ").strip().upper() or "A"
    modo = input("  Entrada: 1-linha a linha  2-formato [[1,2],[3,4]] ou '1 2; 3 4': ").strip()
    if modo == "2":
        try:
            M = parse_matriz_colchetes(input("  Matriz: "))
        except ValueError as e:
            return erro(str(e))
    else:
        M = ler_matriz_teclado(nome)
    memoria[nome] = M
    msg(f"✓ Matriz {nome} salva.", "green")
    mostrar(M, nome)


def op_listar():
    if not memoria:
        return msg("Nenhuma matriz na memória.", "yellow")
    for nome, M in memoria.items():
        mostrar(M, nome)


def op_remover():
    nome = input("  Nome da matriz a remover: ").strip().upper()
    if memoria.pop(nome, None) is None:
        erro("Matriz não encontrada.")
    else:
        msg(f"✓ {nome} removida.", "green")


def executar_operacao(op):
    """Executa uma Operacao do catálogo, pedindo os dados pelo teclado."""
    mats = [escolher(f"Matriz {letra}") for letra in "AB"[: op.nmat]]
    extra = []
    if op.param == "k":
        extra = [ler_numero("  Escalar k: ")]
    elif op.param == "n":
        extra = [ler_int("  Expoente inteiro (negativo = potência da inversa): ", minimo=-100)]
    try:
        resultado = op.fn(*mats, *extra)
    except ValueError as e:
        return erro(str(e))
    primeira = None
    for rotulo, valor in resultado:
        if isinstance(valor, sp.MatrixBase):
            mostrar(valor, rotulo)
            primeira = primeira if primeira is not None else valor
        else:
            msg(f"{rotulo} {valor}".strip(), "bold green")
    if primeira is not None:
        salvar_opcional(primeira)


def ler_sistema():
    """Retorna (A, b) lidos do teclado ou da memória."""
    origem = input("  1-Digitar equações  2-Usar matrizes da memória (A e b): ").strip()
    if origem == "2":
        A = escolher("Matriz dos coeficientes A")
        b = escolher("Vetor de termos independentes b (coluna)")
        if b.cols != 1 or b.rows != A.rows:
            erro("b deve ser uma coluna com o mesmo nº de linhas de A.")
            return None
        return A, b
    m = ler_int("  Número de equações: ")
    n = ler_int("  Número de incógnitas: ")
    msg(
        f"  Cada equação: {n} coeficientes + termo independente. Ex.: 2x + y - z = 8 → 2 1 -1 8",
        "dim",
    )
    M = sp.Matrix([ler_linha(f"  Equação {i + 1}: ", n + 1) for i in range(m)])
    return M[:, :n], M[:, n]


def op_sistema():
    r = ler_sistema()
    if r is None:
        return
    A, b = r
    print(
        "  Método: 1-Escalonamento (Gauss-Jordan)  2-Regra de Cramer  "
        "3-Matriz inversa  4-Comparar os três"
    )
    metodo = {"1": "gauss", "2": "cramer", "3": "inversa", "4": "todos"}.get(
        input("  Escolha [1]: ").strip() or "1"
    )
    if metodo is None:
        return erro("Método inválido.")
    tipo, linhas = relatorio_sistema(A, b, metodo)
    cores = {"SPD": "bold green", "SPI": "bold yellow", "SI": "bold red"}
    titulo("Resultado")
    for l in linhas:
        if l.startswith("Classificação"):
            msg(l, cores[tipo])
        elif l.startswith("—"):
            msg(l, "bold")
        elif l.startswith("posto"):
            msg(l, "dim")
        else:
            msg(l)
    if (
        MPL
        and A.cols == 2
        and input("  Salvar gráfico das equações? (s/N): ").strip().lower() == "s"
    ):
        figura_sistema(A, b, tipo).savefig("sistema.png", dpi=120)
        msg("  ✓ Gráfico salvo em sistema.png", "green")


MENU = [
    (
        "Matrizes na memória",
        [
            ("1", "Cadastrar matriz", op_cadastrar),
            ("2", "Listar matrizes", op_listar),
            ("3", "Remover matriz", op_remover),
        ],
    ),
]
for _grupo in ("Operações", "Propriedades"):
    MENU.append(
        (
            _grupo,
            [
                (o.cod, o.nome, lambda o=o: executar_operacao(o))
                for o in OPERACOES
                if o.grupo == _grupo
            ],
        )
    )
MENU.append(
    (
        "Sistemas lineares",
        [
            ("17", "Resolver e classificar (SPD / SPI / SI)", op_sistema),
        ],
    )
)
ACOES = {cod: fn for _, itens in MENU for cod, _, fn in itens}


def mostrar_menu():
    titulo("CALCULADORA DE MATRIZES E SISTEMAS LINEARES")
    for grupo, itens in MENU:
        msg(f"\n{grupo}", "bold")
        for cod, nome, _ in itens:
            print(f"  {cod:>2} - {nome}")
    print("\n   0 - Sair")


def main():
    while True:
        mostrar_menu()
        try:
            op = input("\nEscolha uma opção: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if op == "0":
            break
        fn = ACOES.get(op)
        if fn is None:
            erro("Opção inválida.")
            continue
        try:
            fn()
        except (EOFError, KeyboardInterrupt):
            print()
            msg("Operação cancelada.", "yellow")
        except Exception as e:  # nunca derruba o programa
            erro(f"Erro inesperado: {e}")
    msg("Até logo!", "bold")


if __name__ == "__main__":
    main()
