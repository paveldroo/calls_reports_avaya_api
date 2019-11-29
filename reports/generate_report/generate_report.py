import datetime

from django.core.mail import send_mail
from django.db.models import Count
from django.template.loader import render_to_string

from calls.models import CallLeg, Call
from reports.utils import get_report_date_string
from support_calls.constants import EMAIL_FROM, EMAIL_TO
from support_calls.utils import date_range_from_dates


def generate_and_send_calls_report(start_date=None, end_date=None):
    date_range = date_range_from_dates(start_date, end_date)

    report_data = {}
    # Пропущенные звонки
    missed_calls_data = get_missed_calls(date_range)
    report_data.update(missed_calls_data)

    generate_and_send_mail(date_range, report_data)

    # # Вычисляем данные для отчета
    # # Общее количество уникальных звонков (что значит уникальные?)
    # total_calls = get_total_calls(today_calls)
    #
    # # Топ звонящих (сколько штук будет достаточно? топ-3? или всех отсортировать?)
    # top_callers = get_top_callers(today_calls)


def get_total_calls(calls_query):
    total_calls = len(calls_query)
    return total_calls


def get_top_callers(calls_query):
    count = calls_query.values('caller_number').annotate(Count('caller_number')).order_by('-caller_number__count')
    top_callers_list = list(count)[:3]
    return top_callers_list


def get_missed_calls(date_range):
    missed_calls = Call.objects.filter(timestamp__date__range=date_range, answered=False).order_by('-duration')
    missed_calls_cnt = len(missed_calls)

    waiting_seconds = []
    for call in missed_calls:
        waiting_seconds.append(call.duration)

    waiting_avg = int(sum(waiting_seconds) / len(waiting_seconds))
    waiting_max = max(waiting_seconds)

    result_data = {
        'missed_calls': missed_calls,
        'missed_calls_cnt': missed_calls_cnt,
        'waiting_avg': waiting_avg,
        'waiting_max': waiting_max,
    }

    return result_data


def generate_and_send_mail(date_range, report_data):
    email_from = EMAIL_FROM
    email_to = EMAIL_TO

    date_string = get_report_date_string(date_range)

    subject = f'[MLI] {date_string} Отчет по телефонным звонкам в ТП'
    msg_plain = render_to_string('calls_report.txt', {'report_data': report_data})
    msg_html = render_to_string('calls_report.html', {'report_data': report_data})
    send_mail(subject, msg_plain, email_from, email_to, html_message=msg_html)
