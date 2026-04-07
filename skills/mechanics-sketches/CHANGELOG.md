# Changelog

## [1.1.0] - 2026-04-07

### Added
- `shear_distributed_load` element for tangential/shear loads with arrows parallel to surface
- Dynamic arrow placement algorithm with constant gap between arrows
- Distribution line and vertical end lines for shear load visualization

### Changed
- Test scripts updated to use scale=30 and fontsize=20 for better visibility

## [1.0.0] - 2026-02-23

### Added
- Initial release of the MechanicsSketches OpenClaw skill
- Support for beams, trusses, pinned/roller/fixed supports, hinges
- Force and moment arrows with LaTeX annotations
- Dimension arrows and thickness dimensions
- Coordinate system indicators
- Helper script `generate_sketch.py` for JSON-to-PDF rendering
- Condensed API reference in `references/api_reference.md`
