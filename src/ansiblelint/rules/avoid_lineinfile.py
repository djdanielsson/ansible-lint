"""Implementation of the avoid-lineinfile rule."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from ansiblelint.rules import AnsibleLintRule

if TYPE_CHECKING:
    from ansiblelint.file_utils import Lintable
    from ansiblelint.utils import Task


class AvoidLineinfileRule(AnsibleLintRule):
    """Consider using ansible.builtin.template instead of lineinfile."""

    id = "avoid-lineinfile"
    description = (
        "The ``lineinfile`` module is fragile and hard to maintain for complex "
        "configuration. Consider using ``ansible.builtin.template`` which "
        "provides a full view of the file structure and is easier to review."
    )
    severity = "LOW"
    tags = ["idiom", "opt-in"]
    version_changed = "6.22.0"

    _lineinfile_modules = (
        "ansible.builtin.lineinfile",
        "ansible.legacy.lineinfile",
        "lineinfile",
    )

    def matchtask(
        self,
        task: Task,
        file: Lintable | None = None,
    ) -> bool | str:
        if task["action"]["__ansible_module__"] in self._lineinfile_modules:
            return "Consider using ansible.builtin.template instead of lineinfile"
        return False


if "pytest" in sys.modules:
    from ansiblelint.rules import RulesCollection
    from ansiblelint.runner import Runner

    def test_avoid_lineinfile_fail(
        empty_rule_collection: RulesCollection,
    ) -> None:
        """Test rule catches lineinfile usage."""
        empty_rule_collection.register(AvoidLineinfileRule())
        results = Runner(
            "examples/playbooks/rule-avoid-lineinfile-fail.yml",
            rules=empty_rule_collection,
        ).run()
        assert len(results) == 2
        for result in results:
            assert result.rule.id == AvoidLineinfileRule.id

    def test_avoid_lineinfile_pass(
        empty_rule_collection: RulesCollection,
    ) -> None:
        """Test rule allows template and copy usage."""
        empty_rule_collection.register(AvoidLineinfileRule())
        results = Runner(
            "examples/playbooks/rule-avoid-lineinfile-pass.yml",
            rules=empty_rule_collection,
        ).run()
        assert len(results) == 0, results
