class IncorrectHttpStatus(Exception):
    pass

def correction_status(value):
    if value != 200:
        raise IncorrectHttpStatus('Не коррекитный HTTP статус')
