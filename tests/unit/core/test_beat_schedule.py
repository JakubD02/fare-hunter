from celery.schedules import crontab

from app.celery_app import celery_app
from app.core.config import settings

PRICE_TASK = "app.tasks.price_tasks.fetch_all_prices_periodic"


def _price_fetch_entries() -> list[dict]:
    return [entry for entry in settings.CELERY_BEAT_SCHEDULE.values() if entry["task"] == PRICE_TASK]


class TestBeatSchedule:
    """Celery Beat must fetch prices every 8 hours (00:00, 08:00, 16:00 Warsaw time)"""

    def test_price_fetch_task_is_scheduled(self):
        assert len(_price_fetch_entries()) == 1

    def test_price_fetch_uses_crontab(self):
        """crontab gives fixed hours; timedelta would drift after each beat restart"""
        (entry,) = _price_fetch_entries()
        assert isinstance(entry["schedule"], crontab)

    def test_price_fetch_runs_at_0_8_16(self):
        (entry,) = _price_fetch_entries()
        schedule = entry["schedule"]

        assert schedule.hour == {0, 8, 16}
        assert schedule.minute == {0}

    def test_price_fetch_runs_every_day(self):
        (entry,) = _price_fetch_entries()
        schedule = entry["schedule"]

        assert schedule.day_of_week == set(range(7))
        assert schedule.day_of_month == set(range(1, 32))
        assert schedule.month_of_year == set(range(1, 13))

    def test_celery_uses_warsaw_timezone(self):
        """Hours above are only Warsaw time if Celery is configured for it"""
        assert celery_app.conf.timezone == "Europe/Warsaw"

    def test_celery_app_loads_schedule_from_settings(self):
        """Guards against the schedule being defined but never wired into Celery"""
        assert celery_app.conf.beat_schedule == settings.CELERY_BEAT_SCHEDULE
