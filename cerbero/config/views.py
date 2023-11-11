from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import redis
from cerbero.celery import app


@csrf_exempt
def check_services(request):
    # Verificar Redis
    is_redis_running = check_redis()

    # Verificar Celery
    is_celery_running = check_celery()

    return JsonResponse({
        'isRedisRunning': is_redis_running,
        'isCeleryRunning': is_celery_running
    })

def check_redis():
    try:
        # Crea una conexión a Redis
        r = redis.Redis()

        # Verifica si se puede establecer una conexión
        r.ping()

        return True
    except redis.ConnectionError:
        return False

def check_celery():
    try:
        

        # Verifica si se puede establecer una conexión con el trabajador de Celery
        app.control.inspect().ping()

        return True
    except Exception:
        return False