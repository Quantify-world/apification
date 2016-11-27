from django.core.serializers.json import Serializer as JsonSerializer


class Serializer(JsonSerializer):
    def end_object(self, obj):                                                                                                                                                          
        # self._current has the field data
        indent = self.options.get("indent")
        if not self.first:                                                                                                                                                              
            self.stream.write(",")
            if not indent:
                self.stream.write(" ")
        if indent:
            self.stream.write("\n")
        self.stream = self.get_dump_object(obj) #, self.stream, **self.json_kwargs)
        self._current = None
