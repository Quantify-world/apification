from django.test import TestCase, override_settings
from django.core.urlresolvers import reverse
from django.conf.urls import url, include

from apification.actions import Action
from apification.resource_collections import Collection, Collectible
from apification.serializers import Serializer, ListSerializer

from ping_project.ping import Host


class HostSerializer(Serializer):
    pass


class HostCollectionSerializer(ListSerializer):
    pass


class Hosts2(Collection):
    default_serializer = HostCollectionSerializer

    class Get(Action):
        pass

    class Host(Collectible):
        model = Host
        default_serializer = HostSerializer


class TestURLConf(object):
    urlpatterns = [url('', include(Hosts2.urls))]


@override_settings(ROOT_URLCONF=TestURLConf)
class ApiLocalCase(TestCase):
    def test_params_constuction(self):
        url = reverse('hosts2-get')
        self.client.get(url)


class ApiCase(TestCase):
    def test_listing_get(self):
        url = reverse('hosts-get')
        self.client.get(url)
