import os
from typing import Optional


def initialize_checkpointer_tables() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL must be set to initialize LangGraph checkpointer tables")

    try:
        import langgraph
    except ImportError as exc:
        raise ImportError("langgraph package is not installed") from exc

    saver_cls = getattr(langgraph, "PostgresSaver", None)
    if saver_cls is None:
        saver_cls = getattr(langgraph, "PostgresCheckpointSaver", None)

    if saver_cls is None:
        raise AttributeError("langgraph does not expose a PostgresSaver or PostgresCheckpointSaver class")

    saver = saver_cls.from_conn_string(database_url)
    create_fn = getattr(saver, "create_table", None) or getattr(saver, "create_tables", None)
    if create_fn is None:
        raise AttributeError("LangGraph checkpointer saver does not support table creation via create_table/create_tables")

    create_fn()
    print("LangGraph checkpointer tables initialized.")
