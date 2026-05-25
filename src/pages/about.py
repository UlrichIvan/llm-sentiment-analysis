import streamlit as st

from utils.helpers import get_image, tte

LINKED_IN = st.secrets["LINKED_IN"]


def app(page: str, lang: str):
    data_url = get_image("me.jpeg")
    st.markdown(
        f"""
            # {tte(page=page,lang=lang,word="This application had been build by")}:
        """
    )
    authors = [
        {
            "name": "Ulrich",
            "image": data_url,
            "role": tte(
                page=page,
                lang=lang,
                word="Passionate about data science and machine learning",
            ),
        }
    ]
    st.markdown(
        """
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
                <div class="container-fluid">
        """,
        unsafe_allow_html=True,
    )
    for i in range(len(authors)):

        st.markdown(
            f"""
               <div class="col-wrapper my-4">
                    <div class="row align-items-center justify-content-center flex-row">
                            <div class="col-2">
                                    <img src="data:image/jpeg;base64,{authors[i].get("image")}" alt="{authors[i].get("name")}" class="rounded-circle img-fluid">
                            </div>
                            <div class="col-8">
                                    <div class="name text-capitalize" style="font-size:25px;">{authors[i].get("name")}</div>
                                    <div class="role fw-bolder text-capitalize" style="font-size:16px;">{authors[i].get("role")}</div>
                                    <div class="role fw-bolder flex-wrap d-flex text-capitalize" style="font-size:16px;"> 
                                        <a class="me-2" href="{LINKED_IN}">{tte(page=page,lang=lang,word="About Me")}</a>
                                    </div>
                            </div>
                    </div>
               </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(
        f"""
                <div/>
        """,
        unsafe_allow_html=True,
    )
    # st.image(love)
