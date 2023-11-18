import concurrent.futures
from threading import Thread, current_thread, Lock, Event
from config.models import HTTPService, ServiceStatusHttp, TCPService, ServiceStatusTCP,\
    DNSService,ServiceStatusDNS,ICMPService, ServiceStatusICMP,TFProtocolService, ServiceStatusTFProtocol
import threading
import httplib2

from django.utils import timezone


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
                # No hay una prueba en ejecución para detener
                pass

        if pk not in current_threads_http or not current_threads_http[pk].is_alive():
            # Si no hay un hilo en ejecución para el servicio actual
            stop_flag = threading.Event()  # Crear una nueva bandera de detención de prueba
            # Almacenar la bandera en el diccionario
            stop_flags_http[pk] = stop_flag
        thread = threading.Thread(target=test_https, name=service.name, args=(service, stop_flag))
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

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i in range(current_iteration, num_of_tests):
                # Comprobar si se ha activado la bandera de detención
                if stop_flag.is_set():
                    with test_status:
                        service.in_process = False  # Establecer el estado in_process en False
                        service.current_iteration = current_iteration
                        service.save()
                    break

                future = executor.submit(run_test, http, url)
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                test_results.append(result)

                if result != "error":
                    response_statuss = result

                timestamp = timezone.now()
                service.status = result
                service.save()

                is_up = result
                ServiceStatusHttp.objects.create(
                    service=service,
                    timestamp=timestamp,
                    is_up=is_up,
                    cpu_processing_time=None,  # Cambiar este valor según tus necesidades
                    error_message=None,  # Cambiar este valor según tus necesidades
                    response_status=response_statuss,
                )

                # Actualizar la iteración actual en la base de datos
                current_iteration += 1
                service.current_iteration = current_iteration
                service.save()

                time.sleep(test_duration)

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

def run_test(http, url):
    try:
        response, error = http.request(url)
        if response.status == 301:
            # Tenemos redirección
            location = response.get('location')

            # Seguir redirección
            redirect_response, _ = http.request(location)

            if redirect_response.status == 200:
                result = "up"
            else:
                result = "down"
        else:
            if response.status == 200:
                result = "up"
            else:
                result = "down"

        return result

    except Exception as e:
        return "down"

