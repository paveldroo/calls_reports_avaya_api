import datetime
import logging
import re

from calls.models import CallLeg, Call
from support_calls.utils import date_range_from_dates


def prepare_call_leg_data(call_leg):
    datetime_string = call_leg.get('start_date') + call_leg.get('start_time')
    timestamp = datetime.datetime.strptime(datetime_string, '%d%m%y%H%M%S')

    result = {
        'cdr_id': call_leg.get('cdr_id'),
        'ucid': call_leg.get('ucid'),
        'timestamp': timestamp,
        'duration': call_leg.get('sec_dur'),
        'caller_number': call_leg.get('in_tac'),
        'dialed_number': call_leg.get('dialed_num'),
        'vdn': call_leg.get('vdn')
    }

    return result


def prepare_call_data(call_legs_list):
    result = {}
    answered = True
    for call_leg in call_legs_list:
        call_duration = call_leg.duration
        # Проверяем пропущен ли звонок, если dialed_number == 7410 == vdn и это единственное плечо
        if call_leg.dialed_number == CallLeg.WELCOME_CALL_NUMBER:
            if len(call_legs_list) == 1 and call_leg.dialed_number == call_leg.vdn:
                answered = False
                # Вычитаем 6 секунд IVR из пропущенного звонка
                # Не учитываем звонки < 6 секунд, это время IVR
                call_duration = call_leg.duration - 6
                if call_duration <= 0:
                    continue

        result = {
            'ucid': call_leg.ucid,
            'timestamp': call_leg.timestamp,
            'duration': call_duration,
            'caller_number': call_leg.caller_number,
            'answered': answered
        }

    return result


def get_api_date_format_from_iso(date):
    year_month_day = re.search(r'\d{2}(\d{2})-(\d{2})-(\d{2})', date)
    # get only 2 last digits of the year
    year = year_month_day.group(1)
    month = year_month_day.group(2)
    day = year_month_day.group(3)
    result_date = f'{day}{month}{year}'
    return result_date


def create_calls_from_call_legs(start_date=None, end_date=None):
    date_range = date_range_from_dates(start_date, end_date)
    call_legs = CallLeg.objects.filter(timestamp__date__range=date_range)

    call_legs_to_match = {}
    for call_leg in call_legs:
        ucid = call_leg.ucid
        if ucid in call_legs_to_match.keys():
            call_legs_to_match[ucid].append(call_leg)
        else:
            call_legs_to_match[ucid] = [call_leg]

    calls_to_create = []
    for ucid, call_legs_list in call_legs_to_match.items():
        data_for_instance = prepare_call_data(call_legs_list)
        if data_for_instance:
            call_instance = Call(**data_for_instance)
            calls_to_create.append(call_instance)

    # TODO: доделать логгеры
    logging.info(f'Trying to create {len(calls_to_create)} Calls instances')
    Call.objects.bulk_create(calls_to_create, ignore_conflicts=True)
    logging.info(f'{len(calls_to_create)} Calls instances successfully created')
