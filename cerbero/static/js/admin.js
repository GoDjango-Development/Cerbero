$(document).ready(function () {
    // Crear la tabla con DataTables
    var table = $('#data').DataTable({

    });


    //Evento del boton eliminar .eliminar-btn
    $(document).on('click', '.eliminar-btn', function (event) {
        var objetoId = $(this).data('objeto-id');

        event.preventDefault();

        Swal.fire({
            title: '¿Estás seguro de eliminar el registro?',
            text: 'Esta acción también elimina el historial de este usuario',
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
                    url: '/cerbero/admin/userdelete/' + objetoId + '/',
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
    
    
    });


});


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
