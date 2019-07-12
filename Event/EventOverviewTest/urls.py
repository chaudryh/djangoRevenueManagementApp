from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'index/$', views.index, name='EventOverviewTest_index'),
    url(r'panel1/form1/submit$', views.Panel1.Form1.submit),
    url(r'panel1/form1/get_selections', views.Panel1.Form1.get_selections),

    # url(r'panel1/form1/fileupload$', views.Panel1.Form1.fileupload),
    url(r'panel2/table1/create$', views.Panel2.Table1.create),
    url(r'panel2/table1/edit$', views.Panel2.Table1.edit),
    url(r'panel3/form1/submit$', views.Panel3.Form1.submit),

]