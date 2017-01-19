from apification.actions import Action, PayloadAction
from apification.resources import Resource
from apification.resource_collections import Collection, Collectible
from apification.serializers import Serializer, List
from apification.deserializers import Deserializer

from ping_project.ping import Host


class HostSerializer(Serializer):
    pass


class HostCollectionSerializer(Serializer):
    results = List(
        node_path='./Host',
        serializer_name='default_serializer',
        generation_method_name='iter_collectible_nodes',
    )


@resource
class Hosts(Collection):
    collectible = './Host'
    default_serializer = HostCollectionSerializer

    @action
    class Get(Action):
        pass

    @resource
    class Host(Collectible):
        default_serializer = HostSerializer

        class Get(Action):
            method = 'GET'

    def get_queryset(self):  # temporary until collections will be decoupled from django querysets
        class QS:  # stub
            @staticmethod
            def get(pk):
                return self.get_list()[int(pk)]
        return QS
    
    def get_list(self):
        return Host.get_list()
