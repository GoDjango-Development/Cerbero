from django.contrib import messages
from functools import wraps
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.urls import reverse
from config.models import DNSService as dns_s,  ServiceStatusDNS as ServiceStatus, ServiceModificationDNS
from .forms import ServiceDNSForm
from django.contrib.auth.decorators import login_required, user_passes_test
from config.tasks import monitoreo_dns_services
import json




def is_not_superuser(user):
    return not user.is_superuser


def is_creator_admin(user, service):
    return service.create_by == user or user.groups.filter(name='staff').exists()

def verify_edit_allowed(view_func):
    @wraps(view_func)
    def wrapper(request, pk, *args, **kwargs):
        service = get_object_or_404(dns_s, pk=pk)

        if service.processed_by != 'Esperando' and service.processed_by != 'Detenido':
            messages.error(request, "No se puede editar el elemento porque la prueba está en curso o terminada.")
            return redirect('list_https')

        # Verificar si el usuario actual es el creador del servicio o pertenece al grupo "admin"
        if not is_creator_admin(request.user, service):
            messages.error(request, "No tienes permiso para editar este elemento.")
            return redirect('list_https')

        return view_func(request, pk, *args, **kwargs)

    return wrapper



def verify_deletion_allowed(view_func):
    @wraps(view_func)
    def wrapper(request, pk, *args, **kwargs):
        service = get_object_or_404(dns_s, pk=pk)

        if service.processed_by not in ['Esperando', 'Detenido', 'Terminado']:
            return JsonResponse({'mensaje': 'No se puede eliminar el elemento porque la prueba está en curso.'}, status=400)


        return view_func(request, pk, *args, **kwargs)

    return wrapper


@login_required(login_url='login', redirect_field_name ='login')
@user_passes_test(is_not_superuser, login_url='admin_home')
def create_service_dns(request):
    if request.method == 'POST':
        form = ServiceDNSForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.create_by = request.user

            service.processed_by = 'Esperando'
            service.type_service = 'Servicio DNS'

            service.save()

            mensaje = "Servicio guardado correctamente."
            messages.success(request, mensaje,extra_tags="create")

            return HttpResponseRedirect(reverse('list_dns'))
    else:
        form = ServiceDNSForm()
    return render(request, 'config/createdns.html', {'form': form})


@csrf_exempt
@login_required(login_url='login', redirect_field_name ='login')
def check_service_dns(request, pk):
    if request.method == 'POST':
        action = request.POST.get('action')
        service = get_object_or_404(dns_s, pk=pk)
        if action == 'iniciar':
            service.is_monitoring = True
            service.save()
            monitoreo_dns_services.delay(pk, resume=True)
            message = 'Monitoreo iniciado correctamente.'

            # Enviar evento WebSocket con el estado actual del botón
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('button_state_group', {
                'type': 'send_button_state',
                'text': json.dumps({
                    'pk': pk,
                    'buttonState': True
                })
            })
        elif action == 'detener':
            service.is_monitoring = False
            service.save()
            monitoreo_dns_services.delay(pk, resume=False)
            message = 'Monitoreo detenido correctamente.'

            # Enviar evento WebSocket con el estado actual del botón
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('button_state_group', {
                'type': 'send_button_state',
                'text': json.dumps({
                    'pk': pk,
                    'buttonState': False
                })
            })
        else:
            message = 'Acción no válida.'

        return JsonResponse({'message': message})

    return JsonResponse({'message': 'Método no permitido.'})

@login_required(login_url='login', redirect_field_name ='login')
def update_data_dns(request):
    datos = dns_s.objects.all()

    update = []
    for datos in datos:
        status = datos.status
        processed_by = datos.processed_by
        id = datos.pk

        # Crea el contenido HTML personalizado para la columna "Status" en función del valor
        if status == 'up':
            status_html = '<i class="fas fa-circle" style="color: green;"></i>'
        elif status == 'down':
            status_html = '<i class="fas fa-circle" style="color: red;"></i>'
        elif status == 'error':
            status_html = '<i class="fas fa-circle" style="color: yellow;"></i>'
        else:
            status_html = '<i class="fas fa-circle" style="color: grey;"></i>'

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
            'id': id
        }
        update.append(date)
    return JsonResponse(update, safe=False)

@login_required(login_url='login', redirect_field_name ='login')
@user_passes_test(is_not_superuser, login_url='admin_home')
def list_service_dns(request):
    if request.user.groups.filter(name = 'staff').exists():        

        contexto = {'dns_s': dns_s.objects.all()}
    else:
        contexto = {'dns_s': dns_s.objects.filter(create_by = request.user)}

    return render(request, 'config/listdns.html', contexto)




@login_required(login_url='login', redirect_field_name ='login')
@verify_edit_allowed
@user_passes_test(is_not_superuser, login_url='admin_home')
def edit_dns(request, pk):
    service = get_object_or_404(dns_s, pk=pk)

    
    if request.method == 'POST':
        form = ServiceDNSForm(request.POST, instance=service)
        form.fields['number_probe'].required = False

        if form.is_valid():
            # Guardar el servicio editado
            modified_service = form.save(commit=False)
            modified_service.last_modified_by = request.user  # Establecer el usuario que realizó la modificación
            modified_service.save()
             # Crear una nueva entrada en el historial de modificaciones
            ServiceModificationDNS.objects.create(service=modified_service, modified_by=request.user)
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

@login_required(login_url='login', redirect_field_name ='login')
@user_passes_test(is_not_superuser, login_url='admin_home')
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

@login_required(login_url='login', redirect_field_name ='login')
def statusdnsgraficpoint(request,pk):
    service = dns_s.objects.get(pk=pk)
    statuses = ServiceStatus.objects.filter(service=service)

    data = []
    for status in statuses:
        formatted_date = status.timestamp.strftime('%d-%m-%y')
        data.append({'date': formatted_date, 'is_up': status.is_up, 'cpu_processing_time': round(status.cpu_processing_time, 4)})
    return JsonResponse(data, safe=False)

@login_required(login_url='login', redirect_field_name ='login')
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
@login_required(login_url='login', redirect_field_name ='login')
@verify_deletion_allowed
@user_passes_test(is_not_superuser, login_url='admin_home')
def delete_dns(request, pk):
    service = get_object_or_404(dns_s, pk=pk)

    processed_by_value = service.processed_by
    if processed_by_value not in ['Esperando', 'Detenido', 'Terminado']:
        return JsonResponse({'mensaje': 'No se puede eliminar el elemento porque la prueba está en curso.'}, status=400)

    service.delete()

    return JsonResponse({'mensaje': 'El registro ha sido eliminado exitosamente.'})

    
    


 