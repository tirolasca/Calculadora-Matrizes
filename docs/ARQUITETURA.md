# Arquitetura

Três interfaces (terminal, janela, web) compartilham **um único núcleo matemático**.

```
matrizes/
├── nucleo.py            # cálculo: funções puras sobre sympy.Matrix (sem E/S, sem UI)
├── paleta.py            # paletas claro/escuro compartilhadas (janela e web)
├── cli.py               # menu do terminal              ┐
├── gui.py               # janela tkinter                ├─ só entrada/saída
└── web/                 # plataforma Streamlit          ┘
    ├── app.py           # configuração, tema, st.navigation
    ├── paginas.py       # mapa da navegação (grupos da barra lateral)
    ├── state.py         # EstadoApp em st.session_state
    ├── theme.py         # CSS/paleta (gerar_css é puro)
    ├── config.py        # constantes
    ├── services/        # lógica SEM Streamlit (testável sem navegador)
    │   ├── matrix_service.py     # parser seguro, predefinidas, memória, histórico, análises
    │   ├── calc_service.py       # núcleo + passo a passo para uma operação
    │   ├── step_service.py       # passo a passo em LaTeX, validado contra o núcleo
    │   ├── lab_service.py        # modificações e experimentos guiados
    │   ├── geometry_service.py   # transformações 2D, det↔área, span, autovetores
    │   ├── education_service.py  # conceitos, exemplos, exercícios + correção
    │   └── chart_service.py      # figuras matplotlib
    ├── components/      # peças de UI reutilizáveis (editor de matrizes, painel de operações…)
    └── pages/           # uma função `renderizar()` por página
streamlit_app.py         # entrada para `streamlit run` e Streamlit Community Cloud
```

## Regras (verificadas por testes em `tests/web/test_arquitetura.py`)

- `nucleo`, `paleta`, `cli`, `web.config` e `web.services.*` **não importam o Streamlit**.
- `nucleo`, `cli` e `gui` **não conhecem** `matrizes.web`.
- As dependências do Streamlit são **opcionais**: `pip install ".[web]"`.

## Decisões

| Decisão | Motivo |
| --- | --- |
| Núcleo único, reutilizado | Nenhuma operação é reimplementada na web; `OPERACOES` alimenta terminal, janela e web. |
| `step_service` separado do núcleo | Explicar é diferente de calcular. Cada passo a passo é **conferido contra o núcleo** (`validar`); se divergir, lança `InconsistenciaMatematica` em vez de mostrar uma conta errada. Casos sem explicação confiável (ex.: autovalores irracionais de grau 3, escalonamento simbólico) lançam `PassosIndisponiveis` e o app só mostra o resultado. |
| Aritmética exata (SymPy) | Frações continuam frações; sem erro de arredondamento. Aproximações decimais são opcionais. |
| Parser próprio (`ast` com lista de permissões) | Nunca usa `eval`/`sympify` em texto digitado pelo usuário. |
| Estado em um único objeto (`EstadoApp`) | O Streamlit descarta chaves de widgets ao trocar de página; os dados do usuário vivem em `st.session_state["app"]`, e o editor guarda rascunhos. |
| Tema por CSS na sessão | O Streamlit não troca o tema oficial por usuário; no modo "Automático" seguimos o tema do Streamlit. |
| Tabelas em HTML, não `st.data_editor` | O canvas do editor não obedece ao tema escuro. |
| Gráficos com `matplotlib.figure.Figure` (sem `pyplot`) | Seguro entre sessões/threads do servidor. |
| Exercícios gerados por semente | Reprodutíveis; gabaritos calculados pelo núcleo, nunca escritos à mão. |

## Como estender

- **Nova operação**: escreva `f_xxx` em `nucleo.py` e registre em `OPERACOES` — aparece no terminal, na janela e na web. Para ganhar passo a passo, adicione um gerador em `step_service.GERADORES` (e um caso em `tests/web/test_step_service.py`).
- **Nova página**: crie `pages/xxx.py` com `renderizar()` e liste em `paginas.ESTRUTURA`.
