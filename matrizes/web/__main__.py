"""Inicia a interface web: ``calculadora-matrizes-web`` ou ``python -m matrizes.web``."""

import sys
from pathlib import Path


def main() -> None:
    try:
        from streamlit.web import cli as stcli
    except ImportError:
        sys.exit(
            "Streamlit não está instalado. Instale com:  pip install 'calculadora-matrizes[web]'"
        )
    app = Path(__file__).with_name("app.py")
    sys.argv = ["streamlit", "run", str(app), *sys.argv[1:]]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
