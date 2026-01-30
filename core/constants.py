# core/constants.py

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
PORTRAIT = {"w": 810, "h": 1440}


def make_default_preview_config(orientation: str = "Landscape"):
    """
    Defines a starting layout for preview composition.
    We can tune reel_window numbers later based on your exact safe zones.
    """
    if orientation == "Portrait":
        cw, ch = PORTRAIT["w"], PORTRAIT["h"]
        # Reel window: centered-ish, taller
        reel_window = {"x": 185, "y": 360, "w": 440, "h": 720}
    else:
        cw, ch = LANDSCAPE["w"], LANDSCAPE["h"]
        # Reel window: centered, classic landscape
        reel_window = {"x": 400, "y": 170, "w": 640, "h": 420}

    return {
        "orientation": orientation,
        "canvas": {"w": cw, "h": ch},
        "reel_window": reel_window,
        "frame": reel_window,
    }
