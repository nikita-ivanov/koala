import streamlit as st

from utils import translate

st.header("Translator")

input_text = st.text_area("Input (German)", key="input", value="Hallo Welt, wie geht es?")

translation = translate(st.session_state["input"])
output_text = st.text_area("Output (English)", value=translation, key="output")

st.markdown("""
Translation above is enabled by training a custom neural machine translation model.
It is based on an encoder-decoder transformer architecture.
The model was trained on 200k German-English sentence pairs from an ISWLT [dataset](https://huggingface.co/datasets/IWSLT/iwslt2017).
The model is tiny by current standards. It contains 10M parameters and its weight is 40MB.
Therefore, translations might not be accurate. It works best with short sentences.
The source code for training the model can be found [here](https://github.com/nikita-ivanov/neural_translation/blob/main/translator_transformer.ipynb).
""")
