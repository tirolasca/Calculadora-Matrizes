"""Garantias de arquitetura: o núcleo e os serviços não dependem do Streamlit."""

import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2] / "matrizes"


def importa_streamlit(codigo: str) -> bool:
    """Roda `codigo` num processo limpo e diz se o Streamlit acabou importado."""
    prog = f"import sys\n{codigo}\nsys.exit(1 if 'streamlit' in sys.modules else 0)"
    return (
        subprocess.run(
            [sys.executable, "-c", prog], capture_output=True, cwd=RAIZ.parent
        ).returncode
        == 1
    )


@pytest.mark.parametrize(
    "modulo",
    [
        "matrizes.nucleo",
        "matrizes.paleta",
        "matrizes.cli",
        "matrizes.web",
        "matrizes.web.config",
        "matrizes.web.services.matrix_service",
    ],
)
def test_modulos_puros_nao_importam_streamlit(modulo):
    assert not importa_streamlit(f"import {modulo}")


def test_codigo_dos_servicos_e_do_nucleo_nao_menciona_streamlit():
    arquivos = [
        RAIZ / "nucleo.py",
        RAIZ / "cli.py",
        RAIZ / "gui.py",
        *(RAIZ / "web" / "services").glob("*.py"),
    ]
    for arq in arquivos:
        texto = arq.read_text(encoding="utf-8")
        assert "import streamlit" not in texto and "from streamlit" not in texto, arq.name


def test_gui_e_cli_nao_importam_o_pacote_web():
    for arq in (RAIZ / "nucleo.py", RAIZ / "cli.py", RAIZ / "gui.py"):
        assert "matrizes.web" not in arq.read_text(encoding="utf-8"), arq.name
