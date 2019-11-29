import logging

import requests

from calls.models import CallLeg
from calls.utils import get_api_date_format_from_iso, prepare_call_leg_data
from support_calls.constants import CALLS_API_USER, CALLS_API_PASSWORD, CALLS_API_URL


def get_data(start_date, end_date):
    time_from = '000000'
    time_to = '235959'
    date_from = get_api_date_format_from_iso(start_date)
    date_to = get_api_date_format_from_iso(end_date)

    url = CALLS_API_URL
    headers = {'cache-control': 'no-cache'}
    data = {
        "date_from": date_from,
        "date_to": date_to,
        "time_from": time_from,
        "time_to": time_to
    }

    response = requests.post(
        url,
        json=data,  # using json instead of data for auto-change headers to 'application/json'
        auth=(CALLS_API_USER, CALLS_API_PASSWORD),
        headers=headers,
        verify=False
    )

    content = response.json()
    result_data = content[CALLS_API_USER]
    return result_data


def import_call_legs(start_date, end_date):
    call_legs_from_api = get_data(start_date, end_date)

    outgoing_calls_mask = ['A', 'B', '7']
    call_legs_to_import = []
    for call_leg in call_legs_from_api:
        # исключаем исходящие звонки
        # TODO: как только пофиксят баг с cond_code='O' поправить call_leg.get('dialed_num')
        # TODO: пока так можно определить исходящий с cond_code='O'
        if call_leg.get('cond_code') in outgoing_calls_mask or not call_leg.get('dialed_num'):
            continue
        # временно чистим ucid в связи с багом
        call_leg = clean_ucid(call_leg)

        data_for_instance = prepare_call_leg_data(call_leg)
        call_leg_instance = CallLeg(**data_for_instance)
        call_legs_to_import.append(call_leg_instance)

    # TODO: доделать логгеры
    logging.info(f'Trying to create {len(call_legs_to_import)} Calls instances')
    CallLeg.objects.bulk_create(call_legs_to_import, ignore_conflicts=True)
    logging.info(f'{len(call_legs_to_import)} Calls instances successfully created')


def clean_ucid(call):
    ucid = call['ucid']
    call['ucid'] = ucid[-10:]
    return call
