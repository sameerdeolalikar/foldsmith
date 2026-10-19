"""Command-line interface; no network calls or runtime dependencies."""

import argparse
from pathlib import Path

from . import __version__
from .geometry import Tray
from .svg import render


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate an open paper tray as a printable SVG. All dimensions are millimetres."
    )
    parser.add_argument("--version", action="version", version=f"foldsmith {__version__}")
    parser.add_argument("--width", required=True, type=float, help="base width in mm")
    parser.add_argument("--depth", required=True, type=float, help="base depth in mm")
    parser.add_argument("--height", required=True, type=float, help="wall height in mm")
    parser.add_argument("--tab", type=float, default=10, help="glue tab width in mm (default: 10)")
    parser.add_argument("--paper", choices=["a4", "letter", "custom"], default="a4")
    parser.add_argument("--orientation", choices=["auto", "portrait", "landscape"], default="auto")
    parser.add_argument("--output", "-o", type=Path, required=True, help="destination SVG path")
    parser.add_argument("--force", action="store_true", help="replace an existing output file")
    args = parser.parse_args(argv)
    try:
        svg = render(Tray(args.width, args.depth, args.height, args.tab), args.paper, args.orientation)
        with args.output.open("w" if args.force else "x", encoding="utf-8") as stream:
            stream.write(svg)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"foldsmith: {exc}\n")
    print(f"Created {args.output}. Print at actual size and check the 50 mm calibration line.")
    return 0
