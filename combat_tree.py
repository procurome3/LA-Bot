"""Strict skill-priority decision layer for Live Arena combat V15.

Perception and champion-specific conditions are computed in livearena_combat.py.
This module deliberately has no third-party dependency: it preserves the old
selector semantics in a few deterministic Python branches.

Rule: a lower-priority skill is considered only when every higher branch is
CONFIRMED unavailable or ineligible. Unknown/uncertain state waits instead of
blindly dropping to a lower skill.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Sequence, Tuple

from livearena_config import SKILL_PRIORITY_BY_FAMILY

DEFAULT_SKILL_PRIORITY = ("A3", "A2", "A1")


@dataclass
class SkillTreeResult:
    skill: Optional[dict]
    state: str          # selected | wait | none
    reason: str
    priority: Tuple[str, ...]
    unknown_reasons: Optional[Tuple[str, ...]] = None


class CombatDecisionTree:
    def __init__(self, champion_priorities: Optional[Mapping[str, Sequence[str]]] = None):
        self.priorities = {
            str(family).lower(): tuple(order)
            for family, order in SKILL_PRIORITY_BY_FAMILY.items()
        }
        if champion_priorities:
            for family, order in champion_priorities.items():
                self.priorities[str(family).lower()] = tuple(order)

    def priority_for(self, family: Optional[str]) -> Tuple[str, ...]:
        if not family:
            return DEFAULT_SKILL_PRIORITY
        return tuple(self.priorities.get(str(family).lower(), DEFAULT_SKILL_PRIORITY))

    def decide(
        self,
        *,
        family: Optional[str],
        skills: Mapping[str, dict],
        declared_skill_ids: Iterable[str],
        dead_ally_available: bool,
        min_score: float,
        prefer_fallback: bool = False,
    ) -> SkillTreeResult:
        priority = self.priority_for(family)
        declared = set(declared_skill_ids)
        unknown_reasons: list[str] = []

        for skill_id in priority:
            if skill_id not in declared:
                continue

            item = skills.get(skill_id)
            if item is None:
                unknown_reasons.append(f"{skill_id}-not-recognised")
                continue

            eligibility = item.get("eligibility", "eligible")
            if eligibility == "ineligible":
                continue
            if eligibility != "eligible":
                unknown_reasons.append(
                    item.get("eligibility_reason") or f"{skill_id}-eligibility-unknown"
                )
                continue

            if item.get("attack_type") == "ally_dead" and not dead_ally_available:
                continue

            availability = item.get("availability", "unknown")
            if availability == "unavailable":
                continue
            if availability != "available":
                unknown_reasons.append(f"{skill_id}-availability-unknown")
                continue

            score = float(item.get("score", 0.0))
            if score < float(min_score):
                unknown_reasons.append(f"{skill_id}-match-uncertain")
                continue

            return SkillTreeResult(
                item,
                "selected",
                item.get("eligibility_reason") or f"priority-{skill_id}-ready",
                priority,
                tuple(unknown_reasons) if unknown_reasons else None,
            )

        if prefer_fallback:
            for skill_id in reversed(priority):
                if skill_id not in declared:
                    continue
                item = skills.get(skill_id)
                if item is None:
                    continue
                if item.get("eligibility", "eligible") != "eligible":
                    continue
                if item.get("availability", "unknown") == "unavailable":
                    continue
                if float(item.get("score", 0.0)) < float(min_score):
                    continue
                return SkillTreeResult(
                    item,
                    "selected",
                    f"fallback-{item.get('skill_name', skill_id)}",
                    priority,
                    tuple(unknown_reasons) if unknown_reasons else None,
                )

        if unknown_reasons:
            return SkillTreeResult(
                None,
                "wait",
                ";".join(unknown_reasons),
                priority,
                tuple(unknown_reasons),
            )

        return SkillTreeResult(
            None,
            "none",
            "all-priority-skills-unavailable-or-ineligible",
            priority,
            tuple(unknown_reasons) if unknown_reasons else None,
        )
