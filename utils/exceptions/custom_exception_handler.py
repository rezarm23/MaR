from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status as drf_status


def custom_exception_handler(exc, context):
    print("🚨 custom_exception_handler CALLED")
    # گرفتن پاسخ اصلی
    response = exception_handler(exc, context)

    if response is not None:
        # اینجا ما به جای اینکه خطاها رو از دیکشنری فیلدها جدا کنیم، همه رو توی یک لیست جمع می‌کنیم
        error_messages = []

        # بررسی اگر داده‌ها دیکشنری باشن
        if isinstance(response.data, dict):
            for key, value in response.data.items():
                if isinstance(value, list):
                    error_messages.extend(value)  # اگر خطاها در قالب لیست هستن، اون‌ها رو اضافه می‌کنیم
                else:
                    error_messages.append(str(value))  # یا هر خطا رو جداگانه اضافه می‌کنیم

        # ارسال پاسخ با ساختار جدید
        return Response({
            'success': 0,
            'message': "خطایی رخ داده است." if not error_messages else error_messages[0],  # اولین پیام خطا
            'errors': error_messages  # لیست خطاها رو در یک لیست بر می‌گردونیم
        }, status=response.status_code)

    # اگر پاسخ اصلی نداشته باشیم، یک خطای عمومی برمی‌گردونیم
    return Response({
        'success': 0,
        'message': 'خطای ناشناخته. لطفاً بعداً تلاش کنید.',
        'errors': [str(exc)]  # جزئیات استثنا را بر می‌گردانیم
    }, status=drf_status.HTTP_500_INTERNAL_SERVER_ERROR)
