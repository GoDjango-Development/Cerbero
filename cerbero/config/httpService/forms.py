from config.models import HTTPService 
from django import forms






class ServiceHTTPForm(forms.ModelForm):
    
    class Meta:
        model = HTTPService
        fields = ("name","port","url", "number_probe","probe_timeout")



        
    

    
    
        
