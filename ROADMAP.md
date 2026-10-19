# Foldsmith roadmap

Foldsmith is a new project, starting with a working open-tray generator. The
following estimates describe future development, not completed work or promised
delivery dates. Priorities will change after printing and assembling prototypes.

## Validate the first shape — 3–5 hours

- Print A4 and Letter samples on real printers; measure calibration and folded size.
- Assemble shallow, tall, and fractional-dimension trays; document tab usability.
- Add measured examples and regression cases for any discovered geometry problems.

## Multi-page printing — 8–12 hours

- Tile large nets across A4/Letter sheets without changing scale.
- Add page coordinates, overlap margins, alignment crosses, and assembly order.
- Test seams through folds and tabs, landscape pages, and exact-boundary cases.
- Success: reassembled pages reproduce a large reference net within measured tolerance.

## Matching lids and clearance — 6–8 hours

- Generate a separate lid with explicit fit clearance and configurable skirt height.
- Keep base dimensions distinct from outside dimensions.
- Test interference and fit using physical cardstock prototypes.

## Material thickness — 6–10 hours

- Document a fold allowance model and its assumptions.
- Accept material thickness and produce adjusted panels and tabs.
- Compare measured results on at least two paper/card stocks.
- Retain the uncompensated mode for simple paper crafts.

## Reusable designs and presets — 4–6 hours

- Save/load a versioned JSON design containing geometry only.
- Provide useful organizer presets and strict validation for malformed files.
- Test round trips, version errors, and deterministic exports.

## PDF export and print documentation — 5–8 hours

- Evaluate an optional PDF exporter while keeping the geometry core dependency-free.
- Preserve physical units, cut/fold distinction, and calibration marks.
- Document browser/editor print settings and known printer limitations.

**Estimated remaining work: 32–49 hours.** No users, release adoption, or physical
validation are claimed at this stage.
