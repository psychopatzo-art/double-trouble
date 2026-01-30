# pages/1_Project_Manager.py

import streamlit as st
from pathlib import Path

from core.models import Project
from core.constants import make_default_preview_config, DEFAULT_REELS, DEFAULT_ROWS, ASSET_CATEGORIES
from core.storage import ensure_project_dirs, save_project

BASE = Path(__file__).resolve().parents[1]

st.header("🗂️ Project Manager")

with st.form("create_project", clear_on_submit=False):
    title = st.text_input("Project title", value="My Slot Game")
    theme = st.text_input("Theme", value="Fruits & Phoenix")
    style_lock = st.text_area(
        "Style lock (art bible / mood / palette / do & don't)",
        value="Bright, glossy, cohesive, readable symbols, clean silhouettes, casino slot polish.",
        height=140,
    )

    cols = st.columns(3)
    reels = cols[0].number_input("Reels", min_value=3, max_value=7, value=DEFAULT_REELS, step=1)
    rows = cols[1].number_input("Rows", min_value=3, max_value=6, value=DEFAULT_ROWS, step=1)
    orientation = cols[2].selectbox("Orientation", ["Landscape", "Portrait"], index=0)

    submitted = st.form_submit_button("Create project", type="primary", use_container_width=True)

if submitted:
    cfg = make_default_preview_config(orientation)
    proj = Project.new(
        title=title,
        theme=theme,
        style_lock=style_lock,
        reels=int(reels),
        rows=int(rows),
        preview_config=cfg,
        orientation=orientation,
    )
    ensure_project_dirs(BASE, proj.id, ASSET_CATEGORIES)
    save_project(BASE, proj)

    st.session_state.active_project_id = proj.id
    st.success(f"Created project: {proj.title} ({proj.id[:8]})")
    st.toast("Project created", icon="✅")

st.divider()
st.caption("Next: go to **Generator** to create a Mockup concept, then **Extract** to generate individual assets.")
