from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

app = Celery('celery', backend='redis://localhost:6379', broker='redis://localhost:6379')

app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ignore other content
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
)

app.conf.beat_schedule = {
    'send_daily_report': {
        'task': 'reports.tasks.send_daily_report',
        # 'schedule': crontab(hour=0, minute=30, day_of_week=1),
        'schedule': timedelta(minutes=2),
    },
}
