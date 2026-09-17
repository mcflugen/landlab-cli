from __future__ import annotations

from collections.abc import Collection
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from landlab_cli._catalog import ALL_TAGS
from landlab_cli._catalog import categorize_class


class Rule(Enum):
    @property
    def code(self) -> str:
        return self.value[0]

    @property
    def message(self) -> str:
        return self.value[1]


class ComponentRule(Rule):
    MISSING_ATTRIBUTE = ("C001", "component is missing a required attribute")
    EMPTY_INFO = ("C002", "component _info is empty")


class FieldRule(Rule):
    MISSING_REQUIRED_KEY = ("F001", "field metadata is missing a required key")
    UNKNOWN_KEY = ("F002", "field metadata contains an unknown key")
    INVALID_DTYPE = ("F003", "field dtype is not a type")
    INVALID_MAPPING = ("F004", "field mapping is invalid")
    INVALID_INTENT = ("F005", "field intent is invalid")
    INVALID_DESCRIPTION = ("F006", "field description is not a string")
    DESCRIPTION_WHITESPACE = ("F007", "field description contains invalid whitespace")


class GridRule(Rule):
    UNKNOWN_CATEGORY = ("G001", "grid member category is unknown")
    MISSING_CATEGORY = ("G002", "grid member has no category")


@dataclass(frozen=True)
class LintIssue:
    rule: Rule
    target: str
    detail: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}: {self.target}: {self.detail}"

    @property
    def code(self) -> str:
        return self.rule.code

    @property
    def message(self) -> str:
        return self.rule.message

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "target": self.target,
            "message": self.message,
            "detail": self.detail,
        }


REQUIRED_FIELD_KEYS = frozenset(
    [
        "doc",
        "dtype",
        "intent",
        "mapping",
        "optional",
        "units",
    ]
)
VALID_MAPPINGS = frozenset(
    [
        "node",
        "link",
        "patch",
        "corner",
        "face",
        "cell",
        "grid",
    ]
)
VALID_INTENTS = frozenset(
    [
        "in",
        "inout",
        "out",
    ]
)


def lint_components(components: dict[str, Any]) -> list[LintIssue]:
    issues = []
    for name, cls in sorted(components.items()):

        issues += [
            LintIssue(ComponentRule.MISSING_ATTRIBUTE, detail=attr, target=name)
            for attr in ("_info", "_name", "_unit_agnostic")
            if not hasattr(cls, attr)
        ]

        if not hasattr(cls, "_info"):
            continue

        if len(cls._info) == 0:
            issues += [LintIssue(ComponentRule.EMPTY_INFO, detail="_info", target=name)]

        issues += lint_component_info(cls._info, component=name)

    return issues


def lint_component_info(
    info: dict[str, Any],
    *,
    component: str | None = None,
) -> list[LintIssue]:
    issues = []
    for field, desc in sorted(info.items()):
        target = field if component is None else f"{component}.{field}"
        issues += lint_field_info(desc, target=target)

    return issues


def lint_field_info(
    info: dict[str, Any],
    *,
    target: str,
) -> list[LintIssue]:
    issues = []

    def new_issue(rule: FieldRule, detail: Any) -> LintIssue:
        return LintIssue(rule=rule, detail=str(detail), target=target)

    issues += [
        new_issue(FieldRule.MISSING_REQUIRED_KEY, detail=attr)
        for attr in sorted(REQUIRED_FIELD_KEYS - set(info))
    ]
    issues += [
        new_issue(FieldRule.UNKNOWN_KEY, detail=attr)
        for attr in sorted(set(info) - REQUIRED_FIELD_KEYS)
    ]

    if "dtype" in info and not isinstance(info["dtype"], type):
        issues += [new_issue(FieldRule.INVALID_DTYPE, detail=info["dtype"])]

    if "mapping" in info and (
        not isinstance(info["mapping"], str) or info["mapping"] not in VALID_MAPPINGS
    ):
        issues += [new_issue(FieldRule.INVALID_MAPPING, detail=info["mapping"])]

    if "doc" in info:
        if not isinstance(info["doc"], str):
            issues += [new_issue(FieldRule.INVALID_DESCRIPTION, detail=info["doc"])]
        elif has_invalid_whitespace(info["doc"]):
            issues += [new_issue(FieldRule.DESCRIPTION_WHITESPACE, detail=info["doc"])]

    if "intent" in info and (
        not isinstance(info["intent"], str) or info["intent"] not in VALID_INTENTS
    ):
        issues += [new_issue(FieldRule.INVALID_INTENT, detail=info["intent"])]

    return issues


def lint_grids(grids: dict[str, Any]) -> list[LintIssue]:
    issues = []
    for name, cls in grids.items():
        categorized_methods = categorize_class(cls)

        issues += [
            LintIssue(GridRule.UNKNOWN_CATEGORY, detail=tag, target=name)
            for tag in sorted(set(categorized_methods) - ALL_TAGS)
        ]

        issues += [
            LintIssue(GridRule.MISSING_CATEGORY, detail=method_name, target=name)
            for method_name in sorted(categorized_methods["uncategorized"])
        ]

    return issues


def select_issues(
    issues: Iterable[LintIssue],
    *,
    exclude: Collection[str] | None = None,
) -> list[LintIssue]:
    exclude = set() if exclude is None else set(exclude)
    return [issue for issue in issues if issue.code not in exclude]


def has_invalid_whitespace(text: str) -> bool:
    return text != " ".join(text.split())
