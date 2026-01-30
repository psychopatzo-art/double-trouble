# pages/4_Preview.py

import streamlit as st
from pathlib import Path
from PIL import Image

from core.storage import load_project
from core.preview_render import render_preview

BASE = Path(__file__).resolve().parents[1]

st.header("🎛️ Preview (Layered Composite)")

pid = st.session_state.get("active_project_id")
if not pid:
    st.warning("Select or create a project in the sidebar first.")
    st.stop()

project = load_project(BASE, pid)
cfg = project.preview_config or {}
TW, TH = cfg.get("canvas", {}).get("w", 1440), cfg.get("canvas", {}).get("h", 810)

st.subheader(project.title)
st.caption(f"Orientation: {project.orientation} | Canvas: {TW}×{TH}")

def latest(category: str):
    for a in project.assets:
        if a.category == category:
            p = BASE / "data" / "projects" / pid / a.path
            if p.exists():
                return Image.open(p)
    return None

bg = latest("Background")
reel_bg = latest("ReelBackground")
frame = latest("Frame")

reels = project.reels
rows = project.rows

st.caption("Preview composes: Background → Reel BG → Symbols grid → Frame overlay.")

# Build a simple symbols grid from available symbols (repeat if not enough)
symbol_imgs = []
for a in project.assets:
    if a.category == "Symbols":
        p = BASE / "data" / "projects" / pid / a.path
        if p.exists():
            symbol_imgs.append(Image.open(p))

grid = None
if symbol_imgs:
    grid = []
    k = 0
    for r in range(rows):
        row_imgs = []
        for c in range(reels):
            row_imgs.append(symbol_imgs[k % len(symbol_imgs)])
            k += 1
        grid.append(row_imgs)

rw = cfg.get("reel_window", {"x": 400, "y": 170, "w": 640, "h": 420})
canvas = (TW, TH)
reel_xywh = (rw["x"], rw["y"], rw["w"], rw["h"])

out = render_preview(
    canvas_size=canvas,
    background=bg,
    reel_bg=reel_bg,
    frame=frame,
    symbols_grid=grid,
    reel_window_xywh=reel_xywh,
)

st.image(out, use_container_width=True)

with st.expander("Preview config (JSON)"):
    st.json(cfg)
