from ping_project.api import Hosts, HostSerializer


def test_parent_class():
    assert Hosts.Host.Get.parent_class == Hosts.Host


def test_serializer_resolve():
    assert Hosts.Host.Get.serializer == HostSerializer
    # assert Hosts.Host.Like.Get.serializer == HostSerializer
    # assert Hosts.Rating.SubResource.Get.serializer == Hosts.default_serializer


def test_collectible_resolve():
    assert Hosts.get_collectible_class() == Hosts.Host


def test_django_checks():
    from django.core.management import call_command

    call_command('check')
