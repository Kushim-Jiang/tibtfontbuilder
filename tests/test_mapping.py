import unicodedata
from pathlib import Path

import pytest

from src.lib_.mapping import codePoints, iterPairs, loadTables, tableNames, toSequence

TABLES = loadTables()
NAMES = tableNames()

# The transcription of GB/T 20542-2006 and GB/T 22238-2008; the authority for
# everything about Extension Set A and B.
TRUTH_PATH = Path(__file__).resolve().parents[1] / "note" / "20542-22238.txt"

# Extension Set ranges as printed in the standards.
EXT_RANGES = {"exta-basic": (0xF300, 0xF8FF), "extb-basic": (0xF0000, 0xF1644)}

# Code spaces and the ranges they may use.  The forward Ext-A tables also carry
# the basic block, so "exta" allows both ranges.  A few punctuation signs are
# mapped as well, which is why the Unicode side allows the punctuation blocks.
UNICODE_RANGES = [
    (0x0020, 0x0020),  # space
    (0x0F00, 0x0FFF),  # Tibetan
    (0x2018, 0x201D),  # quotes
    (0x3000, 0x303F),  # CJK punctuation
    (0xFF00, 0xFFEF),  # fullwidth forms
]
SCHEME_RANGES = {
    "basic": UNICODE_RANGES,
    "exta": UNICODE_RANGES + [(0xF300, 0xF8FF)],
    "extb": [(0xF0000, 0xF1645)],
    "fzdos": [(0x0100, 0xFFFF)],
    "fzwin": [(0x0100, 0xFFFF)],
    "tonguer": [(0x0100, 0xFFFF)],
    "hg": [(1, 9999)],
}

# Snapshot of the imported data, so a broken import cannot silently drop rows.
EXPECTED_COUNTS = {
    "basic-exta": 1536,
    "exta-basic": 1536,
    "extb-basic": 5701,
    "exta-fzdos": 1476,
    "exta-fzwin": 1595,
    "exta-hg": 1594,
    "exta-tonguer": 1382,
    "fzdos-exta": 1504,
    "fzwin-exta": 1670,
    "hg-exta": 1592,
    "tonguer-exta": 1389,
    "fzdos-fzwin": 1390,
    "fzwin-fzdos": 1390,
}


def test_allTablesImported() -> None:
    assert NAMES == sorted(EXPECTED_COUNTS)


@pytest.mark.parametrize("name", NAMES)
def test_schema(name: str) -> None:
    table = TABLES[name]
    assert table["name"] == name
    assert table["title"]
    assert table["source"] in SCHEME_RANGES
    assert table["target"] in SCHEME_RANGES
    assert len(table["entries"]) == EXPECTED_COUNTS[name]

    for source, target in iterPairs(table):
        assert source and target
        assert all(code > 0 for code in source + target)


@pytest.mark.parametrize("name", NAMES)
def test_sourceRanges(name: str) -> None:
    table = TABLES[name]
    ranges = SCHEME_RANGES[table["source"]]
    for source, _ in iterPairs(table):
        for code in source:
            assert any(low <= code <= high for low, high in ranges), f"{code:#x} out of range"


@pytest.mark.parametrize("name", NAMES)
def test_targetRanges(name: str) -> None:
    table = TABLES[name]
    ranges = SCHEME_RANGES[table["target"]]
    for _, target in iterPairs(table):
        for code in target:
            assert any(low <= code <= high for low, high in ranges), f"{code:#x} out of range"


@pytest.mark.parametrize("name", NAMES)
def test_sortedBySource(name: str) -> None:
    """The upstream engine binary searches these tables, so keys must be ordered."""

    keys = [source[0] for source, _ in iterPairs(TABLES[name])]
    assert keys == sorted(keys)


@pytest.mark.parametrize("name", NAMES)
def test_sourceStart(name: str) -> None:
    table = TABLES[name]
    if "sourceStart" not in table:
        return
    first = next(iterPairs(table))[0][0]
    assert table["sourceStart"] == first


def test_basicExtAInverse() -> None:
    basicToExtA = {source: target[0] for source, target in iterPairs(TABLES["basic-exta"])}
    extAToBasic = {source[0]: target for source, target in iterPairs(TABLES["exta-basic"])}
    assert len(basicToExtA) == len(extAToBasic)
    for sequence, code in basicToExtA.items():
        assert extAToBasic[code] == sequence


def readTruth() -> dict[int, tuple[int, ...]]:
    """The standard transcription, decomposed the same way the tables store it."""

    rows: dict[int, tuple[int, ...]] = {}
    for line in TRUTH_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        _, _, code, sequence, _ = line.split("\t")
        text = unicodedata.normalize("NFKD", sequence)
        rows[int(code, 16)] = tuple(ord(char) for char in text)
    return rows


@pytest.mark.parametrize("name", sorted(EXT_RANGES))
def test_matchesTruth(name: str) -> None:
    """Extension Set A and B must be exactly what the standard transcription says."""

    low, high = EXT_RANGES[name]
    expected = {code: sequence for code, sequence in readTruth().items() if low <= code <= high}
    actual = dict(iterPairs(TABLES[name]))

    assert set(actual) == {(code,) for code in expected}
    wrong = {code: (actual[(code,)], sequence) for code, sequence in expected.items() if actual[(code,)] != sequence}
    assert not wrong, f"{len(wrong)} rows differ from the standard"


def test_truthCoversBothExtensionSets() -> None:
    truth = readTruth()
    extA = [code for code in truth if code <= 0xF8FF]
    extB = [code for code in truth if code > 0xF8FF]
    assert extA == list(range(EXT_RANGES["exta-basic"][0], EXT_RANGES["exta-basic"][1] + 1))
    assert extB == list(range(EXT_RANGES["extb-basic"][0], EXT_RANGES["extb-basic"][1] + 1))


def test_truthSequencesAreUnique() -> None:
    """Ext-A is one-to-one with the Basic Set, otherwise basic-exta could not exist."""

    truth = readTruth()
    low, high = EXT_RANGES["exta-basic"]
    sequences = [truth[code] for code in truth if low <= code <= high]
    assert len(set(sequences)) == len(sequences)


@pytest.mark.parametrize("name", ["basic-exta", "exta-basic", "extb-basic"])
def test_sequencesAreDecomposed(name: str) -> None:
    """Every sequence is stored decomposed, like the original C++ arrays."""

    for source, target in iterPairs(TABLES[name]):
        for code in source + target:
            assert unicodedata.normalize("NFKD", chr(code)) == chr(code), f"{code:#06x} is not decomposed"


def test_fzDosWindowsInverse() -> None:
    dosToWin = {source[0]: target[0] for source, target in iterPairs(TABLES["fzdos-fzwin"])}
    winToDos = {source[0]: target[0] for source, target in iterPairs(TABLES["fzwin-fzdos"])}
    for dos, win in dosToWin.items():
        assert winToDos[win] == dos


@pytest.mark.parametrize(
    ("forward", "reverse"),
    [("exta-fzdos", "fzdos-exta"), ("exta-fzwin", "fzwin-exta"), ("exta-hg", "hg-exta"), ("exta-tonguer", "tonguer-exta")],
)
def test_legacyRoundTrip(forward: str, reverse: str) -> None:
    """The reverse tables agree with the forward ones, apart from a handful of
    inconsistencies inherited from the upstream data."""

    back = {source[0]: target[0] for source, target in iterPairs(TABLES[reverse])}
    pairs = list(iterPairs(TABLES[forward]))
    consistent = sum(1 for source, target in pairs if back.get(target[0]) == source[0])
    assert consistent >= len(pairs) - 5


def test_codePoints() -> None:
    assert codePoints([0x0F40, 0x0F71]) == "\u0f40\u0f71"
    assert codePoints(toSequence(0x0F40)) == "\u0f40"
