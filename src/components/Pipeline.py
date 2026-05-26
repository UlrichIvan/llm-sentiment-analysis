from io import BytesIO
import streamlit as st
from typing import Any
import pandas as pd
import plotly.express as px
import zipfile
from src.components.Pipe import BasePipe
from utils.helpers import (
    __DIR__,
    COLUMNS_DATA_POLARITY,
    DIAGRAMS,
    METRCIS,
    MODELS,
    init_user_directory,
    save_cleaned_data,
    save_data_polarity,
)
import time
from streamlit.runtime.uploaded_file_manager import UploadedFile


class Pipeline(BasePipe):

    def __init__(self, page: str, lang: str) -> None:
        super().__init__(page=page, lang=lang, user=st.user)
        self.data: None | pd.DataFrame = None
        self.data_cleaned: None | pd.DataFrame = None
        self.reviews: None | UploadedFile
        self.models = MODELS
        self.diagrams = DIAGRAMS
        self.nb_threads = 5
        self.create_user_directory()

    def hide_btn(self):
        st.session_state["is_loading"] = True

    def create_user_directory(self) -> bool:
        return init_user_directory(str(st.user.get("email")))

    def clean_data_processing(self) -> pd.DataFrame | None:
        st.markdown(f"### {self.translate(word="Cleaning up reviews")}")

        nb_threads = st.number_input(
            label=self.translate(word="Set the number of workers"),
            min_value=5,
            max_value=10,
            icon=":material/engineering:",
            disabled=st.session_state["is_loading"],
            help=self.translate(
                word="set number of workers to use for clean up reviews"
            ),
        )

        btn_runner = st.button(
            label=self.translate(word="Clean Up"),
            type="secondary",
            icon=":material/play_circle:",
            disabled=st.session_state["is_loading"],
            on_click=self.hide_btn,
        )

        if btn_runner:
            st.toast(
                body=self.translate(
                    word="Clean up reviews process is running. if you want to stop it click on reset button on the top of page"
                ),
                icon="😍",
            )
            columns = ["text"]
            threads = self.build_threads_cleaner(
                data=st.session_state["dataset"], nb_threads=nb_threads
            )
            data_cleaned = self.threads_clean_reviews(threads)
            st.session_state["dataset_cleaned"] = pd.DataFrame(
                data_cleaned, columns=columns
            )
            st.balloons()
            st.toast(
                body=self.translate(word="Cleaning up reviews performed successfully"),
                icon="😍",
            )
            time.sleep(1.5)
            st.session_state["is_loading"] = False
            st.rerun(scope="app")  # rerun app to hide button

    def analyse_data_processing(
        self, data: pd.DataFrame, selected_model: str, nb_threads: int = 5
    ) -> None:
        st.session_state["is_loading"] = True
        threads = self.build_threads_predicter(data, nb_threads, selected_model)

        st.markdown("<br>", unsafe_allow_html=True)

        _data_polarity = self.threads_make_predictions(threads)

        # create
        df_polarity = save_data_polarity(
            df=pd.DataFrame(_data_polarity, columns=COLUMNS_DATA_POLARITY),
            user_id=st.session_state["user_id"],
            model=selected_model,
        )
        self.save_data(
            df=st.session_state["dataset"],
            user_id=st.session_state["user_id"],
            model=selected_model,
        )
        save_cleaned_data(
            data=st.session_state["dataset_cleaned"],
            user_id=st.session_state["user_id"],
            model=selected_model,
        )
        st.balloons()
        st.toast(body=self.translate(word="Analyze performed successfully"), icon="😍")
        time.sleep(1.5)
        st.session_state["dataset_polarity"] = df_polarity
        st.session_state["is_loading"] = False
        st.rerun(scope="app")  # rerun app to hide button

    def update_dataset_state(self):
        st.session_state["user_uploading"] = True

    def display_word_cloud(self, df_polarity: pd.DataFrame):
        df_pos = df_neg = None
        data = []
        if df_polarity is not None:
            columns = df_polarity.columns.to_list()
            if "polarity" in columns and "word" in columns:
                df_positives = df_polarity[df_polarity["polarity"] == "Positive"]
                df_negatives = df_polarity[df_polarity["polarity"] == "Negative"]

                series_positives = (
                    df_positives["word"].dropna(inplace=False)
                    if df_positives is not None
                    else None
                )
                series_negatives = (
                    df_negatives["word"].dropna(inplace=False)
                    if df_negatives is not None
                    else None
                )

                if series_positives is not None:
                    df_pos = self.display_words_polarity_graphes(
                        series_positives, positive=True
                    )

                if series_negatives is not None:
                    df_neg = self.display_words_polarity_graphes(
                        series_negatives, positive=False
                    )

                if df_pos is not None:
                    data.append(df_pos)

                if df_pos is not None:
                    data.append(df_neg)

                if len(data):
                    df_concat = pd.concat(data, axis=0)
                    self.display_relative_words_table_metrics(
                        df=df_concat,
                        table_metric_title=f"{self.translate(word="Analyze Results of words polarity")}({df_concat.shape[0]} {self.translate(word="Total words")})",
                    )

                # create download button
                # 1.Create buffer
                zip_buffer = BytesIO()
                with zipfile.ZipFile(
                    zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED
                ) as zf:
                    # 1. get summary from pie diagram as table
                    _, df_table = self.set_table_summary_values_count_into_zip(
                        zf,
                        [df_polarity],
                        filename=self.translate(
                            word="sentiments_analysis_results_table_metrics.csv"
                        ),
                    )

                    # 2. Write image from sentiments analysis
                    # create fig buffer
                    pie_buffer = self.set_plot_image_into_zip(
                        df_table,
                        title=f"{self.translate(word="Analyze Results of Sentiments")}({df_polarity.shape[0]} {self.translate(word="Total reviews")})",
                    )
                    # write img to zip file
                    zf.writestr(
                        self.translate(word="sentiments_analysis_results.png"),
                        pie_buffer.getvalue(),
                    )

                    # 3. get summary from pie diagram as table
                    df_data = []
                    if series_positives is not None:
                        positives_occurences = self.get_words_occurences(
                            " ".join(series_positives.apply(str))
                        )

                        df_ps = self.get_df_from_occurences(
                            words_occurences=positives_occurences, positive=True
                        )

                        self.set_df_into_zip(
                            zf=zf,
                            df=df_ps,
                            filename=self.translate(
                                word="positives_words_frequencies.csv"
                            ),
                        )

                        df_data.append(df_ps)

                    if series_negatives is not None:
                        negatives_occurences = self.get_words_occurences(
                            " ".join(series_negatives.apply(str))
                        )
                        df_ns = self.get_df_from_occurences(
                            words_occurences=negatives_occurences, positive=False
                        )
                        self.set_df_into_zip(
                            zf=zf,
                            df=df_ns,
                            filename=self.translate(
                                word="negatives_words_frequencies.csv"
                            ),
                        )
                        df_data.append(df_ns)

                    if len(df_data):
                        df, df_words_table = (
                            self.set_table_summary_values_count_into_zip(
                                zf,
                                df_data,
                                filename=self.translate(
                                    word="words_analysis_results_table_metrics.csv"
                                ),
                            )
                        )

                        pie_buffer_words = self.set_plot_image_into_zip(
                            df_words_table,
                            title=f"{self.translate(word="Words Polarities Results")} ({df.shape[0]} {self.translate(word="Total words")})",
                        )

                        zf.writestr(
                            self.translate(
                                word="words_sentiments_analysis_results.png"
                            ),
                            pie_buffer_words.getvalue(),
                        )

                    # reset buffer seek to begin
                    zip_buffer.seek(0)
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    label=self.translate(word="Download complete summary analyze"),
                    data=zip_buffer,
                    file_name=self.translate(word="summary_analyse.zip"),
                    mime="application/zip",
                    type="primary",
                    help=self.translate(word="Download complete summary analyze"),
                )

    def render(self) -> Any:
        try:
            # display file uploader
            reviews = st.file_uploader(
                label=self.translate(word="Upload reviews csv file"),
                accept_multiple_files=False,
                type=["csv"],
                help=self.translate(
                    word="Load users reviews csv file which must contains the 'text' column for users reviews and UTF-8 encoding for dataset"
                ),
                disabled=st.session_state["is_loading"],
                on_change=self.update_dataset_state,
            )

            if reviews is not None:  # user upload file
                if st.session_state["dataset"] is not None:  # upload with old data
                    if st.session_state["user_uploading"]:  # user uploaded file trusted
                        data = self.load_dataset_upload(reviews=reviews)
                        if data is not None:
                            self.user_pipeline_analysis()
                            self.alert_user(data)
                        else:
                            self.user_pipeline_analysis()

                    else:  # user not upload file
                        self.user_pipeline_analysis()
                else:  # fisrt upload
                    data = self.load_dataset_upload(reviews=reviews)
                    if data is not None:
                        st.session_state["dataset"] = data
                        st.session_state["user_uploading"] = False
                        st.balloons()
                        st.toast(
                            body=self.translate(word="Reviews loaded successfully"),
                            icon="😍",
                        )
                        time.sleep(1.5)
                        st.rerun(scope="app")
            else:  # user not upload file
                self.user_pipeline_analysis()
        except Exception as e:
            st.toast(
                body=self.translate(word="an error occured, please try again"),
                icon="🚨",
            )
            self.user_pipeline_analysis()

    def format_func_model(self, model: str) -> str:
        return f"{self.translate(word="Model")}(AUC= {float(METRCIS[model].get('auc',""))*100}% , accuracy= {float(METRCIS[model].get('accuracy',""))*100}%)"

    def user_pipeline_analysis(self):
        self.disabled_rerun_app()  # display reset button
        if st.session_state["dataset"] is not None and len(st.session_state["dataset"]):
            # display dataset
            st.markdown(
                f"### {self.translate(word="Reviews")}{st.session_state["dataset"].shape}"
            )
            st.dataframe(st.session_state["dataset"].head())
            if st.session_state["dataset_cleaned"] is None:
                self.clean_data_processing()
            elif st.session_state["dataset_cleaned"] is not None and len(
                st.session_state["dataset_cleaned"]
            ):
                st.markdown(
                    f"### {self.translate(word="Reviews")} {self.translate(word="Cleaned")} {st.session_state["dataset_cleaned"].shape}"
                )
                st.dataframe(st.session_state["dataset_cleaned"].head())
                nb_threads = st.number_input(
                    label=self.translate(word="Set the number of workers"),
                    min_value=5,
                    max_value=10,
                    icon=":material/engineering:",
                    disabled=st.session_state["is_loading"],
                    help=self.translate(
                        word="set number of workers to perform analyse of reviews",
                    ),
                )
                selected_model = st.selectbox(
                    self.translate(
                        word="Select a model(AUC : Overall Performance, Accuracy : Percent Of True Positif)"
                    ),
                    self.models,
                    key="selected_model",
                    format_func=self.format_func_model,
                    index=self.models.index("SVC"),
                    disabled=st.session_state["is_loading"],
                    help=self.translate(
                        word="Select model to perform analyse of reviews"
                    ),
                )
                btn_analyzer = st.button(
                    label=self.translate(word="Analyze"),
                    type="secondary",
                    icon=":material/visibility:",
                    disabled=st.session_state["is_loading"],
                    on_click=self.hide_btn,
                )
                if btn_analyzer:
                    self.analyse_data_processing(
                        data=st.session_state["dataset_cleaned"],
                        selected_model=selected_model,
                        nb_threads=nb_threads,
                    )

            if st.session_state["dataset_polarity"] is not None and len(
                st.session_state["dataset_polarity"]
            ):
                st.markdown(f"### {self.translate(word="Analyze results")}")
                selected_diagram = st.selectbox(
                    self.translate(word="Select diagram"),
                    self.diagrams,
                    key="selected_diagram",
                    index=self.diagrams.index("pie"),
                    disabled=st.session_state["is_loading"],
                    help=self.translate(
                        word="Select a diagram to show analyze results"
                    ),
                )
                self.plot_polarity(
                    df=st.session_state["dataset_polarity"],
                    type_diagram=selected_diagram,
                    title=f"{self.translate(word="Analyze Results of Sentiments")}({st.session_state["dataset_polarity"].shape[0]} {self.translate(word="Total reviews")})",
                )

    def disabled_rerun_app(self):
        # disabled btn if needle
        if st.session_state["is_loading"] == True:
            btn_reset = st.button(
                label="reset",
                type="secondary",
                icon=":material/refresh:",
            )

            if btn_reset:
                st.session_state["is_loading"] = False
                st.rerun(scope="app")

    @st.dialog(title=" ")
    def alert_user(self, data: pd.DataFrame | None):
        st.markdown(
            f"""
            {self.translate(word="Are you sure you want to terminate this action ?<br>Rember that all data on the current page will be lost.<br>")}
            """,
            unsafe_allow_html=True,
        )

        if data is None:
            return

        options = [self.translate(word="Yes"), self.translate(word="No")]
        radio = st.radio(
            label=self.translate(word="Please confirm your choice."),
            options=options,
            index=None,
        )
        if st.button("Confirm"):
            if radio == options[0]:
                st.session_state["dataset"] = data
                st.session_state["dataset_cleaned"] = None
                st.session_state["dataset_polarity"] = None
                st.session_state["user_uploading"] = False
                st.balloons()
                st.toast(
                    body=self.translate(word="Reviews loaded successfully"),
                    icon="😍",
                )
                time.sleep(1.5)
                st.rerun(scope="app")
            else:
                st.session_state["user_uploading"] = False
                st.rerun(scope="app")
