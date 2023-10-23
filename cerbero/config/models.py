from django.db import models
from django.dispatch import receiver    
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save 
from django.conf import settings
from django.core.files import File
from cerbero.settings import MEDIA_URL, STATIC_URL
from django.contrib.auth import get_user_model
import os
import random

from PIL import Image


# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name = 'Nombre de la prueba')
    status = models.CharField(max_length=255, verbose_name = 'Ultimo Estado')
    number_probe = models.IntegerField(default=1, verbose_name = 'Numero de pruebas')
    probe_timeout = models.FloatField(default=1.0, verbose_name = 'Tiempo de espera por pruebas')
    in_process = models.BooleanField(default=False)
    processed_by = models.CharField(max_length=100, null = True)
    current_iteration = models.IntegerField(blank=True, null=True)
    is_monitoring = models.BooleanField(default = False)
    create_by =  models.ForeignKey(User,  on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,related_name='+')


    class Meta:
        db_table = 'Service'
        abstract = True
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

class HTTPService(Service):
    port = models.IntegerField(default=1)
    url= models.URLField()


    class Meta:
        db_table = 'httpSercice'
        managed = True
        verbose_name = 'HTTPService'
        verbose_name_plural = 'HTTPServices'
     
class ICMPService(Service):
    dns_ip = models.CharField( max_length=50)
    class Meta:
        db_table = 'icmpService'
        managed = True
        verbose_name = 'ICMPService'
        verbose_name_plural = 'ICMPServices'

class TFProtocolService(Service):
    address = models.CharField( max_length=100) 
    port = models.IntegerField( null= True, blank=True)
    hash = models.CharField(max_length=250)
    version = models.CharField( max_length=100)
    public_key =  models.TextField(max_length=6000)


    

    class Meta:
        db_table = 'TFProtocolService'
        managed = True
        verbose_name = 'TFProtocolService'
        verbose_name_plural = 'TFProtocolServices'

class DNSService(Service):
    ip_address =  models.GenericIPAddressField(null=True)
    port = models.IntegerField(null=True, blank=True)
    

    
    class Meta:
        db_table = 'DNSService'
        managed = True
        verbose_name = 'DNSService'
        verbose_name_plural = 'DNSServices'

class TCPService(Service):
    ip_address =  models.CharField(verbose_name='IP/DNS', max_length=50)
    port = models.IntegerField(null=True, blank=True)

   

    class Meta:
        db_table = 'TCPService'
        managed = True
        verbose_name = 'TCPService'
        verbose_name_plural = 'TCPServices'  

class ServiceStatusHttp(models.Model):
    service = models.ForeignKey(HTTPService, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_processing_time = models.FloatField(null=True, blank = True)
    is_up = models.CharField( max_length=50)
    response_status = models.CharField( max_length=50, null=True, blank = True)
    error_message = models.TextField(blank=True, null=True)
    


    class Meta:
        ordering = ['-timestamp']

class ServiceStatusTCP(models.Model):
    service = models.ForeignKey(TCPService, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_processing_time = models.FloatField(null=True, blank = True)
    is_up = models.CharField( max_length=50)
    error_message = models.TextField(blank=True, null=True)
   


    class Meta:
        ordering = ['-timestamp']

class ServiceStatusDNS(models.Model):
    service = models.ForeignKey(DNSService, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_processing_time = models.FloatField(null=True, blank = True)
    is_up = models.CharField( max_length=50)
    error_message = models.TextField(blank=True, null=True)
    


    class Meta:
        ordering = ['-timestamp']

class ServiceStatusICMP(models.Model):
    service = models.ForeignKey(ICMPService, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_processing_time = models.FloatField(null=True, blank = True)
    is_up = models.CharField( max_length=50)
    error_message = models.TextField(blank=True, null=True)
    


    class Meta:
        ordering = ['-timestamp']
        
class ServiceStatusTFProtocol(models.Model):
    service = models.ForeignKey(TFProtocolService, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_processing_time = models.FloatField(null=True, blank = True)
    is_up = models.CharField( max_length=50)
    error_message = models.TextField(blank=True, null=True)
    

    class Meta:
        ordering = ['-timestamp']
        
class ServiceModificationHTTP(models.Model):
    service = models.ForeignKey(HTTPService, on_delete=models.CASCADE)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ServiceModificationHTTP'
        verbose_name = 'Service Modification HTTP'
        verbose_name_plural = 'Service Modifications HTTP'      

class ServiceModificationTCP(models.Model):
    service = models.ForeignKey(TCPService, on_delete=models.CASCADE)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ServiceModificationTCP'
        verbose_name = 'Service Modification TCP'
        verbose_name_plural = 'Service Modifications TCP' 

class ServiceModificationTFP(models.Model):
    service = models.ForeignKey(TFProtocolService, on_delete=models.CASCADE)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ServiceModificationTFP'
        verbose_name = 'Service Modification TFProtocol'
        verbose_name_plural = 'Service Modifications TFProtocol' 

class ServiceModificationICMP(models.Model):
    service = models.ForeignKey(ICMPService, on_delete=models.CASCADE)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ServiceModificationICMP'
        verbose_name = 'Service Modification ICMP'
        verbose_name_plural = 'Service Modifications ICMP' 

class ServiceModificationDNS(models.Model):
    service = models.ForeignKey(DNSService, on_delete=models.CASCADE)
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE)
    modified_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'ServiceModificationDNS'
        verbose_name = 'Service Modification DNS'
        verbose_name_plural = 'Service Modifications DNS' 
    
def user_directory_path_profile(instance, filename):
    profile_picture_name = 'users/{0}/profile.jpg'.format(instance.user.username)
    full_path = os.path.join(settings.MEDIA_ROOT, profile_picture_name)

    if os.path.exists(full_path):
        os.remove(full_path)

    return profile_picture_name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    picture = models.ImageField( upload_to=user_directory_path_profile)
    #auth_token = models.CharField(max_length=100)
    #is_verified = models.BooleanField(default=False)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        profile = Profile.objects.create(user=instance)
        select_random_image(profile)
        
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

def select_random_image(profile):
    # Ruta de la carpeta de imágenes
    image_folder = 'static/img/avatar'

    # Obtener la lista de imágenes en la carpeta
    image_files = os.listdir(image_folder)

    # Seleccionar una imagen al azar de la lista
    selected_image = random.choice(image_files)

    # Ruta completa de la imagen seleccionada
    selected_image_path = os.path.join(image_folder, selected_image)

    # Asignar la imagen seleccionada al perfil
    with open(selected_image_path, 'rb') as f:
        profile.picture.save(selected_image, File(f))

def add_user_to_owner_group(sender, instance, created,  **kwargs):
    if created:
        try:
            owner = Group.objects.get(name='owner')
        except Group.DoesNotExist:
            owner = Group.objects.create(name='owner')
            Group.objects.create(name='staff')

        if not instance.user.is_superuser:
            instance.user.groups.add(owner)
            




post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
post_save.connect(add_user_to_owner_group, sender=Profile)




   