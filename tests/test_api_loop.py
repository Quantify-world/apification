from django.test import TestCase

from apification.resources import Resource
from apification.actions import Action
from apification.exceptions import ApiStructureError



class Root(Resource):
    class FirstItem(Resource):
        pass
    
    class SecondItem(Resource):
        
        class SubItem(Resource):
            
            class Get(Action):
                pass
    
    parent_class = SecondItem.SubItem


class ApiCase(TestCase):
    def test_API_tree_loop(self):
        with self.assertRaises(ApiStructureError):
            Root.urls
