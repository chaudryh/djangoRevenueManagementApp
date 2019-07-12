from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'index/$', views.index, name='Event_PricingTable_index'),
    url(r'panel1/table1/create$', views.Panel1.Table1.create),
    url(r'panel1/table1/edit$', views.Panel1.Table1.edit),
    url(r'panel1/table1/export/(?P<filename>\w{0,50}).(?P<ext>\w{0,50})$', views.Panel1.Table1.export),
    url(r'panel2/form1/submit$', views.Panel2.Form1.submit),
]