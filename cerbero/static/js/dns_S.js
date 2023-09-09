$(document).ready(function () {
    // Crear la tabla con DataTables
    var table = $('#data').DataTable({
        // Configuración de DataTables según tus necesidades
        // ...
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

    $('.iniciar-monitoreo-btn').click(function () {
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
            url: '/services/dnsService/' + serviceId + '/',
            type: 'POST',
            headers: { 'X-CSRFToken': csrfToken },
            data: {
                'action': newState === 'true' ? 'iniciar' : 'detener'
            },
            success: function (response) {
                console.log(response.message);
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
            url: "/services/dnsServiceupdate/",
            type: "GET",
            dataType: "json",
            success: function (data) {
                // Recorre los datos y actualiza las tres últimas columnas en cada fila
                $.each(data, function (index, elemento) {
                    $("#status_" + (index + 1)).html(elemento.status);
                    $("#process_" + (index + 1)).html(elemento.processed_by);
                    $("#option_" + (index + 1)).html(elemento.option);
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