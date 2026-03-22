"""Celery Beat schedule configuration."""

from celery.schedules import crontab

beat_schedule = {
    "scrape-live-football": {
        "task": "scrap.live",
        "schedule": 60.0,
        "args": (),
        "kwargs": {"params": {"sport": "football"}},
    },
    "scrape-live-tennis": {
        "task": "scrap.live",
        "schedule": 60.0,
        "args": (),
        "kwargs": {"params": {"sport": "tennis"}},
    },
    "scrape-live-hockey": {
        "task": "scrap.live",
        "schedule": 120.0,
        "args": (),
        "kwargs": {"params": {"sport": "hockey"}},
    },
    "scrape-events-hourly": {
        "task": "scrap.events",
        "schedule": 3600.0,
        "args": (),
        "kwargs": {"params": {}},
    },
    "scrape-predictions-hourly": {
        "task": "scrap.predictions",
        "schedule": 3600.0,
        "args": (),
        "kwargs": {"params": {"upcoming": True}},
    },
    "scrape-predictions-quarter-hourly": {
        "task": "scrap.predictions",
        "schedule": 900.0,
        "args": (),
        "kwargs": {"params": {"upcoming": True}},
    },
    "scrape-leagues-daily": {
        "task": "scrap.leagues",
        "schedule": crontab(hour=6, minute=20),
        "args": (),
        "kwargs": {"params": {}},
    },
    "scrape-teams-daily": {
        "task": "scrap.teams",
        "schedule": crontab(hour=6, minute=30),
        "args": (),
        "kwargs": {"params": {}},
    },
}
