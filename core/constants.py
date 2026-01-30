ASSET_CATEGORIES = [
    "Mockups",
    "Background",
    "ReelBackground",
    "Frame",
    "Symbols",
    "BonusGames",
    "FreeSpins",
    "Splashes",
    "Characters",
    "UI",
    "UploadedAssets",
]

DEFAULT_REELS = 5
DEFAULT_ROWS = 3

LANDSCAPE = {"w": 1440, "h": 810}
PORTRAIT  = {"w": 810,  "h": 1440}

def make_default_preview_config(orientation: str = "Landscape"):
    if orientation == "Portrait":
        cw, ch = 810, 1440
        # reel window примерно по-нагоре и по-тясно
        rw = {"x": 185, "y": 360, "w": 440, "h": 720}
    else:
        cw, ch = 1440, 810
        rw = {"x": 400, "y": 170, "w": 640, "h": 420}

    return {
        "orientation": orientation,
        "canvas": {"w": cw, "h": ch},
        "reel_window": rw,
        "frame": rw,
    }

# Default preview layout (percentages within preview canvas)
DEFAULT_PREVIEW_CONFIG = {
    "canvas": {"w": 1280, "h": 720},
    "background": {"x": 0, "y": 0, "w": 1280, "h": 720},
    "reel_window": {"x": 320, "y": 150, "w": 640, "h": 420},  # visible reels region
    "frame": {"x": 320, "y": 150, "w": 640, "h": 420},       # frame overlay aligned to reel_window
}
