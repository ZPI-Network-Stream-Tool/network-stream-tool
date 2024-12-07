import sys
from enum import StrEnum
from pathlib import Path


class AlgorithmType(StrEnum):
    PREPROCESSING = "preprocessing"
    BATCH = "batch"
    STREAMING = "streaming"


EXECUTABLE = sys.executable.split("\\")[-1]
parent_index = 3 if EXECUTABLE == "python.exe" else 4


DEMOS_DIR = Path(__file__).resolve().parents[parent_index] / "demos"
CONNECTIONS_CSV_FILE = DEMOS_DIR / "connections.csv"
CONNECTION_PREPROCESSING_FUNCTION_FILE = DEMOS_DIR / "connection_preprocessing.py"
DEGREE_CENTRALITY_BATCH_ALGORITHM_FILE = DEMOS_DIR / "degree_centrality_batch.py"
DEGREE_CENTRALITY_STREAM_ALGORITHM_FILE = DEMOS_DIR / "degree_centrality_stream.py"

ALGORITHMS_DIRECTORY = Path(__file__).parents[parent_index] / "algorithms"
ALGORITHM_TEMPLATES_DIRECTORY = ALGORITHMS_DIRECTORY / "_config" / "templates"

EXPERIMENTS_DIRECTORY = Path(__file__).parents[parent_index] / "experiments"
