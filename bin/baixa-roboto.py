"""Traz a Roboto do Google Fonts para o próprio site: assets/fonts/roboto/*.woff2 e assets/css/roboto.css.

Servir a fonte daqui tira do caminho da primeira pintura uma folha de estilo bloqueante de outra
origem (fonts.googleapis.com) e a conexão a fonts.gstatic.com. Só os subconjuntos latin e
latin-ext entram, que cobrem o português; o navegador escolhe pelo unicode-range, como fazia com
o CSS do Google.

Uso: python3 bin/baixa-roboto.py   (só a biblioteca padrão; rodar de novo substitui os arquivos)
"""

from __future__ import annotations

import re
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
URL_CSS = "https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
# O Google serve woff2 só a navegadores que o anunciam pelo User-Agent.
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
SUBCONJUNTOS = ("latin", "latin-ext")
DESTINO_FONTES = RAIZ / "assets/fonts/roboto"
DESTINO_CSS = RAIZ / "assets/css/roboto.css"


def baixar(url: str) -> bytes:
    with urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": UA})
    ) as resposta:
        return resposta.read()


def main() -> None:
    css = baixar(URL_CSS).decode("utf-8")
    blocos = re.findall(r"/\* ([a-z-]+) \*/\n(@font-face \{.*?\})", css, re.DOTALL)
    DESTINO_FONTES.mkdir(parents=True, exist_ok=True)
    saida = [
        "/* Roboto (Apache 2.0), servida daqui. Gerado por bin/baixa-roboto.py a partir do CSS do Google Fonts;",
        "   não editar à mão. */",
    ]
    for subconjunto, bloco in blocos:
        if subconjunto not in SUBCONJUNTOS:
            continue
        peso = re.search(r"font-weight: (\d+)", bloco).group(1)
        url = re.search(
            r"url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)", bloco
        ).group(1)
        nome = f"roboto-{peso}-{subconjunto}.woff2"
        (DESTINO_FONTES / nome).write_bytes(baixar(url))
        bloco_local = bloco.replace(url, f"../fonts/roboto/{nome}")
        saida.append(f"/* {subconjunto} */\n{bloco_local}")
        print(f"{nome}: {(DESTINO_FONTES / nome).stat().st_size // 1024} KB")
    DESTINO_CSS.write_text("\n".join(saida) + "\n", encoding="utf-8")
    print(f"{DESTINO_CSS.relative_to(RAIZ)} com {len(saida) - 2} @font-face")


if __name__ == "__main__":
    main()
