from htmltools import Tag
from shiny import ui


def dataset() -> tuple[Tag, ...]:
    return (
        ui.input_selectize(
            "select_dataset",
            "Dataset",
            {
                "Provided by me": {"0": "Custom dataset"},
                "Presupplied": {"1": "Wroclaw's public transport connections"},
            },
            selected="1",
        ),
        ui.panel_conditional(
            "input.select_dataset == 0",
            ui.input_file("dataset_path", "Path to dataset"),
            ui.input_switch("with_preprocessing", "Preprocess data", False),
        ),
    )
