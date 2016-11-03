from importlib import import_module

from django.conf import settings

def discover_tree(urlconf=None):
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF

    if isinstance(urlconf, basestring):
        urlconf = import_module(urlconf)

    nodes = set()
    for item in urlconf.urlpatterns:
        for p in item.url_patterns:
            nodes.add(p.callback.im_self.get_root_class())

    return nodes
