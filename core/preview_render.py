from __future__ import annotations
from PIL import Image
from typing import Optional, Tuple, List

def _fit(img: Image.Image, w: int, h: int) -> Image.Image:
    return img.resize((w, h), Image.Resampling.LANCZOS)

def render_preview(
    canvas_size: Tuple[int,int],
    background: Optional[Image.Image]=None,
    reel_bg: Optional[Image.Image]=None,
    frame: Optional[Image.Image]=None,
    symbols_grid: Optional[List[List[Image.Image]]]=None,  # rows x reels
    reel_window_xywh: Tuple[int,int,int,int]=(320,150,640,420),
) -> Image.Image:
    cw, ch = canvas_size
    out = Image.new("RGBA", (cw, ch), (0,0,0,0))

    if background:
        out.alpha_composite(_fit(background.convert("RGBA"), cw, ch), (0,0))

    x, y, w, h = reel_window_xywh

    if reel_bg:
        out.alpha_composite(_fit(reel_bg.convert("RGBA"), w, h), (x,y))

    if symbols_grid:
        rows = len(symbols_grid)
        reels = len(symbols_grid[0]) if rows else 0
        if rows and reels:
            cell_w = w // reels
            cell_h = h // rows
            for r in range(rows):
                for c in range(reels):
                    sym = symbols_grid[r][c].convert("RGBA")
                    sym_fit = _fit(sym, cell_w, cell_h)
                    out.alpha_composite(sym_fit, (x + c*cell_w, y + r*cell_h))

    if frame:
        out.alpha_composite(_fit(frame.convert("RGBA"), w, h), (x,y))

    return out
