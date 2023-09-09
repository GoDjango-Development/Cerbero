from config.models import ICMPService 
from django import forms




class ServiceICMPForm(forms.ModelForm):
    
    class Meta:
        model = ICMPService
        fields = ("name","dns_ip","number_probe","probe_timeout")