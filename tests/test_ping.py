from ping_project.api import Hosts, PingSerializer

def test_parent_class():
    assert Hosts.Item.Get.parent_class == Hosts.Item

def test_serializer_resolve():
    assert Hosts.Item.Get.serializer == PingSerializer
