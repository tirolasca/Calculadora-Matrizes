"""Estado da sessão: tudo que precisa sobreviver aos reruns do Streamlit.

Os dados do usuário vivem em um único objeto ``EstadoApp`` guardado em ``st.session_state``
(e não em chaves de widgets, que o Streamlit descarta quando a página muda). A classe em si
não usa o Streamlit; só ``obter()`` toca em ``st.session_state``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import sympy as sp

from .config import LIMITE_HISTORICO, PREFERENCIAS_PADRAO
from .services.matrix_service import (
    Historico,
    Memoria,
    matriz_de_texto,
    matriz_para_texto,
)

CHAVE = "app"
MAX_RECENTES = 8
VERSAO_ARQUIVO = 1


@dataclass
class EstadoApp:
    memoria: Memoria = field(default_factory=Memoria)
    historico: Historico = field(default_factory=lambda: Historico(limite=LIMITE_HISTORICO))
    recentes: list[str] = field(default_factory=list)  # nomes de matrizes usadas há pouco
    preferencias: dict[str, Any] = field(default_factory=lambda: dict(PREFERENCIAS_PADRAO))
    experimentos: dict[str, dict[str, Any]] = field(default_factory=dict)
    progresso: dict[str, dict[str, Any]] = field(default_factory=dict)  # id do exercício → dados
    rascunhos: dict[str, list[list[str]]] = field(default_factory=dict)  # conteúdo dos editores

    # ---------- matrizes recentes ----------
    def registrar_uso(self, *nomes: str) -> None:
        for nome in nomes:
            if nome in self.memoria:
                if nome in self.recentes:
                    self.recentes.remove(nome)
                self.recentes.insert(0, nome)
        del self.recentes[MAX_RECENTES:]

    def limpar_recentes_inexistentes(self) -> None:
        self.recentes = [n for n in self.recentes if n in self.memoria]

    # ---------- rascunhos dos editores ----------
    def rascunho(self, chave: str) -> list[list[str]] | None:
        return self.rascunhos.get(chave)

    def definir_rascunho(self, chave: str, grade: list[list[str]]) -> None:
        self.rascunhos[chave] = [list(l) for l in grade]

    def descartar_rascunho(self, chave: str) -> None:
        self.rascunhos.pop(chave, None)

    # ---------- experimentos ----------
    def salvar_experimento(self, nome: str, matrizes: dict[str, sp.Matrix], nota: str = "") -> str:
        nome = nome.strip()
        if not nome:
            raise ValueError("Dê um nome ao experimento.")
        self.experimentos[nome] = {
            "matrizes": {k: sp.Matrix(v) for k, v in matrizes.items()},
            "nota": nota,
            "criado": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
        return nome

    def restaurar_experimento(self, nome: str) -> dict[str, sp.Matrix]:
        if nome not in self.experimentos:
            raise KeyError(nome)
        return {k: sp.Matrix(v) for k, v in self.experimentos[nome]["matrizes"].items()}

    def excluir_experimento(self, nome: str) -> None:
        self.experimentos.pop(nome, None)

    # ---------- progresso dos exercícios ----------
    def registrar_tentativa(self, id_exercicio: str, acertou: bool) -> dict[str, Any]:
        p = self.progresso.setdefault(
            id_exercicio, {"tentativas": 0, "acertos": 0, "resolvido": False}
        )
        p["tentativas"] += 1
        p["acertos"] += int(acertou)
        p["resolvido"] = p["resolvido"] or acertou
        return p

    def resumo_progresso(self) -> tuple[int, int]:
        """(exercícios resolvidos, exercícios tentados)."""
        return sum(1 for p in self.progresso.values() if p["resolvido"]), len(self.progresso)

    # ---------- exportação / importação da sessão ----------
    def exportar(self) -> str:
        dados = {
            "versao": VERSAO_ARQUIVO,
            "matrizes": self.memoria.para_dict(),
            "experimentos": {
                nome: {
                    "nota": e["nota"],
                    "criado": e["criado"],
                    "matrizes": {k: matriz_para_texto(v) for k, v in e["matrizes"].items()},
                }
                for nome, e in self.experimentos.items()
            },
            "progresso": self.progresso,
            "preferencias": self.preferencias,
        }
        return json.dumps(dados, ensure_ascii=False, indent=2)

    def importar(self, texto: str, *, substituir: bool = False) -> dict[str, int]:
        """Carrega um arquivo exportado por ``exportar``. Retorna contagens importadas."""
        try:
            dados = json.loads(texto)
            if not isinstance(dados, dict) or "matrizes" not in dados:
                raise ValueError
            experimentos = {
                nome: {
                    "nota": str(e.get("nota", "")),
                    "criado": str(e.get("criado", "")),
                    "matrizes": {
                        k: matriz_de_texto([[str(c) for c in lin] for lin in g])
                        for k, g in e["matrizes"].items()
                    },
                }
                for nome, e in dados.get("experimentos", {}).items()
            }
            n_mat = self.memoria.carregar_dict(dados["matrizes"], substituir=substituir)
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError, ValueError):
            raise ValueError(
                "Arquivo inválido: esperado um JSON exportado por esta calculadora."
            ) from None
        if substituir:
            self.experimentos = {}
        self.experimentos.update(experimentos)
        for id_ex, p in dados.get("progresso", {}).items():
            if isinstance(p, dict) and {"tentativas", "acertos", "resolvido"} <= set(p):
                self.progresso[id_ex] = p
        for chave, valor in dados.get("preferencias", {}).items():
            if chave in PREFERENCIAS_PADRAO and type(valor) is type(PREFERENCIAS_PADRAO[chave]):
                self.preferencias[chave] = valor
        return {"matrizes": n_mat, "experimentos": len(experimentos)}

    def pref(self, chave: str) -> Any:
        return self.preferencias.get(chave, PREFERENCIAS_PADRAO[chave])


def obter() -> EstadoApp:
    """Estado da sessão atual (criado na primeira chamada)."""
    import streamlit as st

    if CHAVE not in st.session_state:
        st.session_state[CHAVE] = EstadoApp()
    return st.session_state[CHAVE]
