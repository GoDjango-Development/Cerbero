import re
import tldextract
import ipaddress
from django.utils.safestring import mark_safe

from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, RegexValidator, URLValidator
from django.core.exceptions import ValidationError
from django import forms
from config.models import TFProtocolService

    






class ServiceTFPForm(forms.ModelForm):
    port = forms.CharField(
        label="Puerto",
        validators=[RegexValidator(r'^\d+$', 'Ingrese un número válido para el puerto.')]
    )

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
    
    address = forms.CharField(
        label="IP/DNS",
        error_messages={
            'required': 'Este campo es obligatorio.'
        }
    )
    
    
    version = forms.CharField(
        label="Versión",
        validators=[MinLengthValidator(1)],
        error_messages={
            'required': 'Este campo es obligatorio.'
        }
    )
    
    public_key = forms.CharField(
        label="Clave pública",
        widget=forms.Textarea(attrs={'rows': 5}),
        error_messages={
            'required': 'Este campo es obligatorio.'
        }
    )

    
    
    class Meta:
        model = TFProtocolService
        fields = ("name","port","address","version","hash","public_key","number_probe","probe_timeout")
        widgets = {
            'public_key': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_public_key(self):
        public_key = self.cleaned_data['public_key']
        return mark_safe(public_key)
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        existing_services = TFProtocolService.objects.exclude(pk=self.instance.pk)
        if existing_services.filter(name=name).exists():
            raise ValidationError("El nombre ya está en uso.")
        return name

    def clean_port(self):
        port = self.cleaned_data.get('port')
        if not port.isdigit():
            raise ValidationError("Ingrese un número válido para el puerto.")
        port = int(port)
        if port < 1 or port > 65535:
            raise ValidationError("Ingrese un número de puerto válido (1-65535).")
        return port

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
    
    
    def clean_dns(self):
        dns = self.cleaned_data['ip_address']
        if not is_valid_dns(dns):
            raise forms.ValidationError('La entrada no es un nombre de dominio o una dirección IP válida.')
        return dns


def is_valid_dns(value):
    # Verificar si es una dirección IP válida
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        pass

    # Utilizar tldextract para extraer las partes del nombre de dominio
    extracted = tldextract.extract(value)

    # Verificar si el nombre de dominio tiene una subparte válida
    if not extracted.subdomain and not extracted.domain and not extracted.suffix:
        return False

    # Verificar si el dominio tiene una extensión de sufijo válida
    if not extracted.suffix or not extracted.suffix.isalpha():
        return False

    # Verificar si el dominio y las subpartes solo contienen caracteres alfanuméricos y guiones
    for part in [extracted.subdomain, extracted.domain]:
        if part and not part.replace('-', '').isalnum():
            return False

    # Verificar la longitud del dominio y las subpartes
    if len(extracted.subdomain) > 63 or len(extracted.domain) > 63 or len(extracted.suffix) > 10:
        return False

    return True