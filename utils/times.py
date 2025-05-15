from datetime import datetime


def get_hour(time: datetime = None):
    if time is None:
        time = datetime.now()
    current_hour = (time.hour + (1 if time.minute >= 30 else 0)) % 24
    return current_hour


def getInfoFromTimestamp(ts: int):
    time = timestamp2datetime(ts)
    return time.year, time.month, time.day, time.weekday()+1, time.hour, time.minute


def timestamp2datetime(ts):
    return datetime.fromtimestamp(ts)
