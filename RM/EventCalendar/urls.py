from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'index/$', views.index, name='RM_EventCalendar_index'),
    url(r'panel1/calendar1/event/$', views.Panel1.Calendar1.event),
    url(r'panel1/calendar1/event_select/$', views.Panel1.Calendar1.event_select),
    url(r'panel1/calendar1/event_update/$', views.Panel1.Calendar1.event_update),
    url(r'panel1/calendar1/event_click/$', views.Panel1.Calendar1.event_click),
]
