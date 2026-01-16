import argparse
import math
from pathlib import Path

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI that loads images, a mask, and writes a projected shadow."
    )
    parser.add_argument("--fg", required=True, help="Path to foreground image.")
    parser.add_argument("--bg", required=True, help="Path to background image.")
    parser.add_argument("--mask", required=True, help="Path to foreground mask.")
    parser.add_argument(
        "--out-dir",
        default="outputs",
        help="Directory to write composite.png and shadow_only.png.",
    )
    parser.add_argument(
        "--angle",
        type=float,
        default=45.0,
        help="Shadow direction angle in degrees. 0=right, 90=down.",
    )
    parser.add_argument(
        "--elevation",
        type=float,
        default=45.0,
        help="Light elevation in degrees. Higher = shorter shadow.",
    )
    parser.add_argument(
        "--shadow-scale",
        type=float,
        default=1.0,
        help="Multiplier for shadow length relative to elevation.",
    )
    parser.add_argument(
        "--max-shear",
        type=float,
        default=5.0,
        help="Clamp for extreme low-elevation shadows.",
    )
    return parser.parse_args()


def ensure_out_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_mask(path: Path) -> Image.Image:
    mask_img = Image.open(path)
    if mask_img.mode in ("L", "1"):
        return mask_img.convert("L")
    if mask_img.mode in ("LA", "RGBA"):
        return mask_img.split()[-1]
    return mask_img.convert("L")


def project_shadow(mask: Image.Image, angle: float, elevation: float, scale: float, max_shear: float) -> Image.Image:
    bbox = mask.getbbox()
    if bbox is None:
        raise ValueError("Mask is empty; no non-zero pixels found.")

    y0 = bbox[3]
    angle_rad = math.radians(angle)
    elev_rad = math.radians(elevation)

    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)

    tan_elev = max(math.tan(elev_rad), 1e-3)
    k = min(scale / tan_elev, max_shear)

    denom = 1 + k * dy
    if dy != 0 and abs(denom) < 0.2:
        k = (0.2 - 1) / dy
        denom = 1 + k * dy

    # Affine matrix for output->input mapping.
    a = 1
    b = -k * dx / denom
    c = k * dx * y0 / denom
    d = 0
    e = 1 / denom
    f = k * dy * y0 / denom

    return mask.transform(
        mask.size,
        Image.AFFINE,
        (a, b, c, d, e, f),
        resample=Image.BICUBIC,
        fillcolor=0,
    )


def main() -> None:
    args = parse_args()
    fg_path = Path(args.fg)
    bg_path = Path(args.bg)
    mask_path = Path(args.mask)
    out_dir = Path(args.out_dir)

    ensure_out_dir(out_dir)

    fg = Image.open(fg_path).convert("RGBA")
    bg = Image.open(bg_path).convert("RGBA")
    mask = load_mask(mask_path)

    if fg.size != mask.size:
        raise ValueError("Foreground and mask sizes do not match.")
    if bg.size != fg.size:
        raise ValueError("Background and foreground sizes do not match.")

    shadow_mask = project_shadow(
        mask, args.angle, args.elevation, args.shadow_scale, args.max_shear
    )
    shadow_only = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    shadow_only.putalpha(shadow_mask)

    # Apply mask to foreground for clean compositing.
    fg_with_alpha = fg.copy()
    fg_with_alpha.putalpha(mask)

    composite = Image.alpha_composite(bg, shadow_only)
    composite = Image.alpha_composite(composite, fg_with_alpha)

    shadow_only.save(out_dir / "shadow_only.png")
    composite.save(out_dir / "composite.png")
    mask.save(out_dir / "mask_debug.png")


if __name__ == "__main__":
    main()
