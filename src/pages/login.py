import streamlit as st
from utils.helpers import get_image,__DIR__
def app():
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
        .stButton > [data-testid="stBaseButton-secondary"] {
            height: auto;
            padding-top: 20px !important;
            padding-bottom: 20px !important;
            width: 200px;
            text-transform:capitalize;
        }
        [data-testid="stElementContainer"]{
            margin:auto;
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
        st.markdown(
            f"""
            <h2 style="padding-top:0px;">Easy and Quick Analyses Reviews</h2>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
                "Get's started",
                icon="😍",
            ):
                st.user={
                    "is_logged_in":True,
                    "email_verified":True,
                    "picture" :"" ,
                    "email":"user@email.com"
                }
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
