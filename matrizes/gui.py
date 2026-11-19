"""Interface gráfica (tkinter) da calculadora de matrizes.

Uso:  python -m matrizes.gui            (tema claro)
      python -m matrizes.gui --escuro   (tema escuro)
O botão no canto superior direito alterna entre os temas; Ctrl+Enter executa.
"""

import sys
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk

import sympy as sp

from . import __version__
from . import nucleo as core
from .paleta import TEMAS

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    GRAFICO = core.MPL
except ImportError:  # gráfico é opcional
    GRAFICO = False

MAX_DIM = 8

FAMILIAS_UI = (
    "Segoe UI",
    "SF Pro Text",
    "Helvetica Neue",
    "Inter",
    "Roboto",
    "Noto Sans",
    "DejaVu Sans",
)
FAMILIAS_MONO = (
    "Cascadia Mono",
    "Consolas",
    "SF Mono",
    "Menlo",
    "JetBrains Mono",
    "DejaVu Sans Mono",
    "Courier New",
)


def escolher_familia(raiz, candidatas, padrao):
    existentes = {f.lower(): f for f in tkfont.families(raiz)}
    for c in candidatas:
        if c.lower() in existentes:
            return existentes[c.lower()]
    return padrao


def criar_fontes(raiz):
    ui = escolher_familia(raiz, FAMILIAS_UI, tkfont.nametofont("TkDefaultFont").actual("family"))
    mono = escolher_familia(raiz, FAMILIAS_MONO, tkfont.nametofont("TkFixedFont").actual("family"))
    return {
        "ui": tkfont.Font(root=raiz, family=ui, size=10),
        "ui_b": tkfont.Font(root=raiz, family=ui, size=10, weight="bold"),
        "ui_s": tkfont.Font(root=raiz, family=ui, size=9),
        "titulo": tkfont.Font(root=raiz, family=ui, size=17, weight="bold"),
        "mono": tkfont.Font(root=raiz, family=mono, size=11),
        "mono_b": tkfont.Font(root=raiz, family=mono, size=11, weight="bold"),
    }


def ler_celula(entry, onde):
    """Converte o conteúdo de uma caixa em número exato ou lança ValueError."""
    txt = entry.get().strip()
    if not txt:
        raise ValueError(f"Célula vazia em {onde}.")
    try:
        return core.numero(txt)
    except (ValueError, TypeError, ZeroDivisionError):
        raise ValueError(f"Valor inválido em {onde}: '{txt}' (use 3, -2.5 ou 1/2).") from None


def linhas_resultado(resultado):
    """Transforma a saída das funções do núcleo em [(linha, tag)] para a caixa de texto."""
    linhas = []
    for rotulo, valor in resultado:
        if isinstance(valor, sp.MatrixBase):
            linhas.append((f"{rotulo} ({valor.rows}x{valor.cols}):", "titulo"))
            linhas += [(l, None) for l in core.matriz_texto(valor).split("\n")]
        elif rotulo.startswith("Obs"):
            linhas.append((f"{rotulo} {valor}", "fraco"))
        else:
            linhas.append(
                (f"{rotulo} {valor}".strip(), "destaque" if rotulo.endswith("=") else None)
            )
    return linhas


def texto_rolavel(pai, wrap, fonte, **kw):
    """Caixa de texto somente leitura com barras de rolagem. Retorna (quadro, texto)."""
    quadro = ttk.Frame(pai)
    t = tk.Text(quadro, wrap=wrap, state="disabled", font=fonte, **kw)
    sy = ttk.Scrollbar(quadro, orient="vertical", command=t.yview)
    t.configure(yscrollcommand=sy.set)
    sy.pack(side="right", fill="y")
    if wrap == "none":
        sx = ttk.Scrollbar(quadro, orient="horizontal", command=t.xview)
        t.configure(xscrollcommand=sx.set)
        sx.pack(side="bottom", fill="x")
    t.pack(side="left", fill="both", expand=True)
    return quadro, t


# ----------------------------------------------------------------------
# Janela para digitar/editar uma matriz
# ----------------------------------------------------------------------
class EditorMatriz(tk.Toplevel):
    def __init__(self, app, nome, matriz, ao_salvar):
        super().__init__(app.raiz)
        self.app = app
        self.title("Editar matriz" if matriz is not None else "Nova matriz")
        self.resizable(False, False)
        self.transient(app.raiz)
        self.configure(background=app.t["bg"])
        self.ao_salvar = ao_salvar
        self.celulas = []
        self.valores_iniciais = matriz

        corpo = ttk.Frame(self, padding=16)
        corpo.pack(fill="both", expand=True)

        topo = ttk.Frame(corpo)
        topo.pack(fill="x")
        ttk.Label(topo, text="Nome").grid(row=0, column=0, sticky="w")
        self.var_nome = tk.StringVar(value=nome)
        ttk.Entry(topo, textvariable=self.var_nome, width=5, font=app.fontes["mono"]).grid(
            row=1, column=0, padx=(0, 16)
        )
        self.var_lin = tk.IntVar(value=matriz.rows if matriz is not None else 2)
        self.var_col = tk.IntVar(value=matriz.cols if matriz is not None else 2)
        ttk.Label(topo, text="Linhas").grid(row=0, column=1, sticky="w")
        ttk.Spinbox(
            topo, from_=1, to=MAX_DIM, width=4, textvariable=self.var_lin, command=self.redesenhar
        ).grid(row=1, column=1, padx=(0, 12))
        ttk.Label(topo, text="Colunas").grid(row=0, column=2, sticky="w")
        ttk.Spinbox(
            topo, from_=1, to=MAX_DIM, width=4, textvariable=self.var_col, command=self.redesenhar
        ).grid(row=1, column=2)

        self.grade = ttk.Frame(corpo)
        self.grade.pack(pady=14)

        ttk.Label(corpo, text="Ou cole a matriz pronta", style="Muted.TLabel").pack(anchor="w")
        colar = ttk.Frame(corpo)
        colar.pack(fill="x", pady=(2, 0))
        self.var_colar = tk.StringVar()
        ttk.Entry(colar, textvariable=self.var_colar, width=30, font=app.fontes["mono"]).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(colar, text="Preencher", command=self.preencher).pack(side="left", padx=(6, 0))
        ttk.Label(
            corpo,
            text="Formatos: [[1,2],[3,4]]  ou  1 2; 3 4   (frações: 1/2)",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        rodape = ttk.Frame(corpo)
        rodape.pack(fill="x", pady=(16, 0))
        ttk.Button(rodape, text="Salvar", style="Acento.TButton", command=self.salvar).pack(
            side="right"
        )
        ttk.Button(rodape, text="Cancelar", command=self.destroy).pack(side="right", padx=8)

        self.redesenhar()
        self.bind("<Return>", lambda e: self.salvar())
        self.bind("<Escape>", lambda e: self.destroy())

    def _tamanho(self):
        try:
            return (
                max(1, min(MAX_DIM, int(self.var_lin.get()))),
                max(1, min(MAX_DIM, int(self.var_col.get()))),
            )
        except (tk.TclError, ValueError):
            return None

    def redesenhar(self):
        tam = self._tamanho()
        if tam is None:
            return
        antigos = [[c.get() for c in lin] for lin in self.celulas]
        for w in self.grade.winfo_children():
            w.destroy()
        self.celulas = []
        ini = self.valores_iniciais
        for i in range(tam[0]):
            lin = []
            for j in range(tam[1]):
                e = ttk.Entry(self.grade, width=7, justify="right", font=self.app.fontes["mono"])
                e.grid(row=i, column=j, padx=3, pady=3)
                if i < len(antigos) and j < len(antigos[i]):
                    e.insert(0, antigos[i][j])
                elif ini is not None and not antigos and i < ini.rows and j < ini.cols:
                    e.insert(0, str(ini[i, j]))
                else:
                    e.insert(0, "0")
                lin.append(e)
            self.celulas.append(lin)
        if self.celulas:
            self.celulas[0][0].focus_set()
            self.celulas[0][0].select_range(0, "end")

    def preencher(self):
        try:
            M = core.parse_matriz_colchetes(self.var_colar.get())
        except ValueError as e:
            return messagebox.showerror("Formato inválido", str(e), parent=self)
        if M.rows > MAX_DIM or M.cols > MAX_DIM:
            return messagebox.showerror("Muito grande", f"Máximo {MAX_DIM}x{MAX_DIM}.", parent=self)
        self.valores_iniciais = None
        self.var_lin.set(M.rows)
        self.var_col.set(M.cols)
        self.redesenhar()
        for i in range(M.rows):
            for j in range(M.cols):
                self.celulas[i][j].delete(0, "end")
                self.celulas[i][j].insert(0, str(M[i, j]))

    def salvar(self):
        nome = self.var_nome.get().strip().upper()
        if not nome:
            return messagebox.showerror("Nome", "Dê um nome à matriz (ex.: A).", parent=self)
        try:
            M = sp.Matrix(
                [
                    [ler_celula(c, f"linha {i + 1}, coluna {j + 1}") for j, c in enumerate(lin)]
                    for i, lin in enumerate(self.celulas)
                ]
            )
        except ValueError as e:
            return messagebox.showerror("Valor inválido", str(e), parent=self)
        self.ao_salvar(nome, M)
        self.destroy()


# ----------------------------------------------------------------------
# Janela principal
# ----------------------------------------------------------------------
class App(ttk.Frame):
    def __init__(self, raiz, tema="claro"):
        super().__init__(raiz)
        self.raiz = raiz
        self.pack(fill="both", expand=True)
        self.mem = {}  # memória de matrizes desta janela
        self.canvas = None
        self.ultimo_sistema = None
        self.textos, self.listas, self.combos = [], [], []
        self.fontes = criar_fontes(raiz)
        self.ops = {o.nome: o for o in core.OPERACOES}
        self.estilo = ttk.Style(raiz)
        try:
            self.estilo.theme_use("clam")
        except tk.TclError:
            pass

        self._montar_cabecalho()
        corpo = ttk.Frame(self, padding=(14, 10, 14, 14))
        corpo.pack(fill="both", expand=True)
        self.abas = ttk.Notebook(corpo)
        self.abas.pack(fill="both", expand=True)
        self.aba_ops = ttk.Frame(self.abas, padding=12)
        self.aba_sis = ttk.Frame(self.abas, padding=12)
        self.abas.add(self.aba_ops, text="Matrizes e operações")
        self.abas.add(self.aba_sis, text="Sistemas lineares")
        self._montar_ops()
        self._montar_sistema()
        self.nome_tema = tema
        self.aplicar_tema(tema)
        self.atualizar_memoria()
        raiz.bind("<Control-Return>", lambda e: self.executar_aba_atual())

    # ---------- tema ----------
    def aplicar_tema(self, nome):
        self.nome_tema = nome
        self.t = t = TEMAS[nome]
        f = self.fontes
        st = self.estilo
        self.raiz.configure(background=t["bg"])
        st.configure(
            ".",
            background=t["bg"],
            foreground=t["fg"],
            font=f["ui"],
            bordercolor=t["border"],
            lightcolor=t["bg"],
            darkcolor=t["bg"],
            troughcolor=t["bg"],
            focuscolor=t["bg"],
            insertcolor=t["fg"],
        )
        st.configure("TFrame", background=t["bg"])
        st.configure("TLabel", background=t["bg"], foreground=t["fg"])
        st.configure("Muted.TLabel", foreground=t["muted"], font=f["ui_s"])
        st.configure("Header.TFrame", background=t["header_bg"])
        st.configure("Header.TLabel", background=t["header_bg"], foreground=t["header_fg"])
        st.configure("Titulo.Header.TLabel", font=f["titulo"])
        st.configure("Sub.Header.TLabel", foreground=t["header_fg"], font=f["ui_s"])
        st.configure(
            "TLabelframe",
            background=t["bg"],
            bordercolor=t["border"],
            lightcolor=t["border"],
            darkcolor=t["border"],
            borderwidth=1,
            relief="solid",
        )
        st.configure(
            "TLabelframe.Label", background=t["bg"], foreground=t["accent"], font=f["ui_b"]
        )
        st.configure("TSeparator", background=t["border"])
        st.configure("TNotebook", background=t["bg"], borderwidth=0, tabmargins=(0, 0, 0, 0))
        st.configure(
            "TNotebook.Tab",
            background=t["tab"],
            foreground=t["muted"],
            padding=(20, 9),
            borderwidth=0,
            font=f["ui_b"],
        )
        st.map(
            "TNotebook.Tab",
            background=[("selected", t["bg"])],
            foreground=[("selected", t["accent"])],
        )
        st.configure(
            "TButton",
            background=t["botao"],
            foreground=t["fg"],
            padding=(14, 7),
            borderwidth=1,
            bordercolor=t["botao"],
            lightcolor=t["botao"],
            darkcolor=t["botao"],
            relief="flat",
            font=f["ui"],
        )
        st.map(
            "TButton",
            background=[("active", t["botao_hover"]), ("disabled", t["bg"])],
            bordercolor=[("active", t["botao_hover"])],
            lightcolor=[("active", t["botao_hover"])],
            darkcolor=[("active", t["botao_hover"])],
            foreground=[("disabled", t["muted"])],
        )
        for estilo, base in (("Acento.TButton", "accent"), ("Header.TButton", "header_btn")):
            fundo = t[base]
            hover = t["accent_hover"] if base == "accent" else t["accent"]
            fg = t["accent_fg"] if base == "accent" else t["header_fg"]
            st.configure(
                estilo,
                background=fundo,
                foreground=fg,
                bordercolor=fundo,
                lightcolor=fundo,
                darkcolor=fundo,
                font=f["ui_b"],
            )
            st.map(
                estilo,
                background=[("active", hover)],
                bordercolor=[("active", hover)],
                lightcolor=[("active", hover)],
                darkcolor=[("active", hover)],
            )
        for campo in ("TEntry", "TSpinbox", "TCombobox"):
            st.configure(
                campo,
                fieldbackground=t["campo"],
                foreground=t["fg"],
                padding=5,
                bordercolor=t["border"],
                lightcolor=t["border"],
                darkcolor=t["border"],
                insertcolor=t["fg"],
                arrowcolor=t["fg"],
                background=t["botao"],
                selectbackground=t["selecao"],
                selectforeground=t["fg"],
            )
            st.map(
                campo,
                bordercolor=[("focus", t["accent"])],
                lightcolor=[("focus", t["accent"])],
                darkcolor=[("focus", t["accent"])],
                fieldbackground=[("readonly", t["campo"]), ("disabled", t["bg"])],
                foreground=[("disabled", t["muted"])],
                selectbackground=[("readonly", t["campo"])],
                selectforeground=[("readonly", t["fg"])],
            )
        st.configure(
            "TScrollbar",
            background=t["botao"],
            troughcolor=t["bg"],
            bordercolor=t["bg"],
            lightcolor=t["botao"],
            darkcolor=t["botao"],
            arrowcolor=t["muted"],
            relief="flat",
        )
        st.map("TScrollbar", background=[("active", t["botao_hover"])])
        st.configure("TPanedwindow", background=t["bg"])
        st.configure("Sash", sashthickness=8, background=t["bg"])
        self.raiz.option_add("*TCombobox*Listbox.font", f["ui"])
        self._colorir_widgets_classicos()
        self.btn_tema.configure(text="☾  Tema escuro" if nome == "claro" else "☀  Tema claro")
        if self.ultimo_sistema is not None:
            self.desenhar_grafico(*self.ultimo_sistema)

    def _colorir_widgets_classicos(self):
        """Widgets tk (não-ttk) precisam ser recoloridos à mão."""
        t, f = self.t, self.fontes
        for tx in self.textos:
            tx.configure(
                background=t["texto_bg"],
                foreground=t["fg"],
                insertbackground=t["fg"],
                selectbackground=t["selecao"],
                selectforeground=t["fg"],
                highlightthickness=1,
                highlightbackground=t["border"],
                highlightcolor=t["accent"],
                relief="flat",
                padx=10,
                pady=8,
            )
            tx.tag_configure("titulo", foreground=t["accent"], font=f["mono_b"])
            tx.tag_configure("destaque", foreground=t["ok"], font=f["mono_b"])
            tx.tag_configure("fraco", foreground=t["muted"])
            tx.tag_configure("SPD", foreground=t["ok"], font=f["mono_b"])
            tx.tag_configure("SPI", foreground=t["aviso"], font=f["mono_b"])
            tx.tag_configure("SI", foreground=t["perigo"], font=f["mono_b"])
        for lb in self.listas:
            lb.configure(
                background=t["campo"],
                foreground=t["fg"],
                selectbackground=t["accent"],
                selectforeground=t["accent_fg"],
                highlightthickness=1,
                highlightbackground=t["border"],
                highlightcolor=t["accent"],
                relief="flat",
                activestyle="none",
            )
        for cb in self.combos:  # a lista suspensa do combobox é um widget tk à parte
            try:
                popdown = cb.tk.eval(f"ttk::combobox::PopdownWindow {cb}")
                cb.tk.call(
                    f"{popdown}.f.l",
                    "configure",
                    "-background",
                    t["campo"],
                    "-foreground",
                    t["fg"],
                    "-selectbackground",
                    t["accent"],
                    "-selectforeground",
                    t["accent_fg"],
                )
            except tk.TclError:
                pass

    def alternar_tema(self):
        self.aplicar_tema("escuro" if self.nome_tema == "claro" else "claro")

    # ---------- cabeçalho ----------
    def _montar_cabecalho(self):
        cab = ttk.Frame(self, style="Header.TFrame", padding=(20, 14))
        cab.pack(fill="x")
        textos = ttk.Frame(cab, style="Header.TFrame")
        textos.pack(side="left")
        ttk.Label(textos, text="Calculadora de Matrizes", style="Titulo.Header.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            textos,
            text="Operações, sistemas lineares e classificação  ·  SPD  SPI  SI",
            style="Sub.Header.TLabel",
        ).pack(anchor="w")
        ttk.Label(cab, text=f"v{__version__}", style="Sub.Header.TLabel").pack(
            side="right", padx=(12, 0)
        )
        self.btn_tema = ttk.Button(cab, text="", style="Header.TButton", command=self.alternar_tema)
        self.btn_tema.pack(side="right")

    # ---------- utilidades ----------
    def erro(self, titulo, texto):
        messagebox.showerror(titulo, texto, parent=self.raiz)

    @staticmethod
    def escrever(texto_widget, linhas):
        """Substitui o conteúdo; ``linhas`` é uma lista de (texto, tag)."""
        texto_widget.configure(state="normal")
        texto_widget.delete("1.0", "end")
        for linha, tag in linhas:
            texto_widget.insert("end", linha + "\n", tag or ())
        texto_widget.configure(state="disabled")

    def _texto(self, pai, wrap, **kw):
        quadro, tx = texto_rolavel(pai, wrap, self.fontes["mono"], **kw)
        self.textos.append(tx)
        return quadro, tx

    def _combo(self, pai, **kw):
        cb = ttk.Combobox(pai, font=self.fontes["ui"], **kw)
        self.combos.append(cb)
        return cb

    def executar_aba_atual(self):
        if self.abas.index(self.abas.select()) == 0:
            self.calcular()
        else:
            self.resolver()

    # ---------- aba 1: matrizes e operações ----------
    def _montar_ops(self):
        esq = ttk.LabelFrame(self.aba_ops, text=" Memória ", padding=10)
        esq.pack(side="left", fill="y")
        self.lista = tk.Listbox(
            esq, width=12, height=7, exportselection=False, font=self.fontes["mono_b"]
        )
        self.listas.append(self.lista)
        self.lista.pack(fill="x")
        self.lista.bind("<<ListboxSelect>>", lambda e: self.mostrar_selecionada())
        self.lista.bind("<Double-Button-1>", lambda e: self.editar())
        ttk.Button(esq, text="＋  Nova", style="Acento.TButton", command=self.nova).pack(
            fill="x", pady=(10, 0)
        )
        ttk.Button(esq, text="Editar", command=self.editar).pack(fill="x", pady=(6, 0))
        ttk.Button(esq, text="Remover", command=self.remover).pack(fill="x", pady=(6, 0))
        quadro, self.previa = self._texto(esq, "none", width=24, height=8)
        quadro.pack(fill="both", expand=True, pady=(12, 0))

        dir_ = ttk.Frame(self.aba_ops, padding=(14, 0, 0, 0))
        dir_.pack(side="left", fill="both", expand=True)

        form = ttk.LabelFrame(dir_, text=" Operação ", padding=12)
        form.pack(fill="x")
        ttk.Label(form, text="Operação").grid(row=0, column=0, sticky="w")
        self.cb_op = self._combo(form, state="readonly", width=34, values=list(self.ops))
        self.cb_op.current(0)
        self.cb_op.grid(row=1, column=0, columnspan=4, sticky="we", pady=(2, 10))
        self.cb_op.bind("<<ComboboxSelected>>", lambda e: self.ajustar_campos())

        ttk.Label(form, text="Matriz A").grid(row=2, column=0, sticky="w")
        ttk.Label(form, text="Matriz B").grid(row=2, column=1, sticky="w", padx=(12, 0))
        self.lbl_param = ttk.Label(form, text="Valor")
        self.lbl_param.grid(row=2, column=2, sticky="w", padx=(12, 0))
        self.cb_a = self._combo(form, state="readonly", width=7)
        self.cb_a.grid(row=3, column=0, sticky="w", pady=(2, 0))
        self.cb_b = self._combo(form, state="readonly", width=7)
        self.cb_b.grid(row=3, column=1, sticky="w", padx=(12, 0), pady=(2, 0))
        self.var_param = tk.StringVar()
        self.ent_param = ttk.Entry(
            form, textvariable=self.var_param, width=9, font=self.fontes["mono"]
        )
        self.ent_param.grid(row=3, column=2, sticky="w", padx=(12, 0), pady=(2, 0))
        ttk.Button(form, text="Calcular  ⏎", style="Acento.TButton", command=self.calcular).grid(
            row=3, column=3, sticky="e", padx=(18, 0)
        )
        form.columnconfigure(3, weight=1)

        ttk.Label(form, text="Guardar resultado em", style="Muted.TLabel").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(12, 0)
        )
        self.var_salvar = tk.StringVar(value="R")
        ttk.Entry(form, textvariable=self.var_salvar, width=7, font=self.fontes["mono"]).grid(
            row=5, column=0, sticky="w", pady=(2, 0)
        )

        saida = ttk.LabelFrame(dir_, text=" Resultado ", padding=8)
        saida.pack(fill="both", expand=True, pady=(12, 0))
        quadro, self.saida_ops = self._texto(saida, "none", height=12, width=52)
        quadro.pack(fill="both", expand=True)
        self.ajustar_campos()

    def nomes(self):
        return sorted(self.mem)

    def atualizar_memoria(self, selecionar=None):
        nomes = self.nomes()
        self.lista.delete(0, "end")
        for n in nomes:
            self.lista.insert("end", f" {n}")
        for cb in (self.cb_a, self.cb_b):
            atual = cb.get()
            cb.configure(values=nomes)
            cb.set(atual if atual in nomes else (nomes[0] if nomes else ""))
        if selecionar in nomes:
            self.lista.selection_clear(0, "end")
            self.lista.selection_set(nomes.index(selecionar))
        self.mostrar_selecionada()

    def selecionada(self):
        sel = self.lista.curselection()
        return self.lista.get(sel[0]).strip() if sel else None

    def mostrar_selecionada(self):
        nome = self.selecionada()
        if nome:
            M = self.mem[nome]
            linhas = [(f"{nome} ({M.rows}x{M.cols})", "titulo")]
            linhas += [(l, None) for l in core.matriz_texto(M).split("\n")]
        else:
            linhas = [
                ("Nenhuma matriz selecionada.", "fraco"),
                ("Clique em  ＋ Nova  para cadastrar.", "fraco"),
            ]
        self.escrever(self.previa, linhas)

    def nova(self):
        livres = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c not in self.mem]
        EditorMatriz(self, livres[0] if livres else "M", None, self.guardar)

    def editar(self):
        nome = self.selecionada()
        if nome:
            EditorMatriz(self, nome, self.mem[nome], self.guardar)

    def guardar(self, nome, M):
        self.mem[nome] = M
        self.atualizar_memoria(selecionar=nome)

    def remover(self):
        nome = self.selecionada()
        if nome:
            del self.mem[nome]
            self.atualizar_memoria()

    def ajustar_campos(self):
        op = self.ops[self.cb_op.get()]
        self.cb_b.configure(state="readonly" if op.nmat == 2 else "disabled")
        if op.param is None:
            self.lbl_param.grid_remove()
            self.ent_param.grid_remove()
        else:
            self.lbl_param.configure(text="Escalar k" if op.param == "k" else "Expoente n")
            self.lbl_param.grid()
            self.ent_param.grid()

    def calcular(self):
        op = self.ops[self.cb_op.get()]
        nomes = [self.cb_a.get()] + ([self.cb_b.get()] if op.nmat == 2 else [])
        if not all(n in self.mem for n in nomes):
            return self.erro("Matriz", "Cadastre e selecione as matrizes (botão 'Nova').")
        extra = []
        if op.param:
            txt = self.var_param.get().strip()
            try:
                extra = [core.numero(txt)] if op.param == "k" else [int(txt)]
            except (ValueError, TypeError, ZeroDivisionError):
                return self.erro(
                    "Valor inválido",
                    "Digite um número (3, -2.5, 1/2)."
                    if op.param == "k"
                    else "Digite um expoente inteiro (ex.: 2 ou -1).",
                )
        try:
            resultado = op.fn(*[self.mem[n] for n in nomes], *extra)
        except ValueError as e:
            return self.erro("Não foi possível calcular", str(e))
        cabecalho = [(f"{op.nome}  —  matriz {' e '.join(nomes)}", "titulo"), ("─" * 44, "fraco")]
        self.escrever(self.saida_ops, cabecalho + linhas_resultado(resultado))
        destino = self.var_salvar.get().strip().upper()
        # autovetores não são "o resultado" da operação: não vão para a memória
        primeira = (
            None
            if op.fn is core.f_autovalores
            else next((v for _, v in resultado if isinstance(v, sp.MatrixBase)), None)
        )
        if destino and primeira is not None:
            self.guardar(destino, primeira)

    # ---------- aba 2: sistemas lineares ----------
    def _montar_sistema(self):
        topo = ttk.Frame(self.aba_sis)
        topo.pack(fill="x")
        self.var_m = tk.IntVar(value=3)
        self.var_n = tk.IntVar(value=3)
        ttk.Label(topo, text="Equações").pack(side="left")
        ttk.Spinbox(
            topo, from_=1, to=MAX_DIM, width=3, textvariable=self.var_m, command=self.montar_grade
        ).pack(side="left", padx=(6, 16))
        ttk.Label(topo, text="Incógnitas").pack(side="left")
        ttk.Spinbox(
            topo, from_=1, to=MAX_DIM, width=3, textvariable=self.var_n, command=self.montar_grade
        ).pack(side="left", padx=(6, 16))
        ttk.Label(topo, text="Método").pack(side="left")
        self.rotulos_metodo = {
            **{v: k for k, v in core.METODOS.items()},
            "Comparar os três": "todos",
        }
        self.cb_metodo = self._combo(
            topo, state="readonly", width=30, values=list(self.rotulos_metodo)
        )
        self.cb_metodo.current(0)
        self.cb_metodo.pack(side="left", padx=(6, 16))
        ttk.Button(topo, text="Resolver  ⏎", style="Acento.TButton", command=self.resolver).pack(
            side="left"
        )

        painel = ttk.PanedWindow(self.aba_sis, orient="horizontal")
        painel.pack(fill="both", expand=True, pady=(12, 0))
        esq = ttk.Frame(painel)
        painel.add(esq, weight=3)
        self.dir_grafico = ttk.LabelFrame(painel, text=" Gráfico (2 incógnitas) ", padding=6)
        painel.add(self.dir_grafico, weight=2)

        eq = ttk.LabelFrame(esq, text=" Equações   a1·x1 + a2·x2 + … = b ", padding=10)
        eq.pack(fill="x")
        self.grade_sis = ttk.Frame(eq)
        self.grade_sis.pack()
        self.cel_sis = []

        saida = ttk.LabelFrame(esq, text=" Resultado ", padding=8)
        saida.pack(fill="both", expand=True, pady=(12, 0))
        quadro, self.saida_sis = self._texto(saida, "word", height=12, width=50)
        quadro.pack(fill="both", expand=True)

        self.lbl_grafico = ttk.Label(
            self.dir_grafico,
            text="O gráfico aparece quando o\nsistema tem 2 incógnitas.",
            justify="center",
            style="Muted.TLabel",
        )
        self.lbl_grafico.pack(expand=True)
        self.montar_grade()

    def montar_grade(self):
        try:
            m = max(1, min(MAX_DIM, int(self.var_m.get())))
            n = max(1, min(MAX_DIM, int(self.var_n.get())))
        except (tk.TclError, ValueError):
            return
        antigos = [[c.get() for c in lin] for lin in self.cel_sis]
        for w in self.grade_sis.winfo_children():
            w.destroy()
        self.cel_sis = []
        for i in range(m):
            lin = []
            for j in range(n + 1):
                col = j * 2 if j < n else n * 2
                e = ttk.Entry(self.grade_sis, width=6, justify="right", font=self.fontes["mono"])
                e.grid(row=i, column=col, padx=1, pady=3)
                if i < len(antigos) and len(antigos[i]) == n + 1 and j < len(antigos[i]):
                    e.insert(0, antigos[i][j])
                else:
                    e.insert(0, "0")
                lin.append(e)
                if j < n:
                    sinal = "  =" if j == n - 1 else "  +"
                    ttk.Label(self.grade_sis, text=f"x{j + 1}{sinal}", style="Muted.TLabel").grid(
                        row=i, column=col + 1, padx=(2, 4)
                    )
            self.cel_sis.append(lin)

    def resolver(self):
        try:
            M = sp.Matrix(
                [
                    [ler_celula(c, f"equação {i + 1}, coluna {j + 1}") for j, c in enumerate(lin)]
                    for i, lin in enumerate(self.cel_sis)
                ]
            )
        except ValueError as e:
            return self.erro("Valor inválido", str(e))
        A, b = M[:, :-1], M[:, -1]
        tipo, linhas = core.relatorio_sistema(A, b, self.rotulos_metodo[self.cb_metodo.get()])
        marcadas = []
        for l in linhas:
            if l.startswith("Classificação"):
                marcadas.append((l, tipo))
            elif l.startswith("—"):
                marcadas.append((l, "titulo"))
            elif l.startswith("posto"):
                marcadas.append((l, "fraco"))
            else:
                marcadas.append((l, None))
        self.escrever(self.saida_sis, marcadas)
        self.ultimo_sistema = (A, b, tipo)
        self.desenhar_grafico(A, b, tipo)

    def desenhar_grafico(self, A, b, tipo):
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        t = self.t
        estilo = {
            "fundo": t["texto_bg"],
            "texto": t["fg"],
            "grade": t["border"],
            "eixos": t["muted"],
        }
        fig = core.figura_sistema(A, b, tipo, estilo) if GRAFICO and A.cols == 2 else None
        if fig is None:
            self.lbl_grafico.configure(
                text="O gráfico aparece quando o\nsistema tem 2 incógnitas."
                if A.cols != 2
                else "Instale matplotlib para ver o gráfico."
            )
            self.lbl_grafico.pack(expand=True)
            return
        self.lbl_grafico.pack_forget()
        self.canvas = FigureCanvasTkAgg(fig, master=self.dir_grafico)
        self.canvas.get_tk_widget().configure(highlightthickness=0, background=t["texto_bg"])
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    raiz = tk.Tk()
    raiz.title("Calculadora de Matrizes")
    raiz.geometry("1020x700")
    raiz.minsize(900, 620)
    App(raiz, tema="escuro" if "--escuro" in argv else "claro")
    raiz.mainloop()


if __name__ == "__main__":
    main()
