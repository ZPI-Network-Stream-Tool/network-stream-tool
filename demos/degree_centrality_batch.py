from typing import Any

import networkx as nx
import pandas as pd

from algorithms._config.interfaces import BatchAlgorithm, numeric


class DegreeCentralityBatch(BatchAlgorithm):
    def __init__(self) -> None:
        self.results = {}

    def calculate_property(self, data: pd.DataFrame) -> None:
        graph_type = nx.MultiDiGraph()

        graph = nx.from_pandas_edgelist(
            data,
            source="start_stop",
            target="end_stop",
            edge_attr=None,
            create_using=graph_type,
        )
        self.results = nx.degree_centrality(graph)

    def submit_results(self) -> list[tuple[Any, numeric]]:
        degree_centralities = sorted(
            self.results.items(), key=lambda item: item[1], reverse=True
        )
        return degree_centralities