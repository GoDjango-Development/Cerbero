import time
import httplib2
import socket
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User, Group
from cerbero.settings import EMAIL_HOST_USER
from celery import shared_task
from icmplib import ping
from tfprotocol_client.tfprotocol import TfProtocol
from threading import Thread, current_thread, Lock, Event
from config.models import HTTPService, ServiceStatusHttp, TCPService, ServiceStatusTCP,\
    DNSService,ServiceStatusDNS,ICMPService, ServiceStatusICMP,TFProtocolService, ServiceStatusTFProtocol


stop_flags_http= {}
current_threads_http = {}  # Diccionario para almacenar referencias a los hilos en ejecución
stop_flags_tcp= {}
current_threads_tcp = {}  # Diccionario para almacenar referencias a los hilos en ejecución
stop_flags_dns  =  {}
current_threads_dns = {}
stop_flags_icmp =  {}
current_threads_icmp = {}

stop_flags_tfp =  {}
current_threads_tfp = {}
# Bloqueo para sincronizar el acceso a las banderas de detención
stop_flags_lock = Lock()
# Bloqueo adicional para sincronizar las actualizaciones de las banderas de detención
stop_flags_update_lock = Lock()
test_status = Lock()



def send_test_completion_email(service):
    created_by_user = service.create_by
    service_name = service.name
    cant_test = service.number_probe
     
    # Obtener el grupo "staff"
    staff_group = Group.objects.get(name='staff')

    # Obtener los usuarios asociados al grupo "staff"
    staff_users = staff_group.user_set.all()

    # Renderizar el contenido del correo electrónico en formato HTML
    html_content = render_to_string('email/test_completion.html', {
        'service_name': service_name,
        'cant_test': cant_test,
    })


     # Crear una instancia de EmailMultiAlternatives
    msg = EmailMultiAlternatives(
        subject='Prueba completada',
        body=strip_tags(html_content),  # Versión de texto plano del contenido HTML
        from_email=EMAIL_HOST_USER,
        to=[created_by_user.email],
    )
    msg.attach_alternative(html_content, "text/html")  # Adjuntar el contenido HTML al correo

    # Enviar correo electrónico al usuario creador
    msg.send()

    # Enviar correo electrónico a todos los usuarios del grupo "staff"
    for user in staff_users:
        msg = EmailMultiAlternatives(
            subject='Prueba completada',
            body=strip_tags(html_content),  # Versión de texto plano del contenido HTML
            from_email=EMAIL_HOST_USER,
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")  # Adjuntar el contenido HTML al correo
        msg.send()
    
    
@shared_task
def monitoreo_http_services(pk, resume=False):
    # Obtener el servicio de la base de datos
    global stop_flags_http
    service = HTTPService.objects.get(pk=pk)
    with stop_flags_lock:
        if resume:
            # Reanudar la prueba
            if pk in stop_flags_http:
                stop_flag = stop_flags_http[pk]
                stop_flag.clear()  # Borrar la bandera de detención para reanudar la prueba
                service.save()
            else:
                # No se encontró una prueba detenida para reanudar
                pass
        else:
            # Detener la prueba
            if pk in stop_flags_http:
                stop_flag = stop_flags_http[pk]
                stop_flag.set()  # Establecer la bandera de detención para detener la prueba

                service.save()
            else:
                # No hay una prueba en ejecución para detener/*
                pass
        with test_status:
            if service.processed_by == 'Terminado':
                print("prueba terminada no se puede volver a ejecutar")

        if pk not in current_threads_http or not current_threads_http[pk].is_alive():
            # Si no hay un hilo en ejecución para el servicio actual
            stop_flag = Event()  # Crear una nueva bandera de detención de prueba
            # Almacenar la bandera en el diccionario
            stop_flags_http[pk] = stop_flag
        thread = Thread(target=test_https, name=service.name,args=(service, stop_flag))
        thread.start()
        current_threads_http[pk] = thread


def test_https(service, stop_flag):
    test_results = []
    url = service.url
    num_of_tests = service.number_probe
    test_duration = service.probe_timeout
    response_statuss = None
    error_messages = None
    http = httplib2.Http()
    try:
        service.in_process = True
        service.save()

        # Obtener el estado actual de la prueba
        current_iteration = service.current_iteration or 0
        print(f'valor del current_iteration antes del for {current_iteration}')
        if service.processed_by != 'Terminado':
            for i in range(current_iteration, num_of_tests):
                print(f'iteracion {i} ')

                # Comprobar si se ha activado la bandera de detención
                if stop_flag.is_set():
                    with test_status:
                        service.in_process = False  # Establecer el estado in_process en False
                        print(
                            f'dentro de la preugunta de la parada {service.in_process} el de nombre {service.name}')
                        service.processed_by = 'Detenido'

                        service.current_iteration = current_iteration
                        print(f'se detuvo en { service.current_iteration}')
                        service.save()
                        break
                print(f'continuo en current_iteration {current_iteration}')

                try:
                    start_time = time.time()

                    response, error = http.request(url)
                    service.processed_by = 'Monitoreando'
                    service.save()

                    if response.status == 301:
                        # Tenemos redirección
                        location = response.get('location')
                        print(f"Redireccionando a {location}")

                        # Seguir redirección
                        redirect_response, _ = http.request(location)

                        if redirect_response.status == 200:
                            print("Redirección completada exitosamente")
                            result = "up"

                        else:
                            result = "down"

                        test_results.append(result)
                        response_statuss = redirect_response.status
                    else:
                        if response.status == 200:
                            result = "up"
                        else:
                            result = "down"

                        test_results.append(result)

                        response_statuss = response.status

                    end_time = time.time()
                    cpu_processing_times = end_time - start_time
                    print(f"costo conexión: {cpu_processing_times}")

                except Exception as e:
                    error_messages = str(e)
                    print(f"Error de conexión: {str(e)}")
                    cpu_processing_times = 0
                    result = "error"
                    test_results.append(result)
                timestamp = timezone.now()

                service.status = result
                service.save()

                is_up = result
                ServiceStatusHttp.objects.create(
                    service=service,
                    timestamp=timestamp,
                    is_up=is_up,
                    cpu_processing_time=cpu_processing_times,
                    error_message=error_messages,
                    response_status=response_statuss
                )

                # Actualizar la iteración actual en la base de datos
                current_iteration = i + 1

                print(
                    f'se esta guardando current_iteration{current_iteration}')
                service.current_iteration = current_iteration
                print(
                    f'se esta guardando service.current_iteratio{service.current_iteration} y proceso {service.processed_by}')

                service.save()

                time.sleep(test_duration)
                if current_iteration == num_of_tests:
                    service.processed_by = 'Terminado'
                    service.save()
                    send_test_completion_email(service)

    finally:
        with test_status:
            service.refresh_from_db()
            # Restablecer el estado de la iteración actual
            service.current_iteration = current_iteration
            service.save()

        with stop_flags_update_lock:
            with stop_flags_lock:
                # Eliminar la bandera de detención de prueba
                stop_flags_http.pop(service.pk, None)


@shared_task
def monitoreo_tcp_services(pk, resume=False):
    # Obtener el servicio de la base de datos
    global stop_flags_tcp
    service = TCPService.objects.get(pk=pk)
    with stop_flags_lock:
        if resume:
            # Reanudar la prueba
            if pk in stop_flags_tcp:
                stop_flag = stop_flags_tcp[pk]
                stop_flag.clear()  # Borrar la bandera de detención para reanudar la prueba
                service.save()
            else:
                # No se encontró una prueba detenida para reanudar
                pass
        else:
            # Detener la prueba
            if pk in stop_flags_tcp:
                stop_flag = stop_flags_tcp[pk]
                stop_flag.set()  # Establecer la bandera de detención para detener la prueba

                service.save()
            else:
                # No hay una prueba en ejecución para detener/*
                pass
        with test_status:
            if service.processed_by == 'Terminado':
                print("prueba terminada no se puede volver a ejecutar")

        if pk not in current_threads_tcp or not current_threads_tcp[pk].is_alive():
            # Si no hay un hilo en ejecución para el servicio actual
            stop_flag = Event()  # Crear una nueva bandera de detención de prueba
            # Almacenar la bandera en el diccionario
            stop_flags_tcp[pk] = stop_flag
        thread = Thread(target=test_tcp, name=service.name,args=(service, stop_flag))
        thread.start()
        current_threads_tcp[pk] = thread


def test_tcp(service, stop_flag):
    test_results = []
    ip = service.ip_address
    port = service.port
    num_of_tests = service.number_probe
    test_duration = service.probe_timeout

    try:
        service.in_process = True
        service.save()

        # Obtener el estado actual de la prueba
        current_iteration = service.current_iteration or 0
        print(f'valor del current_iteration antes del for {current_iteration}')
        if service.processed_by != 'Terminado':
            for i in range(current_iteration, num_of_tests):
                service.processed_by = current_thread().name
                service.save()
                print(f'iteracion {i} ')

                # Comprobar si se ha activado la bandera de detención
                if stop_flag.is_set():
                    with test_status:
                        service.in_process = False  # Establecer el estado in_process en False
                        print(
                            f'dentro de la preugunta de la parada {service.in_process} el de nombre {service.name}')
                        service.processed_by = 'Detenido'

                        service.current_iteration = current_iteration
                        print(f'se detuvo en { service.current_iteration}')
                        service.save()
                        break
                print(f'continuo en current_iteration {current_iteration}')

                try:
                    start_time = time.time()
                    service.processed_by = 'Monitoreando'
                    service.save()
                    if ip:
                        with socket.create_connection((ip, port), timeout=5) as sock:
                            result = "up"
                
                    else:
                        result = "down"

                    end_time = time.time()
                    cpu_processing_times = end_time - start_time
                    print(f"costo conexión: {cpu_processing_times}")

                except Exception as e:
                    print(f"Error de conexión: {str(e)}")
                    result = "error"
                    cpu_processing_times = 0
                test_results.append(result)

                service.status = result
                service.save()

                timestamp = timezone.now()

                is_up = result

                service.status = result
                service.save()

                is_up = result
                ServiceStatusTCP.objects.create(
                    service=service,
                    timestamp=timestamp,
                    is_up=is_up,
                    cpu_processing_time=cpu_processing_times
                )
                # Actualizar la iteración actual en la base de datos
                current_iteration = i + 1

                print(
                    f'se esta guardando current_iteration{current_iteration}')
                service.current_iteration = current_iteration
                print(
                    f'se esta guardando service.current_iteratio{service.current_iteration} y proceso {service.processed_by}')

                service.save()

                time.sleep(test_duration)
            if current_iteration == num_of_tests:
                service.processed_by = 'Terminado'
                service.save()

    finally:
        with test_status:
            service.refresh_from_db()
            # Restablecer el estado de la iteración actual
            service.current_iteration = current_iteration
            service.save()

        with stop_flags_update_lock:
            with stop_flags_lock:
                # Eliminar la bandera de detención de prueba
                stop_flags_tcp.pop(service.pk, None)


@shared_task
def monitoreo_dns_services(pk, resume=False):
    # Obtener el servicio de la base de datos
    global stop_flags_dns
    service = DNSService.objects.get(pk=pk)
    with stop_flags_lock:
        if resume:
            # Reanudar la prueba
            if pk in stop_flags_dns:
                stop_flag = stop_flags_dns[pk]
                stop_flag.clear()  # Borrar la bandera de detención para reanudar la prueba
                service.save()
            else:
                # No se encontró una prueba detenida para reanudar
                pass
        else:
            # Detener la prueba
            if pk in stop_flags_dns:
                stop_flag = stop_flags_dns[pk]
                stop_flag.set()  # Establecer la bandera de detención para detener la prueba

                service.save()
            else:
                # No hay una prueba en ejecución para detener/*
                pass
        with test_status:
            if service.processed_by == 'Terminado':
                print("prueba terminada no se puede volver a ejecutar")

        if pk not in current_threads_dns or not current_threads_dns[pk].is_alive():
            # Si no hay un hilo en ejecución para el servicio actual
            stop_flag = Event()  # Crear una nueva bandera de detención de prueba
            # Almacenar la bandera en el diccionario
            stop_flags_dns[pk] = stop_flag
        thread = Thread(target=test_dns, name=service.name,args=(service, stop_flag))
        thread.start()
        current_threads_dns[pk] = thread


def test_dns(service, stop_flag):
    test_results = []
    ip = service.ip_address
    port = service.port
    num_of_tests = service.number_probe
    test_duration = service.probe_timeout

    try:
        service.in_process = True
        service.save()

        # Obtener el estado actual de la prueba
        current_iteration = service.current_iteration or 0
        print(f'valor del current_iteration antes del for {current_iteration}')
        if service.processed_by != 'Terminado':
            for i in range(current_iteration, num_of_tests):
                service.processed_by = current_thread().name
                service.save()
                print(f'iteracion {i} ')

                # Comprobar si se ha activado la bandera de detención
                if stop_flag.is_set():
                    with test_status:
                        service.in_process = False  # Establecer el estado in_process en False
                        print(
                            f'dentro de la preugunta de la parada {service.in_process} el de nombre {service.name}')
                        service.processed_by = 'Detenido'

                        service.current_iteration = current_iteration
                        print(f'se detuvo en { service.current_iteration}')
                        service.save()
                        break
                print(f'continuo en current_iteration {current_iteration}')

                try:
                    start_time = time.time()
                    service.processed_by = 'Monitoreando'
                    service.save()
                    if ip:
                        with socket.create_connection((ip, port), timeout=5) as sock:
                            result = "up"
                
                    else:
                        result = "down"

                    end_time = time.time()
                    cpu_processing_times = end_time - start_time
                    print(f"costo conexión: {cpu_processing_times}")

                except Exception as e:
                    print(f"Error de conexión: {str(e)}")
                    result = "error"
                    cpu_processing_times = 0
                test_results.append(result)

                service.status = result
                service.save()

                timestamp = timezone.now()

                is_up = result

                service.status = result
                service.save()

                is_up = result
                ServiceStatusDNS.objects.create(
                    service=service,
                    timestamp=timestamp,
                    is_up=is_up,
                    cpu_processing_time=cpu_processing_times
                )
                # Actualizar la iteración actual en la base de datos
                current_iteration = i + 1

                print(
                    f'se esta guardando current_iteration{current_iteration}')
                service.current_iteration = current_iteration
                print(
                    f'se esta guardando service.current_iteratio{service.current_iteration} y proceso {service.processed_by}')

                service.save()

                time.sleep(test_duration)
            if current_iteration == num_of_tests:
                service.processed_by = 'Terminado'
                service.save()

    finally:
        with test_status:
            service.refresh_from_db()
            # Restablecer el estado de la iteración actual
            service.current_iteration = current_iteration
            service.save()

        with stop_flags_update_lock:
            with stop_flags_lock:
                # Eliminar la bandera de detención de prueba
                stop_flags_dns.pop(service.pk, None)



@shared_task
def monitoreo_icmp_services(pk, resume=False):
    # Obtener el servicio de la base de datos
    global stop_flags_icmp
    service = ICMPService.objects.get(pk=pk)
    with stop_flags_lock:
        if resume:
            # Reanudar la prueba
            if pk in stop_flags_icmp:
                stop_flag = stop_flags_icmp[pk]
                stop_flag.clear()  # Borrar la bandera de detención para reanudar la prueba
                service.save()
            else:
                # No se encontró una prueba detenida para reanudar
                pass
        else:
            # Detener la prueba
            if pk in stop_flags_icmp:
                stop_flag = stop_flags_icmp[pk]
                stop_flag.set()  # Establecer la bandera de detención para detener la prueba

                service.save()
            else:
                # No hay una prueba en ejecución para detener/*
                pass
        with test_status:
            if service.processed_by == 'Terminado':
                print("prueba terminada no se puede volver a ejecutar")

        if pk not in current_threads_icmp or not current_threads_icmp[pk].is_alive():
            # Si no hay un hilo en ejecución para el servicio actual
            stop_flag = Event()  # Crear una nueva bandera de detención de prueba
            # Almacenar la bandera en el diccionario
            stop_flags_icmp[pk] = stop_flag
        thread = Thread(target=test_icmp, name=service.name,args=(service, stop_flag))
        thread.start()
        current_threads_icmp[pk] = thread


def test_icmp(service, stop_flag):
    test_results = []
    ip = service.dns_ip
    num_of_tests = service.number_probe
    test_duration = service.probe_timeout

    try:
        service.in_process = True
        service.save()

        # Obtener el estado actual de la prueba
        current_iteration = service.current_iteration or 0
        print(f'valor del current_iteration antes del for {current_iteration}')
        if service.processed_by != 'Terminado':
            for i in range(current_iteration, num_of_tests):
                service.processed_by = current_thread().name
                service.save()
                print(f'iteracion {i} ')

                # Comprobar si se ha activado la bandera de detención
                if stop_flag.is_set():
                    with test_status:
                        service.in_process = False  # Establecer el estado in_process en False
                        print(
                            f'dentro de la preugunta de la parada {service.in_process} el de nombre {service.name}')
                        service.processed_by = 'Detenido'

                        service.current_iteration = current_iteration
                        print(f'se detuvo en { service.current_iteration}')
                        service.save()
                        break
                print(f'continuo en current_iteration {current_iteration}')

                try:
                    start_time = time.time()
                    service.processed_by = 'Monitoreando'
                    service.save()
                    icmp = ping(ip, count=3, interval=1, timeout=5)
                    if icmp.is_alive:
                        result = "up"
                    else:
                        result = "down"

                    end_time = time.time()
                    cpu_processing_times = end_time - start_time
                    print(f"costo conexión: {cpu_processing_times}")

                except Exception as e:
                    print(f"Error de conexión: {str(e)}")
                    result = "error"
                    cpu_processing_times = 0
                test_results.append(result)

                service.status = result
                service.save()

                timestamp = timezone.now()

                is_up = result

                service.status = result
                service.save()

                is_up = result
                ServiceStatusICMP.objects.create(
                    service=service,
                    timestamp=timestamp,
                    is_up=is_up,
                    cpu_processing_time=cpu_processing_times
                )
                # Actualizar la iteración actual en la base de datos
                current_iteration = i + 1

                print(
                    f'se esta guardando current_iteration{current_iteration}')
                service.current_iteration = current_iteration
                print(
                    f'se esta guardando service.current_iteratio{service.current_iteration} y proceso {service.processed_by}')

                service.save()

                time.sleep(test_duration)
            if current_iteration == num_of_tests:
                service.processed_by = 'Terminado'
                service.save()

    finally:
        with test_status:
            service.refresh_from_db()
            # Restablecer el estado de la iteración actual
            service.current_iteration = current_iteration
            service.save()

        with stop_flags_update_lock:
            with stop_flags_lock:
                # Eliminar la bandera de detención de prueba
                stop_flags_icmp.pop(service.pk, None)
                
                

@shared_task
def monitoreo_tfp_services(pk, resume=False):
    # Obtener el servicio de la base de datos
    global stop_flags_tfp
    service = TFProtocolService.objects.get(pk=pk)
    with stop_flags_lock:
        if resume:
            # Reanudar la prueba
            if pk in stop_flags_tfp:
                stop_flag = stop_flags_tfp[pk]
                stop_flag.clear()  # Borrar la bandera de detención para reanudar la prueba
                service.save()
            else:
                # No se encontró una prueba detenida para reanudar
                pass
        else:
            # Detener la prueba
            if pk in stop_flags_tfp:
                stop_flag = stop_flags_tfp[pk]
                stop_flag.set()  # Establecer la bandera de detención para detener la prueba

                service.save()
            else:
                # No hay una prueba en ejecución para detener/*
                pass
        with test_status:
            if service.processed_by == 'Terminado':
                print("prueba terminada no se puede volver a ejecutar")

        if pk not in current_threads_tfp or not current_threads_tfp[pk].is_alive():
            # Si no hay un hilo en ejecución para el servicio actual
            stop_flag = Event()  # Crear una nueva bandera de detención de prueba
            # Almacenar la bandera en el diccionario
            stop_flags_tfp[pk] = stop_flag
        thread = Thread(target=test_tfp, name=service.name,args=(service, stop_flag))
        thread.start()
        current_threads_tfp[pk] = thread


def test_tfp(service, stop_flag):
    test_results = []
    address = service.address
    port = service.port
    clienthash = service.hash
    version = service.version 
    publickey = service.public_key
    
    num_of_tests = service.number_probe
    test_duration = service.probe_timeout

    try:
        service.in_process = True
        service.save()

        # Obtener el estado actual de la prueba
        current_iteration = service.current_iteration or 0
        print(f'valor del current_iteration antes del for {current_iteration}')
        if service.processed_by != 'Terminado':
            for i in range(current_iteration, num_of_tests):
                service.processed_by = current_thread().name
                service.save()
                print(f'iteracion {i} ')

                # Comprobar si se ha activado la bandera de detención
                if stop_flag.is_set():
                    with test_status:
                        service.in_process = False  # Establecer el estado in_process en False
                        print(
                            f'dentro de la preugunta de la parada {service.in_process} el de nombre {service.name}')
                        service.processed_by = 'Detenido'

                        service.current_iteration = current_iteration
                        print(f'se detuvo en { service.current_iteration}')
                        service.save()
                        break
                print(f'continuo en current_iteration {current_iteration}')

                try:
                    start_time = time.time()
                    service.processed_by = 'Monitoreando'
                    service.save()
                    
                    proto = TfProtocol(version, publickey, clienthash, address, port) 
                    proto.connect()
                    end_time = time.time()
                    cpu_processing_times = end_time - start_time
                    if proto.connect():
                        print("Conexión establecida")
                        result = 'up'
                    else:
                        print("No se pudo establecer la conexión")
                        result = "down"            
                    print(f"Tiempo de procesamiento: {cpu_processing_times:.2f} segundos")
                    proto.disconnect() 
                except Exception as e:
                    print(f"Error de conexión: {str(e)}")
                    result = "error"
                    cpu_processing_times = 0
                test_results.append(result)

                service.status = result
                service.save()

                timestamp = timezone.now()

                is_up = result

                service.status = result
                service.save()

                is_up = result
                ServiceStatusTFProtocol.objects.create(
                    service=service,
                    timestamp=timestamp,
                    is_up=is_up,
                    cpu_processing_time=cpu_processing_times
                )
                # Actualizar la iteración actual en la base de datos
                current_iteration = i + 1

                print(
                    f'se esta guardando current_iteration{current_iteration}')
                service.current_iteration = current_iteration
                print(
                    f'se esta guardando service.current_iteratio{service.current_iteration} y proceso {service.processed_by}')

                service.save()

                time.sleep(test_duration)
            if current_iteration == num_of_tests:
                service.processed_by = 'Terminado'
                service.save()

    finally:
        with test_status:
            service.refresh_from_db()
            # Restablecer el estado de la iteración actual
            service.current_iteration = current_iteration
            service.save()

        with stop_flags_update_lock:
            with stop_flags_lock:
                # Eliminar la bandera de detención de prueba
                stop_flags_icmp.pop(service.pk, None)
