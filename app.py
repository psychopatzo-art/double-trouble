import streamlit as st
from pathlib import Path
from core.storage import list_projects, load_project
from core.constants import ASSET_CATEGORIES

BASE = Path(__file__).parent

st.set_page_config(page_title="Slot Art Producer (Streamlit)", layout="wide")

def init_state():
    st.session_state.setdefault("active_project_id", None)
    st.session_state.setdefault("provider", "Gemini")
    st.session_state.setdefault("api_keys", {"Gemini": "", "OpenAI": ""})
    st.session_state.setdefault("provider_models", {
        "Gemini": "imagen-4.0-generate-001",
        "OpenAI": "gpt-image-1.5",
    })
    st.session_state.setdefault("transparent_bg", False)

init_state()

st.title("🎰 Slot Art Producer — Streamlit Edition")

with st.sidebar:
    st.header("Provider")
    st.session_state.provider = st.selectbox("Image Provider", ["Gemini", "OpenAI"], index=0 if st.session_state.provider=="Gemini" else 1)

    key_label = "GEMINI_API_KEY" if st.session_state.provider=="Gemini" else "OPENAI_API_KEY"
    st.session_state.api_keys[st.session_state.provider] = st.text_input(
        f"API Key ({key_label})",
        value=st.session_state.api_keys.get(st.session_state.provider, ""),
        type="password",
        help="Stored only in session_state for this browser session. For Streamlit Cloud, use Secrets for persistent keys."
    )

    st.session_state.transparent_bg = st.toggle("Transparent background (if supported)", value=st.session_state.transparent_bg)

    st.caption("Categories: " + ", ".join(ASSET_CATEGORIES))

    st.divider()
    st.header("Project")
    projects = list_projects(BASE)
    options = ["— Create new —"] + [f'{p["title"]} ({p["id"][:8]})' for p in projects]
    choice = st.selectbox("Select project", options, index=0 if not st.session_state.active_project_id else 1)

    if choice != "— Create new —":
        pid = projects[options.index(choice)-1]["id"]
        st.session_state.active_project_id = pid
    else:
        st.session_state.active_project_id = None

    if st.session_state.active_project_id:
        st.success(f"Active: {st.session_state.active_project_id[:8]}")

st.write(
    "Use the pages on the left (Streamlit multipage) to create projects, generate assets, preview, and export."
)
st.info("Start with **Project Manager** page → then **Generator** → then **Library** / **Preview** → then **Export**.")
