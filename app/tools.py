from requests.models import PreparedRequest


def logger_extra(request: PreparedRequest) -> dict:
    """
    Logowanie dodatkowych parametrów żądania na potrzeby diagnostyczne.
    :param request: Żądanie
    :return: Słownik parametrów żądania
    """
    extra = {'endpoint': request.scope['path'], 'scope': str(request.scope),
             'ip': request.headers.get('X-Forwarded-For', request.client.host)}
    return extra
