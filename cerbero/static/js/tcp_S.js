//Crear una conexión WebSocket
let url = "ws://" + window.location.host + "/ws/buttons/";
const socket = new WebSocket(url);


$(document).ready(function () {
    // Crear la tabla con DataTables
    $('#data').DataTable({
        drawCallback: function () {
            // Restaurar el estado de reproducción al cambiar de página
            restoreButtonStates();
        }
    });

    var celeryActivo = false; // Variable para controlar el estado de Celery

    function obtenerEstadoCelery() {
        // Deshabilitar el botón mientras se obtiene el estado de Celery
        $('.monitoreo-btn').prop('disabled', true);

        $.ajax({
            url: '/confirmar/celery/',
            type: 'GET',
            success: function (response) {
                isCeleryRunning = response.isCeleryRunning;
                isRedisRunning = response.isRedisRunning;

                if (isCeleryRunning && isRedisRunning) {
                    celeryActivo = true;
                    $('.monitoreo-btn').prop('disabled', false);
                    $('.monitoreo-btn').attr('title', ''); // Borrar el título del botón si ambos servicios están activos
                } else {
                    celeryActivo = false;
                    $('.monitoreo-btn').prop('disabled', true);
                    $('.monitoreo-btn').attr('title', 'Debe iniciar el servidor de Redis y Celery');
                }
            },
            error: function (xhr) {
                console.error('Error al obtener el estado de Celery:', xhr);
                celeryActivo = false;
                $('.monitoreo-btn').prop('disabled', true);
                $('.monitoreo-btn').attr('title', 'Error al obtener el estado de Celery');
            },
            complete: function () {
                // Habilitar el botón nuevamente al completar la solicitud AJAX
                $('.monitoreo-btn').prop('disabled', !celeryActivo);
            }
        });
    }

    // Llamar a la función para obtener el estado de Celery al cargar la página
    setInterval(obtenerEstadoCelery, 5000); // Llamar a la función cada 1 segundo

    // Manejar el evento de clic del botón de monitoreo
    $('.monitoreo-btn').click(function () {
        if (!celeryActivo) {
            alert('Debe iniciar el servidor de Redis y Celery antes de realizar la acción de monitoreo.');
            return;
        }

        
    });



    //Evento del boton eliminar .eliminar-btn
    $(document).on('click', '.eliminar-btn', function (event) {
        var objetoId = $(this).data('objeto-id');

        event.preventDefault();
        var processedByValue = $(this).data("processed");
        if (processedByValue !== "Esperando" && processedByValue !== "Detenido" && processedByValue !== "Terminado") {
            toastr.warning("No se puede eliminar el elemento porque la prueba está en curso.");
        } else {
            Swal.fire({
                title: '¿Estás seguro de eliminar el registro?',
                text: 'Esta acción también elimina el historial de estados de la prueba',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Eliminar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.value) {
                    var csrfToken = getCookie('csrftoken');
                    $.ajax({
                        url: '/services/delete_tcpService/' + objetoId + '/',
                        type: 'POST',
                        headers: { 'X-CSRFToken': csrfToken },
                        success: function (response) {
                            toastr.success('¡Eliminado! ' + response.mensaje, '', { timeOut: 1000 });

                            setTimeout(function () {
                                window.location.reload();
                            }, 1000); // Espera 3 segundos antes de recargar la página
                        },
                        error: function (xhr) {
                            toastr.error('Error: ' + xhr.responseJSON.mensaje, '', { timeOut: 2000 });
                        }
                    });
                }
            });
        }
    });

    // Verificar si tengo permiso de edición .edit-btn
    $(".edit-btn").click(function (event) {
        event.preventDefault();
        var processedByValue = $(this).data("in-processed");
        if (processedByValue !== "Esperando" && processedByValue !== "Detenido") {
            toastr.warning("No se puede editar el elemento porque la prueba está en curso o terminada.");
        } else {
            var href = $(this).attr("href");
            if (href) {
                window.location.href = href;
            }
        }
    });



    //Evento del boton de monitioreo
    $(document).on('click', '.iniciar-monitoreo-btn', function () {
        var btn = $(this);
        var serviceId = btn.data('service-id');
        console.log(serviceId);
        var currentState = btn.data('button-state');
        var newState = currentState === 'true' ? 'false' : 'true';
        console.log(newState);
        // Realizar el cambio visual inmediato
        actualizarBoton(serviceId, newState === 'true');

        // Realizar la solicitud AJAX para actualizar el estado en el servidor
        actualizarEstadoEnServidor(serviceId, newState);
    });



    function restoreButtonStates() {
        // Obtener el estado almacenado en el atributo data y en el almacenamiento local
        $('.iniciar-monitoreo-btn').each(function () {
            var btn = $(this);
            var serviceId = btn.data('service-id');
            var storedState = localStorage.getItem('buttonState_' + serviceId);
            var buttonState = storedState === 'true';

            // Actualizar el estado visual del botón
            actualizarBoton(serviceId, buttonState);

        });

    }


    // Evento WebSocket: Cuando se recibe un mensaje del servidor
    socket.onmessage = function (event) {
        var message = JSON.parse(event.data);
        var text = JSON.parse(message.text);

        var pk = text.pk
        var buttonState = text.buttonState


        actualizarBoton(pk, buttonState);

    };

});

// Actualizar columnas de estados y procesos
function actualizarColumnas() {
    $.ajax({
        url: "/services/tcpServiceupdate/",
        type: "GET",
        dataType: "json",
        success: function (data) {
            console.log("Datos recibidos:", data);
            // Recorre los datos y actualiza las tres últimas columnas en cada fila
            $.each(data, function (index, elemento) {
                var serviceId = elemento.id; // Obtén el ID del servicio
                console.log("ID del servicio:", serviceId);

                // Actualiza las columnas utilizando el ID del servicio
                $("#status_" + serviceId).html(elemento.status);
                $("#process_" + serviceId).html(elemento.processed_by);
            });

            console.log("Primer elemento de los datos:", data[0]);
        },
        error: function (xhr, status, error) {
            console.error("Error al obtener los datos:", error);
        }
    });
}

// Llama a la función de actualización cada cierto intervalo de tiempo (por ejemplo, cada 1 segundos)
setInterval(actualizarColumnas, 1000);



function actualizarBoton(serviceId, iniciarMonitoreo) {
    var btn = $('[data-service-id="' + serviceId + '"]');
    if (iniciarMonitoreo) {
        btn.find('i').removeClass('fa-play').addClass('fa-pause');
    } else {
        btn.find('i').removeClass('fa-pause').addClass('fa-play');
    }
    // Actualizar el atributo data-button-state
    btn.data('button-state', iniciarMonitoreo.toString());
    // Verificar si el valor de data es "Terminado" y deshabilitar el botón
    console.log(btn.data('in-processed-by'));
    if (btn.data('in-processed-by') === 'Terminado') {
        btn.prop('disabled', true);
        btn.find('i').removeClass('fa-pause').addClass('fa-ban');
        btn.attr('title', 'Monitoreo concluido');
    } else {
        btn.prop('disabled', false);
        btn.removeAttr('title');
    }


    if (socket.readyState === WebSocket.OPEN) {
        var message = {
            serviceId: serviceId,
            newState: iniciarMonitoreo.toString()
        };
        // Enviar el mensaje actualizado a través del WebSocket
        socket.send(JSON.stringify(message));
        console.log("Mensaje enviado al servidor:", message);
    } else {
        console.error("El WebSocket no está en un estado válido para enviar mensajes.");
    }

    // Manejar eventos de apertura de la conexión
    socket.onopen = function (event) {
        console.log('Conexión WebSocket abierta');
    };

    // Guardar el estado actual en el almacenamiento local
    guardarEstadoEnLocalStorage(serviceId, iniciarMonitoreo);
}
// actualizar estado en el servidor del incio o detencion del monitoreo
function actualizarEstadoEnServidor(serviceId, newState) {
    var csrfToken = getCookie('csrftoken');
    $.ajax({
        url: '/services/tcpService/' + serviceId + '/',
        type: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
        data: {
            'action': newState === 'true' ? 'iniciar' : 'detener'
        },
        success: function (response) {
            console.log(response.message);
            toastr.success(response.message)
            // No se requiere hacer nada aquí, el cambio en el servidor ya se realizó

        },
        error: function (xhr, status, error) {
            console.error('Error al actualizar el monitoreo:', error);

            // Revertir el cambio visual en caso de error
            var currentState = newState === 'true' ? 'false' : 'true';
            actualizarBoton(serviceId, currentState);
        }
    });
}
// Guardar estados locales en la pc de como esta los botones
function guardarEstadoEnLocalStorage(serviceId, state) {
    localStorage.setItem('buttonState_' + serviceId, state.toString());
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;

}





