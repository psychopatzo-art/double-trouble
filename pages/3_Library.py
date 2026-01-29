import streamlit as st
from pathlib import Path
from PIL import Image
from core.storage import load_project
from core.constants import ASSET_CATEGORIES

BASE = Path(__file__).resolve().parents[1]

st.header("🗃️ Library")

pid = st.session_state.get("active_project_id")
if not pid:
    st.warning("Select or create a project in the sidebar first.")
    st.stop()

project = load_project(BASE, pid)
st.subheader(project.title)

cat = st.selectbox("Filter category", ["All"] + ASSET_CATEGORIES, index=0)

assets = project.assets
if cat != "All":
    assets = [a for a in assets if a.category == cat]

st.caption(f"{len(assets)} asset(s)")

if not assets:
    st.info("No assets yet. Go to Generator.")
    st.stop()

cols = st.columns(4)
for i, a in enumerate(assets[:200]):
    p = BASE / "data" / "projects" / pid / a.path
    with cols[i % 4]:
        if p.exists():
            st.image(Image.open(p), caption=f"{a.category} • {a.name}", use_container_width=True)
        else:
            st.warning(f"Missing file: {a.path}")
        with st.expander("Details", expanded=False):
            st.write({"provider": a.provider, "model": a.model})
            st.code(a.prompt)
