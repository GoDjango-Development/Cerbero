from django.contrib import messages
from functools import wraps
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django.urls import reverse
from config.models import DNSService as dns_s,  ServiceStatusDNS as ServiceStatus
from .forms import ServiceDNSForm
from config.tasks import monitoreo_dns_services
import json




def create_service_dns(request):
    if request.method == 'POST':
        form = ServiceDNSForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.processed_by = 'Esperando'
            service.save()

            mensaje = "Servicio guardado correctamente."
            messages.success(request, mensaje,extra_tags="create")

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



def verificar_edicion_permitida(view_func):
    @wraps(view_func)
    def wrapper(request, pk, *args, **kwargs):
        service = get_object_or_404(dns_s, pk=pk)

        if service.processed_by != 'Esperando' and service.processed_by != 'Detenido':
            messages.error(
                request, "No se puede editar el elemento porque la prueba está en curso o terminada.")
            return redirect('list_https')
        return view_func(request, pk, *args, **kwargs)

    return wrapper


@verificar_edicion_permitida
def edit_dns(request, pk):
    service = get_object_or_404(dns_s, pk=pk)

    
    if request.method == 'POST':
        form = ServiceDNSForm(request.POST, instance=service)
        form.fields['number_probe'].required = False

        if form.is_valid():
            form.save()
            message = "Servicio editado correctamente. "
            messages.success(request, message, extra_tags="edit")
            return HttpResponseRedirect(reverse('list_dns'))
    else:
        form = ServiceDNSForm(instance=service)
        if service.processed_by == 'Detenido':
            # Si el servicio está detenido, se excluye el campo 'number_probe' del formulario
            form.fields['number_probe'].required = False
            form.fields['number_probe'].widget.attrs['readonly'] = True
    return render(request, 'config/editdns.html', {'form': form})


def service_detail_dns(request, pk):
    service = dns_s.objects.get(pk=pk)
    statuses = ServiceStatus.objects.filter(service=service)

    # data = []
    # for status in statuses:
    #     formatted_date = status.timestamp.strftime('%d-%m-%y')
    #     data.append({'date': formatted_date, 'is_up': status.is_up, 'cpu_processing_time': status.cpu_processing_time})

    context = {
        'service': service,
        'statuses': statuses,
    }
    return render(request, 'config/detaildns.html', context)

def statusdnsgraficpoint(request,pk):
    service = dns_s.objects.get(pk=pk)
    statuses = ServiceStatus.objects.filter(service=service)

    data = []
    for status in statuses:
        formatted_date = status.timestamp.strftime('%d-%m-%y')
        data.append({'date': formatted_date, 'is_up': status.is_up, 'cpu_processing_time': round(status.cpu_processing_time, 4)})
    return JsonResponse(data, safe=False)

def statusdnsrecord(request,pk):
    service = dns_s.objects.get(pk=pk)
    statuses = ServiceStatus.objects.filter(service=service)

    dataa =  []
    for status in statuses:
        pk = status
        is_up = status.is_up
        # Crea el contenido HTML personalizado para la columna "Status" en función del valor
        if is_up == 'up':
            status_html = '<i class="fas fa-circle" style="color: green;"></i>'
        elif is_up == 'down':
            status_html = '<i class="fas fa-circle" style="color: red;"></i>'
        elif is_up == 'error':
            status_html = '<i class="fas fa-circle" style="color: yellow;"></i>'
        else:
            status_html = ''
        timestamp = status.timestamp.strftime('%d-%m-%y')
        cpu_processing_time = round(status.cpu_processing_time,4)
        error_message = status.error_message
        
        
        statusdate = {
            'is_up': status_html,
            'timestamp': timestamp,
            'cpu_processing_time': cpu_processing_time,
            'error_message': error_message
        }
        dataa.append(statusdate)
    return JsonResponse(dataa, safe=False)
    
@csrf_exempt
@require_POST
def delete_dns(request, pk):
    service = get_object_or_404(dns_s, pk=pk)

    processed_by_value = service.processed_by
    if processed_by_value not in ['Esperando', 'Detenido', 'Terminado']:
        return JsonResponse({'mensaje': 'No se puede eliminar el elemento porque la prueba está en curso.'}, status=400)

    service.delete()

    return JsonResponse({'mensaje': 'El registro ha sido eliminado exitosamente.'})

    
    


 