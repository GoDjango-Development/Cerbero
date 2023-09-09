from django.urls import path
from config.httpService.views import view_https, create_https, service_detail_view,check_service_http, edit_https, update_data_http
from config.tcpService.views import create_service_tcp, list_service_tcp, check_service_tcp
from config.dnsService.views import create_service_dns, list_service_dns, check_service_dns, update_data_dns
from config.icmpService.views import create_service_icmp, view_icmp, check_service_icmp, update_data_icmp




urlpatterns = [
    # httpservice
    path('list_httpService/', view_https, name='list_https'),
    path('create_httpService/', create_https, name='create_https'),
    path('edit_httpService/<int:pk>/', edit_https, name='edit_https'),
    path('detail_httpService/<int:pk>/', service_detail_view, name='service_detail'),
    path('httpService/<int:pk>/',check_service_http , name='check_service_http'),
    path('httpServiceupdate/',update_data_http , name='update_data_http'),
    
    
    
    # tcpservice
    path('list_tcpService/', list_service_tcp, name='list_tcp'),
    path('create_tcpService/', create_service_tcp, name='create_tcp'),
    path('tcpService/<int:pk>/',check_service_tcp , name='check_service_tcp'),
    
    
    #dnsservice
    path('list_dnsService/', list_service_dns, name='list_dns'),
    path('create_dnsService/', create_service_dns, name='create_dns'),
    path('dnsService/<int:pk>/',check_service_dns , name='check_service_dns'),
    path('dnsServiceupdate/',update_data_dns , name='update_data_dns'),

    
    
    #icmpservice
    path('create_icmpService/', create_service_icmp, name='create_icmp'),
    path('list_icmpService/', view_icmp, name='list_icmp'),
    path('icmpService/<int:pk>/',check_service_icmp , name='check_service_icmp'),
    path('icmpServiceupdate/',update_data_icmp , name='update_data_icmp'),




    




]


