from abc import ABC, abstractmethod
from io import TextIOWrapper
from typing import Any, LiteralString

import pandas as pd


class FileProcessingStrategy(ABC):
    @abstractmethod
    def get_type_hint(self) -> LiteralString: ...

    @abstractmethod
    def get_reader(self, file_stream: TextIOWrapper) -> Any: ...

    # @abstractmethod
    # def skip_header_lines(self, reader):
    #     ...

    @abstractmethod
    def set_headers(self, reader: Any) -> None: ...

    @abstractmethod
    def process_row(self, row: Any) -> Any: ...

    @abstractmethod
    def get_dataframe(self) -> pd.DataFrame: ...
