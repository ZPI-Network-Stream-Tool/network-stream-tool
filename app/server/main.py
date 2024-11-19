from shiny import reactive, ui

from .reactives import (
    server_edit,
    server_results,
    server_run_experiment,
    server_selectize,
)

errors = reactive.value()

streaming_results = reactive.value()
batch_results = reactive.value()
preprocessing_time = reactive.value()
calculation_time = reactive.value()
memory_history = reactive.value()

results = {
    "streaming": streaming_results,
    "batch": batch_results,
    "preprocessing_time": preprocessing_time,
    "calculation_time": calculation_time,
    "memory": memory_history,
}


def server(input, output, session):
    server_selectize(input)
    server_edit(input)
    server_run_experiment(input, results, errors)
    server_results(input, results)

    @reactive.effect
    @reactive.event(errors)
    def modal_error_display():
        m = ui.modal(str(errors.get()), title="Error", easy_close=True)
        ui.modal_show(m)