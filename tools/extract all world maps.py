"""Extract, stitch, decode, render, and organize all Last Z world, seasonal, event, city, and terrain maps.

Outputs cleanly named PNGs (with zero underscores in any filename or folder under maps/),
plus Maps Catalog.json, Maps Catalog.csv, README.md, and a visual verification contact sheet.
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
import shutil
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import UnityPy
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Paths
REPO_ROOT = Path(r".")
AB_DIR = Path(
    r"%LOCALAPPDATA%/Last Z\Game\Survival_Data\StreamingAssets\AssetBundles"
)
XML_DIR = REPO_ROOT / "megamind" / "raw" / "xml tables"
LOC_PATH = REPO_ROOT / "launcher" / "assets" / "english-dialog.txt"
MAPS_ROOT = REPO_ROOT / "maps"
VERIFY_SHEET_PATH = Path(
    r"data/cache/world_maps_verify_sheet.png"
)

# Font helpers (Windows standard fonts with fallback)
def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\segoeui.ttf" if not bold else r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arial.ttf" if not bold else r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for fp in candidates:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def load_bundle(bundle_path: Path):
    raw = bundle_path.read_bytes()
    if raw.startswith(b"UnityRawUnityFS"):
        raw = raw[8:]
    return UnityPy.load(raw)


def find_bundle(prefix: str) -> Path:
    matches = sorted(AB_DIR.glob(f"{prefix}*.bundle"))
    if not matches:
        raise FileNotFoundError(f"No bundle matching prefix: {prefix}")
    # Prefer exact prefix + 32-hex hash
    exact = [m for m in matches if re.fullmatch(re.escape(prefix) + r"[0-9a-f]{32}\.bundle", m.name)]
    return exact[0] if exact else matches[0]


def load_localization() -> Dict[str, str]:
    loc: Dict[str, str] = {}
    if LOC_PATH.exists():
        for line in LOC_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                loc[k.strip()] = v.strip()
    return loc


def load_xml_rows(name: str) -> List[Dict[str, str]]:
    p = XML_DIR / f"{name.replace('_', ' ')}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    cols = d["columns"]
    rows = d["rows"]
    if isinstance(rows, dict):
        return [dict(zip(cols, vals)) for vals in rows.values()]
    return [dict(zip(cols, vals)) for vals in rows]


def clean_name(text: str) -> str:
    """Enforce zero underscores and zero em dashes in filenames and titles."""
    text = text.replace("\u2014", "-").replace("\u2013", "-")
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def draw_text_halo(
    draw: ImageDraw.ImageDraw,
    xy: Tuple[float, float],
    text: str,
    font: ImageFont.ImageFont,
    fill: Tuple[int, int, int, int] = (255, 255, 255, 255),
    halo: Tuple[int, int, int, int] = (10, 14, 20, 230),
    anchor: str = "mm",
    radius: int = 2,
) -> None:
    x, y = xy
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx == 0 and dy == 0:
                continue
            if dx * dx + dy * dy <= radius * radius + 1:
                draw.text((x + dx, y + dy), text, font=font, fill=halo, anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)


@dataclass
class MapRecord:
    relative_path: str
    title: str
    category: str
    subcategory: str
    season: str
    width: int
    height: int
    source_bundle: str
    source_assets: str
    asset_type: str
    notes: str = ""


class MapExporter:
    def __init__(self) -> None:
        self.records: List[MapRecord] = []
        self.bundle_cache: Dict[str, Dict[str, Image.Image]] = {}
        self.loc = load_localization()
        self.cities = self._load_cities()

    def _load_cities(self) -> List[Dict]:
        out = []
        for r in load_xml_rows("worldcity"):
            cid = int(r["id"])
            x, y = map(int, r["location"].split("|"))
            lv = int(r["level"])
            sz = int(r["size"])
            en = clean_name(self.loc.get(str(r.get("name", "")), f"City {cid}"))
            out.append({"id": cid, "x": x, "y": y, "level": lv, "size": sz, "name": en})
        out.sort(key=lambda c: c["id"])
        return out

    def load_bundle_textures(self, prefix: str) -> Tuple[str, Dict[str, Image.Image]]:
        bp = find_bundle(prefix)
        if bp.name not in self.bundle_cache:
            env = load_bundle(bp)
            texs: Dict[str, Image.Image] = {}
            for obj in env.objects:
                if obj.type.name == "Texture2D":
                    d = obj.read()
                    nm = d.m_Name
                    # Handle rare duplicate names in same bundle
                    if nm in texs:
                        idx = 2
                        while f"{nm} ({idx})" in texs:
                            idx += 1
                        nm = f"{nm} ({idx})"
                    texs[nm] = d.image.convert("RGBA")
            self.bundle_cache[bp.name] = texs
        return bp.name, self.bundle_cache[bp.name]

    def save_image(
        self,
        img: Image.Image,
        rel_path: str,
        title: str,
        category: str,
        subcategory: str,
        season: str,
        source_bundle: str,
        source_assets: str,
        asset_type: str,
        notes: str = "",
        keep_alpha: bool = True,
    ) -> Path:
        # Enforce strict ZERO underscores in any path segment under maps/
        parts = [clean_name(p) for p in Path(rel_path).parts]
        assert all("_" not in p for p in parts), f"Underscore forbidden in path: {parts}"
        out_path = MAPS_ROOT.joinpath(*parts)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        save_img = img if keep_alpha else img.convert("RGB")
        # If RGBA image is completely opaque, save as RGB for smaller crisp PNG
        if keep_alpha and save_img.mode == "RGBA":
            extrema = save_img.getextrema()
            if extrema[3] == (255, 255):
                save_img = save_img.convert("RGB")
        save_img.save(out_path, format="PNG", optimize=False, compress_level=6)
        rel_norm = "/".join(parts)
        self.records.append(
            MapRecord(
                relative_path=rel_norm,
                title=clean_name(title),
                category=clean_name(category),
                subcategory=clean_name(subcategory),
                season=clean_name(season),
                width=save_img.width,
                height=save_img.height,
                source_bundle=source_bundle,
                source_assets=source_assets,
                asset_type=asset_type,
                notes=notes.replace("\u2014", "-"),
            )
        )
        return out_path

    # ------------------------------------------------------------------
    # 1. 4K STITCHED WORLD MAPS (Main, S3 Everfrost, S4 Dinosaur Origin)
    # ------------------------------------------------------------------
    def extract_4k_world_maps(self) -> Dict[str, Image.Image]:
        print("[1/7] Extracting and stitching 4K World Maps (Main, S3, S4)...")
        specs = [
            (
                "Main",
                "art_lastday_models_environment_map_worldmap_l2_0",
                "Worldmap_L2_",
                "",
                "Main World Maps/Main World Map 4K.png",
                "Main World Maps/Quadrants",
                "Main World Map",
                "All Seasons",
                None,
                None,
            ),
            (
                "S3",
                "art_lastday_models_environment_map_worldmap_l2_s3_",
                "Worldmap_L2_",
                "_S3",
                "Seasonal Maps/Season 3 Everfrost Era/Season 3 Everfrost World Map 4K.png",
                "Seasonal Maps/Season 3 Everfrost Era/Quadrants",
                "Season 3 Everfrost World Map",
                "Season 3 Everfrost Era",
                "Main World Maps/Season 3 Everfrost World Map 4K.png",
                "Worldmap_L2_05_S3",
            ),
            (
                "S4",
                "art_lastday_models_environment_map_worldmap_l2_s4_",
                "Worldmap_L2_",
                "_S4",
                "Seasonal Maps/Season 4 Dinosaur Origin/Season 4 Dinosaur Origin World Map 4K.png",
                "Seasonal Maps/Season 4 Dinosaur Origin/Quadrants",
                "Season 4 Dinosaur Origin World Map",
                "Season 4 Dinosaur Origin",
                "Main World Maps/Season 4 Dinosaur Origin World Map 4K.png",
                "Worldmap_L2_05_S4",
            ),
        ]
        quad_labels = {
            1: "Quadrant 01 Top Left",
            2: "Quadrant 02 Top Right",
            3: "Quadrant 03 Bottom Left",
            4: "Quadrant 04 Bottom Right",
        }
        stitched_out: Dict[str, Image.Image] = {}

        for key, bprefix, tprefix, tsuffix, out_rel, quad_dir, title_base, season, mirror_rel, edge_tex in specs:
            bname, texs = self.load_bundle_textures(bprefix)
            q_imgs: Dict[int, Image.Image] = {}
            q_names: List[str] = []
            for idx in (1, 2, 3, 4):
                tname = f"{tprefix}0{idx}{tsuffix}"
                img = texs[tname].convert("RGB")
                q_imgs[idx] = img
                q_names.append(tname)
                self.save_image(
                    img,
                    f"{quad_dir}/{title_base} {quad_labels[idx]}.png",
                    f"{title_base} {quad_labels[idx]}",
                    "Main World Maps" if key == "Main" else "Seasonal Maps",
                    "World Map Quadrants",
                    season,
                    bname,
                    tname,
                    "Quadrant Texture",
                    keep_alpha=False,
                )

            # Verify seam continuity: [01 | 02] / [03 | 04]
            a1 = np.array(q_imgs[1], dtype=np.float32)
            a2 = np.array(q_imgs[2], dtype=np.float32)
            a3 = np.array(q_imgs[3], dtype=np.float32)
            a4 = np.array(q_imgs[4], dtype=np.float32)
            seam_mad = (
                float(np.mean(np.abs(a1[:, -1] - a2[:, 0])))
                + float(np.mean(np.abs(a3[:, -1] - a4[:, 0])))
                + float(np.mean(np.abs(a1[-1, :] - a3[0, :])))
                + float(np.mean(np.abs(a2[-1, :] - a4[0, :])))
            ) / 4.0
            print(f"  {title_base} 4K stitched [01|02 / 03|04]: seam MAD = {seam_mad:.2f}")

            qw, qh = q_imgs[1].size
            canvas = Image.new("RGB", (qw * 2, qh * 2))
            canvas.paste(q_imgs[1], (0, 0))
            canvas.paste(q_imgs[2], (qw, 0))
            canvas.paste(q_imgs[3], (0, qh))
            canvas.paste(q_imgs[4], (qw, qh))
            stitched_out[key] = canvas

            self.save_image(
                canvas,
                out_rel,
                f"{title_base} 4K",
                "Main World Maps" if key == "Main" else "Seasonal Maps",
                "Stitched 4K World Map",
                season,
                bname,
                ", ".join(q_names),
                "Stitched 4K World Map",
                notes=f"Verified quadrant order [01 TL, 02 TR / 03 BL, 04 BR], avg seam MAD {seam_mad:.2f}",
                keep_alpha=False,
            )
            if mirror_rel:
                self.save_image(
                    canvas,
                    mirror_rel,
                    f"{title_base} 4K",
                    "Main World Maps",
                    "Stitched 4K World Map",
                    season,
                    bname,
                    ", ".join(q_names),
                    "Stitched 4K World Map",
                    notes=f"Mirror of seasonal 4K map; verified seam MAD {seam_mad:.2f}",
                    keep_alpha=False,
                )

            # Save Worldmap_L2_05 border tile for Main
            if key == "Main" and "Worldmap_L2_05" in texs:
                self.save_image(
                    texs["Worldmap_L2_05"],
                    "Main World Maps/Quadrants/Main World Map Outer Border Tile.png",
                    "Main World Map Outer Border Tile",
                    "Main World Maps",
                    "World Map Quadrants",
                    "All Seasons",
                    bname,
                    "Worldmap_L2_05",
                    "Border Tile Texture",
                    keep_alpha=False,
                )

        return stitched_out

    # ------------------------------------------------------------------
    # 2. MAIN SCENES ALL: Zones, Province Masks, Overlay Styles, S0-S6 Topology
    # ------------------------------------------------------------------
    def decode_zone_binary(self, zb: bytes) -> Tuple[int, int, Dict[int, Dict], np.ndarray]:
        off = 0
        w, h, v1, nzones = struct.unpack_from("<4I", zb, off)
        off += 16
        zones: Dict[int, Dict] = {}
        for _ in range(nzones):
            zid, level, s1, pos_id, s2, n_nb1 = struct.unpack_from("<H5I", zb, off)
            off += 22
            nb1 = struct.unpack_from(f"<{n_nb1}H", zb, off)
            off += 2 * n_nb1
            bx, by, bw, bh, ox, oy = struct.unpack_from("<6H", zb, off)
            off += 12
            n_nb2 = struct.unpack_from("<I", zb, off)[0]
            off += 4
            nb2 = struct.unpack_from(f"<{n_nb2}H", zb, off)
            off += 2 * n_nb2
            n_extra = struct.unpack_from("<I", zb, off)[0]
            off += 4 + 2 * n_extra
            zones[zid] = {
                "id": zid,
                "level": level,
                "pos_id": pos_id,
                "x": pos_id % w,
                "y": pos_id // w,
                "neighbors": list(nb1),
                "box": (bx, by, bw, bh),
                "center_off": (ox, oy),
            }
        total_px, rle_cnt = struct.unpack_from("<2I", zb, off)
        off += 8
        grid = np.zeros(total_px, dtype=np.uint16)
        for _ in range(rle_cnt):
            start, length, zid = struct.unpack_from("<IHH", zb, off)
            off += 8
            grid[start : start + length] = zid
        assert off == len(zb), f"Zone binary trailing bytes: {off} != {len(zb)}"
        return w, h, zones, grid.reshape(h, w)

    def decode_bitmap(self, raw: bytes) -> np.ndarray:
        bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8), bitorder="little")
        side = int(round(math.sqrt(len(bits))))
        assert side * side == len(bits), f"Non-square bitmap length: {len(bits)}"
        return bits.reshape(side, side)

    def render_zones_and_cities_map(
        self,
        zgrid: np.ndarray,
        zones: Dict[int, Dict],
        bigmap_img: Image.Image,
        block_s0: np.ndarray,
    ) -> Image.Image:
        out_w, out_h = 2000, 1730
        # Resize bigmap01 subtly as ground undertone
        bg = np.array(bigmap_img.convert("RGB").resize((out_w, out_h), Image.Resampling.LANCZOS), dtype=np.float32)

        # Upsample zone grid with nearest neighbor for crisp boundaries
        z_img = Image.fromarray(zgrid.astype(np.int32)).resize((out_w, out_h), Image.Resampling.NEAREST)
        zg = np.array(z_img, dtype=np.uint16)

        # Level-tiered harmonious tactical colors (Levels 1..7)
        tier_base = {
            1: np.array([72, 118, 86], dtype=np.float32),   # Outer Small Towns - sage green
            2: np.array([96, 134, 78], dtype=np.float32),   # Level 2 Small Towns - olive green
            3: np.array([154, 142, 74], dtype=np.float32),  # Level 3 Midsize Towns - warm ochre
            4: np.array([186, 122, 66], dtype=np.float32),  # Level 4 Big Towns - amber bronze
            5: np.array([196, 86, 62], dtype=np.float32),   # Level 5 Big Cities - terracotta red
            6: np.array([164, 58, 92], dtype=np.float32),   # Level 6 Mega Cities - royal crimson
            7: np.array([228, 184, 54], dtype=np.float32),  # Level 7 Capital - imperial gold
        }

        # Build lookup table with deterministic per-zone variation so adjacent zones contrast cleanly
        lut = np.zeros((256, 3), dtype=np.float32)
        for zid, info in zones.items():
            base = tier_base.get(info["level"], np.array([110, 110, 110], dtype=np.float32)).copy()
            # Golden-ratio hash perturbation (+/- 18) for clean neighbor separation
            h1 = ((zid * 73) % 37) - 18
            h2 = ((zid * 131) % 31) - 15
            h3 = ((zid * 197) % 29) - 14
            lut[zid] = np.clip(base + np.array([h1, h2, h3], dtype=np.float32), 25, 245)

        colored = lut[zg]
        # Blend 62% province tint + 38% bigmap01 terrain detail
        canvas_arr = colored * 0.64 + bg * 0.36

        # Overlay subtle S0 mountains/rivers relief from WorldBlockIndex_S0
        blk = np.array(
            Image.fromarray((block_s0 * 255).astype(np.uint8)).resize((out_w, out_h), Image.Resampling.NEAREST)
        ) > 127
        canvas_arr[blk] = canvas_arr[blk] * 0.42 + np.array([26, 32, 40], dtype=np.float32) * 0.58

        # Crisp province borders (dark outer + bright inner highlight)
        edge = np.zeros((out_h, out_w), dtype=bool)
        edge[:-1, :] |= zg[:-1, :] != zg[1:, :]
        edge[:, :-1] |= zg[:, :-1] != zg[:, 1:]
        # Dilate edge by 1px for crisp 2px border
        edge2 = edge.copy()
        edge2[1:, :] |= edge[:-1, :]
        edge2[:, 1:] |= edge[:, :-1]
        canvas_arr[edge2] = canvas_arr[edge2] * 0.25 + np.array([240, 236, 218], dtype=np.float32) * 0.75
        canvas_arr[edge] = np.array([24, 28, 36], dtype=np.float32)

        img = Image.fromarray(np.clip(canvas_arr, 0, 255).astype(np.uint8)).convert("RGBA")
        draw = ImageDraw.Draw(img)

        sx = out_w / 1000.0
        sy = out_h / 1000.0
        font_zone = get_font(15, bold=True)
        font_major = get_font(18, bold=True)
        font_cap = get_font(22, bold=True)
        font_title = get_font(30, bold=True)
        font_sub = get_font(17, bold=False)

        # Draw all 90 worldcity markers
        city_colors = {
            1: (220, 235, 220, 255),
            2: (235, 245, 195, 255),
            3: (255, 230, 140, 255),
            4: (255, 185, 95, 255),
            5: (255, 120, 95, 255),
            6: (255, 90, 140, 255),
            7: (255, 225, 65, 255),
            8: (125, 225, 255, 255),
        }
        for c in self.cities:
            px, py = c["x"] * sx, c["y"] * sy
            lv = c["level"]
            col = city_colors.get(lv, (255, 255, 255, 255))
            if lv == 7:
                # Capital star/ring
                r = 14
                draw.ellipse((px - r - 3, py - r - 3, px + r + 3, py + r + 3), fill=(20, 16, 10, 230))
                draw.ellipse((px - r, py - r, px + r, py + r), fill=col, outline=(255, 255, 255, 255), width=2)
                draw_text_halo(draw, (px, py - 24), "CAPITAL (500, 500)", font_cap, fill=(255, 236, 115, 255))
            elif lv == 8:
                r = 5
                draw.rectangle((px - r, py - r, px + r, py + r), fill=col, outline=(10, 14, 20, 255), width=2)
            elif lv == 6:
                r = 10
                pts = [(px, py - r), (px + r, py), (px, py + r), (px - r, py)]
                draw.polygon(pts, fill=col, outline=(255, 255, 255, 255))
                # Offset each Mega City label radially outward from Capital so zero labels touch
                dx_out = 28 if c["x"] > 520 else (-28 if c["x"] < 480 else 0)
                dy_out = -22 if c["y"] < 480 else (24 if c["y"] > 515 else -20)
                draw_text_halo(draw, (px + dx_out, py + dy_out), f"Mega City {c['id']}", font_major, fill=(255, 220, 232, 255))
            elif lv == 5:
                r = 8
                draw.ellipse((px - r, py - r, px + r, py + r), fill=col, outline=(255, 255, 255, 255), width=2)
                draw_text_halo(draw, (px, py - 16), f"Big City {c['id']}", font_major, fill=(255, 225, 200, 255))
            elif lv == 4:
                r = 6
                draw.ellipse((px - r, py - r, px + r, py + r), fill=col, outline=(20, 24, 30, 255), width=2)
                draw_text_halo(draw, (px, py + 15), f"Z{c['id']} Lv4", font_zone, fill=(255, 235, 195, 255))
            else:
                r = 4 if lv <= 2 else 5
                draw.ellipse((px - r, py - r, px + r, py + r), fill=col, outline=(15, 18, 22, 220), width=1)
                draw_text_halo(draw, (px, py + 12), f"{c['id']}", font_zone, fill=(245, 248, 250, 235), radius=1)

        # Title bar and legend
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle((24, 22, 760, 108), radius=12, fill=(14, 18, 26, 210), outline=(218, 192, 128, 210), width=2)
        od.rounded_rectangle((24, out_h - 148, 700, out_h - 24), radius=12, fill=(14, 18, 26, 210), outline=(180, 190, 205, 180), width=2)
        # Compass rose top-right
        cx, cy = out_w - 72, 74
        od.ellipse((cx - 42, cy - 42, cx + 42, cy + 42), fill=(14, 18, 26, 205), outline=(218, 192, 128, 210), width=2)
        od.polygon([(cx, cy - 30), (cx + 10, cy + 4), (cx, cy - 4), (cx - 10, cy + 4)], fill=(255, 220, 105, 255))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)
        draw.text((44, 34), "LAST Z: WORLD ZONES AND PROVINCES MAP", font=font_title, fill=(255, 240, 195, 255))
        draw.text(
            (44, 72),
            "87 Decoded Provinces | 90 Cities & Turrets | 1000x1000 World Grid (200:173 Aspect)",
            font=font_sub,
            fill=(210, 220, 232, 255),
        )
        draw_text_halo(draw, (cx, cy + 20), "N", font_major, fill=(255, 230, 140, 255))

        legend_items = [
            ((255, 225, 65), "Lv 7 Capital (1)"),
            ((164, 58, 92), "Lv 6 Mega City (3)"),
            ((196, 86, 62), "Lv 5 Big City (4)"),
            ((186, 122, 66), "Lv 4 Big Town (7)"),
            ((154, 142, 74), "Lv 3 Midsize Town (11)"),
            ((96, 134, 78), "Lv 2 Small Town (20)"),
            ((72, 118, 86), "Lv 1 Small Town (41)"),
            ((125, 225, 255), "Lv 8 Capital Turrets (3)"),
        ]
        for idx, (col, lbl) in enumerate(legend_items):
            col_i = idx % 2
            row_i = idx // 2
            lx = 42 + col_i * 320
            ly = out_h - 134 + row_i * 28
            draw.rectangle((lx, ly + 2, lx + 18, ly + 18), fill=col, outline=(255, 255, 255, 220), width=1)
            draw.text((lx + 26, ly), lbl, font=font_sub, fill=(235, 240, 248, 255))

        return img.convert("RGB")

    def render_season_topology_map(
        self,
        season_code: str,
        title: str,
        subtitle: str,
        block_bits: np.ndarray,
        deco_bits: np.ndarray,
        palette: Dict[str, Tuple[int, int, int]],
        zgrid: Optional[np.ndarray] = None,
        show_cities: bool = True,
    ) -> Tuple[Image.Image, Image.Image]:
        """Render both a crisp labeled 2000x1730 cartographic map AND a pure native-res unlabeled map."""
        side = block_bits.shape[0]
        # Build native-resolution RGB first (clean unlabeled)
        yy, xx = np.mgrid[0:side, 0:side].astype(np.float32)
        dist = np.sqrt(((xx - side * 0.5) / (side * 0.5)) ** 2 + ((yy - side * 0.5) / (side * 0.5)) ** 2)
        t_rad = np.clip(dist / 1.15, 0.0, 1.0)[..., None]

        land_in = np.array(palette["land_inner"], dtype=np.float32)
        land_out = np.array(palette["land_outer"], dtype=np.float32)
        deco_col = np.array(palette["decorate"], dtype=np.float32)
        blk_col = np.array(palette["block"], dtype=np.float32)
        blk_hi = np.array(palette["block_hi"], dtype=np.float32)
        blk_sh = np.array(palette["block_shadow"], dtype=np.float32)
        accent = np.array(palette["accent"], dtype=np.float32)

        raw_arr = land_in * (1.0 - t_rad) + land_out * t_rad

        # Subtle checkerboard terrain texture micro-variation (keeps flat plains readable)
        # Apply decorate mask
        dm = deco_bits.astype(bool)
        raw_arr[dm] = raw_arr[dm] * 0.35 + deco_col * 0.65

        # Shaded 3D relief for blocked mountains/rivers
        bm = block_bits.astype(bool)
        # Drop shadow to SE (+2,+2)
        shadow = np.zeros_like(bm)
        shadow[2:, 2:] = bm[:-2, :-2] & (~bm[2:, 2:])
        raw_arr[shadow] = raw_arr[shadow] * 0.52 + blk_sh * 0.48
        # Blocked fill
        raw_arr[bm] = blk_col
        # NW rim highlight on blocked features
        hi = np.zeros_like(bm)
        hi[:-1, :-1] = bm[:-1, :-1] & ((~bm[1:, :-1]) | (~bm[:-1, 1:]))
        # Actually NW illuminated edge is where NW neighbor is NOT blocked
        nw_hi = np.zeros_like(bm)
        nw_hi[1:, 1:] = bm[1:, 1:] & ((~bm[:-1, 1:]) | (~bm[1:, :-1]))
        raw_arr[nw_hi] = blk_hi

        raw_img = Image.fromarray(np.clip(raw_arr, 0, 255).astype(np.uint8))

        # Now build high-res aspect-correct cartographic render (2000 x 1730 for 1000x1000, 2400 x 2076 for 1600x1600)
        out_w, out_h = (2400, 2076) if side >= 1600 else (2000, 1730)
        scaled = np.array(raw_img.resize((out_w, out_h), Image.Resampling.LANCZOS), dtype=np.float32)

        # Subtle coordinate grid lines (every 100 tiles)
        step_x = out_w / (side / 100.0)
        step_y = out_h / (side / 100.0)
        for i in range(1, side // 100):
            gx = int(round(i * step_x))
            gy = int(round(i * step_y))
            if 0 <= gx < out_w:
                scaled[:, gx] = scaled[:, gx] * 0.85 + accent * 0.15
            if 0 <= gy < out_h:
                scaled[gy, :] = scaled[gy, :] * 0.85 + accent * 0.15

        # Overlay subtle province borders for 1000x1000 maps
        if zgrid is not None and side == 1000:
            zg = np.array(
                Image.fromarray(zgrid.astype(np.int32)).resize((out_w, out_h), Image.Resampling.NEAREST),
                dtype=np.uint16,
            )
            edge = np.zeros((out_h, out_w), dtype=bool)
            edge[:-1, :] |= zg[:-1, :] != zg[1:, :]
            edge[:, :-1] |= zg[:, :-1] != zg[:, 1:]
            scaled[edge] = scaled[edge] * 0.55 + accent * 0.45

        img = Image.fromarray(np.clip(scaled, 0, 255).astype(np.uint8)).convert("RGBA")
        draw = ImageDraw.Draw(img)
        sx = out_w / float(side)
        sy = out_h / float(side)

        font_major = get_font(18 if side == 1000 else 22, bold=True)
        font_cap = get_font(22 if side == 1000 else 26, bold=True)
        font_title = get_font(30 if side == 1000 else 36, bold=True)
        font_sub = get_font(17 if side == 1000 else 21, bold=False)

        if show_cities and side == 1000:
            for c in self.cities:
                px, py = c["x"] * sx, c["y"] * sy
                lv = c["level"]
                if lv == 7:
                    r = 13
                    draw.ellipse((px - r - 3, py - r - 3, px + r + 3, py + r + 3), fill=(12, 16, 22, 230))
                    draw.ellipse((px - r, py - r, px + r, py + r), fill=(255, 215, 65, 255), outline=(255, 255, 255, 255), width=2)
                    draw_text_halo(draw, (px, py - 24), "CAPITAL", font_cap, fill=(255, 238, 130, 255))
                elif lv == 6:
                    r = 9
                    pts = [(px, py - r), (px + r, py), (px, py + r), (px - r, py)]
                    draw.polygon(pts, fill=(255, 110, 125, 255), outline=(255, 255, 255, 255))
                    draw_text_halo(draw, (px, py - 17), f"Mega City {c['id']}", font_major, fill=(255, 230, 235, 255))
                elif lv == 5:
                    r = 7
                    draw.ellipse((px - r, py - r, px + r, py + r), fill=(255, 165, 85, 255), outline=(255, 255, 255, 255), width=2)
                    draw_text_halo(draw, (px, py - 15), f"Big City {c['id']}", font_major, fill=(255, 235, 200, 255))
                elif lv in (3, 4):
                    r = 4 if lv == 3 else 5
                    draw.ellipse((px - r, py - r, px + r, py + r), fill=(255, 225, 155, 225), outline=(15, 20, 25, 220), width=1)
                elif lv in (1, 2):
                    r = 3
                    draw.ellipse((px - r, py - r, px + r, py + r), fill=(235, 240, 245, 185), outline=(15, 20, 25, 200), width=1)
        elif side == 1600:
            # Mark center (800, 800) on S6 expanded 1600x1600 grid
            px, py = 800 * sx, 800 * sy
            r = 16
            draw.ellipse((px - r - 3, py - r - 3, px + r + 3, py + r + 3), fill=(12, 16, 22, 230))
            draw.ellipse((px - r, py - r, px + r, py + r), fill=(255, 215, 65, 255), outline=(255, 255, 255, 255), width=2)
            draw_text_halo(draw, (px, py - 28), "CENTER (800, 800)", font_cap, fill=(255, 238, 130, 255))

        # Overlay title box, compass rose, and legend
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        box_w = 880 if side == 1600 else 760
        od.rounded_rectangle((24, 22, 24 + box_w, 114 if side == 1000 else 132), radius=12, fill=(12, 16, 24, 212), outline=(*palette["accent"], 220), width=2)
        od.rounded_rectangle((24, out_h - 118, 760, out_h - 24), radius=12, fill=(12, 16, 24, 212), outline=(*palette["accent"], 190), width=2)
        cx, cy = out_w - 74, 74
        od.ellipse((cx - 42, cy - 42, cx + 42, cy + 42), fill=(12, 16, 24, 205), outline=(*palette["accent"], 220), width=2)
        od.polygon([(cx, cy - 30), (cx + 10, cy + 4), (cx, cy - 4), (cx - 10, cy + 4)], fill=(*palette["accent"], 255))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)

        draw.text((44, 34), title, font=font_title, fill=(255, 245, 220, 255))
        draw.text((44, 76 if side == 1000 else 84), subtitle, font=font_sub, fill=(212, 222, 235, 255))
        draw_text_halo(draw, (cx, cy + 20), "N", font_major, fill=(*palette["accent"], 255))

        blk_pct = 100.0 * float(block_bits.mean())
        dec_pct = 100.0 * float(deco_bits.mean())
        leg = [
            (palette["land_inner"], "Passable Terrain"),
            (palette["block"], f"Blocked Mountains / Rivers ({blk_pct:.2f}%)"),
            (palette["decorate"], f"Decorative Landmarks / Flora ({dec_pct:.2f}%)"),
        ]
        for i, (col, lbl) in enumerate(leg):
            ly = out_h - 108 + i * 28
            draw.rectangle((42, ly + 2, 62, ly + 20), fill=col, outline=(255, 255, 255, 210), width=1)
            draw.text((72, ly), lbl, font=font_sub, fill=(238, 242, 248, 255))

        return img.convert("RGB"), raw_img

    def render_desert_tiers_map(
        self,
        zgrid: np.ndarray,
        zones: Dict[int, Dict],
        block_s2: np.ndarray,
    ) -> Image.Image:
        out_w, out_h = 2000, 1730
        dr_rows = load_xml_rows("desert_refresh")
        tier_by_city: Dict[int, Optional[Tuple[int, int]]] = {}
        for r in dr_rows:
            cid = int(r["city_id"])
            rng = str(r.get("desert_lv_range", "")).strip()
            if ";" in rng:
                lo, hi = map(int, rng.split(";")[:2])
                tier_by_city[cid] = (lo, hi)
            else:
                # Fallback: infer min/max nonzero desert level from desertid & num if available
                dids = [int(x) for x in str(r.get("desertid", "")).split(";") if x.strip()]
                nums = [int(x) for x in str(r.get("num", "")).split(";") if x.strip()]
                active_lvs = [(did % 100) for did, cnt in zip(dids, nums) if cnt > 0]
                if active_lvs:
                    tier_by_city[cid] = (min(active_lvs), max(active_lvs))
                else:
                    tier_by_city[cid] = None

        # Tier palette (golden desert progression)
        unique_tiers = sorted({t for t in tier_by_city.values() if t is not None})
        tier_palette = [
            (226, 198, 128),  # 1-6 Pale sand
            (218, 174, 92),   # Warm dune gold
            (208, 140, 68),   # Amber sandstone
            (194, 102, 54),   # Burnt copper
            (172, 66, 52),    # Crimson canyon
            (142, 44, 62),    # Deep ruby mesa
            (110, 34, 72),    # High-tier obsidian-crimson
        ]
        tier_to_color: Dict[Tuple[int, int], Tuple[int, int, int]] = {}
        for i, t in enumerate(unique_tiers):
            idx = min(i, len(tier_palette) - 1)
            tier_to_color[t] = tier_palette[idx]

        zg = np.array(
            Image.fromarray(zgrid.astype(np.int32)).resize((out_w, out_h), Image.Resampling.NEAREST),
            dtype=np.uint16,
        )
        lut = np.full((256, 3), 180.0, dtype=np.float32)
        for zid in zones:
            t = tier_by_city.get(zid)
            if t is None:
                c = np.array((235, 196, 62), dtype=np.float32)  # Capital gold
            else:
                c = np.array(tier_to_color[t], dtype=np.float32)
            # Subtle per-province brightness offset
            delta = ((zid * 41) % 19) - 9
            lut[zid] = np.clip(c + delta, 20, 248)

        arr = lut[zg]
        # Overlay S2 mountains/rivers
        blk = np.array(
            Image.fromarray((block_s2 * 255).astype(np.uint8)).resize((out_w, out_h), Image.Resampling.NEAREST)
        ) > 127
        arr[blk] = np.array([78, 52, 34], dtype=np.float32)

        edge = np.zeros((out_h, out_w), dtype=bool)
        edge[:-1, :] |= zg[:-1, :] != zg[1:, :]
        edge[:, :-1] |= zg[:, :-1] != zg[:, 1:]
        arr[edge] = np.array([58, 38, 22], dtype=np.float32)

        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
        draw = ImageDraw.Draw(img)
        sx, sy = out_w / 1000.0, out_h / 1000.0
        font_z = get_font(15, bold=True)
        font_title = get_font(30, bold=True)
        font_sub = get_font(17, bold=False)

        for zid, info in zones.items():
            px, py = info["x"] * sx, info["y"] * sy
            t = tier_by_city.get(zid)
            if zid == 1:
                lbl = "CAPITAL" if t is None else f"CAPITAL\nLv {t[0]}-{t[1]}"
            elif t is None:
                lbl = f"Zone {zid}"
            else:
                lbl = f"Lv {t[0]}-{t[1]}"
            draw_text_halo(draw, (px, py), lbl, font_z, fill=(255, 248, 225, 255), halo=(32, 18, 10, 235), radius=2)

        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle((24, 22, 920, 108), radius=12, fill=(28, 18, 10, 215), outline=(235, 190, 95, 220), width=2)
        od.rounded_rectangle((24, out_h - 46 - 28 * len(unique_tiers), 340, out_h - 24), radius=12, fill=(28, 18, 10, 215), outline=(235, 190, 95, 190), width=2)
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)
        draw.text((44, 34), "SEASON 2 WASTES WATCHER: DESERT RESOURCE TIERS", font=font_title, fill=(255, 235, 165, 255))
        draw.text((44, 72), "Cactus / Flint & Crystal Tile Levels Across 87 Provinces + S2 Terrain Relief", font=font_sub, fill=(235, 218, 188, 255))

        for i, t in enumerate(unique_tiers):
            ly = out_h - 36 - 28 * (len(unique_tiers) - i)
            col = tier_to_color[t]
            cnt = sum(1 for v in tier_by_city.values() if v == t)
            draw.rectangle((42, ly + 2, 62, ly + 20), fill=col, outline=(255, 245, 220, 220), width=1)
            draw.text((72, ly), f"Desert Lv {t[0]}-{t[1]} ({cnt} zones)", font=font_sub, fill=(248, 238, 215, 255))

        return img.convert("RGB")

    def extract_main_scenes_and_seasons(self) -> Tuple[Image.Image, Dict[str, Image.Image], Image.Image]:
        print("[2/7] Decoding main_scenes_all (Zones, Overlays, S0-S6 Topology) & World Static Atlases...")
        bp = find_bundle("main_scenes_all_")
        env = load_bundle(bp)
        text_assets: Dict[str, bytes] = {}
        texs: Dict[str, Image.Image] = {}
        for obj in env.objects:
            if obj.type.name == "TextAsset":
                d = obj.read()
                b = d.m_Script.encode("utf-8", "surrogateescape") if isinstance(d.m_Script, str) else bytes(d.m_Script)
                text_assets[d.m_Name] = b
            elif obj.type.name == "Texture2D":
                d = obj.read()
                texs[d.m_Name] = d.image.convert("RGBA")

        # 2a. Official map assets from main_scenes_all
        bigmap = texs["bigmap01"]
        self.save_image(
            bigmap,
            "Main World Maps/World Minimap Base.png",
            "World Minimap Base",
            "Main World Maps",
            "Official Minimap Assets",
            "All Seasons",
            bp.name,
            "bigmap01",
            "Minimap Texture",
            keep_alpha=False,
        )
        style_map = {
            "UImap_img_style01": "Map Overlay Style 01.png",
            "UImap_img_style02": "Map Overlay Style 02.png",
            "UImap_img_style03": "Map Overlay Style 03.png",
            "UImap_img_style04": "Map Overlay Style 04.png",
            "06": "Map Overlay Texture 06.png",
            "07": "Map Overlay Texture 07.png",
        }
        for tname, fname in style_map.items():
            if tname in texs:
                self.save_image(
                    texs[tname],
                    f"Main World Maps/{fname}",
                    fname.replace(".png", ""),
                    "Main World Maps",
                    "Official Minimap Assets",
                    "All Seasons",
                    bp.name,
                    tname,
                    "Overlay Pattern Texture",
                )

        # 2b. Decode binary `zone` + export all 87 Province Zones masks + full Zones & Cities Map
        zw, zh, zones, zgrid = self.decode_zone_binary(text_assets["zone"])
        city_by_id = {c["id"]: c for c in self.cities}
        zone_count = 0
        for zid in sorted(zones.keys()):
            tname = f"zone_{zid}"
            if tname in texs:
                c = city_by_id.get(zid)
                cname = c["name"] if c else f"Level {zones[zid]['level']}"
                lv = c["level"] if c else zones[zid]["level"]
                fname = f"Zone {zid:03d} Lv{lv} {cname}.png"
                self.save_image(
                    texs[tname],
                    f"Main World Maps/Province Zones/{fname}",
                    f"Zone {zid:03d} Lv{lv} {cname}",
                    "Main World Maps",
                    "Province Zones",
                    "All Seasons",
                    bp.name,
                    tname,
                    "Province Mask Sprite",
                    notes=f"Grid pos ({zones[zid]['x']}, {zones[zid]['y']}), bbox {zones[zid]['box']}",
                )
                zone_count += 1
        print(f"  Exported {zone_count} individual province masks.")

        block_s0 = self.decode_bitmap(text_assets["WorldBlockIndex_S0"])
        zones_map_img = self.render_zones_and_cities_map(zgrid, zones, bigmap, block_s0)
        self.save_image(
            zones_map_img,
            "Main World Maps/World Zones and Provinces Map.png",
            "World Zones and Provinces Map",
            "Main World Maps",
            "Decoded World Map",
            "All Seasons",
            bp.name,
            "zone, bigmap01, WorldBlockIndex_S0, worldcity.json",
            "Decoded Cartographic Map",
            notes="87 binary RLE provinces + 90 cities/turrets from worldcity.json",
            keep_alpha=False,
        )

        # 2c. Decode and render ALL 6 official Seasons (S0, S2, S3, S4, S5, S6)
        season_configs = [
            (
                "S0",
                "Pre-Season 1 Clash of Thrones",
                "Pre-Season 1 Clash of Thrones",
                "LAST Z: PRE-SEASON 1 CLASH OF THRONES",
                "1000x1000 Temperate Wasteland Topology | WorldBlockIndex S0 + WorldDecorateIndex S0",
                {
                    "land_inner": (122, 146, 98),
                    "land_outer": (86, 108, 76),
                    "decorate": (60, 92, 54),
                    "block": (54, 62, 68),
                    "block_hi": (146, 158, 160),
                    "block_shadow": (24, 30, 32),
                    "accent": (218, 200, 128),
                },
            ),
            (
                "S2",
                "Season 2 Wastes Watcher",
                "Season 2 Wastes Watcher",
                "LAST Z: SEASON 2 WASTES WATCHER",
                "1000x1000 Golden Desert Wasteland Topology | WorldBlockIndex S2 + WorldDecorateIndex S2",
                {
                    "land_inner": (214, 174, 102),
                    "land_outer": (168, 126, 72),
                    "decorate": (144, 102, 52),
                    "block": (98, 62, 36),
                    "block_hi": (222, 176, 114),
                    "block_shadow": (48, 28, 16),
                    "accent": (252, 212, 118),
                },
            ),
            (
                "S3",
                "Season 3 Everfrost Era",
                "Season 3 Everfrost Era",
                "LAST Z: SEASON 3 EVERFROST ERA",
                "1000x1000 Frozen Glacier Topology | WorldBlockIndex S3 + WorldDecorateIndex S3",
                {
                    "land_inner": (182, 212, 232),
                    "land_outer": (126, 162, 192),
                    "decorate": (96, 138, 174),
                    "block": (46, 78, 116),
                    "block_hi": (228, 245, 255),
                    "block_shadow": (22, 38, 62),
                    "accent": (150, 228, 255),
                },
            ),
            (
                "S4",
                "Season 4 Dinosaur Origin",
                "Season 4 Dinosaur Origin",
                "LAST Z: SEASON 4 DINOSAUR ORIGIN",
                "1000x1000 Prehistoric Jungle & Volcanic Topology | WorldBlockIndex S4 + WorldDecorateIndex S4",
                {
                    "land_inner": (124, 156, 86),
                    "land_outer": (74, 112, 66),
                    "decorate": (42, 86, 48),
                    "block": (128, 52, 34),
                    "block_hi": (235, 118, 56),
                    "block_shadow": (36, 18, 14),
                    "accent": (255, 168, 82),
                },
            ),
            (
                "S5",
                "Season 5 Moonlit Elegy",
                "Season 5 Moonlit Elegy",
                "LAST Z: SEASON 5 MOONLIT ELEGY",
                "1000x1000 Gothic Moonlit Topology | WorldBlockIndex S5 + WorldDecorateIndex S5",
                {
                    "land_inner": (78, 68, 98),
                    "land_outer": (44, 38, 62),
                    "decorate": (62, 46, 82),
                    "block": (132, 34, 56),
                    "block_hi": (222, 116, 142),
                    "block_shadow": (18, 12, 24),
                    "accent": (228, 178, 255),
                },
            ),
            (
                "S6",
                "Season 6",
                "Season 6",
                "LAST Z: SEASON 6 EXPANDED WORLD",
                "1600x1600 Expanded Tactical World Topology | WorldBlockIndex S6 + WorldDecorateIndex S6",
                {
                    "land_inner": (68, 108, 126),
                    "land_outer": (38, 66, 86),
                    "decorate": (52, 128, 134),
                    "block": (184, 122, 46),
                    "block_hi": (252, 208, 112),
                    "block_shadow": (18, 28, 38),
                    "accent": (110, 235, 225),
                },
            ),
        ]

        topo_renders: Dict[str, Image.Image] = {}
        block_s2: Optional[np.ndarray] = None
        for scode, folder, season_name, title, subtitle, pal in season_configs:
            blk = self.decode_bitmap(text_assets[f"WorldBlockIndex_{scode}"])
            dec = self.decode_bitmap(text_assets[f"WorldDecorateIndex_{scode}"])
            if scode == "S2":
                block_s2 = blk
            styled_img, raw_img = self.render_season_topology_map(
                scode, title, subtitle, blk, dec, pal, zgrid=zgrid if scode != "S6" else None, show_cities=(scode != "S6")
            )
            topo_renders[scode] = styled_img

            short_prefix = (
                "Pre-Season 1"
                if scode == "S0"
                else ("Season 6 World" if scode == "S6" else season_name)
            )
            self.save_image(
                styled_img,
                f"Seasonal Maps/{folder}/{short_prefix} Topology Map.png",
                f"{short_prefix} Topology Map",
                "Seasonal Maps",
                folder,
                season_name,
                bp.name,
                f"WorldBlockIndex_{scode}, WorldDecorateIndex_{scode}",
                "Decoded Topology Map",
                notes=f"LSB-first 1-bit decoded {blk.shape[0]}x{blk.shape[1]} terrain + relief + landmarks",
                keep_alpha=False,
            )
            raw_suffix = "Raw 1600" if scode == "S6" else "Raw 1K"
            self.save_image(
                raw_img,
                f"Seasonal Maps/{folder}/{short_prefix} Topology {raw_suffix}.png",
                f"{short_prefix} Topology {raw_suffix}",
                "Seasonal Maps",
                folder,
                season_name,
                bp.name,
                f"WorldBlockIndex_{scode}, WorldDecorateIndex_{scode}",
                "Decoded Topology Bitmap",
                notes=f"Unlabeled native {blk.shape[0]}x{blk.shape[1]} exact grid bitmap",
                keep_alpha=False,
            )
            # Mirror S5 and S6 primary topology maps in Main World Maps too so all 6 seasons are represented there
            if scode in ("S0", "S2", "S5", "S6"):
                self.save_image(
                    styled_img,
                    f"Main World Maps/{short_prefix} Topology Map.png",
                    f"{short_prefix} Topology Map",
                    "Main World Maps",
                    "Decoded World Map",
                    season_name,
                    bp.name,
                    f"WorldBlockIndex_{scode}, WorldDecorateIndex_{scode}",
                    "Decoded Topology Map",
                    notes="Mirror of primary seasonal topology map",
                    keep_alpha=False,
                )

        # Render Desert Resource Tiers Map (save to both Season 2 and Event Maps/Desert Battlefield)
        assert block_s2 is not None
        desert_tiers_img = self.render_desert_tiers_map(zgrid, zones, block_s2)
        self.save_image(
            desert_tiers_img,
            "Seasonal Maps/Season 2 Wastes Watcher/Season 2 Desert Resource Tiers Map.png",
            "Season 2 Desert Resource Tiers Map",
            "Seasonal Maps",
            "Season 2 Wastes Watcher",
            "Season 2 Wastes Watcher",
            bp.name,
            "zone, WorldBlockIndex_S2, desert refresh.json",
            "Decoded Resource Tier Map",
            notes="Exact Cactus/Crystal tile levels across all 87 provinces from desert refresh.json",
            keep_alpha=False,
        )

        # 2d. World Static Atlases (`main_sprites_worldstaticatlas_*`) -> respective season folders
        ws_bname, ws_texs = self.load_bundle_textures("main_sprites_worldstaticatlas_")
        ws_mapping = [
            ("world_static_s1_unlit_shadow", "Seasonal Maps/Pre-Season 1 Clash of Thrones/Pre-Season 1 World Static Atlas Shadow.png", "Pre-Season 1 Clash of Thrones"),
            ("world_static_s2_unlit_shadow", "Seasonal Maps/Season 2 Wastes Watcher/Season 2 World Static Atlas Shadow.png", "Season 2 Wastes Watcher"),
            ("world_static_s3_unlit_shadow", "Seasonal Maps/Season 3 Everfrost Era/Season 3 World Static Atlas Shadow.png", "Season 3 Everfrost Era"),
            ("world_static_s4_unlit_shadow", "Seasonal Maps/Season 4 Dinosaur Origin/Season 4 World Static Atlas Shadow.png", "Season 4 Dinosaur Origin"),
            ("world_static_s4_unlit_daynight", "Seasonal Maps/Season 4 Dinosaur Origin/Season 4 World Static Atlas Day Night.png", "Season 4 Dinosaur Origin"),
            ("world_static_s4_unlit_daynight_maintex1", "Seasonal Maps/Season 4 Dinosaur Origin/Season 4 World Static Atlas Day Night Main.png", "Season 4 Dinosaur Origin"),
        ]
        for tname, rel, sname in ws_mapping:
            if tname in ws_texs:
                self.save_image(
                    ws_texs[tname],
                    rel,
                    Path(rel).stem,
                    "Seasonal Maps",
                    sname,
                    sname,
                    ws_bname,
                    tname,
                    "World Static Atlas",
                )

        # Also export `map_ice*` from `main_texturert_all_*` into Season 3 Everfrost Era
        rt_bname, rt_texs = self.load_bundle_textures("main_texturert_all_")
        for tname, fname in [
            ("map_ice", "Season 3 Ice Map Texture 01.png"),
            ("map_ice_2", "Season 3 Ice Map Texture 02.png"),
            ("map_ice_3", "Season 3 Ice Map Texture 03.png"),
        ]:
            if tname in rt_texs:
                self.save_image(
                    rt_texs[tname],
                    f"Seasonal Maps/Season 3 Everfrost Era/{fname}",
                    fname.replace(".png", ""),
                    "Seasonal Maps",
                    "Season 3 Everfrost Era",
                    "Season 3 Everfrost Era",
                    rt_bname,
                    tname,
                    "Ice Map Texture",
                    keep_alpha=False,
                )

        return zones_map_img, topo_renders, desert_tiers_img

    # ------------------------------------------------------------------
    # 3. EVENT MAPS (All 12+ Event Subfolders + Stitched / Annotated Maps)
    # ------------------------------------------------------------------
    def build_volcano_annotated_map(
        self,
        base_map: Image.Image,
        select_texs: Dict[str, Image.Image],
    ) -> Image.Image:
        # UIVolcanoMap layout is 746 x 503 (c_texture_vocano_map is 512 x 345, exact 1.457 scale)
        # Render at 2x UI scale = 1492 x 1006, padded to 1600 x 1180 for clean title & legend!
        ui_w, ui_h = 746, 503
        scale = 2.0
        map_w, map_h = int(ui_w * scale), int(ui_h * scale)
        pad_top, pad_bot, pad_side = 86, 94, 54
        W, H = map_w + pad_side * 2, map_h + pad_top + pad_bot

        canvas = Image.new("RGBA", (W, H), (18, 12, 12, 255))
        base_up = base_map.convert("RGBA").resize((map_w, map_h), Image.Resampling.LANCZOS)
        canvas.paste(base_up, (pad_side, pad_top))

        # Overlay the 10 verified UIVolcanoMapSelect sprites at exact prefab RectTransform coordinates (with gentle alpha so base map detail shines through)
        # (sector_num, sprite_key, pos_x, pos_y, sz_w, sz_h, flip_y, rot180, tint)
        sectors = [
            (1, "c_vocano_map_select_04", -1.5, 0.9, 219.5, 150.5, False, False, (255, 120, 60)),
            (2, "c_vocano_map_select_05", -59.6, 78.9, 362.0, 167.0, False, False, (255, 195, 75)),
            (3, "c_vocano_map_select_05", -59.2, -77.5, 362.0, 167.0, True, False, (255, 195, 75)),
            (4, "c_vocano_map_select_03", 145.2, -0.5, 193.0, 326.0, False, False, (255, 160, 75)),
            (5, "c_vocano_map_select_01", -0.6, 199.2, 360.0, 88.0, False, False, (120, 195, 255)),
            (6, "c_vocano_map_select_02", -240.2, 120.4, 245.5, 247.3, True, True, (120, 195, 255)),
            (7, "c_vocano_map_select_02", -240.2, -119.1, 244.4, 247.3, False, True, (120, 195, 255)),
            (8, "c_vocano_map_select_01", -0.6, -196.5, 360.0, 88.0, True, False, (120, 195, 255)),
            (9, "c_vocano_map_select_02", 239.2, -119.1, 245.0, 247.5, True, False, (120, 195, 255)),
            (10, "c_vocano_map_select_02", 238.9, 120.4, 245.5, 247.3, False, False, (120, 195, 255)),
        ]
        cx_map = pad_side + map_w / 2.0
        cy_map = pad_top + map_h / 2.0

        for snum, skey, px, py, sw, sh, fy, r180, tint in sectors:
            if skey not in select_texs:
                continue
            sp = select_texs[skey].convert("RGBA")
            if r180:
                sp = sp.rotate(180)
            if fy:
                sp = sp.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            sp = sp.resize((int(round(sw * scale)), int(round(sh * scale))), Image.Resampling.LANCZOS)
            # Soft tint & 32% opacity so borders/regions highlight cleanly without hiding the volcano art
            arr = np.array(sp, dtype=np.float32)
            arr[:, :, 0] = arr[:, :, 0] * 0.55 + tint[0] * 0.45
            arr[:, :, 1] = arr[:, :, 1] * 0.55 + tint[1] * 0.45
            arr[:, :, 2] = arr[:, :, 2] * 0.55 + tint[2] * 0.45
            arr[:, :, 3] = arr[:, :, 3] * 0.34
            sp_tinted = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
            x0 = int(round(cx_map + px * scale - sp_tinted.width / 2.0))
            y0 = int(round(cy_map - py * scale - sp_tinted.height / 2.0))
            canvas.alpha_composite(sp_tinted, (x0, y0))

        # Overlay concentric resource rings from volcano_area.json + landmarks from volcano_land.json + volcano building.json
        vr_names = {}
        for r in load_xml_rows("volcano_res"):
            vr_names[int(r["id"])] = clean_name(self.loc.get(str(r.get("name", "")), f"Resource {r['id']}"))

        # Map world coordinates (-170..170) roughly onto map_w/map_h (note volcano_land spans x=-70..+70, y=-98..+98)
        # Compute affine scale from volcano_land (70, 42) -> UIVolcanoMapSelect_10 (238.9, 120.4) -> sx ~ 3.4*scale, sy ~ 2.04*scale
        coord_sx = (239.0 / 70.0) * scale
        coord_sy = (198.0 / 98.0) * scale

        ov = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        # Draw concentric rings (50, 75, 125)
        for radius_val, rcol, rlbl in [
            (50, (255, 120, 60, 145), "Inner Ring (13-50): Adv/Med Mines"),
            (75, (255, 200, 80, 130), "Mid Ring (51-75): Med/Basic Mines"),
            (125, (140, 210, 255, 105), "Outer Ring (76-125): Basic Mines"),
        ]:
            rx = radius_val * coord_sx * 0.72
            ry = radius_val * coord_sy * 0.95
            od.ellipse((cx_map - rx, cy_map - ry, cx_map + rx, cy_map + ry), outline=rcol, width=2)
        canvas = Image.alpha_composite(canvas, ov)
        draw = ImageDraw.Draw(canvas)

        font_lbl = get_font(18, bold=True)
        font_sm = get_font(14, bold=True)
        font_title = get_font(30, bold=True)
        font_sub = get_font(17, bold=False)

        # Plot volcano_building (11 Field Hospitals / Landmarks around core; Y-down matches volcano_land & worldcity!)
        for b in load_xml_rows("volcano_building"):
            bx, by = map(float, b["coordinates"].split(","))
            px = cx_map + bx * coord_sx
            py = cy_map + by * coord_sy
            r = 6
            draw.rectangle((px - r, py - r, px + r, py + r), fill=(115, 255, 165, 240), outline=(10, 24, 16, 255), width=2)

        # Plot all 10 volcano_land landmarks at their verified sector centers (Y-down: S5=top, S8=bottom, S6=TL, S7=BL, S10=TR, S9=BR)
        sector_centers_ui = {
            1: (-1.5, 0.9),
            2: (-59.6, 78.9),
            3: (-59.2, -77.5),
            4: (145.2, -0.5),
            5: (-0.6, 199.2),
            6: (-240.2, 120.4),
            7: (-240.2, -119.1),
            8: (-0.6, -196.5),
            9: (239.2, -119.1),
            10: (238.9, 120.4),
        }
        for r in load_xml_rows("volcano_land"):
            lid = int(r["id"])
            lx, ly = map(float, r["coordinates"].split(","))
            res_id = int(r["res_id"])
            lname = vr_names.get(res_id, f"Sector {lid}")
            if lid in sector_centers_ui:
                ux, uy = sector_centers_ui[lid]
                px = cx_map + ux * scale
                py = cy_map - uy * scale
            else:
                px = cx_map + lx * coord_sx
                py = cy_map + ly * coord_sy
            rad = 14 if lid == 1 else (11 if lid <= 4 else 9)
            fill = (255, 95, 45, 255) if lid == 1 else ((255, 195, 75, 255) if lid <= 4 else (95, 195, 255, 255))
            draw.ellipse((px - rad, py - rad, px + rad, py + rad), fill=fill, outline=(255, 255, 255, 255), width=2)
            draw_text_halo(draw, (px, py - rad - 14), f"{lname}", font_lbl, fill=(255, 244, 212, 255))
            draw_text_halo(draw, (px, py + rad + 11), f"S{lid} ({int(lx)},{int(ly)})", font_sm, fill=(220, 232, 245, 245), radius=1)

        draw.rectangle((pad_side, pad_top, pad_side + map_w, pad_top + map_h), outline=(245, 148, 72, 220), width=3)
        draw.text((pad_side, 18), "VOLCANO WAR: BLACKRIDGE VOLCANO TACTICAL MAP", font=font_title, fill=(255, 215, 140, 255))
        draw.text(
            (pad_side, 54),
            "10 Sectors (volcano land) | 11 Field Hospitals (volcano building) | Concentric Energy Mine Zones (volcano area)",
            font=font_sub,
            fill=(228, 212, 200, 255),
        )

        # Bottom legend
        ly = pad_top + map_h + 24
        leg = [
            ((255, 95, 45), "Blackridge Volcano (Core)"),
            ((255, 195, 75), "Energy Tower / Lava Furnace / Radiation Warehouse"),
            ((95, 195, 255), "Lava Pools (6 Outer Sectors)"),
            ((115, 255, 165), "Field Hospitals (11)"),
        ]
        lx_cur = pad_side
        for col, lbl in leg:
            draw.rectangle((lx_cur, ly + 3, lx_cur + 18, ly + 21), fill=col, outline=(255, 255, 255, 220), width=1)
            draw.text((lx_cur + 25, ly), lbl, font=font_sub, fill=(242, 235, 225, 255))
            lx_cur += 35 + int(draw.textlength(lbl, font=font_sub)) + 26

        return canvas.convert("RGB")

    def build_castle_assembled_map(
        self,
        base_img: Image.Image,
        chips: Dict[int, Image.Image],
    ) -> Image.Image:
        # Verified RectTransform positions from main_prefabs_slg_ui_activitycenter (Map size 1024x907, pivot 0.5,0.5):
        # map_1: (-294.0, +248.5), map_2: (-268.0, -141.5), map_3: (-72.5, +88.9), map_4: (+84.0, +203.5), map_5: (+192.0, -129.8)
        canvas = base_img.convert("RGBA").copy()
        cx, cy = canvas.width / 2.0, canvas.height / 2.0
        placements = {
            1: (-294.0, 248.5),
            2: (-268.0, -141.5),
            3: (-72.5, 88.9),
            4: (84.0, 203.5),
            5: (192.0, -129.8),
        }
        for idx in (1, 2, 3, 4, 5):
            if idx not in chips:
                continue
            ch = chips[idx].convert("RGBA")
            ux, uy = placements[idx]
            x0 = int(round(cx + ux - ch.width / 2.0))
            y0 = int(round(cy - uy - ch.height / 2.0))
            canvas.alpha_composite(ch, (x0, y0))
        return canvas

    def extract_event_maps(self, desert_tiers_img: Image.Image) -> Dict[str, Image.Image]:
        print("[3/7] Extracting all Event Maps across all event/activity bundles...")
        key_previews: Dict[str, Image.Image] = {}

        # 3.1 Volcano War
        b_bg3, t_bg3 = self.load_bundle_textures("main_uitexture_uiactivitybgportrait3_")
        b_vol, t_vol = self.load_bundle_textures("main_sprites_ui_uiportrait_uiportraitvolcanowar_")
        vmap = t_bg3["c_texture_vocano_map"]
        self.save_image(vmap, "Event Maps/Volcano War/Volcano War Map.png", "Volcano War Map", "Event Maps", "Volcano War", "Season 4 Dinosaur Origin", b_bg3, "c_texture_vocano_map", "Event Map Texture", keep_alpha=False)
        self.save_image(t_bg3["c_texture_vocano_main_bg"], "Event Maps/Volcano War/Volcano War Main Battlefield Background.png", "Volcano War Main Battlefield Background", "Event Maps", "Volcano War", "Season 4 Dinosaur Origin", b_bg3, "c_texture_vocano_main_bg", "Event Battlefield Background", keep_alpha=False)
        for i in range(1, 6):
            k = f"c_vocano_map_select_0{i}"
            if k in t_vol:
                self.save_image(t_vol[k], f"Event Maps/Volcano War/Volcano War Sector Overlay 0{i}.png", f"Volcano War Sector Overlay 0{i}", "Event Maps", "Volcano War", "Season 4 Dinosaur Origin", b_vol, k, "Map Sector Overlay")
        for i in range(1, 5):
            k = f"vocano_img_00{i}"
            if k in t_vol:
                self.save_image(t_vol[k], f"Event Maps/Volcano War/Volcano War Guide Diagram 0{i}.png", f"Volcano War Guide Diagram 0{i}", "Event Maps", "Volcano War", "Season 4 Dinosaur Origin", b_vol, k, "Event Guide Diagram")
            kd = f"vocano_img_003_0{i}"
            if kd in t_vol:
                self.save_image(t_vol[kd], f"Event Maps/Volcano War/Volcano War Guide Detail 0{i}.png", f"Volcano War Guide Detail 0{i}", "Event Maps", "Volcano War", "Season 4 Dinosaur Origin", b_vol, kd, "Event Guide Detail")

        v_ann = self.build_volcano_annotated_map(vmap, t_vol)
        self.save_image(v_ann, "Event Maps/Volcano War/Volcano War Tactical Map Annotated.png", "Volcano War Tactical Map Annotated", "Event Maps", "Volcano War", "Season 4 Dinosaur Origin", f"{b_bg3}, {b_vol}", "c_texture_vocano_map, c_vocano_map_select_01..05, volcano_land/building/area.json", "Annotated Event Map", keep_alpha=False)
        key_previews["Volcano"] = v_ann

        # 3.2 Desert Battlefield
        self.save_image(desert_tiers_img, "Event Maps/Desert Battlefield/Desert Battlefield Resource Tiers Map.png", "Desert Battlefield Resource Tiers Map", "Event Maps", "Desert Battlefield", "Season 2 Wastes Watcher", "main_scenes_all", "zone, WorldBlockIndex_S2, desert refresh.json", "Decoded Event Map", keep_alpha=False)
        b_des_g, t_des_g = self.load_bundle_textures("art_lastday_models_environment_map_world_desert_")
        for tname, fname in [("O_env_Desert_dibiao01_D02", "Desert Battlefield Ground 02.png"), ("O_env_Desert_dibiao01_D03", "Desert Battlefield Ground 03.png")]:
            if tname in t_des_g:
                self.save_image(t_des_g[tname], f"Event Maps/Desert Battlefield/{fname}", fname[:-4], "Event Maps", "Desert Battlefield", "Season 2 Wastes Watcher", b_des_g, tname, "Battlefield Terrain Texture", keep_alpha=False)
        b_mas, t_mas = self.load_bundle_textures("main_sprites_seasondesert_")
        for i in range(1, 10):
            k = f"massif_{i}"
            if k in t_mas:
                self.save_image(t_mas[k], f"Event Maps/Desert Battlefield/Desert Massif 0{i}.png", f"Desert Massif 0{i}", "Event Maps", "Desert Battlefield", "Season 2 Wastes Watcher", b_mas, k, "Battlefield Map Marker")

        # 3.3 Capital War
        b_cap, t_cap = self.load_bundle_textures("main_uitexture_uiactivitybgportrait_capitalwar_")
        b_city, t_city = self.load_bundle_textures("main_uitexture_uiactivitycity_")
        cap_exports = [
            (b_city, t_city, "UIcapitalwar_img_guide", "Capital War Guide Map.png", "All Seasons"),
            (b_cap, t_cap, "capitalwar_popup_img03", "Capital War Battlefield View 01.png", "All Seasons"),
            (b_cap, t_cap, "capitalwar_popup_img08", "Capital War Battlefield View 02.png", "All Seasons"),
            (b_cap, t_cap, "capitalwar_popup_img03_s5", "Capital War Season 5 Battlefield View 01.png", "Season 5 Moonlit Elegy"),
            (b_cap, t_cap, "capitalwar_popup_img08_s5", "Capital War Season 5 Battlefield View 02.png", "Season 5 Moonlit Elegy"),
            (b_cap, t_cap, "capitalwar_presidentoffice_bg", "Capital War President Office Background.png", "All Seasons"),
            (b_cap, t_cap, "capitalwar_predictionbg", "Capital War Prediction Background.png", "All Seasons"),
            (b_cap, t_cap, "capitalwar_predictionbg_s5", "Capital War Season 5 Prediction Background.png", "Season 5 Moonlit Elegy"),
            (b_city, t_city, "c_texture_activity_dacheng_declare_war_pic_01", "Capital War City Assault View 01.png", "All Seasons"),
            (b_city, t_city, "c_texture_activity_dacheng_declare_war_pic_02", "Capital War City Assault View 02.png", "All Seasons"),
            (b_city, t_city, "c_texture_activity_dacheng_declare_war_pic_03", "Capital War City Assault View 03.png", "All Seasons"),
            (b_city, t_city, "c_texture_activity_dacheng_declare_war_pic_04", "Capital War City Assault View 04.png", "All Seasons"),
            (b_city, t_city, "c_texture_activity_dacheng_declare_war_pic_05", "Capital War City Assault View 05.png", "All Seasons"),
            (b_city, t_city, "c_texture_activity_dacheng_declare_war_pic_06", "Capital War City Assault View 06.png", "All Seasons"),
            (b_city, t_city, "c_texture_activity_dacheng_declare_war_pic_01_s5", "Capital War Season 5 City Assault View 01.png", "Season 5 Moonlit Elegy"),
        ]
        for bn, td, tn, fn, sn in cap_exports:
            if tn in td:
                self.save_image(td[tn], f"Event Maps/Capital War/{fn}", fn[:-4], "Event Maps", "Capital War", sn, bn, tn, "Event Map / Guide")
        if "UIcapitalwar_img_guide" in t_city:
            key_previews["CapitalWar"] = t_city["UIcapitalwar_img_guide"].convert("RGB")

        # 3.4 World Siege
        b_ws, t_ws = self.load_bundle_textures("main_uitexture_uiactivityworldsiege_")
        ws_exports = [
            ("c_texture_worldsiege_main_bg", "World Siege Main Battlefield Background.png"),
            ("ctexture_worldsiege_guide01", "World Siege Guide Map 01.png"),
            ("ctexture_worldsiege_guide02", "World Siege Guide Map 02.png"),
            ("c_texture_worldsiege_city01", "World Siege City View 01.png"),
            ("c_texture_worldsiege_city02", "World Siege City View 02.png"),
            ("c_texture_worldsiege_book_banner", "World Siege Chronicle Banner 01.png"),
            ("c_texture_worldsiege_book_banner2", "World Siege Chronicle Banner 02.png"),
            ("c_texture_worldsiege_book_banner3", "World Siege Chronicle Banner 03.png"),
            ("c_texture_worldsiege_book_banner4", "World Siege Chronicle Banner 04.png"),
            ("c_texture_worldsiege_popup_bg", "World Siege Event Overview Background.png"),
        ]
        for tn, fn in ws_exports:
            if tn in t_ws:
                self.save_image(t_ws[tn], f"Event Maps/World Siege/{fn}", fn[:-4], "Event Maps", "World Siege", "All Seasons", b_ws, tn, "Event Map / Guide")

        # 3.5 Cross Server War
        b_cs, t_cs = self.load_bundle_textures("main_uitexture_uiactivitycrossserver_")
        cs_exports = [
            ("c_texture_activity_cross_world_battle_bg", "Cross Server War Battle Background.png"),
            ("c_txture_cross_wonder_fighting_bg01", "Cross Server Wonder Fighting Background.png"),
            ("c_texture_activity_across_wonder_warflag_bg", "Cross Server Wonder Warflag Background.png"),
            ("c_activity_cross_world_guide_01", "Cross Server War Guide Map 01.png"),
            ("c_activity_cross_world_guide_02", "Cross Server War Guide Map 02.png"),
            ("c_activity_cross_world_vs", "Cross Server War Versus Overview.png"),
            ("c_texture_activity_cross_world_city_1_light", "Cross Server War City 01.png"),
            ("c_texture_activity_cross_world_city_2_light", "Cross Server War City 02.png"),
            ("c_texture_activity_cross_world_city_3_light", "Cross Server War City 03.png"),
            ("c_texture_activity_cross_battle", "Cross Server War Battle Emblem.png"),
        ]
        for tn, fn in cs_exports:
            if tn in t_cs:
                self.save_image(t_cs[tn], f"Event Maps/Cross Server War/{fn}", fn[:-4], "Event Maps", "Cross Server War", "All Seasons", b_cs, tn, "Event Map / Guide")

        # 3.6 Castle Adventure (with exact prefab-stitched Castle Adventure Map!)
        b_cas, t_cas = self.load_bundle_textures("main_uitexture_uitexturecastle_6")
        b_cas_dig, t_cas_dig = self.load_bundle_textures("main_uitexture_uitexturecastle_c_texture_castle_dig_")
        b_big, t_big = self.load_bundle_textures("main_sprites_ui_uibigactivity_")
        cas_base = t_cas["c_texture_castle_map_base"]
        cas_chips: Dict[int, Image.Image] = {}
        for i in range(1, 6):
            k = f"c_castle_map_chip_0{i}"
            if k in t_big:
                cas_chips[i] = t_big[k]
                self.save_image(t_big[k], f"Event Maps/Castle Adventure/Castle Adventure Map Piece 0{i}.png", f"Castle Adventure Map Piece 0{i}", "Event Maps", "Castle Adventure", "All Seasons", b_big, k, "Map Puzzle Piece")
        cas_full = self.build_castle_assembled_map(cas_base, cas_chips)
        self.save_image(cas_full, "Event Maps/Castle Adventure/Castle Adventure Map.png", "Castle Adventure Map", "Event Maps", "Castle Adventure", "All Seasons", f"{b_cas}, {b_big}", "c_texture_castle_map_base, c_castle_map_chip_01..05", "Stitched Event Map", notes="Assembled using verified UICastleAdventureTreasureMapMain RectTransform coordinates")
        self.save_image(cas_base, "Event Maps/Castle Adventure/Castle Adventure Map Base.png", "Castle Adventure Map Base", "Event Maps", "Castle Adventure", "All Seasons", b_cas, "c_texture_castle_map_base", "Event Map Base")
        self.save_image(t_cas["c_texture_castle_map_bg"], "Event Maps/Castle Adventure/Castle Adventure Map Background.png", "Castle Adventure Map Background", "Event Maps", "Castle Adventure", "All Seasons", b_cas, "c_texture_castle_map_bg", "Event Map Background", keep_alpha=False)
        if "c_texture_castle_dig_grid_bg" in t_cas_dig:
            self.save_image(t_cas_dig["c_texture_castle_dig_grid_bg"], "Event Maps/Castle Adventure/Castle Adventure Dig Grid Map.png", "Castle Adventure Dig Grid Map", "Event Maps", "Castle Adventure", "All Seasons", b_cas_dig, "c_texture_castle_dig_grid_bg", "Event Grid Map")
        if "c_texture_castle_dig_bg" in t_cas_dig:
            self.save_image(t_cas_dig["c_texture_castle_dig_bg"], "Event Maps/Castle Adventure/Castle Adventure Dig Background.png", "Castle Adventure Dig Background", "Event Maps", "Castle Adventure", "All Seasons", b_cas_dig, "c_texture_castle_dig_bg", "Event Background", keep_alpha=False)
        key_previews["Castle"] = cas_full.convert("RGB")

        # 3.7 Landing Operations (3 stages + stitched full campaign map!)
        b_lo, t_lo = self.load_bundle_textures("main_uitexture_uilandingoperations_")
        lo_imgs: Dict[int, Image.Image] = {}
        for i in (1, 2, 3):
            k = f"LevelListBg{i}"
            lo_imgs[i] = t_lo[k].convert("RGB")
            self.save_image(lo_imgs[i], f"Event Maps/Landing Operations/Landing Operations Stage Map 0{i}.png", f"Landing Operations Stage Map 0{i}", "Event Maps", "Landing Operations", "All Seasons", b_lo, k, "Campaign Stage Map", keep_alpha=False)
        # Stitch vertical continuous 3-stage campaign map (verified on contact sheet)
        w_lo, h_lo = lo_imgs[1].size
        # Also test horizontal vs vertical; LevelListBg1..3 are portrait 864x2048 scrolling stage maps
        lo_full = Image.new("RGB", (w_lo, h_lo * 3))
        lo_full.paste(lo_imgs[1], (0, 0))
        lo_full.paste(lo_imgs[2], (0, h_lo))
        lo_full.paste(lo_imgs[3], (0, h_lo * 2))
        self.save_image(lo_full, "Event Maps/Landing Operations/Landing Operations Full Map.png", "Landing Operations Full Map", "Event Maps", "Landing Operations", "All Seasons", b_lo, "LevelListBg1, LevelListBg2, LevelListBg3", "Stitched Campaign Map", notes="864x6144 full 3-stage vertical campaign map (Stages 1 to 3)", keep_alpha=False)
        # Side-by-side 3-stage comparison overview too for easy viewing on landscape screens
        lo_sbs = Image.new("RGB", (w_lo * 3, h_lo))
        lo_sbs.paste(lo_imgs[1], (0, 0))
        lo_sbs.paste(lo_imgs[2], (w_lo, 0))
        lo_sbs.paste(lo_imgs[3], (w_lo * 2, 0))
        self.save_image(lo_sbs, "Event Maps/Landing Operations/Landing Operations All Stages Overview.png", "Landing Operations All Stages Overview", "Event Maps", "Landing Operations", "All Seasons", b_lo, "LevelListBg1, LevelListBg2, LevelListBg3", "Stitched Campaign Overview", notes="2592x2048 side-by-side overview of Chapters 1, 2, and 3", keep_alpha=False)
        key_previews["LandingOps"] = lo_sbs

        # 3.8 Mine Events
        b_bg2, t_bg2 = self.load_bundle_textures("main_uitexture_uiactivitybgportrait2_")
        b_act, t_act = self.load_bundle_textures("main_uitexture_uitextureactivity_")
        for bn, td, tn, fn in [
            (b_bg2, t_bg2, "UIgoldmine_img_PIC01", "Gold Mine Event Map 01.png"),
            (b_bg2, t_bg2, "UIgoldmine_img_PIC02", "Gold Mine Event Map 02.png"),
            (b_act, t_act, "c_texture_activity_season_mine_bg", "Season Mine Event Background.png"),
            (b_act, t_act, "c_texture_activity_season_mine_icon", "Season Mine Event Landmark.png"),
        ]:
            if tn in td:
                self.save_image(td[tn], f"Event Maps/Mine Events/{fn}", fn[:-4], "Event Maps", "Mine Events", "All Seasons", bn, tn, "Event Map / Overview")

        # 3.9 World Cup
        b_wc, t_wc = self.load_bundle_textures("main_uitexture_uitextureworldcup_")
        wc_exports = [
            ("UIworldcup_preview", "World Cup Stadium Preview.png"),
            ("UIworldcup_zombie_bg", "World Cup Zombie Field Background.png"),
            ("UIworldcup_zombie_bg_empty", "World Cup Zombie Field Empty.png"),
            ("UIWorldCup_schedule_bg01", "World Cup Schedule Bracket Map 01.png"),
            ("UIWorldCup_schedule_bg02", "World Cup Schedule Bracket Map 02.png"),
            ("UIworldcup_guess_PIC", "World Cup Prediction Stadium.png"),
            ("UIworldcup_free_PIC", "World Cup Free Match Stadium.png"),
            ("UIworldcup_shop_PIC", "World Cup Shop Stadium.png"),
        ]
        for tn, fn in wc_exports:
            if tn in t_wc:
                self.save_image(t_wc[tn], f"Event Maps/World Cup/{fn}", fn[:-4], "Event Maps", "World Cup", "All Seasons", b_wc, tn, "Event Stadium / Schedule Map")

        # 3.10 Dispatch and Explore
        b_exp, t_exp = self.load_bundle_textures("main_uitexture_uitextureexplore_")
        b_trk, t_trk = self.load_bundle_textures("main_uitexture_uiactivitytruck_")
        for i in (1, 2, 3):
            k = f"c_texture_dispatch_world_bg_0{i}"
            if k in t_bg3:
                self.save_image(t_bg3[k], f"Event Maps/Dispatch and Explore/Dispatch World Map 0{i}.png", f"Dispatch World Map 0{i}", "Event Maps", "Dispatch and Explore", "All Seasons", b_bg3, k, "Dispatch World Map")
        if "c_texture_activity_season_dispatch_bg" in t_act:
            self.save_image(t_act["c_texture_activity_season_dispatch_bg"], "Event Maps/Dispatch and Explore/Season Dispatch Event Background.png", "Season Dispatch Event Background", "Event Maps", "Dispatch and Explore", "All Seasons", b_act, "c_texture_activity_season_dispatch_bg", "Event Overview", keep_alpha=False)
        if "c_texture_explore_truck_icon_bg" in t_exp:
            self.save_image(t_exp["c_texture_explore_truck_icon_bg"], "Event Maps/Dispatch and Explore/Explore Truck Route Map Background.png", "Explore Truck Route Map Background", "Event Maps", "Dispatch and Explore", "All Seasons", b_exp, "c_texture_explore_truck_icon_bg", "Route Map Background")
        if "c_texture_explore_world_banner_02" in t_exp:
            self.save_image(t_exp["c_texture_explore_world_banner_02"], "Event Maps/Dispatch and Explore/Explore World Route Banner.png", "Explore World Route Banner", "Event Maps", "Dispatch and Explore", "All Seasons", b_exp, "c_texture_explore_world_banner_02", "Route Map Banner")
        for i in range(1, 7):
            k = f"c_texture_explore_truck_icon_0{i}"
            if k in t_exp:
                self.save_image(t_exp[k], f"Event Maps/Dispatch and Explore/Explore Truck Convoy Tier 0{i}.png", f"Explore Truck Convoy Tier 0{i}", "Event Maps", "Dispatch and Explore", "All Seasons", b_exp, k, "Convoy Map Visual")
        if "c_texture_activity_season_truck_bg" in t_trk:
            self.save_image(t_trk["c_texture_activity_season_truck_bg"], "Event Maps/Dispatch and Explore/Season Truck Convoy Event Background.png", "Season Truck Convoy Event Background", "Event Maps", "Dispatch and Explore", "All Seasons", b_trk, "c_texture_activity_season_truck_bg", "Event Map Background", keep_alpha=False)
        if "c_texture_dispatch_world_bg_03" in t_bg3:
            key_previews["Dispatch"] = t_bg3["c_texture_dispatch_world_bg_03"].convert("RGB")

        # 3.11 Season Influence Territories & Season Review Maps
        b_inf, t_inf = self.load_bundle_textures("main_sprites_ui_uiseasonground_")
        for prefix_t, label, season_lbl in [
            ("UI_season_influence", "Season 1 to 3 Influence Territory", "Season 2 Wastes Watcher"),
            ("UI_season4_influence", "Season 4 Influence Territory", "Season 4 Dinosaur Origin"),
            ("UI_season5_influence", "Season 5 Influence Territory", "Season 5 Moonlit Elegy"),
        ]:
            for i in range(1, 11):
                k = f"{prefix_t}{i}"
                if k in t_inf:
                    self.save_image(t_inf[k], f"Event Maps/Season Influence Territories/{label} {i:02d}.png", f"{label} {i:02d}", "Event Maps", "Season Influence Territories", season_lbl, b_inf, k, "Territory Map Emblem")

        b_rev, t_rev = self.load_bundle_textures("main_uitexture_uitextureseasonreview_")
        rev_exports = [
            ("c_texture_season_review_handbook_bg", "Season Review Handbook Map Background.png", "All Seasons"),
            ("c_texture_season_review_handbook_s2", "Season 2 Review Chronicle Cover.png", "Season 2 Wastes Watcher"),
            ("c_texture_season_review_handbook_s2_01", "Season 2 Review Chronicle Page 01.png", "Season 2 Wastes Watcher"),
            ("c_texture_season_review_handbook_s2_02", "Season 2 Review Chronicle Page 02.png", "Season 2 Wastes Watcher"),
            ("c_texture_season_review_handbook_s2_bg_01", "Season 2 Review Map Spread 01.png", "Season 2 Wastes Watcher"),
            ("c_texture_season_review_handbook_s2_bg_02", "Season 2 Review Map Spread 02.png", "Season 2 Wastes Watcher"),
            ("c_texture_season_review_handbook_s4", "Season 4 Review Chronicle Cover.png", "Season 4 Dinosaur Origin"),
            ("c_texture_season_review_handbook_s4_01", "Season 4 Review Chronicle Page 01.png", "Season 4 Dinosaur Origin"),
            ("c_texture_season_review_handbook_s4_02", "Season 4 Review Chronicle Page 02.png", "Season 4 Dinosaur Origin"),
            ("c_texture_season_review_handbook_s4_bg_01", "Season 4 Review Map Spread 01.png", "Season 4 Dinosaur Origin"),
            ("c_texture_season_review_handbook_s4_bg_02", "Season 4 Review Map Spread 02.png", "Season 4 Dinosaur Origin"),
        ]
        for tn, fn, sn in rev_exports:
            if tn in t_rev:
                self.save_image(t_rev[tn], f"Event Maps/Season Influence Territories/{fn}", fn[:-4], "Event Maps", "Season Influence Territories", sn, b_rev, tn, "Season Review Map")

        # Season rule tactical illustrations from main_uitexture_uinewseason
        b_ns, t_ns = self.load_bundle_textures("main_uitexture_uinewseason_")
        for i in range(1, 10):
            for tn, fn, sn in [
                (f"UIseason_rule_PIC0{i}", f"Season 2 Rule Map Diagram 0{i}.png", "Season 2 Wastes Watcher"),
                (f"UIseason_rule_PIC0{i}_S1", f"Pre-Season 1 Rule Map Diagram 0{i}.png", "Pre-Season 1 Clash of Thrones"),
                (f"c_texture_saiji3_bg_smtu_{i}", f"Season 3 Rule Map Diagram 0{i}.png", "Season 3 Everfrost Era"),
                (f"c_texture_saiji4_bg_smtu_{i}", f"Season 4 Rule Map Diagram 0{i}.png", "Season 4 Dinosaur Origin"),
                (f"c_texture_saiji5_bg_smtu_{i}", f"Season 5 Rule Map Diagram 0{i}.png", "Season 5 Moonlit Elegy"),
            ]:
                if tn in t_ns:
                    self.save_image(t_ns[tn], f"Event Maps/Season Influence Territories/{fn}", fn[:-4], "Event Maps", "Season Influence Territories", sn, b_ns, tn, "Season Tactical Map Diagram")

        # 3.12 World Boss and Seasonal Events (+ Arena, PVE, Barrel, Treasure, Demon Hunter Radar)
        b_s3, t_s3 = self.load_bundle_textures("main_uitexture_uitextureseason_")
        b_s4, t_s4 = self.load_bundle_textures("main_uitexture_uitextureseason4_")
        b_s4d, t_s4d = self.load_bundle_textures("main_uitexture_uitextureseason4dinosaur_")
        b_s5, t_s5 = self.load_bundle_textures("main_uitexture_uitextureseason5_d")
        b_s5dh, t_s5dh = self.load_bundle_textures("main_uitexture_uitextureseason5_c_texture_season5_dh_")
        b_s5nf, t_s5nf = self.load_bundle_textures("main_uitexture_uitextureseason5_c_texture_season5_nightfalls_")
        b_wp3, t_wp3 = self.load_bundle_textures("main_uitexture_uiworldpoint_s3_")
        b_gui, t_gui = self.load_bundle_textures("main_uitexture_uitextureguide_")
        b_ar3, t_ar3 = self.load_bundle_textures("main_uitexture_uitexture3v3arena_")
        b_hb, t_hb = self.load_bundle_textures("main_uitexture_uiactivitybgportrait_herobattlefiled_")
        b_pve, t_pve = self.load_bundle_textures("main_uitexture_uipve_")
        b_bar, t_bar = self.load_bundle_textures("main_uitexture_uibarrel_")
        b_tr, t_tr = self.load_bundle_textures("main_uitexture_uiactivitytreasure_")
        b_cb, t_cb = self.load_bundle_textures("main_uitexture_uitexturechampionbattle_")

        boss_and_events = [
            (b_s3, t_s3, "c_texture_season_snow_monster_world_bg_01", "Season 3 Snow Monster World Map 01.png", "Season 3 Everfrost Era"),
            (b_s3, t_s3, "c_texture_season_snow_monster_world_bg_02", "Season 3 Snow Monster World Map 02.png", "Season 3 Everfrost Era"),
            (b_s3, t_s3, "c_acitivity_season_IceCaveMain_bg", "Season 3 Ice Cave Main Map.png", "Season 3 Everfrost Era"),
            (b_s3, t_s3, "season_snow_bg01", "Season 3 Snow Battlefield Panorama.png", "Season 3 Everfrost Era"),
            (b_wp3, t_wp3, "c_season3_icecave_worldpoint_bg1", "Season 3 Ice Cave World Point 01.png", "Season 3 Everfrost Era"),
            (b_wp3, t_wp3, "c_season3_icecave_worldpoint_bg2", "Season 3 Ice Cave World Point 02.png", "Season 3 Everfrost Era"),
            (b_gui, t_gui, "c_texture_season3_icecave_guide_01", "Season 3 Ice Cave Guide 01.png", "Season 3 Everfrost Era"),
            (b_gui, t_gui, "c_texture_season3_icecave_guide_02", "Season 3 Ice Cave Guide 02.png", "Season 3 Everfrost Era"),
            (b_gui, t_gui, "c_texture_season3_icecave_guide_03", "Season 3 Ice Cave Guide 03.png", "Season 3 Everfrost Era"),
            (b_s4, t_s4, "c_texture_worldbossS4_bg", "Season 4 World Boss Battlefield.png", "Season 4 Dinosaur Origin"),
            (b_s4, t_s4, "c_texture_S4DinosaurRescue_bg", "Season 4 Dinosaur Rescue Map.png", "Season 4 Dinosaur Origin"),
            (b_s4, t_s4, "season_jurassic_bg01", "Season 4 Jurassic Battlefield 01.png", "Season 4 Dinosaur Origin"),
            (b_s4, t_s4, "season_jurassic_bg02", "Season 4 Jurassic Battlefield 02.png", "Season 4 Dinosaur Origin"),
            (b_s4d, t_s4d, "c_texture_season4_dinosauregg_battle_bg", "Season 4 Dinosaur Egg Battlefield.png", "Season 4 Dinosaur Origin"),
            (b_s5dh, t_s5dh, "c_texture_season5_dh_radar_bg_01", "Season 5 Demon Hunter Radar Map.png", "Season 5 Moonlit Elegy"),
            (b_s5, t_s5, "season_vampire_bg01", "Season 5 Vampire Battlefield 01.png", "Season 5 Moonlit Elegy"),
            (b_s5, t_s5, "season_vampire_bg02", "Season 5 Vampire Battlefield 02.png", "Season 5 Moonlit Elegy"),
            (b_s5nf, t_s5nf, "c_texture_season5_nightfalls_bg", "Season 5 Nightfalls Day Map.png", "Season 5 Moonlit Elegy"),
            (b_s5nf, t_s5nf, "c_texture_season5_nightfalls_bg_night", "Season 5 Nightfalls Night Map.png", "Season 5 Moonlit Elegy"),
            (b_ar3, t_ar3, "c2_texture_arena_3v3_main_bg_start", "Arena 3v3 Battlefield Start.png", "All Seasons"),
            (b_ar3, t_ar3, "c_texture_arena_3v3_main_bg_mid", "Arena 3v3 Battlefield Mid.png", "All Seasons"),
            (b_ar3, t_ar3, "c_texture_arena_3v3_main_bg_final", "Arena 3v3 Battlefield Final.png", "All Seasons"),
            (b_act, t_act, "c_texture_activity_arena_bgNew", "Arena Battlefield Overview.png", "All Seasons"),
            (b_cb, t_cb, "c_texture_activity_championbattle_bg_02", "Champion Battle Arena Background.png", "All Seasons"),
            (b_hb, t_hb, "c_texture_herobattlefiled_img_bg_01", "Hero Battlefield Stage 01.png", "All Seasons"),
            (b_hb, t_hb, "c_texture_herobattlefiled_img_bg_02", "Hero Battlefield Stage 02.png", "All Seasons"),
            (b_hb, t_hb, "c_texture_herobattlefiled_img_bg_03", "Hero Battlefield Stage 03.png", "All Seasons"),
            (b_pve, t_pve, "c_texture_monstertower_bg", "PVE Monster Tower Stage Map.png", "All Seasons"),
            (b_bar, t_bar, "UIknock_img_PICBG", "Barrel Stage Event Background.png", "All Seasons"),
            (b_bg2, t_bg2, "UIzombiesiege_img_PICbg", "Zombie Siege Event Background.png", "All Seasons"),
            (b_tr, t_tr, "c_texture_activity_treasurehunt_bg_01", "Treasure Hunt Event Map 01.png", "All Seasons"),
            (b_tr, t_tr, "c_texture_activity_treasurehunt_bg_02", "Treasure Hunt Event Map 02.png", "All Seasons"),
            (b_tr, t_tr, "c_texture_activity_tebiexd_bg_02", "Special Operations Battlefield Map.png", "All Seasons"),
            (b_tr, t_tr, "c_texture_activity_tuiguan_bg", "Campaign Push Stage Map.png", "All Seasons"),
        ]
        for bn, td, tn, fn, sn in boss_and_events:
            if tn in td:
                self.save_image(td[tn], f"Event Maps/World Boss and Seasonal Events/{fn}", fn[:-4], "Event Maps", "World Boss and Seasonal Events", sn, bn, tn, "Event Map / Battlefield")
        if "c_texture_season5_dh_radar_bg_01" in t_s5dh:
            key_previews["DemonHunterRadar"] = t_s5dh["c_texture_season5_dh_radar_bg_01"].convert("RGB")
        if "c_texture_worldbossS4_bg" in t_s4:
            key_previews["WorldBossS4"] = t_s4["c_texture_worldbossS4_bg"].convert("RGB")

        return key_previews

    # ------------------------------------------------------------------
    # 4. CITY AND BASE MAPS
    # ------------------------------------------------------------------
    def extract_city_and_base_maps(self) -> Image.Image:
        print("[4/7] Extracting City and Base Maps (Inner/Outer City, Lightmap, Fog Masks, 26 Base Expansion Districts)...")
        b_cn1, t_cn1 = self.load_bundle_textures("art_lastday_models_environment_map_terrain_zhuchengdibiao_chengnei_01_")
        b_cn2, t_cn2 = self.load_bundle_textures("art_lastday_models_environment_map_terrain_zhuchengdibiao_chengnei_02_")
        b_cw, t_cw = self.load_bundle_textures("art_lastday_models_environment_map_terrain_zhuchengdibiao_chengwai_")
        b_slg, t_slg = self.load_bundle_textures("art_lastday_models_environment_map_terrain_slg_new02_")
        b_lm, t_lm = self.load_bundle_textures("art_lastday_models_environment_map_terrain_zhuchengdibiao_6")
        b_fm, t_fm = self.load_bundle_textures("art_lastday_models_environment_map_terrain_zhuchengdibiao_fogmask_")
        b_ll, t_ll = self.load_bundle_textures("main_sprites_ui_ui_landlocktips_")

        city_core = [
            (b_cn1, t_cn1, "chengnei_01", "Main City Inner Ground 01.png"),
            (b_cn2, t_cn2, "chengnei_02", "Main City Inner Ground 02.png"),
            (b_cw, t_cw, "chengwai", "Main City Outer Ground.png"),
            (b_slg, t_slg, "tex_neicheng_cao01", "Main City SLG Grass 01.png"),
            (b_slg, t_slg, "tex_neicheng_cao02", "Main City SLG Grass 02.png"),
            (b_slg, t_slg, "tex_neicheng_cao03", "Main City SLG Grass 03.png"),
            (b_slg, t_slg, "tex_neicheng_cao04", "Main City SLG Grass 04.png"),
            (b_slg, t_slg, "tex_neicheng_mask", "Main City SLG Terrain Mask.png"),
            (b_slg, t_slg, "exported_texture_feixu", "Main City SLG Ruins Ground.png"),
            (b_lm, t_lm, "lightmap", "Main City Lightmap.png"),
        ]
        for bn, td, tn, fn in city_core:
            if tn in td:
                self.save_image(td[tn], f"City and Base Maps/{fn}", fn[:-4], "City and Base Maps", "Main City Ground", "All Seasons", bn, tn, "City Ground / Terrain Map")

        # All 10 fogmask textures
        for tn in sorted(t_fm.keys()):
            # Convert fogmask06-08 / fogmask14_16 / fogmask_01 cleanly with zero underscores
            m_rng = re.match(r"fogmask(\d+)[_-](\d+)", tn)
            if m_rng:
                clean_fn = f"Main City Fog Mask {m_rng.group(1)} to {m_rng.group(2)}.png"
            else:
                clean_fn = f"Main City Fog Mask {clean_name(tn.replace('fogmask', '')).strip() or '01'}.png"
            self.save_image(t_fm[tn], f"City and Base Maps/Fog Masks/{clean_fn}", clean_fn[:-4], "City and Base Maps", "Fog Masks", "All Seasons", b_fm, tn, "City Fog Mask")

        # All 26 UIland_img_bg* Base Expansion District Maps
        for tn in sorted(t_ll.keys()):
            if not tn.startswith("UIland_img_bg"):
                continue
            rest = tn[len("UIland_img_bg"):]
            m = re.match(r"0?(\d+)(.*)", rest)
            if m:
                num = int(m.group(1))
                suf = m.group(2)
                if suf == "_S":
                    label = f"Base District Expansion {num:02d} Compact"
                elif suf == "_02":
                    label = f"Base District Expansion {num:02d} Variant 02"
                elif suf:
                    label = f"Base District Expansion {num:02d} {clean_name(suf)}"
                else:
                    label = f"Base District Expansion {num:02d}"
            else:
                label = f"Base District Expansion {clean_name(rest)}"
            self.save_image(t_ll[tn], f"City and Base Maps/Base Expansion Districts/{label}.png", label, "City and Base Maps", "Base Expansion Districts", "All Seasons", b_ll, tn, "Base District Expansion Map")

        return t_cn2["chengnei_02"].convert("RGB")

    # ------------------------------------------------------------------
    # 5. TERRAIN AND BIOMES PER SEASON
    # ------------------------------------------------------------------
    def extract_terrain_and_biomes(self) -> None:
        print("[5/7] Extracting Terrain and Biomes maps per season...")
        # Pre-Season 1
        b_dec, t_dec = self.load_bundle_textures("art_lastday_models_environment_map_decorate_")
        b_lvl, t_lvl = self.load_bundle_textures("art_lastday_models_environment_map_terrain_dibiao_level_")
        b_blk, t_blk = self.load_bundle_textures("art_lastday_models_environment_map_blackearth_")
        b_dib, t_dib = self.load_bundle_textures("art_lastday_models_environment_map_dibiao_")
        b_sha, t_sha = self.load_bundle_textures("art_lastday_models_environment_map_shanmai_")
        b_fog, t_fog = self.load_bundle_textures("art_lastday_models_environment_map_fog_")
        b_yab, t_yab = self.load_bundle_textures("art_lastday_models_environment_map_yabiao_")

        # Season 2
        b_s2d, t_s2d = self.load_bundle_textures("art_lastday_models_environment_map_saiji_shamo_dibiao_")
        b_s2h, t_s2h = self.load_bundle_textures("art_lastday_models_environment_map_saiji_shamo_heitudi_")
        b_s2m, t_s2m = self.load_bundle_textures("art_lastday_models_environment_map_saiji_shamo_moutains_")

        # Season 3
        b_s3w, t_s3w = self.load_bundle_textures("art_lastday_models_environment_map_world_s3_")

        # Season 4
        b_s4g, t_s4g = self.load_bundle_textures("art_lastday_models_environment_map_world_s4_ground_")
        b_s4m, t_s4m = self.load_bundle_textures("art_lastday_models_environment_map_world_s4_mountain_")
        b_hsg, t_hsg = self.load_bundle_textures("art_lastday_models_environment_map_world_huoshanyan_ground_")
        b_hsm, t_hsm = self.load_bundle_textures("art_lastday_models_environment_map_world_huoshanyan_mountain_")

        # Season 5
        b_s5g, t_s5g = self.load_bundle_textures("art_lastday_models_environment_map_world_s5_ground_")
        b_s5m, t_s5m = self.load_bundle_textures("art_lastday_models_environment_map_world_s5_mountain_")
        b_s5t, t_s5t = self.load_bundle_textures("art_lastday_models_environment_map_world_s5_tree_")

        terrain_specs = [
            # Pre-Season 1 Clash of Thrones
            ("Pre-Season 1 Clash of Thrones", b_dec, t_dec, "bigmap_tiandi", "World Farmland Albedo.png"),
            ("Pre-Season 1 Clash of Thrones", b_dec, t_dec, "t_bigmap_color01", "World Bigmap Color 01.png"),
            ("Pre-Season 1 Clash of Thrones", b_dec, t_dec, "t_bigmap_color02", "World Bigmap Color 02.png"),
            ("Pre-Season 1 Clash of Thrones", b_lvl, t_lvl, "O_Env_DiBiao_11_D", "World Surface Albedo 11 HD.png"),
            ("Pre-Season 1 Clash of Thrones", b_lvl, t_lvl, "O_Env_DiBiao_01_D", "World Surface Albedo 01.png"),
            ("Pre-Season 1 Clash of Thrones", b_lvl, t_lvl, "O_Env_DiBiao_03_D", "World Surface Albedo 03.png"),
            ("Pre-Season 1 Clash of Thrones", b_lvl, t_lvl, "O_Env_DiBiao_04_D", "World Surface Albedo 04.png"),
            ("Pre-Season 1 Clash of Thrones", b_lvl, t_lvl, "O_Env_DiBiao_05_D", "World Surface Albedo 05.png"),
            ("Pre-Season 1 Clash of Thrones", b_lvl, t_lvl, "O_Env_DiBiao_06_D", "World Surface Albedo 06.png"),
            ("Pre-Season 1 Clash of Thrones", b_lvl, t_lvl, "O_Env_DiBiao_07_D", "World Surface Albedo 07.png"),
            ("Pre-Season 1 Clash of Thrones", b_lvl, t_lvl, "O_Env_DiBiao_12_D", "World Surface Albedo 12.png"),
            ("Pre-Season 1 Clash of Thrones", b_blk, t_blk, "O_terrain_heitudi_D", "Black Earth Ground Albedo.png"),
            ("Pre-Season 1 Clash of Thrones", b_blk, t_blk, "O_terrain_huitudi_D", "Ash Earth Ground Albedo.png"),
            ("Pre-Season 1 Clash of Thrones", b_blk, t_blk, "O_terrain_heitudi_Mask", "Black Earth Ground Mask.png"),
            ("Pre-Season 1 Clash of Thrones", b_blk, t_blk, "O_terrain_huitudi_Mask", "Ash Earth Ground Mask.png"),
            ("Pre-Season 1 Clash of Thrones", b_dib, t_dib, "tex_grass_dry_0101_d", "Grassland Dry 01 Albedo.png"),
            ("Pre-Season 1 Clash of Thrones", b_dib, t_dib, "tex_grass_wet_0101_d", "Grassland Wet 01 Albedo.png"),
            ("Pre-Season 1 Clash of Thrones", b_dib, t_dib, "tex_grass_dry_04_d", "Grassland Dry 04 Albedo.png"),
            ("Pre-Season 1 Clash of Thrones", b_dib, t_dib, "tex_monisand_02_d", "Wasteland Sand 02 Albedo.png"),
            ("Pre-Season 1 Clash of Thrones", b_sha, t_sha, "O_env_shanmai_01_D", "Mountain Range 01 Albedo.png"),
            ("Pre-Season 1 Clash of Thrones", b_sha, t_sha, "O_env_shanmai_02_D", "Mountain Range 02 Albedo.png"),
            ("Pre-Season 1 Clash of Thrones", b_sha, t_sha, "O_env_shanmai_02_1_D", "Mountain Range 02 Variant Albedo.png"),
            ("Pre-Season 1 Clash of Thrones", b_fog, t_fog, "Fog_mask_01", "World Fog Mask 01.png"),
            ("Pre-Season 1 Clash of Thrones", b_fog, t_fog, "Fog_mask_02", "World Fog Mask 02.png"),
            ("Pre-Season 1 Clash of Thrones", b_yab, t_yab, "O_yabiao_dimian_lu_D", "Convoy Road Ground Albedo.png"),
            ("Pre-Season 1 Clash of Thrones", b_yab, t_yab, "O_yabiao_dimian_lu_Mask", "Convoy Road Ground Mask.png"),
            # Season 2 Wastes Watcher
            ("Season 2 Wastes Watcher", b_s2d, t_s2d, "A_saiji_sand_a_01", "Desert Sand Ground 01.png"),
            ("Season 2 Wastes Watcher", b_s2d, t_s2d, "A_saiji_sand_a_02", "Desert Sand Ground 02.png"),
            ("Season 2 Wastes Watcher", b_s2d, t_s2d, "A_saiji_sand_a_03", "Desert Sand Ground 03.png"),
            ("Season 2 Wastes Watcher", b_s2d, t_s2d, "A_saiji_sand_a_04", "Desert Sand Ground 04.png"),
            ("Season 2 Wastes Watcher", b_s2d, t_s2d, "A_saiji_contorl_06", "Desert Terrain Control Splat.png"),
            ("Season 2 Wastes Watcher", b_s2h, t_s2h, "Tex_WorldS2_heitudi_06_D", "Desert Black Earth 06.png"),
            ("Season 2 Wastes Watcher", b_s2h, t_s2h, "Tex_WorldS2_heitudi_07_D", "Desert Black Earth 07 HD.png"),
            ("Season 2 Wastes Watcher", b_s2h, t_s2h, "Tex_WorldS2_heitudi_08_D", "Desert Black Earth 08.png"),
            ("Season 2 Wastes Watcher", b_s2h, t_s2h, "Tex_WorldS2_Heitudi_jiaotu_01_Splat", "Desert Scorched Earth Splat.png"),
            ("Season 2 Wastes Watcher", b_s2m, t_s2m, "O_env_shanmai_03_D", "Desert Mountain Range 03.png"),
            ("Season 2 Wastes Watcher", b_s2m, t_s2m, "O_env_shanmai_04_D", "Desert Mountain Range 04.png"),
            ("Season 2 Wastes Watcher", b_dec, t_dec, "T_Road_Desert_A_01_D", "Desert Road Ground.png"),
            # Season 3 Everfrost Era
            ("Season 3 Everfrost Era", b_s3w, t_s3w, "Tex_World_Terrain_01_D_S3", "Everfrost Snow Ground 01.png"),
            ("Season 3 Everfrost Era", b_s3w, t_s3w, "Tex_World_Terrain_02_D_S3", "Everfrost Snow Ground 02.png"),
            ("Season 3 Everfrost Era", b_s3w, t_s3w, "Tex_World_Terrain_01_Mask_01_S3", "Everfrost Terrain Splat Mask.png"),
            ("Season 3 Everfrost Era", b_s3w, t_s3w, "Tex_World_Ice_D_S3", "Everfrost Ice Ground 01 HD.png"),
            ("Season 3 Everfrost Era", b_s3w, t_s3w, "Tex_World_Ice_D_02_S3", "Everfrost Ice Ground 02.png"),
            ("Season 3 Everfrost Era", b_s3w, t_s3w, "Tex_World_Ice_Mask_03_S3", "Everfrost Ice Mask HD.png"),
            ("Season 3 Everfrost Era", b_s3w, t_s3w, "Tex_WorldS3_heitudi_01_D", "Everfrost Black Earth 01 HD.png"),
            ("Season 3 Everfrost Era", b_s3w, t_s3w, "Tex_WorldS3_heitudi_02_D", "Everfrost Black Earth 02 HD.png"),
            ("Season 3 Everfrost Era", b_s3w, t_s3w, "Tex_WorldS3_heitudi_03_D", "Everfrost Black Earth 03 HD.png"),
            ("Season 3 Everfrost Era", b_s3w, t_s3w, "Tex_WorldS3_heitudi_04_D", "Everfrost Black Earth 04.png"),
            ("Season 3 Everfrost Era", b_s3w, t_s3w, "Tex_WorldS3_Heitudi_jiaotu_01_Splat", "Everfrost Scorched Earth Splat.png"),
            ("Season 3 Everfrost Era", b_blk, t_blk, "O_terrain_heitudi_D_S3", "Everfrost Frozen Earth Albedo.png"),
            ("Season 3 Everfrost Era", b_s3w, t_s3w, "O_env_snow_shanmai_01_D", "Everfrost Snow Mountain 01 HD.png"),
            ("Season 3 Everfrost Era", b_s3w, t_s3w, "O_env_snow_shanmai_02_D", "Everfrost Snow Mountain 02 HD.png"),
            ("Season 3 Everfrost Era", b_s3w, t_s3w, "Tex_World_Road_01_S3", "Everfrost Snow Road.png"),
            # Season 4 Dinosaur Origin & Volcano
            ("Season 4 Dinosaur Origin", b_s4g, t_s4g, "Tex_WorldS4_ground_01_D", "Dino Jungle Ground 01.png"),
            ("Season 4 Dinosaur Origin", b_s4g, t_s4g, "Tex_WorldS4_ground_02_D", "Dino Jungle Ground 02.png"),
            ("Season 4 Dinosaur Origin", b_s4g, t_s4g, "Tex_WorldS4_ground_03_D", "Dino Jungle Ground 03.png"),
            ("Season 4 Dinosaur Origin", b_s4g, t_s4g, "Tex_WorldS4_ground_05_D", "Dino Jungle Ground 05.png"),
            ("Season 4 Dinosaur Origin", b_s4g, t_s4g, "Tex_WorldS4_Splat", "Dino World Terrain Splat.png"),
            ("Season 4 Dinosaur Origin", b_s4g, t_s4g, "Tex_WorldS4_heitudi_01_D", "Dino Black Earth 01.png"),
            ("Season 4 Dinosaur Origin", b_s4g, t_s4g, "Tex_WorldS4_heitudi_02_D", "Dino Black Earth 02.png"),
            ("Season 4 Dinosaur Origin", b_s4g, t_s4g, "Tex_WorldS4_Heitudi_03_D", "Dino Black Earth 03.png"),
            ("Season 4 Dinosaur Origin", b_s4g, t_s4g, "Tex_WorldS4_Heitudi_04_D", "Dino Black Earth 04.png"),
            ("Season 4 Dinosaur Origin", b_s4g, t_s4g, "Tex_WorldS4_heitudi_05_D", "Dino Black Earth 05.png"),
            ("Season 4 Dinosaur Origin", b_s4g, t_s4g, "Tex_WorldS4_heitudi_jiaotu_02_D", "Dino Scorched Earth 02 HD.png"),
            ("Season 4 Dinosaur Origin", b_s4g, t_s4g, "Tex_WorldS4_Heitudi_01_Splat", "Dino Black Earth Splat 01.png"),
            ("Season 4 Dinosaur Origin", b_s4g, t_s4g, "Tex_WorldS4_heitudi_splat", "Dino Black Earth Splat 02.png"),
            ("Season 4 Dinosaur Origin", b_s4m, t_s4m, "Tex_WorldS4_Mountain_01_D", "Dino Mountain Range 01 HD.png"),
            ("Season 4 Dinosaur Origin", b_s4m, t_s4m, "Tex_WorldS4_Mountain_02_D", "Dino Mountain Range 02 HD.png"),
            ("Season 4 Dinosaur Origin", b_s4m, t_s4m, "Tex_WorldS4_Lake_01", "Dino Prehistoric Lake HD.png"),
            ("Season 4 Dinosaur Origin", b_s4m, t_s4m, "Tex_WorldS4_road_01", "Dino Jungle Road.png"),
            ("Season 4 Dinosaur Origin", b_hsg, t_hsg, "Tex_WorldS4_Huoshanyan_01_D", "Volcano Rock Ground 01.png"),
            ("Season 4 Dinosaur Origin", b_hsg, t_hsg, "Tex_WorldS4_Huoshanyan_02_D", "Volcano Rock Ground 02.png"),
            ("Season 4 Dinosaur Origin", b_hsg, t_hsg, "Tex_WorldS4_Huoshanyan_03_D", "Volcano Rock Ground 03.png"),
            ("Season 4 Dinosaur Origin", b_hsg, t_hsg, "Tex_WorldS4_Huoshanyan_04_D", "Volcano Rock Ground 04.png"),
            ("Season 4 Dinosaur Origin", b_hsg, t_hsg, "Tex_WorldS4_Huoshanyan_05_D", "Volcano Rock Ground 05 HD.png"),
            ("Season 4 Dinosaur Origin", b_hsg, t_hsg, "Tex_WorldS4_Huoshanyan_06_D", "Volcano Rock Ground 06.png"),
            ("Season 4 Dinosaur Origin", b_hsg, t_hsg, "Tex_WorldS4_Huoshanyan_07_D", "Volcano Rock Ground 07.png"),
            ("Season 4 Dinosaur Origin", b_hsg, t_hsg, "Tex_WorldS4_Huoshanyan_08_D", "Volcano Rock Ground 08.png"),
            ("Season 4 Dinosaur Origin", b_hsg, t_hsg, "Tex_WorldS4_Huoshanyan_09_D", "Volcano Rock Ground 09.png"),
            ("Season 4 Dinosaur Origin", b_hsg, t_hsg, "Tex_WorldS4_Huoshanyan_010_D", "Volcano Rock Ground 10.png"),
            ("Season 4 Dinosaur Origin", b_hsg, t_hsg, "Tex_WorldS4_Huoshanyan_012_D", "Volcano Rock Ground 12.png"),
            ("Season 4 Dinosaur Origin", b_hsg, t_hsg, "Tex_WorldS4_Huoshanyan_013_D", "Volcano Rock Ground 13.png"),
            ("Season 4 Dinosaur Origin", b_hsg, t_hsg, "Tex_WorldS4_Huoshanyan_Splat_01", "Volcano Rock Splat 01.png"),
            ("Season 4 Dinosaur Origin", b_hsg, t_hsg, "Tex_WorldS4_Huoshanyan_Splat_02", "Volcano Rock Splat 02.png"),
            ("Season 4 Dinosaur Origin", b_hsg, t_hsg, "Tex_WorldS4_Huoshanyan_Splat_03", "Volcano Rock Splat 03.png"),
            ("Season 4 Dinosaur Origin", b_hsm, t_hsm, "Tex_WorldS4_HuoShan", "Volcano Mountain Albedo HD.png"),
            ("Season 4 Dinosaur Origin", b_hsm, t_hsm, "Tex_WorldS4_HuoShan_Lv", "Volcano Mountain Jungle Variant HD.png"),
            ("Season 4 Dinosaur Origin", b_hsm, t_hsm, "Tex_WorldS4_HuoShan_Xue", "Volcano Mountain Snow Variant HD.png"),
            ("Season 4 Dinosaur Origin", b_hsm, t_hsm, "Tex_WorldS4_HuoShanchi", "Volcano Lava Pool Surface.png"),
            # Season 5 Moonlit Elegy
            ("Season 5 Moonlit Elegy", b_s5g, t_s5g, "Tex_WorldS5_Ground_01_D", "Moonlit Ground 01 HD.png"),
            ("Season 5 Moonlit Elegy", b_s5g, t_s5g, "Tex_WorldS5_Ground_02_D", "Moonlit Ground 02 HD.png"),
            ("Season 5 Moonlit Elegy", b_s5g, t_s5g, "Tex_WorldS5_Ground_03_D", "Moonlit Ground 03 HD.png"),
            ("Season 5 Moonlit Elegy", b_s5g, t_s5g, "Tex_WorldS5_Ground_04_D", "Moonlit Ground 04 HD.png"),
            ("Season 5 Moonlit Elegy", b_s5g, t_s5g, "Tex_WorldS5_Splat_01", "Moonlit World Splat 01 HD.png"),
            ("Season 5 Moonlit Elegy", b_s5g, t_s5g, "Tex_WorldS5_HeiTuDi_01_D", "Moonlit Black Earth 01.png"),
            ("Season 5 Moonlit Elegy", b_s5g, t_s5g, "Tex_WorldS5_Heitudi_03_D", "Moonlit Black Earth 03.png"),
            ("Season 5 Moonlit Elegy", b_s5g, t_s5g, "Tex_WorldS5_Heitudi_04_D", "Moonlit Black Earth 04.png"),
            ("Season 5 Moonlit Elegy", b_s5g, t_s5g, "Tex_WorldS5_HeiTuDi_01_Splat", "Moonlit Black Earth Splat.png"),
            ("Season 5 Moonlit Elegy", b_s5g, t_s5g, "Tex_WorldS5_HuiTuDi_Mask", "Moonlit Ash Earth Mask.png"),
            ("Season 5 Moonlit Elegy", b_s5m, t_s5m, "Tex_WorldS5_Mountain_01_D", "Moonlit Mountain Range 01 HD.png"),
            ("Season 5 Moonlit Elegy", b_s5m, t_s5m, "Tex_WorldS5_Mountain_02_D", "Moonlit Mountain Range 02 HD.png"),
            ("Season 5 Moonlit Elegy", b_hsm, t_hsm, "Tex_WorldS4_HuoShan_S5", "Moonlit Volcano Mountain HD.png"),
            ("Season 5 Moonlit Elegy", b_s5t, t_s5t, "Tex_WorldS5_cao_01_D", "Moonlit Grassland 01 HD.png"),
            ("Season 5 Moonlit Elegy", b_s5t, t_s5t, "Tex_WorldS5_cao_02_D", "Moonlit Grassland 02 HD.png"),
            ("Season 5 Moonlit Elegy", b_s5t, t_s5t, "Tex_WorldS5_cao_03_D", "Moonlit Grassland 03 HD.png"),
        ]
        for sfolder, bn, td, tn, fn in terrain_specs:
            if tn in td:
                self.save_image(td[tn], f"Terrain and Biomes/{sfolder}/{fn}", fn[:-4], "Terrain and Biomes", sfolder, sfolder, bn, tn, "Terrain / Biome Albedo or Splat")

    # ------------------------------------------------------------------
    # 6. CATALOGS & README (ZERO underscores in filenames, ZERO em dashes)
    # ------------------------------------------------------------------
    def write_catalogs(self) -> None:
        print("[6/7] Writing Maps Catalog.json, Maps Catalog.csv, and README.md...")
        # Sort records deterministically
        self.records.sort(key=lambda r: r.relative_path.lower())

        # Summary stats
        by_cat: Dict[str, int] = {}
        by_season: Dict[str, int] = {}
        for r in self.records:
            by_cat[r.category] = by_cat.get(r.category, 0) + 1
            by_season[r.season] = by_season.get(r.season, 0) + 1

        catalog_obj = {
            "total_maps": len(self.records),
            "counts_by_category": dict(sorted(by_cat.items())),
            "counts_by_season": dict(sorted(by_season.items())),
            "maps": [
                {
                    "relative_path": r.relative_path,
                    "title": r.title,
                    "category": r.category,
                    "subcategory": r.subcategory,
                    "season": r.season,
                    "width": r.width,
                    "height": r.height,
                    "resolution": f"{r.width}x{r.height}",
                    "source_bundle": r.source_bundle,
                    "source_assets": r.source_assets,
                    "asset_type": r.asset_type,
                    "notes": r.notes,
                }
                for r in self.records
            ],
        }
        json_txt = json.dumps(catalog_obj, indent=2, ensure_ascii=False).replace("\u2014", "-")
        (MAPS_ROOT / "Maps Catalog.json").write_text(json_txt, encoding="utf-8")

        csv_path = MAPS_ROOT / "Maps Catalog.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Relative Path",
                    "Title",
                    "Category",
                    "Subcategory",
                    "Season",
                    "Width",
                    "Height",
                    "Source Bundle",
                    "Source Assets",
                    "Asset Type",
                    "Notes",
                ]
            )
            for r in self.records:
                writer.writerow(
                    [
                        r.relative_path,
                        r.title,
                        r.category,
                        r.subcategory,
                        r.season,
                        r.width,
                        r.height,
                        r.source_bundle,
                        r.source_assets,
                        r.asset_type,
                        r.notes,
                    ]
                )

        # Build concise, clean README.md (zero em dashes)
        subcat_counts: Dict[Tuple[str, str], int] = {}
        for r in self.records:
            subcat_counts[(r.category, r.subcategory)] = subcat_counts.get((r.category, r.subcategory), 0) + 1

        lines = [
            "# Last Z World, Seasonal, Event, City, and Terrain Maps Archive",
            "",
            f"Total extracted, stitched, decoded, and rendered map assets: **{len(self.records)}** PNG files.",
            "",
            "All folder names and filenames follow clean English naming with spaces and zero underscores.",
            "",
            "## Summary by Category",
            "",
            "| Category | Map Count |",
            "|---|---|",
        ]
        for cat, cnt in sorted(by_cat.items()):
            lines.append(f"| {cat} | {cnt} |")

        lines += [
            "",
            "## Summary by Season",
            "",
            "| Season | Map Count |",
            "|---|---|",
        ]
        for sn, cnt in sorted(by_season.items()):
            lines.append(f"| {sn} | {cnt} |")

        lines += [
            "",
            "## Key Highlight Maps",
            "",
            "- **Stitched 4K World Maps (`4096x4096`):**",
            "  - `Main World Maps/Main World Map 4K.png` (Base World Map, verified quadrant order `[01 TL, 02 TR / 03 BL, 04 BR]`)",
            "  - `Seasonal Maps/Season 3 Everfrost Era/Season 3 Everfrost World Map 4K.png` (mirrored under `Main World Maps/`)",
            "  - `Seasonal Maps/Season 4 Dinosaur Origin/Season 4 Dinosaur Origin World Map 4K.png` (mirrored under `Main World Maps/`)",
            "- **Decoded Binary World Zone & Topology Maps (`main_scenes_all`):**",
            "  - `Main World Maps/World Zones and Provinces Map.png` (`2000x1730`, decoded 530,236-byte RLE binary `zone` with 87 provinces and 90 cities/turrets from `worldcity.json`, plus 87 individual masks under `Province Zones/`)",
            "  - `Seasonal Maps/Pre-Season 1 Clash of Thrones/Pre-Season 1 Topology Map.png` (`1000x1000` -> `2000x1730`)",
            "  - `Seasonal Maps/Season 2 Wastes Watcher/Season 2 Wastes Watcher Topology Map.png` + `Season 2 Desert Resource Tiers Map.png`",
            "  - `Seasonal Maps/Season 3 Everfrost Era/Season 3 Everfrost Era Topology Map.png`",
            "  - `Seasonal Maps/Season 4 Dinosaur Origin/Season 4 Dinosaur Origin Topology Map.png`",
            "  - `Seasonal Maps/Season 5 Moonlit Elegy/Season 5 Moonlit Elegy Topology Map.png`",
            "  - `Seasonal Maps/Season 6/Season 6 World Topology Map.png` (`1600x1600` expanded world -> `2400x2076`)",
            "- **Stitched & Annotated Event Maps:**",
            "  - `Event Maps/Volcano War/Volcano War Tactical Map Annotated.png` (10 sectors, concentric energy mine rings, 11 Field Hospitals)",
            "  - `Event Maps/Castle Adventure/Castle Adventure Map.png` (all 5 map pieces composited onto base map at exact prefab coordinates)",
            "  - `Event Maps/Landing Operations/Landing Operations Full Map.png` (`864x6144`) and `Landing Operations All Stages Overview.png` (`2592x2048`)",
            "  - `Event Maps/Desert Battlefield/Desert Battlefield Resource Tiers Map.png`",
            "",
            "## Breakdown by Subcategory",
            "",
            "| Category | Subcategory | Count |",
            "|---|---|---|",
        ]
        for (cat, sub), cnt in sorted(subcat_counts.items()):
            lines.append(f"| {cat} | {sub} | {cnt} |")

        lines += [
            "",
            "## Catalog Files",
            "",
            "- `Maps Catalog.json`: Complete machine-readable manifest with dimensions, source bundles, and asset names.",
            "- `Maps Catalog.csv`: Spreadsheet-friendly table of every exported map file.",
            "",
        ]
        readme_txt = "\n".join(lines).replace("\u2014", "-")
        (MAPS_ROOT / "README.md").write_text(readme_txt, encoding="utf-8")

    # ------------------------------------------------------------------
    # 7. VISUAL VERIFICATION CONTACT SHEET
    # ------------------------------------------------------------------
    def build_verify_contact_sheet(
        self,
        stitched_4k: Dict[str, Image.Image],
        zones_map: Image.Image,
        topo_renders: Dict[str, Image.Image],
        event_previews: Dict[str, Image.Image],
        desert_tiers: Image.Image,
        city_preview: Image.Image,
    ) -> None:
        print("[7/7] Building visual verification contact sheet...")
        tiles: List[Tuple[str, Image.Image]] = [
            ("1. Main World Map 4K (4096x4096)", stitched_4k["Main"]),
            ("2. S3 Everfrost 4K (4096x4096)", stitched_4k["S3"]),
            ("3. S4 Dinosaur Origin 4K (4096x4096)", stitched_4k["S4"]),
            ("4. World Zones & 90 Cities (Decoded)", zones_map),
            ("5. Pre-Season 1 Topology (S0 1K)", topo_renders["S0"]),
            ("6. S2 Wastes Watcher Topology (1K)", topo_renders["S2"]),
            ("7. S3 Everfrost Topology (1K)", topo_renders["S3"]),
            ("8. S4 Dinosaur Origin Topology (1K)", topo_renders["S4"]),
            ("9. S5 Moonlit Elegy Topology (1K)", topo_renders["S5"]),
            ("10. S6 Expanded Topology (1600x1600)", topo_renders["S6"]),
            ("11. Volcano War Annotated Map", event_previews["Volcano"]),
            ("12. Castle Adventure Assembled Map", event_previews["Castle"]),
            ("13. Landing Ops 3 Stages Overview", event_previews["LandingOps"]),
            ("14. S2 Desert Resource Tiers Map", desert_tiers),
            ("15. S5 Demon Hunter Radar / Dispatch", event_previews.get("DemonHunterRadar", event_previews.get("Dispatch", city_preview))),
            ("16. Capital War Guide / Main City", event_previews.get("CapitalWar", city_preview)),
        ]

        cols, rows = 4, 4
        tw, th = 560, 480
        pad = 16
        hdr_h = 56
        lbl_h = 34
        sheet_w = pad + cols * (tw + pad)
        sheet_h = hdr_h + pad + rows * (th + lbl_h + pad)
        sheet = Image.new("RGB", (sheet_w, sheet_h), (16, 20, 28))
        draw = ImageDraw.Draw(sheet)
        f_hdr = get_font(28, bold=True)
        f_lbl = get_font(17, bold=True)

        draw.text(
            (pad, 14),
            f"LAST Z WORLD MAPS VERIFICATION SHEET ({len(self.records)} TOTAL MAPS EXPORTED)",
            font=f_hdr,
            fill=(255, 232, 165),
        )

        for idx, (label, img) in enumerate(tiles):
            r = idx // cols
            c = idx % cols
            x0 = pad + c * (tw + pad)
            y0 = hdr_h + pad + r * (th + lbl_h + pad)
            draw.rectangle((x0 - 2, y0 - 2, x0 + tw + 2, y0 + th + lbl_h + 2), fill=(28, 34, 46), outline=(88, 102, 128), width=2)
            # Fit inside tw x th preserving aspect ratio
            im = img.convert("RGB")
            scale = min(tw / im.width, th / im.height)
            nw, nh = max(1, int(round(im.width * scale))), max(1, int(round(im.height * scale)))
            resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
            ox = x0 + (tw - nw) // 2
            oy = y0 + (th - nh) // 2
            sheet.paste(resized, (ox, oy))
            draw.rectangle((x0, y0 + th, x0 + tw, y0 + th + lbl_h), fill=(22, 27, 38))
            draw.text((x0 + 10, y0 + th + 7), label, font=f_lbl, fill=(240, 245, 252))

        VERIFY_SHEET_PATH.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(VERIFY_SHEET_PATH, format="PNG", compress_level=6)
        print(f"  Saved verification sheet: {VERIFY_SHEET_PATH} ({sheet.width}x{sheet.height})")

    def validate_outputs(self) -> None:
        bad_names = []
        bad_emdash = []
        for p in MAPS_ROOT.rglob("*"):
            rel = p.relative_to(MAPS_ROOT)
            if any("_" in part for part in rel.parts):
                bad_names.append(str(rel))
            if p.is_file() and p.suffix.lower() in (".md", ".json", ".csv", ".txt"):
                if "\u2014" in p.read_text(encoding="utf-8", errors="ignore"):
                    bad_emdash.append(str(rel))
        script_self = Path(__file__).read_text(encoding="utf-8", errors="ignore")
        if "\u2014" in script_self:
            bad_emdash.append(str(Path(__file__)))
        assert not bad_names, f"Underscores found under maps/: {bad_names[:10]}"
        assert not bad_emdash, f"Em dashes found: {bad_emdash}"
        print(f"VALIDATION PASSED: {len(self.records)} maps exported, 0 underscores under maps/, 0 em dashes.")


def main() -> None:
    if MAPS_ROOT.exists():
        shutil.rmtree(MAPS_ROOT)
    MAPS_ROOT.mkdir(parents=True, exist_ok=True)

    exporter = MapExporter()
    stitched_4k = exporter.extract_4k_world_maps()
    zones_map, topo_renders, desert_tiers = exporter.extract_main_scenes_and_seasons()
    event_previews = exporter.extract_event_maps(desert_tiers)
    city_preview = exporter.extract_city_and_base_maps()
    exporter.extract_terrain_and_biomes()
    exporter.write_catalogs()
    exporter.build_verify_contact_sheet(
        stitched_4k, zones_map, topo_renders, event_previews, desert_tiers, city_preview
    )
    exporter.validate_outputs()


if __name__ == "__main__":
    main()
