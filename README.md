# Slot Art Producer (Streamlit)

A Streamlit port of the Slot Art Producer workflow:
**Project → Generate → Library → Preview → Export**

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
streamlit run app.py
```

## API Keys
- Gemini/Imagen: get an API key from Google AI Studio.
- OpenAI: use an OpenAI API key.

The UI lets you paste a key per provider. For Streamlit Cloud, add them in **Secrets**.
