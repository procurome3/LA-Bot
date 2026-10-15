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
    ) -> SkillTreeResult:
        priority = self.priority_for(family)
        declared = set(declared_skill_ids)

        for skill_id in priority:
            if skill_id not in declared:
                continue

            item = skills.get(skill_id)
            if item is None:
                return SkillTreeResult(
                    None, "wait", f"{skill_id}-not-recognised", priority
                )

            eligibility = item.get("eligibility", "eligible")
            if eligibility == "ineligible":
                continue
            if eligibility != "eligible":
                return SkillTreeResult(
                    None,
                    "wait",
                    item.get("eligibility_reason") or f"{skill_id}-eligibility-unknown",
                    priority,
                )

            # A single-target revive branch cannot run without a confirmed corpse.
            if item.get("attack_type") == "ally_dead" and not dead_ally_available:
                continue

            availability = item.get("availability", "unknown")
            if availability == "unavailable":
                continue
            if availability != "available":
                return SkillTreeResult(
                    None, "wait", f"{skill_id}-availability-unknown", priority
                )

            if float(item.get("score", 0.0)) < float(min_score):
                return SkillTreeResult(
                    None, "wait", f"{skill_id}-match-uncertain", priority
                )

            return SkillTreeResult(
                item,
                "selected",
                item.get("eligibility_reason") or f"priority-{skill_id}-ready",
                priority,
            )

        return SkillTreeResult(
            None,
            "none",
            "all-priority-skills-unavailable-or-ineligible",
            priority,
        )
