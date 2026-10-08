"""Human-facing decision contracts for non-technical Mission formation.

This module validates decision evidence. It does not choose for the user, call a
model, infer permissions, or treat a recommendation as approval.
"""
from __future__ import annotations

import json
from pathlib import Path

from .common import OserError, canonical, digest, require, safe_path, text

LEVELS = ("D0", "D1", "D2", "D3")
REVERSIBILITY = ("easy", "partial", "hard", "irreversible")
FULL_FIELDS = (
    "consequence", "gain", "tradeoff", "risk", "reversibility",
    "data_impact", "recurring_cost", "maintenance", "next_action",
)


def validate_decision(value):
    require(isinstance(value, dict), "INVALID_DECISION", "decision must be an object")
    level = value.get("level")
    require(level in LEVELS, "INVALID_DECISION", "decision.level must be D0, D1, D2 or D3")
    did = text(value.get("id"), "decision.id")
    question = text(value.get("question"), "decision.question")
    topic = text(value.get("topic", question), "decision.topic")
    options = value.get("options")
    require(isinstance(options, list) and len(options) >= 2, "INVALID_DECISION", "decision needs at least two options")

    ids, labels, recommended = set(), set(), 0
    normalized = []
    for raw in options:
        require(isinstance(raw, dict), "INVALID_DECISION", "option must be an object")
        oid = text(raw.get("id"), "option.id")
        label = text(raw.get("label"), "option.label")
        require(oid not in ids and label not in labels, "INVALID_DECISION", "option ids/labels must be unique")
        ids.add(oid)
        labels.add(label)
        option = {"id": oid, "label": label}

        if level in ("D1", "D2", "D3"):
            option["consequence"] = text(raw.get("consequence"), "option.consequence")
            option["reversibility"] = raw.get("reversibility")
            require(option["reversibility"] in REVERSIBILITY, "INVALID_DECISION",
                    "option.reversibility must be easy, partial, hard or irreversible")

        if level in ("D2", "D3"):
            for field in FULL_FIELDS:
                if field in ("consequence", "reversibility"):
                    continue
                option[field] = text(raw.get(field), "option." + field)

        rec = raw.get("recommended", False)
        require(type(rec) is bool, "INVALID_DECISION", "option.recommended must be boolean")
        option["recommended"] = rec
        recommended += int(rec)
        normalized.append(option)

    require(recommended <= 1, "INVALID_DECISION", "at most one option may be recommended")

    uncertainty = value.get("uncertainty_option")
    if level in ("D2", "D3"):
        require(isinstance(uncertainty, dict), "UNCERTAINTY_PATH_REQUIRED",
                "material decisions need an explicit investigate/test-first path")
        uid = text(uncertainty.get("id"), "uncertainty_option.id")
        label = text(uncertainty.get("label"), "uncertainty_option.label")
        require(uid not in ids and label not in labels, "INVALID_DECISION", "uncertainty option must be distinct")
        uncertainty = {
            "id": uid,
            "label": label,
            "consequence": text(uncertainty.get("consequence"), "uncertainty_option.consequence"),
            "next_action": text(uncertainty.get("next_action"), "uncertainty_option.next_action"),
        }

    approval_required = value.get("approval_required", level == "D3")
    require(type(approval_required) is bool, "INVALID_DECISION", "approval_required must be boolean")
    if level == "D3":
        require(approval_required, "APPROVAL_REQUIRED", "D3 decisions require explicit human approval")

    result = {
        "schema": "nnc-oser/decision@1",
        "id": did,
        "level": level,
        "topic": topic,
        "question": question,
        "options": normalized,
        "uncertainty_option": uncertainty if level in ("D2", "D3") else None,
        "approval_required": approval_required,
    }
    if value.get("recommended_reason") is not None:
        result["recommended_reason"] = text(value.get("recommended_reason"), "recommended_reason")
    return result


def render_decision(value):
    decision = validate_decision(value)
    lines = ["%s · %s" % (decision["level"], decision["topic"]), decision["question"], ""]
    for index, option in enumerate(decision["options"], 1):
        rec = " · KHUYẾN NGHỊ" if option["recommended"] else ""
        lines.append("%d. %s%s" % (index, option["label"], rec))
        if decision["level"] in ("D1", "D2", "D3"):
            lines.append("   Hệ quả: " + option["consequence"])
            lines.append("   Đảo ngược: " + option["reversibility"])
        if decision["level"] in ("D2", "D3"):
            lines.extend([
                "   Được: " + option["gain"],
                "   Đánh đổi: " + option["tradeoff"],
                "   Rủi ro: " + option["risk"],
                "   Dữ liệu/quyền: " + option["data_impact"],
                "   Chi phí lặp lại: " + option["recurring_cost"],
                "   Bảo trì: " + option["maintenance"],
                "   Bước tiếp: " + option["next_action"],
            ])
    if decision["uncertainty_option"]:
        u = decision["uncertainty_option"]
        lines.extend(["", "? " + u["label"], "   Hệ quả: " + u["consequence"], "   Bước tiếp: " + u["next_action"]])
    if decision["approval_required"]:
        lines.extend(["", "YÊU CẦU: quyết định rõ của người có thẩm quyền; khuyến nghị không phải phê duyệt."])
    return "\n".join(lines)


def ask_user_payload(value):
    decision = validate_decision(value)
    options = []
    for option in decision["options"]:
        if decision["level"] == "D0":
            description = option["label"]
        elif decision["level"] == "D1":
            description = "Hệ quả: %s | Đảo ngược: %s" % (option["consequence"], option["reversibility"])
        else:
            description = ("Hệ quả: %s | Được: %s | Đánh đổi: %s | Rủi ro: %s | "
                           "Đảo ngược: %s | Dữ liệu/quyền: %s | Chi phí: %s | Bảo trì: %s | Bước tiếp: %s") % (
                               option["consequence"], option["gain"], option["tradeoff"], option["risk"],
                               option["reversibility"], option["data_impact"], option["recurring_cost"],
                               option["maintenance"], option["next_action"])
        options.append({"label": option["label"], "description": description})
    if decision["uncertainty_option"]:
        u = decision["uncertainty_option"]
        options.append({"label": u["label"],
                        "description": "Hệ quả: %s | Bước tiếp: %s" % (u["consequence"], u["next_action"])})
    return {"questions": [{"question": decision["question"], "header": decision["topic"][:24],
                             "options": options, "multiSelect": False}]}


def load_matching_decision(project, question):
    root = Path(project).resolve()
    directory = safe_path(root, ".nnc-oser/decisions")
    if not directory.is_dir():
        return None
    matches = []
    for path in sorted(directory.glob("*.json")):
        if path.is_symlink() or path.stat().st_size > 2 * 1024 * 1024:
            continue
        try:
            card = validate_decision(json.loads(path.read_text(encoding="utf-8")))
        except (OserError, OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
            continue
        if card["question"] == question:
            matches.append(card)
    require(len(matches) <= 1, "DECISION_AMBIGUOUS", "multiple decision cards use the same question")
    return matches[0] if matches else None


def write_decision(project, value):
    decision = validate_decision(value)
    root = Path(project).resolve()
    directory = safe_path(root, ".nnc-oser/decisions")
    require(not directory.is_symlink(), "UNSAFE_PATH", "decision directory must not be a symlink")
    directory.mkdir(parents=True, exist_ok=True)
    target = safe_path(root, ".nnc-oser/decisions/%s.json" % decision["id"])
    require(not target.is_symlink(), "UNSAFE_PATH", "decision path must not be a symlink")
    payload = canonical(decision) + "\n"
    if target.exists():
        previous = json.loads(target.read_text(encoding="utf-8"))
        require(digest(previous) == digest(decision), "DECISION_EXISTS",
                "decision id already exists with different content; create a new decision/version")
        return {"path": target.relative_to(root).as_posix(), "decision": decision, "changed": False}
    target.write_text(payload, encoding="utf-8")
    return {"path": target.relative_to(root).as_posix(), "decision": decision, "changed": True}


def load_decision(project, decision_id):
    decision_id = text(decision_id, "decision_id")
    path = safe_path(Path(project).resolve(), ".nnc-oser/decisions/%s.json" % decision_id)
    require(path.is_file(), "DECISION_NOT_FOUND", "decision card not found")
    return validate_decision(json.loads(path.read_text(encoding="utf-8")))
