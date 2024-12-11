import traceback
from datetime import datetime
from pathlib import Path
from random import random
from typing import Any

from shiny import Inputs, reactive, ui

from app.server._config import CONNECTIONS_CSV_FILE
from app.server.logic import Runner


class MissingPathError(ValueError):
    def __init__(self, object_name: str) -> None:
        super().__init__(
            f"No {object_name} path was selected. Please provide a valid path to the {object_name}."
        )


def select_dataset(option: str, path: list[dict[str, str]]) -> Path:
    dataset_path = Path()
    match option:
        case "0":
            if path is None:
                raise MissingPathError("dataset")
            dataset_path = Path(path[0]["datapath"])
        case "1":
            dataset_path = CONNECTIONS_CSV_FILE
    return dataset_path


def get_paths(input: Inputs) -> tuple[Any, ...]:
    dataset_path: Path = select_dataset(input.select_dataset(), input.dataset_path())
    preprocess_path: Path | None = (
        input.select_preprocessing() if input.with_preprocessing() else None
    )
    streaming_path: Path = input.select_streaming()
    batch_path: Path | None = input.select_batch() if input.with_batch() else None

    return dataset_path, preprocess_path, streaming_path, batch_path


def server_run_experiment(
    input: Inputs,
    results: dict[str, reactive.Value],
    errors: reactive.Value,
) -> None:
    @ui.bind_task_button(button_id="run_experiment")
    @reactive.extended_task
    async def run_experiment(runner: Runner) -> None:
        try:
            runner.validate_implementation()
            runner.run_experiment()
        except Exception as exception:
            message = traceback.format_exc()
            if isinstance(exception, UnicodeDecodeError):
                message = (
                    "The dataset you provided is not in a UTF-8-compatible encoding."
                )
            elif isinstance(exception, TypeError):
                message = str(exception)
            errors.set((random(), message))
        else:
            stream_results = sorted(
                runner.get_stream_results(), key=lambda item: item[1], reverse=True
            )
            batch_results = sorted(
                runner.get_batch_results(), key=lambda item: item[1], reverse=True
            )

            if type(stream_results) is dict:
                stream_results = stream_results.items()
            elif type(stream_results) is not list:
                stream_results = list(stream_results)

            if type(batch_results) is dict:
                batch_results = batch_results.items()
            elif type(batch_results) is not list:
                batch_results = list(batch_results)

            results["runner"].set(runner)
            results["streaming_results"].set(stream_results)
            results["batch_results"].set(batch_results)
            results["calculation_time"].set(runner.calculation_time_per_edge)
            results["memory_usage"].set(runner.memory_usage)

    @reactive.effect
    @reactive.event(input.run_experiment)
    def _() -> None:
        try:
            dataset_path, preprocess_path, streaming_path, batch_path = get_paths(input)
            runner = Runner(
                dataset_path=dataset_path,
                preprocessing_path=preprocess_path,
                streaming_path=streaming_path,
                batch_path=batch_path,
            )
            run_experiment(runner)
            ui.update_text(
                "experiment_name", value=datetime.now().strftime("%Y-%m-%d %H_%M_%S")
            )
        except Exception as exception:
            message = traceback.format_exc()
            if isinstance(exception, MissingPathError):
                message = str(exception)
            elif isinstance(exception, AttributeError):
                message = "No implementation was selected for one of the functions/algorithms."
            errors.set((random(), message))
