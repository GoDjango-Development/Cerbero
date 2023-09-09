from config.models import * 
from django import forms




class ServiceDNSForm(forms.ModelForm):
    
    class Meta:
        model = DNSService
        fields = ("name","port","ip_address", "number_probe","probe_timeout")