"""Constantes e valores padrão da interface web (sem dependência do Streamlit)."""

from .. import __version__

NOME_APP = "Calculadora de Matrizes"
SUBTITULO = "Plataforma de Álgebra Linear: calcule, experimente, visualize e aprenda"
VERSAO = __version__

MAX_DIM = 8  # dimensão máxima de matrizes no editor
LIMITE_HISTORICO = 200

TEMAS_OPCOES = ("sistema", "claro", "escuro")
ROTULOS_TEMA = {"sistema": "Automático (sistema)", "claro": "Claro", "escuro": "Escuro"}

PREFERENCIAS_PADRAO = {
    "tema": "sistema",
    "aproximacao": True,  # mostrar valor decimal ao lado de resultados exatos
    "casas": 4,  # casas decimais das aproximações
    "mostrar_passos": True,  # abrir o passo a passo junto do resultado
    "grade_geometria": True,  # mostrar a malha nas visualizações 2D
}
