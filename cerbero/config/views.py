from django.http import JsonResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
import redis
from cerbero.celery import app
from typing import re


from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

#Import the celery app from project






@csrf_exempt
def check_services(request):
    # Verificar Redis
    is_redis_running = check_redis()

    # Verificar Celery
    is_celery_running = check_celery()

    return JsonResponse({
        'isRedisRunning': is_redis_running,
        'isCeleryRunning': is_celery_running,
        'redisStatus' : is_redis_running,
        'celeryStats' : is_celery_running
        
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
    flag = False
    try:
        

        # Verifica si se puede establecer una conexión con el trabajador de Celery
        insp = app.control.inspect()
        nodes = insp.stats()
        if  nodes:
            flag = True
         
        return flag
    except Exception:
        return flag
    
    
    
