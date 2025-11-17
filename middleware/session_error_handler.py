# middleware/session_error_handler.py

from django.shortcuts import redirect
from django.db.utils import OperationalError

class SessionErrorMiddleware:
    """
    Prevents crash when 'django_session' table is missing or session expired.
    Redirects user to login page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except OperationalError as e:
            if "django_session" in str(e):
                return redirect('/dashboard/login/?session_expired=1')
            raise e
