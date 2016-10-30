from apification.actions import Action, PayloadAction
from apification.resources import Resource
from apification.collections import Collection, Collectible
from apification.serializers import Serializer, ListSerializer
from apification.deserializers import Deserializer
from apification.params import RequestParam, PkParam

from ping_project.ping import Host


class Comment:
    pass


class HostSerializer(Serializer):
    def from_object(self, obj):
        return {'hostname': obj.hostname}

    
# class HostCollectionSerializer(Serializer):
#     class Items(ListSerializer):
#         serializer_name = 'default_serializer'
#         def iter_nodes(self):
#             return iter(self.node)

class HostCollectionSerializer(ListSerializer):
    def iter_nodes(self):
        return iter(self.node)

class PingSerializer(Serializer):
    pass


class HostSerializer2(Serializer):
    pass
    #comments = CommentCollectionSerializer
    

class CommentCollectionSerializer(Serializer):
    pass

class CommentSerializer(Serializer):
    pass

class PingDeserializer(Deserializer):
    pass



class Hosts(Collection):
    default_serializer = HostCollectionSerializer

    class Get(Action):
        pass

    class Rating(Resource):
        pass

    class Host(Collectible):
        model = Host
        default_serializer = HostSerializer
    
        class Like(Resource):
            class Get(Action):
                method = 'PUT'
            class Post(Action):
                method = 'POST'

        class Comments(Collection):
            model = Comment
            class Item(Resource):
                default_serializer = CommentSerializer

        class Get(Action):
            method = 'GET'
    
        class Ping(PayloadAction):
            def process(obj):
                #HERE call Host.ping
                pass

    def get_queryset(self):  # temporary until collections will be decoupled from django querysets
        class QS:
            @staticmethod
            def get(pk):
                return self.get_list()[int(pk)]
        return QS
    
    def get_list(self):
        return Host.get_list()
