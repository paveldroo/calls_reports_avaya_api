from django.core.management import BaseCommand

from calls.api.api_data_getter import import_call_legs
from calls.utils import create_calls_from_call_legs
from reports.generate_report.generate_report import generate_and_send_calls_report


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        start_date = '2019-11-28'
        end_date = '2019-11-29'
        import_call_legs(start_date, end_date)
        create_calls_from_call_legs(start_date, end_date)

        generate_and_send_calls_report()
        return
