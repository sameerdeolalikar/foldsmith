import contextlib
import io
import math
from pathlib import Path
import random
import tempfile
import unittest
from xml.etree import ElementTree as ET

from foldsmith.cli import main
from foldsmith.geometry import Tray, edges, faces
from foldsmith.svg import layout, render

NS = {"s": "http://www.w3.org/2000/svg"}


class GeometryTests(unittest.TestCase):
    def test_net_has_one_closed_cut_boundary_and_eight_folds(self):
        cuts, folds = edges(Tray(80, 60, 25))
        self.assertEqual(len(folds), 8)
        self.assertEqual(len(cuts), 20)
        adjacency = {}
        for a, b in cuts:
            adjacency.setdefault(a, []).append(b)
            adjacency.setdefault(b, []).append(a)
        self.assertTrue(all(len(neighbors) == 2 for neighbors in adjacency.values()))
        visited, pending = set(), [next(iter(adjacency))]
        while pending:
            point = pending.pop()
            if point not in visited:
                visited.add(point)
                pending.extend(adjacency[point])
        self.assertEqual(visited, set(adjacency))

    def test_base_retains_requested_dimensions(self):
        tray = Tray(80, 60, 25)
        base = faces(tray)[0]
        self.assertEqual(base.points, ((25, 25), (105, 25), (105, 85), (25, 85)))
        self.assertEqual(tray.size, (130, 110))

    def test_fractional_nets_keep_shared_edges_and_bounds(self):
        rng = random.Random(42)
        for _ in range(200):
            h, d = rng.uniform(5, 100), rng.uniform(10, 150)
            tray = Tray(rng.uniform(5, 200), d, h, min(h * 0.8, d * 0.4))
            with self.subTest(tray=tray):
                cuts, folds = edges(tray)
                self.assertEqual((len(cuts), len(folds)), (20, 8))
                width, height = tray.size
                for face in faces(tray):
                    for x, y in face.points:
                        self.assertTrue(-1e-8 <= x <= width + 1e-8)
                        self.assertTrue(-1e-8 <= y <= height + 1e-8)

    def test_invalid_and_nonfinite_dimensions_are_rejected(self):
        for value in (0, -1, 0.5, math.nan, math.inf, 5001):
            for field in ("width", "depth", "height", "tab"):
                args = dict(width=80, depth=60, height=25, tab=10)
                args[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    Tray(**args)

    def test_tabs_cannot_overlap_after_folding_or_exceed_wall(self):
        for args in ((80, 20, 25, 10), (80, 60, 5, 10)):
            with self.assertRaises(ValueError):
                Tray(*args)


class PrintTests(unittest.TestCase):
    def test_a4_physical_units_and_calibration_are_preserved(self):
        svg = ET.fromstring(render(Tray(80, 60, 25)))
        self.assertEqual(svg.attrib["width"], "210mm")
        self.assertEqual(svg.attrib["height"], "297mm")
        self.assertEqual(svg.attrib["viewBox"], "0 0 210 297")
        line = svg.find("s:g[@id='calibration']/s:line", NS)
        self.assertEqual(float(line.attrib["x2"]) - float(line.attrib["x1"]), 50)
        self.assertNotIn("scale(", ET.tostring(svg, encoding="unicode"))

    def test_landscape_is_selected_only_when_needed(self):
        tray = Tray(180, 50, 20)
        sheet = layout(tray)
        self.assertEqual((sheet.width, sheet.height), (297, 210))
        with self.assertRaises(ValueError):
            layout(tray, orientation="portrait")

    def test_letter_and_custom_paper(self):
        self.assertEqual(layout(Tray(80, 60, 25), "letter").width, 215.9)
        tray = Tray(300, 200, 40)
        sheet = layout(tray, "custom")
        self.assertEqual((sheet.width, sheet.height), (400, 346))
        with self.assertRaisesRegex(ValueError, "will not be scaled"):
            layout(tray)

    def test_net_never_overlaps_header_or_footer(self):
        for tray in (Tray(80, 60, 25), Tray(180, 50, 20), Tray(300, 200, 40)):
            sheet = layout(tray, "custom")
            self.assertGreaterEqual(sheet.x, 10)
            self.assertGreaterEqual(sheet.y, 32)
            self.assertLessEqual(sheet.x + tray.size[0], sheet.width - 10)
            self.assertLessEqual(sheet.y + tray.size[1], sheet.height - 34)

    def test_cut_and_fold_layers_are_separate(self):
        svg = ET.fromstring(render(Tray(80, 60, 25)))
        cuts = svg.find(".//s:g[@id='cut-lines']", NS)
        folds = svg.find(".//s:g[@id='fold-lines']", NS)
        self.assertEqual(len(cuts), 20)
        self.assertEqual(len(folds), 8)
        self.assertNotIn("stroke-dasharray", cuts.attrib)
        self.assertIn("stroke-dasharray", folds.attrib)

    def test_invalid_layout_options(self):
        for paper, orientation in (("a3", "auto"), ("a4", "diagonal"), ("custom", "portrait")):
            with self.assertRaises(ValueError):
                layout(Tray(80, 60, 25), paper, orientation)


class CliTests(unittest.TestCase):
    def test_output_is_not_overwritten_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "tray.svg"
            args = ["--width", "80", "--depth", "60", "--height", "25", "-o", str(target)]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(args), 0)
            target.write_text("keep me")
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                main(args)
            self.assertEqual(error.exception.code, 2)
            self.assertEqual(target.read_text(), "keep me")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(args + ["--force"]), 0)
            ET.fromstring(target.read_text())

    def test_failed_fit_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "tray.svg"
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                main(["--width", "300", "--depth", "200", "--height", "40", "-o", str(target)])
            self.assertEqual(error.exception.code, 2)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
