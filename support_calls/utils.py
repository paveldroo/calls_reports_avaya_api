import datetime


def date_range_from_dates(start_date, end_date):
    if not start_date or not end_date:
        date_range = (datetime.date.today() - datetime.timedelta(days=1), datetime.date.today())
    else:
        date_range = (datetime.datetime.strptime(start_date, '%Y-%m-%d'),
                      datetime.datetime.strptime(end_date, '%Y-%m-%d'))

    return date_range
