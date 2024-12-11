from io import TextIOWrapper
from pathlib import Path
from typing import Callable, Sequence

import pandas as pd

from .processing_interface import FileProcessingStrategy


def processing_placeholder(line: str):
    return line


class TEXTFile(FileProcessingStrategy):
    def __init__(
        self, file_path: Path, processing_function=processing_placeholder
    ) -> None:
        self._file_path = file_path
        self._process: Callable[[str], Sequence | dict] = processing_function

    def get_reader(self, file_stream: TextIOWrapper) -> TextIOWrapper:
        return file_stream

    def set_headers(self, reader: TextIOWrapper) -> None:
        self._headers = []

    def process_row(self, row: str) -> str:
        return row

    def get_dataframe(self) -> pd.DataFrame:
        # this is more of an placeholer solution
        result = []
        with open(self._file_path, encoding="utf-8") as file:
            for row in file:
                result.append(self._process(row))

        return pd.DataFrame(result)
