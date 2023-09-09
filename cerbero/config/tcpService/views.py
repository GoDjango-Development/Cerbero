
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from config.models import TCPService as tcp_s, ServiceStatusTCP as ServiceStatus
from .forms import ServiceTCPForm
from config.tasks import monitoreo_tcp_services
import json


# def service_detail_view(request, pk):
#     service = http_s.objects.get(pk=pk)
#     statuses = ServiceStatus.objects.filter(service=service)

#     data = []
#     for status in statuses:
#         formatted_date = status.timestamp.strftime('%d-%m-%y')
#         data.append({'date': formatted_date, 'is_up': status.is_up, 'cpu_processing_time': status.cpu_processing_time})

#     context = {
#         'service': service,
#         'statuses': statuses,
#         'data_json': json.dumps(data)
#     }
#     return render(request, 'config/detailhttp.html', context)


def create_service_tcp(request):
    if request.method == 'POST':
        form = ServiceTCPForm(request.POST)
        if form.is_valid():
            service = form.save()

        # monitoreo_http_services.delay()
        mensaje = "Servicio guardado correctamente."
        messages.success(request, mensaje)

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


def list_service_tcp(request):
    tcp_sservice = tcp_s.objects.all()
    contexto = {'tcp_s': tcp_sservice,
                }
    return render(request, 'config/listtcp.html', contexto)


# def edit_https(request, pk):
#     service = get_object_or_404(http_s, pk = pk)
#     if request.method == 'POST':
#         if service.in_process:
#             # Redireccionar y mostrar una alerta
#             return redirect('error_edit_https')

#         else:
#             form = ServiceHTTPForm(request.POST, instance=service)

#             if form.is_valid():
#                 form.save()
#                 return HttpResponseRedirect(reverse('list_https'))

#     form = ServiceHTTPForm(instance=service)
#     return render(request, 'config/edithttp.html', {'form': form})


# def error_edit_https(request):
#     mensaje = 'Lo siento no se puede editar el servicio porque este ya está siendo monitoreado o termino el monitoreo'
#     return render(request, 'base/errorEdit.html',{"mensaje":mensaje})
