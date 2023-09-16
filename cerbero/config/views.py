from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse, Http404



# Create your views here.



def dashboard(request):
    return HttpResponse( "Actualizacion exitosa")



