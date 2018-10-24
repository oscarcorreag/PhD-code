from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response


class NotEnoughNodesException(APIException):
    status_code = 500
    default_detail = 'There are not enough nodes to work with. There might be because the random sample was created over a region with no road network. Try again.'
    default_code = 'internal_server_error'


class ActiveSessionExistsException(APIException):
    status_code = 500
    default_detail = 'There are active sessions already. The active session must be first ended by its creator.'
    default_code = 'internal_server_error'


class NewSessionTransactionException(APIException):
    status_code = 500
    default_detail = 'An error occurred when the new session with its details was being saved. This is a persistent error. Contact the administrator.'
    default_code = 'internal_server_error'
