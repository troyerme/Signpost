"""Signpost: student adaptation of rayna-xu-is/RXpizzeria."""
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")


def setting(name, default=""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except FileNotFoundError:
        return os.getenv(name, default)


st.set_page_config(page_title="Signpost | Museum Visitor Guide", page_icon="💡")
st.title("Signpost")
st.caption("An unofficial student visitor guide to the American Sign Museum")
if (ROOT / "logo.png").exists():
    st.image(str(ROOT / "logo.png"), width=220)
st.write("Ask about admission, opening hours, tours, or planning a visit.")
st.caption("Information checked November 3, 2026. Confirm changes with the museum.")
st.link_button("Official visitor information", "https://www.americansignmuseum.org/visit/")

if "messages" not in st.session_state:
    st.session_state.messages = []
if st.button("Clear conversation"):
    st.session_state.messages = []

api_key = setting("OPENAI_API_KEY")
grounding = setting("GROUNDING") or (ROOT / "grounding.txt").read_text(encoding="utf-8")
if not api_key:
    st.info("Add your OPENAI_API_KEY to assignment4_app/.env to enable chat. On Streamlit Community Cloud, use app Secrets.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help you plan your visit?", disabled=not bool(api_key)):
    user_message = {"role": "user", "content": prompt}
    with st.chat_message("user"):
        st.markdown(prompt)
    try:
        with st.chat_message("assistant"), st.spinner("Checking your question..."):
            client = OpenAI(api_key=api_key, timeout=60, max_retries=1)
            response = client.responses.create(
                model=setting("OPENAI_MODEL", "gpt-5-mini"),
                instructions=grounding,
                input=st.session_state.messages + [user_message],
                store=False,
            )
            answer = response.output_text
            if not answer.strip():
                raise ValueError("Empty response")
            st.markdown(answer)
        st.session_state.messages.extend([user_message, {"role": "assistant", "content": answer}])
    except (OpenAIError, ValueError):
        st.error("The reply could not be completed. Check your API access and connection, then try again.")
