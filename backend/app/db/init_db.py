import os
import sys
from sqlalchemy.exc import SQLAlchemyError
from app.db.engine import engine
from app.db.models import Base


def create_app_tables() -> None:
    """Create application database tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)


def initialize_checkpointer_tables() -> None:
    """Initialize LangGraph Postgres checkpointer tables if supported."""
    from app.graph.checkpointer import initialize_checkpointer_tables as init_cp

    init_cp()


def main() -> int:
    try:
        create_app_tables()
        print("App database tables created or already exist.")
    except SQLAlchemyError as exc:
        print(f"Failed to create app tables: {exc}", file=sys.stderr)
        return 1

    try:
        initialize_checkpointer_tables()
    except Exception as exc:
        print(f"Warning: checkpointer table initialization skipped: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
