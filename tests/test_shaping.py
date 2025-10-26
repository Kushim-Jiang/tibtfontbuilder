import pytest

from fixtures import loadTestCases, output


@pytest.mark.parametrize(
    ("codes", "result", "goal"),
    loadTestCases(output, ["tibetan"]),
)
def test_tibetan(codes: str, result: str, goal: str) -> None:
    assert result == goal, f"code: {codes}\nres:  {result}\ngoal: {goal}"


@pytest.mark.parametrize(
    ("codes", "result", "goal"),
    loadTestCases(output, ["sanskrit-a"]),
)
def test_sanskrit_a(codes: str, result: str, goal: str) -> None:
    assert result == goal, f"code: {codes}\nres:  {result}\ngoal: {goal}"


@pytest.mark.parametrize(
    ("codes", "result", "goal"),
    loadTestCases(output, ["sanskrit-b"]),
)
def test_sanskrit_b(codes: str, result: str, goal: str) -> None:
    assert result == goal, f"code: {codes}\nres:  {result}\ngoal: {goal}"
