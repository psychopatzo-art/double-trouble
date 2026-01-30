# pages/6_Extract.py

import streamlit as st
from pathlib import Path
from PIL import Image
import time

from core.storage import load_project, add_asset, ensure_project_dirs
from core.models import Asset
from core.constants import ASSET_CATEGORIES
from core.providers import PROVIDERS
from core.image_post import to_canvas, to_exact_symbol_size

BASE = Path(__file__).resolve().parents[1]

st.header("🧩 Extract (Generate Individual Assets)")

pid = st.session_state.get("active_project_id")
if not pid:
    st.warning("Select or create a project in the sidebar first.")
    st.stop()

project = load_project(BASE, pid)
ensure_project_dirs(BASE, pid, ASSET_CATEGORIES)

cfg = project.preview_config or {}
TW, TH = cfg.get("canvas", {}).get("w", 1440), cfg.get("canvas", {}).get("h", 810)

st.subheader(project.title)
st.caption(f"Orientation: {project.orientation} | Canvas: {TW}×{TH}")

# Find latest mockup concept
mockup_asset = None
for a in project.assets:
    if a.category == "Mockups":
        mockup_asset = a
        break

if not mockup_asset:
    st.warning("No Mockup concept found. Go to Generator → create a Mockup first.")
    st.stop()

mockup_path = BASE / "data" / "projects" / pid / mockup_asset.path
if mockup_path.exists():
    st.image(Image.open(mockup_path), caption=f"Selected concept: {mockup_asset.name}", use_container_width=True)
else:
    st.warning("Mockup file missing on disk, but listed in project.json.")

st.divider()

symbols_count = st.slider("How many symbols to generate", min_value=6, max_value=14, value=10, step=1)

colA, colB = st.columns([2, 1])

with colB:
    # Provider/model/size
    if st.session_state.provider == "Gemini":
        model = st.selectbox("Model", ["imagen-4.0-generate-001"], index=0)
        size = st.selectbox("Size", ["1K", "2K"], index=1)
    else:
        model = st.selectbox("Model", ["gpt-image-1.5", "gpt-image-1", "dall-e-3"], index=1)
        default_size = "1792x1024" if project.orientation == "Landscape" else "1024x1792"
        size = st.selectbox("Size", ["1024x1024", "1792x1024", "1024x1792"], index=["1024x1024","1792x1024","1024x1792"].index(default_size))

with colA:
    st.write("This generates **separate assets** that match the approved concept style.")
    run = st.button("Extract assets now", type="primary", use_container_width=True)

def _save_images(category: str, base_name: str, prompt: str, images):
    pdir = BASE / "data" / "projects" / pid / "assets" / category
    ts = int(time.time())
    saved = []

    for idx, img in enumerate(images, start=1):
        if category == "Background":
            img = to_canvas(img, TW, TH, mode="cover")
        elif category in ["ReelBackground", "Frame", "UI", "Splashes", "BonusGames", "FreeSpins", "Characters"]:
            img = to_canvas(img, TW, TH, mode="contain")
        elif category == "Symbols":
            img = to_exact_symbol_size(img, 158, 178)

        fn = f"{base_name}-{ts}-{idx}.png"
        fpath = pdir / fn
        img.save(fpath, "PNG")

        rel = str(fpath.relative_to(BASE / "data" / "projects" / pid))
        asset = Asset.new(
            category=category,
            name=fn,
            prompt=prompt,
            provider=st.session_state.provider,
            model=model,
            path=rel,
            meta={"size": size, "canvas": f"{TW}x{TH}", "orientation": project.orientation},
        )
        add_asset(BASE, project, asset)
        saved.append(str(fpath))
    return saved

if run:
    provider_key = st.session_state.provider
    api_key = (st.session_state.api_keys.get(provider_key) or "").strip()
    if not api_key:
        st.error("Missing API key for selected provider.")
        st.stop()

    provider = PROVIDERS["Gemini" if provider_key == "Gemini" else "OpenAI"]

    base = (
        f"{project.theme}. {project.style_lock}\n\n"
        "Match the exact style, materials, palette, lighting, and rendering quality of the approved concept.\n"
        "No logos, no text.\n"
    )

    prompts = {
        "Background": base + "Generate the BACKGROUND ONLY (no reels, no frame, no symbols). Full scene, high quality.",
        "ReelBackground": base + "Generate the REEL BACKGROUND / reel window panel ONLY (no symbols, no frame). Subtle texture, readable.",
        "Frame": base + "Generate the FRAME OVERLAY ONLY. Center must be a clean hole for reels; frame is ornate and cohesive.",
        "Symbols": base + "Generate ONE slot SYMBOL icon, centered, readable silhouette, glossy render. Prefer transparent background if possible.",
    }

    saved_all = []

    try:
        with st.spinner("Generating Background..."):
            res = provider.generate(api_key=api_key, model=model, prompt=prompts["Background"], n=1, size=size, transparent=False)
        saved_all += _save_images("Background", "background", prompts["Background"], res.images)

        with st.spinner("Generating ReelBackground..."):
            res = provider.generate(api_key=api_key, model=model, prompt=prompts["ReelBackground"], n=1, size=size, transparent=False)
        saved_all += _save_images("ReelBackground", "reelbg", prompts["ReelBackground"], res.images)

        # Frame: try transparent if user enabled it; otherwise contain-mode canvas still works
        want_transparent = bool(st.session_state.get("transparent_bg", False))
        with st.spinner("Generating Frame..."):
            res = provider.generate(api_key=api_key, model=model, prompt=prompts["Frame"], n=1, size=size, transparent=want_transparent)
        saved_all += _save_images("Frame", "frame", prompts["Frame"], res.images)

        with st.spinner(f"Generating Symbols x{symbols_count}..."):
            res = provider.generate(api_key=api_key, model=model, prompt=prompts["Symbols"], n=int(symbols_count), size=size, transparent=want_transparent)
        saved_all += _save_images("Symbols", "symbol", prompts["Symbols"], res.images)

    except Exception as e:
        st.error("Extraction failed. Check logs and provider settings.")
        st.exception(e)
        st.stop()

    st.success("Extraction complete: Background + ReelBackground + Frame + Symbols (158×178).")
    st.session_state["last_generated_paths"] = saved_all
