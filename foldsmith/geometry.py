"""An open tray net: five faces and four tapered corner glue tabs.

All coordinates and dimensions are millimetres. Shared polygon edges are
folds; exposed edges are cuts. No printer-dependent scaling is applied.
"""

from collections import Counter
from dataclasses import dataclass
import math

Point = tuple[float, float]
Edge = tuple[Point, Point]


@dataclass(frozen=True)
class Tray:
    width: float
    depth: float
    height: float
    tab: float = 10.0

    def __post_init__(self) -> None:
        for name in ("width", "depth", "height", "tab"):
            value = getattr(self, name)
            if not math.isfinite(value) or not 1 <= value <= 5000:
                raise ValueError(f"{name} must be a finite number from 1 to 5000 mm")
        if self.tab > self.height:
            raise ValueError("tab width cannot exceed wall height")
        if 2 * self.tab >= self.depth:
            raise ValueError("two glue tabs must fit along the depth without overlapping")

    @property
    def size(self) -> Point:
        return self.width + 2 * self.height, self.depth + 2 * self.height


@dataclass(frozen=True)
class Face:
    name: str
    points: tuple[Point, ...]
    glue: bool = False


def rectangle(name: str, x: float, y: float, w: float, h: float) -> Face:
    return Face(name, ((x, y), (x + w, y), (x + w, y + h), (x, y + h)))


def faces(tray: Tray) -> tuple[Face, ...]:
    w, d, h, t = tray.width, tray.depth, tray.height, tray.tab
    result = [
        rectangle("BASE", h, h, w, d),
        rectangle("BACK", h, 0, w, h),
        rectangle("FRONT", h, h + d, w, h),
        rectangle("LEFT", 0, h, h, d),
        rectangle("RIGHT", h + w, h, h, d),
    ]
    taper = min(h * 0.2, t * 0.4)
    for y, label in ((0, "back"), (h + d, "front")):
        result.extend((
            Face(f"{label}-left tab", (
                (h, y), (h - t, y + taper),
                (h - t, y + h - taper), (h, y + h),
            ), glue=True),
            Face(f"{label}-right tab", (
                (h + w, y), (h + w + t, y + taper),
                (h + w + t, y + h - taper), (h + w, y + h),
            ), glue=True),
        ))
    return tuple(result)


def edges(tray: Tray) -> tuple[tuple[Edge, ...], tuple[Edge, ...]]:
    counts: Counter[Edge] = Counter()
    for face in faces(tray):
        for i, start in enumerate(face.points):
            end = face.points[(i + 1) % len(face.points)]
            # Arithmetic paths to a shared vertex can differ at float precision.
            a = (round(start[0], 8), round(start[1], 8))
            b = (round(end[0], 8), round(end[1], 8))
            counts[tuple(sorted((a, b)))] += 1
    cuts = tuple(edge for edge, count in counts.items() if count == 1)
    folds = tuple(edge for edge, count in counts.items() if count == 2)
    return cuts, folds
