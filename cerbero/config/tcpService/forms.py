from config.models import TCPService 
from django import forms




class ServiceTCPForm(forms.ModelForm):
    
    class Meta:
        model = TCPService
        fields = ("name","port","ip_address","number_probe","probe_timeout")



        