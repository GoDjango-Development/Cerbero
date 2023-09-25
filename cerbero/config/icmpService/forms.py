from config.models import ICMPService 
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
import re
from django import forms




class ServiceICMPForm(forms.ModelForm):
    number_probe = forms.CharField(
        label="Número de prueba",
        required=False,
        validators=[RegexValidator(r'^\d+$', 'Ingrese un número válido para el número de prueba.')]
    )
    probe_timeout = forms.CharField(
        label="Tiempo de prueba",
        validators=[RegexValidator(r'^\d+(\.\d+)?$', 'Ingrese un número válido para el tiempo de prueba.')]
    )
    name = forms.CharField(
        label="Nombre",
        validators=[MinLengthValidator(1)],
        error_messages={
            'required': 'Este campo es obligatorio.'
        }
    )
    dns_ip = forms.GenericIPAddressField(
        label="Dirección IP",
        error_messages={
            'required': 'Este campo es obligatorio.'
        }
    )
    
    class Meta:
        model = ICMPService
        fields = ("name","dns_ip","number_probe","probe_timeout")
        
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        existing_services = ICMPService.objects.exclude(pk=self.instance.pk)
        if existing_services.filter(name=name).exists():
            raise ValidationError("El nombre ya está en uso.")
        return name

  
    def clean_number_probe(self):
        number_probe = self.cleaned_data.get('number_probe')
        if number_probe is not None and not number_probe.isdigit():
            raise ValidationError("Ingrese un número válido para el número de prueba.")
        return number_probe

    def clean_probe_timeout(self):
        probe_timeout = self.cleaned_data.get('probe_timeout')
        if probe_timeout is not None and not re.match(r'^\d+(\.\d+)?$', probe_timeout):
            raise ValidationError("Ingrese un número válido para el tiempo de prueba.")
        return probe_timeout