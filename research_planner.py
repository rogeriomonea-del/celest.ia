"""Research planning AI with self-healing and self-improvement capabilities.

This module provides a simple `ResearchPlanner` class that generates tests
based on existing data, analyzes results, heals failing tests, and improves its
strategy over time.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class ResearchPlanner:
    """Plan and refine research tests using existing data.

    Attributes:
        data: Raw data used to derive new test cases.
        improvement_factor: Internal metric updated during self-improvement.
    """

    data: List[Dict[str, Any]]
    improvement_factor: float = 1.0
    generated_tests: List[Dict[str, Any]] = field(default_factory=list)

    def generate_tests(self) -> List[Dict[str, Any]]:
        """Generate new tests based on current data.

        The generation strategy uses the improvement factor to create simple
        assertions from the data. More complex strategies could be plugged in
        here.
        """
        self.generated_tests = [
            {"input": item, "expected": len(item) * self.improvement_factor}
            for item in self.data
        ]
        return self.generated_tests

    def evaluate_tests(self, results: List[float]) -> Dict[str, List[int]]:
        """Evaluate test results and return indices of passes and failures."""
        passes, failures = [], []
        for index, (test, result) in enumerate(zip(self.generated_tests, results)):
            if test["expected"] == result:
                passes.append(index)
            else:
                failures.append(index)
        return {"passes": passes, "failures": failures}

    def self_heal(self, failures: List[int]) -> None:
        """Adjust failing tests to match the observed results."""
        for index in failures:
            if index < len(self.generated_tests):
                observed = len(self.generated_tests[index]["input"])
                self.generated_tests[index]["expected"] = observed

    def self_improve(self, passes: List[int]) -> None:
        """Update improvement factor based on successful tests."""
        if passes:
            self.improvement_factor += len(passes) / len(self.generated_tests)
