import argparse
from pathlib import Path

from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Minimal CLI that loads images and writes placeholder outputs."
    )
    parser.add_argument("--fg", required=True, help="Path to foreground image.")
    parser.add_argument("--bg", required=True, help="Path to background image.")
    parser.add_argument(
        "--out-dir",
        default="outputs",
        help="Directory to write composite.png and shadow_only.png.",
    )
    return parser.parse_args()


def ensure_out_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    args = parse_args()
    fg_path = Path(args.fg)
    bg_path = Path(args.bg)
    out_dir = Path(args.out_dir)

    ensure_out_dir(out_dir)

    # Load inputs to confirm paths are valid; outputs are placeholders for now.
    fg = Image.open(fg_path).convert("RGBA")
    bg = Image.open(bg_path).convert("RGBA")

    # Placeholder shadow: fully transparent image matching background size.
    shadow_only = Image.new("RGBA", bg.size, (0, 0, 0, 0))

    # Placeholder composite: background only.
    composite = bg.copy()

    shadow_only.save(out_dir / "shadow_only.png")
    composite.save(out_dir / "composite.png")

    # Save a quick debug for the mask step later.
    fg.save(out_dir / "fg_debug.png")


if __name__ == "__main__":
    main()
