import pandas as pd
import joblib
import os
from os.path import dirname, abspath, join
import spacy
import base64
import re, string
from pathlib import Path
import shutil

from utils.tools import DICTIONNARY

USER_FOLDER_ANALYSE_NAME = "analyses"
USER_FOLDER_RESULTS_NAME = "results"


nlp = spacy.load("fr_core_news_lg")

__DIR__ = dirname(dirname(abspath(__file__)))

STORAGE_DIR = join(__DIR__, "src", "storage")
MODELS_DIR = join(__DIR__, "src", "models")

MODELS = ["LR", "SVC"]
METRCIS = {"LR": {"auc": 0.83, "accuracy": 0.75}, "SVC": {"auc": 0.96, "accuracy": 0.9}}
DIAGRAMS = ["pie", "histogram"]
WORDS_SENDS = ["VERB", "ADJ"]
MAX_TOKENS = 1_000_000
COLUMNS_DATA_POLARITY = ["text", "word", "polarity"]


def get_doc_text(text: str) -> str:
    doc = nlp(text=text)
    wds = [w.lemma_ for w in doc if w.pos_ in WORDS_SENDS]
    return " ".join(wds)


def get_important_words_cloud(texts: str) -> str:
    total = len(texts)
    if total >= MAX_TOKENS:
        T = MAX_TOKENS / 2
        q, r = divmod(len(texts), MAX_TOKENS)
        # get text slices count
        nb_slices = 2 * q
        # get texts selection by slices
        texts_selected = [
            get_doc_text(texts[T * i : T * (i + 1)]) for i in range(nb_slices)
        ]
        # get rest of texts slice if present
        if r > 0:
            texts_selected.extend([get_doc_text(texts[T * (nb_slices) : total])])
        return (" ".join(texts_selected)).strip()
    else:
        return get_doc_text(text=texts).strip()


def init_user_directory(user_id: str) -> bool:
    try:
        if not os.path.exists(join(__DIR__, STORAGE_DIR)):
            os.mkdir(STORAGE_DIR)
        for _, model in enumerate(MODELS):
            fd_analyses = Path(
                join(__DIR__, STORAGE_DIR, user_id, model, USER_FOLDER_ANALYSE_NAME)
            )
            fd_results = Path(
                join(__DIR__, STORAGE_DIR, user_id, model, USER_FOLDER_RESULTS_NAME)
            )
            for _, file in enumerate([fd_analyses, fd_results]):
                if not file.parent.parent.exists():
                    os.mkdir(file.parent.parent)
                if not file.parent.exists():
                    os.mkdir(file.parent)
                if not file.exists():
                    os.mkdir(file)
        return True
    except:
        return False


def save_data_polarity(df: pd.DataFrame, user_id: str, model: str) -> pd.DataFrame:
    user_data_polarity = Path(
        join(
            __DIR__,
            STORAGE_DIR,
            str(user_id),
            model,
            USER_FOLDER_RESULTS_NAME,
            "data_polarity.csv",
        )
    )
    if user_data_polarity.parent.exists():
        df.to_csv(user_data_polarity)
        return df[["text", "polarity"]]
    else:
        os.mkdir(user_data_polarity.parent)
        df.to_csv(user_data_polarity)
        return df[["text", "polarity"]]


def get_data_polarity(user_id: str, model: str) -> pd.DataFrame | None:
    try:
        user_file = Path(
            join(
                __DIR__,
                STORAGE_DIR,
                str(user_id),
                model,
                USER_FOLDER_RESULTS_NAME,
                "data_polarity.csv",
            )
        )
        if user_file.exists():
            data = pd.read_csv(user_file, usecols=COLUMNS_DATA_POLARITY)
            return data
        else:
            return None
    except:
        return None


def get_data(user_id: str, model: str) -> None | pd.DataFrame:
    """
    Retrieve user data from a CSV file if it exists.
    Args:
        user_id (str): The unique identifier for the user whose data is to be retrieved.
    Returns:
        pd.DataFrame | None: A DataFrame containing the 'text' column from the user's original data if the file exists,
        otherwise None.
    """

    try:
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
        if user_data_original.exists():
            data = pd.read_csv(user_data_original, usecols=["text"])
            return data
        else:
            return None
    except:
        return None


def get_data_cleaned(user_id: str, model: str) -> None | pd.DataFrame:
    """
    Retrieves a cleaned data CSV file for a given user and returns its contents as a pandas DataFrame.

    Args:
        user_id (str): The unique identifier for the user whose cleaned data is to be retrieved.

    Returns:
        pd.DataFrame | None: A DataFrame containing the 'text' column from the user's cleaned data file if it exists,
        otherwise None.

    Notes:
        - The function expects the cleaned data file to be located at 'storage/<user_id>/data_cleaned.csv' relative to the current directory.
        - If the file does not exist or an error occurs during reading, the function returns None.
    """
    try:
        user_file = Path(
            join(
                __DIR__,
                STORAGE_DIR,
                str(user_id),
                model,
                USER_FOLDER_ANALYSE_NAME,
                "data_cleaned.csv",
            )
        )
        data = pd.read_csv(user_file, usecols=["text"])
        if user_file.exists():
            return data
        else:
            return None
    except:
        return None


def save_cleaned_data(data: pd.DataFrame, user_id: str, model: str) -> pd.DataFrame:
    """
    Saves the cleaned DataFrame to a CSV file in the user's storage directory.

    Args:
        data (pd.DataFrame): The cleaned data to be saved.
        user_id (str): The unique identifier for the user.

    Returns:
        None | pd.DataFrame: Returns the DataFrame if the file was saved successfully,
        otherwise returns None.

    Notes:
        - The file is saved as 'data_cleaned.csv' under 'storage/<user_id>/' relative to the current directory.
        - If the target directory does not exist, the function returns None and does not save the file.
    """
    user_data_cleaned = Path(
        join(
            __DIR__,
            STORAGE_DIR,
            str(user_id),
            model,
            USER_FOLDER_ANALYSE_NAME,
            "data_cleaned.csv",
        )
    )
    data.to_csv(user_data_cleaned)
    return data[["text"]]


def clean_text(text):
    """
    Cleans and preprocesses input text for sentiment analysis.

    This function performs the following operations on the input text:
        - Removes URLs.
        - Removes HTML tags.
        - Removes punctuation.
        - Removes newline characters.
        - Removes words containing digits.
        - Converts text to lowercase.
        - Removes any remaining non-alphabetic characters (except spaces).
        - Normalizes repeated characters (e.g., "soooo" becomes "soo").
        - Lemmatizes words and removes stopwords using a spaCy language model.

    Args:
        text (str): The input text to be cleaned.

    Returns:
        str: The cleaned and preprocessed text.
    """
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    # Remove HTML tags
    text = re.sub(r"<.*?>", "", text)
    # Remove punctuation
    text = re.sub(f"[{string.punctuation}]", "", text)
    # Remove newlines
    text = re.sub(r"\n", "", text)
    # Remove alphanumeric words (words containing digits)
    text = re.sub(r"\b\w*\d\w*\b", "", text)
    # Convert to lowercase
    text = text.lower()
    # Remove remaining non-alphabetic characters (except spaces)
    text = re.sub(r"[^a-z\s]", "", text)
    # Normalize repeated characters (e.g., "soooo" -> "so")
    text = re.sub(r"(.)\1+", r"\1\1", text)
    # Make lemmatization
    words = [w.lemma_ for w in nlp(text) if not w.is_stop]
    return " ".join(words)


def predict(X: list, model: str) -> tuple:
    """
    Predicts the sentiment of the input data using the specified machine learning model.

    Args:
        X (list): The input features for prediction.
        model (str): The name of the model to use for prediction.
            Accepts "SVC" for Support Vector Machine Classifier or any other value for Logistic Regression.

    Returns:
        tuple: The predicted sentiment label or value.

    Raises:
        FileNotFoundError: If the specified model file does not exist.
        Exception: If there is an error during model loading or prediction.
    """
    try:
        if model == "SVC":
            model_path = join(MODELS_DIR, "svc.model")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            svc_model = joblib.load(model_path)
            return svc_model.predict(X)[0]
        else:
            model_path = join(MODELS_DIR, "LR.model")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            LR_model = joblib.load(model_path)
            return LR_model.predict(X)[0]
    except FileNotFoundError as e:
        raise e
    except Exception as e:
        raise Exception(f"Error during model prediction: {e}")


def get_image(filename: str) -> str:
    """
    Reads an image file from the 'public' directory, encodes its contents in base64, and returns the encoded string.

    Args:
        filename (str): The name of the image file to read.

    Returns:
        str: The base64-encoded string representation of the image file's contents.

    Raises:
        FileNotFoundError: If the specified image file does not exist.
        Exception: For other errors during file reading or encoding.
    """
    try:
        file_path = join(__DIR__, "public", filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")
        with open(file_path, "rb") as file_:
            contents = file_.read()
            data_url = base64.b64encode(contents).decode("utf-8")
        return data_url
    except FileNotFoundError as e:
        raise e
    except Exception as e:
        raise Exception(f"Error reading or encoding image file: {e}")


def drop_user_data(user_id: str) -> bool:
    user_folder = Path(
        join(
            __DIR__,
            STORAGE_DIR,
            user_id,
        )
    )

    try:
        if user_folder.exists():
            shutil.rmtree(path=user_folder, ignore_errors=True)
            return True
        return True
    except:
        return False


def tte(page: str, lang: str, word: str) -> str:
    if (
        lang in list(DICTIONNARY.keys())
        and page in list(DICTIONNARY[lang].keys())
        and word in list(DICTIONNARY[lang][page].keys())
    ):
        return DICTIONNARY[lang][page][word]
    else:
        return word
