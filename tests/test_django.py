from django.test import TestCase, override_settings
from django.core.urlresolvers import reverse
from django.conf.urls import url, include

from apification.params import Param
from apification.actions import Action
from apification.resource_collections import Collection, Collectible
from apification.serializers import Serializer, ListSerializer, NodeSerializer
from apification.fields import IntField, TextField
from ping_project.ping import Host



class HostSerializer(Serializer):
    class Pk(IntField):
        pass

    class Hostname(TextField):
        pass

class HostCollectionSerializer(NodeSerializer):
    class Items(ListSerializer):
        pass


class Hosts2(Collection):
    default_serializer = HostCollectionSerializer

    class Get(Action):
        pass

    class Host(Collectible):
        model = Host
        default_serializer = HostSerializer

    @classmethod
    def get_local_params(cls):
        return {'bad_param': Param}


class TestURLConf(object):
    urlpatterns = [url('', include(Hosts2.urls))]


@override_settings(ROOT_URLCONF=TestURLConf)
class ApiCase(TestCase):
    def test_params_constuction(self):
        url = reverse('hosts2-get')
        self.assertRaises(TypeError, self.client.get, url)
