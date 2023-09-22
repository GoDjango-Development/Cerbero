from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
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
    
    

class InactividadMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.tiempo_inactividad = 1  # 5 minutos en segundos

    def __call__(self, request):
        print('se llamo este metodo')
        # Verificar si el usuario está autenticado y si hay un temporizador existente en la sesión
        if request.user.is_authenticated and 'ultima_actividad' in request.session:
            tiempo_transcurrido = timezone.now() - request.session['ultima_actividad']
            if tiempo_transcurrido.total_seconds() >= self.tiempo_inactividad:
                logout(request)  # Cerrar sesión del usuario
                print("La sesión se ha cerrado debido a inactividad.")
                return self.redirect_to_login()

        # Actualizar la marca de tiempo de la última actividad en la sesión
        request.session['ultima_actividad'] = timezone.now()

        response = self.get_response(request)
        return response


    def redirect_to_login(self):
        redirect_url = reverse('login')
        return redirect(redirect_url)