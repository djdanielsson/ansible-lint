"""Implementation of the type-cast-variables rule."""

from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING

from ansiblelint.rules import AnsibleLintRule
from ansiblelint.yaml_utils import nested_items_path

if TYPE_CHECKING:
    from ansiblelint.file_utils import Lintable
    from ansiblelint.utils import Task

# Matches a numeric comparison: operator followed by a number.
_NUMERIC_COMPARE = re.compile(r"\s+[><]=?\s+\d+")

# Matches an expression with a type cast before a numeric comparison.
_HAS_CAST = re.compile(r"\|\s*(?:int|float)\s+[><]=?\s+\d+")


class TypeCastVariablesRule(AnsibleLintRule):
    """Use type filters when comparing variables to numbers."""

    id = "type-cast-variables"
    description = (
        "Variables compared to numeric values should use ``| int`` or "
        "``| float`` filters to ensure type safety. Without casting, "
        "string values may cause unexpected comparison results."
    )
    severity = "MEDIUM"
    tags = ["idiom", "opt-in"]
    version_changed = "6.22.0"

    def _check_condition(self, condition: str) -> bool:
        """Return True if condition has an uncast numeric comparison."""
        if not _NUMERIC_COMPARE.search(condition):
            return False
        if _HAS_CAST.search(condition):
            return False
        return True

    def matchtask(
        self,
        task: Task,
        file: Lintable | None = None,
    ) -> bool | str:
        for k, v, _ in nested_items_path(task):
            if k == "when":
                if isinstance(v, str):
                    if self._check_condition(v):
                        return "Use '| int' or '| float' when comparing to numbers"
                elif isinstance(v, bool):
                    pass
                else:
                    for item in v:
                        if isinstance(item, str) and self._check_condition(item):
                            return (
                                "Use '| int' or '| float' when comparing to numbers"
                            )
        return False


if "pytest" in sys.modules:
    from ansiblelint.rules import RulesCollection
    from ansiblelint.runner import Runner

    def test_type_cast_variables_fail(
        empty_rule_collection: RulesCollection,
    ) -> None:
        """Test rule catches uncast numeric comparisons."""
        empty_rule_collection.register(TypeCastVariablesRule())
        results = Runner(
            "examples/playbooks/rule-type-cast-variables-fail.yml",
            rules=empty_rule_collection,
        ).run()
        assert len(results) == 3
        for result in results:
            assert result.rule.id == TypeCastVariablesRule.id

    def test_type_cast_variables_pass(
        empty_rule_collection: RulesCollection,
    ) -> None:
        """Test rule allows properly cast numeric comparisons."""
        empty_rule_collection.register(TypeCastVariablesRule())
        results = Runner(
            "examples/playbooks/rule-type-cast-variables-pass.yml",
            rules=empty_rule_collection,
        ).run()
        assert len(results) == 0, results
