"""Testa o menu do terminal conduzindo-o por entrada padrão."""

import os
import subprocess
import sys

import pytest


def rodar(*linhas):
    r = subprocess.run(
        [sys.executable, "-m", "matrizes"],
        input="\n".join(linhas) + "\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "NO_COLOR": "1"},
        timeout=60,
    )
    assert r.returncode == 0, r.stderr
    return r.stdout


def test_sistema_spd_por_cramer():
    saida = rodar("17", "1", "2", "2", "3 2 1", "1 -1 2", "2", "n", "0")
    assert "SPD" in saida and "det(A) = -5" in saida
    assert "x1 = -5/-5 = 1" in saida


@pytest.mark.parametrize(
    "eqs, tipo",
    [(("1 1 2", "1 1 3"), "SI"), (("1 1 2", "2 2 4"), "SPI")],
)
def test_sistema_si_e_spi(eqs, tipo):
    saida = rodar("17", "1", "2", "2", *eqs, "1", "n", "0")
    assert f"Classificação: {tipo}" in saida


def test_operacao_com_matriz_da_memoria():
    # cadastra A, calcula a inversa de A, não salva o resultado
    saida = rodar("1", "A", "2", "[[2,1],[1,1]]", "10", "A", "", "0")
    assert "1" in saida and "Matriz A salva" in saida


def test_entradas_invalidas_nao_derrubam_o_programa():
    saida = rodar("abc", "99", "0")
    assert saida.count("Opção inválida") == 2
