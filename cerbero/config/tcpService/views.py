
from django.contrib import messages
from functools import wraps
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from config.models import TCPService as tcp_s, ServiceStatusTCP as ServiceStatus
from .forms import ServiceTCPForm
from config.tasks import monitoreo_tcp_services
import json


def service_detail_tcp(request, pk):
    service = tcp_s.objects.get(pk=pk)
    statuses = ServiceStatus.objects.filter(service=service)
    context = {
        'service': service,
        'statuses': statuses,
    }
    return render(request, 'config/detailtcp.html', context)


def create_service_tcp(request):
    if request.method == 'POST':
        form = ServiceTCPForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.processed_by = 'Esperando'
            service.save()

            mensaje = "Servicio guardado correctamente."
            messages.success(request, mensaje, extra_tags="create")

            return HttpResponseRedirect(reverse('list_tcp'))
    else:
        form = ServiceTCPForm()
    return render(request, 'config/createtcp.html', {'form': form})


@csrf_exempt
def check_service_tcp(request, pk):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'iniciar':
            monitoreo_tcp_services.delay(pk, resume=True)
            message = 'Monitoreo iniciado correctamente.'
        elif action == 'detener':
            monitoreo_tcp_services.delay(pk, resume=False)
            message = 'Monitoreo detenido correctamente.'
        else:
            message = 'Acción no válida.'

        return JsonResponse({'message': message})

    return JsonResponse({'message': 'Método no permitido.'})


def update_data_tcp(request):
    datos = tcp_s.objects.all()

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


def list_service_tcp(request):
    tcp_sservice = tcp_s.objects.all()
    contexto = {'tcp_s': tcp_sservice,
                }
    return render(request, 'config/listtcp.html', contexto)


def verificar_edicion_permitida(view_func):
    @wraps(view_func)
    def wrapper(request, pk, *args, **kwargs):
        service = get_object_or_404(tcp_s, pk=pk)

        if service.processed_by != 'Esperando' and service.processed_by != 'Detenido':
            messages.error(
                request, "No se puede editar el elemento porque la prueba está en curso o terminada.")
            return redirect('list_tcp')
        return view_func(request, pk, *args, **kwargs)

    return wrapper


@verificar_edicion_permitida
def edit_tcp(request, pk):
    service = get_object_or_404(tcp_s, pk=pk)

    if request.method == 'POST':
        form = ServiceTCPForm(request.POST, instance=service)
        form.fields['number_probe'].required = False

        if form.is_valid():
            form.save()
            message = "Servicio editado correctamente."
            messages.success(request, message, extra_tags="edit" )
            return HttpResponseRedirect(reverse('list_tcp'))
    else:
        form = ServiceTCPForm(instance=service)
        if service.processed_by == 'Detenido':
            # Si el servicio está detenido, se excluye el campo 'number_probe' del formulario
            form.fields['number_probe'].required = False
            form.fields['number_probe'].widget.attrs['readonly'] = True

    return render(request, 'config/edittcp.html', {'form': form})


def statustcpgraficpoint(request, pk):
    service = tcp_s.objects.get(pk=pk)
    statuses = ServiceStatus.objects.filter(service=service)

    data = []
    for status in statuses:
        formatted_date = status.timestamp.strftime('%d-%m-%y')
        data.append({'date': formatted_date, 'is_up': status.is_up,
                    'cpu_processing_time': round(status.cpu_processing_time, 4)})
    return JsonResponse(data, safe=False)


def statustcprecord(request, pk):
    service = tcp_s.objects.get(pk=pk)
    statuses = ServiceStatus.objects.filter(service=service)

    dataa = []
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
        cpu_processing_time = round(status.cpu_processing_time, 4)
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
def delete_tcp(request, pk):
    service = get_object_or_404(tcp_s, pk=pk)

    processed_by_value = service.processed_by
    if processed_by_value not in ['Esperando', 'Detenido', 'Terminado']:
        return JsonResponse({'mensaje': 'No se puede eliminar el elemento porque la prueba está en curso.'}, status=400)

    service.delete()

    return JsonResponse({'mensaje': 'El registro ha sido eliminado exitosamente.'})
