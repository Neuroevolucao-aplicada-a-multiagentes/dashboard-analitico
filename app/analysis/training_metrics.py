"""Training metrics placeholders."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd



def summarize_training_metrics(training_data: "pd.DataFrame") -> dict[str, Any]:
    """Return a minimal training metrics summary.

    Detailed metric definitions depend on the formal data contract.
    """

    return {"rows": int(training_data.shape[0]), "columns": list(training_data.columns)}
