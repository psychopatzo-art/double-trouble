import streamlit as st
from pathlib import Path
from PIL import Image
import time

from core.storage import load_project, add_asset, ensure_project_dirs
from core.models import Asset
from core.constants import ASSET_CATEGORIES
from core.providers import PROVIDERS

BASE = Path(__file__).resolve().parents[1]

st.header("🧪 Generator")

pid = st.session_state.get("active_project_id")
if not pid:
    st.warning("Select or create a project in the sidebar first.")
    st.stop()

project = load_project(BASE, pid)
ensure_project_dirs(BASE, pid, ASSET_CATEGORIES)

st.subheader(project.title)
st.caption(f"Theme: {project.theme}")

colA, colB = st.columns([2, 1])

with colB:
    category = st.selectbox("Asset category", ASSET_CATEGORIES, index=ASSET_CATEGORIES.index("Mockups"))
    name = st.text_input("Asset name", value=f"{category.lower()}-01")
    n = st.slider("How many", 1, 4, 1)
    if st.session_state.provider == "Gemini":
        model = st.selectbox("Model", ["imagen-4.0-generate-001"], index=0)
        size = st.selectbox("Size", ["1K", "2K"], index=0)
    else:
        model = st.selectbox("Model", ["gpt-image-1.5", "gpt-image-1", "dall-e-3"], index=0)
        size = st.selectbox("Size", ["1024x1024", "1792x1024", "1024x1792"], index=0)

with colA:
    base_prompt = st.text_area("Prompt", value=f"{project.theme}. {project.style_lock}\n\nGenerate {category} asset: {name}.")
    go = st.button("Generate", type="primary", use_container_width=True)

    if go:
        provider_key = st.session_state.provider
        api_key = st.session_state.api_keys.get(provider_key, "").strip()
        if not api_key:
            st.error("Missing API key for selected provider.")
            st.stop()

        provider = PROVIDERS["Gemini" if provider_key=="Gemini" else "OpenAI"]
        with st.spinner("Generating..."):
            res = provider.generate(
                api_key=api_key,
                model=model,
                prompt=base_prompt,
                n=int(n),
                size=size,
                transparent=bool(st.session_state.get("transparent_bg", False)),
            )

        st.success(f"Generated {len(res.images)} image(s). Saving to project...")
        pdir = BASE / "data" / "projects" / pid / "assets" / category
        saved = []
        ts = int(time.time())
        for idx, img in enumerate(res.images, start=1):
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
                meta={"size": size, "n": n},
            )
            add_asset(BASE, project, asset)
            saved.append(fpath)

        st.toast("Saved to Library", icon="🗃️")
        st.session_state["last_generated_paths"] = [str(p) for p in saved]

paths = st.session_state.get("last_generated_paths", [])
if paths:
    st.subheader("Last generated")
    cols = st.columns(min(4, len(paths)))
    for i, p in enumerate(paths):
        with cols[i % len(cols)]:
            st.image(Image.open(p), caption=Path(p).name, use_container_width=True)
