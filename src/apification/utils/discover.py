from importlib import import_module

from django.conf import settings

from apification.utils.attr import has_descent_attrs


def discover_tree(urlconf=None):
    """Finds all ApiNode usage in given or default urlconf"""

    if urlconf is None:
        urlconf = settings.ROOT_URLCONF

    if isinstance(urlconf, basestring):
        urlconf = import_module(urlconf)

    nodes = set()
    for item in urlconf.urlpatterns:
        for p in item.url_patterns:
            if has_descent_attrs(p.callback, 'im_self', 'get_root_class'):
                nodes.add(p.callback.im_self.get_root_class())

    return nodes
