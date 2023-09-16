
from django.contrib import messages
from functools import wraps
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


from django.urls import reverse
from config.models import HTTPService as http_s, ServiceStatusHttp as ServiceStatus
from .forms import ServiceHTTPForm
from config.tasks import monitoreo_http_services
import json


def service_detail_view(request, pk):
    service = http_s.objects.get(pk=pk)
    statuses = ServiceStatus.objects.filter(service=service)

    context = {
        'service': service,
        'statuses': statuses,
    }

    return render(request, 'config/detailhttp.html', context)


def statushttpgraficpoint(request, pk):
    service = http_s.objects.get(pk=pk)
    statuses = ServiceStatus.objects.filter(service=service)

    data = []
    for status in statuses:
        formatted_date = status.timestamp.strftime('%d-%m-%y')
        data.append({'date': formatted_date, 'is_up': status.is_up,
                    'cpu_processing_time': round(status.cpu_processing_time, 4)})
    return JsonResponse(data, safe=False)


def create_https(request):
    if request.method == 'POST':
        form = ServiceHTTPForm(request.POST)
        if form.is_valid():

            service = form.save(commit=False)
            service.processed_by = 'Esperando'
            service.save()

            message = "Servicio guardado correctamente."
            messages.success(request, message, extra_tags="create")

            return HttpResponseRedirect(reverse('list_https'))
    else:
        form = ServiceHTTPForm()
    return render(request, 'config/createhttp.html', {'form': form})


@csrf_exempt
def check_service_http(request, pk):
    if request.method == 'POST':
        action = request.POST.get('action')
        service = get_object_or_404(http_s, pk=pk)
        if action == 'iniciar':
            monitoreo_http_services.delay(pk, resume=True)

            message = 'Monitoreo iniciado correctamente.'
        elif action == 'detener':
            monitoreo_http_services.delay(pk, resume=False)
            message = 'Monitoreo detenido correctamente.'
        else:
            message = 'Acción no válida.'

        return JsonResponse({'message': message})

    return JsonResponse({'message': 'Método no permitido.'})


def view_https(request):
    contexto = {'http_s': http_s.objects.all()}
    return render(request, 'config/listhttp.html', contexto)


def statushttprecord(request, pk):
    service = http_s.objects.get(pk=pk)
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
        response_status = status.response_status
        error_message = status.error_message

        statusdate = {
            'is_up': status_html,
            'timestamp': timestamp,
            'cpu_processing_time': cpu_processing_time,
            'response_status': response_status,
            'error_message': error_message
        }
        dataa.append(statusdate)
    return JsonResponse(dataa, safe=False)


def update_data_http(request):
    datos = http_s.objects.all()

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


def verificar_edicion_permitida(view_func):
    @wraps(view_func)
    def wrapper(request, pk, *args, **kwargs):
        service = get_object_or_404(http_s, pk=pk)

        if service.processed_by != 'Esperando' and service.processed_by != 'Detenido':
            messages.error(
                request, "No se puede editar el elemento porque la prueba está en curso o terminada.")
            return redirect('list_https')
        return view_func(request, pk, *args, **kwargs)

    return wrapper


@verificar_edicion_permitida
def edit_https(request, pk):
    service = get_object_or_404(http_s, pk=pk)

    if request.method == 'POST':
        form = ServiceHTTPForm(request.POST, instance=service)
        # Quita la validación del campo 'number_probe' si el servicio está detenido y el campo está vacío
        if service.processed_by == 'Detenido' and not request.POST.get('number_probe'):
            form.fields['number_probe'].required = False
        if form.is_valid():
            form.save()
            message = "Servicio editado correctamente."
            messages.success(request, message, extra_tags="edit")
            return HttpResponseRedirect(reverse('list_https'))
    else:
        form = ServiceHTTPForm(instance=service)
        if service.processed_by == 'Detenido':
            # Si el servicio está detenido, se excluye el campo 'number_probe' del formulario
            form.fields['number_probe'].required = False
            form.fields['number_probe'].widget.attrs['readonly'] = True
    return render(request, 'config/edithttp.html', {'form': form})


@csrf_exempt
@require_POST
def delete_http(request, pk):
    service = get_object_or_404(http_s, pk=pk)

    processed_by_value = service.processed_by
    if processed_by_value not in ['Esperando', 'Detenido', 'Terminado']:
        return JsonResponse({'mensaje': 'No se puede eliminar el elemento porque la prueba está en curso.'}, status=400)

    service.delete()

    return JsonResponse({'mensaje': 'El registro ha sido eliminado exitosamente.'})
