from datetime import datetime


def get_hour(time: datetime = None):
    if time is None:
        time = datetime.now()
    current_hour = (time.hour + (1 if time.minute >= 30 else 0)) % 24
    return current_hour
