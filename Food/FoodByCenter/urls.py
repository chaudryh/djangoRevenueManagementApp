from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'index/$', views.index, name='Food_FoodByCenter_index'),
    url(r'panel1/form1/submit$', views.Panel1.Form1.submit),
    url(r'panel1/form1/get_selections', views.Panel1.Form1.get_selections),
    url(r'panel1/form1/fileupload$', views.Panel1.Form1.fileupload),
    url(r'panel2/table1/get_columns$', views.Panel2.Table1.get_columns),
    url(r'panel2/table1/create$', views.Panel2.Table1.create),
    url(r'panel2/table1/edit$', views.Panel2.Table1.edit),
    url(r'panel2/table1/export/(?P<filename>\w{0,50}).(?P<ext>\w{0,50})$', views.Panel2.Table1.export),
]