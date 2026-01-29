import streamlit as st
from pathlib import Path
from core.export_utils import zip_project

BASE = Path(__file__).resolve().parents[1]

st.header("📦 Export")

pid = st.session_state.get("active_project_id")
if not pid:
    st.warning("Select or create a project in the sidebar first.")
    st.stop()

project_path = BASE / "data" / "projects" / pid
if not project_path.exists():
    st.error("Project folder missing.")
    st.stop()

st.write("This exports the entire project folder: `project.json` + `assets/`")
if st.button("Build ZIP", type="primary"):
    blob = zip_project(project_path)
    st.download_button(
        "Download project ZIP",
        data=blob,
        file_name=f"slot_project_{pid[:8]}.zip",
        mime="application/zip",
    )
    st.success("ZIP ready.")
