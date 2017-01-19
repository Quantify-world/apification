from django.test import TestCase

from apification import resource, action
from apification.resources import Resource
from apification.actions import Action
from apification.exceptions import ApiStructureError


@resource
class Root(Resource):
    @resource
    class FirstItem(Resource):
        pass

    @resource
    class SecondItem(Resource):

        @resource
        class SubItem(Resource):
            
            @action
            class Get(Action):
                pass

Root.parent_class = Root.resources['SecondItem'].resources['SubItem']


class ApiCase(TestCase):
    def test_API_tree_loop(self):
        with self.assertRaises(ApiStructureError):
            Root.urls
