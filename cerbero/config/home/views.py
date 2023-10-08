from typing import re

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth import authenticate, login
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from config.models import Profile
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import TemplateView, View
from .forms import EditProfileForm
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
User = get_user_model()


@login_required(login_url='login', redirect_field_name='login')
def dashboard(request):
    return render(request, 'config/dashboard.html')

@login_required(login_url='login', redirect_field_name='login')
def admin(request):
    return render(request, 'config/admin_home.html')


def user_list(request):
    users = User.objects.select_related('profile').all()
    return render(request,'config/userlist.html', {'users':users})



@never_cache
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
             # Redirigir a la plantilla del administrador para superusuarios
            if request.user.is_superuser:
                print('pase por aca')
                return redirect('admin_home') 
            else:
                # Redirigir a la plantilla del usuarios
                print('entre aqui')
                return redirect('home')
        else:
            # Mostrar un mensaje de error si las credenciales son inválidas
            messages.warning(request, "Usuario o contraseña incorrecta.")
            return render(request, 'registration/login.html')
    else:
        if request.user.is_authenticated:
            # Redireccionar al usuario si ya ha iniciado sesión
            if request.user.is_superuser:
                print('pase por aca')
                return redirect('admin_home') 
            # Redirigir a la plantilla del administrador para superusuarios
            else:
                print('entre aqui')
                return redirect('home')
        else:
            response = render(request, 'registration/login.html')
            # Configurar una cookie para evitar el caché de las páginas después de cerrar sesión
            response.set_cookie('session_cleared', 'true')
            return response

def logout_view(request):
    try:
        logout(request)
        message = "Has cerrado sesión exitosamente."

        messages.success(request, message, extra_tags='Éxito')
    except Exception as e:
        # Aquí puedes realizar acciones específicas en caso de que se produzca una excepción al llamar a logout
        message = "Ha ocurrido un error al cerrar sesión."
        messages.success(request, message, extra_tags='Error')

    # Redirigir a la página de inicio de sesión con el mensaje en la URL
    return redirect('login')

def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            User = get_user_model()
            owner_group = Group.objects.get(name='owner')
            
            username = form.cleaned_data['username']
            
            # Verificar si ya existe un usuario con el mismo nombre de usuario
            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'message': 'Ya existe un usuario con este nombre de usuario.'})
            
            # Guarda el usuario creado por el formulario
            user = form.save()

            # Agrega al usuario al grupo "owner"
            user.groups.add(owner_group)
            user.save()

            return JsonResponse({'success': True, 'message': '¡Registro exitoso!'})
        else:
            errors = dict(form.errors.items())
            return JsonResponse({'success': False, 'message': 'Por favor, corrige los errores en el formulario.', 'errors': errors})
    else:
        return JsonResponse({'success': False, 'message': 'Método no permitido.'})
 
 
@login_required(login_url='login', redirect_field_name='login')    
def profile_view(request):
    user = request.user
    usercontactinfo = Profile.objects.get(user=user)
    
    
    context = {
        'user': user,
        'usercontactinfo': usercontactinfo
    }
    if request.user.is_superuser:
        return render(request, 'config/detail_profile_admin.html', context)

    else:
        return render(request, 'config/detail_profile.html', context) 

@login_required(login_url='login', redirect_field_name='login')
def edit_profile(request):
    user = request.user.id
    profile = Profile.objects.get(user__id=user)
    user_basic_info = User.objects.get(id=user)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile, initial={'first_name': user_basic_info.first_name, 'last_name': user_basic_info.last_name})
        if form.is_valid():
            user_basic_info.first_name = form.cleaned_data.get('first_name')
            user_basic_info.last_name = form.cleaned_data.get('last_name')

            # Actualizar la imagen solo si se proporciona una nueva
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            user_basic_info.save()
            return redirect('detile_profile')
    else:
        form = EditProfileForm(instance=profile, initial={'first_name': user_basic_info.first_name, 'last_name': user_basic_info.last_name})

    context = {
        'form': form,
    }

    if request.user.is_superuser:
        return render(request, 'config/edit_profile_admin.html', context)
    else:
        return render(request, 'config/edit_profile.html', context)