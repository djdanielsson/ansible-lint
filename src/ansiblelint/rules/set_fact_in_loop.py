"""Implementation of the set-fact-in-loop rule."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from ansiblelint.rules import AnsibleLintRule

if TYPE_CHECKING:
    from ansiblelint.file_utils import Lintable
    from ansiblelint.utils import Task

_LOOP_KEYWORDS = frozenset((
    "loop",
    "with_items",
    "with_list",
    "with_dict",
    "with_fileglob",
    "with_filetree",
    "with_first_found",
    "with_indexed_items",
    "with_ini",
    "with_inventory_hostnames",
    "with_lines",
    "with_nested",
    "with_random_choice",
    "with_sequence",
    "with_subelements",
    "with_together",
    "with_flattened",
))


class SetFactInLoopRule(AnsibleLintRule):
    """Avoid using set_fact inside a loop."""

    id = "set-fact-in-loop"
    description = (
        "Using ``ansible.builtin.set_fact`` inside a loop is a performance "
        "anti-pattern. Use Jinja2 filters like ``map``, ``select``, or "
        "``selectattr`` to transform data instead."
    )
    severity = "MEDIUM"
    tags = ["idiom", "opt-in"]
    version_changed = "6.22.0"

    _set_fact_modules = (
        "ansible.builtin.set_fact",
        "ansible.legacy.set_fact",
        "set_fact",
    )

    def matchtask(
        self,
        task: Task,
        file: Lintable | None = None,
    ) -> bool | str:
        if task["action"]["__ansible_module__"] not in self._set_fact_modules:
            return False

        raw = task.raw_task
        for keyword in _LOOP_KEYWORDS:
            if keyword in raw:
                return "set_fact inside a loop is a performance anti-pattern"

        return False


if "pytest" in sys.modules:
    from ansiblelint.rules import RulesCollection
    from ansiblelint.runner import Runner

    def test_set_fact_in_loop_fail(
        empty_rule_collection: RulesCollection,
    ) -> None:
        """Test rule catches set_fact used in a loop."""
        empty_rule_collection.register(SetFactInLoopRule())
        results = Runner(
            "examples/playbooks/rule-set-fact-in-loop-fail.yml",
            rules=empty_rule_collection,
        ).run()
        assert len(results) == 2
        for result in results:
            assert result.rule.id == SetFactInLoopRule.id

    def test_set_fact_in_loop_pass(
        empty_rule_collection: RulesCollection,
    ) -> None:
        """Test rule allows set_fact without a loop."""
        empty_rule_collection.register(SetFactInLoopRule())
        results = Runner(
            "examples/playbooks/rule-set-fact-in-loop-pass.yml",
            rules=empty_rule_collection,
        ).run()
        assert len(results) == 0, results
