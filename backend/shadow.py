import math
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter


def load_mask(path: Path) -> Image.Image:
    mask_img = Image.open(path)
    if mask_img.mode in ("L", "1"):
        return mask_img.convert("L")
    if mask_img.mode in ("LA", "RGBA"):
        return mask_img.split()[-1]
    return mask_img.convert("L")


def load_mask_from_image(image: Image.Image) -> Image.Image:
    if image.mode in ("L", "1"):
        return image.convert("L")
    if image.mode in ("LA", "RGBA"):
        return image.split()[-1]
    return image.convert("L")


def derive_mask_from_fg(fg: Image.Image) -> Image.Image:
    if fg.mode in ("LA", "RGBA"):
        return fg.split()[-1]
    raise ValueError("Foreground has no alpha channel; provide --mask.")


def project_shadow(
    mask: Image.Image, angle: float, elevation: float, scale: float, max_shear: float
) -> Image.Image:
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


def compute_shadow_extent(size: tuple[int, int], y0: int, dx: float, dy: float) -> float:
    w, h = size
    corners = [
        (0, 0),
        (w - 1, 0),
        (0, h - 1),
        (w - 1, h - 1),
    ]
    max_t = 1.0
    for x, y in corners:
        t = dx * x + dy * (y - y0)
        if t > max_t:
            max_t = t
    return max_t


def build_fade_mask(
    size: tuple[int, int], y0: int, dx: float, dy: float, max_distance: float
) -> Image.Image:
    w, h = size
    max_distance = max(max_distance, 1.0)
    data: list[int] = []
    for y in range(h):
        y_term = dy * (y - y0)
        for x in range(w):
            t = dx * x + y_term
            if t <= 0:
                alpha = 255
            elif t >= max_distance:
                alpha = 0
            else:
                alpha = int(255 * (1 - (t / max_distance)))
            data.append(alpha)
    fade = Image.new("L", size)
    fade.putdata(data)
    return fade


def build_shadow_alpha(
    mask: Image.Image,
    angle: float,
    elevation: float,
    shadow_scale: float,
    max_shear: float,
    contact_fade: float,
    soft_fade: float,
) -> Image.Image:
    shadow_mask = project_shadow(mask, angle, elevation, shadow_scale, max_shear)

    bbox = mask.getbbox()
    if bbox is None:
        raise ValueError("Mask is empty; no non-zero pixels found.")
    y0 = bbox[3]
    angle_rad = math.radians(angle)
    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)

    # Reverse the fade direction so near-contact stays darker and far fades out.
    fade_dx = -dx
    fade_dy = -dy

    max_extent = compute_shadow_extent(mask.size, y0, fade_dx, fade_dy)
    contact_distance = max_extent * max(contact_fade, 0.01)
    soft_distance = max_extent * max(soft_fade, 0.01)

    contact_fade_mask = build_fade_mask(mask.size, y0, fade_dx, fade_dy, contact_distance)
    soft_fade_mask = build_fade_mask(mask.size, y0, fade_dx, fade_dy, soft_distance)

    contact_shadow = shadow_mask.filter(ImageFilter.GaussianBlur(2))
    contact_shadow = ImageChops.multiply(contact_shadow, contact_fade_mask)

    soft_shadow = shadow_mask.filter(ImageFilter.GaussianBlur(12))
    soft_shadow = ImageChops.multiply(soft_shadow, soft_fade_mask)

    return ImageChops.lighter(contact_shadow, soft_shadow)


def composite_shadow(
    fg: Image.Image,
    bg: Image.Image,
    mask: Image.Image,
    angle: float,
    elevation: float,
    shadow_scale: float,
    max_shear: float,
    contact_fade: float,
    soft_fade: float,
) -> tuple[Image.Image, Image.Image]:
    shadow_alpha = build_shadow_alpha(
        mask,
        angle,
        elevation,
        shadow_scale,
        max_shear,
        contact_fade,
        soft_fade,
    )

    shadow_only = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    shadow_only.putalpha(shadow_alpha)

    fg_with_alpha = fg.copy()
    fg_with_alpha.putalpha(mask)

    composite = Image.alpha_composite(bg, shadow_only)
    composite = Image.alpha_composite(composite, fg_with_alpha)

    return shadow_only, composite
