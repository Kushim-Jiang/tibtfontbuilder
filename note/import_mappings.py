"""Import the character-set mapping tables kept in ``src/data_/mapping``.

Two sources are used.

``note/20542-22238.txt`` is the transcription of GB/T 20542-2006 (Tibetan
Extension Set A) and GB/T 22238-2008 (Tibetan Extension Set B).  It is the
authority for the Ext-A / Ext-B mappings, so those tables are built from it and
never from the legacy C++ arrays.

``tibetancodecs/src/*_tab.cpp`` holds the arrays of the original conversion
engine and is the only source for the legacy code spaces (Founder DOS and
Windows, HuaGuang, TongUer).

Every sequence is stored fully decomposed (NFKD), the same form the C++ arrays
use, so the deprecated precomposed signs of the standards (U+0F73, U+0F75,
U+0F77, U+0F79, U+0F81) and the precomposed letters (U+0F43, U+0F69, U+0F76,
...) never appear in the data.

Every table is written in the same format::

    name:        table identifier, ``<source>-<target>``
    title:       human readable description
    source:      code space of the left hand side
    target:      code space of the right hand side
    sourceStart: first code of the left hand side, when the source is contiguous
    entries:     ``[from, to]`` pairs, where each side is a code or a code sequence

Codes are hexadecimal in every code space except ``hg``, whose codes are decimal
partition/bit numbers.

Usage::

    python note/import_mappings.py
    python note/import_mappings.py --source D:/Tortoise/tibetancodecs/src
"""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "src" / "data_" / "mapping"
TRUTH_PATH = ROOT / "note" / "20542-22238.txt"
DEFAULT_SOURCE = Path(r"D:\Tortoise\tibetancodecs\src")

BAD_CHAR = 0

# Code space definitions, only used for the documentation part of the YAML.
SCHEMES = {
    "basic": "Tibetan Basic Set (U+0F00-U+0FFF)",
    "exta": "Tibetan Extension Set A (U+F300-U+F8FF)",
    "extb": "Tibetan Extension Set B (U+F0000-U+F1645)",
    "fzdos": "Founder (FangZheng) DOS encoding",
    "fzwin": "Founder (FangZheng) Windows encoding",
    "hg": "HuaGuang encoding, addressed by its decimal partition/bit number",
    "tonguer": "TongUer encoding",
}

# Ranges of the two Extension Sets as printed in the standards.
EXTA_START = 0xF300
EXTA_END = 0xF8FF
EXTB_START = 0xF0000
EXTB_END = 0xF1644

# name -> (source, target, title, C++ array name, sourceStart)
LEGACY_TABLES: dict[str, tuple[str, str, str, str, int | None]] = {
    "exta-fzdos": (
        "exta",
        "fzdos",
        "Tibetan Basic Set and Extension Set A to Founder DOS",
        "tabExtAtoFZDos",
        None,
    ),
    "exta-fzwin": (
        "exta",
        "fzwin",
        "Tibetan Basic Set and Extension Set A to Founder Windows",
        "tabExtAtoFZWin",
        None,
    ),
    "exta-hg": (
        "exta",
        "hg",
        "Tibetan Basic Set and Extension Set A to HuaGuang",
        "tabExtAtoHG",
        None,
    ),
    "exta-tonguer": (
        "exta",
        "tonguer",
        "Tibetan Basic Set and Extension Set A to TongUer",
        "tabExtAtoTonguer",
        None,
    ),
    "fzdos-exta": (
        "fzdos",
        "exta",
        "Founder DOS to Tibetan Extension Set A",
        "tabFZDostoExtA",
        0xC02D,
    ),
    "fzwin-exta": (
        "fzwin",
        "exta",
        "Founder Windows to Tibetan Extension Set A",
        "tabFZWintoExtA",
        0xA3A2,
    ),
    "hg-exta": (
        "hg",
        "exta",
        "HuaGuang to Tibetan Extension Set A",
        "tabHGtoExtA",
        1601,
    ),
    "tonguer-exta": (
        "tonguer",
        "exta",
        "TongUer to Tibetan Extension Set A",
        "tabTonguertoExtA",
        0x8140,
    ),
    "fzdos-fzwin": (
        "fzdos",
        "fzwin",
        "Founder DOS to Founder Windows",
        "tabFZDostoFZWin",
        None,
    ),
    "fzwin-fzdos": (
        "fzwin",
        "fzdos",
        "Founder Windows to Founder DOS",
        "tabFZWintoFZDos",
        None,
    ),
}

# The files that hold the arrays, in import order.
SOURCE_FILES = [
    "exta_fzdos_tab.cpp",
    "exta_fzwin_tab.cpp",
    "exta_hg_tab.cpp",
    "exta_tonguer_tab.cpp",
    "fzdos_exta_tab.cpp",
    "fzwin_exta_tab.cpp",
    "hg_exta_tab.cpp",
    "tonguer_exta_tab.cpp",
    "fzdos_fzwin_tab.cpp",
    "fzwin_fzdos_tab.cpp",
]

# Forward tables (tabExtAto*) cover the basic block first, then Ext-A.
BASIC_BLOCK_SIZE = 256
BASIC_BLOCK_START = 0x0F00


def decompose(sequence: Iterable[int]) -> tuple[int, ...]:
    """Fully decompose a sequence, the form the C++ arrays are written in.

    NFKD (rather than NFD) is used so that the compatibility signs U+0F77 and
    U+0F79 also lose their precomposed form.
    """

    text = unicodedata.normalize("NFKD", "".join(chr(code) for code in sequence))
    return tuple(ord(char) for char in text)


def readTruth(path: Path) -> dict[int, tuple[int, ...]]:
    """Read ``index, pua, code, sequence, transliteration`` rows into code -> sequence."""

    rows: dict[int, tuple[int, ...]] = {}
    expectedIndex = 1
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        columns = line.split("\t")
        if len(columns) != 5:
            raise SystemExit(f"{path.name}: row {expectedIndex} has {len(columns)} columns")
        index, pua, code, sequence, _ = columns
        if int(index) != expectedIndex:
            raise SystemExit(f"{path.name}: expected index {expectedIndex}, found {index}")
        if pua != chr(int(code, 16)):
            raise SystemExit(f"{path.name}: row {index} has a PUA column that is not the code")
        if not sequence:
            raise SystemExit(f"{path.name}: row {index} has an empty sequence")
        rows[int(code, 16)] = decompose(ord(char) for char in sequence)
        expectedIndex += 1

    extA = sorted(code for code in rows if code <= EXTA_END)
    extB = sorted(code for code in rows if code > EXTA_END)
    if extA != list(range(EXTA_START, EXTA_END + 1)):
        raise SystemExit(f"{path.name}: Ext-A codes are not contiguous")
    if extB != list(range(EXTB_START, EXTB_END + 1)):
        raise SystemExit(f"{path.name}: Ext-B codes are not contiguous")
    if sorted(rows) != extA + extB:
        raise SystemExit(f"{path.name}: codes outside the Extension Sets")
    return rows


def buildExtToBasic(truth: dict[int, tuple[int, ...]], low: int, high: int) -> list:
    entries = []
    for code in sorted(truth):
        if low <= code <= high:
            sequence = truth[code]
            entries.append([code, list(sequence) if len(sequence) > 1 else sequence[0]])
    return entries


def buildBasicToExt(extToBasic: list) -> list:
    """Ext-A to Basic is one-to-one, so the reverse table is its exact inverse."""

    entries = []
    for code, sequence in extToBasic:
        key = sequence if isinstance(sequence, list) else [sequence]
        entries.append([key, code])
    keys = [tuple(entry[0]) for entry in entries]
    if len(set(keys)) != len(keys):
        raise SystemExit("Ext-A to Basic is not one-to-one, cannot invert")
    return sorted(entries, key=lambda entry: tuple(entry[0]))


def parseRows(path: Path, arrayName: str) -> list[tuple[list[int], str]]:
    """Extract ``(numbers, trailing comment)`` for every row of a C array."""

    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(
        rf"extern const [\w ]+ {arrayName}\[[^\]]*\](?:\[[^\]]*\])?\s*=\s*\{{(.*?)\n\}};",
        text,
        re.S,
    )
    if not match:
        raise SystemExit(f"array {arrayName} not found in {path.name}")

    rows: list[tuple[list[int], str]] = []
    for line in match.group(1).splitlines():
        line = re.sub(r"/\*.*?\*/", "", line)
        code, _, comment = line.partition("//")
        if not code.strip():
            continue
        numbers = [
            BAD_CHAR if token == "BAD_CHAR" else int(token, 0)
            for token in re.findall(r"BAD_CHAR|0x[0-9a-fA-F]+|\b\d+\b", code)
        ]
        if numbers:
            rows.append((numbers, comment.strip()))
    return rows


def commentCode(comment: str) -> int | None:
    """Read the code written in a row comment, e.g. ``0xc02d,3213`` or ``1601``."""

    first = comment.split(",")[0].strip()
    try:
        return int(first, 0)
    except ValueError:
        return None


def trimSequence(values: Iterable[int]) -> tuple[int, ...]:
    """Drop the zero padding that terminates a sequence in the C arrays."""

    sequence: list[int] = []
    for value in values:
        if value == BAD_CHAR:
            break
        sequence.append(value)
    return tuple(sequence)


def fzdosCode(partBit: int) -> int:
    high = 0xA0 + partBit // 100
    low = 0x20 + partBit % 100
    return (high << 8) | low


def fzwinCode(partBit: int) -> int:
    high = 0xA0 + partBit // 100
    low = 0xA0 + partBit % 100
    return (high << 8) | low


def buildExtAtoLegacy(rows: list[tuple[list[int], str]]) -> list:
    entries = []
    for index, (numbers, _) in enumerate(rows):
        if index < BASIC_BLOCK_SIZE:
            code = BASIC_BLOCK_START + index
        else:
            code = 0xF300 + index - BASIC_BLOCK_SIZE
        value = numbers[0]
        if value != BAD_CHAR:
            entries.append([code, value])
    return entries


def buildLegacyToExtA(
    rows: list[tuple[list[int], str]],
    start: int,
    keyFromPartBit,
) -> list:
    entries = []
    for index, (numbers, comment) in enumerate(rows):
        value = numbers[0]
        if value == BAD_CHAR:
            continue
        key = keyFromPartBit(start + index)
        expected = commentCode(comment)
        if expected is not None and expected != key:
            raise SystemExit(f"row {index}: key {key:#x}, comment says {expected:#x}")
        entries.append([key, value])
    return entries


def buildPairs(rows: list[tuple[list[int], str]]) -> list:
    entries = []
    for numbers, _ in rows:
        if len(numbers) < 2 or BAD_CHAR in numbers[:2]:
            continue
        entries.append([numbers[0], numbers[1]])
    return entries


def radixOf(scheme: str) -> int:
    """HuaGuang codes are partition/bit numbers, everything else is hexadecimal."""

    return 10 if scheme == "hg" else 16


def formatCode(value: int, radix: int) -> str:
    if radix == 10:
        return str(value)
    return f"0x{value:04X}" if value <= 0xFFFF else f"0x{value:05X}"


def formatEntry(value: Any, radix: int) -> str:
    if isinstance(value, int):
        return formatCode(value, radix)
    return "[" + ", ".join(formatEntry(item, radix) for item in value) + "]"


def writeTable(
    name: str,
    source: str,
    target: str,
    title: str,
    sourceStart: int | None,
    entries: list,
    provenance: str,
) -> Path:
    lines = [
        f"# Imported from {provenance}",
        f"name: {name}",
        f"title: {title}",
        f"source: {source}  # {SCHEMES[source]}",
        f"target: {target}  # {SCHEMES[target]}",
    ]
    if sourceStart is not None:
        lines.append(f"sourceStart: {formatCode(sourceStart, radixOf(source))}")
    lines.append(f"entries:  # {len(entries)} pairs")
    lines.extend(
        f"- [{formatEntry(pair[0], radixOf(source))}, {formatEntry(pair[1], radixOf(target))}]"
        for pair in entries
    )
    lines.append("")

    path = OUT_DIR / f"{name}.yaml"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()

    if not args.source.is_dir():
        raise SystemExit(f"source directory not found: {args.source}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written: dict[str, int] = {}

    def emit(name: str, source: str, target: str, title: str, start: int | None, entries: list, provenance: str) -> None:
        path = writeTable(name, source, target, title, start, entries, provenance)
        written[name] = len(entries)
        print(f"{path.relative_to(ROOT)}: {len(entries)} pairs")

    truth = readTruth(TRUTH_PATH)

    extAToBasic = buildExtToBasic(truth, EXTA_START, EXTA_END)
    emit(
        "exta-basic",
        "exta",
        "basic",
        "Tibetan Extension Set A to Tibetan Basic Set",
        EXTA_START,
        extAToBasic,
        "note/20542-22238.txt (GB/T 20542-2006)",
    )
    emit(
        "extb-basic",
        "extb",
        "basic",
        "Tibetan Extension Set B to Tibetan Basic Set",
        EXTB_START,
        buildExtToBasic(truth, EXTB_START, EXTB_END),
        "note/20542-22238.txt (GB/T 22238-2008)",
    )
    emit(
        "basic-exta",
        "basic",
        "exta",
        "Tibetan Basic Set to Tibetan Extension Set A",
        None,
        buildBasicToExt(extAToBasic),
        "note/20542-22238.txt, inverted from exta-basic",
    )

    for fileName in SOURCE_FILES:
        path = args.source / fileName
        for name, (source, target, title, arrayName, sourceStart) in LEGACY_TABLES.items():
            if arrayName not in path.read_text(encoding="utf-8", errors="replace"):
                continue
            rows = parseRows(path, arrayName)
            if name in ("exta-fzdos", "exta-fzwin", "exta-hg", "exta-tonguer"):
                entries = buildExtAtoLegacy(rows)
            elif name == "fzdos-exta":
                entries = buildLegacyToExtA(rows, 3213, fzdosCode)
            elif name == "fzwin-exta":
                entries = buildLegacyToExtA(rows, 302, fzwinCode)
            elif name == "hg-exta":
                entries = buildLegacyToExtA(rows, 1601, lambda partBit: partBit)
            elif name == "tonguer-exta":
                entries = buildLegacyToExtA(rows, 0x8140, lambda partBit: partBit)
            else:
                entries = buildPairs(rows)
            emit(name, source, target, title, sourceStart, entries, f"tibetancodecs src/{fileName} ({arrayName})")

    missing = sorted({"basic-exta", "exta-basic", "extb-basic", *LEGACY_TABLES} - set(written))
    if missing:
        raise SystemExit(f"tables not imported: {', '.join(missing)}")


if __name__ == "__main__":
    main()
