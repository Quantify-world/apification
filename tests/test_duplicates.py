from django.test import TestCase, override_settings
from django.conf.urls import url, include

from apification.resources import Resource
from apification.exceptions import ApiStructureError


#  Correct tree for overriding urlconf
class FirstItem(Resource):
        pass

class Root(Resource):
    FirstItem = FirstItem    
    
    class SecondItem(Resource):
        pass
    
class TestURLConf(object):
    urlpatterns = [url('', include(Root.urls))]

@override_settings(ROOT_URLCONF=TestURLConf)
class ApiCase(TestCase):
    def test_API_tree_duplicates(self):
        with self.assertRaises(ApiStructureError):
            #  Incorrect tree
            class Root(Resource):
                FirstItem = FirstItem    
                
                class SecondItem(Resource):
                    wrong_child = FirstItem
        
    
