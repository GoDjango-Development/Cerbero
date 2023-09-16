from typing import re

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout

from django.urls import reverse
from django.http import HttpResponseRedirect

def dashboard(request):
    return render(request, 'config/dashboard.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redireccionar a la página de inicio después del inicio de sesión exitoso
            return redirect('home')
        else:
            # Mostrar un mensaje de error si las credenciales son inválidas
            messages.warning(request, "Usuario o contraseña incorrecta.")
            return render(request, 'registration/login.html')
    else:
        return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirige a la página de inicio de sesión


