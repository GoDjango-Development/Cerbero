import re
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
from config.models import DNSService

class ServiceDNSForm(forms.ModelForm):
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
    ip_address = forms.GenericIPAddressField(
        label="Dirección IP",
        error_messages={
            'required': 'Este campo es obligatorio.'
        }
    )

    class Meta:
        model = DNSService
        fields = ("name", "port", "ip_address", "number_probe", "probe_timeout")

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if DNSService.objects.filter(name=name).exists():
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