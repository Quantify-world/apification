from django.test import TestCase, override_settings
from django.conf.urls import url, include

from apification import resource
from apification.resources import Resource


#  Correct tree for overriding urlconf
class FirstItem(Resource):
        pass

@resource
class Root(Resource):
    FirstItem = resource(FirstItem)
    
    @resource
    class SecondItem(Resource):
        pass
    

class TestURLConf(object):
    urlpatterns = [url('', include(Root.urls))]


@override_settings(ROOT_URLCONF=TestURLConf)
class ApiCase(TestCase):
    def test_API_tree_duplicates(self):
        with self.assertRaises(TypeError):
            #  Incorrect tree
            @resource
            class Root(Resource):
                FirstItem = resource(FirstItem)
                
                @resource
                class SecondItem(Resource):
                    wrong_child = resource(FirstItem)

