"""Comparative analysis placeholders."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd



def compare_training_and_execution(
    training_metrics: "pd.DataFrame",
    execution_metrics: "pd.DataFrame",
) -> dict[str, Any]:
    """Return a minimal comparison summary between two metric tables."""

    return {
        "training_rows": int(training_metrics.shape[0]),
        "execution_rows": int(execution_metrics.shape[0]),
    }
