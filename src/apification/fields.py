
# class NodeMeta(type):
#     def __getattribute__(cls, name):
#         if cls.node:
#             getattr(cls.node, name)
# 
# class node(object):
#     __metaclass__ = nodeMeta

from apification.deserializers import ctx

class HostDeser(Deser):
    like = ctx('Like.deserializer')  # ctx.Like.deserializer

        
class PingDeser(Deser):
    count = factory(IntField, requred=True)
    extra_args = factory(ExtraArgs)
    
    ('id', 'title', '')