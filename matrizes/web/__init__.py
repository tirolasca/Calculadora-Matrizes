"""Interface web (Streamlit) da calculadora.

Este ``__init__`` não importa o Streamlit: ``matrizes.web.services`` é Python puro e pode ser
reutilizado por outras interfaces (por exemplo, uma API FastAPI). Só ``app``, ``state``,
``theme``, ``components`` e ``pages`` dependem do Streamlit.
"""
