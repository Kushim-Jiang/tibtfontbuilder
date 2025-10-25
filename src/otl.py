from __future__ import annotations

import yaml
from .lib_.spec import FontSpec, GlyphSpec
from tptq.feacomposer import FeaComposer


def getData(dir: str):
    with open(dir, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


VARIANTS: dict[str, list[dict[str, str | int | list[str]]]] = getData("src/data_/letter.yaml")
CATEGORIES: dict[str, list[str]] = getData("src/data_/category.yaml")

LAB = True


def getGlyphName(cp: int) -> str:
    for variants in VARIANTS.values():
        for variant in variants:
            if "cp" in variant and variant["cp"] == cp:
                assert isinstance(variant["name"], str)
                return variant["name"]
    return ""


class TibtFeaComposer(FeaComposer):
    def __init__(self, cmap: dict[int, str], glyphs: list[str]) -> None:
        self.cmap = cmap
        self.glyphs = glyphs

        self.spec = FontSpec(cmap={}, newGlyphs={}, openTypeCategories={})

        self.classes = {}
        self.conditions = {}

        super().__init__(languageSystems={"tibt": {"dflt"}}, glyphNameProcessor=(lambda x: x + "-tibt"))

    def compose(self) -> FontSpec:
        self.initVariants()
        self.ia(self)
        self.iia(self)
        self.iib(self)
        self.iic(self)
        return self.spec

    def initVariants(self) -> None:
        for letter, variants in VARIANTS.items():
            variantNames: list[str] = []
            for variant in variants:
                assert isinstance(variant["name"], str)
                if self.glyphNameProcessor(variant["name"]) not in self.glyphs:
                    self.spec.newGlyphs[variant["name"]] = GlyphSpec([])
                variantNames.append(variant["name"])
            self.classes[letter] = self.namedGlyphClass(letter, variantNames)

        for category, letters in CATEGORIES.items():
            letters = [self.classes[letter] for letter in letters]
            self.classes[category] = self.namedGlyphClass(category, letters)

        subGlyphs = ["aa", "u"]
        for letter, variants in VARIANTS.items():
            for variant in variants:
                assert isinstance(variant["name"], str)
                if "Sub" in variant["name"]:
                    subGlyphs.append(variant["name"])
        self.classes["sub"] = self.namedGlyphClass("subGlyphs", subGlyphs)

    def ia(self, c: TibtFeaComposer) -> None:
        with c.Lookup("Ia.letters.decomposition", feature="ccmp"):
            for variants in VARIANTS.values():
                for variant in variants:
                    if "decompose" in variant:
                        assert isinstance(variant["cp"], int)
                        nominal = getGlyphName(variant["cp"])
                        decomposed = variant["decompose"]
                        assert isinstance(decomposed, list)
                        c.sub(nominal, by=decomposed)

        with c.Lookup("Ia.letters.composition", feature="ccmp"):
            for variants in VARIANTS.values():
                for variant in variants:
                    if "compose" in variant:
                        assert isinstance(variant["cp"], int)
                        nominal = getGlyphName(variant["cp"])
                        composed = variant["compose"]
                        assert isinstance(composed, list)
                        c.sub(*composed, by=nominal)

    def iia(self, c: TibtFeaComposer) -> None:
        cl = self.classes

        # rago
        letters = c.namedGlyphClass(
            "ragoConsonants",
            [letter + "Sub" for letter in CATEGORIES["consonant"] if letter not in ["nya", "la", "ra", "wa", "ya"]],
        )
        with c.Lookup("IIa.ra.rago", feature="rclt", flags={"UseMarkFilteringSet": letters}):
            c.sub(c.input("ra"), letters, by="rago")

            if LAB:
                letters = c.glyphClass(["nyaSub", "laSub"])
                c.sub(c.input("rha"), letters, by="rago")
                if 0x200D in self.cmap:
                    c.sub(c.input("ra"), self.cmap[0x200D], by="rago")

        with c.Lookup("IIa.rha.postprocessing", feature="rclt"):
            c.sub("rha", by="ra")

        # mirror
        with c.Lookup("_.mirror") as mirLookup:
            for letter in ["wata", "rata", "yata"]:
                c.sub(letter + "Sub", by=letter + "SubMir")

        mirConsonants = c.namedGlyphClass(
            "mirConsonants",
            [cl["tta"], cl["ttha"], cl["dda"], cl["nna"], cl["ssa"], cl["kka"], cl["rra"], "wataSubMir", "rataSubMir"],
        )
        with c.Lookup("IIa.mirror.consonants", feature="rclt", flags={"UseMarkFilteringSet": self.classes["sub"]}):
            c.sub(mirConsonants, c.input(c.glyphClass(["wataSub", "rataSub", "yataSub"]), mirLookup), by=None)

    def iib(self, c: TibtFeaComposer) -> None:
        ligatures = {}
        maxCompCount = 0
        for glyph in self.glyphs:
            if "_" in glyph:
                components = glyph.split("_")
                ligatures[glyph] = components
                if len(components) > maxCompCount:
                    maxCompCount = len(components)

        with c.Lookup("IIb.ligatures", feature="rlig"):
            for compCount in range(maxCompCount, 1, -1):
                for ligature, components in ligatures.items():
                    if len(components) == compCount:
                        c.sub(*components, by=ligature)

    def iic(self, c: TibtFeaComposer) -> None:
        pass


if __name__ == "__main__":
    composer = TibtFeaComposer(cmap={0x200D: "zwj"}, glyphs=["aa_iMir"])
    spec = composer.compose()
    code = composer.asFeatureFile().asFea()
    print(code)
    print(spec)
