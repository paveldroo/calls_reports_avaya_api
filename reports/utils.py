import datetime


def get_report_date_string(date_range):
    start_date = date_range[0]
    end_date = date_range[1] - datetime.timedelta(days=1)

    if start_date == end_date:
        date_string = start_date.strftime('%d.%m.%Y')
    else:
        date_string = f'{start_date.strftime("%d.%m.%Y")} – {end_date.strftime("%d.%m.%Y")}'

    return date_string
