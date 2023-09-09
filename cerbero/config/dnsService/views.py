from django.contrib import messages
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from config.models import DNSService as dns_s
from .forms import ServiceDNSForm
from config.tasks import monitoreo_dns_services



def create_service_dns(request):
    if request.method == 'POST':
        form = ServiceDNSForm(request.POST)
        if form.is_valid():
            service = form.save()

        # monitoreo_http_services.delay()
        mensaje = "Servicio guardado correctamente."
        messages.success(request, mensaje)

        return HttpResponseRedirect(reverse('list_dns'))
    else:
        form = ServiceDNSForm()
    return render(request, 'config/createdns.html', {'form': form})



@csrf_exempt
def check_service_dns(request, pk):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'iniciar':
            monitoreo_dns_services.delay(pk, resume=True)
            message = 'Monitoreo iniciado correctamente.'
        elif action == 'detener':
            monitoreo_dns_services.delay(pk, resume=False)
            message = 'Monitoreo detenido correctamente.'
        else:
            message = 'Acción no válida.'

        return JsonResponse({'message': message})

    return JsonResponse({'message': 'Método no permitido.'})


def update_data_dns(request):
    datos = dns_s.objects.all()

    update = []
    for datos in datos:
        status = datos.status
        processed_by = datos.processed_by

        # Crea el contenido HTML personalizado para la columna "Status" en función del valor
        if status == 'up':
            status_html = '<i class="fas fa-circle" style="color: green;"></i>'
        elif status == 'down':
            status_html = '<i class="fas fa-circle" style="color: red;"></i>'
        elif status == 'error':
            status_html = '<i class="fas fa-circle" style="color: yellow;"></i>'
        else:
            status_html = ''

        # Crea el contenido HTML personalizado para la columna "Processed By" en función del valor
        if processed_by == 'Terminado':
            processed_by_html = '<h6><span class="badge badge-pill badge-success">Terminado</span></h6>'
        elif processed_by == 'Detenido':
            processed_by_html = '<h6><span class="badge badge-pill badge-warning">Detenido</span></h6>'
        elif processed_by == 'Monitoreando':
            processed_by_html = '<h6><span class="badge badge-pill badge-primary">Monitoreando</span></h6>'
        else:
            processed_by_html = '<h6><span class="badge badge-pill badge-secondary">Esperando</span></h6>'

        

        date = {
            'status': status_html,
            'processed_by': processed_by_html,
        }
        update.append(date)
    return JsonResponse(update, safe=False)



def list_service_dns(request):

    contexto = {'dns_s': dns_s.objects.all()}
    return render(request, 'config/listdns.html', contexto)