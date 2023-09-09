from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from config.models import ICMPService as icmp_s, ServiceStatusICMP as ServiceStatus
from .forms import ServiceICMPForm
from config.tasks import monitoreo_icmp_services

import json






def create_service_icmp(request):
    if request.method == 'POST':
        form = ServiceICMPForm(request.POST)
        if form.is_valid():
            service = form.save()

        # monitoreo_http_services.delay()
        mensaje = "Servicio guardado correctamente."
        messages.success(request, mensaje)

        return HttpResponseRedirect(reverse('list_icmp'))
    else:
        form = ServiceICMPForm()
    return render(request, 'config/createicmp.html', {'form': form})



def view_icmp(request):
    contexto = {'icmp_s': icmp_s.objects.all()}
    return render(request, 'config/listicmp.html', contexto)




def update_data_icmp(request):
    datos = icmp_s.objects.all()

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



@csrf_exempt
def check_service_icmp(request, pk):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'iniciar':
            monitoreo_icmp_services.delay(pk, resume=True)
            message = 'Monitoreo iniciado correctamente.'
        elif action == 'detener':
            monitoreo_icmp_services.delay(pk, resume=False)
            message = 'Monitoreo detenido correctamente.'
        else:
            message = 'Acción no válida.'

        return JsonResponse({'message': message})

    return JsonResponse({'message': 'Método no permitido.'})

