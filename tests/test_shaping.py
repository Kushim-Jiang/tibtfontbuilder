import pytest

from fixtures import loadTestCases, output


@pytest.mark.parametrize(
    ("codes", "index", "result", "goal"),
    loadTestCases(output, ["tibetan"]),
)
def test_tibt(codes: str, index: str, result: str, goal: str) -> None:
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"
