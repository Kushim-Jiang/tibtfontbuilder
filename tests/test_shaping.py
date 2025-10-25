import pytest

from fixtures import loadTestCases, output


@pytest.mark.parametrize(
    ("codes", "result", "goal"),
    loadTestCases(output, ["tibetan"]),
)
def test_tibt(codes: str, result: str, goal: str) -> None:
    assert result == goal, f"code: {codes}\nres:  {result}\ngoal: {goal}"
