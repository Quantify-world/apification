from ping_project.api import Hosts, HostSerializer


def test_parent_class():
    assert Hosts.children['Host'].children['Get'].parent_class == Hosts.resources['Host']


def test_serializer_resolve():
    assert Hosts.children['Host'].actions['Get'].serializer == HostSerializer  # will break once serializer will be reworked with decorators and without sb
    # assert Hosts.Host.Like.Get.serializer == HostSerializer
    # assert Hosts.Rating.SubResource.Get.serializer == Hosts.default_serializer

def test_attribute_notation():
    assert Hosts.Host.Get.serializer == HostSerializer


def test_collectible_resolve():
    assert Hosts.get_collectible_class() == Hosts.resources['Host']


def test_django_checks():
    from django.core.management import call_command

    call_command('check')
