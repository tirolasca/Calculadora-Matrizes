# Calculadora de Matrizes

[![CI](https://github.com/tirolasca/Calculadora-Matrizes/actions/workflows/ci.yml/badge.svg)](https://github.com/tirolasca/Calculadora-Matrizes/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-web-FF4B4B?logo=streamlit&logoColor=white)
![SymPy](https://img.shields.io/badge/SymPy-exato-3B5526?logo=sympy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-gr%C3%A1ficos-11557c)
![Ruff](https://img.shields.io/badge/lint-ruff-D7FF64?logo=ruff&logoColor=black)
![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-green)

Calculadora de **matrizes e sistemas lineares** com três interfaces: uma **plataforma web educacional** (Streamlit), uma **janela** (tkinter, com tema claro e escuro) e um **menu no terminal**. Resolve sistemas por escalonamento, regra de Cramer ou matriz inversa e **classifica** cada um como **SPD**, **SPI** ou **SI**.

Todas as contas usam aritmética **exata** (frações, via [SymPy](https://www.sympy.org)), sem erros de arredondamento: `1/3` continua `1/3`.

<p align="center">
  <img src="docs/web-inicio.png" width="92%" alt="Painel inicial da plataforma web, com cabeçalho animado, indicadores e atalhos">
</p>

## Sumário

- [Tecnologias e bibliotecas](#tecnologias-e-bibliotecas)
- [Recursos](#recursos)
- [Plataforma web (Streamlit)](#plataforma-web-streamlit)
- [Instalação](#instalação) · [Uso](#uso) · [Desenvolvimento](#desenvolvimento)

## Tecnologias e bibliotecas

### Linguagem e execução

| Tecnologia | Para que serve no projeto |
| --- | --- |
| [**Python 3.11+**](https://www.python.org) | Linguagem de todo o projeto (testado de 3.11 a 3.15) |
| [**tkinter**](https://docs.python.org/3/library/tkinter.html) | Interface de janela, com tema claro e escuro (já vem com o Python) |
| [**Streamlit**](https://streamlit.io) | Plataforma web: navegação, widgets, temas, atalhos de teclado e hospedagem no Community Cloud |

### Bibliotecas de execução

Instaladas por `pip install -e ".[web]"` (veja `pyproject.toml` e `requirements.txt`).

| Biblioteca | Versão | Uso |
| --- | --- | --- |
| [**SymPy**](https://www.sympy.org) | `>=1.14.0,<1.15.0` | Álgebra exata: matrizes, determinante, autovalores, decomposições, pseudo-inversa, espaços fundamentais |
| [**mpmath**](https://mpmath.org) | (vem com o SymPy) | Valores singulares e autovalores numéricos com 30 dígitos |
| [**Matplotlib**](https://matplotlib.org) | `>=3.11.2` | Gráfico das retas de um sistema 2×2 e visualizações geométricas |
| [**Rich**](https://github.com/Textualize/rich) | `>=15.0.0` | Menu e tabelas coloridos no terminal |
| [**Streamlit**](https://streamlit.io) | `>=1.67.0` | Interface web (extra opcional `web`) |
| [**KaTeX**](https://katex.org) | (embutido no Streamlit) | Renderiza as fórmulas LaTeX do passo a passo |

### Interface web: como o visual é feito

- **CSS próprio** injetado pelo app: variáveis de cor para os temas claro/escuro, transições, efeitos de foco e *hover*, e animações de entrada (`@keyframes`).
- **Ícones SVG embutidos** (`matrizes/web/components/icones.py`): sem fontes de ícones nem arquivos externos; herdam a cor do tema e são "desenhados" na entrada.
- **Material Symbols** (nativos do Streamlit) nos botões e no menu lateral.
- **Fontes** [Inter](https://rsms.me/inter/) e [JetBrains Mono](https://www.jetbrains.com/lp/mono/) via Google Fonts, com *fallback* para as fontes do sistema.
- As animações respeitam `prefers-reduced-motion` e podem ser desligadas em **Configurações**.

### Qualidade e automação

| Ferramenta | Uso |
| --- | --- |
| [**pytest**](https://pytest.org) | Testes do núcleo, do terminal, da janela e da web (com o `AppTest` do Streamlit) |
| [**Ruff**](https://docs.astral.sh/ruff/) | Lint e formatação |
| [**mypy**](https://mypy-lang.org) | Checagem de tipos da interface web |
| [**GitHub Actions**](https://github.com/features/actions) | Integração contínua em Linux, Windows e macOS |
| [**Dependabot**](https://docs.github.com/code-security/dependabot) | Atualização mensal de dependências e *workflows* |
| [**Dev Containers**](https://containers.dev) | Ambiente pronto no VS Code e no GitHub Codespaces |
| [**setuptools**](https://setuptools.pypa.io) | Empacotamento (`pyproject.toml`) e comandos de console |

## Recursos

| Área | O que faz |
| --- | --- |
| **Memória de matrizes** | Cadastre A, B, C… e reutilize em qualquer operação; resultados podem ser guardados com um nome |
| **Operações** | soma, subtração, multiplicação, escalar, potência (inclusive negativa), transposta, inversa, adjunta, cofatores, **produto de Hadamard**, **produto de Kronecker** e **pseudo-inversa de Moore-Penrose** |
| **Propriedades** | determinante, posto, traço, RREF, autovalores e autovetores, LU, QR, Cholesky, diagonalização, **espaços fundamentais** (Col, Lin, núcleo e núcleo à esquerda) e **normas com número de condição** |
| **Sistemas lineares** | resolve e classifica em **SPD** (solução única), **SPI** (infinitas soluções, com a solução geral) ou **SI** (sem solução), pelo teorema de Rouché-Capelli |
| **Métodos** | escalonamento (Gauss-Jordan), regra de Cramer, matriz inversa (`x = A⁻¹·b`) ou comparar os três |
| **Gráfico** | para sistemas com 2 incógnitas, desenha as retas (e mostra se cruzam, coincidem ou são paralelas) |

A regra de Cramer e a matriz inversa só se aplicam a sistemas quadrados com `det(A) ≠ 0`. Nos demais casos o programa explica o motivo e indica o escalonamento, que resolve qualquer sistema.

Números podem ser digitados como inteiros, decimais ou frações: `3`, `-2.5`, `1/2`.

<p align="center">
  <img src="docs/gui-operacoes.png" width="48%" alt="Operações com matrizes na janela">
  <img src="docs/gui-sistemas.png" width="48%" alt="Sistema linear classificado como SPD na janela">
</p>

## Plataforma web (Streamlit)

Calcule, experimente, visualize e aprenda: a mesma matemática do terminal e da janela, com **passo a passo em LaTeX**, laboratório, geometria e exercícios.

<p align="center">
  <img src="docs/web-operacoes.png" width="48%" alt="Editor de matrizes com colchetes e resultado da soma">
  <img src="docs/web-sistemas.png" width="48%" alt="Sistema linear classificado como SPD">
</p>
<p align="center">
  <img src="docs/web-transformacoes.png" width="48%" alt="Transformações lineares no plano">
  <img src="docs/web-escuro.png" width="48%" alt="Modo escuro">
</p>

### Novidades da versão 1.1

| | |
| --- | --- |
| **Visual** | Cabeçalho animado (um quadrado unitário sendo transformado por uma matriz), ícones SVG, cartões que reagem ao mouse, entrada escalonada dos blocos, botões com gradiente e foco acessível |
| **Editor de matrizes** | Grade com **colchetes**, fonte monoespaçada, **colar matriz de texto** (`[[1,2],[3,4]]`, `1 2; 3 4`, CSV ou uma linha por linha), **transpor** e **trocar sinais** no próprio editor, mais predefinidas (Vandermonde, Pascal, anti-identidade) |
| **Resultados** | Bloco **Copiar ou exportar**: LaTeX com botão de copiar e download em **CSV** e **.tex** |
| **Produtividade** | **Ctrl+Enter** calcula; indicador de carregamento; interruptor de **modo escuro** na barra lateral |
| **Cálculo** | 5 operações novas: Hadamard, Kronecker, pseudo-inversa, espaços fundamentais, normas e número de condição |
| **Configurações** | Liga/desliga as animações |

### Páginas

| Grupo | Páginas |
| --- | --- |
| **Calculadora** | Operações · Propriedades e decomposições (LU, QR, Cholesky, diagonalização) · Sistemas (Gauss, Cramer, inversa) |
| **Laboratório** | Experimentação (antes/depois das propriedades, experimentos guiados) · Transformações lineares · Comparação de matrizes e propriedades algébricas · Visualização geométrica (vetores, span, autovetores) |
| **Aprendizado** | Conceitos · Passo a passo · Exemplos resolvidos · Exercícios (3 níveis, correção e solução explicada) |
| **Ferramentas** | Histórico · Matrizes salvas · Configurações (tema, animações, exportar/importar sessão) |

```bash
pip install -e ".[web]"
calculadora-matrizes-web            # ou: streamlit run streamlit_app.py
```

Aceita frações, decimais e expressões (`1/2`, `sqrt(2)`, `2*pi`, parâmetros como `a`). Os passos mostrados são **conferidos contra o núcleo**; quando não há explicação confiável (ex.: raízes irracionais de grau 3), só o resultado é exibido. As operações de pseudo-inversa, espaços fundamentais e normas exigem números (sem parâmetros simbólicos).

**Publicar no Streamlit Community Cloud:** em [share.streamlit.io](https://share.streamlit.io) escolha este repositório, branch `main` e o arquivo principal `streamlit_app.py` (as dependências vêm de `requirements.txt`). Depois de publicar, coloque o link aqui: `https://<seu-app>.streamlit.app`.

## Instalação

Requer **Python 3.11 ou superior**.

```bash
git clone https://github.com/tirolasca/Calculadora-Matrizes.git
cd Calculadora-Matrizes

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e .
```

> **Linux:** o tkinter (janela) pode precisar de `sudo apt install python3-tk`.
> No Windows e no macOS ele já vem com o Python.

## Uso

```bash
calculadora-matrizes-gui            # janela (ou: python -m matrizes.gui)
calculadora-matrizes-gui --escuro   # janela já no tema escuro
calculadora-matrizes                # menu no terminal (ou: python -m matrizes)
calculadora-matrizes-web            # plataforma web (precisa do extra "web")
```

Na janela: **Ctrl+Enter** executa a operação da aba atual e o botão no topo alterna entre o tema claro e o escuro.

### Exemplo: classificando um sistema

No terminal, opção `17`, e digite cada equação como os coeficientes seguidos do termo independente. O sistema

```
 2x +  y -  z =   8
-3x -  y + 2z = -11
-2x +  y + 2z =  -3
```

é digitado como `2 1 -1 8`, `-3 -1 2 -11` e `-2 1 2 -3`, e a resposta é:

```
Classificação: SPD — Sistema Possível e Determinado (solução única).
  x1 = 2
  x2 = 3
  x3 = -1
```

Exemplos de **SPI** e **SI**:

| Sistema | Classificação | Resultado |
| --- | --- | --- |
| `x + y = 2` · `2x + 2y = 4` | SPI | `x1 = 2 - x2`, com `x2` livre |
| `x + y = 2` · `x + y = 3` | SI | sem solução |

## Desenvolvimento

```bash
pip install -e ".[dev,web]"

ruff check .            # erros e estilo
ruff format .           # formatação
mypy                    # tipos (interface web)
pytest                  # testes (a janela é pulada se não houver display)
xvfb-run -a pytest      # Linux sem tela: roda também os testes da janela
```

A integração contínua (GitHub Actions, `.github/workflows/ci.yml`) roda o lint, a checagem de tipos, os testes em Linux (Python 3.11 a 3.15), Windows e macOS, e confere se o pacote é construído.

### Estrutura

```
matrizes/
├── nucleo.py   # cálculo (funções puras sobre sympy.Matrix); sem entrada/saída
├── paleta.py   # paletas claro/escuro compartilhadas
├── cli.py      # menu do terminal
├── gui.py      # janela tkinter
└── web/        # plataforma Streamlit
    ├── services/    # lógica sem UI (passo a passo, matrizes, geometria…)
    ├── components/  # editor de matrizes, painel de operações, ícones SVG, blocos visuais
    ├── pages/       # uma função `renderizar()` por página
    └── theme.py     # tema claro/escuro, CSS e animações
streamlit_app.py
tests/          # pytest: núcleo, terminal, janela e web (AppTest)
docs/           # capturas de tela e ARQUITETURA.md
```

O núcleo não imprime nem lê nada; terminal, janela e web só cuidam de entrada e exibição, e **nenhuma operação é reimplementada**. Detalhes e decisões em [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md).

## Licença

[MIT](LICENSE)
