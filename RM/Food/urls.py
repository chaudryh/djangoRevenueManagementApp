from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'index/$', views.index, name='RM_Food_index'),
    url(r'panel1/form1/submit$', views.Panel1.Form1.submit),
    url(r'panel1/form1/food_menu$', views.Panel1.Form1.get_food_menu),
    url(r'panel1/form1/fileupload$', views.Panel1.Form1.fileupload),
    url(r'panel2/table1/create$', views.Panel2.Table1.create),
    url(r'panel2/table1/edit$', views.Panel2.Table1.edit),
    url(r'panel2/modal1food/add/$', views.Panel2.Modal1Food.add),
    url(r'panel2/modal1food/delete$', views.Panel2.Modal1Food.delete),
    url(r'panel2/modal2menu/add$', views.Panel2.Modal2Menu.add),
    url(r'panel2/modal2menu/edit$', views.Panel2.Modal2Menu.edit),
    url(r'panel2/modal2menu/delete$', views.Panel2.Modal2Menu.delete),
    url(r'panel2/modal3tier/add$', views.Panel2.Modal3Tier.add),
    url(r'panel2/modal3tier/edit$', views.Panel2.Modal3Tier.edit),
    url(r'panel2/modal3tier/delete$', views.Panel2.Modal3Tier.delete),
]