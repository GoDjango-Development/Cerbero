from django.contrib import admin

# Register your models here.
from .models import *



admin.site.register(DNSService)
admin.site.register(TCPService)
admin.site.register(HTTPService)
admin.site.register(ICMPService)
admin.site.register(UserContactInfo)

admin.site.register(ServiceStatusTCP)
admin.site.register(ServiceStatusHttp)
admin.site.register(ServiceStatusDNS)








