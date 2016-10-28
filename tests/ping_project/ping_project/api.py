
from apification.actions import Action, PayloadAction
from apification.resources import Resource
from apification.collections import Collection
from apification.serializers import Serializer
from apification.deserializers import Deserializer

from ping_project.ping import Host


class HostSerializer(Serializer):
    def from_object(self):
        return {'hostname': self.obj.hostname}
    
class HostCollectionSerializer(Serializer):
    def from_object(self):
        data_list = []
        for i, item in enumerate(self.obj):
            d = HostSerializer(self.action, item).from_object()
            d['pk'] = i
            data_list.append(d)
        return {'results': data_list} 


class PingSerializer(Serializer):
    pass


class PingDeserializer(Deserializer):
    pass



class Hosts(Collection):
    #name = 'hosts'  #  set automaticaly from class name
    someHCSerializer = HostCollectionSerializer
    some_refer_string = PingSerializer 

    class Get(Action):
        serializer = 'someHCSerializer'
         
    class Item(Resource):
        #default_serializer = HostSerializer
        default_serializer = 'some_refer_string'
        alternative_serializer = 'someHCSerializer'
    
        class Get(Action):
            method = 'PUT'
    
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
