
$(document).ready(function () {
    // Crear la tabla con DataTables
    var table = $('#data').DataTable({
    });


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
                        url: '/services/delete_httpService/' + objetoId + '/',
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

    // Verificar si tengo permiso de edición
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

    // Obtener el estado almacenado en el atributo data y en el almacenamiento local
    $('.iniciar-monitoreo-btn').each(function () {
        var btn = $(this);
        var serviceId = btn.data('service-id');
        var storedState = localStorage.getItem('buttonState_' + serviceId);
        var buttonState = storedState === 'true';

        // Actualizar el estado visual del botón
        actualizarBoton(serviceId, buttonState);

    });

    $(document).on('click', '.iniciar-monitoreo-btn', function () {
        var btn = $(this);
        var serviceId = btn.data('service-id');
        var currentState = btn.data('button-state');
        var newState = currentState === 'true' ? 'false' : 'true';
        // Realizar el cambio visual inmediato
        actualizarBoton(serviceId, newState === 'true');
        // Realizar la solicitud AJAX para actualizar el estado en el servidor
        actualizarEstadoEnServidor(serviceId, newState);
    });

    function actualizarBoton(serviceId, iniciarMonitoreo) {
        var btn = $('[data-service-id="' + serviceId + '"]');
        if (iniciarMonitoreo) {
            btn.html('<i class="fas fa-pause"></i>');
        } else {
            btn.html('<i class="fas fa-play"></i>');
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
        // Guardar el estado actual en el almacenamiento local
        guardarEstadoEnLocalStorage(serviceId, iniciarMonitoreo);
    }


    function actualizarEstadoEnServidor(serviceId, newState) {
        var csrfToken = getCookie('csrftoken');
        $.ajax({
            url: '/services/httpService/' + serviceId + '/',
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

    function actualizarColumnas() {
        $.ajax({
            url: "/services/httpServiceupdate/",
            type: "GET",
            dataType: "json",
            success: function (data) {
                // Recorre los datos y actualiza las tres últimas columnas en cada fila
                $.each(data, function (index, elemento) {
                    $("#status_" + (index + 1)).html(elemento.status);
                    $("#process_" + (index + 1)).html(elemento.processed_by);
                    
                });
            },
            error: function (xhr, status, error) {
                console.error("Error al obtener los datos:", error);
            }
        });
    }


    // Llama a la función de actualización cada cierto intervalo de tiempo (por ejemplo, cada 5 segundos)
    setInterval(actualizarColumnas, 5000);

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

});

