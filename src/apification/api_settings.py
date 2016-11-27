from apification.serializer_backends import DjangoSerializerBackend, ToJsonSerializerBackend, AllAttributesBackend

VALID_HTTP_METHODS = ('GET', 'POST', 'DELETE', 'PUT', 'PATCH', 'HEAD', 'OPTION')

SERIALIZER_BACKENDS = ToJsonSerializerBackend + DjangoSerializerBackend + AllAttributesBackend
