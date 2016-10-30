from apification.actions import Action, PayloadAction
from apification.resources import Resource
from apification.collections import Collection
from apification.serializers import Serializer, ListSerializer
from apification.deserializers import Deserializer
from apification.params import RequestParam, PkParam

from ping_project.ping import Host


class Comment:
    pass


class HostSerializer(Serializer):
    def from_object(self):
        return {'hostname': self.obj.hostname}

    
class HostCollectionSerializer(Serializer):
    class Items(ListSerializer):
        serializer_name = 'default_serializer'
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
    #name = 'hosts'  #  set automaticaly from class name
    someHCSerializer = HostCollectionSerializer
    some_refer_string = PingSerializer
    params = {'request': RequestParam}

    class Get(Action):
        serializer = 'someHCSerializer'
         
    class Item(Resource):
        params = {'request': RequestParam, 'host_pk': PkParam}
        model = Host
        default_serializer = 'some_refer_string'
        alternative_serializer = 'someHCSerializer'
    
        class Like(Resource):
            params = {'request': RequestParam}
            class Get(Action):
                method = 'PUT'
            class Post(Action):
                method = 'POST'

        class Comments(Collection):
            model = Comment
            params = {'request': RequestParam}
            class Item(Resource):
                default_serializer = CommentSerializer
                params = {'request': RequestParam, 'comment_pk': PkParam}

        class Get(Action):
            method = 'GET'
    
        class Ping(PayloadAction):
            def process(obj):
                #HERE call Host.ping
                pass
        
        def get_object(self):
            pk = int(self.kwargs['host_pk'])
            obj_list = self.parent.get_object()
            return obj_list[pk]
    
    def get_object(self):
        return Host.get_list()
