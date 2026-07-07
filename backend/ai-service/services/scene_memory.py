"""
scene_memory.py

Tracks detected objects across consecutive frames so the assistant can
say "still ahead" / "moving away" instead of repeating "Person ahead."
every single frame, and so it can announce when a previously dangerous
path has become clear.

Design notes
------------------------------------------------------------
There is no persistent object ID coming from the detector (no
ByteTrack/DeepSORT-style tracker), so this module does lightweight
frame-to-frame matching itself:

  - Candidates are matched by (same object class) + (closest box
    overlap, falling back to closest direction/closeness if boxes
    don't overlap -- e.g. because the camera or user moved slightly).
  - Each matched object gets a `status` of:
        "new"           -- not seen in the previous frame
        "still"         -- closeness roughly unchanged
        "approaching"   -- closeness increased meaningfully
        "moving_away"   -- closeness decreased meaningfully
  - A small grace period (MAX_MISSED_FRAMES) keeps a track alive for a
    couple of frames if the object briefly drops out of detection, so
    a single missed frame doesn't reset "still" back to "new".

IMPORTANT - statefulness:
SceneMemory holds state and must be instantiated ONCE PER USER SESSION
(e.g. per device/connection), not as a single global instance shared
across all users. In your FastAPI route layer, keep a
dict[session_id, SceneMemory] (or attach one instance to the websocket
connection / request session) and call .update() on each new frame for
that session.
"""

from typing import List, Dict, Any, Optional, Tuple
import time

# closeness change beyond this magnitude counts as approaching/moving away
CLOSENESS_DELTA_THRESHOLD = 0.07

# how many consecutive frames a track survives without a fresh match
MAX_MISSED_FRAMES = 2

# minimum box IoU to consider two boxes "the same object"
IOU_MATCH_THRESHOLD = 0.3


def _iou(box_a: List[float], box_b: List[float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter_area

    if union <= 0:
        return 0.0
    return inter_area / union


class _Track:
    __slots__ = ("object_class", "direction", "closeness", "box", "missed_frames", "last_seen")

    def __init__(self, obj: Dict[str, Any]):
        self.object_class = obj.get("object")
        self.direction = obj.get("direction")
        self.closeness = obj.get("closeness", 0.0)
        self.box = obj.get("box")
        self.missed_frames = 0
        self.last_seen = time.time()


class SceneMemory:
    """
    One instance per user session. Call update() once per processed
    frame with the current frame's detected objects and the planner's
    path output.
    """

    def __init__(self):
        self._tracks: List[_Track] = []
        self._previous_danger: bool = False

    def update(
        self,
        objects: List[Dict[str, Any]],
        path: Dict[str, Any],
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Returns:
            (objects_with_status, path_just_cleared)

            objects_with_status: same objects passed in, each with an
                added "status" key (new/still/approaching/moving_away)

            path_just_cleared: True only on the frame where danger
                transitions from True -> False, so the caller can say
                "Path clear" once instead of staying silent or
                repeating "Path is clear" every frame.
        """
        matched_objects = self._match_and_annotate(objects)

        current_danger = bool(path.get("danger", False))
        path_just_cleared = self._previous_danger and not current_danger
        self._previous_danger = current_danger

        return matched_objects, path_just_cleared

    def reset(self) -> None:
        """Clear all memory, e.g. when a navigation session ends/restarts."""
        self._tracks = []
        self._previous_danger = False

    # ------------------------------------------------------------
    # internal matching
    # ------------------------------------------------------------

    def _match_and_annotate(self, objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        annotated: List[Dict[str, Any]] = []
        used_track_indices = set()

        for obj in objects:
            track_index = self._find_best_track(obj, used_track_indices)

            if track_index is None:
                status = "new"
            else:
                used_track_indices.add(track_index)
                prev_track = self._tracks[track_index]
                status = self._status_from_delta(
                    prev_track.closeness, obj.get("closeness", 0.0)
                )

            annotated_obj = dict(obj)
            annotated_obj["status"] = status
            annotated.append(annotated_obj)

        # age out / drop tracks that weren't matched this frame
        new_tracks: List[_Track] = []
        for i, track in enumerate(self._tracks):
            if i in used_track_indices:
                continue
            track.missed_frames += 1
            if track.missed_frames <= MAX_MISSED_FRAMES:
                new_tracks.append(track)

        # add freshly matched/created tracks for this frame's objects
        for obj in objects:
            new_tracks.append(_Track(obj))

        self._tracks = new_tracks
        return annotated

    def _find_best_track(
        self, obj: Dict[str, Any], used_indices: set
    ) -> Optional[int]:
        best_index = None
        best_score = 0.0

        obj_box = obj.get("box")
        obj_class = obj.get("object")
        obj_direction = obj.get("direction")

        for i, track in enumerate(self._tracks):
            if i in used_indices or track.object_class != obj_class:
                continue

            score = 0.0
            if obj_box and track.box:
                score = _iou(obj_box, track.box)

            if score < IOU_MATCH_THRESHOLD:
                # fall back to direction match when boxes don't overlap
                # enough (camera/user moved between frames)
                if track.direction == obj_direction:
                    score = max(score, IOU_MATCH_THRESHOLD)
                else:
                    continue

            if score > best_score:
                best_score = score
                best_index = i

        return best_index

    @staticmethod
    def _status_from_delta(previous_closeness: float, current_closeness: float) -> str:
        delta = current_closeness - previous_closeness
        if delta >= CLOSENESS_DELTA_THRESHOLD:
            return "approaching"
        if delta <= -CLOSENESS_DELTA_THRESHOLD:
            return "moving_away"
        return "still"