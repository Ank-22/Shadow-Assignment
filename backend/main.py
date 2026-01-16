import argparse
import sys
from pathlib import Path

from PIL import Image

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shadow import composite_shadow, derive_mask_from_fg, load_mask


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CLI that loads images, a mask, and writes a projected shadow."
    )
    parser.add_argument("--fg", required=True, help="Path to foreground image.")
    parser.add_argument("--bg", required=True, help="Path to background image.")
    parser.add_argument("--mask", help="Path to foreground mask.")
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
    parser.add_argument(
        "--contact-fade",
        type=float,
        default=0.15,
        help="Fraction of shadow length used for sharp contact fade.",
    )
    parser.add_argument(
        "--soft-fade",
        type=float,
        default=1.0,
        help="Fraction of shadow length used for soft falloff.",
    )
    parser.add_argument(
        "--contact-blur",
        type=float,
        default=2.0,
        help="Base blur radius for contact shadow.",
    )
    parser.add_argument(
        "--blur-ratio",
        type=float,
        default=6.0,
        help="Multiplier for soft shadow blur relative to contact blur.",
    )
    return parser.parse_args()


def ensure_out_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()
    fg_path = Path(args.fg)
    bg_path = Path(args.bg)
    mask_path = Path(args.mask) if args.mask else None
    out_dir = Path(args.out_dir)

    ensure_out_dir(out_dir)

    fg = Image.open(fg_path).convert("RGBA")
    bg = Image.open(bg_path).convert("RGBA")
    if mask_path:
        mask = load_mask(mask_path)
    else:
        mask = derive_mask_from_fg(fg)

    if fg.size != mask.size:
        raise ValueError("Foreground and mask sizes do not match.")
    if bg.size != fg.size:
        raise ValueError("Background and foreground sizes do not match.")

    shadow_only, composite = composite_shadow(
        fg=fg,
        bg=bg,
        mask=mask,
        angle=args.angle,
        elevation=args.elevation,
        shadow_scale=args.shadow_scale,
        max_shear=args.max_shear,
        contact_fade=args.contact_fade,
        soft_fade=args.soft_fade,
        contact_blur=args.contact_blur,
        blur_ratio=args.blur_ratio,
    )

    shadow_only.save(out_dir / "shadow_only.png")
    composite.save(out_dir / "composite.png")
    mask.save(out_dir / "mask_debug.png")


if __name__ == "__main__":
    main()
