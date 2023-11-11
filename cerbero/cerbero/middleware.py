from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib.sessions.middleware import SessionMiddleware

from django.utils import timezone

class SessionClearMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if 'session_cleared' in request.COOKIES and request.user.is_authenticated:
            logout(request)
            response.delete_cookie('session_cleared')

        return response
    
    


    
