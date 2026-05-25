from collections.abc import Callable
from threading import Thread
from typing import Any, Iterable, Mapping

import pandas as pd

from utils.helpers import clean_text, predict


class WorkerThread:
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data.reset_index(inplace=False)
        self.content = []
        self.progress = 0

    def add_progress(self, percent: float):
        self.progress = percent
        return True


class CleanerThread(WorkerThread):
    def __init__(self, data: pd.DataFrame):
        super().__init__(data=data)


class PredictThread(WorkerThread):
    def __init__(self, selected_model: str, data: pd.DataFrame):
        super().__init__(data=data)
        self.selected_model = selected_model
