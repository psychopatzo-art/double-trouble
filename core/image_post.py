from PIL import Image

def to_canvas(img: Image.Image, target_w: int, target_h: int, mode: str = "cover") -> Image.Image:
    """
    mode="cover": fills canvas, crops center if needed (best for backgrounds/mockups)
    mode="contain": fits entire image inside canvas with padding (best for frames/panels)
    """
    img = img.convert("RGBA")
    iw, ih = img.size
    tw, th = target_w, target_h

    if mode == "cover":
        scale = max(tw / iw, th / ih)
    else:
        scale = min(tw / iw, th / ih)

    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)

    out = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    x = (tw - nw) // 2
    y = (th - nh) // 2

    if mode == "cover":
        cx1 = max(0, -x)
        cy1 = max(0, -y)
        cx2 = cx1 + tw
        cy2 = cy1 + th
        cropped = resized.crop((cx1, cy1, cx2, cy2))
        out.alpha_composite(cropped, (0, 0))
    else:
        out.alpha_composite(resized, (x, y))

    return out

def to_exact_symbol_size(img: Image.Image, w: int = 158, h: int = 178) -> Image.Image:
    img = img.convert("RGBA")
    scale = min(w / img.width, h / img.height)
    new_size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
    resized = img.resize(new_size, Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = (w - resized.width) // 2
    y = (h - resized.height) // 2
    canvas.alpha_composite(resized, (x, y))
    return canvas
