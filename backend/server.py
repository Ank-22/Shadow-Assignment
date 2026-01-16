import base64
import io
import sys
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from shadow import composite_shadow, derive_mask_from_fg, load_mask_from_image

FRONTEND_DIR = ROOT_DIR.parent / "frontend"

app = Flask(__name__)


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/styles.css")
def styles():
    return send_from_directory(FRONTEND_DIR, "styles.css")


@app.get("/app.js")
def app_js():
    return send_from_directory(FRONTEND_DIR, "app.js")


def _parse_float(name: str, default: float) -> float:
    value = request.form.get(name)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


@app.post("/api/compose")
def compose():
    fg_file = request.files.get("fg")
    bg_file = request.files.get("bg")
    mask_file = request.files.get("mask")
    if not fg_file or not bg_file:
        return jsonify({"error": "fg and bg are required"}), 400

    fg = Image.open(fg_file.stream).convert("RGBA")
    bg = Image.open(bg_file.stream).convert("RGBA")
    try:
        if mask_file:
            mask = Image.open(mask_file.stream)
            mask = load_mask_from_image(mask)
        else:
            mask = derive_mask_from_fg(fg)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if fg.size != mask.size or bg.size != fg.size:
        return jsonify({"error": "fg, bg, and mask must have matching dimensions"}), 400

    shadow_only, composite = composite_shadow(
        fg=fg,
        bg=bg,
        mask=mask,
        angle=_parse_float("angle", 45.0),
        elevation=_parse_float("elevation", 45.0),
        shadow_scale=_parse_float("shadow_scale", 1.0),
        max_shear=_parse_float("max_shear", 5.0),
        contact_fade=_parse_float("contact_fade", 0.15),
        soft_fade=_parse_float("soft_fade", 1.0),
    )

    composite_bytes = io.BytesIO()
    shadow_bytes = io.BytesIO()
    composite.save(composite_bytes, format="PNG")
    shadow_only.save(shadow_bytes, format="PNG")

    return jsonify(
        {
            "composite": base64.b64encode(composite_bytes.getvalue()).decode("ascii"),
            "shadow_only": base64.b64encode(shadow_bytes.getvalue()).decode("ascii"),
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=8000)
