"""bowlero_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import include, url
# from django.urls import path

urlpatterns = [
    url(r'admin/', admin.site.urls),
    url(r'^', include('landing.urls')),
    url(r'^Audit/', include('Audit.urls')),
    url(r'session_security/', include('session_security.urls')),
]

urlpatterns += [
    url(r'^RM/CenterTest/', include('RM.CenterTest.urls')),
    url(r'^RM/Centers/', include('RM.Centers.urls')),
    url(r'^RM/Pricing/', include('RM.Pricing.urls')),
    url(r'^RM/PricingTable/', include('RM.PricingTable.urls')),
    url(r'^RM/PricingTier/', include('RM.PricingTier.urls')),
    url(r'^RM/OpenHours/', include('RM.OpenHours.urls')),
    url(r'^RM/Bundle/', include('RM.Bundle.urls')),
    url(r'^RM/Food/', include('RM.Food.urls')),
    url(r'^RM/ProductOpt/', include('RM.ProductOpt.urls')),
    url(r'^RM/ProductSchedule/', include('RM.ProductSchedule.urls')),
    url(r'^RM/EventCalendar/', include('RM.EventCalendar.urls')),
]

urlpatterns += [
    url(r'^BowlingShoe/BSChangeReport/', include('BowlingShoe.BSChangeReport.urls')),
]

urlpatterns += [
    url(r'^Food/FoodChangeReport/', include('Food.FoodChangeReport.urls')),
    url(r'^Food/FoodByCenter/', include('Food.FoodByCenter.urls')),
]

urlpatterns += [
    url(r'^Alcohol/Alcohol/', include('Alcohol.Alcohol.urls')),
    url(r'^Alcohol/AlcoholTier/', include('Alcohol.AlcoholTier.urls')),
    url(r'^Alcohol/AlcoholChangeReport/', include('Alcohol.AlcoholChangeReport.urls')),
]

urlpatterns += [
    url(r'^Event/EventPricingTier/', include('Event.EventPricingTier.urls')),
    url(r'^Event/EventPricing/', include('Event.EventPricing.urls')),
    url(r'^Event/EventPricingTable/', include('Event.EventPricingTable.urls')),
    url(r'^Event/EventAllocation/', include('Event.EventAllocation.urls')),
    url(r'^Event/EventPriceByCenter/', include('Event.EventPriceByCenter.urls')),
    url(r'^Event/EventPriceByCenterTest/', include('Event.EventPriceByCenterTest.urls')),
    url(r'^Event/EventChangeReport/', include('Event.EventChangeReport.urls')),
    url(r'^Event/EventOverview/', include('Event.EventOverview.urls')),
    url(r'^Event/EventOverviewTest/', include('Event.EventOverviewTest.urls')),
    url(r'^Event/EventPromo/', include('Event.EventPromo.urls')),
    url(r'^Event/EventCenterTier/', include('Event.EventCenterTier.urls')),
    url(r'^Event/EventRMPS/', include('Event.EventRMPS.urls')),
    url(r'^Event/EventRMPSTest/', include('Event.EventRMPSTest.urls')),
]

urlpatterns += [
    url(r'^League/LeaguePricingSheet/', include('League.LeaguePricingSheet.urls')),
    url(r'^League/LeagueCenterInfo/', include('League.LeagueCenterInfo.urls')),
]

urlpatterns += [
    url(r'^Email/EmailNotice/', include('Email.EmailNotice.urls')),
    url(r'^Email/EmailNoticeLog/', include('Email.EmailNoticeLog.urls')),
]

urlpatterns += [
    url(r'^Weather/Weather/', include('Weather.Weather.urls')),
]

from .views import *
urlpatterns += [
    url(r'^test/', testView),
]