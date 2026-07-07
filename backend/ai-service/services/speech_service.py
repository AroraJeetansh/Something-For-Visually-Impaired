"""
speech_service.py

Generates natural navigation speech from the planner's output.

Design notes (why this differs from the previous version)
------------------------------------------------------------
The previous version re-computed "nearest object" itself instead of
using the planner's `warning` field, so speech and navigation logic
could disagree about which object mattered most. It also only handled
"left"/"right"/"center" in movement_text, silently defaulting
"far_left"/"far_right" to "Continue straight." -- which is actively
wrong (it would tell the user to walk straight into a sector that was
just flagged as the path of an obstacle... no, in that case far_left
sectors were never reachable as safe_direction before, but now that
the new planner CAN choose far_left/far_right, this needs full
handling).

This version:
1. Reads `path["warning"]` directly instead of recomputing it.
2. Has a movement phrase for every sector, with intensity scaled to
   how sharp the turn is (slight vs sharp).
3. Separates "what's out there" phrasing from "what to do" phrasing so
   it reads like natural spoken guidance instead of two robotic
   fragments.
4. Formats object class names (e.g. "fire_hydrant") into readable
   speech ("fire hydrant").
"""

from typing import List, Dict, Any, Optional


def _label(object_class: str) -> str:
    """Turn a raw class name like 'fire_hydrant' into 'Fire hydrant'."""
    text = object_class.replace("_", " ").replace("-", " ").strip()
    if not text:
        return "Object"
    return text[0].upper() + text[1:]


def _direction_phrase(direction: str) -> str:
    mapping = {
        "far_left": "far to your left",
        "left": "on your left",
        "center": "ahead of you",
        "right": "on your right",
        "far_right": "far to your right",
    }
    return mapping.get(direction, direction)


def _movement_phrase(safe_direction: str) -> str:
    mapping = {
        "center": "Continue straight.",
        "left": "Move slightly left.",
        "right": "Move slightly right.",
        "far_left": "Move sharply left.",
        "far_right": "Move sharply right.",
    }
    return mapping.get(safe_direction, "Continue straight.")


def _status_phrase(status: Optional[str]) -> Optional[str]:
    """
    Short follow-up phrase for a previously-seen object, so we don't
    repeat the full "Person ahead of you." every frame.
    """
    mapping = {
        "still": "Still there.",
        "approaching": "Getting closer.",
        "moving_away": "Moving away.",
    }
    return mapping.get(status)


def _find_warning_status(
    warning: Dict[str, Any], annotated_objects: List[Dict[str, Any]]
) -> Optional[str]:
    """
    `path["warning"]` is produced by the planner before scene_memory
    annotates objects with a status. Match it back to the annotated
    list (by class + direction, which is how scene_memory itself
    matches tracks) to retrieve its status.
    """
    for obj in annotated_objects:
        if (
            obj.get("object") == warning.get("object")
            and obj.get("direction") == warning.get("direction")
        ):
            return obj.get("status")
    return None


def _warning_sentence(
    warning: Optional[Dict[str, Any]],
    status: Optional[str] = None,
) -> Optional[str]:
    if not warning:
        return None

    # "new" or unknown status -> full description, as before.
    if status in ("still", "approaching", "moving_away"):
        status_phrase = _status_phrase(status)
        if status_phrase:
            return status_phrase

    label = _label(warning.get("object", "Object"))
    direction = _direction_phrase(warning.get("direction", "center"))
    distance_label = warning.get("distance_label")

    if distance_label and distance_label != "Unknown":
        return f"{label} {direction}, {distance_label.lower()}."

    return f"{label} {direction}."


def build_navigation_speech(
    objects: List[Dict[str, Any]],
    path: Dict[str, Any],
    annotated_objects: Optional[List[Dict[str, Any]]] = None,
    path_just_cleared: bool = False,
) -> str:
    """
    Builds a natural-sounding speech string from detected objects and
    the planner's decision.

    Expected `path` keys (from path_planner.plan_path):
        safe_direction, danger, warning, sector_scores

    Optional memory integration (from scene_memory.SceneMemory.update):
        annotated_objects -- objects list with a "status" key added
            per object (new/still/approaching/moving_away). If not
            provided, speech behaves exactly as before (no memory).
        path_just_cleared -- True on the single frame where danger
            transitions from True to False.
    """
    if not objects:
        if path_just_cleared:
            return "Path clear. Continue straight."
        return "Path is clear. Continue straight."

    sentences = []

    if path.get("danger"):
        sentences.append("Obstacle very close.")

    warning = path.get("warning")
    status = None
    if warning and annotated_objects:
        status = _find_warning_status(warning, annotated_objects)

    warning_sentence = _warning_sentence(warning, status)
    if warning_sentence:
        sentences.append(warning_sentence)

    sentences.append(_movement_phrase(path.get("safe_direction", "center")))

    return " ".join(sentences)