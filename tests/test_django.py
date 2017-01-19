from django.test import TestCase, override_settings
from django.core.urlresolvers import reverse
from django.conf.urls import url, include

from apification import resource, action, serializer
from apification.actions import Action
from apification.resource_collections import Collection, Collectible
from apification.serializers import Serializer
from apification.serializer_backends import AllAttributesBackend

from ping_project.ping import Host


class HostSerializer(Serializer):
    pass


class HostCollectionSerializer(Serializer):
    pass


class Hosts2(Collection):
    collectible = './Host'
    default_serializer = serializer(HostCollectionSerializer)
    
    def get_queryset(self):
        return []

    @action
    class Get(Action):
        pass

    @resource
    class Host(Collectible):
        model = Host
        default_serializer = serializer(HostSerializer)


class TestURLConf(object):
    urlpatterns = [url('', include(Hosts2.urls))]


@override_settings(ROOT_URLCONF=TestURLConf)
class ApiLocalCase(TestCase):
    def test_params_constuction(self):
        url = reverse('hosts2-get')
        self.client.get(url)

