import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from research_planner import ResearchPlanner


def sample_data():
    return ["alpha", "beta", "gamma"]


def test_generate_and_evaluate():
    planner = ResearchPlanner(data=sample_data())
    tests = planner.generate_tests()
    assert len(tests) == 3
    results = [len("alpha"), len("beta"), 10]
    evaluation = planner.evaluate_tests(results)
    assert evaluation["passes"] == [0, 1]
    assert evaluation["failures"] == [2]


def test_self_heal_and_improve():
    planner = ResearchPlanner(data=sample_data())
    planner.generate_tests()
    results = [len("alpha"), len("beta"), 10]
    evaluation = planner.evaluate_tests(results)
    planner.self_heal(evaluation["failures"])
    assert planner.generated_tests[2]["expected"] == len("gamma")
    planner.self_improve(evaluation["passes"])
    assert planner.improvement_factor > 1.0
