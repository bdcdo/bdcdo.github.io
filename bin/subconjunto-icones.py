# /// script
# requires-python = ">=3.11"
# dependencies = ["fonttools[woff]==4.56.0"]
# ///
"""Gera, a partir das fontes completas em _fonts-completas/, as fontes de ícone servidas em assets/, só com os glifos que o tema usa.

As fontes completas (Font Awesome 6 Free, Academicons e Tabler Icons) somam mais de 7 MB para
cerca de 60 ícones que aparecem nos templates. O navegador baixava, por exemplo, 730 KB do
tabler-icons-outline.woff2 para desenhar um único glifo, o do botão de tema.

Regra: entra todo ícone cuja classe (fa-*, ai-*, ti-*) aparece em algum template, página, dado
ou script do tema, inclusive os de redes sociais que o _config.yml não liga hoje. Assim ligar
uma rede nova no _config.yml não exige regenerar as fontes; só um ícone que o tema nunca citou
exige rodar este script de novo.

Uso:
    uv run bin/subconjunto-icones.py            # regenera os arquivos em assets/
    uv run bin/subconjunto-icones.py --check    # falha se os arquivos em assets/ estiverem defasados (CI)

A versão do fonttools é fixa no cabeçalho para a saída ser idêntica byte a byte entre máquinas,
que é o que o modo --check compara.
"""

from __future__ import annotations

import argparse
import filecmp
import logging
import re
import sys
import tempfile
from pathlib import Path

from fontTools import subset

# O fonttools avisa sobre tabelas que não sabe subdividir (FFTM) e carimbos de data estranhos
# das fontes de ícone; nada disso muda o resultado, então só erro aparece.
logging.getLogger("fontTools").setLevel(logging.ERROR)

RAIZ = Path(__file__).resolve().parent.parent
COMPLETAS = RAIZ / "_fonts-completas"

# Onde procurar classes de ícone. _sass fica de fora porque define todas as classes.
ONDE_PROCURAR = [
    "_includes",
    "_layouts",
    "_pages",
    "_posts",
    "_projects",
    "_news",
    "_data",
    "_bibliography",
    "_config.yml",
    "assets/js",
]
EXTENSOES = {".liquid", ".html", ".md", ".yml", ".yaml", ".bib", ".js"}
PADRAO_CLASSE = re.compile(r"\b(fa|ai|ti)-([a-z0-9][a-z0-9-]*)\b")

# (origem em _fonts-completas, destino em assets sem extensão, prefixo das classes)
FONTES = [
    ("webfonts/fa-solid-900.ttf", "assets/webfonts/fa-solid-900", "fa"),
    ("webfonts/fa-regular-400.ttf", "assets/webfonts/fa-regular-400", "fa"),
    ("webfonts/fa-brands-400.ttf", "assets/webfonts/fa-brands-400", "fa"),
    ("fonts/academicons.ttf", "assets/fonts/academicons", "ai"),
    ("fonts/tabler-icons.ttf", "assets/fonts/tabler-icons", "ti"),
    ("fonts/tabler-icons-filled.ttf", "assets/fonts/tabler-icons-filled", "ti"),
    ("fonts/tabler-icons-outline.ttf", "assets/fonts/tabler-icons-outline", "ti"),
]


def classes_usadas() -> dict[str, set[str]]:
    """Nomes de ícone citados nos templates, por prefixo. Inclui ruído como fa-solid ou fa-sm,
    que não tem glifo e é descartado no mapeamento."""
    usadas: dict[str, set[str]] = {"fa": set(), "ai": set(), "ti": set()}
    for item in ONDE_PROCURAR:
        caminho = RAIZ / item
        arquivos = (
            [caminho]
            if caminho.is_file()
            else [p for p in caminho.rglob("*") if p.suffix in EXTENSOES]
        )
        for arquivo in arquivos:
            if "vendor" in arquivo.parts or ".min." in arquivo.name:
                continue
            for prefixo, nome in PADRAO_CLASSE.findall(
                arquivo.read_text(encoding="utf-8", errors="replace")
            ):
                usadas[prefixo].add(nome)
    return usadas


def mapa_codepoints() -> dict[str, dict[str, int]]:
    """Nome do ícone -> codepoint, lido das definições que o próprio tema versiona."""
    mapa: dict[str, dict[str, int]] = {"fa": {}, "ai": {}, "ti": {}}
    fa = (RAIZ / "_sass/font-awesome/_variables.scss").read_text(encoding="utf-8")
    for nome, hexa in re.findall(
        r"^\$fa-var-([a-z0-9-]+):\s*\\([0-9a-f]+);", fa, re.MULTILINE
    ):
        mapa["fa"][nome] = int(hexa, 16)
    ai = (RAIZ / "assets/css/academicons.min.css").read_text(encoding="utf-8")
    for nome, hexa in re.findall(
        r"\.ai-([a-z0-9-]+):before\s*\{content:\s*\"\\([0-9a-f]+)\";\}", ai
    ):
        mapa["ai"][nome] = int(hexa, 16)
    for arquivo in (RAIZ / "_sass/tabler-icons").glob("*.scss"):
        for nome, hexa in re.findall(
            r"^\$ti-icon-([a-z0-9-]+):\s*unicode\(\"([0-9a-f]+)\"\);",
            arquivo.read_text(encoding="utf-8"),
            re.MULTILINE,
        ):
            mapa["ti"][nome] = int(hexa, 16)
    return mapa


def codepoints_por_prefixo() -> dict[str, list[int]]:
    usadas, mapa = classes_usadas(), mapa_codepoints()
    saida = {}
    for prefixo in usadas:
        encontrados = sorted(
            {mapa[prefixo][n] for n in usadas[prefixo] if n in mapa[prefixo]}
        )
        saida[prefixo] = encontrados
    return saida


def gerar(origem: Path, destino_base: Path, codepoints: list[int]) -> None:
    """Escreve <destino>.woff2 e <destino>.ttf com os codepoints pedidos. Glifo que a fonte não
    tem é ignorado (uma lista única serve às três famílias do Font Awesome, por exemplo).

    Usa a API em vez de subset.main() para a configuração de log acima valer; o main() reconfigura
    o logger a cada chamada. As classes de ícone chegam ao glifo pelo cmap (content: "\\f0e0"),
    então as tabelas de layout (ligaduras e kerning) não fazem falta; descartá-las também contorna
    a tabela GSUB malformada das fontes do Tabler, que faz o fonttools abortar ao fechar ligaduras.
    O carimbo de data não é recalculado para a saída ser idêntica entre rodadas."""
    destino_base.parent.mkdir(parents=True, exist_ok=True)
    for sufixo, flavor in ((".woff2", "woff2"), (".ttf", None)):
        opcoes = subset.Options()
        opcoes.flavor = flavor
        opcoes.recalc_timestamp = False
        opcoes.layout_closure = False
        opcoes.drop_tables = list(opcoes.drop_tables) + ["GSUB", "GPOS", "GDEF"]
        fonte = subset.load_font(str(origem), opcoes)
        subdivisor = subset.Subsetter(opcoes)
        subdivisor.populate(unicodes=codepoints)
        subdivisor.subset(fonte)
        subset.save_font(fonte, f"{destino_base}{sufixo}", opcoes)
        fonte.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="não escreve; falha se assets/ estiver defasado",
    )
    args = parser.parse_args()

    por_prefixo = codepoints_por_prefixo()
    for prefixo, lista in por_prefixo.items():
        print(f"{prefixo}: {len(lista)} glifos")

    defasados = []
    with tempfile.TemporaryDirectory() as tmp:
        for origem_rel, destino_rel, prefixo in FONTES:
            origem = COMPLETAS / origem_rel
            if not origem.exists():
                print(f"ERRO: falta a fonte completa {origem}", file=sys.stderr)
                return 2
            destino = (Path(tmp) / destino_rel) if args.check else (RAIZ / destino_rel)
            gerar(origem, destino, por_prefixo[prefixo])
            for sufixo in (".woff2", ".ttf"):
                gerado = Path(f"{destino}{sufixo}")
                if args.check:
                    atual = RAIZ / f"{destino_rel}{sufixo}"
                    if not atual.exists() or not filecmp.cmp(
                        gerado, atual, shallow=False
                    ):
                        defasados.append(str(atual.relative_to(RAIZ)))
                else:
                    print(
                        f"  {gerado.relative_to(RAIZ)}: {origem.stat().st_size // 1024} KB -> {gerado.stat().st_size / 1024:.1f} KB"
                    )

    if args.check:
        if defasados:
            print(
                "Fontes de ícone defasadas; rode `uv run bin/subconjunto-icones.py` e commite:",
                *defasados,
                sep="\n  ",
            )
            return 1
        print("Fontes de ícone em dia.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
