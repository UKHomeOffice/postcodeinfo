from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.decorators.cache import cache_page

from rest_framework import routers

from postcode_api import views

router = routers.DefaultRouter()

timeout = settings.CACHES['default']['TIMEOUT']
urlpatterns = patterns('',
                       url(r'addresses',
                           cache_page(timeout)(views.AddressViewSet.as_view({'get': 'list'}))),

                       url(r'^postcodes/'
                           '(?P<postcode>[a-zA-Z0-9\s]+)/$',
                           cache_page(timeout)(views.PostcodeView.as_view())),

                       url(r'^postcodes/'
                           'partial/(?P<postcode>[a-zA-Z0-9\s]+)/$',
                           cache_page(timeout)(views.PartialPostcodeView.as_view())),

                       url('ping.json',
                           views.PingDotJsonView.as_view()),

                       url('healthcheck.json',
                           views.HealthcheckDotJsonView.as_view()),

                       url(r'^', include(router.urls)),

                       url(r'^admin/', include(admin.site.urls)),
                       )

