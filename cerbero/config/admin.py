from django.contrib import admin

# Register your models here.
from .models import *



admin.site.register(DNSService)
admin.site.register(TCPService)
admin.site.register(HTTPService)
admin.site.register(TFProtocolService)
admin.site.register(ICMPService)
admin.site.register(Profile)

admin.site.register(ServiceStatusICMP)
admin.site.register(ServiceStatusTFProtocol)
admin.site.register(ServiceStatusTCP)
admin.site.register(ServiceStatusHttp)
admin.site.register(ServiceStatusDNS)

admin.site.register(ServiceModificationHTTP)







