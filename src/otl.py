from __future__ import annotations

import yaml
from lib_.spec import FontSpec
from tptq.feacomposer import FeaComposer


def getData():
    with open("src/data_/letter.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


TIBT_DATA: dict[str, list[dict[str, str | int | list[str]]]] = getData()


def getGlyphName(cp: int) -> str:
    for variants in TIBT_DATA.values():
        for variant in variants:
            if "cp" in variant and variant["cp"] == cp:
                return variant["name"]


class TibtFeaComposer(FeaComposer):
    def __init__(self) -> None:
        self.spec = FontSpec(cmap={}, newGlyphs={}, openTypeCategories={})
        super().__init__(languageSystems={"tibt": {"dflt"}})

    def compose(self) -> FontSpec:
        self.ia(self)
        return self.spec

    def ia(self, c: TibtFeaComposer) -> None:
        with c.Lookup("Ia.letters.decomposition", feature="ccmp"):
            for variants in TIBT_DATA.values():
                for variant in variants:
                    if "decompose" in variant:
                        nominal = getGlyphName(variant["cp"])
                        decomposed = variant["decompose"]
                        c.sub(nominal, by=decomposed)


if __name__ == "__main__":
    composer = TibtFeaComposer()
    spec = composer.compose()
    code = composer.asFeatureFile().asFea()
    print(code)
