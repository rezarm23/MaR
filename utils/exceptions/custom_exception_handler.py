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
                    for item in value:
                        if key == 'email':
                            error_messages.append(f"فرمت ایمیل معتبر نیست.")
                        elif key == 'phone_number':
                            error_messages.append(f"شماره باید 11 رقمی و با 09 شروع شود.")
                        elif key == 'password':
                            error_messages.append(f"رمز عبور باید حداقل ۸ کاراکتر باشد.")
                        else:
                            error_messages.append(str(item))
                else:
                    error_messages.append(str(value))

        return Response({
            'success': 0,
            'message': "خطایی رخ داده است." if not error_messages else error_messages[0],
            'errors': error_messages
        }, status=response.status_code)


    return Response({
        'success': 0,
        'message': 'خطای ناشناخته. لطفاً بعداً تلاش کنید.',
        'errors': [str(exc)]
    }, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)
