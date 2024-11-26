from datetime import datetime
from pathlib import Path
from typing import Any

import faicons as fa
import pandas as pd
import plotly.express as px
from htmltools import Tag
from plotly.graph_objs import Figure
from shiny import Inputs, reactive, render, ui
from shinywidgets import render_widget

from app.server.logic.actions import save_results
from app.server.logic.runner import Runner


def get_experiment_name(experiment_name: str) -> str | Path:
    current_date = Path(datetime.now().strftime("%Y-%m-%d"))
    current_time = Path(datetime.now().strftime("%H_%M_%S"))
    ui.update_text(
        "experiment_name", placeholder=f"{str(current_date)} {str(current_time)}"
    )
    return experiment_name or current_date / current_time


def get_size_with_unit(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size} {unit}"
        size //= 1024
    return "Very large"


def server_results(input: Inputs, results: dict[str, reactive.Value]):
    @reactive.calc
    def plotly_template() -> str:
        return "plotly_dark" if input.mode() == "dark" else "plotly"

    @reactive.calc
    def get_streaming_node_rank() -> pd.DataFrame:
        return pd.DataFrame(
            results["streaming_results"].get(), columns=["node", "value"]
        )

    @render.ui
    def streaming_node_rank() -> Tag:
        return ui.card(
            ui.card_header("Streaming node rank"),
            render.data_frame(get_streaming_node_rank),
            full_screen=True,
        )

    @reactive.calc
    def get_batch_node_rank() -> pd.DataFrame:
        return pd.DataFrame(results["batch_results"].get(), columns=["node", "value"])

    @render.ui
    def batch_node_rank() -> Tag | None:
        return ui.card(
            ui.card_header("Batch node rank"),
            render.data_frame(get_batch_node_rank),
            full_screen=True,
        )

    @reactive.calc
    def get_calculation_time_plot() -> Figure:
        df = pd.DataFrame(results["calculation_time"].get(), columns=["time [ns]"])
        line_plot = px.line(
            df,
            y=df.columns.values[0],
            labels={"index": "edge"},
            template=plotly_template(),
        )
        return line_plot

    @render.ui
    def calculation_time_plot() -> Tag:
        return ui.card(
            ui.card_header("Calculation time"),
            render_widget(get_calculation_time_plot),  # type: ignore
            full_screen=True,
        )

    @reactive.calc
    def get_memory_history_plot() -> Figure:
        edge, memory = zip(*results["memory_history"].get())
        df = pd.DataFrame({"edge": edge, "memory": memory})
        line_plot = px.line(
            df,
            x="edge",
            y="memory",
            labels={"edge": "edge", "memory": "memory [B]"},
            template=plotly_template(),
        )
        return line_plot

    @render.ui
    def memory_history_plot() -> Tag:
        return ui.card(
            ui.card_header("Memory history"),
            render_widget(get_memory_history_plot),  # type: ignore
            full_screen=True,
        )

    @reactive.calc
    def get_comparison_metrics() -> tuple[float | Any, float | Any]:
        runner: Runner = results["runner"].get()
        order, cardinality = (
            input.node_rank_order() == "Descending",
            input.node_rank_cardinality(),
        )
        jaccard_similarity = runner.get_jaccard_similarity(order, cardinality)
        streaming_accuracy = runner.get_streaming_accuracy(order, cardinality)
        return jaccard_similarity, streaming_accuracy

    @render.text
    def total_edge_count() -> str:
        runner: Runner = results["runner"].get()
        return str(runner.edge_count)

    @render.text
    def dataset_size() -> str:
        runner: Runner = results["runner"].get()
        return get_size_with_unit(runner.dataset_size)

    @render.text
    def jaccard_similarity() -> str:
        return f"{get_comparison_metrics()[0]:.4g}"

    @render.text
    def streaming_accuracy() -> str:
        return f"{get_comparison_metrics()[1]:.4g}"

    @render.ui
    def metrics_with_batch() -> Tag:
        return ui.card(
            ui.card_header("Comparison metrics"),
            ui.row(
                ui.column(
                    6,
                    ui.value_box(
                        "Total edge count",
                        ui.output_text("total_edge_count"),
                        showcase=fa.icon_svg("circle-nodes", margin_left="2rem"),
                    ),
                ),
                ui.column(
                    6,
                    ui.value_box(
                        "Size of dataset",
                        ui.output_text("dataset_size"),
                        showcase=fa.icon_svg("database", margin_left="2rem"),
                    ),
                ),
                class_="value-box-row",
            ),
            ui.row(
                ui.input_selectize(
                    "node_rank_order",
                    label="Sorting order",
                    choices=["Ascending", "Descending"],
                    width="50%",
                ),
                ui.input_numeric(
                    "node_rank_cardinality",
                    label="Cardinality of node rank",
                    value=10,
                    min=1,
                    width="50%",
                ),
            ),
            ui.row(
                ui.column(
                    6,
                    ui.value_box(
                        "Jaccard similarity",
                        ui.output_text("jaccard_similarity"),
                        showcase=fa.icon_svg("overlap", margin_left="2rem"),
                    ),
                ),
                ui.column(
                    6,
                    ui.value_box(
                        "Streaming accuracy",
                        ui.output_text("streaming_accuracy"),
                        showcase=fa.icon_svg("bullseye", margin_left="2rem"),
                    ),
                ),
                class_="value-box-row",
            ),
            height="100%",
        )

    @render.ui
    def metrics_no_batch() -> Tag:
        return ui.card(
            ui.card_header("Comparison metrics"),
            ui.value_box(
                "Total edge count",
                ui.output_text("total_edge_count"),
                showcase=fa.icon_svg("circle-nodes", margin_left="2rem"),
            ),
            ui.tags.div(class_="flex-divider"),
            ui.value_box(
                "Size of dataset",
                ui.output_text("dataset_size"),
                showcase=fa.icon_svg("database", margin_left="2rem"),
            ),
        )

    @render.ui
    @reactive.event(input.run_experiment)
    def results_first_row() -> Tag:
        columns = (
            (
                ui.output_ui("streaming_node_rank"),
                ui.output_ui("batch_node_rank"),
                ui.output_ui("metrics_with_batch"),
            )
            if input.with_batch()
            else (
                ui.output_ui("streaming_node_rank"),
                ui.output_ui("calculation_time_plot"),
            )
        )
        return ui.layout_columns(
            *columns,
            max_height="48%",
            col_widths=[3, 3, 6] if input.with_batch() else [3, 9],
        )

    @render.ui
    @reactive.event(input.run_experiment)
    def results_second_row() -> Tag:
        columns = (
            (
                ui.output_ui("memory_history_plot"),
                ui.output_ui("calculation_time_plot"),
            )
            if input.with_batch()
            else (ui.output_ui("metrics_no_batch"), ui.output_ui("memory_history_plot"))
        )
        return ui.layout_columns(
            *columns,
            max_height="49%",
            col_widths=[6, 6] if input.with_batch() else [3, 9],
        )

    @render.ui
    @reactive.event(input.run_experiment)
    def save_results_button() -> Tag:
        return ui.input_task_button(
            "save_results",
            "Save results",
            icon=fa.icon_svg("floppy-disk"),
            label_busy="Saving...",
            class_="btn-outline-success",
        )

    @ui.bind_task_button(button_id="save_results")
    @reactive.extended_task
    async def save_results_task(
        experiment_name: str, results: str, plots: list
    ) -> None:
        save_results(experiment_name, results, plots)

    @reactive.effect
    @reactive.event(input.save_results)
    def _() -> None:
        results = get_streaming_node_rank().to_markdown() + "\n"
        if input.with_batch():
            results += get_batch_node_rank().to_markdown() + "\n"
        calculation_time_plot = (
            "calculation_time_per_edge",
            get_calculation_time_plot(),
        )
        memory_history_plot = ("memory_history", get_memory_history_plot())
        plots = [calculation_time_plot, memory_history_plot]
        save_results_task(input.experiment_name(), results, plots)