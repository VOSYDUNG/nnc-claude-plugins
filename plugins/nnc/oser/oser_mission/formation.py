"""Formation packet validation before a durable Mission is locked.

Formation is advisory/draft state. It helps an agent move from a vague problem
to an evidence-backed direction without pretending the direction is approved
Mission authority.
"""
from __future__ import annotations

from copy import deepcopy

from .common import require, text
from .decision import validate_decision

STAGES = ("INTAKE", "REALITY_AUDIT", "RESEARCH", "DECISION", "MISSION_READY")


def _strings(value, label):
    require(isinstance(value, list), "INVALID_FORMATION", label + " must be a list")
    for item in value:
        text(item, label + " item")
    return list(value)


def validate_formation(value):
    require(isinstance(value, dict), "INVALID_FORMATION", "formation must be an object")
    result = {
        "schema": "nnc-oser/formation@1",
        "id": text(value.get("id"), "formation.id"),
        "stage": value.get("stage", "INTAKE"),
        "actor": text(value.get("actor"), "formation.actor"),
        "problem": text(value.get("problem"), "formation.problem"),
    }
    require(result["stage"] in STAGES, "INVALID_FORMATION", "unknown formation stage")

    reality = value.get("current_reality", {})
    require(isinstance(reality, dict), "INVALID_FORMATION", "current_reality must be an object")
    if result["stage"] != "INTAKE":
        result["current_reality"] = {
            "workflow": text(reality.get("workflow"), "current_reality.workflow"),
            "pain": text(reality.get("pain"), "current_reality.pain"),
            "current_tools": _strings(reality.get("current_tools", []), "current_reality.current_tools"),
            "constraints": _strings(reality.get("constraints", []), "current_reality.constraints"),
        }
        if reality.get("baseline") is not None:
            result["current_reality"]["baseline"] = text(reality["baseline"], "current_reality.baseline")
    else:
        result["current_reality"] = deepcopy(reality)

    research = value.get("research", [])
    require(isinstance(research, list), "INVALID_FORMATION", "research must be a list")
    normalized_research = []
    for item in research:
        require(isinstance(item, dict), "INVALID_FORMATION", "research item must be an object")
        normalized_research.append({
            "candidate": text(item.get("candidate"), "research.candidate"),
            "class": text(item.get("class"), "research.class"),
            "fit": text(item.get("fit"), "research.fit"),
            "source_ref": text(item.get("source_ref"), "research.source_ref"),
            "unknowns": _strings(item.get("unknowns", []), "research.unknowns"),
        })
    result["research"] = normalized_research
    if result["stage"] in ("RESEARCH", "DECISION", "MISSION_READY"):
        require(bool(normalized_research), "RESEARCH_REQUIRED",
                "research at least one native/tool/configure/build candidate before locking a direction")

    decision = value.get("decision")
    if result["stage"] in ("DECISION", "MISSION_READY"):
        require(decision is not None, "DECISION_REQUIRED", "formation needs a decision card")
        result["decision"] = validate_decision(decision)
    elif decision is not None:
        result["decision"] = validate_decision(decision)

    result["selected_direction"] = value.get("selected_direction")
    if result["selected_direction"] is not None:
        result["selected_direction"] = text(result["selected_direction"], "selected_direction")

    result["unresolved"] = _strings(value.get("unresolved", []), "formation.unresolved")

    if result["stage"] == "MISSION_READY":
        require(result["selected_direction"], "DIRECTION_REQUIRED",
                "lock a selected direction before Mission formation")
        require(not result["unresolved"], "FORMATION_UNRESOLVED",
                "resolve or explicitly defer Formation unknowns before Mission lock")
        draft = value.get("mission_draft")
        require(isinstance(draft, dict), "MISSION_DRAFT_REQUIRED",
                "MISSION_READY requires a Mission draft")
        result["mission_draft"] = {
            "goal": text(draft.get("goal"), "mission_draft.goal"),
            "owner": text(draft.get("owner"), "mission_draft.owner"),
            "authority_refs": _strings(draft.get("authority_refs", []), "mission_draft.authority_refs"),
            "acceptance_outcomes": _strings(draft.get("acceptance_outcomes", []), "mission_draft.acceptance_outcomes"),
        }
        require(result["mission_draft"]["authority_refs"], "AUTHORITY_REQUIRED",
                "Mission draft needs approved authority refs")
        require(result["mission_draft"]["acceptance_outcomes"], "ACCEPTANCE_REQUIRED",
                "Mission draft needs outcome acceptance")
    elif value.get("mission_draft") is not None:
        result["mission_draft"] = deepcopy(value["mission_draft"])

    return result


def formation_view(value):
    formation = validate_formation(value)
    return {
        "id": formation["id"],
        "stage": formation["stage"],
        "problem": formation["problem"],
        "research_candidates": len(formation["research"]),
        "decision": formation.get("decision", {}).get("id"),
        "selected_direction": formation.get("selected_direction"),
        "unresolved": formation["unresolved"],
        "mission_ready": formation["stage"] == "MISSION_READY",
        "note": "MISSION_READY is a validated draft state, not approval and not oser init.",
    }
