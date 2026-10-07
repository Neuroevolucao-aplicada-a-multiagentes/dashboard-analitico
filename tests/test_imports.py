"""Basic import smoke tests."""

from importlib import import_module



def test_project_modules_can_be_imported() -> None:
    """Ensure core project modules are importable."""

    modules = [
        "app",
        "app.data.config",
        "app.data.local_loader",
        "app.data.sample_loader",
        "app.data.supabase_client",
        "app.data.supabase_loader",
        "app.data.data_contract",
        "app.data.data_manager",
        "app.analysis.training_metrics",
        "app.analysis.execution_metrics",
        "app.analysis.comparative_analysis",
        "app.visualizations.fitness_evolution",
    ]

    for module in modules:
        import_module(module)
