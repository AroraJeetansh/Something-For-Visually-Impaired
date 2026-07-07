"""
distance_estimator.py

Classifies each detected object into a qualitative distance bucket
(Very Close / Close / Medium / Far) using thresholds that adapt to the
CURRENT SCENE's depth distribution -- not fixed numbers, since the
"depth" value from Depth Anything V2 is not calibrated to real-world
units yet (no meters).

Why percentile-based, not closeness-based
------------------------------------------------------------
navigation_service.py already computes a `closeness` value per object
as `1 - (median_depth / max_depth)`. That's usable for the path
planner's relative ranking, but it's a bit fragile as a basis for
qualitative labels: max_depth is a single pixel in the depth map, and
if that one pixel is a noisy outlier (common with depth models at
image edges/sky/reflections), every object's closeness shifts.

Instead, this module ranks each object's median depth against the
FULL distribution of depth values in the scene (percentile rank). An
object that's closer than 90% of everything else in the frame is
"Very Close" regardless of what any single extreme pixel reads. This
is more robust and is still 100% scene-adaptive, no hardcoded depth
numbers.

Calibration path (for later, per the roadmap -- do NOT implement yet)
------------------------------------------------------------
When real-world reference measurements are available (e.g. "object
measured at 2.3m had raw depth value 143.25 in this scene"), the
intended upgrade is a CALIBRATION_TABLE that maps depth/percentile to
meters, and a `get_distance_meters(obj)` function added alongside
`classify_distance`. Nothing about the call sites needs to change --
navigation_service.py would just additionally read a "distance_meters"
key if calibration is enabled. This is a deliberate seam left in the
architecture for that, not implemented now since no calibration data
exists yet.
"""

from typing import List, Dict, Any
import numpy as np

# Percentile bucket boundaries (object is closer than this % of the
# scene's depth values). These define the SHAPE of the buckets, not
# real-world distance -- e.g. "Very Close" = nearest 15% of depth
# values present in this particular frame.
VERY_CLOSE_PERCENTILE = 15
CLOSE_PERCENTILE = 45
MEDIUM_PERCENTILE = 75
# anything beyond MEDIUM_PERCENTILE -> "Far"

LABELS = ["Very Close", "Close", "Medium", "Far"]


def _percentile_rank(value: float, distribution: np.ndarray) -> float:
    """
    Returns what percentage of `distribution` is FARTHER than `value`
    (i.e. how close `value` is relative to the scene), 0-100.
    Lower depth = closer, so we invert the usual percentile direction.
    """
    if distribution.size == 0:
        return 50.0
    farther_count = np.sum(distribution > value)
    return float(farther_count) / distribution.size * 100.0


def _label_from_percentile(closeness_percentile: float) -> str:
    if closeness_percentile >= (100 - VERY_CLOSE_PERCENTILE):
        return "Very Close"
    if closeness_percentile >= (100 - CLOSE_PERCENTILE):
        return "Close"
    if closeness_percentile >= (100 - MEDIUM_PERCENTILE):
        return "Medium"
    return "Far"


def classify_distance(
    objects: List[Dict[str, Any]],
    depth_map: np.ndarray,
) -> List[Dict[str, Any]]:
    """
    Adds a "distance_label" key (Very Close/Close/Medium/Far) to each
    object, based on where its median depth falls within this frame's
    full depth distribution.

    objects: list of detected object dicts, each must have "depth"
        (the median depth value already computed in navigation_service)
    depth_map: the full depth map numpy array for this frame, used to
        build the scene's depth distribution.

    Returns a NEW list (does not mutate the input dicts).
    """
    if not objects:
        return []

    flat_depths = depth_map.flatten()

    labeled_objects = []
    for obj in objects:
        depth_value = obj.get("depth")

        if depth_value is None:
            label = "Unknown"
        else:
            closeness_percentile = _percentile_rank(depth_value, flat_depths)
            label = _label_from_percentile(closeness_percentile)

        new_obj = dict(obj)
        new_obj["distance_label"] = label
        labeled_objects.append(new_obj)

    return labeled_objects