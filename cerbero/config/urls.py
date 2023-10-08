from django.urls import path
from config.httpService.views import view_https, create_https, service_detail_view, check_service_http, edit_https, update_data_http, statushttprecord, statushttpgraficpoint, delete_http
from config.tcpService.views import create_service_tcp, list_service_tcp, delete_tcp, check_service_tcp, update_data_tcp, edit_tcp, service_detail_tcp, statustcprecord, statustcpgraficpoint
from config.dnsService.views import create_service_dns, list_service_dns, delete_dns,check_service_dns, update_data_dns, edit_dns, service_detail_dns, statusdnsrecord, statusdnsgraficpoint
from config.icmpService.views import create_service_icmp, view_icmp,delete_icmp, check_service_icmp, update_data_icmp, edit_icmp, service_detail_icmp, statusicmpgraficpoint, statusicmprecord
from config.tfpService.views import list_service_tfp, create_service_tfp, update_data_tfp, check_service_tfp, service_detail_tfp, statustfpgraficpoint, edit_tfp, delete_tfp, statustfprecord


urlpatterns = [
    # httpservice
    path('list_httpService/', view_https, name='list_https'),
    path('create_httpService/', create_https, name='create_https'),
    path('edit_httpService/<int:pk>/', edit_https, name='edit_https'),
    path('detail_httpService/<int:pk>/',service_detail_view, name='service_detail'),
    path('httpService/<int:pk>/', check_service_http, name='check_service_http'),
    path('httpServiceupdate/', update_data_http, name='update_data_http'),
    path('httpStatusrecord/<int:pk>/', statushttprecord, name='statushttprecord'),
    path('httpStatusgraficpoint/<int:pk>/', statushttpgraficpoint, name='statushttpgraficpoint'),
    path('delete_httpService/<int:pk>/', delete_http, name='delete_http'),



    # tcpservice
    path('list_tcpService/', list_service_tcp, name='list_tcp'),
    path('create_tcpService/', create_service_tcp, name='create_tcp'),
    path('tcpService/<int:pk>/', check_service_tcp, name='check_service_tcp'),
    path('tcpServiceupdate/',update_data_tcp, name='update_data_tcp'),
    path('edit_tcpService/<int:pk>/', edit_tcp, name='edit_tcp'),
    path('detail_tcpService/<int:pk>/',service_detail_tcp, name='service_detail_tcp'),
    path('tcpStatusrecord/<int:pk>/', statustcprecord, name='statustcprecord'),
    path('tcpStatusgraficpoint/<int:pk>/', statustcpgraficpoint, name='statustcpgraficpoint'),
    path('delete_tcpService/<int:pk>/', delete_tcp, name='delete_tcp'),




    # dnsservice
    path('list_dnsService/', list_service_dns, name='list_dns'),
    path('create_dnsService/', create_service_dns, name='create_dns'),
    path('dnsService/<int:pk>/', check_service_dns, name='check_service_dns'),
    path('dnsServiceupdate/', update_data_dns, name='update_data_dns'),
    path('edit_dnsService/<int:pk>/', edit_dns, name='edit_dns'),
    path('detail_dnsService/<int:pk>/',service_detail_dns, name='service_detail_dns'),
    path('dnsStatusrecord/<int:pk>/', statusdnsrecord, name='statusdnsrecord'),
    path('dnsStatusgraficpoint/<int:pk>/', statusdnsgraficpoint, name='statusdnsgraficpoint'),
    path('delete_dnsService/<int:pk>/', delete_dns, name='delete_dns'),


    # tfpservice
    path('list_tfprotocolService/', list_service_tfp, name='list_tfp'),
    path('create_tfprotocolService/', create_service_tfp, name='create_tfp'),
    path('edit_tfpService/<int:pk>/', edit_tfp, name='edit_tfp'),
    path('tfpServiceupdate/', update_data_tfp, name='update_data_tfp'),
    path('tfpService/<int:pk>/', check_service_tfp, name='check_service_tfp'),
    path('detail_tfpService/<int:pk>/',service_detail_tfp, name='service_detail_tfp'),
    path('tfpStatusgraficpoint/<int:pk>/', statustfpgraficpoint, name='statustfpgraficpoint'),
    path('delete_tfpService/<int:pk>/', delete_tfp, name='delete_tfp'),
    path('ftpStatusrecord/<int:pk>/', statustfprecord, name='statustfprecord'),


    # icmpservice
    path('create_icmpService/', create_service_icmp, name='create_icmp'),
    path('list_icmpService/', view_icmp, name='list_icmp'),
    path('icmpService/<int:pk>/', check_service_icmp, name='check_service_icmp'),
    path('icmpServiceupdate/', update_data_icmp, name='update_data_icmp'),
    path('edit_icmpService/<int:pk>/', edit_icmp, name='edit_icmp'),
    path('detail_icmpService/<int:pk>/',service_detail_icmp, name='service_detail_icmp'),
    path('icmpStatusrecord/<int:pk>/', statusicmprecord, name='statusicmprecord'),
    path('icmpStatusgraficpoint/<int:pk>/', statusicmpgraficpoint, name='statusicmpgraficpoint'),
    path('delete_icmpService/<int:pk>/', delete_icmp, name='delete_icmp'),


]
