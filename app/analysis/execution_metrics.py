"""Execution metrics placeholders."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd



def summarize_execution_metrics(execution_data: "pd.DataFrame") -> dict[str, Any]:
    """Return a minimal execution metrics summary.

    Detailed metric definitions depend on the formal data contract.
    """

    return {"rows": int(execution_data.shape[0]), "columns": list(execution_data.columns)}
