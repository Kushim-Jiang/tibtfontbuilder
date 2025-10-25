import csv
import sys
from importlib.resources import files
from os import environ
from os.path import relpath
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import pytest
from _pytest.mark.structures import ParameterSet
from fontTools.ttLib import TTFont
from ufo2ft import OTFCompiler
from ufo2ft.constants import CFFOptimization
from ufoLib2 import Font
from utils import parseVariants, tempDir, testsDir

import data
from src.lib_.spec import applySpecToFont
from src.otl import TibtFeaComposer


input = testsDir / "tibetan.ufo"
intermediate = tempDir / input.name
output = intermediate.with_suffix(".otf")


compiler = OTFCompiler(
    useProductionNames=False,
    optimizeCFF=CFFOptimization.NONE,
)
environ["FONTTOOLS_LOOKUP_DEBUGGING"] = "1"
if not intermediate.exists():
    intermediate.parent.mkdir(parents=True, exist_ok=True)

srcFont = Font.open(input)
try:
    composer = TibtFeaComposer(
        cmap={j: i.removesuffix("-tibt") for i in srcFont.keys() for j in srcFont[i].unicodes},
        glyphs=[i.removesuffix("-tibt") for i in srcFont.keys()],
    )
    spec = composer.compose()
    applySpecToFont(spec, srcFont)
    srcFont.features.text = composer.asFeatureFile().asFea()
    srcFont.save(intermediate, overwrite=True)
except Exception:
    raise

font: TTFont = compiler.compile(Font.open(intermediate))
font.save(output)
print(relpath(output))


def loadTestCases(
    font: Path,
    test_info: list[str],
) -> list[tuple[str, str, str] | ParameterSet]:
    test_cases: list[tuple[str, str, str] | ParameterSet] = []
    for testSet in test_info:
        file_path = files(data) / f"{testSet}.tsv"
        with open(file_path, "r", encoding="utf-8") as f:  # type: ignore
            rules = [tuple(i) for i in csv.reader(f, delimiter="\t") if i and not i[0].startswith("#")]
        for index, letters, goal in rules:
            try:
                test_case = (
                    f"{testSet} > {index}",
                    parseVariants(letters, font),
                    goal,
                )
                test_cases.append(test_case)
            except AssertionError as e:
                pytest.fail(f"ind:  {testSet} > {index}\n" f"code: {letters}\n" f"parsedText: {letters}\n" f"err:  \n  {e}")
    return test_cases
