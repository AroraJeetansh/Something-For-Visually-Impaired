"""
path_planner.py

Chooses the safest navigation direction for the user.

Design notes (why this differs from the previous version)
------------------------------------------------------------
The previous planner only looked at the single nearest object and then
picked the "opposite" direction by a fixed rule (e.g. left -> right).
This is unsafe because it never checks whether the opposite direction is
also blocked. It can produce contradictory instructions like
"obstacle on your left -> keep left" if the per-direction string
mapping is misread downstream, and more importantly it can route a user
straight into a second obstacle on the "safe" side.

This version:
1. Scores every sector (far_left, left, center, right, far_right) using
   ALL detected objects, not just the closest one. Closer + larger
   objects contribute more risk to their sector.
2. Picks the sector with the lowest (risk + turn_cost) score, where
   turn_cost penalizes sharper turns so the user isn't routed into a
   wide swerve when a small step would do.
3. Still returns the same API contract: safe_direction, danger,
   warning, sector_scores -- so callers (speech_service, etc.) don't
   need to change.
"""

from typing import List, Dict, Any, Optional

VERY_CLOSE = 0.85          # closeness threshold that counts as "danger"
DANGER_PATH_SECTORS = ("left", "center", "right")  # the user's immediate walking path

SECTORS = [
    "far_left",
    "left",
    "center",
    "right",
    "far_right",
]

# How costly it is to move into each sector relative to walking straight.
# Lower cost = preferred when risk is roughly equal.
TURN_COST = {
    "center": 0.0,
    "left": 1.0,
    "right": 1.0,
    "far_left": 2.0,
    "far_right": 2.0,
}

# How much a unit of "risk" outweighs a unit of "turn cost".
# This must dominate turn_cost so the planner never picks a riskier
# sector just because it's a smaller turn.
DANGER_WEIGHT = 10.0


def _object_risk(obj: Dict[str, Any]) -> float:
    """
    Risk contribution of a single object to its sector.
    Closer objects (higher closeness) and larger objects (higher
    normalized area) contribute more risk.
    """
    closeness = obj.get("closeness", 0.0)
    area = obj.get("normalized_area", 0.0)
    # closeness is squared so risk ramps up sharply as something
    # approaches, rather than scaling linearly.
    return (closeness ** 2) * (1.0 + area)


def _compute_sector_scores(objects: List[Dict[str, Any]]) -> Dict[str, float]:
    scores = {s: 0.0 for s in SECTORS}
    for obj in objects:
        direction = obj.get("direction")
        if direction in scores:
            scores[direction] += _object_risk(obj)
    return scores


def _compute_danger(objects: List[Dict[str, Any]]) -> bool:
    """
    Danger means something is very close AND in the user's immediate
    walking path (left/center/right) -- not the peripheral far sectors.
    """
    for obj in objects:
        if (
            obj.get("direction") in DANGER_PATH_SECTORS
            and obj.get("closeness", 0.0) >= VERY_CLOSE
        ):
            return True
    return False


def _nearest_object(objects: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not objects:
        return None
    return max(objects, key=lambda o: o.get("closeness", 0.0))


def plan_path(objects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Main entry point. Returns:
        {
            "safe_direction": one of SECTORS,
            "danger": bool,
            "warning": nearest object dict or None,
            "sector_scores": {sector: risk_score, ...}
        }
    """
    if not objects:
        return {
            "safe_direction": "center",
            "danger": False,
            "warning": None,
            "sector_scores": {s: 0.0 for s in SECTORS},
        }

    sector_scores = _compute_sector_scores(objects)
    danger = _compute_danger(objects)

    # Combined cost: risk dominates, turn distance is the tie-breaker.
    combined_cost = {
        s: (sector_scores[s] * DANGER_WEIGHT) + TURN_COST[s]
        for s in SECTORS
    }

    safe_direction = min(combined_cost, key=combined_cost.get)

    return {
        "safe_direction": safe_direction,
        "danger": danger,
        "warning": _nearest_object(objects),
        "sector_scores": sector_scores,
    }