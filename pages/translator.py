import streamlit as st

from utils import translate

st.header("Translator")
input_text = st.text_area("Input (German)", key="input", value="Hallo Welt, wie geht es?")

translation = translate(st.session_state["input"])
output_text = st.text_area("Output (English)", value=translation, key="output")
