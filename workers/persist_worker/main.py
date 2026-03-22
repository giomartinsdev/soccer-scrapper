"""Persist worker main entry point."""

from workers.persist_worker.slices.persist.tasks import persist_app


if __name__ == "__main__":
    persist_app.start()
