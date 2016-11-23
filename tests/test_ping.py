from ping_project.api import Hosts, HostSerializer


def test_parent_class():
    assert Hosts.Host.Get.parent_class == Hosts.Host


def test_serializer_resolve():
    assert Hosts.Host.Get.serializer == HostSerializer


def test_collectible_resolve():
    assert Hosts.get_collectible_class() == Hosts.Host


def test_params_definition():
    assert len(Hosts.Host.Get.get_params()) == 2


def test_django_checks():
    from django.core.management import call_command

    call_command('check')
