import streamlit as st
from src.components.Pipeline import Pipeline
from utils.helpers import tte


def app(page: str, lang: str):
    st.title(tte(page=page, lang=lang, word="French Sentiments Analysis"))
    Pipeline(page=page, lang=lang).render()
