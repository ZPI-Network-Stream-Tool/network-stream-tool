from io import TextIOWrapper
from pathlib import Path
from typing import LiteralString

import pandas as pd
from scipy.io import mminfo, mmread

from .processing_interface import FileProcessingStrategy


class MTXFile(FileProcessingStrategy):
    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def get_type_hint(self) -> LiteralString:
        return "The given edge is a tuple. Access its data by indexing: 0 - source node, 1 - destination node, (optionally) 2 - weight of the edge."

    def get_reader(self, file_stream: TextIOWrapper) -> TextIOWrapper:
        return file_stream

    def set_headers(self, reader: TextIOWrapper) -> None:
        # opening the same file multiple times in one process is safe (using the defult read-only mode)
        # each time a new file object iterator is created - no shared state between them exists

        # checking the header and comment count and iterating the main reader accordingly
        with open(self._file_path) as file:
            comment_count = 1
            for line in file:
                if line.startswith("%"):
                    comment_count += 1
                    continue
                else:
                    break

        for _ in range(comment_count):
            next(reader)

        self._headers = mminfo(self._file_path)

    def process_row(self, row: str) -> tuple[int, int] | tuple[int, int, float]:
        # currently the formatting is based on the demo datasets, might not encapsulate all .mtx possibilities
        split_row = row.rstrip().split(" ")
        result = (0, 0)
        if len(split_row) == 2:
            result = (int(split_row[0]), int(split_row[1]))
        elif len(split_row) == 3:
            result = (int(split_row[0]), int(split_row[1]), float(split_row[2]))
        return result

    def get_dataframe(self) -> pd.DataFrame:
        matrix = mmread(self._file_path)
        dense_matrix = matrix.todense()  # type: ignore

        return pd.DataFrame(dense_matrix)
