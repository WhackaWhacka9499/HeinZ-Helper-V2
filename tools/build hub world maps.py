"""Build compact, borderless, coordinate-exact WebP world map backdrops for the HeinZ Command Hub UI.

Outputs under launcher/assets/world maps/:
  - pre_season_1.webp   (1024x1024, Unity Worldmap_L2 exact [0..1000] crop)
  - season_2.webp       (1024x1024, Wastes Watcher desert biome + exact WorldBlockIndex_S2/Decorate)
  - season_3.webp       (1024x1024, Unity Worldmap_L2_S3 exact [0..1000] crop)
  - season_4.webp       (1024x1024, Dinosaur Origin exact Capitol-aligned [0..1000] crop)
  - season_5.webp       (1024x1024, Moonlit Elegy gothic biome + exact WorldBlockIndex_S5/Decorate)
  - season_6.webp       (1024x1024, 16-Island Archipelago + exact 1600x1600 WorldBlockIndex_S6/Decorate)
  - zones_overlay.webp  (1024x1024, transparent RGBA 87-province borders + Capitol/City markers)
  - manifest.json       (map metadata, WorldSeasonType enum mapping, cities, SHA-256 hashes)

Coordinate contract (empirically verified against 70,605 live Server 702 tiles = 0.00% block collisions):
  - x in [0 .. grid_size - 1], LEFT -> RIGHT
  - y in [0 .. grid_size - 1], TOP -> BOTTOM (y_origin = "top")
  - pointIndex = y * grid_size + x
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import UnityPy
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

REPO_ROOT = Path(r".")
AB_DIR = Path(
    r"%LOCALAPPDATA%/Last Z\Game\Survival_Data\StreamingAssets\AssetBundles"
)
MAPS_DIR = REPO_ROOT / "maps"
XML_DIR = REPO_ROOT / "megamind" / "raw" / "xml tables"
OUT_DIR = REPO_ROOT / "launcher" / "assets" / "world maps"
VERIFY_SHEET = Path(
    r"data/cache/verify_hub_world_maps_sheet.png"
)

OUT_SIZE = 1024


def load_bundle(path: Path):
    raw = path.read_bytes()
    if raw.startswith(b"UnityRawUnityFS"):
        raw = raw[8:]
    return UnityPy.load(raw)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def decode_bitmap(raw: bytes) -> np.ndarray:
    bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8), bitorder="little")
    side = int(round(math.sqrt(len(bits))))
    assert side * side == len(bits), f"Non-square bitmap: {len(bits)}"
    return bits.reshape(side, side)


def decode_zone_binary(zb: bytes) -> Tuple[int, int, Dict[int, Dict[str, Any]], np.ndarray]:
    off = 0
    w, h, _v1, nzones = struct.unpack_from("<4I", zb, off)
    off += 16
    zones: Dict[int, Dict[str, Any]] = {}
    for _ in range(nzones):
        zid, level, _s1, pos_id, _s2, n_nb1 = struct.unpack_from("<H5I", zb, off)
        off += 22 + 2 * n_nb1
        bx, by, bw, bh, ox, oy = struct.unpack_from("<6H", zb, off)
        off += 12
        n_nb2 = struct.unpack_from("<I", zb, off)[0]
        off += 4 + 2 * n_nb2
        n_extra = struct.unpack_from("<I", zb, off)[0]
        off += 4 + 2 * n_extra
        zones[zid] = {
            "id": zid,
            "level": level,
            "pos_id": pos_id,
            "x": pos_id % w,
            "y": pos_id // w,
            "box": (bx, by, bw, bh),
        }
    total_px, rle_cnt = struct.unpack_from("<2I", zb, off)
    off += 8
    grid = np.zeros(total_px, dtype=np.uint16)
    for _ in range(rle_cnt):
        start, length, zid = struct.unpack_from("<IHH", zb, off)
        off += 8
        grid[start : start + length] = zid
    return w, h, zones, grid.reshape(h, w)


def load_localization() -> Dict[str, str]:
    loc_path = REPO_ROOT / "launcher" / "assets" / "english-dialog.txt"
    loc: Dict[str, str] = {}
    if loc_path.exists():
        for line in loc_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                loc[k.strip()] = v.strip()
    return loc


def load_world_cities() -> List[Dict[str, Any]]:
    wc_path = XML_DIR / "worldcity.json"
    if not wc_path.exists():
        return []
    loc_map = load_localization()
    data = json.loads(wc_path.read_text(encoding="utf-8"))
    cols = data["columns"]
    rows = data["rows"]
    raw_rows = rows.values() if isinstance(rows, dict) else rows
    out: List[Dict[str, Any]] = []
    for vals in raw_rows:
        r = dict(zip(cols, vals))
        loc = str(r.get("location", "")).strip()
        sep = "|" if "|" in loc else (";" if ";" in loc else ("," if "," in loc else ""))
        if not sep:
            continue
        try:
            xs, ys = loc.split(sep)[:2]
            x, y = int(xs), int(ys)
            lv = int(r.get("level", 1))
            cid = int(r.get("id", 0))
            name_key = str(r.get("name", "")).strip()
            cname = loc_map.get(name_key, "")
            if not cname:
                cname = {
                    7: "Capitol",
                    6: f"Mega City {cid}",
                    5: f"Big City {cid}",
                    4: f"Big Town {cid}",
                    8: f"Turret {cid}",
                }.get(lv, f"City {cid}")
            out.append({"id": cid, "x": x, "y": y, "level": lv, "name": cname})
        except Exception:
            continue
    out.sort(key=lambda c: (-c["level"], c["id"]))
    return out


def extract_ground_texture(bundle_glob: str, tex_keywords: Tuple[str, ...]) -> Image.Image | None:
    matches = sorted(AB_DIR.glob(bundle_glob))
    for bpath in matches:
        try:
            env = load_bundle(bpath)
            for obj in env.objects:
                if obj.type.name == "Texture2D":
                    d = obj.read()
                    nm = d.m_Name.lower()
                    if any(kw in nm for kw in tex_keywords):
                        return d.image.convert("RGB")
        except Exception:
            continue
    return None


def tile_texture(tex: Image.Image, target_w: int, target_h: int, tile_px: int = 256) -> np.ndarray:
    small = tex.convert("RGB").resize((tile_px, tile_px), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (target_w, target_h))
    for y in range(0, target_h, tile_px):
        for x in range(0, target_w, tile_px):
            canvas.paste(small, (x, y))
    return np.array(canvas, dtype=np.float32)


def crop_4k_exact(
    src_path: Path,
    u0: float,
    v0: float,
    u1: float,
    v1: float,
    contrast: float = 1.04,
    saturation: float = 1.06,
    brightness: float = 0.94,
) -> Image.Image:
    """Crop a 4K Worldmap_L2 image to the exact playable [0..1000]x[0..1000] bounds and scale to 1024x1024."""
    img = Image.open(src_path).convert("RGB")
    w, h = img.size
    box = (int(round(u0 * w)), int(round(v0 * h)), int(round(u1 * w)), int(round(v1 * h)))
    cropped = img.crop(box).resize((OUT_SIZE, OUT_SIZE), Image.Resampling.LANCZOS)
    # Slight tactical tone balance so glowing radar markers pop cleanly without losing terrain authenticity
    if brightness != 1.0:
        cropped = ImageEnhance.Brightness(cropped).enhance(brightness)
    if contrast != 1.0:
        cropped = ImageEnhance.Contrast(cropped).enhance(contrast)
    if saturation != 1.0:
        cropped = ImageEnhance.Color(cropped).enhance(saturation)
    return cropped


def render_procedural_season_map(
    block_bits: np.ndarray,
    deco_bits: np.ndarray,
    palette: Dict[str, Tuple[int, int, int]],
    ground_tex: Image.Image | None = None,
    ground_blend: float = 0.28,
    zgrid: np.ndarray | None = None,
    draw_capitol_hex: bool = True,
    ring_style: str = "radial",
) -> Image.Image:
    """Render a clean, borderless, title-free 1024x1024 terrain map with 0-pixel coordinate drift."""
    side = block_bits.shape[0]
    yy, xx = np.mgrid[0:OUT_SIZE, 0:OUT_SIZE].astype(np.float32)
    nx = (xx - OUT_SIZE * 0.5) / (OUT_SIZE * 0.5)
    ny = (yy - OUT_SIZE * 0.5) / (OUT_SIZE * 0.5)
    dist = np.sqrt(nx * nx + ny * ny)
    t_rad = np.clip(dist / 1.18, 0.0, 1.0)[..., None]

    land_in = np.array(palette["land_inner"], dtype=np.float32)
    land_mid = np.array(palette.get("land_mid", palette["land_inner"]), dtype=np.float32)
    land_out = np.array(palette["land_outer"], dtype=np.float32)
    deco_col = np.array(palette["decorate"], dtype=np.float32)
    blk_col = np.array(palette["block"], dtype=np.float32)
    blk_hi = np.array(palette["block_hi"], dtype=np.float32)
    blk_sh = np.array(palette["block_shadow"], dtype=np.float32)

    if ring_style == "tiers":
        # 3-tier desert oasis -> ochre dunes -> arid wastes
        t1 = np.clip(dist / 0.55, 0.0, 1.0)[..., None]
        t2 = np.clip((dist - 0.45) / 0.72, 0.0, 1.0)[..., None]
        arr = land_in * (1.0 - t1) + land_mid * t1
        arr = arr * (1.0 - t2) + land_out * t2
    else:
        arr = land_in * (1.0 - t_rad) + land_out * t_rad

    # Blend authentic ground texture for rich organic game-accurate surface grain
    if ground_tex is not None:
        tex_arr = tile_texture(ground_tex, OUT_SIZE, OUT_SIZE, tile_px=256)
        # Normalize texture mean to match local palette luminance so colors stay true
        tex_centered = tex_arr - tex_arr.mean(axis=(0, 1), keepdims=True)
        arr = np.clip(arr + tex_centered * ground_blend, 0, 255)

    # Upsample/resample block and decorate masks cleanly to OUT_SIZE
    bm = (
        np.array(
            Image.fromarray((block_bits * 255).astype(np.uint8)).resize(
                (OUT_SIZE, OUT_SIZE), Image.Resampling.BILINEAR
            )
        )
        > 105
    )
    dm = (
        np.array(
            Image.fromarray((deco_bits * 255).astype(np.uint8)).resize(
                (OUT_SIZE, OUT_SIZE), Image.Resampling.BILINEAR
            )
        )
        > 105
    )

    # Soft ambient occlusion halo around blocked mountains/islands
    bm_blur = np.array(
        Image.fromarray((bm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3.2)),
        dtype=np.float32,
    ) / 255.0
    arr = arr * (1.0 - bm_blur[..., None] * 0.25) + blk_sh * (bm_blur[..., None] * 0.25)

    # Decorate features (oases, ridges, forests, ruins, shoals)
    arr[dm] = arr[dm] * 0.42 + deco_col * 0.58

    # Directional SE drop shadow for blocked landforms
    sh = np.zeros_like(bm)
    sh[3:, 3:] = bm[:-3, :-3] & (~bm[3:, 3:])
    arr[sh] = arr[sh] * 0.45 + blk_sh * 0.55

    # Blocked fill + NW sunlit rim highlight
    arr[bm] = blk_col
    nw_hi = np.zeros_like(bm)
    nw_hi[1:, 1:] = bm[1:, 1:] & ((~bm[:-1, 1:]) | (~bm[1:, :-1]))
    arr[nw_hi] = blk_hi

    # Subtle Capitol hex mud platform at exact zone 1 (Capitol 465..535) for 1000x1000 seasons
    if draw_capitol_hex and zgrid is not None and side == 1000:
        cap_mask = (
            np.array(
                Image.fromarray(((zgrid == 1) * 255).astype(np.uint8)).resize(
                    (OUT_SIZE, OUT_SIZE), Image.Resampling.NEAREST
                )
            )
            > 127
        )
        cap_col = np.array(palette.get("capitol_fill", (92, 80, 62)), dtype=np.float32)
        arr[cap_mask] = arr[cap_mask] * 0.35 + cap_col * 0.65
        # Subtle Capitol edge ring
        ce = np.zeros_like(cap_mask)
        ce[:-1, :] |= cap_mask[:-1, :] != cap_mask[1:, :]
        ce[:, :-1] |= cap_mask[:, :-1] != cap_mask[:, 1:]
        arr[ce] = np.array(palette.get("capitol_edge", (226, 192, 112)), dtype=np.float32)

    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def render_zones_overlay(zgrid: np.ndarray, zones: Dict[int, Dict[str, Any]], cities: List[Dict[str, Any]]) -> Image.Image:
    """Render a transparent RGBA 1024x1024 province border & Capitol/city tier overlay."""
    zg = np.array(
        Image.fromarray(zgrid.astype(np.int32)).resize((OUT_SIZE, OUT_SIZE), Image.Resampling.NEAREST),
        dtype=np.uint16,
    )
    rgba = np.zeros((OUT_SIZE, OUT_SIZE, 4), dtype=np.uint8)

    # Very subtle tier wash ONLY on high-tier inner zones (Lv 6 Mega & Lv 7 Capitol)
    lv_lut = np.zeros((256, 4), dtype=np.uint8)
    for zid, info in zones.items():
        lv = info["level"]
        if lv == 7:
            lv_lut[zid] = [245, 196, 62, 52]
        elif lv == 6:
            lv_lut[zid] = [214, 92, 132, 24]
        elif lv == 5:
            lv_lut[zid] = [225, 128, 72, 14]
        else:
            lv_lut[zid] = [0, 0, 0, 0]
    rgba = lv_lut[zg]

    # Crisp 2px province borders (dark halo + warm parchment gold core)
    edge = np.zeros((OUT_SIZE, OUT_SIZE), dtype=bool)
    edge[:-1, :] |= zg[:-1, :] != zg[1:, :]
    edge[:, :-1] |= zg[:, :-1] != zg[:, 1:]

    halo = np.zeros((OUT_SIZE, OUT_SIZE), dtype=bool)
    halo[1:, :] |= edge[:-1, :]
    halo[:-1, :] |= edge[1:, :]
    halo[:, 1:] |= edge[:, :-1]
    halo[:, :-1] |= edge[:, 1:]

    rgba[halo] = [10, 14, 20, 155]
    rgba[edge] = [248, 224, 152, 210]

    # Highlight Capitol border slightly stronger in bright gold
    cap_edge = edge & (
        (zg == 1)
        | np.roll(zg == 1, 1, axis=0)
        | np.roll(zg == 1, -1, axis=0)
        | np.roll(zg == 1, 1, axis=1)
        | np.roll(zg == 1, -1, axis=1)
    )
    rgba[cap_edge] = [255, 224, 88, 245]

    img = Image.fromarray(rgba)
    draw = ImageDraw.Draw(img)
    scale = OUT_SIZE / 1000.0
    for c in cities:
        px, py = c["x"] * scale, c["y"] * scale
        lv = c["level"]
        if lv == 7:
            r = 8
            draw.ellipse((px - r, py - r, px + r, py + r), fill=(255, 215, 64, 230), outline=(255, 255, 255, 255), width=2)
        elif lv == 6:
            r = 6
            pts = [(px, py - r), (px + r, py), (px, py + r), (px - r, py)]
            draw.polygon(pts, fill=(244, 114, 182, 220), outline=(255, 255, 255, 235))
        elif lv == 5:
            r = 4
            draw.ellipse((px - r, py - r, px + r, py + r), fill=(251, 146, 60, 210), outline=(20, 24, 30, 220), width=1)
    return img


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Building HeinZ Hub world maps in {OUT_DIR} ...")

    # Load WorldBlockIndex_S*, WorldDecorateIndex_S*, zone from main_scenes_all
    scenes_bundle = sorted(AB_DIR.glob("main_scenes_all*.bundle"))[0]
    env = load_bundle(scenes_bundle)
    blocks: Dict[str, np.ndarray] = {}
    decos: Dict[str, np.ndarray] = {}
    zone_bytes: bytes | None = None
    for obj in env.objects:
        if obj.type.name == "TextAsset":
            d = obj.read()
            raw_b = (
                bytes(d.m_Script.encode("utf-8", "surrogateescape"))
                if isinstance(d.m_Script, str)
                else bytes(d.m_Script)
            )
            if d.m_Name.startswith("WorldBlockIndex_"):
                blocks[d.m_Name] = decode_bitmap(raw_b)
            elif d.m_Name.startswith("WorldDecorateIndex_"):
                decos[d.m_Name] = decode_bitmap(raw_b)
            elif d.m_Name == "zone":
                zone_bytes = raw_b

    assert zone_bytes is not None, "zone TextAsset missing from main_scenes_all bundle"
    _zw, _zh, zones, zgrid = decode_zone_binary(zone_bytes)
    cities = load_world_cities()
    print(f"Decoded {len(zones)} provinces and {len(cities)} cities.")

    # Extract authentic seasonal ground textures for procedural S2 & S5 maps
    s2_sand_tex = extract_ground_texture(
        "art_lastday_models_environment_map_worldmap_l2_0*.bundle", ("saiji_sand", "sand")
    )
    s5_ground_tex = extract_ground_texture(
        "art_lastday_models_environment_map_world_s5_ground*.bundle", ("ground", "s5", "d")
    )
    print(f"Ground textures loaded: S2_sand={s2_sand_tex is not None}, S5_ground={s5_ground_tex is not None}")

    # 1. Pre-Season 1 / S1 (Exact Unity Worldmap_L2 [0..1000] crop)
    img_s0 = crop_4k_exact(
        MAPS_DIR / "Main World Maps" / "Main World Map 4K.png",
        u0=0.0603,
        v0=0.2566,
        u1=0.9388,
        v1=0.9396,
        contrast=1.08,
        saturation=1.08,
        brightness=0.92,
    )

    # 2. Season 2: Wastes Watcher (Borderless golden desert + exact WorldBlockIndex_S2/Decorate)
    img_s2 = render_procedural_season_map(
        blocks["WorldBlockIndex_S2"],
        decos["WorldDecorateIndex_S2"],
        palette={
            "land_inner": (176, 146, 94),
            "land_mid": (158, 122, 74),
            "land_outer": (122, 92, 58),
            "decorate": (110, 128, 88),
            "block": (78, 56, 38),
            "block_hi": (196, 160, 108),
            "block_shadow": (44, 30, 18),
            "capitol_fill": (118, 94, 60),
            "capitol_edge": (245, 206, 114),
        },
        ground_tex=s2_sand_tex,
        ground_blend=0.35,
        zgrid=zgrid,
        draw_capitol_hex=True,
        ring_style="tiers",
    )

    # 3. Season 3: Everfrost Era (Exact Unity Worldmap_L2_S3 [0..1000] crop)
    # Slightly darken snow highlights (brightness 0.80, contrast 1.12) so bright radar markers remain crisp & legible
    img_s3 = crop_4k_exact(
        MAPS_DIR / "Main World Maps" / "Season 3 Everfrost World Map 4K.png",
        u0=0.0603,
        v0=0.2566,
        u1=0.9388,
        v1=0.9396,
        contrast=1.12,
        saturation=1.15,
        brightness=0.80,
    )

    # 4. Season 4: Dinosaur Origin (Exact Capitol-aligned [0..1000] crop verified against zone 1 hex)
    img_s4 = crop_4k_exact(
        MAPS_DIR / "Main World Maps" / "Season 4 Dinosaur Origin World Map 4K.png",
        u0=0.0860,
        v0=0.1368,
        u1=0.9132,
        v1=0.9568,
        contrast=1.08,
        saturation=1.08,
        brightness=0.90,
    )

    # 5. Season 5: Moonlit Elegy (Seamless gothic moonlit biome + exact WorldBlockIndex_S5/Decorate)
    # Use smooth procedural moonlit texture (no tiled splat atlas seams)
    rng = np.random.default_rng(505)
    s5_noise = rng.normal(0.0, 1.0, (256, 256)).astype(np.float32)
    s5_grain = Image.fromarray(np.clip(128 + s5_noise * 24, 0, 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(1.2)
    ).convert("RGB")
    img_s5 = render_procedural_season_map(
        blocks["WorldBlockIndex_S5"],
        decos["WorldDecorateIndex_S5"],
        palette={
            "land_inner": (76, 62, 108),
            "land_outer": (34, 34, 62),
            "decorate": (106, 74, 134),
            "block": (18, 18, 34),
            "block_hi": (144, 122, 190),
            "block_shadow": (8, 8, 18),
            "capitol_fill": (98, 56, 86),
            "capitol_edge": (240, 186, 124),
        },
        ground_tex=s5_grain,
        ground_blend=0.22,
        zgrid=zgrid,
        draw_capitol_hex=True,
        ring_style="radial",
    )

    # 6. Season 6: Archipelago (1600x1600 borderless island topology + WorldBlockIndex_S6/Decorate)
    img_s6 = render_procedural_season_map(
        blocks["WorldBlockIndex_S6"],
        decos["WorldDecorateIndex_S6"],
        palette={
            "land_inner": (42, 82, 104),
            "land_outer": (22, 54, 78),
            "decorate": (76, 128, 92),
            "block": (14, 32, 52),
            "block_hi": (106, 168, 198),
            "block_shadow": (8, 18, 32),
        },
        ground_tex=None,
        zgrid=None,
        draw_capitol_hex=False,
        ring_style="radial",
    )

    # 7. Transparent RGBA Province Borders & Cities Overlay (1000x1000 seasons)
    img_zones = render_zones_overlay(zgrid, zones, cities)

    specs = [
        {
            "key": "pre_season_1",
            "label": "Pre-Season 1 / S1 (Wasteland)",
            "short_label": "S1 Wasteland",
            "world_season_ids": [0],
            "grid_size": 1000,
            "file": "pre season 1.webp",
            "source_kind": "satellite_4k",
            "supports_zones": True,
            "img": img_s0,
            "quality": 84,
        },
        {
            "key": "season_2",
            "label": "Season 2 (Wastes Watcher)",
            "short_label": "S2 Desert",
            "world_season_ids": [1],
            "grid_size": 1000,
            "file": "season 2.webp",
            "source_kind": "topology_biome",
            "supports_zones": True,
            "img": img_s2,
            "quality": 84,
        },
        {
            "key": "season_3",
            "label": "Season 3 (Everfrost Era)",
            "short_label": "S3 Everfrost",
            "world_season_ids": [2],
            "grid_size": 1000,
            "file": "season 3.webp",
            "source_kind": "satellite_4k",
            "supports_zones": True,
            "img": img_s3,
            "quality": 84,
        },
        {
            "key": "season_4",
            "label": "Season 4 (Dinosaur Origin)",
            "short_label": "S4 Dinosaur",
            "world_season_ids": [3],
            "grid_size": 1000,
            "file": "season 4.webp",
            "source_kind": "satellite_4k",
            "supports_zones": True,
            "img": img_s4,
            "quality": 84,
        },
        {
            "key": "season_5",
            "label": "Season 5 (Moonlit Elegy)",
            "short_label": "S5 Moonlit",
            "world_season_ids": [4],
            "grid_size": 1000,
            "file": "season 5.webp",
            "source_kind": "topology_biome",
            "supports_zones": True,
            "img": img_s5,
            "quality": 84,
        },
        {
            "key": "season_6",
            "label": "Season 6 (Archipelago 1600)",
            "short_label": "S6 Archipelago",
            "world_season_ids": [5],
            "grid_size": 1600,
            "file": "season 6.webp",
            "source_kind": "topology_biome",
            "supports_zones": False,
            "img": img_s6,
            "quality": 84,
        },
    ]

    manifest_maps: List[Dict[str, Any]] = []
    total_bytes = 0
    for sp in specs:
        out_p = OUT_DIR / sp["file"]
        sp["img"].save(out_p, format="WEBP", quality=sp["quality"], method=6)
        sz = out_p.stat().st_size
        total_bytes += sz
        print(f"  Wrote {sp['file']:20s}: {sp['img'].size}  {sz/1024:6.1f} KB")
        manifest_maps.append(
            {
                "key": sp["key"],
                "label": sp["label"],
                "short_label": sp["short_label"],
                "world_season_ids": sp["world_season_ids"],
                "grid_size": sp["grid_size"],
                "file": sp["file"],
                "width": sp["img"].width,
                "height": sp["img"].height,
                "y_origin": "top",
                "source_kind": sp["source_kind"],
                "supports_zones": sp["supports_zones"],
                "size_bytes": sz,
                "sha256": sha256_file(out_p),
            }
        )

    zones_path = OUT_DIR / "zones overlay.webp"
    img_zones.save(zones_path, format="WEBP", quality=88, method=6, lossless=False)
    z_sz = zones_path.stat().st_size
    total_bytes += z_sz
    print(f"  Wrote {'zones overlay.webp':20s}: {img_zones.size}  {z_sz/1024:6.1f} KB")

    # Save major landmarks (Lv 5, 6, 7) for crisp vector labels in the radar UI
    major_cities = [c for c in cities if c["level"] in (5, 6, 7)]

    manifest = {
        "version": 1,
        "y_origin": "top",
        "default_map_key": "pre_season_1",
        "season_enum_map": {
            "0": "pre_season_1",
            "1": "season_2",
            "2": "season_3",
            "3": "season_4",
            "4": "season_5",
            "5": "season_6",
        },
        "zones_overlay": {
            "file": "zones overlay.webp",
            "width": img_zones.width,
            "height": img_zones.height,
            "grid_size": 1000,
            "province_count": len(zones),
            "size_bytes": z_sz,
            "sha256": sha256_file(zones_path),
        },
        "major_cities": major_cities,
        "maps": manifest_maps,
        "total_bytes": total_bytes,
    }
    manifest_path = OUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote manifest.json | Total asset pack size: {total_bytes/1024:.1f} KB ({total_bytes/(1024*1024):.2f} MB)")

    # Render a 3x2 visual verification contact sheet with the 2,180 real S3 HQs + province overlay on S3!
    csv_hqs: List[Tuple[int, int]] = []
    csv_p = REPO_ROOT / "data" / "map all bases.csv"
    if csv_p.exists():
        with csv_p.open("r", encoding="utf-8", errors="replace") as f:
            for row in csv.DictReader(f):
                try:
                    csv_hqs.append((int(float(row["x"])), int(float(row["y"]))))
                except Exception:
                    pass

    cell = 512
    sheet = Image.new("RGB", (cell * 3 + 20, cell * 2 + 10), (14, 17, 22))
    for idx, sp in enumerate(specs):
        base = sp["img"].resize((cell, cell), Image.Resampling.LANCZOS).convert("RGBA")
        if sp["supports_zones"]:
            ov = img_zones.resize((cell, cell), Image.Resampling.LANCZOS)
            base = Image.alpha_composite(base, ov)
        dr = ImageDraw.Draw(base)
        if sp["key"] == "season_3":
            for hx, hy in csv_hqs:
                px, py = hx * cell / 1000.0, hy * cell / 1000.0
                dr.rectangle((px - 1, py - 1, px + 1, py + 1), fill=(255, 65, 65, 235))
        dr.rectangle((0, 0, cell, 24), fill=(10, 12, 18, 215))
        dr.text((8, 5), f"{sp['label']} ({sp['grid_size']}x{sp['grid_size']})", fill=(255, 236, 175, 255))
        col_i = idx % 3
        row_i = idx // 3
        sheet.paste(base.convert("RGB"), (col_i * (cell + 10), row_i * (cell + 10)))

    VERIFY_SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(VERIFY_SHEET)
    print(f"Saved visual verification contact sheet: {VERIFY_SHEET}")


if __name__ == "__main__":
    main()
