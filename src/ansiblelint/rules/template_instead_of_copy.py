"""Implementation of the template-instead-of-copy rule."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from ansiblelint.rules import AnsibleLintRule

if TYPE_CHECKING:
    from ansiblelint.file_utils import Lintable
    from ansiblelint.utils import Task

_CONFIG_EXTENSIONS = frozenset((
    ".conf",
    ".cfg",
    ".ini",
    ".yml",
    ".yaml",
    ".json",
    ".xml",
    ".properties",
    ".toml",
    ".env",
))


class UseTemplateInsteadOfCopyRule(AnsibleLintRule):
    """Configuration files should use template instead of copy."""

    id = "template-instead-of-copy"
    description = (
        "Using ``ansible.builtin.template`` instead of ``ansible.builtin.copy`` "
        "for configuration files makes it easier to add variables later and "
        "provides a clearer view of the full file structure."
    )
    severity = "MEDIUM"
    tags = ["idiom", "opt-in"]
    version_changed = "6.22.0"

    _copy_modules = (
        "ansible.builtin.copy",
        "ansible.legacy.copy",
        "copy",
    )

    def matchtask(
        self,
        task: Task,
        file: Lintable | None = None,
    ) -> bool | str:
        if task["action"]["__ansible_module__"] not in self._copy_modules:
            return False

        dest = task["action"].get("dest", "")
        if not isinstance(dest, str):
            return False

        if dest.startswith("/etc/"):
            return "Use ansible.builtin.template for config files under /etc/"

        for ext in _CONFIG_EXTENSIONS:
            if dest.endswith(ext):
                return f"Use ansible.builtin.template for {ext} config files"

        return False


if "pytest" in sys.modules:
    from ansiblelint.rules import RulesCollection
    from ansiblelint.runner import Runner

    def test_template_instead_of_copy_fail(
        empty_rule_collection: RulesCollection,
    ) -> None:
        """Test rule catches copy used for config files."""
        empty_rule_collection.register(UseTemplateInsteadOfCopyRule())
        results = Runner(
            "examples/playbooks/rule-template-instead-of-copy-fail.yml",
            rules=empty_rule_collection,
        ).run()
        assert len(results) == 3
        for result in results:
            assert result.rule.id == UseTemplateInsteadOfCopyRule.id

    def test_template_instead_of_copy_pass(
        empty_rule_collection: RulesCollection,
    ) -> None:
        """Test rule allows non-config copy usage."""
        empty_rule_collection.register(UseTemplateInsteadOfCopyRule())
        results = Runner(
            "examples/playbooks/rule-template-instead-of-copy-pass.yml",
            rules=empty_rule_collection,
        ).run()
        assert len(results) == 0, results
