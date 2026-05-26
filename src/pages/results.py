import streamlit as st

from src.components.Pipeline import Pipeline
from utils.helpers import (
    get_data,
    get_data_polarity,
    get_image,
)


def app(page: str, lang: str):
    try:
        empty = get_image(filename="empty-image-cart.png")
        with st.container():
            pipeline = Pipeline(page=page, lang=lang)
            selected_model = st.selectbox(
                pipeline.translate(
                    word="Select a model(AUC : Overall Performance, Accuracy : Percent Of True Positif)"
                ),
                pipeline.models,
                key="selected_model",
                format_func=pipeline.format_func_model,
                index=pipeline.models.index("SVC"),
                disabled=st.session_state["is_loading"],
                help=pipeline.translate(
                    word="Select model to show analyze results of reviews"
                ),
            )
            selected_diagram = st.selectbox(
                pipeline.translate(word="Select diagram"),
                pipeline.diagrams,
                key="selected_diagram",
                index=pipeline.diagrams.index("pie"),
                disabled=st.session_state["is_loading"],
                help=pipeline.translate(
                    word="Select a diagram to show analyze results"
                ),
            )
            if selected_diagram and selected_model:
                df = get_data_polarity(user_id=str(st.user.get("email")), model=selected_model)
                data = get_data(user_id=str(st.user.get("email")), model=selected_model)
                if df is not None:
                    if data is not None:
                        st.markdown(
                            f"### {pipeline.translate("Last Reviews")} {data.shape}"
                        )
                        st.dataframe(data.head())
                    st.markdown(f"### {pipeline.translate("Analyze results")}")
                    pipeline.plot_polarity(
                        df=df,
                        type_diagram=selected_diagram,
                        title=f"{pipeline.translate(word="Analyze Results of Sentiments")}({df.shape[0]} {pipeline.translate(word="Total reviews")})",
                    )
                    pipeline.display_word_cloud(df_polarity=df)
                else:
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
                    st.markdown(
                        f"""
                    <img src="data:image/jpeg;base64,{empty}" alt="empty results" width="300" class="rounded-circle img-fluid">
                    <p style="text-transform:capitalize;"> you don't have results analysis</p>
                    """,
                        unsafe_allow_html=True,
                    )
    except Exception as e:
        st.toast(
            body=pipeline.translate(word="an error occured, please try again"),
            icon="🚨",
        )
