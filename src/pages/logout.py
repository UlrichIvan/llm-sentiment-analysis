import streamlit as st

from utils.helpers import get_image, tte


def app(page: str, lang: str):
    company = get_image(filename="company_logo.png")
    st.markdown(
        """
    <style>
        .stMainBlockContainer{ 
            display: flex;
            justify-content: center;
        }
        .stMain {
            justify-content: center;
            align-items: center;
        }
        .stVerticalBlock{
            text-align:center;
        }
        .stButton > button {
            height: auto;
            padding-top: 20px !important;
            padding-bottom: 20px !important;
            width: 200px;
            text-transform:capitalize;
        }
    </style>
""",
        unsafe_allow_html=True,
    )
    with st.container():
        st.markdown("<div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <img src="data:image/jpeg;base64,{company}" alt="company_logo" class="rounded-circle img-fluid">
            """,
            unsafe_allow_html=True,
        )
        if st.button(tte(page=page, lang=lang, word="Logout"), icon="😍"):
            st.logout()
        st.markdown("</div>", unsafe_allow_html=True)
