"""
URL configuration for cerbero project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
import config.home.views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from config.views import check_services


urlpatterns = [
    path('inicio/', config.home.views.dashboard , name='home'),
    path('login/', config.home.views.login_view , name='login'),
    path('detile_profile/', config.home.views.profile_view , name='detile_profile'),
    path('profile/edit', config.home.views.edit_profile , name='edit_profile'),
    path('cerbero/admin/', config.home.views.admin , name='admin_home'),
    path('cerbero/admin/userlist/', config.home.views.user_list , name='user_list'),
    path('cerbero/admin/userdelete/<int:pk>/', config.home.views.delete_user , name='delete'),
    path('cerbero/admin/useredit/<int:pk>/', config.home.views.edit_user , name='edituser'),
    path('register/', config.home.views.register_user , name='register'),
    path('cerbero/admin/usercreate/', config.home.views.create_user , name='createuser'),
    path('logout/', config.home.views.logout_view , name='logout'),
    path('confirmar/<str:uidb64>/<str:token>/', config.home.views.account_activation, name='account_activation'),
    path('confirmar/celery/', check_services, name='check_services'),
    path('cerbero/admin/grouplist/', config.home.views.group_list , name='group_list'),
    path('services/', include('config.urls')),
     # Otras rutas de tu aplicación
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)