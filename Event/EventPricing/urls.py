from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'index/$', views.index, name='Event_Pricing_index'),
    url(r'panel1/form1/submit$', views.Panel1.Form1.submit),
    url(r'panel1/table1/create$', views.Panel1.Table1.create),
    # url(r'panel2/form1/create', views.Panel2.Form1.create),
    url(r'panel2/form1/submit$', views.Panel2.Form1.submit),
    # url(r'panel2/form2/create', views.Panel2.Form2.create),
    # url(r'panel2/form2/submit$', views.Panel2.Form2.submit),
    url(r'panel3/table1/create$', views.Panel3.Table1.create),
    url(r'panel3/table1/edit$', views.Panel3.Table1.edit),
]