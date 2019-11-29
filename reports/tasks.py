from calls.utils import create_calls_from_call_legs
from reports.generate_report.generate_report import generate_and_send_calls_report
from support_calls.celery import app


@app.task
def send_daily_report():
    create_calls_from_call_legs()
    generate_and_send_calls_report()
