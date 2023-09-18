from django.db import models
from django.urls import reverse


# Create your models here.
class Service(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name = 'Nombre de la prueba')
    status = models.CharField(max_length=255, verbose_name = 'Ultimo Estado')
    number_probe = models.IntegerField(default=1, verbose_name = 'Numero de pruebas')
    probe_timeout = models.FloatField(default=1.0, verbose_name = 'Tiempo de espera por pruebas')
    in_process = models.BooleanField(default=False)
    processed_by = models.CharField(max_length=100, null = True)
    current_iteration = models.IntegerField(blank=True, null=True)
    stop_flags = models.IntegerField(blank=True, null=True)
    is_monitoring = models.BooleanField(default = False)

    

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


