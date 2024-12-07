from csv import DictReader
from io import TextIOWrapper
from pathlib import Path
from typing import LiteralString

import pandas as pd

from .processing_interface import FileProcessingStrategy


class CSVFile(FileProcessingStrategy):
    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def get_type_hint(self) -> LiteralString:
        return "The edge is a dictionary. Its keys are the headers of the supplied .csv file."

    def get_reader(self, file_stream: TextIOWrapper) -> DictReader[str]:
        return DictReader(file_stream)

    def set_headers(self, reader: DictReader[str]) -> None:
        self._headers = reader.fieldnames

    def process_row(self, row: dict) -> dict:
        return row

    def get_dataframe(self) -> pd.DataFrame:
        return pd.read_csv(self._file_path)
