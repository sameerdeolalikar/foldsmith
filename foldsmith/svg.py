"""Lay out a dimensionally accurate net on a physical SVG sheet."""

from dataclasses import dataclass
from xml.etree import ElementTree as ET

from .geometry import Tray, edges, faces

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
PAPERS = {"a4": (210.0, 297.0), "letter": (215.9, 279.4)}
MARGIN = 10.0
HEADER = 22.0
FOOTER = 24.0


@dataclass(frozen=True)
class Layout:
    width: float
    height: float
    x: float
    y: float


def layout(tray: Tray, paper: str = "a4", orientation: str = "auto") -> Layout:
    if paper not in (*PAPERS, "custom"):
        raise ValueError("paper must be a4, letter, or custom")
    if orientation not in ("auto", "portrait", "landscape"):
        raise ValueError("orientation must be auto, portrait, or landscape")
    net_w, net_h = tray.size
    required_w = max(net_w + 2 * MARGIN, 180.0)
    required_h = net_h + 2 * MARGIN + HEADER + FOOTER
    if paper == "custom":
        if orientation != "auto":
            raise ValueError("custom paper uses auto orientation only")
        return Layout(required_w, required_h, (required_w - net_w) / 2, MARGIN + HEADER)
    w, h = PAPERS[paper]
    candidates = [(w, h), (h, w)] if orientation == "auto" else (
        [(w, h)] if orientation == "portrait" else [(h, w)]
    )
    for w, h in candidates:
        if required_w <= w and required_h <= h:
            return Layout(w, h, (w - net_w) / 2, MARGIN + HEADER + (
                h - required_h
            ) / 2)
    raise ValueError(
        f"pattern needs at least {required_w:g} × {required_h:g} mm including "
        f"print margins and instructions; it does not fit {paper.upper()} "
        f"({orientation}). Use smaller dimensions or --paper custom. "
        "The pattern will not be scaled."
    )


def element(parent: ET.Element, tag: str, **attrs: str) -> ET.Element:
    return ET.SubElement(parent, f"{{{NS}}}{tag}", attrs)


def text(parent: ET.Element, x: float, y: float, content: str, size: float = 3.2,
         **attrs: str) -> None:
    node = element(parent, "text", x=f"{x:g}", y=f"{y:g}",
                   **{"font-size": f"{size:g}", **attrs})
    node.text = content


def render(tray: Tray, paper: str = "a4", orientation: str = "auto") -> str:
    sheet = layout(tray, paper, orientation)
    root = ET.Element(f"{{{NS}}}svg", {
        "width": f"{sheet.width:g}mm", "height": f"{sheet.height:g}mm",
        "viewBox": f"0 0 {sheet.width:g} {sheet.height:g}",
        "role": "img", "aria-labelledby": "title description",
        "font-family": "sans-serif", "fill": "#172b36",
    })
    element(root, "title", id="title").text = "Foldsmith printable tray pattern"
    element(root, "desc", id="description").text = (
        f"Open tray: {tray.width:g} by {tray.depth:g} mm base, "
        f"{tray.height:g} mm walls. Solid lines are cuts; dashed lines are folds. "
        "Glue the four shaded tabs inside the adjacent side walls."
    )
    element(root, "rect", width="100%", height="100%", fill="white")
    text(root, MARGIN, 16, "FOLDSMITH / OPEN TRAY", 5,
         **{"font-weight": "bold"})
    text(root, MARGIN, 23, (
        f"Base {tray.width:g} × {tray.depth:g} mm · wall {tray.height:g} mm · "
        f"glue tab {tray.tab:g} mm"
    ))
    net = element(root, "g", id="pattern", transform=f"translate({sheet.x:g} {sheet.y:g})")
    for face in faces(tray):
        if face.glue:
            element(net, "polygon", points=" ".join(f"{x:g},{y:g}" for x, y in face.points),
                    fill="#e3e9ec")
        else:
            xs, ys = zip(*face.points)
            if max(xs) - min(xs) >= 24 and max(ys) - min(ys) >= 12:
                text(net, (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2 + 1,
                     face.name, 2.6, **{"text-anchor": "middle", "fill": "#61747f"})
    cuts, folds = edges(tray)
    for name, segments, dash in (("cut-lines", cuts, None), ("fold-lines", folds, "2 1.5")):
        attrs = {"id": name, "fill": "none", "stroke": "#172b36", "stroke-width": "0.25"}
        if dash:
            attrs["stroke-dasharray"] = dash
        group = element(net, "g", **attrs)
        for (x1, y1), (x2, y2) in segments:
            element(group, "line", x1=f"{x1:g}", y1=f"{y1:g}", x2=f"{x2:g}", y2=f"{y2:g}")
    y = sheet.height - 26
    text(root, MARGIN, y, "Cut solid lines. Score dashed lines. Fold walls up; glue tabs inside sides.", 3)
    text(root, MARGIN, y + 6, "Print at 100% / actual size. Disable fit-to-page and browser headers/footers.", 3)
    ruler = element(root, "g", id="calibration", stroke="#172b36", **{"stroke-width": "0.3"})
    for x1, y1, x2, y2 in ((10, y + 12, 60, y + 12),
                            (10, y + 10, 10, y + 14), (60, y + 10, 60, y + 14)):
        element(ruler, "line", x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2))
    text(root, 64, y + 13, "50 mm — measure before cutting", 3)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"
