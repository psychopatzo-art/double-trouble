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

# Default preview layout (percentages within preview canvas)
DEFAULT_PREVIEW_CONFIG = {
    "canvas": {"w": 1280, "h": 720},
    "background": {"x": 0, "y": 0, "w": 1280, "h": 720},
    "reel_window": {"x": 320, "y": 150, "w": 640, "h": 420},  # visible reels region
    "frame": {"x": 320, "y": 150, "w": 640, "h": 420},       # frame overlay aligned to reel_window
}
