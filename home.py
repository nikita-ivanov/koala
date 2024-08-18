import streamlit as st

st.set_page_config(page_title="Koala",
                   page_icon="🐨",
                   menu_items={"Report a bug": "https://github.com/nikita-ivanov/koala/issues",
                               "About": "Personal webpage"})

st.markdown("""
## Welcome 🐨
Welcome to my personal webpage.
It is meant to showcase some of the projects I've been working on.
The source code for this webapp can be found [here](https://github.com/nikita-ivanov/koala).

## Privacy
No personal or any other kind of data is stored. There are no cookies or logs.

## Projects
You can find currently available projects at the left sidebar.
- <a href='translator' target='_self'>Translator</a>
- <a href='finance' target='_self'>Financial Planner</a>

## Contact
- [GitHub](https://github.com/nikita-ivanov/koala)
- [LinkedIn](https://linkedin.com/in/nikitaivanovde)
""", unsafe_allow_html=True)
