from django.conf.urls import url, include
#from django.contrib import admin
from ping_project.api import HostCollection

urlpatterns = [
    url('', include(HostCollection.urls))
]
