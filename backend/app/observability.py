import os


def init_observability():
    """Initialize Sentry and LangSmith if available and configured.
    This is best-effort: failures are logged locally but do not raise.
    """
    # Sentry
    try:
        import sentry_sdk
        ds = os.getenv("SENTRY_DSN")
        if ds:
            sentry_sdk.init(dsn=ds, traces_sample_rate=float(os.getenv("SENTRY_TRACES_RATE", "0.1")))
    except Exception:
        pass

    # LangSmith / LangGraph tracing — best-effort
    try:
        # `langsmith` or langchain integration may be available in the environment
        from langsmith import Client as LangSmithClient
        ls_key = os.getenv("LANGSMITH_API_KEY")
        project = os.getenv("LANGSMITH_PROJECT")
        tracing = os.getenv("LANGSMITH_TRACING", "false").lower() in ("1", "true", "yes")
        if ls_key and tracing:
            # Create a client instance (module-level only) so tests can import
            client = LangSmithClient(api_key=ls_key)
            # Optionally set project name on client if supported
            try:
                client.set_project(project)
            except Exception:
                pass
            globals()["langsmith_client"] = client
    except Exception:
        # LangSmith not installed or not configured — ignore
        pass
