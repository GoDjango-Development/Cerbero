import os
from typing import re
from cerbero.settings import EMAIL_HOST_USER
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, EmailMultiAlternatives
from email.mime.image import MIMEImage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import UserChangeForm
from config.models import Profile
from .forms import CustomUserCreationForm, UpdateUser,EditProfileForm
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
User = get_user_model()

def is_not_superuser(user):
    return not user.is_superuser

def is_superuser(user):
    return user.is_superuser

@login_required(login_url='login', redirect_field_name='login')
@user_passes_test(is_not_superuser, login_url='admin_home')
def dashboard(request):
    return render(request, 'config/dashboard.html')

@login_required(login_url='login', redirect_field_name='login')
@user_passes_test(is_superuser, login_url='home')
def admin(request):
    return render(request, 'config/admin_home.html')

@login_required(login_url='login', redirect_field_name='login')
@user_passes_test(is_superuser, login_url='home')
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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
 
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'ya existe un usuario con este correo electrónico')
            if form.errors:
                form_errors = form.errors.get_json_data()
                context= {
                        'form': form,'form_errors':form_errors
                    }
                return render(request, 'registration/register.html', context)
            # Guardar el usuario creado por el formulario con los datos adicionales
            user = form.save(commit=False)
            user.email = email
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = False  # Desactiva la cuenta hasta que no confirme
            user.save()

            token = default_token_generator.make_token(user)
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            scheme = request.scheme
            token_url = f"{scheme}://{current_site.domain}/confirmar/{uid}/{token}"

            # Renderizar el contenido del correo electrónico en formato HTML
            html_content = render_to_string('email/confirmation.html', {
                'user': user,
                'token_url': token_url
            })

            # Obtener la ruta de la imagen
            image_path = os.path.join(settings.BASE_DIR, 'static/img/logo.png')
            # Leer el contenido de la imagen
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Obtener el nombre de archivo de la imagen
            image_filename = 'logo.png'

            # Crear una instancia de EmailMultiAlternatives
            msg = EmailMultiAlternatives(
                subject='Confirmación de correo electrónico',
                body=strip_tags(html_content),  # Versión de texto plano del contenido HTML
                from_email=settings.EMAIL_HOST_USER,
                to=[email],
            )
            msg.attach_alternative(html_content, "text/html")
            image = MIMEImage(image_data)
            image.add_header('Content-ID', '<imagen>')
            image.add_header('Content-Disposition', 'inline', filename=image_filename)
            msg.attach(image)

            msg.send()
            
            messages.success(request, 'Por favor, acceda al correo proporcionado y verifique su identidad.')

            return HttpResponseRedirect(reverse('login'))
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@csrf_exempt
@require_POST
@login_required(login_url='login', redirect_field_name='login')
@user_passes_test(is_superuser, login_url='home')
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()

    return JsonResponse({'mensaje': 'El registro ha sido eliminado exitosamente.'})

def account_activation(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Activar la cuenta del usuario
        user.is_active = True
        user.save()

        # Redirigir a una página de éxito o mostrar un mensaje de éxito
        return render(request, 'registration/account_activation_success.html')  

@login_required(login_url='login', redirect_field_name='login')
@user_passes_test(is_superuser, login_url='home')
def create_user(request):
    user = User.objects.all()

    
    if request.method == 'POST':
        form = UpdateUser(request.POST)
        if form.is_valid():
            form.save()

           

            return redirect('user_list')
    else:
        form = UpdateUser()

    groups = Group.objects.all()

    context = {
        'form': form,
        'user': user,
        'groups': groups,
    }
    return render(request, 'config/edit_user.html', context)

    pass

@login_required(login_url='login', redirect_field_name='login')
def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)

    
    if request.method == 'POST':
        form = UpdateUser(request.POST, instance=user)
        if form.is_valid():
            form.save()

            # Actualizar grupos
            selected_groups = request.POST.getlist('groups')
            user.groups.set(selected_groups)

            return redirect('user_list')
    else:
        form = UpdateUser(instance=user)

    groups = Group.objects.all()

    context = {
        'form': form,
        'user': user,
        'groups': groups,
    }
    return render(request, 'config/edit_user.html', context)


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
    
@login_required(login_url='login', redirect_field_name='login')  
@user_passes_test(is_superuser, login_url='home')
def group_list(request):
    groups = Group.objects.all()
    return render(request,'config/listgroup.html', {'groups':groups})




#404: página no encontrada
def error_404(request, exception):
    if request.user.is_authenticated:
         
        return render(request, 'base/404.html')
    return redirect('login')



