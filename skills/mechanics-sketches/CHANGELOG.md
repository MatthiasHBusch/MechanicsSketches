# Changelog

## [1.3.0] - 2026-05-04

### Added
- `pressure` element: n radial arrows around a central annotation (Drucksymbol)
- `abs_length` parameter for `fixed_support`: absolute wall length in scene units, scale-independent

## [1.2.0] - 2026-04-13

### Added
- `fontsize` parameter to all functions with `fontsize_scale` for absolute font size override
- `force_normal` element for forces perpendicular to the image plane (dot/cross symbols)

### Changed
- `fontsize` parameter is now truly absolute: specifies final rendered size in points, independent of `scale_factor`

## [1.1.0] - 2026-04-08

### Added
- `shear_distributed_load` element for tangential/shear loads with arrows parallel to surface
- Dynamic arrow placement algorithm with constant gap between arrows
- Distribution line and vertical end lines for shear load visualization
- `show_distribution_line` parameter for distributed_load and shear_distributed_load
- `tip_at_surface` parameter for force, distributed_load, and shear_distributed_load

### Changed
- Test scripts updated to use scale=30 and fontsize=20 for better visibility
- Shear load annotation positioned closer when distribution line is hidden

## [1.0.0] - 2026-02-23

### Added
- Initial release of the MechanicsSketches OpenClaw skill
- Support for beams, trusses, pinned/roller/fixed supports, hinges
- Force and moment arrows with LaTeX annotations
- Dimension arrows and thickness dimensions
- Coordinate system indicators
- Helper script `generate_sketch.py` for JSON-to-PDF rendering
- Condensed API reference in `references/api_reference.md`
