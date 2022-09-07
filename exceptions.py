class IncorrectHttpStatus(Exception):
    pass

def correction_status(value):
    if value != 200:
        raise IncorrectHttpStatus('Не коррекитный HTTP статус')

class ErrorTelegram(Exception):
    pass

class NotResponse(Exception):
    pass

class JSONError(Exception):
    pass

class HomeworksNotList(Exception):
    pass

class InvalidStatus(Exception):
    pass
