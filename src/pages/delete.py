import time
import streamlit as st

from utils.helpers import drop_user_data, get_image, tte


def app(page: str, lang: str):
    @st.dialog(tte(page=page, lang=lang, word="Delete Data"))
    def drop_consent(page: str, lang: str):
        st.markdown(
            f"""
                {tte(
                    page=page, lang=lang, word="Are you sure you want to delete your data ?"
                )} 
                <br>{tte(
                    page=page, lang=lang, word="this action is not reversible"
                )}<br>
            """,
            unsafe_allow_html=True,
        )
        options = [
            tte(page=page, lang=lang, word="Yes"),
            tte(page=page, lang=lang, word="No"),
        ]
        radio = st.radio(
            label=tte(page=page, lang=lang, word="Please make your choice."),
            options=options,
            index=None,
        )
        if st.button(tte(page=page, lang=lang, word="Confirm")):
            if radio == options[0]:
                drop_user_data(str(st.user.email))
                st.balloons()
                time.sleep(2)
                st.rerun(scope="app")
            else:
                st.rerun(scope="app")

    nexa = get_image(filename="trash.png")
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
            text-align:left;
        }
        .stButton > button {
            height: auto;
            padding-top: 15px !important;
            padding-bottom: 15px !important;
            width: 200px;
            text-transform:capitalize;
            margin : 15px auto;
        }
    </style>
""",
        unsafe_allow_html=True,
    )
    try:
        with st.container():
            st.markdown("<div>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <img src="data:image/jpeg;base64,{nexa}" width="300" alt="nexa" class="rounded-circle img-fluid">
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                tte(page=page, lang=lang, word="Drop my data"),
                icon="🚨",
            ):
                drop_consent(page=page, lang=lang)
            st.markdown("</div>", unsafe_allow_html=True)
    except:
        st.toast(
            body=tte(page=page, lang=lang, word="an error occured, please try again"),
            icon="🚨",
        )
