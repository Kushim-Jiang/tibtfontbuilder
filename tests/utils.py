from functools import cache
from pathlib import Path

import uharfbuzz
from fontTools.ttLib import TTFont


testsDir = Path(__file__).parent
repo = testsDir / ".."
tempDir = repo / "temp"
tempDir.mkdir(exist_ok=True)


@cache
def loadHBFont(path: Path) -> uharfbuzz.Font:  # type: ignore
    from uharfbuzz import Blob, Face, Font  # type: ignore

    return Font(Face(Blob.from_file_path(path)))


def parseVariants(text: str, font: Path) -> str:
    from uharfbuzz import Buffer, shape  # type: ignore

    hbFont = loadHBFont(font)
    buffer = Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    shape(hbFont, buffer)

    glyphNames: list[str] = [hbFont.glyph_to_string(info.codepoint) for info in buffer.glyph_infos]
    letters: list[str] = []
    for glyphName in glyphNames:
        name = glyphName.removesuffix("-tibt")
        parts = name.split("_")
        letters.extend(parts)
    return " ".join(letters)


def makeFontFilename(font: TTFont) -> str:
    from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e

    table: table__n_a_m_e = font["name"]  # type: ignore
    postScriptName = table.getDebugName(6)
    assert postScriptName

    suffix = ".otf" if {"CFF ", "CFF2"}.intersection(font.keys()) else ".ttf"
    return postScriptName + suffix
