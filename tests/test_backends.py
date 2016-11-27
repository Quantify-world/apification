from apification.backends import BaseBackend, BackendRegistry


class TestBackend_1(BaseBackend):
    registry_name = 'test'

class TestBackend_2(BaseBackend):
    registry_name = 'test'


def test_registry_creation():
    registry = TestBackend_1 + (TestBackend_2 + TestBackend_1) + TestBackend_1
    assert len(registry) == 4
    assert isinstance(registry, BackendRegistry)
    assert TestBackend_1 in registry
