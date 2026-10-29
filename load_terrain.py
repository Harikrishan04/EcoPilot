"""
load_terrain.py — EcoPilot Phase 1: Terrain Data Pipeline
=========================================================

Fetches SRTM GL1 (30 m) elevation data for the Mantripukhri / IIIT Manipur
campus bounding box, then processes and exports all required terrain artefacts.

Tools used (as required by the project spec):
  * rasterio  — read/write GeoTIFF, crop to bounding box, bilinear resample
  * numpy     — array math, normalisation, .npy export
  * matplotlib— 4-panel preview image (contourf, imshow, 3-D surface, histogram)

Data-acquisition strategy (tried in order):
  1. OpenTopography SRTM GL1 GeoTIFF  (needs OPENTOPO_API_KEY env var)
  2. Open-Elevation batch-point API   (free, no key — backed by SRTM)
  3. Cached raw elevation JSON        (from a previous successful fetch)
  4. sys.exit(1)                      (never silently generate synthetic data)

Bounding box (WGS-84):
  south=24.8423, north=24.8559, west=93.9302, east=93.9442
  (Mantripukhri, Imphal West, Manipur, India)

Outputs (written to terrain/):
  terrain.npy             — float32, shape (GRID_SIZE, GRID_SIZE), values [0,1]
  terrain.json            — JSON with metadata + nested list of rows
  terrain_heightmap.png   — 8-bit grayscale PNG for the browser canvas
  terrain_preview.png     — matplotlib 4-panel composite for visual verification

Usage:
  python3 load_terrain.py                        # auto-fetch + rasterio pipeline
  python3 load_terrain.py --local path/to/dem.tif # use a pre-downloaded GeoTIFF
  python3 load_terrain.py --grid-size 32          # 32×32 instead of 24×24
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request
from typing import Tuple

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_bounds as transform_from_bounds
from rasterio.windows import from_bounds

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for headless operation
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# ──────────────────────────────────────────────────────────────────────────────
# Configuration — Mantripukhri, Imphal West, Manipur (IIIT Manipur campus area)
# ──────────────────────────────────────────────────────────────────────────────
SOUTH = 24.8423
NORTH = 24.8559
WEST  = 93.9302
EAST  = 93.9442

GRID_SIZE = 24  # N×N output grid

# Output paths (relative to this script)
OUT_DIR        = os.path.join(os.path.dirname(os.path.abspath(__file__)), "terrain")
NPY_PATH       = os.path.join(OUT_DIR, "terrain.npy")
JSON_PATH      = os.path.join(OUT_DIR, "terrain.json")
HEIGHTMAP_PATH = os.path.join(OUT_DIR, "terrain_heightmap.png")
PREVIEW_PATH   = os.path.join(OUT_DIR, "terrain_preview.png")
RAW_ELEV_PATH  = os.path.join(OUT_DIR, "terrain_raw_elevations_m.json")
GEOTIFF_PATH   = os.path.join(OUT_DIR, "srtm_gl1.tif")


# ══════════════════════════════════════════════════════════════════════════════
# 1. DATA ACQUISITION
# ══════════════════════════════════════════════════════════════════════════════

def fetch_srtm_geotiff(dest_path: str) -> bool:
    """Download the SRTM GL1 GeoTIFF from OpenTopography.

    Requires a free API key set in the OPENTOPO_API_KEY environment variable.
    Register at https://portal.opentopography.org/newUser to get one.
    Returns True if the GeoTIFF was saved successfully.
    """
    api_key = os.getenv("OPENTOPO_API_KEY", "")
    if not api_key:
        print("[source-1] OPENTOPO_API_KEY not set — skipping OpenTopography.")
        return False

    params = {
        "demtype":      "SRTMGL1",
        "south":        SOUTH,
        "north":        NORTH,
        "west":         WEST,
        "east":         EAST,
        "outputFormat": "GTiff",
        "API_Key":      api_key,
    }
    url = "https://portal.opentopography.org/API/globaldem?" + urllib.parse.urlencode(params)
    print("[source-1] Requesting SRTM GL1 GeoTIFF from OpenTopography …")

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()

        # Validate — GeoTIFFs start with TIFF magic bytes
        if len(data) < 1024 or data[:2] not in (b"II", b"MM"):
            print(f"  Response is not a valid TIFF ({len(data)} bytes). Skipping.")
            return False

        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "wb") as f:
            f.write(data)
        print(f"  Saved {len(data)/1024:.1f} KB → {dest_path}")
        return True

    except Exception as exc:
        print(f"  Download failed: {exc}")
        return False


def fetch_open_elevation(grid_size: int) -> np.ndarray | None:
    """Query the Open-Elevation API (free, no key) for elevation at grid points.

    Sends a single batch POST with grid_size² coordinates.
    Returns a (grid_size, grid_size) float32 array of elevations in metres,
    or None on failure.  The API is backed by SRTM data.
    """
    # Build sample points — row 0 = northernmost
    lats = np.linspace(NORTH, SOUTH, grid_size)
    lons = np.linspace(WEST,  EAST,  grid_size)

    locations = [
        {"latitude": float(lat), "longitude": float(lon)}
        for lat in lats
        for lon in lons
    ]

    url = "https://api.open-elevation.com/api/v1/lookup"
    payload = json.dumps({"locations": locations}).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )

    print(f"[source-2] Open-Elevation API — querying {len(locations)} points …")
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = json.load(resp)

        results = body.get("results", [])
        if len(results) != grid_size * grid_size:
            print(f"  Unexpected result count: {len(results)} (need {grid_size**2})")
            return None

        elev = np.array([r["elevation"] for r in results], dtype=np.float32)
        elev = elev.reshape((grid_size, grid_size))
        print(f"  Raw elevations: {elev.min():.1f} – {elev.max():.1f} m")
        return elev

    except Exception as exc:
        print(f"  Request failed: {exc}")
        return None


def load_cached_raw_elevations() -> np.ndarray | None:
    """Load raw-metre elevations from a previous successful fetch (JSON cache)."""
    if not os.path.isfile(RAW_ELEV_PATH):
        return None
    try:
        with open(RAW_ELEV_PATH) as f:
            d = json.load(f)
        values = d.get("values_m") or d.get("values")
        if values is None:
            return None
        arr = np.array(values, dtype=np.float32)
        print(f"[source-3] Loaded cached elevations from {RAW_ELEV_PATH}")
        print(f"  Shape: {arr.shape}  range: {arr.min():.1f} – {arr.max():.1f} m")
        return arr
    except Exception as exc:
        print(f"  Cache load failed: {exc}")
        return None


def save_raw_elevations(raw_m: np.ndarray, source: str) -> None:
    """Save raw-metre elevations as JSON for auditing and cache."""
    os.makedirs(OUT_DIR, exist_ok=True)
    payload = {
        "source":    source,
        "grid_size": raw_m.shape[0],
        "bbox":      {"south": SOUTH, "north": NORTH, "west": WEST, "east": EAST},
        "min_m":     float(raw_m.min()),
        "max_m":     float(raw_m.max()),
        "values_m":  np.round(raw_m, 2).tolist(),
    }
    with open(RAW_ELEV_PATH, "w") as f:
        json.dump(payload, f, separators=(",", ":"))
    print(f"  Saved raw elevations → {RAW_ELEV_PATH}")


def write_geotiff_from_array(arr: np.ndarray, path: str) -> None:
    """Write a numpy array as a single-band GeoTIFF (EPSG:4326).

    This allows the rasterio processing path (process_geotiff) to be
    exercised even when the data came from the Open-Elevation API rather
    than a direct GeoTIFF download.
    """
    rows, cols = arr.shape
    transform = transform_from_bounds(WEST, SOUTH, EAST, NORTH, cols, rows)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with rasterio.open(
        path, "w",
        driver="GTiff",
        height=rows,
        width=cols,
        count=1,
        dtype=arr.dtype,
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(arr, 1)
    print(f"  Wrote intermediate GeoTIFF → {path}")


# ══════════════════════════════════════════════════════════════════════════════
# 2. RASTERIO PROCESSING
# ══════════════════════════════════════════════════════════════════════════════

def process_geotiff(tif_path: str, grid_size: int) -> np.ndarray:
    """Read a GeoTIFF with rasterio, crop to bbox, bilinear-resample to
    grid_size×grid_size. Returns raw elevation array in metres.
    """
    print(f"[rasterio] Processing GeoTIFF: {tif_path}")
    with rasterio.open(tif_path) as src:
        print(f"  CRS: {src.crs}  |  bounds: {src.bounds}")
        print(f"  Native size: {src.width}×{src.height}  |  dtype: {src.dtypes[0]}")

        # Crop to bounding box
        window = from_bounds(WEST, SOUTH, EAST, NORTH, transform=src.transform)

        # Read with bilinear resampling to target grid size
        data = src.read(
            1,                              # band 1 (elevation)
            window=window,
            out_shape=(grid_size, grid_size),
            resampling=Resampling.bilinear,
        ).astype(np.float32)

        # Replace NoData with NaN
        if src.nodata is not None:
            data[data == src.nodata] = np.nan

    # Fill any NaN gaps with iterative neighbour-mean
    if np.isnan(data).any():
        print(f"  Filling {np.isnan(data).sum()} NaN cells …")
        for _ in range(10):
            mask = np.isnan(data)
            if not mask.any():
                break
            padded = np.pad(data, 1, mode="edge")
            neigh_mean = np.nanmean([
                padded[:-2, 1:-1],   # north
                padded[2:,  1:-1],   # south
                padded[1:-1, :-2],   # west
                padded[1:-1, 2:],    # east
            ], axis=0)
            data[mask] = neigh_mean[mask]

    print(f"  Elevation after crop+resample: {data.min():.1f} – {data.max():.1f} m")
    return data


# ══════════════════════════════════════════════════════════════════════════════
# 3. NORMALISATION
# ══════════════════════════════════════════════════════════════════════════════

def normalise(arr: np.ndarray) -> Tuple[np.ndarray, float, float]:
    """Normalise to [0, 1]. Returns (normalised_grid, min_metres, max_metres)."""
    lo = float(np.nanmin(arr))
    hi = float(np.nanmax(arr))
    span = hi - lo
    if span < 0.01:
        print(f"[warn] Very small elevation range ({span:.3f} m). Nearly flat.")
        span = max(span, 1.0)
    norm = ((arr - lo) / span).astype(np.float32)
    norm = np.clip(norm, 0.0, 1.0)
    return norm, lo, hi


# ══════════════════════════════════════════════════════════════════════════════
# 4. EXPORT FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def save_npy(grid: np.ndarray) -> None:
    """Save normalised grid as terrain.npy (numpy binary, float32)."""
    os.makedirs(OUT_DIR, exist_ok=True)
    np.save(NPY_PATH, grid)
    size_kb = os.path.getsize(NPY_PATH) / 1024
    print(f"[save] terrain.npy         → {NPY_PATH}  "
          f"(shape={grid.shape}, dtype={grid.dtype}, {size_kb:.1f} KB)")


def save_json(grid: np.ndarray, source_label: str, lo: float, hi: float) -> None:
    """Save normalised grid as terrain.json with full metadata."""
    os.makedirs(OUT_DIR, exist_ok=True)
    # Round values to 4 decimal places to keep file compact
    values = [[round(float(v), 4) for v in row] for row in grid]
    payload = {
        "grid_size": int(grid.shape[0]),
        "south": SOUTH, "north": NORTH, "west": WEST, "east": EAST,
        "source": source_label,
        "description": (
            "Normalised SRTM GL1 elevation grid for Mantripukhri, Imphal West, "
            "Manipur, India. Row 0 = northernmost. "
            "Values in [0, 1]: 0 = lowest point, 1 = highest point in bbox."
        ),
        "min_normalised": round(float(grid.min()), 4),
        "max_normalised": round(float(grid.max()), 4),
        "min_elevation_m": round(lo, 2),
        "max_elevation_m": round(hi, 2),
        "values": values,
    }
    with open(JSON_PATH, "w") as f:
        json.dump(payload, f, separators=(",", ":"))
    size_kb = os.path.getsize(JSON_PATH) / 1024
    print(f"[save] terrain.json        → {JSON_PATH}  ({size_kb:.1f} KB)")


def save_heightmap_png(grid: np.ndarray) -> None:
    """Export an 8-bit grayscale PNG for the browser canvas layer.

    Uses PIL (via matplotlib's imsave would produce RGBA) to ensure a true
    single-channel grayscale image.  Pixel brightness = normalised height × 255.
    """
    from PIL import Image
    os.makedirs(OUT_DIR, exist_ok=True)
    pixels = (grid * 255).clip(0, 255).astype(np.uint8)
    img = Image.fromarray(pixels, mode="L")
    img.save(HEIGHTMAP_PATH)
    print(f"[save] terrain_heightmap.png → {HEIGHTMAP_PATH}  "
          f"({img.size[0]}×{img.size[1]} px, mode={img.mode})")


def save_preview_png(grid: np.ndarray, source_label: str) -> None:
    """Create a 4-panel matplotlib figure for visual validation.

    Panels:
      (1) Filled contour map — terrain colourmap
      (2) Grayscale imshow   — same as the PNG heightmap
      (3) 3-D surface        — rotated perspective view
      (4) Height histogram   — distribution with stats annotation
    """
    rows, cols = grid.shape

    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(
        f"EcoPilot — Terrain Preview ({source_label})\n"
        f"Mantripukhri, Imphal West, Manipur  |  "
        f"BBox: [{SOUTH}, {WEST}] → [{NORTH}, {EAST}]  |  Grid: {rows}×{cols}",
        fontsize=11, fontweight="bold",
    )

    # ── (1) Filled contour ──────────────────────────────────────────────────
    ax1 = fig.add_subplot(2, 2, 1)
    cf = ax1.contourf(grid, levels=20, cmap="terrain")
    fig.colorbar(cf, ax=ax1, label="Normalised height")
    ax1.set_title("(1) Top-down contour map")
    ax1.set_xlabel("Column (W → E)")
    ax1.set_ylabel("Row (N → S)")
    ax1.set_aspect("equal")

    # ── (2) Grayscale imshow ────────────────────────────────────────────────
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.imshow(grid, cmap="gray", origin="upper", vmin=0, vmax=1)
    ax2.set_title("(2) Grayscale heightmap")
    ax2.axis("off")

    # ── (3) 3-D surface view ───────────────────────────────────────────────
    ax3 = fig.add_subplot(2, 2, 3, projection="3d")
    xs = np.linspace(WEST, EAST, cols)
    ys = np.linspace(NORTH, SOUTH, rows)
    X, Y = np.meshgrid(xs, ys)
    ax3.plot_surface(X, Y, grid, cmap="terrain", linewidth=0, antialiased=True)
    ax3.set_xlabel("Longitude")
    ax3.set_ylabel("Latitude")
    ax3.set_zlabel("Height")
    ax3.set_title("(3) 3-D surface")

    # ── (4) Height histogram ───────────────────────────────────────────────
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.hist(grid.ravel(), bins=30, color="steelblue", edgecolor="white")
    ax4.set_xlabel("Normalised height")
    ax4.set_ylabel("Cell count")
    ax4.set_title("(4) Height distribution")
    stats_text = (
        f"min={grid.min():.4f}  max={grid.max():.4f}\n"
        f"mean={grid.mean():.4f}  std={grid.std():.4f}"
    )
    ax4.text(0.97, 0.95, stats_text, transform=ax4.transAxes,
             ha="right", va="top", fontsize=8,
             bbox=dict(boxstyle="round", fc="white", alpha=0.7))

    plt.tight_layout()
    plt.savefig(PREVIEW_PATH, dpi=150)
    plt.close(fig)
    print(f"[save] terrain_preview.png   → {PREVIEW_PATH}")


# ══════════════════════════════════════════════════════════════════════════════
# 5. VALIDATION
# ══════════════════════════════════════════════════════════════════════════════

def validate(grid: np.ndarray, grid_size: int) -> bool:
    """Run sanity checks on the normalised grid. Returns True if all pass."""
    print("\n[validate] Sanity checks …")
    ok = True

    def _check(cond: bool, pass_msg: str, fail_msg: str) -> None:
        nonlocal ok
        if cond:
            print(f"  ✓  {pass_msg}")
        else:
            print(f"  ✗  {fail_msg}")
            ok = False

    _check(grid.shape == (grid_size, grid_size),
           f"shape = {grid.shape}",
           f"shape {grid.shape} ≠ expected ({grid_size},{grid_size})")

    _check(grid.min() >= -1e-4,
           f"min = {grid.min():.4f}  (≥ 0)",
           f"min = {grid.min():.4f}  (negative!)")

    _check(grid.max() <= 1 + 1e-4,
           f"max = {grid.max():.4f}  (≤ 1)",
           f"max = {grid.max():.4f}  (exceeds 1!)")

    _check(not np.any(np.isnan(grid)),
           "no NaN values",
           "NaN values present!")

    _check(not np.any(np.isinf(grid)),
           "no Inf values",
           "Inf values present!")

    std = float(grid.std())
    if std < 0.01:
        print(f"  ⚠  std = {std:.4f}  (very low — nearly flat terrain)")
    else:
        print(f"  ✓  std = {std:.4f}")

    return ok


# ══════════════════════════════════════════════════════════════════════════════
# 6. MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="EcoPilot Phase 1 — Terrain Data Pipeline"
    )
    parser.add_argument(
        "--local", metavar="PATH",
        help="Path to a pre-downloaded GeoTIFF (skip network fetches)"
    )
    parser.add_argument(
        "--grid-size", type=int, default=GRID_SIZE,
        help=f"Output grid resolution N×N (default {GRID_SIZE})"
    )
    args = parser.parse_args()
    grid_size = args.grid_size

    print("=" * 64)
    print("EcoPilot — Phase 1: Terrain Data Pipeline")
    print("=" * 64)
    print(f"Target : Mantripukhri, Imphal West, Manipur")
    print(f"BBox   : S={SOUTH}  N={NORTH}  W={WEST}  E={EAST}")
    print(f"Grid   : {grid_size}×{grid_size}")
    print(f"Tools  : rasterio + numpy + matplotlib")
    print()

    raw_m: np.ndarray | None = None
    source_label = ""
    tif_path = GEOTIFF_PATH

    # ── Step 1: Acquire raw elevation data (metres) ───────────────────────

    if args.local:
        # User provided a GeoTIFF on disk
        if not os.path.isfile(args.local):
            print(f"[error] --local file not found: {args.local}")
            sys.exit(1)
        raw_m = process_geotiff(args.local, grid_size)
        source_label = f"Local GeoTIFF ({os.path.basename(args.local)})"

    else:
        # Strategy 1: OpenTopography (needs API key)
        if fetch_srtm_geotiff(tif_path):
            raw_m = process_geotiff(tif_path, grid_size)
            source_label = "OpenTopography SRTM GL1 (30 m GeoTIFF)"

        # Strategy 2: Open-Elevation batch API (no key)
        if raw_m is None:
            elev = fetch_open_elevation(grid_size)
            if elev is not None:
                raw_m = elev
                source_label = "Open-Elevation API (SRTM-30 m, real data)"
                # Save raw + write a GeoTIFF so rasterio path is also exercised
                save_raw_elevations(raw_m, source_label)
                write_geotiff_from_array(raw_m, tif_path)
                print("[rasterio] Re-reading through rasterio to exercise the GeoTIFF path …")
                raw_m = process_geotiff(tif_path, grid_size)

        # Strategy 3: Cached data from a previous successful fetch
        if raw_m is None:
            cached = load_cached_raw_elevations()
            if cached is not None:
                raw_m = cached
                source_label = "Cached SRTM data (from previous fetch)"
                # Write GeoTIFF from cache so rasterio is exercised
                write_geotiff_from_array(raw_m, tif_path)
                print("[rasterio] Re-reading through rasterio to exercise the GeoTIFF path …")
                raw_m = process_geotiff(tif_path, grid_size)

        if raw_m is None:
            print("\n[error] All data sources failed and no cache available.")
            print("        Set OPENTOPO_API_KEY or re-run when network is available.")
            sys.exit(1)

    # ── Step 2: Normalise ─────────────────────────────────────────────────
    norm_grid, lo, hi = normalise(raw_m)
    print(f"\n[normalise] {lo:.1f} m → 0.0 , {hi:.1f} m → 1.0  "
          f"(range {hi - lo:.1f} m)")

    # ── Step 3: Validate ──────────────────────────────────────────────────
    if not validate(norm_grid, grid_size):
        print("[error] Validation failed — aborting.")
        sys.exit(1)

    # ── Step 4: Export all artefacts ──────────────────────────────────────
    print()
    save_npy(norm_grid)
    save_json(norm_grid, source_label, lo, hi)
    save_heightmap_png(norm_grid)
    save_preview_png(norm_grid, source_label)

    # Save raw elevations if not already saved
    if not os.path.isfile(RAW_ELEV_PATH):
        save_raw_elevations(raw_m, source_label)

    # ── Step 5: Summary ──────────────────────────────────────────────────
    print()
    print("=" * 64)
    print("Phase 1 DONE — outputs:")
    all_ok = True
    for label, p in [
        ("terrain.npy           ", NPY_PATH),
        ("terrain.json          ", JSON_PATH),
        ("terrain_heightmap.png ", HEIGHTMAP_PATH),
        ("terrain_preview.png   ", PREVIEW_PATH),
    ]:
        exists = os.path.isfile(p)
        all_ok = all_ok and exists
        tick = "✓" if exists else "✗"
        size = f"({os.path.getsize(p)/1024:.1f} KB)" if exists else "(MISSING)"
        print(f"  {tick}  {label}  {size}")

    print()
    print(f"  Source  : {source_label}")
    print(f"  Grid    : {grid_size}×{grid_size}")
    print(f"  Range   : {lo:.1f} – {hi:.1f} m  ({hi-lo:.1f} m relief)")
    print(f"  Stats   : min={norm_grid.min():.4f}  max={norm_grid.max():.4f}  "
          f"mean={norm_grid.mean():.4f}  std={norm_grid.std():.4f}")
    print()

    if not all_ok:
        print("  ⚠  Some output files are missing. Check errors above.")
        sys.exit(1)

    print("  → Open terrain/terrain_preview.png to visually verify.")
    print("=" * 64)


if __name__ == "__main__":
    main()
