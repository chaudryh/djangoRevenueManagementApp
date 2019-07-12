from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'index/$', views.index, name='LeaguePricingSheet_index'),
    url(r'panel1/form1/submit$', views.Panel1.Form1.submit),
    # url(r'panel1/form1/fileupload$', views.Panel1.Form1.fileupload),
    url(r'panel2/table1/create$', views.Panel2.Table1.create),
    url(r'panel2/table1/edit$', views.Panel2.Table1.edit),
    url(r'panel2/modal1/add/$', views.Panel2.Modal1.add),
]