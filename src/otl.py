from __future__ import annotations

import yaml
from lib_.spec import FontSpec
from tptq.feacomposer import FeaComposer


def get_data():
    with open("data/letter.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


TIBT_DATA = get_data()


def get_nominal_glyph(cp: int) -> str:
    for letter, variants in TIBT_DATA.items():
        for variant in variants:
            if "cp" in variant and variant["cp"] == cp:
                if "mark" in variant:
                    return letter + ".mark"
                return letter


class TibtFeaComposer(FeaComposer):

    def __init__(self) -> None:
        self.spec = FontSpec(cmap={}, newGlyphs={}, openTypeCategories={})
        super().__init__(languageSystems={"tibt": {"dflt"}})

    def compose(self) -> FontSpec:
        self.ia(self)
        return self.spec

    def ia(self, c: TibtFeaComposer) -> None:
        with c.Lookup("Ia.consonant.decomposing", feature="ccmp"):
            for variants in TIBT_DATA.values():
                for variant in variants:
                    if "decompose" in variant:
                        nominal = get_nominal_glyph(variant["cp"])
                        decomposed = [get_nominal_glyph(cp) for cp in variant["decompose"]]
                        c.sub(nominal, by=decomposed)


if __name__ == "__main__":
    composer = TibtFeaComposer()
    spec = composer.compose()
    code = composer.asFeatureFile().asFea()
    print(code)
