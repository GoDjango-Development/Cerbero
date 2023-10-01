from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save 
from django.conf import settings
from cerbero.settings import MEDIA_URL, STATIC_URL
from django.contrib.auth import get_user_model
import os
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
    dns = models.CharField( max_length=50)
    ip_address =  models.GenericIPAddressField(null= True, blank=True)
    port = models.IntegerField( null= True, blank=True)
    hash = models.CharField(max_length=250)
    version = models.CharField( max_length=100)
    public_key =  models.CharField(max_length=100)


    

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


class UserContactInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='users/%Y/%m/%d', null=True, blank=True)
    phone_number = models.CharField(max_length=20)

    
    def __str__(self):
        return self.user.username

    def get_image(self):
        if self.image:
            return '{}{}'.format(MEDIA_URL, self.image)
        return '{}{}'.format(STATIC_URL, 'img/default-150x150.png')


  
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserContactInfo.objects.create(user=instance)


# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

# created profile
post_save.connect(create_user_profile, sender=User)
# save created profile
# post_save.connect(save_user_profile, sender=User)
  
