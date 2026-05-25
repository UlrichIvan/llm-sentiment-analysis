from io import BytesIO
from pathlib import Path
from posixpath import join
from typing import Any
import zipfile
from matplotlib import pyplot as plt
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
import plotly.express as px

import pandas as pd
from wordcloud import WordCloud

from utils.helpers import (
    __DIR__,
    STORAGE_DIR,
    USER_FOLDER_ANALYSE_NAME,
    clean_text,
    get_important_words_cloud,
    predict,
    tte,
)
from utils.thread import CleanerThread, PredictThread


class BasePipe:
    def __init__(self, page: str, lang: str, user: Any) -> None:
        self.page = page
        self.lang = lang
        self.user = user
        # init sessions
        if "is_loading" not in st.session_state:
            st.session_state["is_loading"] = False

        if "user_id" not in st.session_state:
            st.session_state["user_id"] = str(self.user.email)

        if "dataset" not in st.session_state:
            st.session_state["dataset"] = None

        if "dataset_cleaned" not in st.session_state:
            st.session_state["dataset_cleaned"] = None

        if "dataset_polarity" not in st.session_state:
            st.session_state["dataset_polarity"] = None

        if "user_uploading" not in st.session_state:
            st.session_state["user_uploading"] = False

    def save_data(
        self, df: pd.DataFrame, user_id: int | str, model: str
    ) -> pd.DataFrame | None:
        """
        Saves uploaded review data for a specific user and returns the DataFrame.

        Parameters:
            reviews (UploadedFile): The uploaded file containing review data, expected to be a CSV file.
            user_id (int | str): The unique identifier for the user.

        Returns:
            tuple:
                - pd.DataFrame: The DataFrame containing the uploaded review data if successful.
                - pd.DataFrame: A copy of the original DataFrame.
                If the required 'text' column is missing, returns (None, None) and displays a toast message.

        Notes:
            - The function saves the uploaded data to a user-specific directory under 'storage/{user_id}/original_data.csv'.
            - The uploaded CSV file must contain a 'text' column with all text reviews.
            - If the directory does not exist, it is created.
            - If the 'text' column is missing, a toast notification is shown to the user.
        """

        user_data_original = Path(
            join(
                __DIR__,
                STORAGE_DIR,
                str(user_id),
                model,
                USER_FOLDER_ANALYSE_NAME,
                "original_data.csv",
            )
        )

        if "text" in df.columns.to_list():
            df.to_csv(user_data_original, columns=["text"])
            return df[["text"]]
        else:
            st.toast(
                self.translate(
                    word="Dataframe must be contains 'text' column with all text reviews, please choose another valid file"
                ),
                icon="🚨",
            )
            return None

    def translate(self, word: str) -> str:
        return tte(page=self.page, lang=self.lang, word=word)

    def load_dataset_upload(self, reviews: UploadedFile) -> pd.DataFrame | None:
        try:
            df = pd.read_csv(reviews, encoding="utf-8", on_bad_lines="skip")
            if "text" in df.columns.to_list():
                return df[["text"]]
            else:
                st.toast(
                    self.translate(
                        word="Dataframe must be contains 'text' column with all text reviews, please choose another valid file"
                    ),
                    icon="🚨",
                )
            return None
        except Exception as e:
            if type(e).__name__ == "UnicodeDecodeError":
                st.toast(
                    self.translate(
                        word="CSV file must be encoded in UTF8. Please change the encoding of your csv to UTF8, you can just open your csv file and save it with UTF8 format and try again"
                    ),
                    icon="🚨",
                )
            else:
                raise e

    def plot_pie_diagram(
        self,
        col_polarity_name: str,
        positive_val: str,
        negative_val: str,
        df_copy: pd.DataFrame,
        title: str,
    ):
        fig = px.pie(
            df_copy,
            names=col_polarity_name,
            title=title,
            color=col_polarity_name,
            color_discrete_map={negative_val: "#dc3545", positive_val: "#28a745"},
            hole=0.4,
        )
        # update template hovering
        fig.update_traces(
            hovertemplate=f"<b>%{'{label}'}</b><br>{self.translate(word="Polarity count")} : %{'{value}'}<extra></extra>"
        )
        st.plotly_chart(fig)

    def plot_histogram(
        self,
        col_polarity_name: str,
        positive_val: str,
        negative_val: str,
        df_copy: pd.DataFrame,
        title: str,
    ):
        fig = px.histogram(
            data_frame=df_copy,
            x=col_polarity_name,
            color=col_polarity_name,
            title=title,
            color_discrete_map={negative_val: "#dc3545", positive_val: "#28a745"},
        )

        # update axis
        fig.update_layout(
            xaxis_title=self.translate(word="Polarity of reviews"),
            yaxis_title=self.translate(word="Polarity count"),
        )

        # update template hovering
        counts = (df_copy[col_polarity_name].value_counts(normalize=True) * 100).apply(
            lambda e: f"{round(e)}%"
        )
        text = {
            positive_val: [counts[positive_val]],
            negative_val: [counts[negative_val]],
        }
        # update trace and set text percent
        for trace in fig.data:
            if getattr(trace, "name") == positive_val:
                setattr(trace, "text", text[positive_val])
                setattr(trace, "textposition", "outside")
            if trace.name == negative_val:  # type: ignore
                setattr(trace, "text", text[negative_val])
                setattr(trace, "textposition", "outside")
        fig.update_traces(
            hovertemplate=f"<b>{col_polarity_name} : {'%{fullData.name}'}</b><br>{self.translate(word="Polarity count")} : %{'{y}'}<extra></extra>"
        )
        st.plotly_chart(fig)

    def plot_polarity(self, df: pd.DataFrame, title: str, type_diagram="pie"):
        # translate targets for diagram
        col_polarity_name = self.translate(word="polarity")
        positive_val = self.translate(word="Positive")
        negative_val = self.translate(word="Negative")
        # get copy of dataframe and apply target value translate
        df_copy = df.copy()
        df_copy.rename({"polarity": col_polarity_name}, axis=1, inplace=True)
        df_copy[col_polarity_name] = df_copy[col_polarity_name].apply(
            lambda val: positive_val if val == "Positive" else negative_val
        )
        if type_diagram == "histogram":
            self.plot_histogram(
                col_polarity_name=col_polarity_name,
                positive_val=positive_val,
                negative_val=negative_val,
                df_copy=df_copy,
                title=title,
            )
        elif type_diagram == "pie":
            self.plot_pie_diagram(
                col_polarity_name=col_polarity_name,
                positive_val=positive_val,
                negative_val=negative_val,
                df_copy=df_copy,
                title=title,
            )

    def threads_clean_reviews(
        self,
        threads: list[CleanerThread],
    ) -> list:
        data = []
        with st.spinner(
            text=f"{self.translate(word="Workers in progress...")}({self.translate(word="Total workers")} = {len(threads)})",
            show_time=True,
        ):
            for i, thread in enumerate(threads):
                bar = st.progress(0)
                total = len(thread.data)
                count = i + 1
                if total > 1:
                    data_cleaned = [
                        [clean_text(thread.data["text"][j])]
                        for j in range(total)
                        if thread.add_progress(percent=round(j / (total - 1) * 100))
                        and bar.progress(
                            thread.progress,
                            f"{self.translate(word="Worker")}-{(count)} {self.translate(word="In progress...") if thread.progress<100 else self.translate(word="Completed")}({thread.progress} %)",
                        )
                    ]
                    data.extend(data_cleaned)
                elif total == 1:
                    percent = 100
                    data_cleaned = [[clean_text(thread.data["text"][0])]]
                    bar.progress(
                        percent,
                        f"{self.translate(word="Worker")}-{(count)} {self.translate(word="Completed")} ({percent} %)",
                    )
                    data.extend(data_cleaned)
                else:
                    bar.empty()
        return data

    def threads_make_predictions(
        self,
        threads: list[PredictThread],
    ) -> list:
        data = []
        with st.spinner(
            text=f"{self.translate(word="Workers in progress...")}({self.translate(word="Total workers")} = {len(threads)})",
            show_time=True,
        ):

            for i, thread in enumerate(threads):
                bar = st.progress(0)
                total = len(thread.data)
                count = i + 1
                if total > 1:
                    data_predict = [
                        [
                            thread.data["text"][j],
                            get_important_words_cloud(thread.data["text"][j]),
                            predict(
                                [thread.data["text"][j]],
                                model=thread.selected_model,
                            ),
                        ]
                        for j in range(total)
                        if thread.add_progress(percent=round(j / (total - 1) * 100))
                        and bar.progress(
                            thread.progress,
                            f"{self.translate(word="Worker")}-{(count)} {self.translate(word="In progress...") if thread.progress<100 else self.translate(word="Completed")}({thread.progress} %)",
                        )
                    ]
                    data.extend(data_predict)
                elif total == 1:
                    percent = 100
                    data_predict = [
                        [
                            thread.data["text"][0],
                            get_important_words_cloud(thread.data["text"][0]),
                            predict(
                                [thread.data["text"][0]],
                                model=thread.selected_model,
                            ),
                        ]
                    ]

                    bar.progress(
                        percent,
                        text=f"{self.translate(word="Worker")}-{(count)} {self.translate(word="Completed")}({percent} %)",
                    )
                    data.extend(data_predict)

        return data

    def get_slices(self, data: pd.DataFrame, nb_threads: int) -> list[tuple[int, int]]:
        total = len(data)
        q, r = divmod(data.shape[0], nb_threads)  # set thread

        # create slices
        slices = [(q * i, q * (i + 1)) for i in range(nb_threads)]
        slices = slices if r == 0 else [*slices, (slices[-1][1], total)]
        return slices

    def build_threads_predicter(
        self, data: pd.DataFrame, nb_threads: int, selected_model: str
    ) -> list[PredictThread]:
        slices = self.get_slices(data, nb_threads)
        threads = [
            PredictThread(
                data=data[slices[i][0] : slices[i][1]], selected_model=selected_model
            )
            for i in range(len(slices))
        ]
        return threads

    def build_threads_cleaner(
        self, data: pd.DataFrame, nb_threads: int
    ) -> list[CleanerThread]:

        slices = self.get_slices(data, nb_threads)

        threads = [
            CleanerThread(
                data=data[slices[i][0] : slices[i][1]],
            )
            for i in range(len(slices))
        ]

        return threads

    def get_words_occurences(self, join_words: str) -> pd.Series:
        words_count = pd.Series([w for w in join_words.split() if len(w.strip())])
        words_count.dropna(inplace=True)
        return words_count.value_counts(ascending=False)

    def words_slicing(self, series: pd.Series) -> tuple[list, int]:
        T = 1_000
        slices = []
        q, r = divmod(len(series), T)
        if q > 0:
            slices = [[i * T, (i + 1) * T] for i in range(q)]
        if r > 0:
            slices.append([q * T, len(series)])
        return slices, T

    def get_pie_figure(self, df_table: pd.Series, title: str):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_title(title)
        data = {}
        # table is already has indexes transformed
        polarity_labels = df_table.index.to_list()
        for _, val in enumerate(polarity_labels):
            if val == self.translate(word="Positive"):
                data[val] = {"value": df_table[val], "color": "#28a745"}
            else:
                data[val] = {"value": df_table[val], "color": "#dc3545"}

        X = [data[key]["value"] for _, key in enumerate(polarity_labels)]
        colors = [data[key]["color"] for _, key in enumerate(polarity_labels)]
        text_properties = {"color": "black", "fontsize": 12, "fontweight": "bold"}
        patches, _, autotexts = ax.pie(  # type: ignore
            X,
            labels=polarity_labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
            textprops=text_properties,
        )
        # change color of text percent
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")
        ax.legend(
            patches,
            polarity_labels,
            title=self.translate(word="Polarities"),
            loc="best",
        )
        # set equal sciling for pie diagram
        ax.axis("equal")
        return fig

    def set_plot_image_into_zip(self, df_table: pd.Series, title: str):
        pie_buffer = BytesIO()
        # save fig into buffer
        pie_fig = self.get_pie_figure(
            df_table=df_table,
            title=title,
        )
        # save figure into buffer
        pie_fig.savefig(pie_buffer, format="png")
        plt.close(pie_fig)
        return pie_buffer

    def set_df_into_zip(
        self, zf: zipfile.ZipFile, df: pd.DataFrame, filename: str
    ) -> None:
        # Rename columns before to save df into buffer
        df_translate = df.rename(
            {
                "polarity": self.translate(word="polarity"),
                "words": self.translate(word="words"),
                "count": self.translate(word="count"),
            },
            axis=1,
            inplace=False,
        )
        zf.writestr(
            filename,
            df_translate.to_csv(index=True).encode("utf-8"),
        )

    def set_table_summary_values_count_into_zip(
        self, zf, df_data: list[pd.DataFrame], filename: str
    ):
        df = pd.concat(df_data, axis=0)
        df_words = df["polarity"].value_counts(normalize=False)
        df_words.rename(
            {
                "Positive": self.translate(word="Positive"),
                "Negative": self.translate(word="Negative"),
            },
            inplace=True,
        )
        zf.writestr(
            filename,
            df_words.to_csv(index=True).encode("utf-8"),
        )

        return df, df_words

    def display_relative_words_table_metrics(
        self, df: pd.DataFrame, table_metric_title: str
    ):
        col_polarity_name = self.translate(word="polarity")
        positive_val = self.translate(word="Positive")
        negative_val = self.translate(word="Negative")
        self.plot_pie_diagram(
            col_polarity_name=col_polarity_name,
            positive_val=positive_val,
            negative_val=negative_val,
            df_copy=df.copy(),
            title=table_metric_title,
        )

    def plot_word_cloud(
        self, words_occurences: pd.Series, title: str, color: str
    ) -> None:
        words_cloud = WordCloud(
            width=900,
            height=600,
            background_color=color,
            random_state=0,
            collocations=False,
        ).generate_from_frequencies(words_occurences)

        st.markdown(f"**{title}**")
        st.image(words_cloud.to_array())

    def get_df_from_occurences(
        self, words_occurences: pd.Series, positive: bool
    ) -> pd.DataFrame:
        names_words = list(words_occurences.index)
        freq_words = list(words_occurences.values)
        columns = ["words", "count", "polarity"]
        data = [
            [names_words[i], freq_words[i], "Positive" if positive else "Negative"]
            for i in range(len(words_occurences))
        ]

        df_words = pd.DataFrame(data=data, columns=columns).dropna(inplace=False)
        return df_words

    def plot_words_freq(
        self, title: str, words_occurences: pd.Series, positive: bool
    ) -> pd.DataFrame:
        df_words = self.get_df_from_occurences(words_occurences, positive)
        col_polarity_name = self.translate(word="polarity")
        col_words_name = self.translate(word="words")
        col_count_name = self.translate(word="count")
        positive_val = self.translate(word="Positive")
        negative_val = self.translate(word="Negative")
        # get copy of dataframe and apply target value translate
        df_copy = df_words.copy()
        df_copy.rename(
            {
                "polarity": col_polarity_name,
                "words": col_words_name,
                "count": col_count_name,
            },
            axis=1,
            inplace=True,
        )
        df_copy[col_polarity_name] = df_copy[col_polarity_name].apply(
            lambda val: positive_val if val == "Positive" else negative_val
        )
        fig = px.bar(
            data_frame=df_copy,
            x=col_words_name,
            y=col_count_name,
            hover_name=col_words_name,
            hover_data=col_count_name,
            title=title,
        )

        st.plotly_chart(fig)

        return df_copy

    def display_words_polarity_graphes(
        self, series_polarity: pd.Series, positive: bool
    ) -> pd.DataFrame | None:
        st.markdown(
            f"#### #{self.translate("Positives words") if positive else self.translate("Negatives words")}",
            unsafe_allow_html=True,
        )
        w_slices, T = self.words_slicing(series=series_polarity)
        slice_index = st.selectbox(
            label=self.translate(word="Pages"),
            options=list(range(len(w_slices))),
            format_func=lambda v: f"{v + 1}",
            index=0,
        )

        df_pos = None
        if slice_index + 1:
            _col_2, _col_3 = st.columns(2, vertical_alignment="center")
            (_col_4,) = st.columns(1, vertical_alignment="center")
            with st.container():
                with _col_2:
                    # get words by slice
                    s = series_polarity[
                        w_slices[slice_index][0] : w_slices[slice_index][1]
                    ]

                    # remove nan value
                    s.dropna(inplace=True)

                    join_words = " ".join(s.apply(str))
                    series_occurences = self.get_words_occurences(join_words)
                    self.plot_word_cloud(
                        series_occurences,
                        title=(
                            self.translate(word="Positives words cloud")
                            if positive
                            else self.translate(word="Negatives words cloud")
                        ),
                        color="white" if positive else "black",
                    )
                with _col_3:
                    df_pos = self.plot_words_freq(
                        title=(
                            self.translate(word="Positives words frequencies")
                            if positive
                            else self.translate(word="Negatives words frequencies")
                        ),
                        words_occurences=series_occurences,
                        positive=positive,
                    )

                    with _col_4:
                        st.markdown(f"<br>", unsafe_allow_html=True)
                        st.markdown(
                            f"{ self.translate(word="Positives words frequencies") if positive else self.translate(word="Negatives words frequencies")}({self.translate(word="Total")}= {len(df_pos)})"
                        )
                        st.dataframe(
                            df_pos.sort_values(
                                by=self.translate(word="count"), ascending=False
                            ).reset_index(drop=True)
                        )
        return df_pos
