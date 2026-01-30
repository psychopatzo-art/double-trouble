# pages/2_Generator.py

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

st.header("🧪 Generator")

pid = st.session_state.get("active_project_id")
if not pid:
    st.warning("Select or create a project in the sidebar first.")
    st.stop()

project = load_project(BASE, pid)
ensure_project_dirs(BASE, pid, ASSET_CATEGORIES)

cfg = project.preview_config or {}
TW, TH = cfg.get("canvas", {}).get("w", 1440), cfg.get("canvas", {}).get("h", 810)

st.subheader(project.title)
st.caption(f"Theme: {project.theme} | Orientation: {project.orientation} | Canvas: {TW}×{TH}")

colA, colB = st.columns([2, 1])

with colB:
    category = st.selectbox("Asset category", ASSET_CATEGORIES, index=ASSET_CATEGORIES.index("Mockups"))
    name = st.text_input("Asset name", value=f"{category.lower()}-01")

    # For mockups we always generate 1, for others you can choose
    if category == "Mockups":
        n = 1
        st.info("Mockups generate ONE full concept image (screenshot-style).")
    else:
        n = st.slider("How many", 1, 4, 1)

    # Model/size UI
    if st.session_state.provider == "Gemini":
        model = st.selectbox("Model", ["imagen-4.0-generate-001"], index=0)
        size = st.selectbox("Size", ["1K", "2K"], index=1)  # default 2K
    else:
        model = st.selectbox("Model", ["gpt-image-1.5", "gpt-image-1", "dall-e-3"], index=1)

        # pick a good default by orientation (closest aspect)
        default_size = "1792x1024" if project.orientation == "Landscape" else "1024x1792"
        size = st.selectbox("Size", ["1024x1024", "1792x1024", "1024x1792"], index=["1024x1024","1792x1024","1024x1792"].index(default_size))

with colA:
    # Prompt UI
    if category == "Mockups":
        base_prompt = st.text_area(
            "Mockup prompt (concept)",
            value=(
                f"{project.theme}. {project.style_lock}\n\n"
                "Create ONE complete slot game mockup screenshot.\n"
                "Include: background environment + reel window panel + ornate frame overlay + reels filled with symbol icons.\n"
                "No UI buttons, no logos, no text labels.\n"
                "Cohesive style, high readability, clean silhouettes, polished casino slot look.\n"
            ),
            height=220,
        )
    else:
        base_prompt = st.text_area(
            "Prompt",
            value=f"{project.theme}. {project.style_lock}\n\nGenerate {category} asset: {name}.",
            height=220,
        )

    go = st.button("Generate", type="primary", use_container_width=True)

def _postprocess_for_category(img: Image.Image, cat: str) -> Image.Image:
    if cat in ["Background", "Mockups"]:
        return to_canvas(img, TW, TH, mode="cover")
    if cat in ["ReelBackground", "Frame", "UI", "Splashes", "BonusGames", "FreeSpins", "Characters"]:
        return to_canvas(img, TW, TH, mode="contain")
    if cat == "Symbols":
        return to_exact_symbol_size(img, 158, 178)
    # UploadedAssets or unknown: keep as-is
    return img.convert("RGBA")

if go:
    provider_key = st.session_state.provider  # "Gemini" or "OpenAI"
    api_key = (st.session_state.api_keys.get(provider_key) or "").strip()
    if not api_key:
        st.error("Missing API key for selected provider.")
        st.stop()

    provider = PROVIDERS["Gemini" if provider_key == "Gemini" else "OpenAI"]

    # For mockups: transparent OFF (we want a screenshot)
    transparent = False if category == "Mockups" else bool(st.session_state.get("transparent_bg", False))

    try:
        with st.spinner("Generating..."):
            res = provider.generate(
                api_key=api_key,
                model=model,
                prompt=base_prompt,
                n=int(n),
                size=size,
                transparent=transparent,
            )
    except Exception as e:
        st.error("Generation failed. Check your provider/model/key and Streamlit logs.")
        st.exception(e)
        st.stop()

    st.success(f"Generated {len(res.images)} image(s). Saving...")

    pdir = BASE / "data" / "projects" / pid / "assets" / category
    saved = []
    ts = int(time.time())

    for idx, img in enumerate(res.images, start=1):
        img = _postprocess_for_category(img, category)

        fn = f"{name}-{ts}-{idx}.png"
        fpath = pdir / fn
        img.save(fpath, "PNG")

        rel = str(fpath.relative_to(BASE / "data" / "projects" / pid))
        asset = Asset.new(
            category=category,
            name=fn,
            prompt=base_prompt,
            provider=provider_key,
            model=model,
            path=rel,
            meta={"size": size, "n": n, "canvas": f"{TW}x{TH}", "orientation": project.orientation},
        )
        add_asset(BASE, project, asset)
        saved.append(str(fpath))

    st.toast("Saved to Library", icon="🗃️")
    st.session_state["last_generated_paths"] = saved

paths = st.session_state.get("last_generated_paths", [])
if paths:
    st.subheader("Last generated")
    cols = st.columns(min(4, len(paths)))
    for i, p in enumerate(paths):
        with cols[i % len(cols)]:
            st.image(Image.open(p), caption=Path(p).name, use_container_width=True)
