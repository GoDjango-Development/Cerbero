from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, Http404



# Create your views here.



def dashboard(request):
    return HttpResponse( "Actualizacion exitosa")




