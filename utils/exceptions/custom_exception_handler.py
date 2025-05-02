from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status as drf_status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_messages = []

        if isinstance(response.data, dict):
            for key, value in response.data.items():
                if isinstance(value, list):
                    error_messages.extend(value)
                else:
                    error_messages.append(str(value))

        return Response({
            'success': 0,
            'message': "An error has occurred." if not error_messages else error_messages[0],
            'errors': error_messages
        }, status=response.status_code)

    return Response({
        'success': 0,
        'message': 'Unknown error. Please try again later.',
        'errors': [str(exc)]
    }, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)
